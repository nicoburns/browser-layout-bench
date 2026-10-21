# Benchmark caveats

**These benchmarks are useful for diagnosing engine costs, but are not yet a clean
cross-browser ranking.** The strongest comparisons are the text-free cases with
matching geometry. Several other tables compare different work, and the saved
samples show substantial variability.

This review was made on 2026-10-20 against
[`f6d5695`](https://github.com/nicoburns/browser-layout-bench/commit/f6d56957334a2aa95e169ab4f41b8b6ec4051d35),
with the Ladybird and verification updates through
[`dbbdbce`](https://github.com/nicoburns/browser-layout-bench/commit/dbbdbce)
accounted for below. Numerical examples come from the saved samples, not new
measurements. Revisit these caveats when the harness, engines, or results change.

The harness does several things well: deterministic inputs, explicit font loading,
phase timing rather than process startup, raw samples, geometry checks, and the
correction of Servo's excessive tracing overhead.

## 1. "Whole pipeline" has different endpoints

The report compares:

- **Blitz:** `resolve()`, including transforms, paint-tree building, damage cleanup,
  and other bookkeeping.
- **Servo:** `handle_reflow`, including stacking-context/display-list work when
  performed.
- **Chrome/Firefox:** style/tree construction + layout, excluding the corresponding
  later rendering work.
- **Ladybird:** committed layout, not display-list construction.

That systematically gives Blitz/Servo more work inside the reported interval. It
is not a fair "style to paint tree/display list" comparison.

**Choose a common endpoint**, preferably layout completion for this benchmark.
Merely subtracting Blitz's paint-tree duration would not remove all the extra work.

Sources: [reported intervals](run.py),
[Blitz's resolve implementation](https://github.com/DioxusLabs/blitz/blob/28f848d/packages/blitz-dom/src/resolve.rs),
and [Ladybird instrumentation](patches/ladybird-phase-timing.patch).

## 2. Equal-work validation is incomplete

Known failures still receive timings and can win rows. The clearest exclusion is
Servo's `pangui/percentage_and_ratio`: it renders empty. Its timing should be
**N/A**, not eligible to win a row.

Other cases need qualification:

- `flex/absolute/10000` has substantially different geometry.
- `flex/wide/10000` reports **3,505 box-size mismatches, a maximum difference of
  735,072 px, yet 0% viewport pixel difference** for Blitz versus Chrome. Whether
  this is a dump/correspondence bug or a layout difference, it is unresolved
  verification evidence, not proof of equal work.
- Servo's text check sees only the first 800 pixels: "7/7 background bands equal"
  does not establish equivalence across 1,000 paragraphs.
- Ladybird's `flex/huge_nested/*` root sizes differ substantially from Chrome's,
  and some text paragraphs wrap differently. Matching node counts alone does not
  establish matching layout work.

The original verification snapshot lacked Firefox even though it appeared in the
timing tables. **That coverage gap was resolved by `dbbdbce`**, which adds Firefox
and Ladybird to the committed [verification table](out/verify.md). This does not
resolve the geometry and viewport-coverage limitations above.

Small rasterisation differences are not themselves disqualifying. Missing layout
features, different wrapping, or skipped content are. Validation should cover
offscreen geometry and text line counts, not just viewport pixels or root sizes.
Exclude known unequal-work engine/case pairs from rankings, and investigate
unexplained mismatches before treating them as equivalent.

### Frozen real pages

The [real-pages work reviewed at `0f0d306`](https://github.com/nicoburns/browser-layout-bench/blob/0f0d306/README.md)
adds useful coverage, but is not equal-work evidence: it documents unsupported
floats and other layout differences. For example, the frozen Wikipedia page at
1024 px is 69,635 px tall in Chrome versus 75,984 px in Blitz. Knowing the cause
explains the mismatch; it does not make the workloads equivalent.

These pages are simplified snapshots: scripts are removed, fonts are replaced,
images become placeholders, and some CSS and controls are rewritten. They test
the resulting frozen documents, not the original live sites.

## 3. Minimum-of-nine hides significant instability

For Blitz's `text/paragraphs/1000` resolve time, the saved samples have:

| Statistic | Time |
|---|---:|
| Minimum | 143.4 ms |
| Median | 265.8 ms |
| Maximum | 288.7 ms |

That is far beyond a 1–3% variation. A minimum can legitimately estimate best-case
latency, but it is not typical performance, and ratios of independently selected
minima can be unstable. The spread alone does not identify its cause.

The [benchmark-development session](https://dioxus.staging.devinenterprise.com/sessions/e0bfdcc712c54fceabf93d2b8815a524)
assembled the dataset through several `--merge` runs: Chrome was rerun separately,
and Firefox/parallel-construction variants were added later. Consequently, the
final cross-engine comparisons do not all benefit from contemporaneous
interleaving, even though each individual invocation supports it.

**Report median plus spread**, retain minimum as a secondary statistic, and rerun
the final engine set together on an idle machine. Record the run configuration
and provenance so later subset updates remain identifiable.

Sources: [raw samples](out/results.json), [aggregation and merge logic](run.py),
and [documented protocol](README.md#versions-and-methodology).

## 4. Cache state and CPU allocation are not matched

- **Taffy:** reuses its tree, explicitly warms up twice, then dirties nodes.
- **Blitz:** fresh document, but several iterations within one process; mimalloc as the
  global allocator (with glibc, allocator work and page faults were ~37% of the `layout`
  phase on the 100k-node cases).
- **Chrome:** fresh pages within one browser launch.
- **Servo/Firefox/Ladybird:** fresh process per iteration.

Excluding startup time does not eliminate differences in allocator, font,
thread-pool, and other process-local caches. This is neither a consistently cold
nor consistently warmed protocol. Choose and document a common lifecycle, or
report cold and warmed cases separately.

CPU placement also differs: pinned single-threaded configurations, unpinned
parallel configurations, and content-process-only pinning for Firefox. Those are
valid **configuration comparisons**, but not controlled equal-resource
comparisons. Separate single-threaded layout/style and default-parallelism
results, with affinity and worker counts stated explicitly.

Sources: [Taffy runner](gen/src/main.rs), [Blitz runner](blitz-runner/src/main.rs),
[browser runners](run.py), and [Ladybird runner](engines_ladybird.py).

## 5. Instrumentation and corpus scope limit the conclusions

The Servo tracing fix was important: the documented example fell from **31 ms to
2.3 ms** after removing per-item spans. But tracing overhead has not been
equivalently calibrated across all engines. Chrome still enables broad
`blink`/timeline categories; Blitz's outer `resolve()` timer even includes printing
its phase log. Small differences deserve particular caution. Calibrate
instrumentation overhead rather than assuming it is equal or negligible.

Direct Taffy also uses a different revision and, by default, omits the browser's
containing-block wrapper. It is an **algorithm baseline**, not a browser score or
a clean measure of Blitz's integration overhead.

Finally, the synthetic corpus and frozen, simplified real pages measure specific
initial-layout workloads, not general browsing, incremental layout, JavaScript,
or time-to-paint.

Sources: [Servo tracing filter](README.md#servo-tracing-filter),
[versions and methodology](README.md#versions-and-methodology),
[Taffy's optional wrapper](gen/src/main.rs), and [Blitz's outer timer](blitz-runner/src/main.rs).

## 6. Text shaping is in construction for Blitz/Servo but in layout for Chrome/Firefox/Ladybird

Blitz shapes when it builds the Parley inline layout (`construct`, including the deferred
`pconstruct` tasks) and Servo during Box Tree Construction; Chrome, Firefox and Ladybird shape
text lazily while laying it out, so their layout figures include shaping, line breaking and font
fallback and their construction figures (where they exist) are a tree walk. The "Layout only"
table therefore compares different work on any case with text: Blitz `layout` and Servo Fragment
Tree are post-shaping line breaking and box placement, Chrome `Layout` and Ladybird `layout` are
shaping plus that. The "Box construction + layout" table contains the same work for every engine
and is where Firefox's `Reflow` is listed (its frame construction happens inside the `Styles`
flush, with no marker of its own, so that table under-counts Firefox by the frame-construction
time and the Style table over-counts it by the same amount; frame construction is a tree walk
with no shaping, so the amount is small relative to Reflow on text-heavy pages). The `flex/`,
`grid/` and most `pangui/` cases have no text, so there the two tables differ only by genuine
construction cost and "Layout only" is comparable across all engines.

## How to interpret the results

- Treat large differences on geometry-validated, text-free cases as useful leads
  for investigation, for the particular configurations measured.
- Do not rely on current whole-pipeline rankings or failed-verification rows.
- Prioritise matching timing boundaries, excluding unequal-work cases, and
  collecting a fresh, consistently warmed and interleaved dataset with dispersion
  shown before drawing headline browser-performance conclusions.
