//! The PanGUI benchmark templates (`pangui/*.txt`, copied from Taffy's `benches/pangui/`), built
//! into Taffy trees with the same translation as Taffy's `benches/benches/pangui.rs`.
use std::path::Path;

use rand::Rng;
use taffy::prelude::*;
use taffy::style::Style;
use taffy_benchmarks::pangui_template::{parse_test_case, BenchmarkSize, FlowDirection, LayoutNode, SizeMode, WrapMode};
use taffy_benchmarks::{BuildTree, BuildTreeExt, GenStyle, TaffyTreeBuilder};

use crate::Case;

/// The size that the root node is laid out into along an axis in which it does not have a size in pixels
const DEFAULT_ROOT_SIZE: f32 = 1000.0;

fn is_mode(size: &Option<BenchmarkSize>, mode: SizeMode) -> bool {
    size.is_some_and(|size| size.mode == mode)
}

fn dimension(size: &Option<BenchmarkSize>) -> Dimension {
    match size {
        Some(BenchmarkSize { mode: SizeMode::Pixels, value }) => length(*value),
        Some(BenchmarkSize { mode: SizeMode::Percentage, value }) => percent(*value),
        // `Expand` is translated to `flex-grow` or `align-items: stretch`, and `Ratio` to `aspect-ratio`
        Some(BenchmarkSize { mode: SizeMode::Fit | SizeMode::Expand | SizeMode::Ratio, .. }) | None => auto(),
    }
}

fn min_max_size(size: &Option<BenchmarkSize>, property: &str) -> LengthPercentageAuto {
    match size {
        Some(BenchmarkSize { mode: SizeMode::Pixels, value }) => length(*value),
        Some(BenchmarkSize { mode: SizeMode::Percentage, value }) => percent(*value),
        Some(BenchmarkSize { mode, .. }) => panic!("{mode:?} is not supported as a value of {property}"),
        None => auto(),
    }
}

/// Translate a node of a PanGUI template into a flexbox style. `parent_is_row` is whether the parent of the
/// node lays out its children horizontally.
fn style(node: &LayoutNode, parent_is_row: bool) -> Style {
    let (main_size, main_min_size) =
        if parent_is_row { (&node.width, &node.min_width) } else { (&node.height, &node.min_height) };

    // A node which expands along the main axis of its parent shares out all of the space in the parent
    // (`flex: <weight> 1 0` with a minimum size of 0, as PanGUI has no automatic minimum size). A node which
    // has `Expand` as its minimum size grows from its own size (`flex: <weight> 0 auto`). A node which expands
    // along the cross axis is stretched by `align-items`.
    let expands = is_mode(main_size, SizeMode::Expand);
    let (flex_grow, flex_shrink, flex_basis) = match (main_size, main_min_size) {
        (Some(BenchmarkSize { mode: SizeMode::Expand, value }), _) => (*value, 1.0, length(0.0)),
        (_, Some(BenchmarkSize { mode: SizeMode::Expand, value })) => (*value, 0.0, auto()),
        _ => (0.0, 0.0, auto()),
    };

    let mut min_size = Size { width: auto(), height: auto() };
    if !(parent_is_row && is_mode(&node.min_width, SizeMode::Expand)) {
        min_size.width = min_max_size(&node.min_width, "MinWidth");
    }
    if !(!parent_is_row && is_mode(&node.min_height, SizeMode::Expand)) {
        min_size.height = min_max_size(&node.min_height, "MinHeight");
    }
    if expands {
        if parent_is_row && node.min_width.is_none() {
            min_size.width = length(0.0);
        }
        if !parent_is_row && node.min_height.is_none() {
            min_size.height = length(0.0);
        }
    }

    let aspect_ratio = match (&node.width, &node.height) {
        (Some(BenchmarkSize { mode: SizeMode::Ratio, value }), _) => Some(*value),
        (_, Some(BenchmarkSize { mode: SizeMode::Ratio, value })) => Some(1.0 / *value),
        _ => None,
    };

    let gap = length(node.gap.unwrap_or(0.0));
    Style {
        display: Display::Flex,
        flex_direction: match node.flow_direction {
            Some(FlowDirection::Horizontal) => FlexDirection::Row,
            Some(FlowDirection::Vertical) | None => FlexDirection::Column,
        },
        flex_wrap: match node.wrap {
            Some(WrapMode::Auto) => FlexWrap::Wrap,
            Some(WrapMode::NoWrap) | None => FlexWrap::NoWrap,
        },
        size: Size { width: dimension(&node.width), height: dimension(&node.height) },
        min_size,
        max_size: Size {
            width: min_max_size(&node.max_width, "MaxWidth"),
            height: min_max_size(&node.max_height, "MaxHeight"),
        },
        aspect_ratio,
        gap: Size { width: gap, height: gap },
        padding: Rect {
            left: length(node.padding_left.unwrap_or(0.0)),
            right: length(node.padding_right.unwrap_or(0.0)),
            top: length(node.padding_top.unwrap_or(0.0)),
            bottom: length(node.padding_bottom.unwrap_or(0.0)),
        },
        margin: Rect {
            left: length(node.margin_left.unwrap_or(0.0)),
            right: length(node.margin_right.unwrap_or(0.0)),
            top: length(node.margin_top.unwrap_or(0.0)),
            bottom: length(node.margin_bottom.unwrap_or(0.0)),
        },
        flex_grow,
        flex_shrink,
        flex_basis,
        align_items: AlignItems::STRETCH,
        justify_content: JustifyContent::START,
        align_content: AlignContent::START,
        ..Default::default()
    }
}

/// Gives the root node of the tree the style of the root node of a template.
/// The styles of all other nodes are passed to [`BuildTree::create_node_with_style`].
#[derive(Clone)]
struct RootStyle(Style);
impl GenStyle<Style> for RootStyle {
    fn create_leaf_style(&mut self, _rng: &mut impl Rng) -> Style {
        Style::default()
    }
    fn create_container_style(&mut self, _rng: &mut impl Rng) -> Style {
        Style::default()
    }
    fn create_root_style(&mut self, _rng: &mut impl Rng) -> Style {
        self.0.clone()
    }
}

fn build_children<R: Rng, B: BuildTree<R, RootStyle>>(builder: &mut B, parent: &LayoutNode) -> Vec<B::Node> {
    let parent_is_row = parent.flow_direction == Some(FlowDirection::Horizontal);
    parent
        .children
        .iter()
        .map(|child| {
            let children = build_children(builder, child);
            builder.create_node_with_style(style(child, parent_is_row), &children)
        })
        .collect()
}

/// The size that the root node is laid out into: its own size in pixels where it has one
fn root_size(size: &Option<BenchmarkSize>) -> f32 {
    match size {
        Some(BenchmarkSize { mode: SizeMode::Pixels, value }) => *value,
        _ => DEFAULT_ROOT_SIZE,
    }
}

/// Read and parse every template in the `pangui` directory, in order of name
fn templates() -> Vec<(String, LayoutNode)> {
    let directory = Path::new(env!("CARGO_MANIFEST_DIR")).join("pangui");
    let mut paths: Vec<_> = std::fs::read_dir(&directory).unwrap().map(|entry| entry.unwrap().path()).collect();
    paths.sort();
    paths
        .iter()
        .map(|path| {
            let file_name = path.file_name().unwrap().to_str().unwrap();
            let text = std::fs::read_to_string(path).unwrap();
            let test_case = parse_test_case(file_name, &text).unwrap_or_else(|error| panic!("{file_name}: {error}"));
            (test_case.name, test_case.root_node.unwrap())
        })
        .collect()
}

/// One case per template, laid out into the root's own pixel size (1000px along an axis without one),
/// as in Taffy's benchmark.
pub fn cases() -> Vec<Case> {
    templates()
        .into_iter()
        .map(|(name, root)| {
            // The root node has no parent. PanGUI's own translation treats it as the child of a column.
            let mut builder = TaffyTreeBuilder::new(RootStyle(style(&root, false)));
            let children = build_children(&mut builder, &root);
            builder.set_root_children(&children);
            let (tree, root_node) = builder.into_tree_and_root();
            let avail = Size { width: length(root_size(&root.width)), height: length(root_size(&root.height)) };
            Case { name: format!("pangui/{name}"), tree, root: root_node, avail }
        })
        .collect()
}
