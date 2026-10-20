//! Generates the synthetic benchmark corpus: Taffy benchmark-shaped trees serialised to HTML
//! with inline styles (`gen html <dir>`), and times Taffy itself on the same trees (`gen bench`).
use std::fmt::Write as _;
use std::fs;
use std::path::Path;
use std::time::Instant;

use rand::{Rng, SeedableRng};
use rand_chacha::ChaCha8Rng;
use taffy::prelude::*;
use taffy::style::*;
use taffy_benchmarks::{BuildTree, BuildTreeExt, FixedStyleGenerator, GenStyle, TaffyTreeBuilder};

const SEED: u64 = 12345;
const HUGE: f32 = 1_000_000.0;

struct Case {
    name: String,
    tree: TaffyTree,
    root: NodeId,
    avail: Size<AvailableSpace>,
}

// ---- style generators (mirroring taffy/benches/benches/flexbox.rs) ----

fn random_dimension(rng: &mut impl Rng) -> Dimension {
    match rng.random_range(0.0..=1.0) {
        r if r < 0.2 => auto(),
        r if r < 0.8 => length(rng.random_range(0.0..500.0)),
        _ => percent(rng.random_range(0.0..1.0)),
    }
}

/// Like [`random_dimension`] but never a percentage: percentage heights of flex items in an
/// auto-height container compute to `auto` in CSS (Chrome, Servo) while Taffy resolves them.
fn random_height(rng: &mut impl Rng) -> Dimension {
    match rng.random_range(0.0..=1.0) {
        r if r < 0.2 => auto(),
        _ => length(rng.random_range(0.0..500.0)),
    }
}

fn random_inset(rng: &mut impl Rng) -> LengthPercentageAuto {
    match rng.random_range(0.0..=1.0) {
        r if r < 0.4 => auto(),
        r if r < 0.8 => length(rng.random_range(0.0..500.0)),
        _ => percent(rng.random_range(0.0..1.0)),
    }
}

#[derive(Clone)]
struct RandomStyleGenerator;
impl GenStyle<Style> for RandomStyleGenerator {
    fn create_leaf_style(&mut self, rng: &mut impl Rng) -> Style {
        Style { size: Size { width: random_dimension(rng), height: random_height(rng) }, ..Default::default() }
    }
    fn create_container_style(&mut self, rng: &mut impl Rng) -> Style {
        Style { size: Size { width: random_dimension(rng), height: random_height(rng) }, ..Default::default() }
    }
}

#[derive(Clone)]
struct RandomAbsoluteStyleGenerator;
impl GenStyle<Style> for RandomAbsoluteStyleGenerator {
    fn create_leaf_style(&mut self, rng: &mut impl Rng) -> Style {
        Style {
            position: Position::Absolute,
            inset: Rect {
                left: random_inset(rng),
                right: random_inset(rng),
                top: random_inset(rng),
                bottom: random_inset(rng),
            },
            size: Size { width: random_dimension(rng), height: random_height(rng) },
            ..Default::default()
        }
    }
    fn create_container_style(&mut self, rng: &mut impl Rng) -> Style {
        Style {
            position: Position::Relative,
            size: Size { width: random_dimension(rng), height: random_height(rng) },
            ..Default::default()
        }
    }
}

// ---- grid trees (mirroring taffy/benches/benches/grid.rs) ----

fn random_track(rng: &mut impl Rng) -> TrackSizingFunction {
    match rng.random_range(0.0..=1.0) {
        r if r < 0.2 => auto(),
        r if r < 0.35 => min_content(),
        r if r < 0.5 => max_content(),
        r if r < 0.7 => fr(rng.random_range(1..4) as f32),
        r if r < 0.85 => length(rng.random_range(50.0..200.0)),
        r if r < 0.93 => percent(rng.random_range(0.05..0.3)),
        _ => minmax(length(rng.random_range(20.0..80.0)), fr(1.0)),
    }
}

fn random_tracks(rng: &mut impl Rng, n: usize) -> Vec<GridTemplateComponent<String>> {
    (0..n).map(|_| GridTemplateComponent::Single(random_track(rng))).collect()
}

fn grid_style(rng: &mut impl Rng, cols: usize, rows: usize) -> Style {
    Style {
        display: Display::Grid,
        grid_template_columns: random_tracks(rng, cols),
        grid_template_rows: random_tracks(rng, rows),
        ..Default::default()
    }
}

fn build_wide_grid(n: usize) -> (TaffyTree, NodeId) {
    let rng = &mut ChaCha8Rng::seed_from_u64(SEED);
    let mut tree = TaffyTree::new();
    let children: Vec<_> = (0..n * n).map(|_| tree.new_leaf(Style::default()).unwrap()).collect();
    let root = tree.new_with_children(grid_style(rng, n, n), &children).unwrap();
    (tree, root)
}

fn build_deep_grid(tracks: usize, levels: usize) -> (TaffyTree, NodeId) {
    fn build(tree: &mut TaffyTree, rng: &mut impl Rng, tracks: usize, level: usize) -> NodeId {
        if level == 0 {
            return tree.new_leaf(Style { size: Size { width: length(20.0), height: length(20.0) }, ..Default::default() }).unwrap();
        }
        let children: Vec<_> = (0..tracks * tracks).map(|_| build(tree, rng, tracks, level - 1)).collect();
        tree.new_with_children(grid_style(rng, tracks, tracks), &children).unwrap()
    }
    let rng = &mut ChaCha8Rng::seed_from_u64(SEED);
    let mut tree = TaffyTree::new();
    let root = build(&mut tree, rng, tracks, levels);
    (tree, root)
}

// ---- case list ----

fn flex<G: GenStyle<Style> + Clone>(name: &str, gen_: G, build: impl FnOnce(&mut TaffyTreeBuilder<ChaCha8Rng, G>), avail: Size<AvailableSpace>) -> Case {
    let mut builder = TaffyTreeBuilder::<ChaCha8Rng, G>::new(gen_);
    build(&mut builder);
    let (tree, root) = builder.into_tree_and_root();
    Case { name: name.to_string(), tree, root, avail }
}

fn case(name: &str, (tree, root): (TaffyTree, NodeId), avail: Size<AvailableSpace>) -> Case {
    Case { name: name.to_string(), tree, root, avail }
}

fn all_cases() -> Vec<Case> {
    let max = Size::MAX_CONTENT;
    let fixed_grow = || FixedStyleGenerator(Style { size: length(10.0), flex_grow: 1.0, ..Default::default() });
    let fixed_margin = || FixedStyleGenerator(Style { flex_grow: 1.0, margin: length(10.0), ..Default::default() });
    let mut cases = vec![];
    for n in [1_000, 10_000] {
        cases.push(flex(&format!("flex/huge_nested/{n}"), fixed_grow(), |b| b.build_deep_hierarchy(n, 10), max));
        cases.push(flex(&format!("flex/wide/{n}"), RandomStyleGenerator, |b| b.build_flat_hierarchy(n), max));
        cases.push(flex(&format!("flex/absolute/{n}"), RandomAbsoluteStyleGenerator, |b| b.build_flat_hierarchy(n), max));
        cases.push(flex(&format!("flex/deep_auto/{n}"), fixed_margin(), |b| b.build_deep_hierarchy(n, 2), max));
        cases.push(flex(&format!("flex/deep_random/{n}"), RandomStyleGenerator, |b| b.build_deep_hierarchy(n, 2), max));
    }
    for depth in [50, 100] {
        cases.push(flex(&format!("flex/superdeep/{depth}"), fixed_margin(), |b| b.build_super_deep_hierarchy(depth, 3), max));
    }
    for n in [31, 100] {
        cases.push(case(&format!("grid/wide/{n}x{n}"), build_wide_grid(n), max));
    }
    cases.push(case("grid/deep/2x2x5", build_deep_grid(2, 5), Size { width: length(12000.0), height: length(12000.0) }));
    cases.push(case("grid/deep/3x3x4", build_deep_grid(3, 4), Size { width: length(12000.0), height: length(12000.0) }));
    cases.push(case("grid/superdeep/100", build_deep_grid(1, 100), max));
    cases
}

// ---- CSS serialisation ----

fn num(v: f32) -> String {
    if v == v.trunc() { format!("{}", v as i64) } else { format!("{v}") }
}

fn cl(c: CompactLength) -> String {
    match c.tag() {
        CompactLength::LENGTH_TAG => format!("{}px", num(c.value())),
        CompactLength::PERCENT_TAG => format!("{}%", num(c.value() * 100.0)),
        CompactLength::AUTO_TAG => "auto".into(),
        CompactLength::FR_TAG => format!("{}fr", num(c.value())),
        CompactLength::MIN_CONTENT_TAG => "min-content".into(),
        CompactLength::MAX_CONTENT_TAG => "max-content".into(),
        CompactLength::FIT_CONTENT_PX_TAG => format!("fit-content({}px)", num(c.value())),
        CompactLength::FIT_CONTENT_PERCENT_TAG => format!("fit-content({}%)", num(c.value() * 100.0)),
        tag => panic!("unsupported CompactLength tag {tag:#x}"),
    }
}

fn same(a: CompactLength, b: CompactLength) -> bool {
    a.tag() == b.tag() && a.value().to_bits() == b.value().to_bits()
}

fn track(t: &TrackSizingFunction) -> String {
    let (min, max) = (t.min.into_raw(), t.max.into_raw());
    if same(min, max) {
        cl(min)
    } else if min.tag() == CompactLength::AUTO_TAG && matches!(max.tag(), CompactLength::FR_TAG | CompactLength::FIT_CONTENT_PX_TAG | CompactLength::FIT_CONTENT_PERCENT_TAG) {
        cl(max)
    } else {
        format!("minmax({}, {})", cl(min), cl(max))
    }
}

fn template(components: &[GridTemplateComponent<String>]) -> String {
    components
        .iter()
        .map(|c| match c {
            GridTemplateComponent::Single(t) => track(t),
            GridTemplateComponent::Repeat(rep) => {
                let count = match rep.count {
                    RepetitionCount::Count(n) => n.to_string(),
                    RepetitionCount::AutoFill => "auto-fill".into(),
                    RepetitionCount::AutoFit => "auto-fit".into(),
                };
                let tracks: Vec<_> = rep.tracks.iter().map(track).collect();
                format!("repeat({count}, {})", tracks.join(" "))
            }
        })
        .collect::<Vec<_>>()
        .join(" ")
}

fn placement(p: &GridPlacement<String>) -> String {
    match p {
        GridPlacement::Auto => "auto".into(),
        GridPlacement::Line(l) => l.as_i16().to_string(),
        GridPlacement::NamedLine(name, n) => format!("{n} {name}"),
        GridPlacement::Span(n) => format!("span {n}"),
        GridPlacement::NamedSpan(name, n) => format!("span {n} {name}"),
    }
}

fn align_items(a: AlignItems) -> Option<&'static str> {
    use AlignItemsKeyword as K;
    Some(match a.keyword {
        K::Normal => return None,
        K::Start => "start",
        K::End => "end",
        K::FlexStart => "flex-start",
        K::FlexEnd => "flex-end",
        K::SelfStart => "self-start",
        K::SelfEnd => "self-end",
        K::Center => "center",
        K::Baseline => "baseline",
        K::Stretch => "stretch",
    })
}

fn align_content(a: AlignContent) -> Option<&'static str> {
    use AlignContentKeyword as K;
    Some(match a.keyword {
        K::Normal => return None,
        K::Start => "start",
        K::End => "end",
        K::FlexStart => "flex-start",
        K::FlexEnd => "flex-end",
        K::Center => "center",
        K::Stretch => "stretch",
        K::SpaceBetween => "space-between",
        K::SpaceEvenly => "space-evenly",
        K::SpaceAround => "space-around",
    })
}

fn overflow(o: Overflow) -> &'static str {
    match o {
        Overflow::Visible => "visible",
        Overflow::Clip => "clip",
        Overflow::Hidden => "hidden",
        Overflow::Scroll => "scroll",
    }
}

/// Serialises the non-default parts of a Taffy style as inline CSS. The stylesheet in
/// [`page`] supplies Taffy's defaults that differ from CSS (`display:flex`, `box-sizing:border-box`).
fn css(s: &Style) -> String {
    let mut out = String::new();
    macro_rules! prop {
        ($name:expr, $val:expr) => {{
            let _ = write!(out, "{}:{};", $name, $val);
        }};
    }
    match s.display {
        Display::Flex => {}
        Display::Block => prop!("display", "block"),
        Display::FlowRoot => prop!("display", "flow-root"),
        Display::Grid => prop!("display", "grid"),
        Display::None => prop!("display", "none"),
    }
    if s.box_sizing == BoxSizing::ContentBox { prop!("box-sizing", "content-box"); }
    if s.overflow.x != Overflow::Visible || s.overflow.y != Overflow::Visible {
        prop!("overflow", format!("{} {}", overflow(s.overflow.x), overflow(s.overflow.y)));
    }
    match s.position {
        Position::Static => {}
        Position::Relative => prop!("position", "relative"),
        Position::Absolute => prop!("position", "absolute"),
        Position::Fixed => prop!("position", "fixed"),
        Position::Sticky => prop!("position", "sticky"),
    }
    for (name, v) in [("left", s.inset.left), ("right", s.inset.right), ("top", s.inset.top), ("bottom", s.inset.bottom)] {
        if !v.is_auto() { prop!(name, cl(v.into_raw())); }
    }
    for (name, v) in [("width", s.size.width), ("height", s.size.height)] {
        if !v.is_auto() { prop!(name, cl(v.into_raw())); }
    }
    for (name, v) in [("min-width", s.min_size.width), ("min-height", s.min_size.height), ("max-width", s.max_size.width), ("max-height", s.max_size.height)] {
        if !v.is_auto() { prop!(name, cl(v.into_raw())); }
    }
    if let Some(r) = s.aspect_ratio { prop!("aspect-ratio", num(r)); }
    for (name, v) in [("margin-left", s.margin.left), ("margin-right", s.margin.right), ("margin-top", s.margin.top), ("margin-bottom", s.margin.bottom)] {
        if !same(v.into_raw(), CompactLength::ZERO) { prop!(name, cl(v.into_raw())); }
    }
    for (name, v) in [("padding-left", s.padding.left), ("padding-right", s.padding.right), ("padding-top", s.padding.top), ("padding-bottom", s.padding.bottom)] {
        if !same(v.into_raw(), CompactLength::ZERO) { prop!(name, cl(v.into_raw())); }
    }
    let b = &s.border;
    if [b.left, b.right, b.top, b.bottom].iter().any(|v| !same(v.into_raw(), CompactLength::ZERO)) {
        prop!("border-style", "solid");
        prop!("border-color", "transparent");
        prop!("border-width", format!("{} {} {} {}", cl(b.top.into_raw()), cl(b.right.into_raw()), cl(b.bottom.into_raw()), cl(b.left.into_raw())));
    }
    if let Some(v) = align_items(s.align_items) { prop!("align-items", v); }
    if let Some(v) = s.align_self.and_then(align_items) { prop!("align-self", v); }
    if let Some(v) = align_items(s.justify_items) { prop!("justify-items", v); }
    if let Some(v) = s.justify_self.and_then(align_items) { prop!("justify-self", v); }
    if let Some(v) = align_content(s.align_content) { prop!("align-content", v); }
    if let Some(v) = align_content(s.justify_content) { prop!("justify-content", v); }
    if !same(s.gap.width.into_raw(), CompactLength::ZERO) || !same(s.gap.height.into_raw(), CompactLength::ZERO) {
        prop!("gap", format!("{} {}", cl(s.gap.height.into_raw()), cl(s.gap.width.into_raw())));
    }
    match s.flex_direction {
        FlexDirection::Row => {}
        FlexDirection::Column => prop!("flex-direction", "column"),
        FlexDirection::RowReverse => prop!("flex-direction", "row-reverse"),
        FlexDirection::ColumnReverse => prop!("flex-direction", "column-reverse"),
    }
    match s.flex_wrap {
        FlexWrap::NoWrap => {}
        FlexWrap::Wrap => prop!("flex-wrap", "wrap"),
        FlexWrap::WrapReverse => prop!("flex-wrap", "wrap-reverse"),
        FlexWrap::Balance | FlexWrap::BalanceReverse => panic!("flex-wrap: balance has no CSS equivalent"),
    }
    if !s.flex_basis.is_auto() { prop!("flex-basis", cl(s.flex_basis.into_raw())); }
    if s.flex_grow != 0.0 { prop!("flex-grow", num(s.flex_grow)); }
    if s.flex_shrink != 1.0 { prop!("flex-shrink", num(s.flex_shrink)); }
    if !s.grid_template_rows.is_empty() { prop!("grid-template-rows", template(&s.grid_template_rows)); }
    if !s.grid_template_columns.is_empty() { prop!("grid-template-columns", template(&s.grid_template_columns)); }
    if !s.grid_auto_rows.is_empty() { prop!("grid-auto-rows", s.grid_auto_rows.iter().map(track).collect::<Vec<_>>().join(" ")); }
    if !s.grid_auto_columns.is_empty() { prop!("grid-auto-columns", s.grid_auto_columns.iter().map(track).collect::<Vec<_>>().join(" ")); }
    match s.grid_auto_flow {
        GridAutoFlow::Row => {}
        GridAutoFlow::Column => prop!("grid-auto-flow", "column"),
        GridAutoFlow::RowDense => prop!("grid-auto-flow", "row dense"),
        GridAutoFlow::ColumnDense => prop!("grid-auto-flow", "column dense"),
    }
    if s.grid_row.start != GridPlacement::Auto || s.grid_row.end != GridPlacement::Auto {
        prop!("grid-row", format!("{} / {}", placement(&s.grid_row.start), placement(&s.grid_row.end)));
    }
    if s.grid_column.start != GridPlacement::Auto || s.grid_column.end != GridPlacement::Auto {
        prop!("grid-column", format!("{} / {}", placement(&s.grid_column.start), placement(&s.grid_column.end)));
    }
    out
}

fn leaf_colour(i: u32) -> String {
    let c = i.wrapping_add(1).wrapping_mul(2654435761) >> 8;
    format!("#{:06x}", c & 0xffffff)
}

fn write_node(out: &mut String, tree: &TaffyTree, node: NodeId, counter: &mut u32) {
    let children = tree.children(node).unwrap();
    let mut style = css(tree.style(node).unwrap());
    if children.is_empty() {
        let _ = write!(style, "background:{};", leaf_colour(*counter));
    }
    *counter += 1;
    let _ = write!(out, "<div style=\"{style}\">");
    for child in children {
        write_node(out, tree, child, counter);
    }
    out.push_str("</div>");
}

fn avail_px(a: AvailableSpace) -> f32 {
    match a {
        AvailableSpace::Definite(v) => v,
        AvailableSpace::MinContent => 0.0,
        AvailableSpace::MaxContent => HUGE,
    }
}

fn page(case: &Case) -> (String, u32) {
    let (w, h) = (avail_px(case.avail.width), avail_px(case.avail.height));
    let mut out = String::new();
    let _ = write!(
        out,
        "<!DOCTYPE html>\n<html><head><meta charset=\"utf-8\"><title>{}</title>\n<style>\nhtml,body{{margin:0;padding:0}}\ndiv{{display:flex;box-sizing:border-box}}\n#cb{{position:relative;width:{}px;height:{}px}}\n#cb>div{{position:absolute;left:0;top:0}}\n</style></head><body>\n<div id=\"cb\">\n",
        case.name, num(w), num(h)
    );
    let mut count = 0;
    write_node(&mut out, &case.tree, case.root, &mut count);
    out.push_str("</div>\n</body></html>\n");
    (out, count)
}

fn all_nodes(tree: &TaffyTree, root: NodeId) -> Vec<NodeId> {
    let mut nodes = vec![root];
    let mut i = 0;
    while i < nodes.len() {
        nodes.extend(tree.children(nodes[i]).unwrap());
        i += 1;
    }
    nodes
}

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let cmd = args.first().map(String::as_str).unwrap_or("list");
    let filter = |name: &str, pat: Option<&String>| pat.is_none_or(|p| name.contains(p.as_str()));
    match cmd {
        "list" => {
            for c in all_cases() {
                println!("{}\t{} nodes", c.name, all_nodes(&c.tree, c.root).len());
            }
        }
        "html" => {
            let dir = Path::new(args.get(1).expect("gen html <out_dir> [filter]"));
            fs::create_dir_all(dir).unwrap();
            let mut manifest = String::new();
            for c in all_cases() {
                if !filter(&c.name, args.get(2)) { continue; }
                let (html, nodes) = page(&c);
                let file = format!("{}.html", c.name.replace('/', "_"));
                fs::write(dir.join(&file), html).unwrap();
                let _ = writeln!(manifest, "{}\t{}\t{}\t{}\t{}", c.name, file, num(avail_px(c.avail.width)), num(avail_px(c.avail.height)), nodes);
            }
            fs::write(dir.join("manifest.tsv"), manifest).unwrap();
        }
        "bench" => {
            let iters: usize = args.iter().position(|a| a == "--iters").and_then(|i| args.get(i + 1)).map(|v| v.parse().unwrap()).unwrap_or(10);
            let pat = args.get(1).filter(|a| !a.starts_with("--"));
            // Mirror the generated page: the tree root is an absolutely positioned child of a
            // viewport-sized `#cb`, so it is laid out in one pass like in the browsers.
            let wrapped = args.iter().any(|a| a == "--wrapped");
            for mut c in all_cases() {
                if !filter(&c.name, pat) { continue; }
                if wrapped {
                    let (w, h) = (avail_px(c.avail.width), avail_px(c.avail.height));
                    let mut root_style = c.tree.style(c.root).unwrap().clone();
                    root_style.position = Position::Absolute;
                    root_style.inset.left = length(0.0);
                    root_style.inset.top = length(0.0);
                    c.tree.set_style(c.root, root_style).unwrap();
                    let cb_style = Style { position: Position::Relative, size: Size { width: length(w), height: length(h) }, ..Default::default() };
                    c.root = c.tree.new_with_children(cb_style, &[c.root]).unwrap();
                    c.avail = Size { width: AvailableSpace::Definite(w), height: AvailableSpace::Definite(h) };
                }
                let nodes = all_nodes(&c.tree, c.root);
                for i in 0..iters + 2 {
                    for &n in &nodes { c.tree.mark_dirty(n).unwrap(); }
                    let t = Instant::now();
                    c.tree.compute_layout(c.root, c.avail).unwrap();
                    let ns = t.elapsed().as_nanos();
                    if i >= 2 { println!("taffy\t{}\t{ns}", c.name); }
                }
                let l = c.tree.layout(c.root).unwrap();
                eprintln!("{}: root {}x{}", c.name, l.size.width, l.size.height);
            }
        }
        other => panic!("unknown command {other}"),
    }
}
