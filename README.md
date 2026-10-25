# layout-bench

Comparable layout-performance numbers for Taffy, Blitz (Taffy + Stylo + Parley), Servo, and Chrome
on identical pages.

**Before interpreting the rankings, read the [benchmark caveats](CAVEATS.md):**
phase boundaries, equal-work validation, cache state, and sampling affect which
numbers are comparable.

Servo's layout has no standalone entry point (it reflows a script-owned DOM), so the common unit is
a page: the same HTML, the same viewport, timed from styled DOM to final boxes in each engine.

## Corpus

`gen` builds the trees from Taffy's benchmark suite (wide / deep / super-deep flexbox, absolute
positioning, wide / deep grids) and serialises them to HTML with inline styles, one `<div>` per
Taffy node. Every leaf gets a distinct background colour so renders can be pixel-compared. There is
no text, so text shaping and line breaking are excluded; these pages measure the layout algorithms
and the surrounding style/box machinery only. The `pangui/<template>` cases are the PanGUI flexbox
templates from Taffy's benchmark crate (`gen/pangui/*.txt`, `taffy_benchmarks::pangui_template`),
translated to Taffy styles the same way as Taffy's `pangui` bench and serialised like the rest.

The `text/` cases (`paragraphs`, `flex_cards`, `inline_mixed`, each at 100 and 1000 items) are
hand-built HTML with deterministic prose (a fixed word list sampled with the seed), set in DejaVu
Sans shipped in `fonts/` (`@font-face`, four faces, loaded via a relative `url()`; licence in
`fonts/LICENSE-DejaVu.txt`), with `line-height: 20px` and `text-rendering: geometricPrecision`
(without it Chrome rounds each glyph advance to a whole pixel and breaks ~5% of lines differently).
They have no Taffy tree, so Taffy direct is not measured for them; they compare Blitz (Parley)
`construct`+`layout` against Servo Box+Fragment Tree and Chrome `rebuildLayoutTree`+`Layout`, i.e.
shaping plus line breaking (see the phase table below for why shaping lands in the construction phases).

The root is absolutely positioned inside a `#cb` containing block sized to the Taffy available
space (`max-content` becomes a 1,000,000px box). `run.py gen` also writes `corpus/reveal/*.html`
for Servo and Chrome: the tree starts `display:none` and a trailing script reveals it and forces
layout, so the whole tree is styled and laid out in a single reflow after parsing has finished.
Pages with `@font-face` reveal the tree only after `document.fonts` has loaded every face, so that
reflow shapes with the web font rather than a fallback. Servo loads the reveal pages over a
localhost HTTP server started by `run.py` because its fetch rejects `file://` fonts (CORS mode from
an opaque origin); `blitz-runner` serves `file://` URLs itself, synchronously, before the timed
`resolve()`.

### `real/`: saved web pages

The `real/<page>` cases are seven real pages saved on 2026-10-20 and frozen by `real/freeze.py`
(sources and licences in `real/LICENSES.md`; the saved originals live in `real/raw/`, ignored):

| case | page | elements under `<body>` |
|---|---|---:|
| `real/wikipedia` | en.wikipedia.org/wiki/Barack_Obama (Vector 2022 skin) | 21,889 |
| `real/mdn` | developer.mozilla.org/en-US/docs/Web/CSS/display | 2,212 |
| `real/rustdoc` | doc.rust-lang.org/std/vec/struct.Vec.html | 15,947 |
| `real/css-flexbox-1` | www.w3.org/TR/css-flexbox-1/ | 15,890 |
| `real/servo-org` | servo.org | 226 |
| `real/dioxuslabs-com` | dioxuslabs.com | 158 |
| `real/bootstrap-dashboard` | getbootstrap.com/docs/5.3/examples/dashboard/ | 199 |

`real/freeze.py fetch <page>` saves a page with `wget -p -k -E -H` into `real/raw/<page>/`;
`real/freeze.py freeze <page>` rewrites it into `real/<page>/index.html` plus the placeholder
images, and `real/manifest.tsv` (name, directory, element count, viewports). `run.py gen` copies
`real/<page>/` into `corpus/real/<page>/` and `corpus/reveal/real/<page>/` and appends one manifest
line per viewport (every page is currently 1280×800, as `real/<page>`; another width would be
`real/<page>@<w>` via the optional 7th manifest column, which the other pages leave at the global 1280×800). Node count is the number
of elements under `<body>`; there is no Taffy tree. The `<body>` itself is the `#cb` element (a
wrapper `<div>` would change the containing block of fixed/absolute children and `body`'s own
margin and flex behaviour), so the reveal script restores its stylesheet `display` instead of
forcing `block`, and the runners wait for `display != none`.

Freezing rules (all in `real/freeze.py`, never by hand-editing the saved HTML): scripts, inline
handlers, `<noscript>`, `<template>`, `<link>`s (screen stylesheets are inlined first, print and
dark-scheme sheets dropped), `<meta http-equiv>` and comments go; `<img>`, `<picture>`, `<video>`,
`<iframe>`, `<canvas>`, `<object>`, `<embed>` and inline `<svg>` become `<img>` placeholders of the
same natural size (flat grey PNGs under `real/<page>/ph/`, `width`/`height` attributes kept or taken
from the saved file, id/class/style kept so CSS sizing resolves the same way); form controls become
`span.lb-input` (UA control sizes differ); closed `<details>` keep only their `<summary>`. In CSS,
`@import`, `@font-face` and every `url()` go (no background images), `font-family`/`font` are
rewritten to `"LB Sans"` or `"LB Mono"` (the DejaVu faces in `fonts/`, via `../../fonts/`), and
`text-rendering`, `scrollbar-gutter` (Chrome reserved a 15px gutter on MDN, Firefox and Blitz none),
`transform`/`translate`/`rotate`/`scale` (dioxuslabs.com's hidden search modal is `scale: 1.1`; it
does not affect layout but skews `getBoundingClientRect()` and the screenshot) and `animation`
declarations are stripped. The page gets `html{text-rendering:geometricPrecision;font-family:"LB
Sans"}` and `pre,code,kbd,samp,tt{font-family:"LB Mono"}` at the lowest specificity so that elements
left in the UA default font do not fall back to system fonts (Blitz is built without any and
rendered the flexbox spec's unstyled paragraphs 0px tall). No page issues a non-`file://` request
(checked with Playwright request logging); file names with `?` are renamed by wget's `-E`/`-k`
handling and nothing is referenced with `%3F`.

Equal-work check (`./run.py verify --engines chrome,blitz,firefox1,servo1,ladybird --filter real/`,
2026-10-20; page height = `document.documentElement.scrollHeight`, Blitz: the `<html>` box's scrollable
overflow, Ladybird: `getBoundingClientRect()` like Chrome; Servo reports neither boxes nor a root):

| case | nodes | px differing: Blitz / Firefox / Servo / Ladybird vs Chrome | Blitz vs Chrome boxes (`div`/`p`/`h3`) | page height Chrome / Firefox / Blitz / Ladybird |
|---|---:|---|---|---|
| `real/wikipedia` | 21,889 | 9.0% / 7.1% / 10.5% / 13.1% | 460/866 sizes, 753 positions | 85,068 / 85,261 / 83,201 / 800 (body) |
| `real/mdn` | 2,212 | 4.6% / 3.7% / 5.6% / 4.2% | 18/176, 163 | 19,760 / 19,786 / 19,976 / 19,760 |
| `real/rustdoc` | 15,947 | 2.3% / 2.2% / 4.4% / 2.3% | 56/1792, 1770 | 155,326 / 155,359 / 155,421 / 155,398 |
| `real/css-flexbox-1` | 15,890 | 2.8% / 2.0% / 7.5% / 6.7% | 28/471, 438 | 90,168 / 90,277 / 90,308 / 90,120 |
| `real/servo-org` | 226 | 22.4% / 1.4% / 2.1% / 1.6% | 31/84, 79 | 5,445 / 5,449 / 5,967 / 5,450 |
| `real/dioxuslabs-com` | 158 | 7.8% / 1.2% / 3.3% / 2.7% | 2/48, 6 | 1,232 / 1,232 / 1,232 / 1,232 |
| `real/bootstrap-dashboard` | 199 | 2.9% / 1.3% / 1.9% / 1.8% | 4/12, 1 | 1,136 / 1,136 / 1,154 / 1,136 |

WebKit (`./run.py verify --engines chrome,webkit --filter real/`, 2026-10-24; details and the two saturated
flex cases in `out/webkit.md`): px differing vs Chrome 6.0% / 3.6% / 1.8% / 1.6% / 1.2% / 1.0% / 1.4% in the
table's order; boxes 208/866 sizes (594 positions), 4/176 (23), 0/1792 (0), 3/471 (428), 0/84 (0), 0/48 (0),
2/12 (2); page heights 84,997 / 19,788 / 155,326 / 90,170 / 5,444 / 1,232 / 1,136. WebKit uses the same 1/64 px
`int32` `LayoutUnit` as Blink and clamps `flex/wide/10000` and `flex/absolute/10000` at the same 33,554,432 px
(8,440 / 5,800 boxes clamped vs Chrome's 8,416 / 5,729), so those two cases are not equal work for it either.

Chrome and Firefox agree on every page to within 0.3% of the page height (the pixel difference is
glyph rasterisation plus a few 1px line-height roundings). Known differences, each with the CSS
feature responsible (Blitz unless stated; "positions" differ wherever an earlier height does):

- `float`: Blitz is built with its opt-in `floats` feature (without it floats are laid out in
  flow and Wikipedia's infobox becomes a full-width block: 21.9 % of pixels, page 87,076 px). With
  floats the page is 83,201 px (2.2 % shorter than Chrome) and 460 of the 866 boxes still differ,
  mostly text wrapped beside the infobox and the `.hlist`/navbox tables below it; not isolated to a
  feature yet. Servo floats the infobox but wraps the text beside it narrower than Chrome/Firefox
  (its 10.5 % pixel difference; it gives no boxes to quantify).
- Inline-level elements (`.mw-heading h3{display:inline}`, `.marriage-display-inline`, `.hlist`
  items, rustdoc's inline `<code>`) have no box in Blitz's `--boxes` dump (they live in the text
  layout) and are reported as 0×0; they count as size differences without being layout differences.
- Replaced elements with a cyclic percentage `max-width` and a `max-height` (servo.org:
  `img{max-width:100%;display:block}` with `.section-feature img{max-height:6rem}` and
  `.navbar-brand img{max-height:4rem}`): Blitz uses the intrinsic width (401–1024px) as the image's
  min-content contribution, so the `flex: 0 1 25%` feature tiles cannot shrink to Chrome's 301px and
  the navbar brand is 1024px instead of 560px (31/84 boxes, page 5,967 vs 5,445). MDN's logo
  wrapper (`.navigation__logo`, around the 83×24 placeholder of an inline SVG) is 99px wide in
  Blitz and 16px in Chrome; this one is not isolated to a feature yet.
- `display: table` / `table-column` / `table-row` / `table-cell` on `<div>`s (the flexbox spec's
  `#overview-example` figure): the column and row boxes are 0×0 in Blitz and the figure is 30px
  shorter (28/471 boxes, +201px over the page from a few such figures).
- Inline-block `<code>` in prose (rustdoc's `.docblock p code{display:inline-block}` with
  `white-space:pre-wrap`): some paragraphs wrap to one more line in Blitz (24 vs 48px), and the
  `🔬` in `.stab.unstable` falls back to no emoji font (511 vs 528px wide); 56/1792 boxes, page
  height 155,421 vs 155,326 (without the `floats` feature the page was 6 % taller, 164,853).
- Table rows: Blitz rounds layout to whole pixels, so each of the Bootstrap dashboard's 17 table
  rows is 1px taller (`.table-responsive` 544 vs 526px, page +18px). Wikipedia's toolbar tabs are
  35px instead of 32px for the same reason (`.vector-menu-content`, ±3px).
- Ladybird (`07fac502`): 1.6–6.7 % of pixels differ on every page but Wikipedia (13.1 %) and its body heights match Chrome's page heights within 0.1 % (the flexbox spec
  and servo.org body is 16 px narrower: Ladybird reserves a scrollbar gutter). Wikipedia's
  `html,body{height:100%}` gives an 800 px body whose content overflows, so the dump reports no page
  height there; the `div`/`p`/`h3` box counts are lower than Chrome's (812 vs 866) because inline
  `div`s/`h3`s have no block box in the dump, as with Blitz, and are compared as missing.
- The dioxuslabs.com and Bootstrap pixel differences beyond the boxes above are the placeholder
  images, which Blitz paints without the pages' `border-radius`/`object-fit` clipping, and
  anti-aliasing.

The real pages are not pixel-equal and are not meant to be; the check that matters before timing
them is the heights and box counts above, which pin each remaining difference to a feature.

## Engines and phases

| engine | how it is run | phases reported |
|---|---|---|
| `taffy` | `gen bench`: the Taffy tree itself, all nodes marked dirty, `compute_layout` | `layout` |
|  | `gen bench --wrapped`: same tree as an absolutely positioned child of a viewport-sized box, mirroring the page's `#cb` (one layout pass from a definite containing block, as in the browsers; ~10% more work than the bare root) | `layout` |
| `blitz` | `blitz-runner`: fresh `HtmlDocument`, `incremental=false`, one `resolve()` per iteration, phase times from Blitz's `log-phase-times` timer (vendored to print ns); `construct` includes Blitz's `pconstruct` phase (deferred tasks, where the Parley text layouts are built, i.e. text is shaped) | `style`, `construct`, `layout`, `paint_tree`, `resolve` |
| `blitz-par` | same with `StyleThreading::Parallel` | same |
| `blitz-pcon` / `blitz-par-pcon` | `blitz-runner` built with `--features parallel-construct` (see [Running](#running) for the build commands): the deferred construction tasks (`pconstruct`, Parley layout builds) run on the rayon pool; with sequential / parallel style | same |
| `blitz-pcon-pl1` / `blitz-par-pcon-pl` | third build of the same `src/main.rs` against the parallel-layout prototype [blitz#1034](https://github.com/DioxusLabs/blitz/pull/1034) (`blitz-runner-pl/Cargo.toml`: #1034 merged onto the Blitz revision of the other builds, with taffy#1230 merged onto their Taffy; features `parallel-layout` + `parallel-construct`): Taffy hands Blitz batches of independent sibling layouts, which run on the rayon pool when their estimated weight is above a threshold. `pl1` = `BLITZ_PARALLEL_LAYOUT_THREADS=1` (a dedicated one-thread pool, i.e. the feature's batching/bookkeeping without parallelism) and pinned like `blitz`, the baseline for the feature's cost; `par-pcon-pl` = everything parallel | same |
| `servo1` / `servo` | servoshell built with `--features tracing-perfetto`, `--pref layout_threads=1` / `3` (default), one `--webdriver` process per round for all of the round's cases (a discarded warm-up window per case, then a fresh window per iteration, see [Versions and methodology](#versions-and-methodology)), spans read from the round's `servo.pftrace` | `Styling`, `Box Tree Construction`, `Fragment Tree Construction`, `restyle_and_build_trees`, `Stacking Context Tree Construction`, `Display List Construction`, `handle_reflow` |
| `chrome` | Playwright chromium-headless-shell, CDP `Tracing` with `devtools.timeline` + `blink_style` | `Document::recalcStyle` (style), `Document::rebuildLayoutTree` (LayoutObject construction), `UpdateLayoutTree` (= both), `Layout` |
| `webkit` | Playwright WebKit (WPE MiniBrowser), driven directly over its `--inspector-pipe` protocol by `engines_webkit.py` (Playwright exposes no raw session for WebKit); new page per iteration, corpus served over localhost HTTP with COOP/COEP headers (a cross-origin-isolated page gets a 20 µs `performance.now()` instead of 1 ms); phases timed by a bootstrap script's `performance.now()` around the reveal's forced style update (`getComputedStyle`) and forced layout (`offsetHeight`); the Inspector `Timeline` domain is used by `verify` only, to count layouts (recording it doubles the style time, see [Versions and methodology](#versions-and-methodology)) | `style` (style resolution, includes render-tree construction), `layout` (includes text shaping / line layout), `style+layout` |
| `firefox` | Playwright Firefox, one process per round for all of the round's cases (launch retried on the occasional startup segfault), per case a discarded warm-up tab then a fresh tab per iteration, all in one content process kept alive by a blank `file://` page (a process's first load gets an extra full reflow and cold font caches; a cold process is 10–20% slower on text-heavy pages, and a case's first load in a warm process is still 10–100% slower on text/real pages, hence the warm-up per case), Gecko profiler started at launch (`MOZ_PROFILER_STARTUP`, markers only) and written at shutdown (`MOZ_PROFILER_SHUTDOWN`); default `layout.css.stylo-threads` (6 on this VM) | `Styles` (style traversal + frame construction), `Reflow`, `DoFlushPendingNotifications` (the flush containing both), `DisplayList` |
| `ladybird` | `Ladybird` driven over its `WebDriver` server (headless), one browser per round and a fresh window (= WebContent process) per iteration, built with `patches/ladybird-phase-timing.patch` which prints `LADYBIRD_UPDATE pid=<pid> url=<url> reason=<reason>` and `LADYBIRD_PHASE pid=<pid> style=<ns> construct=<ns> layout=<ns> total=<ns> full_layouts=<n>` to stderr for every `Document::update_layout()` round (see [Ladybird](#ladybird)) | `style` (`Document::update_style()`), `construct` (layout tree build, `LayoutRoundJob::build`), `layout` (`lay_out_root` / `lay_out_boundary`, the layout pass including the `LayoutState` commit), `total` (the whole round) |

Phase mapping used in the report:

- Layout only: Taffy `compute_layout` ≈ Blitz `layout` ≈ Servo Fragment Tree Construction; Chrome `Layout`
  and Ladybird `layout` are listed too but include text shaping (see below), so on text-bearing cases they
  are only comparable with each other.
- Box construction + layout: Blitz `construct + layout` ≈ Servo Box Tree + Fragment Tree ≈ Chrome
  `rebuildLayoutTree + Layout` (Chrome builds `LayoutObject`s inside `UpdateLayoutTree`, not `Layout`)
  ≈ Ladybird `construct + layout` ≈ Firefox `Reflow` ≈ WebKit `layout` (WebKit, like Firefox, builds its
  render tree while resolving style, so `layout` is the whole box pass). Firefox's frame construction happens inside the
  `Styles` flush with no marker of its own, so `Reflow` under-counts this table by the frame-construction
  time (small: it is a tree walk with no shaping) and `Styles` over-counts the Style table by the same amount.
- Text shaping sits in different phases: Blitz shapes when it builds the Parley inline layout in `construct`
  (`build_inline_layout_into`, run as the deferred `pconstruct` tasks), Servo in Box Tree Construction
  (`inline/shaping_queue.rs::shape_batch` → `font.shape_text` while building each inline formatting context), whereas Chrome (`NGInlineNode::PrepareLayout`
  → HarfBuzz inside `Layout`), WebKit (inline layout measures runs through `FontCascade::width`, which shapes),
  Firefox (`nsTextFrame::Reflow` → `EnsureTextRun` → `gfxFont::ShapeText`)
  and Ladybird (`inline_level_iterator.rs::shape_glyph_data` → `shape_text` during inline layout) shape
  lazily while laying out. Shaping dominates construction on text-heavy pages (Blitz Wikipedia: construct
  60 ms vs layout 20 ms), so "Box construction + layout" is the like-for-like table for any case with text;
  "Layout only" is like-for-like only among Taffy, Blitz and Servo (the `text/` cases have no Taffy tree).
- Style: Blitz `style` ≈ Servo `Styling` ≈ Chrome `recalcStyle`; Firefox `Styles` and WebKit `style` are listed
  here too but, like Chrome's `UpdateLayoutTree`, they include frame / render-tree construction; Ladybird `style` is `update_style()`.
- Whole pipeline (style to laid-out tree): Blitz `resolve()` ≈ Servo `restyle_and_build_trees` (Styling + Box
  Tree + Fragment Tree, plus stylist preparation and damage computation) ≈ Chrome `UpdateLayoutTree + Layout`
  ≈ Firefox `Styles + Reflow` ≈ WebKit `style + layout` ≈ Ladybird `update_layout()`. None of these includes display-list or paint work:
  Blitz's `resolve()` ends with `build_paint_tree` (the stacking-context / paint-order lists, ~0.3 ms on
  Wikipedia; scene generation in `blitz_paint::paint_scene` is outside the timed interval), Servo's stacking-context tree is built by the enclosing `handle_reflow` (recorded as `reflow`, not
  shown in the table; ~9 ms on Wikipedia), and the measured reflows build no display list.

`out/servo-threads.md` is a `layout_threads` = 1/3/4/6/8 sweep of Servo on seven cases (`servoN` is accepted as an
engine id by `bench` for any N; only `servo1`/`servo` are in the main run).

Servo's `restyle_and_build_trees` and `handle_reflow` include work the children spans do not
(stylist preparation, damage computation); the report shows them separately.

### Blitz feature cost

blitz-dom's `floats` and `writing-mode` are opt-in and the runner enables both (`apps/browser`
ships with `floats`). What they cost, as callgrind instructions in `resolve_layout` for one layout
of the page (deterministic; the layout hashes are identical across the four builds on all 43 pages):

| page | neither | `floats` | `writing-mode` | both |
|---|---:|---:|---:|---:|
| flex/wide/10000 | 134.6M | 134.4M (0%) | 149.0M (+10.7%) | 149.6M (+11.2%) |
| grid/wide/100x100 | 231.9M | 230.4M (−0.6%) | 264.1M (+13.9%) | 251.8M (+8.6%) |
| text/paragraphs/1000 | 188.4M | 211.7M (+12.4%) | 189.0M (+0.3%) | 212.2M (+12.7%) |

`writing-mode` is paid on every style read (the frame-transposing getters in `stylo_taffy`), `floats`
in block layout with inline content; so the Blitz columns measured with both are ~10% above what a
build without them would show on these pages.

Firefox reports the longest `Reflow` and `Styles` marker of the page's content process. The reveal
flush is one `Styles` + one `Reflow`; the page also records a few sub-0.1 ms reflows (the initial
`display:none` document, a nested flush after the reveal), so `verify` prints the reflow count and
the sum of all reflows relative to the longest. The `Styles` marker's `elementsTraversed` is the
styled-element count (`styled=` in `verify`, nodes + `html`/`body`/`#cb`).

## Relayout scenarios

Every case is also measured in five incremental-layout scenarios, in the same document load as the first layout
(one load per iteration = first layout, then the scenarios in a fixed order, each mutation batched, forced to a single
layout, then reverted — the revert's layout is discarded):

| key | mutation | measures |
|---|---|---|
| `root_width` | the case root's `width` set to 0.8× its laid-out width | warm full relayout (the headless stand-in for a viewport resize) |
| `leaf_1` | one deepest leaf's `width` +1 px | invalidation along one path |
| `leaf_10pct` | every 10th leaf's `width` +1 px | many dirty subtrees with overlapping ancestor paths |
| `leaf_all` | every leaf's `width` +1 px | incremental machinery vs. a full relayout |
| `append` | the last 10 % of the root's children cloned and appended | DOM mutation + construction + layout |

Leaves are the innermost block-level elements under `#cb`: elements with a box (`getClientRects()` non-empty) that
are not `display: inline` and have no such child (`width` changes no geometry on a non-replaced inline, and Blitz
has no node layout for it to mutate); `append` clones the root's boxed children. The widths are all read before any is written, so the
preparation itself does not flush N layouts. The same script (`relayout.js`, driven as `window.__lb.relayout(step,
'apply'|'revert')`) runs in Chrome, WebKit, Firefox (Playwright `evaluate`) and Servo, Ladybird (WebDriver Execute
Script); the Blitz runner applies the identical mutations natively through `DocumentMutator` with
`incremental: true` and times one `resolve()` per step. Step *k* runs with caches warmed by the first layout and
steps 1..k−1 — the same for every engine, and stated here rather than avoided.

Per step the sample carries `relayout/<step>/<metric>`: `layout` (Chrome `Layout`, WebKit forced-layout timer,
Firefox `Reflow`, Ladybird layout, Blitz `layout`) and a whole-pipeline figure (Chrome `UpdateLayoutTree`+`Layout`,
WebKit style+layout, Firefox `Styles`+`Reflow`, Ladybird `update_layout()`, Servo `restyle_and_build_trees`, Blitz
`resolve()`), reported as the "Relayout (…)" tables and the Scenario selector on the results site. Servo's incremental
reflows take the box/fragment repair path, whose spans are empty, so only its whole-pipeline figure exists. Chrome's
events are selected between `performance.mark` user-timing marks around the forced layout (`blink.user_timing`
category), Firefox's from the same marks in the profile, Servo's and Ladybird's by the order of the window's reflows
after the reveal.

## Running

Prerequisites (Linux only: the runners pin with `taskset` and Servo/Ladybird run headless with
Linux-specific flags):

- Rust toolchain (measured with rustc 1.99.1; Blitz and Taffy are pinned by `rev` in `Cargo.toml`
  and `blitz-runner-pl/Cargo.toml`, Stylo by `Cargo.lock`).
- Python ≥ 3.8 with `pip install playwright==1.64.0 perfetto pillow && python -m playwright install
  chromium firefox webkit && python -m playwright install-deps webkit` (the Playwright version fixes the
  Chrome, Firefox and WebKit builds, see the table below; Firefox and WebKit are optional: `run.py` skips
  `firefox*` and `webkit` with a message if they are not installed).
- A Servo checkout at `1403b364d` (with [servo#49259](https://github.com/servo/servo/pull/49259)) built with `./mach build --release --features tracing-perfetto`
  (`SERVOSHELL=/path/to/servoshell` if not at `~/repos/servo/target/release/servoshell`; skipped
  with a message if missing).
- Optionally Ladybird `07fac502` with `patches/ladybird-phase-timing.patch`, built as described in
  [Ladybird](#ladybird) (`LADYBIRD_BIN`, with the `WebDriver` binary next to it; skipped if missing).
- Only for re-saving real pages (`real/freeze.py`): `wget` and `pip install beautifulsoup4`.

```sh
cargo build --release --features floats,writing-mode                                            # gen + blitz-runner
cargo build --release -p layout-bench-blitz --features floats,writing-mode,parallel-construct --target-dir target-pcon
cargo build --release --manifest-path blitz-runner-pl/Cargo.toml --target-dir target-pl         # blitz#1034 prototype
./run.py gen                                   # writes corpus/
./run.py bench --rounds 3 --iters 3 --cpus 2   # all engines, interleaved rounds; out/report.md, out/results.json
./run.py report                                 # rewrite out/report.md from out/results.json
./run.py plot                                   # bar charts of out/results.json into out/plots/<suite>/<case>.svg + <suite>.md
./run.py pages                                  # static results site of out/results.json into out/pages/ (serve with python3 -m http.server -d out/pages)
./run.py bench --engines taffy,blitz,servo1 --filter grid
./run.py verify                                # screenshots per engine + % pixels differing, out/shots/
./run.py verify --filter real/ --engines chrome,blitz,firefox,servo1    # the saved real pages
real/freeze.py fetch wikipedia && real/freeze.py freeze wikipedia       # re-save and re-freeze a real page
```

`bench` runs every engine on every case in each round, alternating engine order between rounds,
and reports the minimum (or `--agg median`) over all samples. The Firefox, Servo and Ladybird columns
(`BATCH_ENGINES`) take a whole round at once — one browser for all of the round's cases, run before
or after the per-case engines according to their place in the round's engine order — so each round
costs one launch and one profile/trace decode instead of one per case (Servo: per iteration).
`--cpus` pins the single-threaded runners (`taffy`, `blitz`, `servo1`) with `taskset` (give `servo1`
two CPUs, `--cpus 2,3`, so its script and layout threads do not share one); `blitz-par`, `servo`, `chrome`,
`firefox` and `ladybird` always run unpinned. The current dataset was run without `--cpus` (see Methodology).

`verify` is the equal-work check: before trusting a timing, confirm the engines agree on the layout
(pixel diff of the 1280×800 viewport, Chrome's `totalObjects` layout-object count, Servo's reflow
count, Firefox's styled-element and reflow counts, Blitz's box hash, Chrome's `document.fonts` status). Blitz and Chrome also dump the border
boxes of every `div`/`p`/`h3` under `#cb` (`blitz-runner --boxes`, `getBoundingClientRect()`), and
`verify` reports how many sizes and positions differ by more than 1px (Blitz rounds layout to whole
pixels). Glyph anti-aliasing differs between engines, so the pixel diff is a few percent on the
text pages even when the layout is identical; for them `verify` additionally compares the
background bands down column x=1 of the screenshots (inside the paragraphs' padding), which are the
leaf boxes' vertical extents and therefore their line counts, and works for Servo, which gives no
box output. The table is also written to `out/verify.md`.

Cases that cannot be made equal: `flex/absolute/10000` (percent insets on a 424,000px-wide root
amplify f32 rounding, so the three engines place boxes up to ~170px apart although the root sizes
agree to 0.003%); `pangui/percentage_and_ratio` renders empty in Servo (it gives
`aspect-ratio` items zero height, in flex and block layout alike), so its Servo timings are not
comparable; `pangui/fit_nesting` (0.99px leaves) and `pangui/flex_expand_equal_weights` (0.67px
items) differ by ~11% of pixels against Chrome because Blitz and Servo snap such boxes to the pixel
grid differently, while the box sizes agree within 1px.

## Versions and methodology

Measured on 2026-10-25 on an 8-vCPU Intel Xeon AWS VM (31 GB, Ubuntu 22.04.5, kernel 6.8.0-1060-aws),
rustc 1.99.1, Python Playwright 1.64.0, in two windows: all engines interleaved, 15:33–16:58 UTC
(`bench --rounds 3 --iters 3`, raw run `out/runs/2026-10-25-full.json`; its Servo rounds failed, the 3-iteration
trace being over the Python protobuf parser's 2 GB message limit), then Servo(1), Servo(3) and Chrome
interleaved, 17:44–18:22 UTC (`out/runs/2026-10-25-servo-chrome.json`). Chrome's per-case minima in the second
window are those of the first within noise (new/old median 0.998, p10 0.97, p90 1.03 over the initial layout and
the five relayout steps of all 43 cases), so the Servo columns are merged in as measured, unscaled. Every sample
is the relayout protocol's (one load, the initial layout, then the five mutation steps), so the initial-layout
numbers come from the same documents and processes as the relayout ones. No runner was pinned in this run
(`--cpus` not given): `servo1` differs from `servo` only by `layout_threads=1`. Every number in `out/` comes
from this machine; children sessions that add engines or cases only verify equal work and run a one-round
smoke test, the measurement is redone here with `bench --merge`.

Earlier epochs: the 2026-10-23 dataset (`out/runs/2026-10-23-full.json`, one 27-minute window, single-threaded
runners pinned with `--cpus 2`, Ladybird with the previous one-process-per-iteration runner) with WebKit measured
on 2026-10-24 (`out/runs/2026-10-24-webkit-chrome.json`) and folded in via `run.py normalize`; and before it the
2026-10-20 run (`out/runs/2026-10-23-blitz-servo-chrome.json`). Against the 2026-10-23 epoch the 2026-10-25
windows are a uniform 9–17 % faster for every engine (initial-layout minima of the same cases, new/old: Chrome
0.89, WebKit 0.88, Firefox 0.83, Blitz 0.89, Taffy 0.92, Ladybird 0.86, p10–p90 within ±5 % of each median), so
the absolute times fell but the cross-engine ratios did not.

| engine | version | how it is driven and timed |
|---|---|---|
| Chrome | Chromium 156.0.8078.4 (Playwright `chromium_headless_shell-1248`, headless shell, `--no-sandbox`) | New page per iteration, 1280×800, `file://` reveal page, `load` + wait for the reveal; CDP `Tracing` with categories `devtools.timeline`, `disabled-by-default-devtools.timeline`, `blink`, `blink_style`; longest `X` event of each name: `Document::recalcStyle` (style), `Document::rebuildLayoutTree` (LayoutObject construction), `UpdateLayoutTree` (both), `Layout` (fragment-tree layout). `totalObjects` from the `Layout` event is the equal-work count. Not pinned (multi-process). |
| WebKit | WebKit 27.2 (Playwright `webkit-2370`, the WPE MiniBrowser bundle Playwright 1.64.0 installs; `browser.version` = `27.2`, user agent `AppleWebKit/605.1.15 (KHTML, like Gecko) Version/27.2 Safari/605.1.15`; the bundle names no upstream WebKit revision) | New page per iteration at the case's viewport, corpus served over localhost HTTP with `Cross-Origin-Opener-Policy: same-origin` + `Cross-Origin-Embedder-Policy: require-corp` (the reveal page is otherwise unchanged; WebKit swaps the page into a fresh web process on the navigation, so every sample is a cold process), `load` + wait for the reveal. Driven directly over the binary's `--inspector-pipe` protocol (`engines_webkit.py`). Phase times come from a `Page.setBootstrapScript` that wraps `HTMLElement.prototype.offsetHeight`: on the reveal script's `cb.offsetHeight` it takes `performance.now()`, forces style with `getComputedStyle(cb).display` (`style`: style resolution and render-tree construction of the revealed tree), then the original getter (`layout`: the box layout, including line layout and shaping). Cross-origin isolation turns `performance.now()` from 1 ms to 20 µs resolution (`Performance::allowHighPrecisionTime`). The Web Inspector `Timeline` domain would give the same intervals as `RecalculateStyles`/`Layout` records (agreement within 0.3 ms when both are on) but recording emits an `InvalidateLayout` record with a captured JS stack for every renderer that gets dirtied (one per box, 101k on `pangui/fit_nesting`), which makes the style phase 2–2.5× slower, so it is only turned on by `verify` to count layouts (`n_layouts`; one `Layout` of the revealed tree per sample, preceded only by the ≤1 ms layout of the hidden page on cases whose reveal awaits `document.fonts`). Not pinned (multi-process). |
| Firefox | Firefox 157.0 (Playwright `firefox-1555`) | One browser launch per round for all of the round's cases; per case a discarded warm-up tab (`?warmup`) then a fresh tab per iteration (`?i=N`, the profile is filtered by page URL), all tabs of the round in one content process (a blank `file://` page is kept open: each Playwright `new_page()` is a new context and the file content process exits with its last tab, so otherwise every sample would run in a fresh cold process, 10–20% slower on text-heavy pages): a Firefox process's first page load does a second full reflow ~200 ms after the first with nothing restyled (105 ms on Wikipedia, 64 ms on rustdoc; absent on a second load of the same page) that Chrome, Servo and Ladybird have no counterpart to, and its first reflow runs 5–15 % slower on cold font/text caches; in a warm process a case's own first load is still 10–100% slower on text/real pages (rustdoc, paragraphs: cold shaped-word/font caches), so the warm-up is per case. Gecko profiler on from startup (`MOZ_PROFILER_STARTUP=1`, features `nostacksampling,nomarkerstacks`, filter `GeckoMain`), profile written by `MOZ_PROFILER_SHUTDOWN`; the content process whose page is the case is read for the `Styles` interval marker (style, includes frame construction), `Reflow` start/end pairs (layout; the longest one is reported, the sum is within 1% of it) and `DisplayList`. Default `layout.css.stylo-threads` (5 style workers here), unpinned. |
| Ladybird | `07fac502` (2026-10-20) + `patches/ladybird-phase-timing.patch`, Release build, Qt 6.10.3 | One `WebDriver --headless` browser per round for all of the round's cases; for the real pages a discarded warm-up window (`?warmup`; the first load of a page in a fresh browser is 14–18 % slower in `layout` on `real/wikipedia`/`real/rustdoc`, within 2 % on the synthetic pages), then a fresh window per iteration (`?i=N`) at the case's viewport, `file://` reveal page, navigation + wait for the reveal. Every window is a new WebContent process (default site isolation), so each sample is a cold content process's first layout; the UI process's font service is warm. Phase times from the patch's `LADYBIRD_PHASE` stderr lines, attributed to the window by pid + URL, the round with reason `HTMLElementOffsetHeight` (the reveal script's forced layout): `style` (`update_style()`), `construct` (layout tree build), `layout` (layout passes incl. shaping), `total`. Protocol change from the 2026-10-23 run (one `--headless=layout-tree` process per iteration, cold font service): `layout` of `real/wikipedia`/`real/rustdoc` is 13–16 % lower (min), other stages and the synthetic cases within 3 %. Not pinned (multi-process). |
| Servo | servoshell 0.7.0-1403b364d (built 2026-10-25 from servo/servo `1403b364d`, `./mach build --release --features tracing-perfetto`; Stylo `633f43ad`) | One headless process per round for all of the round's cases (`-z --webdriver`, started on `about:blank`, which stays open so the process never has zero windows), driven over WebDriver by `engines_servo.py` (stdlib `urllib`): per case a discarded warm-up window (`?warmup`), then per iteration `New Window` → `Set Window Rect` to the case's viewport (really resizes the headless webview) → navigate to `?i=N` → `Execute Script` polled until `#cb` is shown → `Close Window`. Page served over localhost HTTP (its fetch rejects `file://` fonts); `SERVO_TRACING=layout::layout_impl=trace,layout::flow::root=trace` (phase spans only; per-item spans would add >10×), the round's `servo.pftrace` decoded packet by packet from the protobuf with the `perfetto` package's generated classes (its TraceProcessor costs ~1 s per trace; a round's trace runs to GBs, as every layout query the relayout script makes — `getClientRects`/`getComputedStyle` on each element, `getBoundingClientRect` per leaf — is a `handle_reflow` span of its own, so only the phase spans are kept). A window's reflows are the `handle_reflow` spans whose `webview_id` field ([servo#49259](https://github.com/servo/servo/pull/49259)) is the window's WebDriver handle, and its sample is the `restyle_and_build_trees` among them before the observed reveal that built the tree (the earlier, `display:none` reflows construct nothing): `Styling`, `Box Tree Construction`, `Fragment Tree Construction`, `Stacking Context Tree Construction`, `Display List Construction`, `handle_reflow`, summed by time containment in the reflow (in a warm process with `layout_threads` > 1 the box and fragment passes run on a `StyleThread#N` rayon worker, nested under nothing). Protocol change from the stored run (one `-z -x` process per iteration): a warm process. `servo1` (`--pref layout_threads=1`, pinned to two CPUs) is 5–35 % faster per stage than a cold process (style 15–47 %, box 7–37 %, fragment 0–35 %, `restyle_and_build` 6–34 % on the seven validation cases) with the same spread; within the warm process a case's own first load is slower still (style ≤ 1.17×, box ≤ 1.40× on `flex/wide/10000`, ≤ 1.08× on the real pages), hence the per-case warm-up. `servo` (default 3 layout threads, Stylo pool shared by style and box construction, unpinned) does not gain: its mins on the text/real pages came out 7–26 % higher than cold processes with a wider spread (bimodal samples, all phases slow together, the layout threads themselves consuming the extra CPU time; not pinned down, see the PR write-up). |
| Blitz | DioxusLabs/blitz `main` `1c5265a8` (2026-10-23; blitz-dom with Taffy `main` `802e497b`, Stylo 0.22 at `DioxusLabs/stylo` `d6502e00`, Parley 0.12.0, harfrust 0.12.0, skrifa 0.44.0); the `*-pl` engines: [blitz#1034](https://github.com/DioxusLabs/blitz/pull/1034) rebased on that `main` (`fac9b358`, with [taffy#1230](https://github.com/DioxusLabs/taffy/pull/1230) rebased on Taffy `main`, `a2b0f009`) | `blitz-runner` (this repo): fresh `HtmlDocument` per iteration from the plain `corpus/*.html`, `incremental=false`, one `resolve()`; phase times from Blitz's own `log-phase-times` timer via a vendored `debug_timer` printing ns: `style`, `construct` (+ `pconstruct`, the deferred Parley layout builds = shaping), `layout` (Taffy + Parley line breaking), `paint_tree`, `resolve`. Built with blitz-dom's opt-in `floats` and `writing-mode` features (as `apps/browser` does for floats; neither is in blitz-dom's defaults). Global allocator mimalloc (`blitz-runner/src/main.rs`): with glibc malloc the `layout` phase of `pangui/wide_no_wrap_simple_many` is 233 ms instead of 147 ms (per-node `LayoutData` boxes and Taffy's item vectors, re-faulted every iteration because the heap top is trimmed when the previous document is dropped). `blitz` = sequential style, pinned; `blitz-par` = `StyleThreading::Parallel`; `blitz-pcon` / `blitz-par-pcon` = second build with `--features parallel-construct` (deferred construction on the rayon pool). Equal work: hash of every element's final box, `--boxes` dump. |
| Taffy | DioxusLabs/taffy `4e59968` (`taffy_benchmarks` for the tree shapes and PanGUI templates) | `gen bench`: the same tree built directly in a `TaffyTree`, all nodes dirtied, `compute_layout` timed with `Instant`; pinned. `--wrapped` lays it out as the page does (abspos child of a viewport-sized box, ~10% more work). Blitz's Taffy is `main` `802e497b` (this one plus everything merged since, taffy#1343 included). |

Common protocol: `bench --rounds 3 --iters 3`, engines interleaved within a round (order reversed every
other round), `min` over all 9 samples per engine and case (medians via `--agg median`); the first
layout of a freshly loaded page is measured, never a relayout. Only single-threaded runners are pinned
(`--cpus`); parallel ones use all 8 vCPUs. Caveats: VM wall-clock noise is 1–3% between rounds when the
machine is idle and much more when it is not (check `uptime`); Servo's remaining tracing overhead is
~1.5 ms per page; Chrome and Firefox numbers include no process start or parse time, only the named
events; Taffy direct is not wrapped in the page's containing block unless `--wrapped` is used.

## Results

Both forms are committed and regenerated by `run.py`:

- `out/results.json`: raw samples, nanoseconds, one list per engine and case. Each sample is a dict
  of the phases above (`layout`, `style`, `construct`, `construct+layout`, `resolve`/`reflow`/
  `style+layout`, Servo `box`/`fragment`/`box+fragment`/`display_list`, Chrome `update_layout_tree`/
  `total_objects`/`n_layouts`, Firefox `layout_sum`/`n_reflows`/`display_list`, …) plus, for verify
  runs, `root`, `hash`, `boxes`, and `chrome_norm` on samples folded in from a later run (see
  [Versions and methodology](#versions-and-methodology)). `bench --merge` re-measures a subset of
  engines or cases in place; `normalize <run> --engines …` folds a `bench --out` run that included
  Chrome into it, scaled per case by Chrome's stored/new ratio. Raw later runs are kept in `out/runs/`.
- `out/report.md`: the formatted tables (`./run.py report` rewrites it from `results.json`), columns
  ordered Chrome, Firefox, Servo, Blitz, Taffy, each cell `ms` over `N.NNx` (a `<br>`), the fastest non-Taffy cell of the row in bold, relative to the Chrome column of
  the same table. A final `Sample spread` table gives median ÷ min of the samples behind each
  cell (per engine on its layout metric), with median and p90 case rows, so the spread behind the `min` figures is visible.
- `out/verify.md`: the equal-work table (`./run.py verify`).
- `out/pages/`: the results site (`./run.py pages`, `pages.py` + `web/site.js`/`site.css`; not committed), deployed to GitHub
  Pages by `.github/workflows/pages.yml` on pushes to `main` that touch `results.json`, the README, CAVEATS or the generator.
  The front page is the results, with two tabs: a table
  with a sticky header and pinned case column, and a bar chart per case stacked by stage with sample whiskers; the suite,
  comparison table (from `COLUMNS`), min/median and engines are switchable; values are ms on a
  linear axis. An About page carries this README's methodology and versions and CAVEATS.md.
- `out/plots/<suite>/<case>.svg`: horizontal bar charts per case (the Box construction + layout, Style and Whole pipeline tables; Layout only and Construction are the segments of the stacked bars, so Taffy appears in the report only), embedded in one page per suite `out/plots/<suite>.md` (`./run.py plot`, index in [out/plots/README.md](out/plots/README.md)),
  in the style of [arewelayoutyet](https://arewelayoutyet.mespin.me): one row per case, one dot per engine (minimum,
  whisker to the median), log x axis, faster to the left; three views each: `-per-node` (ns per node), `-relative`
  (x the fastest engine of the row) and `-milliseconds`.

## Ladybird

Ladybird is optional: `run.py` looks for the binary at `LADYBIRD_BIN` or
`~/repos/ladybird/Build/release/bin/Ladybird` and skips the engine with a message if it is missing.

Build (Ubuntu 22.04, 8 cores; Ladybird commit `07fac502`, 2026-10-20). Ladybird needs Clang ≥ 19 or
GCC ≥ 14, CMake ≥ 3.30, Ninja, nasm and Qt ≥ 6.10, all newer than the distro packages, so:

```sh
# toolchain: LLVM apt (clang-22), Kitware apt (cmake 4.4), ninja, nasm, build deps from BuildInstructionsLadybird.md
sudo apt install clang-22 lld-22 cmake ninja-build nasm autoconf autoconf-archive automake libtool pkg-config \
     libgl1-mesa-dev libpulse-dev libssl-dev libegl1-mesa-dev zip unzip tar curl
pip install aqtinstall && aqt install-qt linux desktop 6.10.3 linux_gcc_64 -O ~/Qt   # Qt 6.10 (apt has 6.2)

git clone --depth 50 https://github.com/LadybirdBrowser/ladybird ~/repos/ladybird
cd ~/repos/ladybird && git apply /path/to/layout-bench/patches/ladybird-phase-timing.patch
export CMAKE_PREFIX_PATH=$HOME/Qt/6.10.3/gcc_64 PATH=$HOME/Qt/6.10.3/gcc_64/bin:$PATH
unset BASH_ENV   # the build script runs `bash -c` snippets; a BASH_ENV that returns non-zero fails the vcpkg step
./Meta/ladybird.py build --cc clang-22 --cxx clang++-22 ladybird     # Release preset -> Build/release/bin/Ladybird
```

The build took 36 min wall-clock on 8 cores (≈11 min of vcpkg dependencies — ICU, ffmpeg, Skia
and friends are compiled from source when the binary cache has no entry for the toolchain — and
≈25 min for Ladybird itself). Applying the patch to an existing build and rebuilding takes
~1 min: it only touches the Rust layout crate and one LibWeb file. The `WebDriver` binary is not
part of the `ladybird` target: `ninja -C Build/release WebDriver` (8 s) puts it next to `Ladybird`.

The patch instruments `Libraries/LibWeb/Rust/src/layout/update_layout.rs`, where LibWeb's layout
update now lives (`Document::update_layout()` in `Libraries/LibWeb/Layout/UpdateLayout.cpp` calls
`render_state_update_layout` once per round; a round re-runs only when a layout reached a web font
or image that was already available). Per round it prints the time spent in the style callback
(`Document::update_style()`), in the layout tree build (`construct`), in the layout pass(es)
(`layout`, which commits the `LayoutState` as it goes) and in the round as a whole (`total`), plus
how many full (root) layout passes ran; the `LADYBIRD_UPDATE` line printed before it names the
process, the document's URL and the `UpdateLayoutReason` that triggered the round (the WebContent
processes of a browser share one stderr, so a `PHASE` line belongs to the last `UPDATE` line of the
same pid). The runner (`engines_ladybird.py`) drives Ladybird over WebDriver: one `WebDriver
--headless` server and browser per round for all of the round's cases, the session's about:blank
window kept open, for the real pages a discarded warm-up load (`?warmup`), then a fresh window per
iteration (`?i=N`, sized with Set Window Rect before the navigation, closed afterwards). With Ladybird's
default site isolation every window gets its own WebContent process, so each sample is the first
layout of a cold content process, as before, while the browser's UI process — and its font service,
which hands WebContent the system fonts — is warm: the first load of a page in a fresh browser
lays out 14–18 % slower on `real/wikipedia` and `real/rustdoc` (shaping, cold font service), hence
their warm-up; the synthetic pages (one font) do not change (within 2 %), so they have none. The sample is the round with reason
`HTMLElementOffsetHeight` and a full layout pass: the `cb.offsetHeight` the reveal script reads
right after showing `#cb`, i.e. the first layout of the revealed tree (the `display:none`
document's rounds come before it; later rounds are relayouts); `layouts=N` is the number of the
document's rounds with a full layout pass. `verify` reads `root`, the `div`/`p`/`h3` boxes and
`document.fonts` with Execute Script, exactly as `run_chrome` does, and takes the 1280×800
screenshot with Take Screenshot. The runner keeps fontconfig's cache in `out/ladybird-cache`
(a fresh `XDG_CACHE_HOME` per browser made fontconfig rescan the system fonts). One round of the
suite (43 cases × 3 iterations) takes 131 s against 152 s with the previous one-process-per-iteration
runner: 82 s of measured spans plus 0.38 s per iteration of window creation, WebContent start and
page parse (0.53 s before), 0.1 s of browser start per round and the 7 real-page warm-up loads.

### Ladybird vs Chrome

`verify --engines chrome,ladybird` (Ladybird `07fac502` + the patch): every flex, grid and pangui
case agrees with Chrome within 1 px of box size and position, with these exceptions:

- `flex/huge_nested/*`: Ladybird's root is 8,000 px (80,000 px) wide, Chrome's 100 px. The root is
  an absolutely positioned (shrink-to-fit) flex container whose items have `width:10px;
  flex-grow:1` and each contain ten such items. Ladybird takes the items' max-content
  contribution from their content (10 × 10 px, recursively, so ×10 per level) instead of their
  definite `width`, and `flex-grow` then spreads the surplus. Same boxes, so the timing is of the
  same tree, but of a differently sized one.
- `flex/wide/10000`, `flex/absolute/10000`: the root's intrinsic width differs by 0.003 %
  (854,624 vs 854,597 px) because a few items' max-content contributions differ by up to 0.4 %
  (same f32/fixed-point class as the note above; the 1,000-node variants agree within 3 px), and
  everything to the right of them shifts by up to 3,000 px.
- `pangui/fit_nesting` (28 % px) and `pangui/flex_expand_equal_weights` (12 % px): the 0.99 px and
  0.67 px boxes are snapped to the pixel grid differently, as with Blitz and Servo; the box sizes
  are equal and `equal_weights` positions drift by 1 px after ~130 items (fixed-point
  accumulation).
- text pages: 5–10 % of pixels differ from glyph rasterisation alone (bands equal). 7/1000
  `paragraphs`, 2/1000 `inline_mixed` and 2/3000 `flex_cards` paragraphs are one line taller in
  Ladybird: a line that fits Chrome's 944 px content box with 0.2 px to spare (paragraph 32 of
  `text/paragraphs`, line 2 at 943.80 px) wraps in Ladybird, whose glyph advances accumulate in
  1/64 px `CSSPixels`, and the rest of the paragraph re-wraps.
- Ladybird's screenshots include its own scrollbars (every page overflows the viewport); they are
  part of the pixel percentage.

Ladybird is not pinned: `taskset` on the whole process tree (UI process, WebContent, RequestServer)
made `style` ~5 % slower on flex/wide/10000 and left `layout` unchanged, so the `--cpus` set is ignored
for it. A build moved from another machine needs the Qt Positioning module next to Qt and
`QT_QPA_PLATFORM=offscreen` (set by the runner).

`layouts=1` or `2` on every page (the reveal, preceded by a round for the `display:none` document
when a rendering update ran before the parser reached the reveal script); the font pages add one
round per web font that finishes loading before the reveal.

## Servo tracing filter

Servo is run with `SERVO_TRACING="layout::layout_impl=trace,layout::flow::root=trace"`, which
enables only the phase spans. `layout=trace` would also record the per-item spans
(`FlexItem::layout`, `FlexContainer::layout`, ...), and at ~6 µs per span those inflate
Fragment Tree Construction by more than 10x on these trees (31 ms vs 2.3 ms for flex/wide/1000).
