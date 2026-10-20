Times in ms, min over all rounds and iterations. Servo(n) = `layout_threads=n`; Firefox(1) = `layout.css.stylo-threads=1` (no style worker threads).

### Layout only

| case | nodes | Taffy | Blitz `layout` | Servo(1) Fragment Tree | Servo(3) Fragment Tree | Chrome Layout | Firefox(1) Reflow | Firefox Reflow |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| text/paragraphs/100 | 101 | - | 1.321 | 3.153 | 1.301 | 7.494 | 7.358 | 6.911 |
| text/flex_cards/100 | 301 | - | 1.574 | 2.222 | 1.849 | 4.974 | 6.428 | 6.076 |
| text/inline_mixed/100 | 1599 | - | 1.594 | 7.798 | 2.323 | 12.835 | 18.694 | 18.745 |
| text/paragraphs/1000 | 1001 | - | 14.737 | 28.976 | 14.810 | 70.024 | 54.633 | 51.165 |
| text/flex_cards/1000 | 3001 | - | 18.039 | 33.664 | 33.283 | 44.302 | 40.332 | 38.967 |
| text/inline_mixed/1000 | 16361 | - | 16.320 | 52.710 | 19.631 | 111.273 | 136.964 | 127.937 |
| pangui/expand_with_max_constraint | 3001 | 2.050 | 5.299 | 6.591 | 6.589 | 5.126 | - | - |
| pangui/expand_with_min_constraint | 3001 | 2.044 | 5.244 | 6.468 | 6.322 | 5.187 | - | - |
| pangui/fit_nesting | 101111 | 57.874 | 165.051 | 593.806 | 284.921 | 172.667 | - | - |
| pangui/flex_expand_equal_weights | 15001 | 4.382 | 18.711 | 19.458 | 20.444 | 16.085 | - | - |
| pangui/flex_expand_weights | 15001 | 8.044 | 21.811 | 23.737 | 24.037 | 16.106 | - | - |
| pangui/nested_vertical_stack | 10001 | 3.133 | 17.621 | 18.603 | 18.487 | 10.235 | - | - |
| pangui/padding_and_margin | 101 | 0.024 | 0.119 | 0.233 | 0.238 | 0.189 | - | - |
| pangui/percentage_and_ratio | 10001 | 3.107 | 11.243 | 15.544 | 15.413 | 20.102 | - | - |
| pangui/perpendicular_expand_with_wrap | 12001 | 4.588 | 28.130 | 1968.099 | 1956.721 | 19.264 | - | - |
| pangui/pixels_with_min_expand_constraint | 30001 | 24.589 | 67.819 | 68.462 | 71.100 | 53.624 | - | - |
| pangui/wide_no_wrap_simple_few | 1001 | 0.251 | 1.135 | 1.349 | 1.255 | 1.174 | - | - |
| pangui/wide_no_wrap_simple_many | 100001 | 60.313 | 209.254 | 171.306 | 176.065 | 117.492 | - | - |
| pangui/wide_wrapping | 10001 | 3.188 | 17.474 | 567.436 | 554.451 | 12.095 | - | - |
| flex/huge_nested/1000 | 911 | 0.394 | 1.265 | 1.522 | 0.955 | 1.363 | - | - |
| flex/wide/1000 | 1000 | 0.657 | 1.884 | 2.014 | 1.954 | 1.798 | - | - |
| flex/absolute/1000 | 1003 | 0.458 | 1.324 | 1.683 | 1.666 | 1.782 | - | - |
| flex/deep_auto/1000 | 767 | 1.419 | 2.484 | 2.019 | 2.009 | 2.437 | - | - |
| flex/deep_random/1000 | 767 | 0.598 | 1.135 | 1.465 | 1.451 | 1.314 | - | - |
| flex/huge_nested/10000 | 9111 | 4.268 | 10.920 | 15.073 | 8.568 | 12.668 | - | - |
| flex/wide/10000 | 10001 | 7.092 | 20.738 | 20.282 | 20.159 | 18.220 | - | - |
| flex/absolute/10000 | 10004 | 5.169 | 12.312 | 17.261 | 17.140 | 17.879 | - | - |
| flex/deep_auto/10000 | 8191 | 14.653 | 27.823 | 21.431 | 21.159 | 24.815 | - | - |
| flex/deep_random/10000 | 8191 | 6.364 | 13.409 | 15.740 | 15.987 | 12.861 | - | - |
| flex/superdeep/50 | 151 | 0.217 | 0.482 | 0.428 | 0.429 | 0.626 | - | - |
| flex/superdeep/100 | 301 | 0.433 | 0.961 | 0.862 | 0.872 | 1.233 | - | - |
| grid/wide/31x31 | 962 | 0.845 | 2.357 | 3.858 | 3.808 | 3.819 | - | - |
| grid/wide/100x100 | 10001 | 10.501 | 26.759 | 39.966 | 39.964 | 45.412 | - | - |
| grid/deep/2x2x5 | 1365 | 3.467 | 4.957 | 20.989 | 20.872 | 9.218 | - | - |
| grid/deep/3x3x4 | 7381 | 15.992 | 22.672 | 81.761 | 81.185 | 40.101 | - | - |
| grid/superdeep/100 | 101 | 0.468 | 0.670 | 269.340 | 261.370 | 1.930 | - | - |

### Box construction + layout

| case | nodes | Blitz construct+layout | Servo(1) Box+Fragment | Servo(3) Box+Fragment | Chrome rebuildLayoutTree+Layout |
|---|---:|---:|---:|---:|---:|
| text/paragraphs/100 | 101 | 13.704 | 22.547 | 17.521 | 7.608 |
| text/flex_cards/100 | 301 | 5.938 | 9.975 | 7.253 | 5.219 |
| text/inline_mixed/100 | 1599 | 18.278 | 35.950 | 17.436 | 14.243 |
| text/paragraphs/1000 | 1001 | 137.437 | 215.317 | 170.671 | 70.853 |
| text/flex_cards/1000 | 3001 | 61.734 | 101.408 | 82.767 | 46.450 |
| text/inline_mixed/1000 | 16361 | 183.386 | 330.163 | 144.352 | 125.361 |
| pangui/expand_with_max_constraint | 3001 | 5.640 | 10.191 | 8.677 | 6.737 |
| pangui/expand_with_min_constraint | 3001 | 5.579 | 10.037 | 8.487 | 6.759 |
| pangui/fit_nesting | 101111 | 186.247 | 705.652 | 324.907 | 223.716 |
| pangui/flex_expand_equal_weights | 15001 | 21.711 | 36.011 | 36.761 | 23.434 |
| pangui/flex_expand_weights | 15001 | 24.890 | 44.840 | 34.825 | 24.030 |
| pangui/nested_vertical_stack | 10001 | 19.523 | 31.689 | 29.500 | 15.029 |
| pangui/padding_and_margin | 101 | 0.129 | 0.419 | 0.467 | 0.266 |
| pangui/percentage_and_ratio | 10001 | 13.356 | 28.820 | 26.722 | 25.015 |
| pangui/perpendicular_expand_with_wrap | 12001 | 30.406 | 1982.709 | 1971.039 | 25.170 |
| pangui/pixels_with_min_expand_constraint | 30001 | 74.241 | 111.905 | 93.302 | 69.348 |
| pangui/wide_no_wrap_simple_few | 1001 | 1.206 | 2.337 | 2.308 | 1.696 |
| pangui/wide_no_wrap_simple_many | 100001 | 254.860 | 337.787 | 294.020 | 166.735 |
| pangui/wide_wrapping | 10001 | 19.350 | 581.738 | 567.341 | 16.911 |
| flex/huge_nested/1000 | 911 | 1.343 | 2.486 | 1.441 | 1.847 |
| flex/wide/1000 | 1000 | 1.981 | 3.227 | 2.733 | 2.326 |
| flex/absolute/1000 | 1003 | 1.415 | 3.083 | 2.479 | 2.602 |
| flex/deep_auto/1000 | 767 | 2.573 | 6.267 | 3.232 | 2.873 |
| flex/deep_random/1000 | 767 | 1.240 | 3.285 | 2.692 | 1.750 |
| flex/huge_nested/10000 | 9111 | 11.840 | 24.150 | 12.145 | 17.295 |
| flex/wide/10000 | 10001 | 22.073 | 31.634 | 26.577 | 23.157 |
| flex/absolute/10000 | 10004 | 13.612 | 30.839 | 24.394 | 25.831 |
| flex/deep_auto/10000 | 8191 | 28.986 | 32.015 | 32.068 | 29.456 |
| flex/deep_random/10000 | 8191 | 14.682 | 26.352 | 27.141 | 17.345 |
| flex/superdeep/50 | 151 | 0.497 | 0.805 | 0.812 | 0.746 |
| flex/superdeep/100 | 301 | 0.991 | 1.545 | 1.557 | 1.483 |
| grid/wide/31x31 | 962 | 2.421 | 5.021 | 4.912 | 4.315 |
| grid/wide/100x100 | 10001 | 27.887 | 54.768 | 52.667 | 50.168 |
| grid/deep/2x2x5 | 1365 | 5.088 | 22.643 | 21.641 | 10.012 |
| grid/deep/3x3x4 | 7381 | 23.416 | 91.739 | 84.584 | 43.953 |
| grid/superdeep/100 | 101 | 0.687 | 272.959 | 261.962 | 2.044 |

### Style

| case | nodes | Blitz style | Blitz style (parallel) | Servo(1) Styling | Servo(3) Styling | Chrome recalcStyle | Firefox(1) Styles (incl. frame construction) | Firefox Styles (incl. frame construction) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| text/paragraphs/100 | 101 | 0.545 | 0.390 | 0.776 | 0.599 | 0.293 | 0.736 | 0.444 |
| text/flex_cards/100 | 301 | 0.868 | 0.580 | 1.397 | 0.962 | 0.486 | 1.374 | 0.793 |
| text/inline_mixed/100 | 1599 | 1.754 | 1.492 | 2.853 | 1.876 | 1.218 | 3.297 | 2.065 |
| text/paragraphs/1000 | 1001 | 5.432 | 8.849 | 8.506 | 7.346 | 2.454 | 7.170 | 2.749 |
| text/flex_cards/1000 | 3001 | 8.972 | 8.734 | 15.430 | 9.704 | 4.089 | 13.698 | 6.358 |
| text/inline_mixed/1000 | 16361 | 19.326 | 17.726 | 31.188 | 19.510 | 11.571 | 33.445 | 18.776 |
| pangui/expand_with_max_constraint | 3001 | 11.721 | 11.445 | 19.135 | 13.915 | 6.336 | - | - |
| pangui/expand_with_min_constraint | 3001 | 11.687 | 12.298 | 19.286 | 13.675 | 6.218 | - | - |
| pangui/fit_nesting | 101111 | 628.385 | 787.676 | 958.390 | 743.658 | 322.449 | - | - |
| pangui/flex_expand_equal_weights | 15001 | 87.863 | 129.982 | 137.845 | 117.131 | 40.190 | - | - |
| pangui/flex_expand_weights | 15001 | 65.079 | 60.682 | 95.702 | 72.551 | 30.705 | - | - |
| pangui/nested_vertical_stack | 10001 | 57.518 | 88.359 | 89.803 | 76.626 | 26.743 | - | - |
| pangui/padding_and_margin | 101 | 0.575 | 0.370 | 1.060 | 0.769 | 0.384 | - | - |
| pangui/percentage_and_ratio | 10001 | 58.011 | 90.829 | 92.093 | 77.214 | 29.299 | - | - |
| pangui/perpendicular_expand_with_wrap | 12001 | 66.854 | 105.786 | 102.480 | 93.137 | 32.246 | - | - |
| pangui/pixels_with_min_expand_constraint | 30001 | 135.677 | 131.289 | 200.846 | 142.195 | 62.836 | - | - |
| pangui/wide_no_wrap_simple_few | 1001 | 5.455 | 8.550 | 10.502 | 7.846 | 2.761 | - | - |
| pangui/wide_no_wrap_simple_many | 100001 | 624.976 | 928.311 | 963.486 | 772.329 | 319.860 | - | - |
| pangui/wide_wrapping | 10001 | 58.512 | 89.713 | 91.396 | 78.836 | 27.349 | - | - |
| flex/huge_nested/1000 | 911 | 4.333 | 4.366 | 11.343 | 5.756 | 2.038 | - | - |
| flex/wide/1000 | 1000 | 3.136 | 2.790 | 9.600 | 3.502 | 1.919 | - | - |
| flex/absolute/1000 | 1003 | 3.257 | 2.548 | 10.046 | 3.786 | 2.209 | - | - |
| flex/deep_auto/1000 | 767 | 1.757 | 1.498 | 5.989 | 2.144 | 1.134 | - | - |
| flex/deep_random/1000 | 767 | 1.774 | 0.885 | 7.039 | 2.355 | 1.337 | - | - |
| flex/huge_nested/10000 | 9111 | 43.742 | 61.629 | 72.429 | 59.266 | 19.868 | - | - |
| flex/wide/10000 | 10001 | 32.168 | 31.811 | 61.270 | 34.514 | 18.657 | - | - |
| flex/absolute/10000 | 10004 | 33.505 | 31.932 | 62.665 | 35.060 | 21.653 | - | - |
| flex/deep_auto/10000 | 8191 | 25.869 | 31.943 | 41.605 | 31.280 | 14.304 | - | - |
| flex/deep_random/10000 | 8191 | 20.038 | 8.451 | 42.781 | 20.519 | 14.196 | - | - |
| flex/superdeep/50 | 151 | 0.398 | 0.405 | 0.993 | 1.019 | 0.394 | - | - |
| flex/superdeep/100 | 301 | 0.764 | 0.780 | 1.856 | 1.834 | 0.714 | - | - |
| grid/wide/31x31 | 962 | 4.693 | 7.859 | 12.669 | 7.183 | 1.728 | - | - |
| grid/wide/100x100 | 10001 | 49.589 | 86.469 | 82.777 | 76.222 | 17.714 | - | - |
| grid/deep/2x2x5 | 1365 | 3.628 | 1.800 | 8.497 | 3.992 | 3.024 | - | - |
| grid/deep/3x3x4 | 7381 | 21.305 | 12.779 | 43.468 | 21.091 | 15.216 | - | - |
| grid/superdeep/100 | 101 | 0.242 | 0.261 | 0.678 | 0.709 | 0.280 | - | - |

### Whole pipeline (style to paint tree / display list)

| case | nodes | Blitz resolve() | Servo(1) handle_reflow | Servo(3) handle_reflow | Chrome UpdateLayoutTree+Layout | Firefox(1) Styles+Reflow | Firefox Styles+Reflow |
|---|---:|---:|---:|---:|---:|---:|---:|
| text/paragraphs/100 | 101 | 14.287 | 23.861 | 18.659 | 7.932 | 8.177 | 7.400 |
| text/flex_cards/100 | 301 | 6.915 | 11.739 | 8.561 | 5.723 | 7.802 | 7.021 |
| text/inline_mixed/100 | 1599 | 20.290 | 40.017 | 20.544 | 15.488 | 22.071 | 21.982 |
| text/paragraphs/1000 | 1001 | 143.365 | 229.913 | 183.832 | 73.331 | 61.828 | 54.238 |
| text/flex_cards/1000 | 3001 | 71.641 | 119.717 | 96.906 | 50.587 | 54.030 | 45.325 |
| text/inline_mixed/1000 | 16361 | 206.301 | 375.841 | 177.094 | 136.957 | 172.529 | 149.949 |
| pangui/expand_with_max_constraint | 3001 | 18.201 | 31.938 | 25.899 | 13.170 | - | - |
| pangui/expand_with_min_constraint | 3001 | 18.093 | 31.773 | 25.278 | 13.050 | - | - |
| pangui/fit_nesting | 101111 | 872.891 | 1729.949 | 1139.703 | 546.216 | - | - |
| pangui/flex_expand_equal_weights | 15001 | 119.402 | 181.839 | 167.031 | 63.991 | - | - |
| pangui/flex_expand_weights | 15001 | 98.025 | 151.148 | 117.937 | 54.994 | - | - |
| pangui/nested_vertical_stack | 10001 | 80.590 | 127.578 | 113.780 | 41.916 | - | - |
| pangui/padding_and_margin | 101 | 0.738 | 2.983 | 2.809 | 0.710 | - | - |
| pangui/percentage_and_ratio | 10001 | 76.213 | 127.529 | 110.379 | 54.412 | - | - |
| pangui/perpendicular_expand_with_wrap | 12001 | 103.812 | 2093.545 | 2076.551 | 57.781 | - | - |
| pangui/pixels_with_min_expand_constraint | 30001 | 232.936 | 336.518 | 250.582 | 132.552 | - | - |
| pangui/wide_no_wrap_simple_few | 1001 | 6.996 | 14.699 | 11.977 | 4.545 | - | - |
| pangui/wide_no_wrap_simple_many | 100001 | 959.131 | 1362.613 | 1134.069 | 493.428 | - | - |
| pangui/wide_wrapping | 10001 | 81.383 | 682.160 | 653.726 | 44.474 | - | - |
| flex/huge_nested/1000 | 911 | 5.841 | 18.628 | 9.163 | 3.964 | - | - |
| flex/wide/1000 | 1000 | 5.342 | 17.629 | 8.294 | 4.317 | - | - |
| flex/absolute/1000 | 1003 | 4.935 | 15.271 | 8.556 | 4.892 | - | - |
| flex/deep_auto/1000 | 767 | 4.499 | 13.917 | 7.205 | 4.075 | - | - |
| flex/deep_random/1000 | 767 | 3.225 | 14.583 | 6.962 | 3.163 | - | - |
| flex/huge_nested/10000 | 9111 | 57.700 | 101.309 | 77.209 | 37.276 | - | - |
| flex/wide/10000 | 10001 | 57.148 | 98.534 | 67.421 | 41.841 | - | - |
| flex/absolute/10000 | 10004 | 50.020 | 102.523 | 68.849 | 47.558 | - | - |
| flex/deep_auto/10000 | 8191 | 57.734 | 79.008 | 68.699 | 43.876 | - | - |
| flex/deep_random/10000 | 8191 | 37.314 | 74.418 | 53.611 | 31.617 | - | - |
| flex/superdeep/50 | 151 | 0.947 | 3.310 | 3.473 | 1.228 | - | - |
| flex/superdeep/100 | 301 | 1.832 | 4.948 | 5.064 | 2.270 | - | - |
| grid/wide/31x31 | 962 | 7.271 | 22.012 | 14.008 | 6.115 | - | - |
| grid/wide/100x100 | 10001 | 80.562 | 144.684 | 135.626 | 67.905 | - | - |
| grid/deep/2x2x5 | 1365 | 9.077 | 35.885 | 27.780 | 13.136 | - | - |
| grid/deep/3x3x4 | 7381 | 46.458 | 140.110 | 110.434 | 59.232 | - | - |
| grid/superdeep/100 | 101 | 0.970 | 275.231 | 264.309 | 2.410 | - | - |
