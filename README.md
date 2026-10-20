# layout-bench

Comparable layout-performance numbers for Taffy, Blitz (Taffy + Stylo + Parley), Servo, and Chrome
on identical pages.

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

| case | page | elements under `<body>` | viewports |
|---|---|---:|---|
| `real/wikipedia` | en.wikipedia.org/wiki/Barack_Obama (Vector 2022 skin) | 21,889 | 1280, 1024 |
| `real/mdn` | developer.mozilla.org/en-US/docs/Web/CSS/display | 2,212 | 1280, 1024 |
| `real/rustdoc` | doc.rust-lang.org/std/vec/struct.Vec.html | 15,947 | 1280 |
| `real/css-flexbox-1` | www.w3.org/TR/css-flexbox-1/ | 15,890 | 1280 |
| `real/servo-org` | servo.org | 226 | 1280, 1024 |
| `real/dioxuslabs-com` | dioxuslabs.com | 158 | 1280, 1024 |
| `real/bootstrap-dashboard` | getbootstrap.com/docs/5.3/examples/dashboard/ | 199 | 1280, 1024 |

`real/freeze.py fetch <page>` saves a page with `wget -p -k -E -H` into `real/raw/<page>/`;
`real/freeze.py freeze <page>` rewrites it into `real/<page>/index.html` plus the placeholder
images, and `real/manifest.tsv` (name, directory, element count, viewports). `run.py gen` copies
`real/<page>/` into `corpus/real/<page>/` and `corpus/reveal/real/<page>/` and appends one manifest
line per viewport (`real/<page>` is 1280×800, `real/<page>@1024` is 1024×800; the viewport is an
optional 7th manifest column, the other pages keep the global 1280×800). Node count is the number
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

Equal-work check (`./run.py verify --engines chrome,blitz,firefox1,servo1 --filter real/`, 2026-10-20;
page height = `document.documentElement.scrollHeight`, Blitz: the `<html>` box's scrollable
overflow; Servo reports neither boxes nor a root):

| case | nodes | px differing: Blitz / Firefox / Servo vs Chrome | Blitz vs Chrome boxes (`div`/`p`/`h3`) | page height Chrome / Firefox / Blitz |
|---|---:|---|---|---|
| `real/wikipedia` | 21,889 | 21.9% / 7.1% / 10.5% | 474/866 sizes, 754 positions | 85,068 / 85,261 / 87,076 |
| `real/wikipedia@1024` | 21,889 | 18.6% / 5.2% / 9.1% | 472/866, 760 | 69,635 / 69,912 / 75,984 |
| `real/mdn` | 2,212 | 4.6% / 3.7% / 5.6% | 18/176, 163 | 19,760 / 19,786 / 19,976 |
| `real/mdn@1024` | 2,212 | 4.6% / 3.6% / 6.0% | 12/176, 164 | 19,672 / 19,698 / 19,832 |
| `real/rustdoc` | 15,947 | 2.3% / 2.2% / 4.4% | 129/1792, 1770 | 155,326 / 155,359 / 164,853 |
| `real/css-flexbox-1` | 15,890 | 2.8% / 2.0% / 7.5% | 28/471, 438 | 90,168 / 90,277 / 90,369 |
| `real/servo-org` | 226 | 22.4% / 1.4% / 2.1% | 31/84, 79 | 5,445 / 5,449 / 5,967 |
| `real/servo-org@1024` | 226 | 22.9% / 2.9% / 4.1% | 31/84, 79 | 5,605 / 5,611 / 6,057 |
| `real/dioxuslabs-com` | 158 | 7.8% / 1.2% / 3.3% | 2/48, 6 | 1,232 / 1,232 / 1,232 |
| `real/dioxuslabs-com@1024` | 158 | 9.0% / 1.4% / 3.8% | 2/48, 6 | 1,232 / 1,232 / 1,232 |
| `real/bootstrap-dashboard` | 199 | 2.9% / 1.3% / 1.9% | 4/12, 1 | 1,136 / 1,136 / 1,154 |
| `real/bootstrap-dashboard@1024` | 199 | 4.0% / 2.2% / 3.2% | 4/12, 1 | 1,132 / 1,132 / 1,150 |

Chrome and Firefox agree on every page to within 0.3% of the page height (the pixel difference is
glyph rasterisation plus a few 1px line-height roundings). Known differences, each with the CSS
feature responsible (Blitz unless stated; "positions" differ wherever an earlier height does):

- `float`: Blitz lays floats out in flow. Wikipedia's infobox (`.stack-right{float:right}`) and
  `.mw-indicators{float:right}` become full-width blocks above the lead paragraphs, so every
  paragraph is 752px wide instead of beside the 326px infobox: the page is 2.4% taller at 1280
  and 9.1% at 1024, and 474 of the 866 boxes differ. Servo floats the infobox but wraps the text
  beside it narrower than Chrome/Firefox (its 10.5% pixel difference; it gives no boxes to quantify).
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
  `🔬` in `.stab.unstable` falls back to no emoji font (511 vs 528px wide); over the 15,947-element
  page this adds 6% of height (164,853 vs 155,326), 129/1792 boxes.
- Table rows: Blitz rounds layout to whole pixels, so each of the Bootstrap dashboard's 17 table
  rows is 1px taller (`.table-responsive` 544 vs 526px, page +18px). Wikipedia's toolbar tabs are
  35px instead of 32px for the same reason (`.vector-menu-content`, ±3px).
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
| `blitz-pcon` / `blitz-par-pcon` | `blitz-runner` built with `--features parallel-construct` (`cargo build --release -p layout-bench-blitz --features parallel-construct --target-dir target-pcon`): the deferred construction tasks (`pconstruct`, Parley layout builds) run on the rayon pool; with sequential / parallel style | same |
| `servo1` / `servo` | servoshell built with `--features tracing-perfetto`, `--pref layout_threads=1` / `3` (default), one process per iteration, spans read from `servo.pftrace` | `Styling`, `Box Tree Construction`, `Fragment Tree Construction`, `restyle_and_build_trees`, `Stacking Context Tree Construction`, `Display List Construction`, `handle_reflow` |
| `chrome` | Playwright chromium-headless-shell, CDP `Tracing` with `devtools.timeline` + `blink_style` | `Document::recalcStyle` (style), `Document::rebuildLayoutTree` (LayoutObject construction), `UpdateLayoutTree` (= both), `Layout` |
| `firefox1` / `firefox` | Playwright Firefox, one process per iteration (launch retried on the occasional startup segfault), Gecko profiler started at launch (`MOZ_PROFILER_STARTUP`, markers only) and written at shutdown (`MOZ_PROFILER_SHUTDOWN`); `layout.css.stylo-threads=1` (no style worker threads) / default (6 on this VM) | `Styles` (style traversal + frame construction), `Reflow`, `DoFlushPendingNotifications` (the flush containing both), `DisplayList` |
| `ladybird` | `Ladybird --headless=layout-tree`, one process per iteration, built with `patches/ladybird-phase-timing.patch` which prints `LADYBIRD_PHASE style=<ns> construct=<ns> layout=<ns> total=<ns> full_layouts=<n>` to stderr for every `Document::update_layout()` round (see [Ladybird](#ladybird)) | `style` (`Document::update_style()`), `construct` (layout tree build, `LayoutRoundJob::build`), `layout` (`lay_out_root` / `lay_out_boundary`, the layout pass including the `LayoutState` commit), `total` (the whole round) |

Phase mapping used in the report:

- Layout only: Taffy `compute_layout` ≈ Blitz `layout` ≈ Servo Fragment Tree Construction ≈ Chrome `Layout`
  ≈ Firefox `Reflow` ≈ Ladybird `layout`.
- Box construction + layout: Blitz `construct + layout` ≈ Servo Box Tree + Fragment Tree ≈ Chrome
  `rebuildLayoutTree + Layout` (Chrome builds `LayoutObject`s inside `UpdateLayoutTree`, not `Layout`)
  ≈ Ladybird `construct + layout`.
  Firefox is left out: Gecko constructs frames inside the `Styles` flush and has no separate
  marker for it, so `Reflow` is layout only.
- Style: Blitz `style` ≈ Servo `Styling` ≈ Chrome `recalcStyle`; Firefox `Styles` is listed
  here too but, like Chrome's `UpdateLayoutTree`, it includes frame construction; Ladybird `style` is `update_style()`.
- Whole pipeline: Blitz `resolve()` (style to paint tree) ≈ Servo `handle_reflow` (style to display
  list) ≈ Chrome `UpdateLayoutTree + Layout` ≈ Firefox `Styles + Reflow`
  ≈ Ladybird `update_layout()` (style to committed layout tree; no display list).

Servo's `restyle_and_build_trees` and `handle_reflow` include work the children spans do not
(stylist preparation, damage computation); the report shows them separately.

Firefox reports the longest `Reflow` and `Styles` marker of the page's content process. The reveal
flush is one `Styles` + one `Reflow`; the page also records a few sub-0.1 ms reflows (the initial
`display:none` document, a nested flush after the reveal), so `verify` prints the reflow count and
the sum of all reflows relative to the longest. The `Styles` marker's `elementsTraversed` is the
styled-element count (`styled=` in `verify`, nodes + `html`/`body`/`#cb`).

## Running

Prerequisites: Rust toolchain; `pip install playwright perfetto pillow && python -m playwright
install chromium firefox` (Firefox is optional: `run.py` skips `firefox*` with a message if it is
not installed); a Servo checkout built with `./mach build --release --features tracing-perfetto`
(`SERVOSHELL=/path/to/servoshell` if not at `~/repos/servo/target/release/servoshell`).

```sh
cargo build --release
./run.py gen                                   # writes corpus/
./run.py bench --rounds 3 --iters 3 --cpus 2   # all engines, interleaved rounds; out/report.md, out/results.json
./run.py report                                 # rewrite out/report.md from out/results.json
./run.py bench --engines taffy,blitz,servo1 --filter grid
./run.py verify                                # screenshots per engine + % pixels differing, out/shots/
./run.py verify --filter real/ --engines chrome,blitz,firefox1,servo1   # the saved real pages
real/freeze.py fetch wikipedia && real/freeze.py freeze wikipedia       # re-save and re-freeze a real page
```

`bench` runs every engine on every case in each round, alternating engine order between rounds,
and reports the minimum (or `--agg median`) over all samples. `--cpus` pins the single-threaded
runners (`taffy`, `blitz`, `servo1`, `firefox1`) with `taskset`; `blitz-par`, `servo`, `chrome` and
`firefox` run unpinned. For `firefox1` only the tab content processes are pinned (found under the
parent via `/proc` after a first blank `file://` page has put the tab in its content process):
pinning the whole browser to one CPU puts the parent process and compositor on the page's CPU and
inflated `Styles`/`Reflow` 3x.

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

Measured on 2026-10-20 on an 8-vCPU Intel Xeon AWS VM (31 GB, Ubuntu 22.04.5, kernel 6.8.0-1060-aws),
rustc 1.99.1, Python Playwright 1.64.0. Every number in `out/` comes from this machine; children
sessions that add engines or cases only verify equal work and run a one-round smoke test, the
measurement is redone here with `bench --merge`.

| engine | version | how it is driven and timed |
|---|---|---|
| Chrome | Chromium 156.0.8078.4 (Playwright `chromium_headless_shell-1248`, headless shell, `--no-sandbox`) | New page per iteration, 1280×800, `file://` reveal page, `load` + wait for the reveal; CDP `Tracing` with categories `devtools.timeline`, `disabled-by-default-devtools.timeline`, `blink`, `blink_style`; longest `X` event of each name: `Document::recalcStyle` (style), `Document::rebuildLayoutTree` (LayoutObject construction), `UpdateLayoutTree` (both), `Layout` (fragment-tree layout). `totalObjects` from the `Layout` event is the equal-work count. Not pinned (multi-process). |
| Firefox | Firefox 157.0 (Playwright `firefox-1555`) | One browser launch per iteration with the Gecko profiler on from startup (`MOZ_PROFILER_STARTUP=1`, features `nostacksampling,nomarkerstacks`, filter `GeckoMain`), profile written by `MOZ_PROFILER_SHUTDOWN`; the content process whose page is the case is read for the `Styles` interval marker (style, includes frame construction), `Reflow` start/end pairs (layout; the longest one is reported, the sum is within 1% of it) and `DisplayList`. `firefox1` sets `layout.css.stylo-threads=1` and pins only the tab content process with `taskset`; `firefox` is the default (5 style workers here), unpinned. |
| Servo | servoshell 0.7.0-5d93f1a6f (built 2026-10-20 from servo/servo `5d93f1a6f`, `./mach build --release --features tracing-perfetto`) | One process per iteration (`-z -x`, 1280×800), page served over localhost HTTP (its fetch rejects `file://` fonts); `SERVO_TRACING=layout::layout_impl=trace,layout::flow::root=trace` (phase spans only; per-item spans would add >10×), spans read from `servo.pftrace` with the `perfetto` Python module: `Styling`, `Box Tree Construction`, `Fragment Tree Construction`, `Stacking Context Tree Construction`, `Display List Construction`, `handle_reflow`. `servo1` = `--pref layout_threads=1`, pinned; `servo` = default 3 layout threads (Stylo pool shared by style and box construction), unpinned. |
| Blitz | DioxusLabs/blitz `28f848d` (blitz-dom with Taffy `ea07c4c`, Stylo 0.22.0, Parley 0.12.0, harfrust 0.12.0, skrifa 0.44.0) | `blitz-runner` (this repo): fresh `HtmlDocument` per iteration from the plain `corpus/*.html`, `incremental=false`, one `resolve()`; phase times from Blitz's own `log-phase-times` timer via a vendored `debug_timer` printing ns: `style`, `construct` (+ `pconstruct`, the deferred Parley layout builds = shaping), `layout` (Taffy + Parley line breaking), `paint_tree`, `resolve`. `blitz` = sequential style, pinned; `blitz-par` = `StyleThreading::Parallel`; `blitz-pcon` / `blitz-par-pcon` = second build with `--features parallel-construct` (deferred construction on the rayon pool). Equal work: hash of every element's final box, `--boxes` dump. |
| Taffy | DioxusLabs/taffy `4e59968` (`taffy_benchmarks` for the tree shapes and PanGUI templates) | `gen bench`: the same tree built directly in a `TaffyTree`, all nodes dirtied, `compute_layout` timed with `Instant`; pinned. `--wrapped` lays it out as the page does (abspos child of a viewport-sized box, ~10% more work). Blitz's Taffy is 4 commits older than this one; measured difference on flex/wide/10000 is 1.4% of instructions. |

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
  runs, `root`, `hash`, `boxes`. `bench --merge` re-measures a subset of engines or cases in place.
- `out/report.md`: the formatted tables (`./run.py report` rewrites it from `results.json`), columns
  ordered Chrome, Firefox, Servo, Blitz, Taffy, each cell `ms` over `N.NNx` (a `<br>`), the fastest non-Taffy cell of the row in bold, relative to the Chrome column of
  the same table.
- `out/verify.md`: the equal-work table (`./run.py verify`).

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
~15 s: it only touches the Rust layout crate, one LibWeb file and LibWebView.

The patch instruments `Libraries/LibWeb/Rust/src/layout/update_layout.rs`, where LibWeb's layout
update now lives (`Document::update_layout()` in `Libraries/LibWeb/Layout/UpdateLayout.cpp` calls
`render_state_update_layout` once per round; a round re-runs only when a layout reached a web font
or image that was already available). Per round it prints the time spent in the style callback
(`Document::update_style()`), in the layout tree build (`construct`), in the layout pass(es)
(`layout`, which commits the `LayoutState` as it goes) and in the round as a whole (`total`), plus
how many full (root) layout passes ran. The runner takes the round with the longest `layout` of
the process, i.e. the reveal layout (the `display:none` document's round builds and lays out a
handful of boxes), and reports the number of rounds with a full layout as `layouts=N`. `verify`
uses `--headless=layout-tree` for the box positions (the dump's `at [x,y]` is the content box; the
runner adds padding and border to get the border boxes it compares with Chrome's
`getBoundingClientRect()`) and a second `--headless=screenshot` process for the 1280×800 image.
The patch also makes both headless modes wait `--screenshot-delay` seconds *after the load event*
(upstream dumps the layout tree at the load event and counts the screenshot delay from the start
of the load): the font pages reveal from a `document.fonts` promise that resolves after the load
event, and the screenshot has to wait for the reveal to be painted. The runner passes
`LADYBIRD_SETTLE_SECONDS` (default 2) for that delay, so every Ladybird process costs that much
extra wall-clock on top of the load; it does not affect the phase timings.

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

`layouts=2` on every page (the `display:none` document, then the reveal); the font pages add one
round per web font that finishes loading before the reveal.

## Servo tracing filter

Servo is run with `SERVO_TRACING="layout::layout_impl=trace,layout::flow::root=trace"`, which
enables only the phase spans. `layout=trace` would also record the per-item spans
(`FlexItem::layout`, `FlexContainer::layout`, ...), and at ~6 µs per span those inflate
Fragment Tree Construction by more than 10x on these trees (31 ms vs 2.3 ms for flex/wide/1000).
