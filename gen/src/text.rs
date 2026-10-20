//! Text-heavy pages: deterministic English-like prose (a fixed word list sampled with the seed)
//! set in the font shipped in `fonts/`, so that text shaping and line breaking can be compared
//! between the engines. These pages have no Taffy tree.
use std::fmt::Write as _;

use rand::seq::IndexedRandom;
use rand::{Rng, SeedableRng};
use rand_chacha::ChaCha8Rng;

use crate::{leaf_colour, SEED};

pub struct TextCase {
    pub name: String,
    pub html: String,
    /// Number of elements inside `#cb`
    pub nodes: u32,
}

/// Column width of every text page
pub const WIDTH: f32 = 960.0;

pub const FONT_FILES: [&str; 4] =
    ["DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans-Oblique.ttf", "DejaVuSans-BoldOblique.ttf"];

const WORDS: &[&str] = &[
    "the", "of", "and", "to", "in", "a", "is", "that", "for", "it", "as", "was", "with", "be", "by", "on", "not",
    "he", "this", "are", "or", "his", "from", "at", "which", "but", "have", "an", "had", "they", "you", "were",
    "their", "one", "all", "we", "can", "her", "has", "there", "been", "if", "more", "when", "will", "would",
    "who", "so", "no", "layout", "engine", "text", "paragraph", "line", "breaking", "shaping", "glyph", "font",
    "width", "height", "margin", "padding", "border", "container", "item", "flex", "grid", "block", "inline",
    "measure", "intrinsic", "content", "available", "space", "definite", "indefinite", "stretch", "baseline",
    "benchmark", "millisecond", "deterministic", "corpus", "viewport", "pixel", "column", "row", "wrap", "gap",
    "serialise", "compare", "engines", "identical", "page", "style", "cascade", "selector", "computed", "value",
    "inherit", "initial", "specified", "resolved", "fragment", "box", "tree", "construction", "reflow", "paint",
    "display", "list", "stacking", "context", "scroll", "overflow", "hidden", "visible", "clip", "absolute",
    "relative", "position", "inset", "auto", "percent", "length", "calc", "minimum", "maximum", "preferred",
    "fit", "expand", "ratio", "aspect", "nested", "deep", "wide", "superdeep", "random", "fixed", "weight",
    "constraint", "perpendicular", "vertical", "horizontal", "stack", "simple", "many", "few", "wrapping",
    "extraordinarily", "incomprehensibly", "characterisation", "internationalisation", "antidisestablishment",
];

fn word(rng: &mut ChaCha8Rng) -> &'static str {
    WORDS.choose(rng).unwrap()
}

/// `n` words as a sentence: capitalised, with a comma somewhere in longer sentences, ending in a full stop.
fn sentence(rng: &mut ChaCha8Rng, n: usize) -> String {
    let comma = if n >= 8 { rng.random_range(3..n - 2) } else { usize::MAX };
    let mut out = String::new();
    for i in 0..n {
        let w = word(rng);
        if i == 0 {
            let mut chars = w.chars();
            out.extend(chars.next().unwrap().to_uppercase());
            out.push_str(chars.as_str());
        } else {
            out.push(' ');
            out.push_str(w);
        }
        if i == comma {
            out.push(',');
        }
    }
    out.push('.');
    out
}

/// Sentences of 6 to 14 words until at least `min_words` words have been written
fn prose(rng: &mut ChaCha8Rng, min_words: usize) -> String {
    let mut out = String::new();
    let mut words = 0;
    while words < min_words {
        let n = rng.random_range(6..=14);
        if !out.is_empty() {
            out.push(' ');
        }
        out.push_str(&sentence(rng, n));
        words += n;
    }
    out
}

/// A paragraph of prose in which runs of 1 to 5 words are wrapped in `<b>`, `<i>`, a larger
/// `<span>`, or `<b><i>` (about a third of the words), so that one line mixes several fonts and sizes.
fn mixed_prose(rng: &mut ChaCha8Rng, min_words: usize) -> String {
    let plain = prose(rng, min_words);
    let words: Vec<&str> = plain.split(' ').collect();
    let mut out = String::new();
    let mut i = 0;
    while i < words.len() {
        if !out.is_empty() {
            out.push(' ');
        }
        if rng.random_range(0.0..1.0) < 0.2 {
            let run = rng.random_range(1..=5).min(words.len() - i);
            let (open, close) = match rng.random_range(0..4) {
                0 => ("<b>", "</b>"),
                1 => ("<i>", "</i>"),
                2 => ("<span style=\"font-size:20px\">", "</span>"),
                _ => ("<b><i>", "</i></b>"),
            };
            out.push_str(open);
            out.push_str(&words[i..i + run].join(" "));
            out.push_str(close);
            i += run;
        } else {
            out.push_str(words[i]);
            i += 1;
        }
    }
    out
}

fn page(name: &str, extra_css: &str, body: &str, nodes: u32) -> TextCase {
    let mut css = String::new();
    for (file, weight, style) in [
        (FONT_FILES[0], "normal", "normal"),
        (FONT_FILES[1], "bold", "normal"),
        (FONT_FILES[2], "normal", "italic"),
        (FONT_FILES[3], "bold", "italic"),
    ] {
        let _ = writeln!(css, "@font-face{{font-family:\"LB Sans\";font-weight:{weight};font-style:{style};src:url(fonts/{file})}}");
    }
    let html = format!(
        "<!DOCTYPE html>\n<html><head><meta charset=\"utf-8\"><title>{name}</title>\n<style>\n{css}html,body{{margin:0;padding:0}}\nbody{{font-family:\"LB Sans\";font-size:16px;line-height:20px}}\np,h3{{margin:0}}\n#cb>div{{width:{}px}}\n{extra_css}</style></head><body>\n<div id=\"cb\">\n{body}</div>\n</body></html>\n",
        crate::num(WIDTH)
    );
    TextCase { name: name.to_string(), html, nodes }
}

/// `n` block paragraphs of about 80 words in a 960px column
fn paragraphs(n: usize) -> TextCase {
    let rng = &mut ChaCha8Rng::seed_from_u64(SEED);
    let mut body = String::from("<div>");
    for i in 0..n {
        let _ = write!(body, "<p style=\"background:{}\">{}</p>", leaf_colour(i as u32), prose(rng, 80));
    }
    body.push_str("</div>\n");
    page(&format!("text/paragraphs/{n}"), "p{padding:4px 8px;margin-bottom:8px}\n", &body, n as u32 + 1)
}

/// `n` wrapping flex cards, each a heading plus two sentences, in a 960px row
fn flex_cards(n: usize) -> TextCase {
    let rng = &mut ChaCha8Rng::seed_from_u64(SEED);
    let mut body = String::from("<div style=\"display:flex;flex-wrap:wrap;gap:16px\">");
    for i in 0..n {
        let n = rng.random_range(2..=5);
        let heading = sentence(rng, n);
        let n = rng.random_range(8..=14);
        let first = sentence(rng, n);
        let n = rng.random_range(8..=14);
        let text = format!("{first} {}", sentence(rng, n));
        let _ = write!(body, "<div class=\"card\" style=\"background:{}\"><h3>{heading}</h3><p>{text}</p></div>", leaf_colour(i as u32));
    }
    body.push_str("</div>\n");
    page(
        &format!("text/flex_cards/{n}"),
        ".card{flex:1 1 280px;padding:12px}\nh3{font-size:20px;line-height:24px;margin-bottom:8px}\n",
        &body,
        3 * n as u32 + 1,
    )
}

/// `n` paragraphs whose words are partly wrapped in bold, italic and larger inline spans
fn inline_mixed(n: usize) -> TextCase {
    let rng = &mut ChaCha8Rng::seed_from_u64(SEED);
    let mut body = String::from("<div>");
    let mut nodes = 1;
    for i in 0..n {
        let text = mixed_prose(rng, 80);
        nodes += 1 + text.matches("<b>").count() as u32 + text.matches("<i>").count() as u32 + text.matches("<span").count() as u32;
        let _ = write!(body, "<p style=\"background:{}\">{text}</p>", leaf_colour(i as u32));
    }
    body.push_str("</div>\n");
    page(&format!("text/inline_mixed/{n}"), "p{padding:4px 8px;margin-bottom:8px}\n", &body, nodes)
}

pub fn cases() -> Vec<TextCase> {
    let mut cases = vec![];
    for n in [100, 1000] {
        cases.push(paragraphs(n));
        cases.push(flex_cards(n));
        cases.push(inline_mixed(n));
    }
    cases
}
