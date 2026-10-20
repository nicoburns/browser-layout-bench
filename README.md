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
and the surrounding style/box machinery only.

The root is absolutely positioned inside a `#cb` containing block sized to the Taffy available
space (`max-content` becomes a 1,000,000px box). `run.py gen` also writes `corpus/reveal/*.html`
for Servo and Chrome: the tree starts `display:none` and a trailing script reveals it and forces
layout, so the whole tree is styled and laid out in a single reflow after parsing has finished.

## Engines and phases

| engine | how it is run | phases reported |
|---|---|---|
| `taffy` | `gen bench`: the Taffy tree itself, all nodes marked dirty, `compute_layout` | `layout` |
|  | `gen bench --wrapped`: same tree as an absolutely positioned child of a viewport-sized box, mirroring the page's `#cb` (one layout pass from a definite containing block, as in the browsers; ~10% more work than the bare root) | `layout` |
| `blitz` | `blitz-runner`: fresh `HtmlDocument`, `incremental=false`, one `resolve()` per iteration, phase times from Blitz's `log-phase-times` timer (vendored to print ns) | `style`, `construct`, `layout`, `paint_tree`, `resolve` |
| `blitz-par` | same with `StyleThreading::Parallel` | same |
| `servo1` / `servo` | servoshell built with `--features tracing-perfetto`, `--pref layout_threads=1` / `3` (default), one process per iteration, spans read from `servo.pftrace` | `Styling`, `Box Tree Construction`, `Fragment Tree Construction`, `restyle_and_build_trees`, `Stacking Context Tree Construction`, `Display List Construction`, `handle_reflow` |
| `chrome` | Playwright chromium-headless-shell, CDP `Tracing` with `devtools.timeline` | `UpdateLayoutTree` (style), `Layout` |

Phase mapping used in the report:

- Layout only: Taffy `compute_layout` ≈ Blitz `layout` ≈ Servo Fragment Tree Construction ≈ Chrome `Layout`.
- Box construction + layout: Blitz `construct + layout` ≈ Servo Box Tree + Fragment Tree ≈ Chrome `Layout`
  (Chrome builds `LayoutObject`s during style recalc, so its `Layout` is the nearest single event).
- Style: Blitz `style` ≈ Servo `Styling` ≈ Chrome `UpdateLayoutTree`.
- Whole pipeline: Blitz `resolve()` (style to paint tree) ≈ Servo `handle_reflow` (style to display
  list) ≈ Chrome `UpdateLayoutTree + Layout`.

Servo's `restyle_and_build_trees` and `handle_reflow` include work the children spans do not
(stylist preparation, damage computation); the report shows them separately.

## Running

Prerequisites: Rust toolchain; `pip install playwright perfetto pillow && python -m playwright
install chromium`; a Servo checkout built with `./mach build --release --features tracing-perfetto`
(`SERVOSHELL=/path/to/servoshell` if not at `~/repos/servo/target/release/servoshell`).

```sh
cargo build --release
./run.py gen                                   # writes corpus/
./run.py bench --rounds 3 --iters 3 --cpus 2   # all engines, interleaved rounds; out/report.md, out/results.json
./run.py bench --engines taffy,blitz,servo1 --filter grid
./run.py verify                                # screenshots per engine + % pixels differing, out/shots/
```

`bench` runs every engine on every case in each round, alternating engine order between rounds,
and reports the minimum (or `--agg median`) over all samples. `--cpus` pins the single-threaded
runners (`taffy`, `blitz`, `servo1`) with `taskset`; `blitz-par` and `servo` run unpinned.

`verify` is the equal-work check: before trusting a timing, confirm the engines agree on the layout
(pixel diff of the 1280×800 viewport, Chrome's `totalObjects` layout-object count, Servo's reflow
count, Blitz's box hash).

## Servo tracing filter

Servo is run with `SERVO_TRACING="layout::layout_impl=trace,layout::flow::root=trace"`, which
enables only the phase spans. `layout=trace` would also record the per-item spans
(`FlexItem::layout`, `FlexContainer::layout`, ...), and at ~6 µs per span those inflate
Fragment Tree Construction by more than 10x on these trees (31 ms vs 2.3 ms for flex/wide/1000).
