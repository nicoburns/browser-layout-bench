//! Loads a local HTML file into Blitz and times a non-incremental initial `resolve()` (style,
//! construct, layout, paint tree) `--iters` times; optionally hashes the final boxes or renders a PNG.
use std::fs;
use std::hash::Hasher;
use std::sync::Arc;
use std::time::Instant;

use anyrender::render_to_buffer;
use anyrender_vello_cpu::VelloCpuImageRenderer;
use blitz_dom::{BaseDocument, DocumentConfig, StyleThreading};
use blitz_html::{HtmlDocument, HtmlProvider};
use blitz_paint::paint_scene;
use blitz_traits::net::{Bytes, NetHandler, NetProvider, Request};
use blitz_traits::shell::{ColorScheme, Viewport};

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
}

fn parse_args() -> Args {
    let mut args = Args { file: String::new(), width: 1280, height: 800, iters: 5, parallel: false, screenshot: None, hash: false, boxes: false };
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
            incremental: Some(false),
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

        if i + 1 == args.iters {
            if args.hash {
                println!("HASH {:016x}", layout_hash(doc.as_ref()));
                let tree = doc.as_ref().tree();
                let root = tree.iter().find(|(_, n)| n.attr(blitz_dom::local_name!("id")) == Some("cb"))
                    .and_then(|(_, cb)| cb.children.iter().find(|c| tree[**c].is_element()).map(|c| tree[*c].final_layout()));
                if let Some(l) = root {
                    println!("ROOT {}x{}", l.size.width, l.size.height);
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
