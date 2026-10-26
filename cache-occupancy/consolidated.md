# Blitz Taffy cache occupancy — consolidated table (43 pages)

Blitz `1c5265a8b3985e1ec05044a115b2ec6266e3fa91`, Taffy `802e497b69689e1c93be2d16e9d53a973971bcb2`, `--features floats,writing-mode`.
Measured sizes: `Cache` 408 B (= `Option<CacheEntry<LayoutOutput>>` 112 B final entry + 9 × `Option<CacheEntry<Size<f32>>>` 32 B + 8 B
bookkeeping); `Node` 192 B; `ElementData` 256 B; `LayoutData` 648 B (holds the `Cache`; `Option<Box<LayoutData>>` on element/document nodes,
allocated on the first layout write — text/comment nodes never own one). Instrumented `--hash` = plain runner on all 43 pages. Counts
measured; bytes = size_of × counts (no allocator rounding).

Columns: **cache owners** = nodes with a `LayoutData` (% of DOM nodes); **final only** = owners with the final-layout entry and no measure
entry after the initial layout (% of owners; owners with *no* entry at all: 25 in the whole corpus, all anonymous blocks on css-flexbox-1/rustdoc);
**0..9** = owners by populated measure slots at the peak relayout snapshot (the most-populated of initial/root_width/leaf_1/leaf_10pct/leaf_all
over the original node set); **evictions** = stores into a full 9-slot array, initial layout / summed over the five relayout steps;
**cache KB today** = owners × 408 B; **lazy** = after the initial layout, C2 = final entry inline + 2 inline measure slots + boxed 9-slot
array when a 3rd key is stored, B = final inline + boxed 9-slot array on first measure store, D = exactly the populated entries;
**% node mem** = saving ÷ (nodes × 192 + elements × 256 + owners × 648).

| page | DOM nodes | cache owners | final only (init) | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | evictions init / Σ relayout | cache KB today | KB lazy C2 (B / D) | saving KB (C2) | % cache | % node mem |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| real/bootstrap-dashboard | 608 | 178 (29%) | 14 (8%) | 14 | 15 | 9 | 3 | 4 | 10 | 16 | 11 | 3 | 93 | 5 / 30 | 71 | 72 (68 / 46) | -1 | -1% | -0.3% |
| real/css-flexbox-1 | 38,735 | 7,564 (20%) | 2,667 (35%) | 2,692 | 28 | 450 | 9 | 7 | 334 | 41 | 207 | 3,607 | 189 | 0 / 115 | 3,014 | 2,776 (2,316 / 1,655) | 238 | +8% | +1.4% |
| real/dioxuslabs-com | 232 | 145 (62%) | 22 (15%) | 22 | 25 | 19 | 37 | 8 | 4 | 7 | 2 | 6 | 15 | 42 / 80 | 58 | 47 (53 / 32) | 10 | +18% | +5.7% |
| real/mdn | 4,804 | 1,434 (30%) | 157 (11%) | 157 | 749 | 272 | 123 | 18 | 39 | 19 | 17 | 4 | 36 | 0 / 248 | 571 | 338 (538 / 245) | 233 | +41% | +9.6% |
| real/rustdoc | 39,944 | 7,981 (20%) | 1,597 (20%) | 1,598 | 902 | 283 | 4,821 | 329 | 47 | 1 | 0 | 0 | 0 | 0 / 0 | 3,180 | 1,604 (2,793 / 1,372) | 1,576 | +50% | +9.4% |
| real/servo-org | 673 | 187 (28%) | 15 (8%) | 15 | 21 | 106 | 34 | 5 | 4 | 0 | 0 | 1 | 1 | 0 / 0 | 75 | 40 (72 / 32) | 35 | +47% | +11.3% |
| real/wikipedia | 47,065 | 3,974 (8%) | 496 (12%) | 501 | 975 | 974 | 149 | 117 | 807 | 38 | 169 | 20 | 224 | 6 / 170 | 1,583 | 1,179 (1,475 / 763) | 405 | +26% | +2.3% |
| pangui/expand_with_max_constraint | 3,015 | 3,005 (100%) | 4 (0%) | 4 | 2,001 | 0 | 0 | 1,000 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 1,197 | 845 (1,220 / 532) | 353 | +29% | +11.0% |
| pangui/expand_with_min_constraint | 3,015 | 3,005 (100%) | 4 (0%) | 4 | 2,001 | 0 | 0 | 1,000 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 1,197 | 845 (1,220 / 532) | 353 | +29% | +11.0% |
| pangui/fit_nesting | 101,125 | 101,115 (100%) | 100,004 (99%) | 100,004 | 1 | 0 | 0 | 1,110 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 40,288 | 18,959 (12,952 / 12,709) | 21,329 | +53% | +19.7% |
| pangui/flex_expand_equal_weights | 15,015 | 15,005 (100%) | 15,005 (100%) | 15,005 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 5,979 | 2,813 (1,876 / 1,876) | 3,165 | +53% | +19.7% |
| pangui/flex_expand_weights | 15,015 | 15,005 (100%) | 5 (0%) | 5 | 15,000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 5,979 | 2,813 (6,094 / 2,344) | 3,165 | +53% | +19.7% |
| pangui/nested_vertical_stack | 10,015 | 10,005 (100%) | 4 (0%) | 4 | 1 | 10,000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 3,986 | 1,876 (4,063 / 1,563) | 2,110 | +53% | +19.7% |
| pangui/padding_and_margin | 115 | 105 (91%) | 4 (4%) | 4 | 1 | 100 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 42 | 20 (42 / 16) | 22 | +53% | +19.3% |
| pangui/percentage_and_ratio | 10,015 | 10,005 (100%) | 5 (0%) | 5 | 0 | 10,000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 3,986 | 1,876 (4,063 / 1,563) | 2,110 | +53% | +19.7% |
| pangui/perpendicular_expand_with_wrap | 12,015 | 12,005 (100%) | 4 (0%) | 4 | 6,001 | 0 | 0 | 0 | 0 | 0 | 6,000 | 0 | 0 | 0 / 0 | 4,783 | 3,938 (4,876 / 2,438) | 845 | +18% | +6.6% |
| pangui/pixels_with_min_expand_constraint | 30,015 | 30,005 (100%) | 4 (0%) | 4 | 20,001 | 0 | 0 | 10,000 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 11,955 | 8,438 (12,188 / 5,313) | 3,517 | +29% | +10.9% |
| pangui/wide_no_wrap_simple_few | 1,015 | 1,005 (99%) | 5 (0%) | 5 | 1,000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 400 | 188 (407 / 157) | 212 | +53% | +19.7% |
| pangui/wide_no_wrap_simple_many | 100,015 | 100,005 (100%) | 5 (0%) | 5 | 100,000 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 39,846 | 18,751 (40,626 / 15,626) | 21,095 | +53% | +19.7% |
| pangui/wide_wrapping | 10,015 | 10,005 (100%) | 4 (0%) | 4 | 10,001 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 3,986 | 1,876 (4,063 / 1,563) | 2,110 | +53% | +19.7% |
| flex/absolute/1000 | 1,017 | 1,007 (99%) | 556 (55%) | 556 | 177 | 227 | 0 | 28 | 7 | 12 | 0 | 0 | 0 | 0 / 0 | 401 | 202 (253 / 147) | 199 | +50% | +18.4% |
| flex/absolute/10000 | 10,018 | 10,008 (100%) | 5,485 (55%) | 5,485 | 1,688 | 2,257 | 0 | 325 | 120 | 133 | 0 | 0 | 0 | 0 / 0 | 3,988 | 2,039 (2,523 / 1,469) | 1,948 | +49% | +18.2% |
| flex/deep_auto/1000 | 781 | 771 (99%) | 4 (1%) | 4 | 1 | 0 | 0 | 0 | 0 | 766 | 0 | 0 | 0 | 0 / 0 | 307 | 360 (312 / 216) | -53 | -17% | -6.4% |
| flex/deep_auto/10000 | 8,205 | 8,195 (100%) | 4 (0%) | 4 | 1 | 0 | 0 | 0 | 0 | 8,190 | 0 | 0 | 0 | 0 / 0 | 3,265 | 3,840 (3,328 / 2,304) | -575 | -18% | -6.6% |
| flex/deep_random/1000 | 781 | 771 (99%) | 4 (1%) | 4 | 562 | 205 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 307 | 145 (312 / 127) | 163 | +53% | +19.6% |
| flex/deep_random/10000 | 8,205 | 8,195 (100%) | 4 (0%) | 4 | 6,040 | 2,151 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 3,265 | 1,537 (3,328 / 1,348) | 1,729 | +53% | +19.7% |
| flex/huge_nested/1000 | 925 | 915 (99%) | 4 (0%) | 4 | 911 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 365 | 172 (371 / 143) | 193 | +53% | +19.7% |
| flex/huge_nested/10000 | 9,125 | 9,115 (100%) | 4 (0%) | 4 | 9,111 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 3,632 | 1,709 (3,702 / 1,424) | 1,923 | +53% | +19.7% |
| flex/superdeep/100 | 315 | 305 (97%) | 4 (1%) | 4 | 1 | 0 | 21 | 0 | 99 | 1 | 7 | 172 | 0 | 0 / 0 | 122 | 142 (123 / 85) | -20 | -16% | -6.1% |
| flex/superdeep/50 | 165 | 155 (94%) | 4 (3%) | 4 | 1 | 0 | 11 | 0 | 49 | 1 | 7 | 82 | 0 | 0 / 0 | 62 | 71 (62 / 43) | -9 | -15% | -5.6% |
| flex/wide/1000 | 1,014 | 1,004 (99%) | 4 (0%) | 4 | 633 | 294 | 19 | 10 | 24 | 12 | 8 | 0 | 0 | 0 / 0 | 400 | 209 (407 / 172) | 191 | +48% | +17.8% |
| flex/wide/10000 | 10,015 | 10,005 (100%) | 4 (0%) | 4 | 6,434 | 2,669 | 229 | 110 | 339 | 123 | 97 | 0 | 0 | 0 / 0 | 3,986 | 2,128 (4,063 / 1,724) | 1,858 | +47% | +17.3% |
| grid/deep/2x2x5 | 1,379 | 1,369 (99%) | 1,046 (76%) | 1,046 | 39 | 60 | 36 | 89 | 76 | 8 | 11 | 3 | 1 | 0 / 4 | 545 | 320 (262 / 206) | 226 | +41% | +15.4% |
| grid/deep/3x3x4 | 7,395 | 7,385 (100%) | 6,585 (89%) | 6,585 | 83 | 152 | 67 | 196 | 177 | 44 | 62 | 17 | 2 | 0 / 30 | 2,942 | 1,544 (1,148 / 1,017) | 1,399 | +48% | +17.7% |
| grid/superdeep/100 | 115 | 105 (91%) | 10 (10%) | 10 | 9 | 21 | 9 | 32 | 22 | 1 | 1 | 0 | 0 | 0 / 0 | 42 | 38 (40 / 23) | 4 | +9% | +3.4% |
| grid/wide/100x100 | 10,015 | 10,005 (100%) | 251 (3%) | 355 | 902 | 2,326 | 507 | 779 | 1,590 | 2,357 | 846 | 0 | 343 | 0 / 588 | 3,986 | 3,840 (3,994 / 2,429) | 146 | +4% | +1.4% |
| grid/wide/31x31 | 976 | 966 (99%) | 32 (3%) | 42 | 106 | 234 | 1 | 34 | 12 | 168 | 44 | 232 | 93 | 0 / 180 | 385 | 363 (383 / 233) | 22 | +6% | +2.1% |
| text/flex_cards/100 | 516 | 305 (59%) | 5 (2%) | 5 | 20 | 20 | 120 | 140 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 122 | 57 (122 / 57) | 64 | +53% | +17.5% |
| text/flex_cards/1000 | 5,016 | 3,005 (60%) | 5 (0%) | 5 | 200 | 200 | 1,200 | 1,400 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 1,197 | 563 (1,219 / 563) | 634 | +53% | +17.6% |
| text/inline_mixed/100 | 4,046 | 105 (3%) | 105 (100%) | 105 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 42 | 20 (13 / 13) | 22 | +53% | +1.8% |
| text/inline_mixed/1000 | 41,192 | 1,005 (2%) | 1,005 (100%) | 1,005 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 400 | 188 (126 / 126) | 212 | +53% | +1.7% |
| text/paragraphs/100 | 216 | 105 (49%) | 105 (100%) | 105 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 42 | 20 (13 / 13) | 22 | +53% | +16.5% |
| text/paragraphs/1000 | 2,016 | 1,005 (50%) | 1,005 (100%) | 1,005 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 400 | 188 (126 / 126) | 212 | +53% | +16.7% |
| **all 43** | 565,914 | 407,544 (72%) | 136,260 (33%) | 136,405 | 185,642 | 33,029 | 7,396 | 16,741 | 3,760 | 11,938 | 7,489 | 4,147 | 997 | 53 / 1445 | 162,381 | 88,989 (127,235 / 64,385) | 73,392 | +45% | +15.3% |

**Where the 9-full nodes come from.** After the initial layout only 40 nodes in the corpus have all 9 slots filled, all on real pages
(mdn 16, dioxuslabs-com 15, wikipedia 6, bootstrap-dashboard 3: inline roots, block containers and a few flex items/anonymous blocks
inside tables and grids), and evictions in the initial layout are 0 on 40 pages (wikipedia 6, dioxuslabs-com 42, bootstrap-dashboard 5).
At the relayout peak 997 nodes are 9-full: 439 flex items that are grid children on `grid/wide/100x100` (343) and `31x31` (93), 391 table
cells/rows (wikipedia 216, css-flexbox-1 98, bootstrap-dashboard 77), 133 inline roots (css-flexbox-1 91, mdn 29) and 23 blocks — i.e.
nodes under grid and table layout, which measure each child under several track/column constraints, re-measured a second time under
`root_width`'s other width; those old-width entries are dead once the width is reverted, so the slot count is not a working-set limit
on any page here.
