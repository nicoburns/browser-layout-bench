# Populated measure slots per node (counts)

Nodes that own a Taffy `Cache` (have a `LayoutData`), by number of populated measure entries (0..9). `final` = how many of them also have the final-layout entry populated. `initial` = after the first layout; `peak` = the relayout snapshot with the most populated slots (`root_width`, `leaf_1`, `leaf_10pct` or `leaf_all`; `append` excluded as it adds nodes). Nodes without a `LayoutData` (text, most inline elements, `display:contents`) have no cache and are not counted. Measured at Blitz 1c5265a / Taffy 802e497.

| page | snapshot | owners | final | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| real/bootstrap-dashboard | initial | 178 | 178 | 14 | 15 | 12 | · | 18 | 86 | 24 | 6 | · | 3 |
| real/bootstrap-dashboard | peak (leaf_10pct) | 178 | 178 | 14 | 15 | 9 | 3 | 4 | 10 | 16 | 11 | 3 | 93 |
| real/css-flexbox-1 | initial | 7564 | 7540 | 2691 | 37 | 8 | 16 | 1450 | 3362 | · | · | · | · |
| real/css-flexbox-1 | peak (leaf_10pct) | 7564 | 7540 | 2692 | 28 | 450 | 9 | 7 | 334 | 41 | 207 | 3607 | 189 |
| real/dioxuslabs-com | initial | 145 | 145 | 22 | 26 | 25 | 37 | 5 | 3 | 4 | 2 | 6 | 15 |
| real/dioxuslabs-com | peak (root_width) | 145 | 145 | 22 | 25 | 19 | 37 | 8 | 4 | 7 | 2 | 6 | 15 |
| real/mdn | initial | 1434 | 1434 | 157 | 1017 | 14 | 128 | 11 | 74 | 17 | · | · | 16 |
| real/mdn | peak (root_width) | 1434 | 1434 | 157 | 749 | 272 | 123 | 18 | 39 | 19 | 17 | 4 | 36 |
| real/rustdoc | initial | 7981 | 7980 | 1598 | 1185 | 4815 | 381 | 1 | · | 1 | · | · | · |
| real/rustdoc | peak (root_width) | 7981 | 7980 | 1598 | 902 | 283 | 4821 | 329 | 47 | 1 | · | · | · |
| real/servo-org | initial | 187 | 187 | 15 | 81 | 75 | 10 | · | 5 | 1 | · | · | · |
| real/servo-org | peak (root_width) | 187 | 187 | 15 | 21 | 106 | 34 | 5 | 4 | · | · | 1 | 1 |
| real/wikipedia | initial | 3974 | 3974 | 496 | 1819 | 118 | 621 | 74 | 813 | 10 | 8 | 9 | 6 |
| real/wikipedia | peak (leaf_10pct) | 3974 | 3974 | 501 | 975 | 974 | 149 | 117 | 807 | 38 | 169 | 20 | 224 |
| pangui/expand_with_max_constraint | initial | 3005 | 3005 | 4 | 2001 | · | 1000 | · | · | · | · | · | · |
| pangui/expand_with_max_constraint | peak (root_width) | 3005 | 3005 | 4 | 2001 | · | · | 1000 | · | · | · | · | · |
| pangui/expand_with_min_constraint | initial | 3005 | 3005 | 4 | 2001 | · | 1000 | · | · | · | · | · | · |
| pangui/expand_with_min_constraint | peak (root_width) | 3005 | 3005 | 4 | 2001 | · | · | 1000 | · | · | · | · | · |
| pangui/fit_nesting | initial | 101115 | 101115 | 100004 | 1 | 1110 | · | · | · | · | · | · | · |
| pangui/fit_nesting | peak (root_width) | 101115 | 101115 | 100004 | 1 | · | · | 1110 | · | · | · | · | · |
| pangui/flex_expand_equal_weights | initial | 15005 | 15005 | 15005 | · | · | · | · | · | · | · | · | · |
| pangui/flex_expand_equal_weights | peak (initial) | 15005 | 15005 | 15005 | · | · | · | · | · | · | · | · | · |
| pangui/flex_expand_weights | initial | 15005 | 15005 | 5 | 15000 | · | · | · | · | · | · | · | · |
| pangui/flex_expand_weights | peak (initial) | 15005 | 15005 | 5 | 15000 | · | · | · | · | · | · | · | · |
| pangui/nested_vertical_stack | initial | 10005 | 10005 | 4 | 10001 | · | · | · | · | · | · | · | · |
| pangui/nested_vertical_stack | peak (root_width) | 10005 | 10005 | 4 | 1 | 10000 | · | · | · | · | · | · | · |
| pangui/padding_and_margin | initial | 105 | 105 | 4 | 101 | · | · | · | · | · | · | · | · |
| pangui/padding_and_margin | peak (root_width) | 105 | 105 | 4 | 1 | 100 | · | · | · | · | · | · | · |
| pangui/percentage_and_ratio | initial | 10005 | 10005 | 5 | 10000 | · | · | · | · | · | · | · | · |
| pangui/percentage_and_ratio | peak (root_width) | 10005 | 10005 | 5 | · | 10000 | · | · | · | · | · | · | · |
| pangui/perpendicular_expand_with_wrap | initial | 12005 | 12005 | 4 | 6001 | · | · | 6000 | · | · | · | · | · |
| pangui/perpendicular_expand_with_wrap | peak (root_width) | 12005 | 12005 | 4 | 6001 | · | · | · | · | · | 6000 | · | · |
| pangui/pixels_with_min_expand_constraint | initial | 30005 | 30005 | 4 | 20001 | · | 10000 | · | · | · | · | · | · |
| pangui/pixels_with_min_expand_constraint | peak (root_width) | 30005 | 30005 | 4 | 20001 | · | · | 10000 | · | · | · | · | · |
| pangui/wide_no_wrap_simple_few | initial | 1005 | 1005 | 5 | 1000 | · | · | · | · | · | · | · | · |
| pangui/wide_no_wrap_simple_few | peak (initial) | 1005 | 1005 | 5 | 1000 | · | · | · | · | · | · | · | · |
| pangui/wide_no_wrap_simple_many | initial | 100005 | 100005 | 5 | 100000 | · | · | · | · | · | · | · | · |
| pangui/wide_no_wrap_simple_many | peak (initial) | 100005 | 100005 | 5 | 100000 | · | · | · | · | · | · | · | · |
| pangui/wide_wrapping | initial | 10005 | 10005 | 4 | 10001 | · | · | · | · | · | · | · | · |
| pangui/wide_wrapping | peak (initial) | 10005 | 10005 | 4 | 10001 | · | · | · | · | · | · | · | · |
| flex/absolute/1000 | initial | 1007 | 1007 | 556 | 307 | 97 | 28 | 7 | 12 | · | · | · | · |
| flex/absolute/1000 | peak (root_width) | 1007 | 1007 | 556 | 177 | 227 | · | 28 | 7 | 12 | · | · | · |
| flex/absolute/10000 | initial | 10008 | 10008 | 5485 | 3039 | 906 | 325 | 120 | 133 | · | · | · | · |
| flex/absolute/10000 | peak (root_width) | 10008 | 10008 | 5485 | 1688 | 2257 | · | 325 | 120 | 133 | · | · | · |
| flex/deep_auto/1000 | initial | 771 | 771 | 4 | 1 | · | · | · | 766 | · | · | · | · |
| flex/deep_auto/1000 | peak (root_width) | 771 | 771 | 4 | 1 | · | · | · | · | 766 | · | · | · |
| flex/deep_auto/10000 | initial | 8195 | 8195 | 4 | 1 | · | · | · | 8190 | · | · | · | · |
| flex/deep_auto/10000 | peak (root_width) | 8195 | 8195 | 4 | 1 | · | · | · | · | 8190 | · | · | · |
| flex/deep_random/1000 | initial | 771 | 771 | 4 | 562 | 205 | · | · | · | · | · | · | · |
| flex/deep_random/1000 | peak (initial) | 771 | 771 | 4 | 562 | 205 | · | · | · | · | · | · | · |
| flex/deep_random/10000 | initial | 8195 | 8195 | 4 | 6040 | 2151 | · | · | · | · | · | · | · |
| flex/deep_random/10000 | peak (initial) | 8195 | 8195 | 4 | 6040 | 2151 | · | · | · | · | · | · | · |
| flex/huge_nested/1000 | initial | 915 | 915 | 4 | 911 | · | · | · | · | · | · | · | · |
| flex/huge_nested/1000 | peak (initial) | 915 | 915 | 4 | 911 | · | · | · | · | · | · | · | · |
| flex/huge_nested/10000 | initial | 9115 | 9115 | 4 | 9111 | · | · | · | · | · | · | · | · |
| flex/huge_nested/10000 | peak (initial) | 9115 | 9115 | 4 | 9111 | · | · | · | · | · | · | · | · |
| flex/superdeep/100 | initial | 305 | 305 | 4 | 1 | · | · | · | 300 | · | · | · | · |
| flex/superdeep/100 | peak (leaf_10pct) | 305 | 305 | 4 | 1 | · | 21 | · | 99 | 1 | 7 | 172 | · |
| flex/superdeep/50 | initial | 155 | 155 | 4 | 1 | · | · | · | 150 | · | · | · | · |
| flex/superdeep/50 | peak (leaf_10pct) | 155 | 155 | 4 | 1 | · | 11 | · | 49 | 1 | 7 | 82 | · |
| flex/wide/1000 | initial | 1004 | 1004 | 4 | 618 | 309 | 47 | 12 | 14 | · | · | · | · |
| flex/wide/1000 | peak (leaf_10pct) | 1004 | 1004 | 4 | 633 | 294 | 19 | 10 | 24 | 12 | 8 | · | · |
| flex/wide/10000 | initial | 10005 | 10005 | 4 | 6240 | 2863 | 591 | 126 | 181 | · | · | · | · |
| flex/wide/10000 | peak (leaf_10pct) | 10005 | 10005 | 4 | 6434 | 2669 | 229 | 110 | 339 | 123 | 97 | · | · |
| grid/deep/2x2x5 | initial | 1369 | 1369 | 1046 | 39 | 60 | 38 | 95 | 81 | 4 | 4 | 2 | · |
| grid/deep/2x2x5 | peak (leaf_10pct) | 1369 | 1369 | 1046 | 39 | 60 | 36 | 89 | 76 | 8 | 11 | 3 | 1 |
| grid/deep/3x3x4 | initial | 7385 | 7385 | 6585 | 83 | 152 | 74 | 205 | 193 | 45 | 37 | 11 | · |
| grid/deep/3x3x4 | peak (root_width) | 7385 | 7385 | 6585 | 83 | 152 | 67 | 196 | 177 | 44 | 62 | 17 | 2 |
| grid/superdeep/100 | initial | 105 | 105 | 10 | 9 | 21 | 10 | 32 | 22 | 1 | · | · | · |
| grid/superdeep/100 | peak (root_width) | 105 | 105 | 10 | 9 | 21 | 9 | 32 | 22 | 1 | 1 | · | · |
| grid/wide/100x100 | initial | 10005 | 10005 | 251 | 774 | 1996 | 644 | 2393 | 2625 | 930 | 392 | · | · |
| grid/wide/100x100 | peak (leaf_10pct) | 10005 | 10005 | 355 | 902 | 2326 | 507 | 779 | 1590 | 2357 | 846 | · | 343 |
| grid/wide/31x31 | initial | 966 | 966 | 32 | 84 | 204 | 51 | 193 | 276 | 76 | 50 | · | · |
| grid/wide/31x31 | peak (leaf_10pct) | 966 | 966 | 42 | 106 | 234 | 1 | 34 | 12 | 168 | 44 | 232 | 93 |
| text/flex_cards/100 | initial | 305 | 305 | 5 | · | 300 | · | · | · | · | · | · | · |
| text/flex_cards/100 | peak (leaf_10pct) | 305 | 305 | 5 | 20 | 20 | 120 | 140 | · | · | · | · | · |
| text/flex_cards/1000 | initial | 3005 | 3005 | 5 | · | 3000 | · | · | · | · | · | · | · |
| text/flex_cards/1000 | peak (leaf_10pct) | 3005 | 3005 | 5 | 200 | 200 | 1200 | 1400 | · | · | · | · | · |
| text/inline_mixed/100 | initial | 105 | 105 | 105 | · | · | · | · | · | · | · | · | · |
| text/inline_mixed/100 | peak (initial) | 105 | 105 | 105 | · | · | · | · | · | · | · | · | · |
| text/inline_mixed/1000 | initial | 1005 | 1005 | 1005 | · | · | · | · | · | · | · | · | · |
| text/inline_mixed/1000 | peak (initial) | 1005 | 1005 | 1005 | · | · | · | · | · | · | · | · | · |
| text/paragraphs/100 | initial | 105 | 105 | 105 | · | · | · | · | · | · | · | · | · |
| text/paragraphs/100 | peak (initial) | 105 | 105 | 105 | · | · | · | · | · | · | · | · | · |
| text/paragraphs/1000 | initial | 1005 | 1005 | 1005 | · | · | · | · | · | · | · | · | · |
| text/paragraphs/1000 | peak (initial) | 1005 | 1005 | 1005 | · | · | · | · | · | · | · | · | · |
