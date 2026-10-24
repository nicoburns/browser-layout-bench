# WebKit engine: timing method, validation and smoke run

Added 2026-10-24 (`engines_webkit.py`). WebKit = Playwright 1.64.0's `webkit-2370` (WPE MiniBrowser bundle,
`browser.version` 27.2, UA `AppleWebKit/605.1.15 … Version/27.2 Safari/605.1.15`). All numbers below were
measured on the same 8-vCPU Xeon VM as the rest of `out/`, but in a different window from `out/results.json`,
so they are not comparable with the stored columns: the Chrome column of each table is the one measured
alongside WebKit.

## How the phases are timed

Playwright exposes no raw protocol session for WebKit in Python, so `engines_webkit.py` launches the binary
itself (`MiniBrowser --inspector-pipe --headless --no-startup-window`) and speaks the Playwright WebKit
protocol over fds 3/4 (null-delimited JSON; `Playwright.createContext/createPage/navigate`, Inspector
domains of a page wrapped in `Target.sendMessageToTarget`). Two methods were tried:

1. **Web Inspector `Timeline` domain** (`Timeline.start/stop`, `Timeline.eventRecorded`): gives
   `RecalculateStyles` and `Layout` records of the reveal, but recording also emits an `InvalidateLayout`
   record, with a captured JS stack, from `RenderObject::setNeedsLayout` for every renderer the reveal
   dirties (one per box: 101,129 records on `pangui/fit_nesting`, 10,019 on `flex/wide/10000`; the protocol
   has no filter and `maxCallStackDepth` does not help), and that work lands inside the style phase.
   Rejected for timing because of (b) below; `verify` still turns it on to count layouts.
2. **JS timing from a bootstrap script** (used): `Page.setBootstrapScript` runs before any page script and
   wraps `HTMLElement.prototype.offsetHeight`. The reveal script (unchanged) does
   `cb.style.display=…; cb.offsetHeight`; the wrapper takes `performance.now()`, forces style with
   `getComputedStyle(cb).display` (WebKit resolves the whole dirty document for a computed-style read),
   takes the time again, runs the original getter (forced layout) and stores `style`, `layout`, `total` in
   `window.__lb`. `performance.now()` is 1 ms-grained in WebKit unless the page is cross-origin isolated
   (`Performance::allowHighPrecisionTime`, 20 µs), so the corpus is served over localhost HTTP with
   COOP `same-origin` + COEP `require-corp` (measured: `crossOriginIsolated` true, smallest `now()` step
   0.02 ms; over `file://` it is 1 ms). COOP makes WebKit swap the page into a fresh web process on the
   navigation (a provisional Inspector target that has to be enabled and resumed), so every sample is a
   cold process, as for the other multi-process engines here.

## Validation (3 iterations per case, ms; `~/scratch/wk_validate2.py`)

"split" is the production bootstrap (style and layout forced separately), "unsplit" the same wrapper
without the `getComputedStyle` call (one forced style+layout), "traced" is split with the Timeline on.

| case | split style | split layout | split total | unsplit total | traced: JS total | traced: Timeline RecalculateStyles / Layout | Timeline records |
|---|---|---|---|---|---|---|---|
| `pangui/fit_nesting` | 408 / 393 / 455 | 226 / 197 / 204 | 634 / 590 / 659 | 689 / 635 / 599 | 1160 / 1148 / 1204 | 958.4 / 201.8, 943.1 / 205.0, 993.8 / 209.8 | 101,129 |
| `flex/wide/10000` | 47.9 / 32.4 / 43.7 | 30.3 / 27.7 / 37.2 | 78.2 / 60.1 / 80.9 | 62.7 / 60.8 / 63.3 | 110 / 121 / 135 | 81.7 / 28.0, 89.0 / 32.1, 97.8 / 36.6 | 10,019 |
| `flex/absolute/10000` | 67.5 / 84.9 / 41.2 | 29.7 / 55.7 / 25.2 | 97.2 / 141 / 66.5 | 68.3 / 70.4 / 69.3 | 152 / 126 / 123 | 123.1 / 29.1, 99.4 / 26.8, 94.6 / 27.9 | 10,021 |
| `grid/wide/100x100` | 48.4 / 77.0 / 38.5 | 106 / 88.4 / 44.7 | 155 / 165 / 83.2 | 96.3 / 84.9 / 73.9 | 203 / 364 / 170 | 73.9 / 128.6, 147.8 / 216.4, 78.5 / 90.9 | 18,724 |
| `text/paragraphs/1000` | 10.0 / 12.0 / 6.3 | 88.4 / 82.6 / 43.3 | 98.4 / 94.6 / 49.6 | 47.9 / 80.3 / 112 | 95.9 / 51.3 / 50.5 | 12.8 / 83.0, 11.3 / 39.9, 11.5 / 39.0 | 1,031 |
| `real/wikipedia` | 191 / 190 / 197 | 401 / 308 / 320 | 592 / 497 / 517 | 522 / 594 / 530 | 706 / 887 / 711 | 346.0 / 359.7, 438.0 / 449.3, 353.3 / 357.9 | 34,576 |

- (a) **Protocol vs JS**: with the Timeline on, its `RecalculateStyles` + `Layout` equals the JS-timed
  split within 0.3 ms on every sample (e.g. 958.39 + 201.76 vs JS 958.6 + 201.8; 346.01 + 359.65 vs
  346.1 + 359.7), so the JS wrapper brackets exactly the two Inspector phases.
- (b) **Instrumentation overhead**: the Timeline is not free — the style phase is 2–2.5× slower with it
  on (fit_nesting 393–455 → 943–994, flex/wide 32–48 → 82–98, wikipedia 190–197 → 346–438) while
  `layout` is unchanged (fit_nesting 197–226 vs 202–210, flex/wide 28–37 vs 28–37). That is why the
  Timeline is not the timing source. The bootstrap wrapper itself costs nothing measurable: splitting
  the forced update into style then layout gives the same total as one forced update (minimum split vs
  unsplit: fit_nesting 590 vs 599, flex/wide 60.1 vs 60.8, flex/absolute 66.5 vs 68.3, grid 83.2 vs 73.9,
  paragraphs 49.6 vs 47.9, wikipedia 497 vs 522; the sample-to-sample spread of this VM is larger than any
  of these differences).
- (c) **First layout of the revealed tree**: one `Layout` record per sample on the generated cases
  (the reveal runs synchronously at the end of parsing, before any rendering update). Cases whose reveal
  awaits `document.fonts` (`text/*`, `real/*`) get one 0.1–0.8 ms layout of the hidden page first
  (`#cb` is `display:none`), then the one measured layout; there is no second full layout like Firefox's.
  `verify` reports the count as `webkit layouts=N` (2 on those cases, 1 otherwise).
- **Noise**: this VM's spread between consecutive samples is up to 2× (grid 83–165 ms, paragraphs
  50–98 ms), which the min-of-9 aggregation absorbs; the report's minima are the comparable figures.

### Per-iteration wall overhead

Wall time per iteration (page creation, process swap, navigation and parse, polling for the reveal,
teardown) minus the measured `style+layout`, split bootstrap, Timeline off: `pangui/fit_nesting`
~830 ms (17.7 MB of HTML to parse), `flex/wide/10000` ~230 ms, `flex/absolute/10000` ~240 ms,
`grid/wide/100x100` ~240 ms, `text/paragraphs/1000` ~250 ms, `real/wikipedia` ~330 ms. With the
Timeline on (verify only) the protocol stream adds another 0.1–1.5 s per iteration.

## LayoutUnit saturation

WebKit's `LayoutUnit` is the same 1/64 px `int32` as Blink's, and it saturates on the same two cases at
the same 33,554,432 px: on `flex/wide/10000` the items overflow their 854,597 px container to a total of
34.3 M px and every box whose left edge or right edge would pass 2^25 px is clamped there, 8,440 of
10,001 boxes in WebKit (first clamped box #1,558) vs 8,416 in Chrome (first #1,581); on
`flex/absolute/10000` 5,800 of 10,004 boxes (first #3,743) vs Chrome's 5,729 (first #3,825). The
`#cb` child itself is below the limit in both (`root` 854,596.9 × 500.0 and 423,959.3 × 499.8 px,
identical in the two engines), so `root` does not show it; the box lists do. The 1,116 / 1,558 box-size
mismatches `verify` reports between them are the un-clamped boxes differing by ~0.4% in width (e.g. box
#17: 615,662 vs 618,184 px; flex-shrink rounding at these magnitudes), not the clamping, which both do.
Neither case is equal work for either browser, as the README already says for Chrome.

## `verify` WebKit vs Chrome (2026-10-24, one sample each, 1280×800 screenshots)

| case | nodes | px differing | WebKit vs Chrome boxes (`div`/`p`/`h3`) | page height Chrome / WebKit | layouts Chrome / WebKit |
|---|---:|---|---|---|---|
| `real/wikipedia` | 21,889 | 5.99% | 208/866 sizes >1 px (max 323.8 px), 594 positions | 85,068 / 84,997 | 2 / 2 |
| `real/mdn` | 2,212 | 3.56% | 4/176 (max 28.0 px), 23 | 19,760 / 19,788 | 2 / 2 |
| `real/rustdoc` | 15,947 | 1.84% | 0/1792 (max 0.3 px), 0 | 155,326 / 155,326 | 3 / 2 |
| `real/css-flexbox-1` | 15,890 | 1.56% | 3/471 (max 528.8 px), 428 | 90,168 / 90,170 | 2 / 2 |
| `real/servo-org` | 226 | 1.16% | 0/84 (max 0.2 px), 0 | 5,445 / 5,444 | 2 / 2 |
| `real/dioxuslabs-com` | 158 | 1.04% | 0/48 (max 0.0 px), 0 | 1,232 / 1,232 | 2 / 2 |
| `real/bootstrap-dashboard` | 199 | 1.40% | 2/12 (max 1.9 px), 2 | 1,136 / 1,136 | 2 / 2 |
| `flex/wide/10000` | 10,001 | 0.00% | 1116/10001 (max 3,016 px), 1567 | root 854,596.9×500.0 both | 2 / 1 |
| `flex/absolute/10000` | 10,004 | 0.33% | 1558/10004 (max 1,476 px), 3990 | root 423,959.3×499.8 both | 2 / 1 |
| `pangui/fit_nesting` | 101,111 | 27.94% | 0/101111 (max 0.0 px), 0 | root 1000.0×1010.0 both | 2 / 1 |

All fonts `loaded` in both. Chrome's layout count includes the layout of the hidden page before the reveal
(its `n_layouts` is from the trace); WebKit's is the Timeline `Layout` record count. `pangui/fit_nesting`'s
27.94% px with identical boxes is paint, not layout: the boxes are sub-pixel wide and the two engines
snap/antialias their fills differently (WebKit's screenshot shows regular lighter vertical bands).

## Smoke benchmark

`./run.py bench --engines chrome,webkit --rounds 3 --iters 3 --out webkit-smoke.json` (2026-10-24, not committed),
43 cases, min of 9 samples, ms. Wall time of the run per engine column, measured around `run_engine` (browser
launch, page creation, navigation and parse, the measured spans, teardown; 43 × 9 samples): Chrome 144.1 s,
WebKit 195.3 s, i.e. 0.37 s and 0.50 s per sample; whole command 339.8 s.

| case | n | Chrome style | WebKit style | Chrome layout | WebKit layout | Chrome style+layout | WebKit style+layout |
|---|--:|--:|--:|--:|--:|--:|--:|
| flex/huge_nested/1000 | 9 | 1.44 | 3.02 | 0.91 | 1.94 | 2.72 | 4.96 |
| flex/wide/1000 | 9 | 1.36 | 3.20 | 1.23 | 2.72 | 3.02 | 5.92 |
| flex/absolute/1000 | 9 | 1.60 | 4.18 | 1.30 | 2.48 | 3.57 | 6.66 |
| flex/deep_auto/1000 | 9 | 0.80 | 2.12 | 1.64 | 1.96 | 2.78 | 4.10 |
| flex/deep_random/1000 | 9 | 0.94 | 2.42 | 0.91 | 2.66 | 2.19 | 5.08 |
| flex/huge_nested/10000 | 9 | 14.13 | 30.48 | 8.67 | 18.34 | 26.49 | 48.82 |
| flex/wide/10000 | 9 | 13.21 | 32.90 | 12.96 | 27.08 | 29.71 | 59.98 |
| flex/absolute/10000 | 9 | 15.90 | 40.82 | 13.96 | 24.92 | 35.95 | 65.74 |
| flex/deep_auto/10000 | 9 | 10.21 | 24.10 | 17.41 | 17.98 | 31.34 | 42.10 |
| flex/deep_random/10000 | 9 | 9.78 | 27.22 | 8.99 | 23.90 | 21.95 | 53.56 |
| flex/superdeep/50 | 9 | 0.30 | 0.64 | 0.45 | 0.50 | 0.90 | 1.14 |
| flex/superdeep/100 | 9 | 0.53 | 1.08 | 0.86 | 0.90 | 1.66 | 1.98 |
| grid/wide/31x31 | 9 | 1.23 | 3.22 | 2.65 | 3.62 | 4.28 | 6.92 |
| grid/wide/100x100 | 9 | 12.29 | 31.90 | 35.62 | 39.88 | 51.22 | 72.28 |
| grid/deep/2x2x5 | 9 | 2.19 | 6.44 | 6.92 | 18.66 | 9.71 | 25.12 |
| grid/deep/3x3x4 | 9 | 10.90 | 28.62 | 29.95 | 82.64 | 43.63 | 111.26 |
| grid/superdeep/100 | 9 | 0.21 | 0.90 | 1.45 | 321.84 | 1.82 | 322.76 |
| pangui/expand_with_max_constraint | 9 | 4.46 | 9.82 | 3.59 | 6.92 | 9.22 | 16.78 |
| pangui/expand_with_min_constraint | 9 | 4.46 | 9.72 | 3.67 | 6.92 | 9.42 | 16.64 |
| pangui/fit_nesting | 9 | 244.28 | 379.16 | 138.32 | 200.06 | 434.40 | 587.60 |
| pangui/flex_expand_equal_weights | 9 | 29.60 | 53.62 | 11.60 | 43.06 | 47.16 | 96.88 |
| pangui/flex_expand_weights | 9 | 21.95 | 46.82 | 11.20 | 43.82 | 39.35 | 90.96 |
| pangui/nested_vertical_stack | 9 | 19.35 | 35.56 | 7.23 | 27.42 | 30.11 | 63.52 |
| pangui/padding_and_margin | 9 | 0.28 | 0.56 | 0.14 | 0.40 | 0.52 | 0.96 |
| pangui/percentage_and_ratio | 9 | 21.61 | 36.44 | 13.97 | 25.44 | 40.34 | 61.88 |
| pangui/perpendicular_expand_with_wrap | 9 | 22.96 | 43.00 | 13.14 | 30.10 | 40.15 | 73.42 |
| pangui/pixels_with_min_expand_constraint | 9 | 44.49 | 95.32 | 35.60 | 70.88 | 91.39 | 166.20 |
| pangui/wide_no_wrap_simple_few | 9 | 1.98 | 3.60 | 0.77 | 1.98 | 3.15 | 5.60 |
| pangui/wide_no_wrap_simple_many | 9 | 231.08 | 368.94 | 83.84 | 213.80 | 361.73 | 586.54 |
| pangui/wide_wrapping | 9 | 19.58 | 36.22 | 8.70 | 20.00 | 32.22 | 56.24 |
| text/paragraphs/100 | 9 | 0.20 | 0.66 | 5.46 | 6.16 | 5.74 | 6.82 |
| text/flex_cards/100 | 9 | 0.31 | 1.16 | 3.54 | 6.14 | 4.05 | 7.32 |
| text/inline_mixed/100 | 9 | 0.79 | 4.82 | 9.12 | 17.68 | 10.90 | 22.60 |
| text/paragraphs/1000 | 9 | 1.72 | 5.66 | 52.89 | 38.32 | 55.23 | 43.98 |
| text/flex_cards/1000 | 9 | 2.80 | 9.52 | 32.65 | 36.00 | 36.98 | 45.52 |
| text/inline_mixed/1000 | 9 | 7.61 | 45.12 | 84.66 | 103.90 | 102.63 | 151.96 |
| real/wikipedia | 9 | 45.88 | 182.46 | 146.33 | 288.72 | 213.92 | 473.20 |
| real/mdn | 9 | 5.75 | 15.80 | 10.95 | 18.34 | 18.30 | 34.14 |
| real/rustdoc | 9 | 19.66 | 61.44 | 88.34 | 145.60 | 121.27 | 207.04 |
| real/css-flexbox-1 | 9 | 18.13 | 63.82 | 86.21 | 197.42 | 115.94 | 262.50 |
| real/servo-org | 9 | 0.75 | 3.02 | 2.12 | 4.02 | 3.10 | 7.06 |
| real/dioxuslabs-com | 9 | 0.98 | 6.40 | 3.30 | 3.32 | 4.47 | 9.72 |
| real/bootstrap-dashboard | 9 | 0.79 | 2.64 | 1.60 | 2.26 | 2.63 | 4.90 |

- `grid/superdeep/100` (100 nested grids): WebKit's layout is 322 ms against Chrome's 1.45 ms in every
  one of the 9 samples, with identical geometry (`verify`: 0/101 boxes differ, root 158.7×82.6 in both,
  1 layout each) — a measured WebKit pathology in nested grid intrinsic sizing; the cause was not
  investigated.
- WebKit's `style` is 2–3× Chrome's on every case and its `layout` 1–3× except `text/paragraphs/1000`
  (38 vs 53 ms) and `flex/deep_auto/10000` / `text/flex_cards/1000` (about equal). Note the WebKit
  `style` includes render-tree construction and Chrome's `style` here is `UpdateLayoutTree`
  (which includes `rebuildLayoutTree`), so the Style and Whole-pipeline columns are comparable work.
- Robustness: one full-suite run before this one stalled on a WebKit page with the browser idle; at the
  time the runner waited only for `load` from a new (process-swapped) target and read the pipe without a
  timeout. It now accepts `load` from the current target as well and times out idle pipe reads; the stall
  did not recur in the 240 page loads tried afterwards nor in this run, so its cause (presumably a
  navigation without a process swap) is inferred, not observed.
