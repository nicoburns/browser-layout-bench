//! Loads a local HTML file into Blitz and times a non-incremental initial `resolve()` (style,
//! construct, layout, paint tree) `--iters` times; optionally hashes the final boxes or renders a PNG.
use std::fs;
use std::hash::Hasher;
use std::sync::Arc;
use std::time::Instant;

use anyrender::render_to_buffer;
use anyrender_vello_cpu::VelloCpuImageRenderer;
use blitz_dom::{BaseDocument, CopyStyleGetters, DocumentConfig, NodeId, StyleThreading};
use blitz_html::{HtmlDocument, HtmlProvider};
use blitz_paint::paint_scene;
use blitz_traits::net::{Bytes, NetHandler, NetProvider, Request};
use blitz_traits::shell::{ColorScheme, Viewport};

/// glibc malloc dominated the `layout` phase on the 100k-node cases (each node's `LayoutData` box
/// plus Taffy's per-container item vectors; the heap top is trimmed after every iteration because
/// each one builds a fresh document): `pangui/wide_no_wrap_simple_many` layout 233 ms → 147 ms with
/// mimalloc, construct 40 ms → 22 ms, style unchanged. Chrome's numbers come from a warmed renderer
/// with PartitionAlloc, so a retaining allocator is the comparable configuration.
#[global_allocator]
static GLOBAL: mimalloc::MiMalloc = mimalloc::MiMalloc;

/// Serves `file://` URLs (the corpus's `@font-face` fonts) synchronously, so every resource a
/// page requests while parsing has been delivered before the timed `resolve()`.
struct FileNetProvider;
impl NetProvider for FileNetProvider {
    fn fetch(&self, _doc_id: usize, request: Request, handler: Box<dyn NetHandler>) {
        assert_eq!(request.url.scheme(), "file", "unsupported URL {}", request.url);
        let bytes = fs::read(request.url.to_file_path().unwrap()).unwrap();
        handler.bytes(request.url.to_string(), Bytes::from(bytes));
    }
}

struct Args {
    file: String,
    width: u32,
    height: u32,
    iters: usize,
    parallel: bool,
    screenshot: Option<String>,
    hash: bool,
    boxes: bool,
    dump: bool,
    relayout: bool,
    check: bool,
    #[cfg_attr(not(feature = "cache-stats"), allow(dead_code))]
    cache_stats: bool,
}

fn parse_args() -> Args {
    let mut args = Args { file: String::new(), width: 1280, height: 800, iters: 5, parallel: false, screenshot: None, hash: false, boxes: false, dump: false, relayout: false, check: false, cache_stats: false };
    let mut it = std::env::args().skip(1);
    while let Some(a) = it.next() {
        match a.as_str() {
            "--width" => args.width = it.next().unwrap().parse().unwrap(),
            "--height" => args.height = it.next().unwrap().parse().unwrap(),
            "--iters" => args.iters = it.next().unwrap().parse().unwrap(),
            "--parallel" => args.parallel = true,
            "--screenshot" => args.screenshot = it.next(),
            "--hash" => args.hash = true,
            "--boxes" => args.boxes = true,
            "--relayout" => args.relayout = true,
            "--dump" => args.dump = true,
            "--check" => args.check = true,
            #[cfg(feature = "cache-stats")]
            "--cache-stats" => args.cache_stats = true,
            _ => args.file = a,
        }
    }
    assert!(!args.file.is_empty(), "usage: blitz-runner <file.html> [--width W] [--height H] [--iters N] [--parallel] [--hash] [--boxes] [--relayout] [--check] [--cache-stats] [--screenshot out.png]");
    args
}

fn layout_hash(doc: &BaseDocument) -> u64 {
    let mut h = std::hash::DefaultHasher::new();
    let mut count = 0u64;
    for (_, node) in doc.tree().iter() {
        if !node.is_element() {
            continue;
        }
        let l = node.final_layout();
        for v in [l.location.x, l.location.y, l.size.width, l.size.height] {
            h.write_u32(v.round().to_bits());
        }
        count += 1;
    }
    h.write_u64(count);
    h.finish()
}

/// Prints the border boxes of the elements matching `BOX_SELECTOR` (document order, page
/// coordinates), the same thing `verify` reads from Chrome with `getBoundingClientRect()`.
const BOX_SELECTOR: &str = "#cb div, #cb p, #cb h3";
fn print_boxes(doc: &BaseDocument) {
    let tree = doc.tree();
    let mut origin = std::collections::HashMap::new();
    origin.insert(doc.root_node().id, (0.0f32, 0.0f32));
    let mut stack = vec![doc.root_node().id];
    while let Some(id) = stack.pop() {
        let (ox, oy) = origin[&id];
        for &child in &tree[id].children {
            if !tree[child].is_element() {
                continue;
            }
            let l = tree[child].final_layout();
            origin.insert(child, (ox + l.location.x, oy + l.location.y));
            stack.push(child);
        }
    }
    for id in doc.query_selector_all(BOX_SELECTOR).unwrap() {
        let l = tree[id].final_layout();
        let (x, y) = origin[&id];
        println!("BOX {x} {y} {} {}", l.size.width, l.size.height);
    }
}

fn write_png(path: &str, width: u32, height: u32, rgba: &[u8]) {
    let file = fs::File::create(path).unwrap();
    let mut encoder = png::Encoder::new(std::io::BufWriter::new(file), width, height);
    encoder.set_color(png::ColorType::Rgba);
    encoder.set_depth(png::BitDepth::Eight);
    encoder.write_header().unwrap().write_image_data(rgba).unwrap();
}

fn main() {
    let args = parse_args();
    let html = fs::read_to_string(&args.file).unwrap();
    let base_url = format!("file://{}", fs::canonicalize(&args.file).unwrap().display());
    let style_threading = if args.parallel { StyleThreading::Parallel } else { StyleThreading::Sequential };

    for i in 0..args.iters {
        let config = DocumentConfig {
            viewport: Some(Viewport::new(args.width, args.height, 1.0, ColorScheme::Light)),
            base_url: Some(base_url.clone()),
            html_parser_provider: Some(Arc::new(HtmlProvider)),
            net_provider: Some(Arc::new(FileNetProvider)),
            style_threading,
            incremental: Some(args.relayout),
            ..Default::default()
        };
        let t = Instant::now();
        let mut doc = HtmlDocument::from_html(&html, config);
        doc.as_mut().handle_messages();
        let parse = t.elapsed().as_nanos();
        #[cfg(feature = "cache-stats")]
        if args.cache_stats {
            taffy::reset_cache_counters();
        }
        let t = Instant::now();
        doc.as_mut().resolve(0.0);
        let resolve = t.elapsed().as_nanos();
        println!("BLITZ parse={parse} resolve={resolve}");
        #[cfg(feature = "cache-stats")]
        if args.cache_stats && i == 0 {
            cache_stats::print_sizes();
            cache_stats::print_stats(doc.as_ref(), "initial");
        }
        if args.relayout {
            // --check: after every step, lay out the mutated document from scratch
            // (serialised and re-parsed, non-incremental) and compare element geometry
            let fresh = |html: &str| {
                let config = DocumentConfig {
                    viewport: Some(Viewport::new(args.width, args.height, 1.0, ColorScheme::Light)),
                    base_url: Some(base_url.clone()),
                    html_parser_provider: Some(Arc::new(HtmlProvider)),
                    net_provider: Some(Arc::new(FileNetProvider)),
                    style_threading,
                    incremental: Some(false),
                    ..Default::default()
                };
                let mut fresh = HtmlDocument::from_html(html, config);
                fresh.as_mut().handle_messages();
                fresh.as_mut().resolve(0.0);
                element_layouts(fresh.as_mut())
            };
            let fresh: &dyn Fn(&str) -> Vec<ElementLayout> = &fresh;
            relayout_steps(doc.as_mut(), args.check.then_some(fresh), args.cache_stats && i == 0);
        }

        if i + 1 == args.iters {
            if args.dump {
                // every element's final layout in `layout_hash` order, for diffing two builds
                for (_, node) in doc.as_ref().tree().iter().filter(|(_, n)| n.is_element()) {
                    let l = node.final_layout();
                    println!("DUMP {} <{}> {} {} {} {}", node.id, node.element_data().unwrap().name.local, l.location.x, l.location.y, l.size.width, l.size.height);
                }
            }
            if args.hash {
                println!("HASH {:016x}", layout_hash(doc.as_ref()));
                let tree = doc.as_ref().tree();
                // the tree's root: the first child of `#cb`, or the document's scrollable size when
                // `#cb` is the `<body>` (real pages)
                let cb = tree.iter().find(|(_, n)| n.attr(blitz_dom::local_name!("id")) == Some("cb")).map(|(_, n)| n);
                if let Some(cb) = cb {
                    if cb.element_data().is_some_and(|e| e.name.local == blitz_dom::local_name!("body")) {
                        let html = tree[cb.parent.unwrap()].final_layout();
                        println!("ROOT {}x{}", html.size.width, html.scrollable_overflow_rect.bottom.max(html.size.height));
                    } else if let Some(l) = cb.children.iter().find(|c| tree[**c].is_element()).map(|c| tree[*c].final_layout()) {
                        println!("ROOT {}x{}", l.size.width, l.size.height);
                    }
                }
            }
            if args.boxes {
                print_boxes(doc.as_ref());
            }
            if let Some(path) = &args.screenshot {
                let (w, h) = (args.width, args.height);
                let mut buf = render_to_buffer::<VelloCpuImageRenderer, _>(|scene| paint_scene(scene, doc.as_mut(), 1.0, w, h, 0, 0), w, h);
                for px in buf.chunks_exact_mut(4) {
                    let a = px[3] as u32;
                    for c in &mut px[..3] {
                        *c = ((*c as u32 * a + 255 * (255 - a)) / 255) as u8;
                    }
                    px[3] = 255;
                }
                write_png(path, w, h, &buf);
            }
        }
    }
}


/// The relayout scenarios of `relayout.js`, applied natively: each step mutates the tree in one batch, times one
/// incremental `resolve()` (printed as `RELAYOUT step=<name> resolve=<ns>` after that resolve's `PHASES` line) and
/// is reverted, the revert's `resolve()` discarded, before the next step.

type ElementLayout = (String, [f32; 4]);

/// Tag and final layout of every element, in tree order
fn element_layouts(doc: &BaseDocument) -> Vec<ElementLayout> {
    let mut out = Vec::new();
    let mut stack = vec![doc.root_node().id];
    while let Some(id) = stack.pop() {
        let node = &doc.tree()[id];
        if let Some(el) = node.element_data() {
            let l = node.final_layout();
            out.push((el.name.local.to_string(), [l.location.x, l.location.y, l.size.width, l.size.height]));
        }
        stack.extend(node.children.iter().rev());
    }
    out
}

/// Blitz serialises empty elements as `<div />`, which the HTML parser reads as an open tag;
/// expand them to `<div></div>` (void elements are left as they are)
fn expand_self_closing_tags(html: &str) -> String {
    const VOID: [&str; 14] = ["area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"];
    let mut out = String::with_capacity(html.len());
    let mut rest = html;
    while let Some(i) = rest.find(" />") {
        let (before, after) = rest.split_at(i);
        let start = before.rfind('<').unwrap();
        let tag: String = before[start + 1..].chars().take_while(|c| c.is_ascii_alphanumeric()).collect();
        out.push_str(before);
        if VOID.contains(&tag.as_str()) {
            out.push_str(" />");
        } else {
            out.push_str("></");
            out.push_str(&tag);
            out.push('>');
        }
        rest = &after[3..];
    }
    out.push_str(rest);
    out
}

fn element_ids(doc: &BaseDocument) -> Vec<NodeId> {
    let mut out = Vec::new();
    let mut stack = vec![doc.root_node().id];
    while let Some(id) = stack.pop() {
        let node = &doc.tree()[id];
        if node.is_element() {
            out.push(id);
        }
        stack.extend(node.children.iter().rev());
    }
    out
}

#[cfg_attr(not(feature = "cache-stats"), allow(unused_variables))]
fn relayout_steps(doc: &mut BaseDocument, check: Option<&dyn Fn(&str) -> Vec<ElementLayout>>, cache_stats: bool) {
    // Two references for the incremental layout: the same document after a forced restyle of
    // every element (`full`: were the right elements restyled?), and a fresh document parsed
    // from the serialised DOM (`fresh`: does it match a from-scratch layout?)
    let verify = |doc: &mut BaseDocument, step: &str| {
        let Some(fresh) = check else { return };
        let incremental = element_layouts(doc);
        let root = doc.root_element().id;
        doc.get_node_mut(root).unwrap().set_restyle_hint(blitz_dom::RestyleHint::restyle_subtree());
        doc.resolve(0.0);
        let full = element_layouts(doc);
        let fresh = fresh(&expand_self_closing_tags(&doc.root_element().outer_html()));
        let mut line = format!("CHECK step={step} elements={}", incremental.len());
        for (name, reference) in [("full", &full), ("fresh", &fresh)] {
            if incremental == *reference {
                line.push_str(&format!(" {name}=ok"));
            } else {
                let diffs: Vec<usize> = (0..incremental.len().max(reference.len())).filter(|&i| incremental.get(i) != reference.get(i)).collect();
                // elements whose size differs are the likely culprits; position-only differences follow from them
                let sized: Vec<usize> = diffs.iter().copied().filter(|&i| match (incremental.get(i), reference.get(i)) {
                    (Some((_, a)), Some((_, b))) => a[2..] != b[2..],
                    _ => true,
                }).collect();
                let last_sized = sized.last().copied().unwrap_or(diffs[0]);
                if std::env::var_os("BLB_CHECK_VERBOSE").is_some() {
                    let ids = element_ids(doc);
                    let html = doc.tree()[ids[last_sized]].outer_html();
                    eprintln!("CHECK {step} {name} last_size_diff html: {}", &html[..html.len().min(1500)]);
                    for &i in sized.iter().take(20) {
                        let html = doc.tree()[ids[i]].outer_html();
                        eprintln!("  {i} incremental={:?} {name}={:?} {}", incremental.get(i), reference.get(i), html.chars().take(100).collect::<String>());
                    }
                }
                line.push_str(&format!(
                    " {name}=mismatch({}_elements={} differing={} size_differing={} first={} incremental={:?} {name}={:?} last_size_diff={} incremental={:?} {name}={:?})",
                    name, reference.len(), diffs.len(), sized.len(), diffs[0], incremental.get(diffs[0]), reference.get(diffs[0]),
                    last_sized, incremental.get(last_sized), reference.get(last_sized)
                ));
            }
        }
        println!("{line}");
    };
    verify(doc, "initial");
    let style_attr = || blitz_dom::QualName::new(None, blitz_dom::ns!(), blitz_dom::local_name!("style"));
    let (root, leaves, deepest) = {
        let tree = doc.tree();
        let cb = doc.query_selector("#cb").expect("selector").expect("#cb");
        let is_body = tree[cb].element_data().is_some_and(|e| e.name.local == blitz_dom::local_name!("body"));
        let root = if is_body { cb } else { *tree[cb].children.iter().find(|c| tree[**c].is_element()).expect("root") };
        // as relayout.js: elements with a box (not display:none/contents, nor inside display:none; the children of a
        // display:contents element do take part); leaves are the innermost block-level elements
        let display = |id: NodeId| tree[id].primary_styles().map(|s| (**s).clone_display());
        let block_level = |id: NodeId| tree[id].has_boxes() && display(id).is_some_and(|d| !d.is_inline_flow());
        let mut leaves = Vec::new();
        let mut stack: Vec<(NodeId, usize)> = tree[cb].children.iter().rev().map(|c| (*c, 1)).collect();
        while let Some((id, depth)) = stack.pop() {
            if !tree[id].is_element() || display(id).is_none_or(|d| d.is_none()) {
                continue;
            }
            let kids: Vec<NodeId> = tree[id].children.iter().copied().filter(|c| tree[*c].is_element()).collect();
            if block_level(id) && !kids.iter().any(|c| block_level(*c)) {
                leaves.push((id, depth));
            }
            stack.extend(kids.into_iter().rev().map(|c| (c, depth + 1)));
        }
        let max_depth = leaves.iter().map(|l| l.1).max().unwrap_or(0);
        let deepest: Vec<NodeId> = leaves.iter().filter(|l| l.1 == max_depth).map(|l| l.0).collect();
        let kids = tree[root].children.iter().filter(|c| tree[**c].is_element() && tree[**c].has_boxes()).count();
        println!("RELAYOUT_INFO leaves={} deepest={} kids={}", leaves.len(), deepest.len(), kids);
        if std::env::var_os("LB_LEAF_DUMP").is_some() {
            for (id, _) in &leaves {
                let mut path = Vec::new();
                let mut cur = *id;
                while cur != cb {
                    let parent = tree[cur].parent.expect("parent");
                    let idx = tree[parent].children.iter().filter(|c| tree[**c].is_element()).position(|c| *c == cur).unwrap();
                    path.push(format!("{}:{idx}", tree[cur].element_data().unwrap().name.local));
                    cur = parent;
                }
                path.reverse();
                println!("LEAF {}", path.join("/"));
            }
        }
        (root, leaves.into_iter().map(|l| l.0).collect::<Vec<NodeId>>(), deepest)
    };
    let widen = |doc: &mut BaseDocument, ids: &[NodeId]| -> Vec<(NodeId, Option<String>)> {
        let saved: Vec<(NodeId, Option<String>, f32)> = {
            let tree = doc.tree();
            ids.iter().map(|&id| (id, tree[id].attr(blitz_dom::local_name!("style")).map(str::to_string), tree[id].final_layout().size.width)).collect()
        };
        let mut m = doc.mutate();
        for (id, style, w) in &saved {
            let base = style.clone().unwrap_or_default();
            m.set_attribute(*id, style_attr(), &format!("{base};width:{}px", w + 1.0));
        }
        drop(m);
        saved.into_iter().map(|(id, style, _)| (id, style)).collect()
    };
    let restore = |doc: &mut BaseDocument, saved: Vec<(NodeId, Option<String>)>| {
        let mut m = doc.mutate();
        for (id, style) in saved {
            m.set_attribute(id, style_attr(), style.as_deref().unwrap_or(""));
        }
    };
    let timed = |doc: &mut BaseDocument, step: &str| {
        #[cfg(feature = "cache-stats")]
        if cache_stats {
            taffy::reset_cache_counters();
        }
        let t = Instant::now();
        doc.resolve(0.0);
        println!("RELAYOUT step={step} resolve={}", t.elapsed().as_nanos());
        #[cfg(feature = "cache-stats")]
        if cache_stats {
            cache_stats::print_stats(doc, step);
        }
        verify(doc, step);
    };
    // root_width: 0.8x the root's current width
    let saved = {
        let (style, w) = { let n = &doc.tree()[root]; (n.attr(blitz_dom::local_name!("style")).map(str::to_string), n.final_layout().size.width) };
        let base = style.clone().unwrap_or_default();
        doc.mutate().set_attribute(root, style_attr(), &format!("{base};width:{}px", (w * 0.8).round()));
        vec![(root, style)]
    };
    timed(doc, "root_width");
    restore(doc, saved);
    doc.resolve(0.0);
    let one = vec![deepest[deepest.len() / 2]];
    let tenth: Vec<NodeId> = leaves.iter().copied().step_by(10).collect();
    for (name, ids) in [("leaf_1", &one), ("leaf_10pct", &tenth), ("leaf_all", &leaves)] {
        let saved = widen(doc, ids);
        timed(doc, name);
        restore(doc, saved);
        doc.resolve(0.0);
    }
    // append: clones of the last 10% of the root's children
    let kids: Vec<NodeId> = doc.tree()[root].children.iter().copied()
        .filter(|c| { let n = &doc.tree()[*c]; n.is_element() && n.has_boxes() }).collect();
    let n = (kids.len() / 10).max(1);
    let clones: Vec<NodeId> = {
        let mut m = doc.mutate();
        let clones: Vec<NodeId> = kids[kids.len() - n..].iter().map(|&c| m.deep_clone_node(c)).collect();
        m.append_children(root, &clones);
        clones
    };
    timed(doc, "append");
    {
        let mut m = doc.mutate();
        for c in clones {
            m.remove_node(c);
        }
    }
    doc.resolve(0.0);
}


/// `--cache-stats` (feature `cache-stats`): needs Taffy patched with `patches/taffy-cache-occupancy.patch`,
/// see `cache-occupancy/README.md`.
#[cfg(feature = "cache-stats")]
mod cache_stats {
    use super::BaseDocument;
    use blitz_dom::CopyStyleGetters;
    use std::collections::BTreeMap;

    /// `--cache-stats`: occupancy of every node's Taffy layout cache after a `resolve()`, by node kind.
    /// `CACHESIZES` gives the `size_of` of the structs involved (once); `CACHECTR step=<s>` the Taffy
    /// cache counters accumulated during that resolve; `CACHEHIST step=<s> kind=<k> final=<0|1> n=<nodes>
    /// m=<populated measure slots>:<count>,...` the joint distribution for nodes of that kind that have
    /// a `LayoutData` (nodes without one have no cache at all and are reported as `CACHEHIST ... final=-`).
    pub fn print_sizes() {
        let sizes = taffy::Cache::sizes();
        println!(
            "CACHESIZES cache={} final_entry={} measure_entry={} key={} layout_output={} measure_slots={} node={} layout_data={} element_data={} layout={}",
            sizes.cache, sizes.final_entry, sizes.measure_entry, sizes.key, sizes.layout_output, sizes.measure_slots,
            std::mem::size_of::<blitz_dom::Node>(), std::mem::size_of::<blitz_dom::node::LayoutData>(),
            std::mem::size_of::<blitz_dom::ElementData>(), std::mem::size_of::<taffy::Layout>(),
        );
    }

    /// Cheap classification of what laid the node out: `text`/`comment`/`document`; `anon_block`
    /// (anonymous block box wrapping inline content); for elements, by computed `display`:
    /// `none`, `contents`, `inline` (inline-level flow content laid out by Parley inside an inline
    /// root), `inline_root` (block-level box whose content is inline, laid out by Parley),
    /// `table`, `table_internal`, `replaced`, `block`, `flex`, `grid`.
    fn node_kind(node: &blitz_dom::Node) -> String {
        match &node.data {
            blitz_dom::NodeData::Document(_) => return "document".into(),
            blitz_dom::NodeData::Text(_) => return "text".into(),
            blitz_dom::NodeData::Comment { .. } => return "comment".into(),
            blitz_dom::NodeData::AnonymousBlock(_) => return "anon_block".into(),
            blitz_dom::NodeData::Element(_) => {}
        }
        let Some(styles) = node.primary_styles() else { return "unstyled".into() };
        let display = (**styles).clone_display();
        if display.is_none() {
            return "none".into();
        }
        if display.is_contents() {
            return "contents".into();
        }
        if node.flags.is_table_root() {
            return "table".into();
        }
        let inside = format!("{:?}", display.inside());
        if inside.starts_with("Table") {
            return "table_internal".into();
        }
        let name = &node.element_data().unwrap().name.local;
        if matches!(&**name, "img" | "input" | "textarea" | "select" | "button" | "canvas" | "video" | "svg" | "iframe") {
            return "replaced".into();
        }
        if node.flags.is_inline_root() {
            return "inline_root".into();
        }
        if display.is_inline_flow() {
            return "inline".into();
        }
        match node.taffy_display() {
            taffy::Display::Flex => "flex".into(),
            taffy::Display::Grid => "grid".into(),
            taffy::Display::Block | taffy::Display::FlowRoot => "block".into(),
            taffy::Display::None => "none".into(),
        }
    }

    pub fn print_stats(doc: &BaseDocument, step: &str) {
            let c = taffy::cache_counters();
        println!(
            "CACHECTR step={step} layout_hits={} layout_misses={} measure_hits={} measure_misses={} mode_misses={} layout_stores={} measure_stores={} measure_updates={} measure_evictions={} measure_uncacheable={} mode_change_clears={} clears={}",
            c.layout_hits, c.layout_misses, c.measure_hits, c.measure_misses, c.mode_misses, c.layout_stores, c.measure_stores, c.measure_updates, c.measure_evictions, c.measure_uncacheable, c.mode_change_clears, c.clears
        );
        // (kind, final: 0/1, or 2 = no LayoutData) -> histogram over populated measure slots
        let mut hist: BTreeMap<(String, u8), [u64; 10]> = BTreeMap::new();
        let mut nodes = 0u64;
        for (_, node) in doc.tree().iter() {
            nodes += 1;
            let kind = node_kind(node);
            let layout_data = match &node.data {
                blitz_dom::NodeData::Element(e) | blitz_dom::NodeData::AnonymousBlock(e) => e.layout_data.as_deref(),
                blitz_dom::NodeData::Document(d) => d.layout_data.as_deref(),
                _ => None,
            };
            let (fin, m) = match layout_data {
                Some(ld) => {
                    let occ = ld.cache.occupancy();
                    (occ.final_populated as u8, occ.measure_populated as usize)
                }
                None => (2, 0),
            };
            hist.entry((kind, fin)).or_insert([0; 10])[m] += 1;
        }
        println!("CACHENODES step={step} nodes={nodes}");
        for ((kind, fin), counts) in hist {
            let fin = match fin { 0 => "0", 1 => "1", _ => "-" };
            let n: u64 = counts.iter().sum();
            let m: Vec<String> = counts.iter().enumerate().filter(|(_, c)| **c > 0).map(|(i, c)| format!("{i}:{c}")).collect();
            println!("CACHEHIST step={step} kind={kind} final={fin} n={n} m={}", m.join(","));
        }
    }
}
