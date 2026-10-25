# How full do Blitz's per-node Taffy layout caches get?

Blitz `1c5265a8b3985e1ec05044a115b2ec6266e3fa91` (the harness pin), Taffy `802e497b69689e1c93be2d16e9d53a973971bcb2` (Blitz's pin),
instrumented with `patches/taffy-cache-occupancy.patch` (read-only accessors and counters; the runner's `--hash` is identical with and
without it on all 43 pages). All counts are measured; bytes are `size_of` × counts (the allocator's size-class rounding is not modelled).
Branch: `devin/blitz-cache-occupancy` (`cache-occupancy/` has the collector, summariser, raw per-page JSON and CSVs).

## Conclusion

The saving is real but it is a synthetic-benchmark saving, not a real-page one, and it does not come from the scheme the question
assumed. On the flex/grid/pangui trees every node is an element that gets laid out, so caches are 37% of the node memory we can account
for (`Node` + `ElementData` + `LayoutData`), and because almost every node ends up with 0–2 measure entries after the initial layout a lazy
cache with two inline slots cuts that by about half: 20.8 MB on `pangui/fit_nesting`, 20.6 MB on `pangui/wide_no_wrap_simple_many`,
1.4–1.9 MB on the 10k-node flex and grid pages, i.e. 15–20% of node memory. On the real pages the caches are already small: 70–92% of DOM
nodes are text or inline elements that never get a `LayoutData` (Blitz boxes `LayoutData`, and the `Cache` inside it, lazily per node), so
caches are 9–32% of node memory and the lazy schemes save 0–50% of that, 0.3–11% of node memory (Wikipedia: 405 KB of 17 MB; rustdoc 1.5 MB
of 16 MB; bootstrap-dashboard nothing). Deep flex trees (`flex/deep_auto`, `flex/superdeep`) fill 4–8 slots on most nodes and lose 15–18%
under every inline-slot scheme; wide grids break even.

The data does not support the obvious design, `Option<Box<[measure; 9]>>` allocated on the first measure store (B in the memory table):
flex and grid layout measure nearly every item at least once before laying it out (initial-layout measure hit rate 0% on `wide_no_wrap`,
`flex_expand_weights`, `huge_nested`), so the array gets allocated for 95–100% of nodes and B saves nothing on 25 of 43 pages (−2% from the
pointer). It only wins where nodes are final-only (`fit_nesting`, `flex_expand_equal_weights`, `grid/deep`, `flex/absolute`, text paragraphs).
Boxing the whole `Cache` (A) is worse still: every owner has the final-layout entry, 0–24 empty caches per page. What the histograms support is
keeping the final entry inline plus one or two inline measure slots and spilling to a heap array only above that: C1 saves 50% and C2 45% of
cache bytes across the corpus after the initial layout (46%/44% at the relayout peak). C2 is positive on every page except the deep flex trees
and `bootstrap-dashboard` (−1%); C1 saves more on the 1-entry flex pages but also loses on the 2-entry pages (`flex/wide`, `text/flex_cards`,
`grid/wide`). An exactly sized heap array (D) is the ceiling at 60%. Nine slots is almost never binding: evictions are 0 in the initial layout
on 40 pages (6 on Wikipedia, 42 on `dioxuslabs-com`, 5 on `bootstrap-dashboard`, all table cells and flex items), and the evictions during the
relayout steps come from old-width and new-width entries coexisting — entries that are dead once the width is reverted.

## Sizes (measured)

| type | bytes |
|---|---:|
| `taffy::Cache` | 408 |
| `Option<CacheEntry<LayoutOutput>>` (final-layout entry) | 112 |
| `Option<CacheEntry<Size<f32>>>` (measure entry, × 9 = 288) | 32 |
| `CacheKey` | 24 |
| `LayoutOutput` | 88 |
| `blitz_dom::Node` | 192 |
| `blitz_dom::node::LayoutData` (`Option<Box<_>>` on `ElementData`/`DocumentData`, holds the `Cache`, `unrounded_layout`, `final_layout`, scroll state) | 648 |
| `blitz_dom::ElementData` (boxed in `NodeData::Element`) | 256 |
| `taffy::Layout` | 92 |

The remaining 8 bytes of `Cache` are `recently_used_entries: u16`, `next_measure_entry: u8`, `is_empty: bool`, `mode: u8` and padding.

**Where the cache lives.** At this Blitz rev the `Cache` is not embedded in every `Node`: it is a field of `LayoutData`, which `ElementData`
and `DocumentData` hold as `Option<Box<LayoutData>>`, allocated on the first `layout_data_mut()` call (Taffy's `set_unrounded_layout`,
`cache_store`, or inline layout writing an inline box's layout). Text and comment nodes have no `LayoutData` slot at all, and `cache_get`
goes through `try_layout_data_mut()`, so an unlaid-out element never allocates one. "Cache bytes today" below is therefore
owners × 408 B, where an owner is a node with a `LayoutData`.

## Per-page summary

All memory figures are taken after the initial layout: the extra entries a relayout adds are measurements under the other root width (or re-measurements after a restyle) and are dead once the mutation is reverted, so they do not describe a lazy cache's working set — they do bound what a lazily grown array that is never freed would hold, which is the "peak" column in the memory table. "Peak relayout" occupancy stats are the most-populated snapshot of the original node set (`append` adds clones that are removed again). "Lazy: box measures" is scheme B, "2 inline + spill" is C2, "exact" is D (see the memory table). Node memory = nodes × 192 + elements × 256 + owners × 648 (strings, attributes, computed styles and Parley layouts are not included, so the percentages overstate the share).

| page | DOM nodes | cache owners | owners with ≥1 entry (initial / peak) | final only (initial) | measure slots mean / median / p90 / max (initial) | same (peak relayout) | evictions (initial / Σ relayout) | cache bytes today | lazy: box measures | lazy: 2 inline + spill | lazy: exact | saving (2 inline) vs today | vs node mem |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| real/bootstrap-dashboard | 608 | 178 (29%) | 178 / 178 | 14 (8%) | 4.24 / 5 / 6 / 9 | 6.42 / 9 / 9 / 9 | 5 / 30 | 71 KB | 68 KB | 72 KB | 46 KB | -1 KB (-1%) | -0.3% |
| real/css-flexbox-1 | 38735 | 7564 (20%) | 7540 / 7540 | 2667 (35%) | 3.00 / 4 / 5 / 5 | 4.61 / 8 / 8 / 9 | 0 / 115 | 3014 KB | 2316 KB | 2776 KB | 1655 KB | 238 KB (8%) | 1.4% |
| real/dioxuslabs-com | 232 | 145 (62%) | 145 / 145 | 22 (15%) | 3.06 / 2 / 9 / 9 | 3.21 / 3 / 9 / 9 | 42 / 80 | 58 KB | 53 KB | 47 KB | 32 KB | 10 KB (18%) | 5.7% |
| real/mdn | 4804 | 1434 (30%) | 1434 / 1434 | 157 (11%) | 1.46 / 1 / 3 / 9 | 1.76 / 1 / 3 / 9 | 0 / 248 | 571 KB | 538 KB | 338 KB | 245 KB | 233 KB (41%) | 9.6% |
| real/rustdoc | 39944 | 7981 (20%) | 7980 / 7980 | 1597 (20%) | 1.50 / 2 / 2 / 6 | 2.19 / 3 / 3 / 6 | 0 / 0 | 3180 KB | 2793 KB | 1604 KB | 1372 KB | 1576 KB (50%) | 9.4% |
| real/servo-org | 673 | 187 (28%) | 187 / 187 | 15 (8%) | 1.56 / 1 / 2 / 6 | 2.10 / 2 / 3 / 9 | 0 / 0 | 75 KB | 72 KB | 40 KB | 32 KB | 35 KB (47%) | 11.3% |
| real/wikipedia | 47065 | 3974 (8%) | 3974 / 3974 | 496 (12%) | 2.14 / 1 / 5 / 9 | 2.88 / 2 / 7 / 9 | 6 / 170 | 1583 KB | 1475 KB | 1179 KB | 763 KB | 405 KB (26%) | 2.3% |
| pangui/expand_with_max_constraint | 3015 | 3005 (100%) | 3005 / 3005 | 4 (0%) | 1.66 / 1 / 3 / 3 | 2.00 / 1 / 4 / 4 | 0 / 0 | 1197 KB | 1220 KB | 845 KB | 532 KB | 353 KB (29%) | 11.0% |
| pangui/expand_with_min_constraint | 3015 | 3005 (100%) | 3005 / 3005 | 4 (0%) | 1.66 / 1 / 3 / 3 | 2.00 / 1 / 4 / 4 | 0 / 0 | 1197 KB | 1220 KB | 845 KB | 532 KB | 353 KB (29%) | 11.0% |
| pangui/fit_nesting | 101125 | 101115 (100%) | 101115 / 101115 | 100004 (99%) | 0.02 / 0 / 0 / 2 | 0.04 / 0 / 0 / 4 | 0 / 0 | 39.3 MB | 12.6 MB | 18.5 MB | 12.4 MB | 20.8 MB (53%) | 19.7% |
| pangui/flex_expand_equal_weights | 15015 | 15005 (100%) | 15005 / 15005 | 15005 (100%) | 0.00 / 0 / 0 / 0 | 0.00 / 0 / 0 / 0 | 0 / 0 | 5979 KB | 1876 KB | 2813 KB | 1876 KB | 3165 KB (53%) | 19.7% |
| pangui/flex_expand_weights | 15015 | 15005 (100%) | 15005 / 15005 | 5 (0%) | 1.00 / 1 / 1 / 1 | 1.00 / 1 / 1 / 1 | 0 / 0 | 5979 KB | 6094 KB | 2813 KB | 2344 KB | 3165 KB (53%) | 19.7% |
| pangui/nested_vertical_stack | 10015 | 10005 (100%) | 10005 / 10005 | 4 (0%) | 1.00 / 1 / 1 / 1 | 2.00 / 2 / 2 / 2 | 0 / 0 | 3986 KB | 4063 KB | 1876 KB | 1563 KB | 2110 KB (53%) | 19.7% |
| pangui/padding_and_margin | 115 | 105 (91%) | 105 / 105 | 4 (4%) | 0.96 / 1 / 1 / 1 | 1.91 / 2 / 2 / 2 | 0 / 0 | 42 KB | 42 KB | 20 KB | 16 KB | 22 KB (53%) | 19.3% |
| pangui/percentage_and_ratio | 10015 | 10005 (100%) | 10005 / 10005 | 5 (0%) | 1.00 / 1 / 1 / 1 | 2.00 / 2 / 2 / 2 | 0 / 0 | 3986 KB | 4063 KB | 1876 KB | 1563 KB | 2110 KB (53%) | 19.7% |
| pangui/perpendicular_expand_with_wrap | 12015 | 12005 (100%) | 12005 / 12005 | 4 (0%) | 2.50 / 1 / 4 / 4 | 4.00 / 1 / 7 / 7 | 0 / 0 | 4783 KB | 4876 KB | 3938 KB | 2438 KB | 845 KB (18%) | 6.6% |
| pangui/pixels_with_min_expand_constraint | 30015 | 30005 (100%) | 30005 / 30005 | 4 (0%) | 1.67 / 1 / 3 / 3 | 2.00 / 1 / 4 / 4 | 0 / 0 | 11.7 MB | 11.9 MB | 8438 KB | 5313 KB | 3517 KB (29%) | 10.9% |
| pangui/wide_no_wrap_simple_few | 1015 | 1005 (99%) | 1005 / 1005 | 5 (0%) | 1.00 / 1 / 1 / 1 | 1.00 / 1 / 1 / 1 | 0 / 0 | 400 KB | 407 KB | 188 KB | 157 KB | 212 KB (53%) | 19.7% |
| pangui/wide_no_wrap_simple_many | 100015 | 100005 (100%) | 100005 / 100005 | 5 (0%) | 1.00 / 1 / 1 / 1 | 1.00 / 1 / 1 / 1 | 0 / 0 | 38.9 MB | 39.7 MB | 18.3 MB | 15.3 MB | 20.6 MB (53%) | 19.7% |
| pangui/wide_wrapping | 10015 | 10005 (100%) | 10005 / 10005 | 4 (0%) | 1.00 / 1 / 1 / 1 | 1.00 / 1 / 1 / 1 | 0 / 0 | 3986 KB | 4063 KB | 1876 KB | 1563 KB | 2110 KB (53%) | 19.7% |
| flex/absolute/1000 | 1017 | 1007 (99%) | 1007 / 1007 | 556 (55%) | 0.67 / 0 / 2 / 5 | 0.84 / 0 / 2 / 6 | 0 / 0 | 401 KB | 253 KB | 202 KB | 147 KB | 199 KB (50%) | 18.4% |
| flex/absolute/10000 | 10018 | 10008 (100%) | 10008 / 10008 | 5485 (55%) | 0.70 / 0 / 2 / 5 | 0.89 / 0 / 2 / 6 | 0 / 0 | 3988 KB | 2523 KB | 2039 KB | 1469 KB | 1948 KB (49%) | 18.2% |
| flex/deep_auto/1000 | 781 | 771 (99%) | 771 / 771 | 4 (1%) | 4.97 / 5 / 5 / 5 | 5.96 / 6 / 6 / 6 | 0 / 0 | 307 KB | 312 KB | 360 KB | 216 KB | -53 KB (-17%) | -6.4% |
| flex/deep_auto/10000 | 8205 | 8195 (100%) | 8195 / 8195 | 4 (0%) | 5.00 / 5 / 5 / 5 | 6.00 / 6 / 6 / 6 | 0 / 0 | 3265 KB | 3328 KB | 3840 KB | 2304 KB | -575 KB (-18%) | -6.6% |
| flex/deep_random/1000 | 781 | 771 (99%) | 771 / 771 | 4 (1%) | 1.26 / 1 / 2 / 2 | 1.26 / 1 / 2 / 2 | 0 / 0 | 307 KB | 312 KB | 145 KB | 127 KB | 163 KB (53%) | 19.6% |
| flex/deep_random/10000 | 8205 | 8195 (100%) | 8195 / 8195 | 4 (0%) | 1.26 / 1 / 2 / 2 | 1.26 / 1 / 2 / 2 | 0 / 0 | 3265 KB | 3328 KB | 1537 KB | 1348 KB | 1729 KB (53%) | 19.7% |
| flex/huge_nested/1000 | 925 | 915 (99%) | 915 / 915 | 4 (0%) | 1.00 / 1 / 1 / 1 | 1.00 / 1 / 1 / 1 | 0 / 0 | 365 KB | 371 KB | 172 KB | 143 KB | 193 KB (53%) | 19.7% |
| flex/huge_nested/10000 | 9125 | 9115 (100%) | 9115 / 9115 | 4 (0%) | 1.00 / 1 / 1 / 1 | 1.00 / 1 / 1 / 1 | 0 / 0 | 3632 KB | 3702 KB | 1709 KB | 1424 KB | 1923 KB (53%) | 19.7% |
| flex/superdeep/100 | 315 | 305 (97%) | 305 / 305 | 4 (1%) | 4.92 / 5 / 5 / 5 | 6.52 / 8 / 8 / 8 | 0 / 0 | 122 KB | 123 KB | 142 KB | 85 KB | -20 KB (-16%) | -6.1% |
| flex/superdeep/50 | 165 | 155 (94%) | 155 / 155 | 4 (3%) | 4.85 / 5 / 5 / 5 | 6.39 / 8 / 8 / 8 | 0 / 0 | 62 KB | 62 KB | 71 KB | 43 KB | -9 KB (-15%) | -5.6% |
| flex/wide/1000 | 1014 | 1004 (99%) | 1004 / 1004 | 4 (0%) | 1.49 / 1 / 2 / 5 | 1.56 / 1 / 2 / 7 | 0 / 0 | 400 KB | 407 KB | 209 KB | 172 KB | 191 KB (48%) | 17.8% |
| flex/wide/10000 | 10015 | 10005 (100%) | 10005 / 10005 | 4 (0%) | 1.51 / 1 / 2 / 5 | 1.60 / 1 / 2 / 7 | 0 / 0 | 3986 KB | 4063 KB | 2128 KB | 1724 KB | 1858 KB (47%) | 17.3% |
| grid/deep/2x2x5 | 1379 | 1369 (99%) | 1369 / 1369 | 1046 (76%) | 0.82 / 0 / 4 / 8 | 0.85 / 0 / 4 / 9 | 0 / 4 | 545 KB | 262 KB | 320 KB | 206 KB | 226 KB (41%) | 15.4% |
| grid/deep/3x3x4 | 7395 | 7385 (100%) | 7385 / 7385 | 6585 (89%) | 0.41 / 0 / 1 / 8 | 0.42 / 0 / 1 / 9 | 0 / 30 | 2942 KB | 1148 KB | 1544 KB | 1017 KB | 1399 KB (48%) | 17.7% |
| grid/superdeep/100 | 115 | 105 (91%) | 105 / 105 | 10 (10%) | 3.10 / 4 / 5 / 6 | 3.13 / 4 / 5 / 7 | 0 / 0 | 42 KB | 40 KB | 38 KB | 23 KB | 4 KB (9%) | 3.4% |
| grid/wide/100x100 | 10015 | 10005 (100%) | 10005 / 10005 | 251 (3%) | 3.77 / 4 / 6 / 7 | 4.13 / 5 / 7 / 9 | 0 / 588 | 3986 KB | 3994 KB | 3840 KB | 2429 KB | 146 KB (4%) | 1.4% |
| grid/wide/31x31 | 976 | 966 (99%) | 966 / 966 | 32 (3%) | 3.73 / 4 / 6 / 7 | 4.95 / 6 / 8 / 9 | 0 / 180 | 385 KB | 383 KB | 363 KB | 233 KB | 22 KB (6%) | 2.1% |
| text/flex_cards/100 | 516 | 305 (59%) | 305 / 305 | 5 (2%) | 1.97 / 2 / 2 / 2 | 3.21 / 3 / 4 / 4 | 0 / 0 | 122 KB | 122 KB | 57 KB | 57 KB | 64 KB (53%) | 17.5% |
| text/flex_cards/1000 | 5016 | 3005 (60%) | 3005 / 3005 | 5 (0%) | 2.00 / 2 / 2 / 2 | 3.26 / 3 / 4 / 4 | 0 / 0 | 1197 KB | 1219 KB | 563 KB | 563 KB | 634 KB (53%) | 17.6% |
| text/inline_mixed/100 | 4046 | 105 (3%) | 105 / 105 | 105 (100%) | 0.00 / 0 / 0 / 0 | 0.00 / 0 / 0 / 0 | 0 / 0 | 42 KB | 13 KB | 20 KB | 13 KB | 22 KB (53%) | 1.8% |
| text/inline_mixed/1000 | 41192 | 1005 (2%) | 1005 / 1005 | 1005 (100%) | 0.00 / 0 / 0 / 0 | 0.00 / 0 / 0 / 0 | 0 / 0 | 400 KB | 126 KB | 188 KB | 126 KB | 212 KB (53%) | 1.7% |
| text/paragraphs/100 | 216 | 105 (49%) | 105 / 105 | 105 (100%) | 0.00 / 0 / 0 / 0 | 0.00 / 0 / 0 / 0 | 0 / 0 | 42 KB | 13 KB | 20 KB | 13 KB | 22 KB (53%) | 16.5% |
| text/paragraphs/1000 | 2016 | 1005 (50%) | 1005 / 1005 | 1005 (100%) | 0.00 / 0 / 0 / 0 | 0.00 / 0 / 0 / 0 | 0 / 0 | 400 KB | 126 KB | 188 KB | 126 KB | 212 KB (53%) | 16.7% |

### Denominators (initial layout)

| page | DOM nodes | elements | cache owners (`LayoutData` allocated) | owners with no entry at all | owners with final entry only | owners with ≥1 measure entry |
|---|---:|---:|---:|---:|---:|---:|
| real/bootstrap-dashboard | 608 | 229 | 178 (29%) | 0 | 14 | 164 |
| real/css-flexbox-1 | 38735 | 17731 | 7564 (20%) | 24 | 2667 | 4873 |
| real/dioxuslabs-com | 232 | 179 | 145 (62%) | 0 | 22 | 123 |
| real/mdn | 4804 | 2440 | 1434 (30%) | 0 | 157 | 1277 |
| real/rustdoc | 39944 | 16965 | 7981 (20%) | 1 | 1597 | 6383 |
| real/servo-org | 673 | 261 | 187 (28%) | 0 | 15 | 172 |
| real/wikipedia | 47065 | 23971 | 3974 (8%) | 0 | 496 | 3478 |
| pangui/expand_with_max_constraint | 3015 | 3008 | 3005 (100%) | 0 | 4 | 3001 |
| pangui/expand_with_min_constraint | 3015 | 3008 | 3005 (100%) | 0 | 4 | 3001 |
| pangui/fit_nesting | 101125 | 101118 | 101115 (100%) | 0 | 100004 | 1111 |
| pangui/flex_expand_equal_weights | 15015 | 15008 | 15005 (100%) | 0 | 15005 | 0 |
| pangui/flex_expand_weights | 15015 | 15008 | 15005 (100%) | 0 | 5 | 15000 |
| pangui/nested_vertical_stack | 10015 | 10008 | 10005 (100%) | 0 | 4 | 10001 |
| pangui/padding_and_margin | 115 | 108 | 105 (91%) | 0 | 4 | 101 |
| pangui/percentage_and_ratio | 10015 | 10008 | 10005 (100%) | 0 | 5 | 10000 |
| pangui/perpendicular_expand_with_wrap | 12015 | 12008 | 12005 (100%) | 0 | 4 | 12001 |
| pangui/pixels_with_min_expand_constraint | 30015 | 30008 | 30005 (100%) | 0 | 4 | 30001 |
| pangui/wide_no_wrap_simple_few | 1015 | 1008 | 1005 (99%) | 0 | 5 | 1000 |
| pangui/wide_no_wrap_simple_many | 100015 | 100008 | 100005 (100%) | 0 | 5 | 100000 |
| pangui/wide_wrapping | 10015 | 10008 | 10005 (100%) | 0 | 4 | 10001 |
| flex/absolute/1000 | 1017 | 1010 | 1007 (99%) | 0 | 556 | 451 |
| flex/absolute/10000 | 10018 | 10011 | 10008 (100%) | 0 | 5485 | 4523 |
| flex/deep_auto/1000 | 781 | 774 | 771 (99%) | 0 | 4 | 767 |
| flex/deep_auto/10000 | 8205 | 8198 | 8195 (100%) | 0 | 4 | 8191 |
| flex/deep_random/1000 | 781 | 774 | 771 (99%) | 0 | 4 | 767 |
| flex/deep_random/10000 | 8205 | 8198 | 8195 (100%) | 0 | 4 | 8191 |
| flex/huge_nested/1000 | 925 | 918 | 915 (99%) | 0 | 4 | 911 |
| flex/huge_nested/10000 | 9125 | 9118 | 9115 (100%) | 0 | 4 | 9111 |
| flex/superdeep/100 | 315 | 308 | 305 (97%) | 0 | 4 | 301 |
| flex/superdeep/50 | 165 | 158 | 155 (94%) | 0 | 4 | 151 |
| flex/wide/1000 | 1014 | 1007 | 1004 (99%) | 0 | 4 | 1000 |
| flex/wide/10000 | 10015 | 10008 | 10005 (100%) | 0 | 4 | 10001 |
| grid/deep/2x2x5 | 1379 | 1372 | 1369 (99%) | 0 | 1046 | 323 |
| grid/deep/3x3x4 | 7395 | 7388 | 7385 (100%) | 0 | 6585 | 800 |
| grid/superdeep/100 | 115 | 108 | 105 (91%) | 0 | 10 | 95 |
| grid/wide/100x100 | 10015 | 10008 | 10005 (100%) | 0 | 251 | 9754 |
| grid/wide/31x31 | 976 | 969 | 966 (99%) | 0 | 32 | 934 |
| text/flex_cards/100 | 516 | 308 | 305 (59%) | 0 | 5 | 300 |
| text/flex_cards/1000 | 5016 | 3008 | 3005 (60%) | 0 | 5 | 3000 |
| text/inline_mixed/100 | 4046 | 1606 | 105 (3%) | 0 | 105 | 0 |
| text/inline_mixed/1000 | 41192 | 16368 | 1005 (2%) | 0 | 1005 | 0 |
| text/paragraphs/100 | 216 | 108 | 105 (49%) | 0 | 105 | 0 |
| text/paragraphs/1000 | 2016 | 1008 | 1005 (50%) | 0 | 1005 | 0 |

## Memory under each cache layout

Bytes per page after the initial layout (last column: C2 at the peak relayout snapshot). Inline part of every lazy layout = 112 B final entry + 8 B pointer/len + 8 B bookkeeping = 128 B
(the final entry stays inline because every owner has one). Heap arrays are 9 × 32 = 288 B; D counts exactly the populated entries.
Not modelled: mimalloc rounds 288 B to its 320 B class and 648 B `LayoutData` to 768 B, so shrinking `LayoutData` by 280–288 B (B/C1) drops it
into the 384 B class — the real saving per owner is then ~384 B rather than the 280 B modelled here, which favours the lazy schemes slightly.

- A `Option<Box<Cache>>`, allocated on the first store.
- B final entry inline, `Option<Box<[Option<CacheEntry<Size<f32>>>; 9]>>` allocated on the first measure store.
- C*n* final entry inline, *n* inline measure slots, spill to a boxed 9-slot array when an (*n*+1)th distinct key is stored.
- D final entry inline, heap array exactly as large as the populated entries (lower bound; ignores growth and allocator overhead).

| page | cache owners | today (eager) | A: box whole `Cache` | B: final inline + boxed 9-slot array | C1: 1 inline slot + spill | C2: 2 inline + spill | C3: 3 inline + spill | D: exact | C2 at peak relayout snapshot | cache share of node memory today |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| real/bootstrap-dashboard | 178 | 71 KB | 72 KB (-2%) | 68 KB (+4%) | 70 KB (+2%) | 72 KB (-1%) | 77 KB (-9%) | 46 KB (+35%) | 75 KB (-6%) | 25% |
| real/css-flexbox-1 | 7564 | 3014 KB | 3063 KB (-2%) | 2316 KB (+23%) | 2542 KB (+16%) | 2776 KB (+8%) | 3008 KB (+0%) | 1655 KB (+45%) | 2776 KB (+8%) | 18% |
| real/dioxuslabs-com | 145 | 58 KB | 59 KB (-2%) | 53 KB (+9%) | 50 KB (+14%) | 47 KB (+18%) | 42 KB (+28%) | 32 KB (+45%) | 49 KB (+14%) | 32% |
| real/mdn | 1434 | 571 KB | 583 KB (-2%) | 538 KB (+6%) | 297 KB (+48%) | 338 KB (+41%) | 347 KB (+39%) | 245 KB (+57%) | 341 KB (+40%) | 24% |
| real/rustdoc | 7981 | 3180 KB | 3242 KB (-2%) | 2793 KB (+12%) | 2709 KB (+15%) | 1604 KB (+50%) | 1746 KB (+45%) | 1372 KB (+57%) | 2958 KB (+7%) | 19% |
| real/servo-org | 187 | 75 KB | 76 KB (-2%) | 72 KB (+4%) | 55 KB (+26%) | 40 KB (+47%) | 43 KB (+43%) | 32 KB (+56%) | 48 KB (+36%) | 24% |
| real/wikipedia | 3974 | 1583 KB | 1614 KB (-2%) | 1475 KB (+7%) | 1088 KB (+31%) | 1179 KB (+26%) | 1128 KB (+29%) | 763 KB (+52%) | 1179 KB (+26%) | 9% |
| pangui/expand_with_max_constraint | 3005 | 1197 KB | 1221 KB (-2%) | 1220 KB (-2%) | 751 KB (+37%) | 845 KB (+29%) | 657 KB (+45%) | 532 KB (+56%) | 845 KB (+29%) | 37% |
| pangui/expand_with_min_constraint | 3005 | 1197 KB | 1221 KB (-2%) | 1220 KB (-2%) | 751 KB (+37%) | 845 KB (+29%) | 657 KB (+45%) | 532 KB (+56%) | 845 KB (+29%) | 37% |
| pangui/fit_nesting | 101115 | 39.3 MB | 40.1 MB (-2%) | 12.6 MB (+68%) | 15.7 MB (+60%) | 18.5 MB (+53%) | 21.6 MB (+45%) | 12.4 MB (+68%) | 18.8 MB (+52%) | 37% |
| pangui/flex_expand_equal_weights | 15005 | 5979 KB | 6096 KB (-2%) | 1876 KB (+69%) | 2345 KB (+61%) | 2813 KB (+53%) | 3282 KB (+45%) | 1876 KB (+69%) | 2813 KB (+53%) | 37% |
| pangui/flex_expand_weights | 15005 | 5979 KB | 6096 KB (-2%) | 6094 KB (-2%) | 2345 KB (+61%) | 2813 KB (+53%) | 3282 KB (+45%) | 2344 KB (+61%) | 2813 KB (+53%) | 37% |
| pangui/nested_vertical_stack | 10005 | 3986 KB | 4065 KB (-2%) | 4063 KB (-2%) | 1563 KB (+61%) | 1876 KB (+53%) | 2189 KB (+45%) | 1563 KB (+61%) | 1876 KB (+53%) | 37% |
| pangui/padding_and_margin | 105 | 42 KB | 43 KB (-2%) | 42 KB (+1%) | 16 KB (+61%) | 20 KB (+53%) | 23 KB (+45%) | 16 KB (+61%) | 20 KB (+53%) | 36% |
| pangui/percentage_and_ratio | 10005 | 3986 KB | 4065 KB (-2%) | 4063 KB (-2%) | 1563 KB (+61%) | 1876 KB (+53%) | 2189 KB (+45%) | 1563 KB (+61%) | 1876 KB (+53%) | 37% |
| pangui/perpendicular_expand_with_wrap | 12005 | 4783 KB | 4877 KB (-2%) | 4876 KB (-2%) | 3563 KB (+26%) | 3938 KB (+18%) | 4314 KB (+10%) | 2438 KB (+49%) | 3938 KB (+18%) | 37% |
| pangui/pixels_with_min_expand_constraint | 30005 | 11.7 MB | 11.9 MB (-2%) | 11.9 MB (-2%) | 7501 KB (+37%) | 8438 KB (+29%) | 6564 KB (+45%) | 5313 KB (+56%) | 8438 KB (+29%) | 37% |
| pangui/wide_no_wrap_simple_few | 1005 | 400 KB | 408 KB (-2%) | 407 KB (-2%) | 157 KB (+61%) | 188 KB (+53%) | 220 KB (+45%) | 157 KB (+61%) | 188 KB (+53%) | 37% |
| pangui/wide_no_wrap_simple_many | 100005 | 38.9 MB | 39.7 MB (-2%) | 39.7 MB (-2%) | 15.3 MB (+61%) | 18.3 MB (+53%) | 21.4 MB (+45%) | 15.3 MB (+61%) | 18.3 MB (+53%) | 37% |
| pangui/wide_wrapping | 10005 | 3986 KB | 4065 KB (-2%) | 4063 KB (-2%) | 1563 KB (+61%) | 1876 KB (+53%) | 2189 KB (+45%) | 1563 KB (+61%) | 1876 KB (+53%) | 37% |
| flex/absolute/1000 | 1007 | 401 KB | 409 KB (-2%) | 253 KB (+37%) | 198 KB (+51%) | 202 KB (+50%) | 226 KB (+44%) | 147 KB (+63%) | 202 KB (+50%) | 37% |
| flex/absolute/10000 | 10008 | 3988 KB | 4066 KB (-2%) | 2523 KB (+37%) | 1981 KB (+50%) | 2039 KB (+49%) | 2260 KB (+43%) | 1469 KB (+63%) | 2039 KB (+49%) | 37% |
| flex/deep_auto/1000 | 771 | 307 KB | 313 KB (-2%) | 312 KB (-2%) | 336 KB (-9%) | 360 KB (-17%) | 384 KB (-25%) | 216 KB (+30%) | 360 KB (-17%) | 37% |
| flex/deep_auto/10000 | 8195 | 3265 KB | 3329 KB (-2%) | 3328 KB (-2%) | 3584 KB (-10%) | 3840 KB (-18%) | 4096 KB (-25%) | 2304 KB (+29%) | 3840 KB (-18%) | 37% |
| flex/deep_random/1000 | 771 | 307 KB | 313 KB (-2%) | 312 KB (-2%) | 178 KB (+42%) | 145 KB (+53%) | 169 KB (+45%) | 127 KB (+59%) | 145 KB (+53%) | 37% |
| flex/deep_random/10000 | 8195 | 3265 KB | 3329 KB (-2%) | 3328 KB (-2%) | 1885 KB (+42%) | 1537 KB (+53%) | 1793 KB (+45%) | 1348 KB (+59%) | 1537 KB (+53%) | 37% |
| flex/huge_nested/1000 | 915 | 365 KB | 372 KB (-2%) | 371 KB (-2%) | 143 KB (+61%) | 172 KB (+53%) | 200 KB (+45%) | 143 KB (+61%) | 172 KB (+53%) | 37% |
| flex/huge_nested/10000 | 9115 | 3632 KB | 3703 KB (-2%) | 3702 KB (-2%) | 1424 KB (+61%) | 1709 KB (+53%) | 1994 KB (+45%) | 1424 KB (+61%) | 1709 KB (+53%) | 37% |
| flex/superdeep/100 | 305 | 122 KB | 124 KB (-2%) | 123 KB (-1%) | 132 KB (-9%) | 142 KB (-16%) | 151 KB (-24%) | 85 KB (+30%) | 142 KB (-16%) | 37% |
| flex/superdeep/50 | 155 | 62 KB | 63 KB (-2%) | 62 KB (-0%) | 66 KB (-8%) | 71 KB (-15%) | 76 KB (-23%) | 43 KB (+31%) | 71 KB (-15%) | 37% |
| flex/wide/1000 | 1004 | 400 KB | 408 KB (-2%) | 407 KB (-2%) | 264 KB (+34%) | 209 KB (+48%) | 227 KB (+43%) | 172 KB (+57%) | 209 KB (+48%) | 37% |
| flex/wide/10000 | 10005 | 3986 KB | 4065 KB (-2%) | 4063 KB (-2%) | 2621 KB (+34%) | 2128 KB (+47%) | 2275 KB (+43%) | 1724 KB (+57%) | 2128 KB (+47%) | 37% |
| grid/deep/2x2x5 | 1369 | 545 KB | 556 KB (-2%) | 262 KB (+52%) | 294 KB (+46%) | 320 KB (+41%) | 352 KB (+36%) | 206 KB (+62%) | 320 KB (+41%) | 37% |
| grid/deep/3x3x4 | 7385 | 2942 KB | 3000 KB (-2%) | 1148 KB (+61%) | 1356 KB (+54%) | 1544 KB (+48%) | 1754 KB (+40%) | 1017 KB (+65%) | 1544 KB (+48%) | 37% |
| grid/superdeep/100 | 105 | 42 KB | 43 KB (-2%) | 40 KB (+5%) | 41 KB (+3%) | 38 KB (+9%) | 38 KB (+8%) | 23 KB (+44%) | 38 KB (+9%) | 36% |
| grid/wide/100x100 | 10005 | 3986 KB | 4065 KB (-2%) | 3994 KB (-0%) | 4089 KB (-3%) | 3840 KB (+4%) | 3972 KB (+0%) | 2429 KB (+39%) | 3850 KB (+3%) | 37% |
| grid/wide/31x31 | 966 | 385 KB | 392 KB (-2%) | 383 KB (+0%) | 390 KB (-1%) | 363 KB (+6%) | 379 KB (+2%) | 233 KB (+39%) | 363 KB (+6%) | 37% |
| text/flex_cards/100 | 305 | 122 KB | 124 KB (-2%) | 122 KB (-1%) | 132 KB (-9%) | 57 KB (+53%) | 67 KB (+45%) | 57 KB (+53%) | 142 KB (-16%) | 33% |
| text/flex_cards/1000 | 3005 | 1197 KB | 1221 KB (-2%) | 1219 KB (-2%) | 1313 KB (-10%) | 563 KB (+53%) | 657 KB (+45%) | 563 KB (+53%) | 1407 KB (-18%) | 33% |
| text/inline_mixed/100 | 105 | 42 KB | 43 KB (-2%) | 13 KB (+69%) | 16 KB (+61%) | 20 KB (+53%) | 23 KB (+45%) | 13 KB (+69%) | 20 KB (+53%) | 3% |
| text/inline_mixed/1000 | 1005 | 400 KB | 408 KB (-2%) | 126 KB (+69%) | 157 KB (+61%) | 188 KB (+53%) | 220 KB (+45%) | 126 KB (+69%) | 188 KB (+53%) | 3% |
| text/paragraphs/100 | 105 | 42 KB | 43 KB (-2%) | 13 KB (+69%) | 16 KB (+61%) | 20 KB (+53%) | 23 KB (+45%) | 13 KB (+69%) | 20 KB (+53%) | 31% |
| text/paragraphs/1000 | 1005 | 400 KB | 408 KB (-2%) | 126 KB (+69%) | 157 KB (+61%) | 188 KB (+53%) | 220 KB (+45%) | 126 KB (+69%) | 188 KB (+53%) | 32% |
| **all 43 pages** | 407544 | 158.6 MB | 161.7 MB (-2%) | 124.3 MB (+22%) | 79.5 MB (+50%) | 86.9 MB (+45%) | 95.2 MB (+40%) | 62.9 MB (+60%) | 89.5 MB (+44%) | 34% |

## Relayout steps

Populated measure slots over all owners after each `resolve()`, evictions (stores into a full 9-slot array) per step, and measure-cache hit
rates. Warm relayouts fill 1.1–2× the slots of the first layout (`root_width` re-measures everything under a new width, the old entries
stay); `leaf_all` restyles most of the tree, which clears most caches; `append` adds 10% clones. Mode-change clears, in-place updates
(`measure_updates`) and mode misses were 0 on every page and step. Final-layout hit rate in the initial layout is 0–17% (a few nodes are
laid out twice with the same inputs on real pages).

| page | populated measure slots: initial → root_width → leaf_1 → leaf_10pct → leaf_all → append | evictions per step (same order) | measure hit rate initial / relayout steps | uncacheable measure results (initial) |
|---|---|---|---:|---:|
| real/bootstrap-dashboard | 754 → 1021 → 1009 → 1142 → 494 → 1502 | 5 / 10 / 0 / 14 / 1 / 5 | 54% / 64% | 4 |
| real/css-flexbox-1 | 22711 → 25946 → 26019 → 34905 → 9756 → 23265 | 0 / 0 / 0 / 115 / 0 / 0 | 0% / 61% | 0 |
| real/dioxuslabs-com | 443 → 465 → 465 → 461 → 365 → 886 | 42 / 0 / 13 / 13 / 12 / 42 | 46% / 52% | 0 |
| real/mdn | 2089 → 2518 → 2514 → 2464 → 1767 → 2365 | 0 / 41 / 0 / 187 / 20 / 0 | 42% / 55% | 193 |
| real/rustdoc | 11968 → 17488 → 17478 → 16317 → 9445 → 29480 | 0 / 0 / 0 / 0 / 0 / 0 | 14% / 25% | 507 |
| real/servo-org | 292 → 392 → 387 → 366 → 251 → 319 | 0 / 0 / 0 / 0 / 0 / 0 | 36% / 51% | 3 |
| real/wikipedia | 8521 → 9794 → 10770 → 11460 → 6894 → 16881 | 6 / 30 / 16 / 116 / 8 / 0 | 34% / 48% | 412 |
| pangui/expand_with_max_constraint | 5001 → 6001 → 5999 → 5601 → 3001 → 5501 | 0 / 0 / 0 / 0 / 0 / 0 | 29% / 68% | 0 |
| pangui/expand_with_min_constraint | 5001 → 6001 → 5999 → 5601 → 3001 → 5501 | 0 / 0 / 0 / 0 / 0 / 0 | 29% / 68% | 0 |
| pangui/fit_nesting | 2221 → 4441 → 4435 → 2221 → 2221 → 2443 | 0 / 0 / 0 / 0 / 0 / 0 | 64% / 65% | 0 |
| pangui/flex_expand_equal_weights | 0 → 0 → 0 → 0 → 0 → 0 | 0 / 0 / 0 / 0 / 0 / 0 | - / - | 0 |
| pangui/flex_expand_weights | 15000 → 15000 → 14999 → 14000 → 5000 → 16500 | 0 / 0 / 0 / 0 / 0 / 0 | 0% / 73% | 0 |
| pangui/nested_vertical_stack | 10001 → 20001 → 20000 → 19001 → 10001 → 11001 | 0 / 0 / 0 / 0 / 0 / 0 | 50% / 78% | 0 |
| pangui/padding_and_margin | 101 → 201 → 200 → 191 → 101 → 111 | 0 / 0 / 0 / 0 / 0 / 0 | 50% / 78% | 0 |
| pangui/percentage_and_ratio | 10000 → 20000 → 19999 → 19000 → 10000 → 11000 | 0 / 0 / 0 / 0 / 0 / 0 | 0% / 57% | 0 |
| pangui/perpendicular_expand_with_wrap | 30001 → 48001 → 48001 → 48001 → 30001 → 45001 | 0 / 0 / 0 / 0 / 0 / 0 | 17% / 65% | 0 |
| pangui/pixels_with_min_expand_constraint | 50001 → 60001 → 60000 → 58001 → 50001 → 55001 | 0 / 0 / 0 / 0 / 0 / 0 | 55% / 75% | 0 |
| pangui/wide_no_wrap_simple_few | 1000 → 1000 → 1000 → 1000 → 1000 → 1100 | 0 / 0 / 0 / 0 / 0 / 0 | 0% / 76% | 0 |
| pangui/wide_no_wrap_simple_many | 100000 → 100000 → 100000 → 100000 → 100000 → 110000 | 0 / 0 / 0 / 0 / 0 / 0 | 0% / 76% | 0 |
| pangui/wide_wrapping | 10001 → 10001 → 10001 → 10001 → 10001 → 11001 | 0 / 0 / 0 / 0 / 0 / 0 | 50% / 88% | 0 |
| flex/absolute/1000 | 673 → 850 → 849 → 818 → 604 → 906 | 0 / 0 / 0 / 0 / 0 / 0 | 30% / 74% | 0 |
| flex/absolute/10000 | 6971 → 8900 → 8897 → 8532 → 6193 → 9616 | 0 / 0 / 0 / 0 / 0 / 0 | 28% / 73% | 0 |
| flex/deep_auto/1000 | 3831 → 4597 → 4594 → 4467 → 3319 → 5748 | 0 / 0 / 0 / 0 / 0 / 0 | 71% / 72% | 0 |
| flex/deep_auto/10000 | 40951 → 49141 → 49139 → 47502 → 32759 → 61428 | 0 / 0 / 0 / 0 / 0 / 0 | 71% / 72% | 0 |
| flex/deep_random/1000 | 972 → 972 → 972 → 965 → 901 → 1464 | 0 / 0 / 0 / 0 / 0 / 0 | 58% / 61% | 0 |
| flex/deep_random/10000 | 10342 → 10342 → 10341 → 10238 → 9244 → 15496 | 0 / 0 / 0 / 0 / 0 / 0 | 58% / 61% | 0 |
| flex/huge_nested/1000 | 911 → 911 → 911 → 911 → 911 → 1002 | 0 / 0 / 0 / 0 / 0 / 0 | 50% / 69% | 0 |
| flex/huge_nested/10000 | 9111 → 9111 → 9111 → 9111 → 9111 → 10022 | 0 / 0 / 0 / 0 / 0 / 0 | 50% / 67% | 0 |
| flex/superdeep/100 | 1501 → 1801 → 1899 → 1990 → 1099 → 1509 | 0 / 0 / 0 / 0 / 0 / 0 | 70% / 80% | 0 |
| flex/superdeep/50 | 751 → 901 → 949 → 990 → 549 → 759 | 0 / 0 / 0 / 0 / 0 / 0 | 70% / 80% | 0 |
| flex/wide/1000 | 1495 → 1553 → 1552 → 1566 → 1280 → 1707 | 0 / 0 / 0 / 0 / 0 / 0 | 57% / 82% | 0 |
| flex/wide/10000 | 15148 → 15858 → 15858 → 16011 → 13072 → 17287 | 0 / 0 / 0 / 0 / 0 / 0 | 57% / 82% | 0 |
| grid/deep/2x2x5 | 1126 → 1126 → 1126 → 1161 → 1126 → 1352 | 0 / 0 / 0 / 4 / 0 / 0 | 60% / 68% | 0 |
| grid/deep/3x3x4 | 3011 → 3109 → 3109 → 3056 → 3013 → 3628 | 0 / 3 / 0 / 10 / 0 / 17 | 64% / 70% | 0 |
| grid/superdeep/100 | 325 → 329 → 325 → 325 → 325 → 649 | 0 / 0 / 0 / 0 / 0 / 0 | 61% / 61% | 0 |
| grid/wide/100x100 | 37719 → 39684 → 40296 → 41292 → 17171 → 42329 | 0 / 0 / 196 / 392 / 0 / 0 | 33% / 89% | 0 |
| grid/wide/31x31 | 3603 → 3873 → 3916 → 4782 → 1396 → 4038 | 0 / 0 / 0 / 180 / 0 / 0 | 35% / 86% | 0 |
| text/flex_cards/100 | 600 → 900 → 904 → 980 → 400 → 663 | 0 / 0 / 0 / 0 / 0 / 0 | 0% / 40% | 0 |
| text/flex_cards/1000 | 6000 → 9000 → 9004 → 9800 → 4000 → 6603 | 0 / 0 / 0 / 0 / 0 / 0 | 0% / 40% | 0 |
| text/inline_mixed/100 | 0 → 0 → 0 → 0 → 0 → 0 | 0 / 0 / 0 / 0 / 0 / 0 | - / - | 0 |
| text/inline_mixed/1000 | 0 → 0 → 0 → 0 → 0 → 0 | 0 / 0 / 0 / 0 / 0 / 0 | - / - | 0 |
| text/paragraphs/100 | 0 → 0 → 0 → 0 → 0 → 0 | 0 / 0 / 0 / 0 / 0 / 0 | - / - | 0 |
| text/paragraphs/1000 | 0 → 0 → 0 → 0 → 0 → 0 | 0 / 0 / 0 / 0 / 0 / 0 | - / - | 0 |

## Which nodes fill the slots (initial layout, summed per suite)

Histogram of populated measure slots 0..9 by node kind (`inline_root` = block-level box whose content is inline, laid out by Parley;
`inline` = inline-level element inside such a box; `anon_block` = anonymous block wrapping inline content; `table_internal` = rows/cells).

| suite | kind | nodes | cache owners | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | mean |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| real | text | 70278 | 0 | | | | | | | | | | | |
| real | inline | 33512 | 94 | 80 | · | 13 | 1 | · | · | · | · | · | · | 0.31 |
| real | inline_root | 11875 | 11875 | 1554 | 1887 | 3208 | 464 | 1512 | 3212 | 9 | · | 8 | 21 | 2.70 |
| real | anon_block | 5109 | 1887 | 1324 | 287 | 167 | 87 | · | 1 | 13 | 3 | · | 5 | 0.55 |
| real | block | 5030 | 4977 | 1505 | 1495 | 1363 | 554 | 22 | 10 | 16 | 1 | · | 11 | 1.25 |
| real | table_internal | 1685 | 1100 | · | · | · | · | · | 1092 | · | 8 | · | · | 5.01 |
| real | contents | 1468 | 0 | | | | | | | | | | | |
| real | none | 1260 | 374 | 374 | · | · | · | · | · | · | · | · | · | 0.00 |
| real | flex | 825 | 825 | 16 | 422 | 307 | 24 | 20 | 7 | 19 | 1 | 7 | 2 | 1.72 |
| real | replaced | 159 | 138 | 10 | 72 | 7 | 23 | 1 | 21 | · | 3 | · | 1 | 2.13 |
| real | table | 104 | 104 | 52 | 12 | 1 | 39 | · | · | · | · | · | · | 1.26 |
| real | grid | 89 | 89 | 78 | 5 | 1 | 1 | 4 | · | · | · | · | · | 0.29 |
| pangui | flex | 310236 | 310236 | 115018 | 176108 | 1110 | 12000 | 6000 | · | · | · | · | · | 0.77 |
| flex | flex | 50410 | 50410 | 6045 | 26832 | 6531 | 991 | 265 | 9746 | · | · | · | · | 1.84 |
| grid | flex (items) | 18552 | 18552 | 7866 | 856 | 2200 | 695 | 2586 | 2901 | 1006 | 442 | · | · | 2.23 |
| grid | grid | 1263 | 1263 | 43 | 133 | 233 | 122 | 332 | 296 | 50 | 41 | 13 | · | 3.53 |
| text | text | 30590 | 0 | | | | | | | | | | | |
| text | inline | 16858 | 0 | | | | | | | | | | | |
| text | inline_root | 4400 | 4400 | 2200 | · | 2200 | · | · | · | · | · | · | · | 1.00 |
| text | block | 1122 | 1122 | 22 | · | 1100 | · | · | · | · | · | · | · | 1.96 |

(The 374 `display:none` and 94 inline owners on the real pages have a `LayoutData` with only the final entry: hidden elements get a
`PerformLayout` of `LayoutOutput::HIDDEN` stored, inline boxes are re-measured through `compute_child_layout` by the inline layout.)

## Appendix

- `histograms.md`: per page, counts of owners by populated measure slots (0..9) for the initial layout and the peak relayout snapshot.
- `histograms.csv`: the same per node kind and per step; `occupancy.csv`: every count and counter per page and step; `memory.csv`: the
  memory models; `raw/*.json`: the runner's output.
- Reproduce: `cache-occupancy/README.md`.
