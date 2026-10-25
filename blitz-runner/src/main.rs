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
}

fn parse_args() -> Args {
    let mut args = Args { file: String::new(), width: 1280, height: 800, iters: 5, parallel: false, screenshot: None, hash: false, boxes: false, dump: false, relayout: false };
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
            _ => args.file = a,
        }
    }
    assert!(!args.file.is_empty(), "usage: blitz-runner <file.html> [--width W] [--height H] [--iters N] [--parallel] [--hash] [--boxes] [--screenshot out.png]");
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
        let t = Instant::now();
        doc.as_mut().resolve(0.0);
        let resolve = t.elapsed().as_nanos();
        println!("BLITZ parse={parse} resolve={resolve}");
        if args.relayout {
            relayout_steps(doc.as_mut());
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

fn relayout_steps(doc: &mut BaseDocument) {
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
        let t = Instant::now();
        doc.resolve(0.0);
        println!("RELAYOUT step={step} resolve={}", t.elapsed().as_nanos());
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
