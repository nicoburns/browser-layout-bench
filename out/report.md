Times in ms, min over all rounds and iterations; second line of each cell is the multiple of the Chrome column of the same table (1.00x = Chrome); bold = fastest engine of the row, Taffy excluded. Servo(n) = `layout_threads=n`; Firefox(1) = `layout.css.stylo-threads=1` (no style worker threads). Text shaping is in the layout phase of Chrome, Firefox and Ladybird but in the construction phase of Blitz and Servo, so "Layout only" is like-for-like only among Servo/Blitz/Taffy and "Box construction + layout" is the comparable table for text-bearing cases; Firefox's Reflow (shaping + layout; its frame construction is inside Styles) is listed there. Case names link to the case's bar chart; one page of charts per suite: [flex/](plots/flex.md) · [grid/](plots/grid.md) · [pangui/](plots/pangui.md) · [text/](plots/text.md) · [real/](plots/real.md).

### Layout only

| case | nodes | Chrome<br>Layout (incl. shaping) | Ladybird<br>layout (incl. shaping) | Servo(1)<br>Fragment Tree | Servo(3)<br>Fragment Tree | Blitz<br>`layout` | Blitz<br>`layout` (#1034 build, 1 thread) | Blitz<br>`layout` (parallel layout) | Taffy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [flex/huge_nested/1000](plots/flex/huge-nested-1000.svg) | 911 | 0.912<br>1.00x | 4.527<br>4.96x | 1.229<br>1.35x | 0.827<br>0.91x | 0.611<br>0.67x | 0.806<br>0.88x | **0.555<br>0.61x** | 0.272<br>0.30x |
| [flex/wide/1000](plots/flex/wide-1000.svg) | 1000 | 1.238<br>1.00x | 6.245<br>5.04x | 1.670<br>1.35x | 1.661<br>1.34x | 1.035<br>0.84x | 1.355<br>1.09x | **0.858<br>0.69x** | 0.447<br>0.36x |
| [flex/absolute/1000](plots/flex/absolute-1000.svg) | 1003 | 1.308<br>1.00x | 4.135<br>3.16x | 1.398<br>1.07x | 1.447<br>1.11x | **0.761<br>0.58x** | 0.930<br>0.71x | 0.878<br>0.67x | 0.314<br>0.24x |
| [flex/deep_auto/1000](plots/flex/deep-auto-1000.svg) | 767 | 1.661<br>1.00x | 6.953<br>4.19x | 1.633<br>0.98x | 1.524<br>0.92x | 1.709<br>1.03x | 2.169<br>1.31x | **0.618<br>0.37x** | 0.921<br>0.55x |
| [flex/deep_random/1000](plots/flex/deep-random-1000.svg) | 767 | 0.906<br>1.00x | 5.626<br>6.21x | 1.220<br>1.35x | 1.179<br>1.30x | 0.758<br>0.84x | 1.006<br>1.11x | **0.476<br>0.52x** | 0.405<br>0.45x |
| [flex/huge_nested/10000](plots/flex/huge-nested-10000.svg) | 9111 | 8.736<br>1.00x | 44.358<br>5.08x | 12.172<br>1.39x | 7.005<br>0.80x | 6.189<br>0.71x | 7.419<br>0.85x | **2.104<br>0.24x** | 3.156<br>0.36x |
| [flex/wide/10000](plots/flex/wide-10000.svg) | 10001 | 12.819<br>1.00x | 69.032<br>5.39x | 16.651<br>1.30x | 16.952<br>1.32x | 11.040<br>0.86x | 13.973<br>1.09x | **7.193<br>0.56x** | 5.326<br>0.42x |
| [flex/absolute/10000](plots/flex/absolute-10000.svg) | 10004 | 13.871<br>1.00x | 47.110<br>3.40x | 14.651<br>1.06x | 15.167<br>1.09x | 8.006<br>0.58x | 10.048<br>0.72x | **6.365<br>0.46x** | 4.041<br>0.29x |
| [flex/deep_auto/10000](plots/flex/deep-auto-10000.svg) | 8191 | 17.363<br>1.00x | 63.792<br>3.67x | 17.476<br>1.01x | 17.623<br>1.01x | 17.989<br>1.04x | 21.785<br>1.25x | **4.176<br>0.24x** | 10.020<br>0.58x |
| [flex/deep_random/10000](plots/flex/deep-random-10000.svg) | 8191 | 8.826<br>1.00x | 54.558<br>6.18x | 12.959<br>1.47x | 13.620<br>1.54x | 8.087<br>0.92x | 9.534<br>1.08x | **3.159<br>0.36x** | 4.685<br>0.53x |
| [flex/superdeep/50](plots/flex/superdeep-50.svg) | 151 | 0.441<br>1.00x | 1.668<br>3.78x | 0.348<br>0.79x | 0.343<br>0.78x | **0.316<br>0.72x** | 0.445<br>1.01x | 0.698<br>1.58x | 0.146<br>0.33x |
| [flex/superdeep/100](plots/flex/superdeep-100.svg) | 301 | 0.868<br>1.00x | 3.021<br>3.48x | 0.719<br>0.83x | 0.703<br>0.81x | **0.613<br>0.71x** | 0.842<br>0.97x | 1.321<br>1.52x | 0.291<br>0.33x |
| [grid/wide/31x31](plots/grid/wide-31x31.svg) | 962 | 2.624<br>1.00x | 5.518<br>2.10x | 2.825<br>1.08x | 2.760<br>1.05x | **1.448<br>0.55x** | 1.936<br>0.74x | 1.900<br>0.72x | 0.609<br>0.23x |
| [grid/wide/100x100](plots/grid/wide-100x100.svg) | 10001 | 36.154<br>1.00x | 66.159<br>1.83x | 30.787<br>0.85x | 30.370<br>0.84x | **15.893<br>0.44x** | 21.644<br>0.60x | 21.961<br>0.61x | 8.260<br>0.23x |
| [grid/deep/2x2x5](plots/grid/deep-2x2x5.svg) | 1365 | 7.005<br>1.00x | 13.724<br>1.96x | 15.711<br>2.24x | 15.699<br>2.24x | 3.502<br>0.50x | 4.865<br>0.69x | **1.480<br>0.21x** | 2.526<br>0.36x |
| [grid/deep/3x3x4](plots/grid/deep-3x3x4.svg) | 7381 | 30.085<br>1.00x | 70.957<br>2.36x | 63.173<br>2.10x | 63.551<br>2.11x | 16.257<br>0.54x | 23.200<br>0.77x | **5.235<br>0.17x** | 12.304<br>0.41x |
| [grid/superdeep/100](plots/grid/superdeep-100.svg) | 101 | 1.492<br>1.00x | 2.484<br>1.67x | 204.492<br>137.06x | 197.354<br>132.27x | **0.473<br>0.32x** | 0.615<br>0.41x | 0.595<br>0.40x | 0.341<br>0.23x |
| [pangui/expand_with_max_constraint](plots/pangui/expand-with-max-constraint.svg) | 3001 | 3.575<br>1.00x | 10.350<br>2.90x | 5.356<br>1.50x | 5.377<br>1.50x | 3.343<br>0.94x | 3.814<br>1.07x | **2.278<br>0.64x** | 1.465<br>0.41x |
| [pangui/expand_with_min_constraint](plots/pangui/expand-with-min-constraint.svg) | 3001 | 3.572<br>1.00x | 10.188<br>2.85x | 5.376<br>1.50x | 5.321<br>1.49x | 3.313<br>0.93x | 3.813<br>1.07x | **2.129<br>0.60x** | 1.451<br>0.41x |
| [pangui/fit_nesting](plots/pangui/fit-nesting.svg) | 101111 | 127.996<br>1.00x | 366.543<br>2.86x | 468.165<br>3.66x | 237.856<br>1.86x | 79.481<br>0.62x | 84.907<br>0.66x | **22.952<br>0.18x** | 32.136<br>0.25x |
| [pangui/flex_expand_equal_weights](plots/pangui/flex-expand-equal-weights.svg) | 15001 | 11.974<br>1.00x | 44.127<br>3.69x | 15.730<br>1.31x | 17.085<br>1.43x | **7.244<br>0.61x** | 8.367<br>0.70x | 8.862<br>0.74x | 3.821<br>0.32x |
| [pangui/flex_expand_weights](plots/pangui/flex-expand-weights.svg) | 15001 | 10.599<br>1.00x | 37.216<br>3.51x | 19.301<br>1.82x | 19.281<br>1.82x | 11.031<br>1.04x | 12.682<br>1.20x | **6.118<br>0.58x** | 5.751<br>0.54x |
| [pangui/nested_vertical_stack](plots/pangui/nested-vertical-stack.svg) | 10001 | 7.265<br>1.00x | 34.590<br>4.76x | 14.344<br>1.97x | 14.595<br>2.01x | **7.141<br>0.98x** | 9.210<br>1.27x | 8.266<br>1.14x | 2.552<br>0.35x |
| [pangui/padding_and_margin](plots/pangui/padding-and-margin.svg) | 101 | 0.137<br>1.00x | 0.617<br>4.51x | 0.201<br>1.47x | 0.210<br>1.54x | **0.066<br>0.48x** | 0.079<br>0.58x | 0.075<br>0.55x | 0.019<br>0.14x |
| [pangui/percentage_and_ratio](plots/pangui/percentage-and-ratio.svg) | 10001 | 13.572<br>1.00x | 31.026<br>2.29x | 12.366<br>0.91x | 12.518<br>0.92x | **5.594<br>0.41x** | 7.074<br>0.52x | 5.803<br>0.43x | 2.521<br>0.19x |
| [pangui/perpendicular_expand_with_wrap](plots/pangui/perpendicular-expand-with-wrap.svg) | 12001 | 13.749<br>1.00x | 39.809<br>2.90x | 1517.525<br>110.37x | 1496.036<br>108.81x | **11.639<br>0.85x** | 14.680<br>1.07x | 13.052<br>0.95x | 3.426<br>0.25x |
| [pangui/pixels_with_min_expand_constraint](plots/pangui/pixels-with-min-expand-constraint.svg) | 30001 | 36.579<br>1.00x | 116.606<br>3.19x | 53.025<br>1.45x | 55.165<br>1.51x | 33.499<br>0.92x | 40.859<br>1.12x | **16.715<br>0.46x** | 15.520<br>0.42x |
| [pangui/wide_no_wrap_simple_few](plots/pangui/wide-no-wrap-simple-few.svg) | 1001 | 0.772<br>1.00x | 2.514<br>3.26x | 1.095<br>1.42x | 1.120<br>1.45x | **0.516<br>0.67x** | 0.785<br>1.02x | 0.830<br>1.08x | 0.182<br>0.24x |
| [pangui/wide_no_wrap_simple_many](plots/pangui/wide-no-wrap-simple-many.svg) | 100001 | 81.769<br>1.00x | 305.512<br>3.74x | 134.211<br>1.64x | 138.445<br>1.69x | **81.338<br>0.99x** | 108.173<br>1.32x | 89.565<br>1.10x | 28.808<br>0.35x |
| [pangui/wide_wrapping](plots/pangui/wide-wrapping.svg) | 10001 | 8.966<br>1.00x | 32.691<br>3.65x | 420.850<br>46.94x | 420.923<br>46.95x | **7.057<br>0.79x** | 9.998<br>1.12x | 8.736<br>0.97x | 2.524<br>0.28x |
| [text/paragraphs/100](plots/text/paragraphs-100.svg) | 101 | 5.490<br>1.00x | 9.051<br>1.65x | 2.267<br>0.41x | 1.490<br>0.27x | 1.063<br>0.19x | 1.110<br>0.20x | **0.280<br>0.05x** | - |
| [text/flex_cards/100](plots/text/flex-cards-100.svg) | 301 | 3.626<br>1.00x | 6.722<br>1.85x | 1.745<br>0.48x | 1.845<br>0.51x | 1.227<br>0.34x | 1.348<br>0.37x | **0.412<br>0.11x** | - |
| [text/inline_mixed/100](plots/text/inline-mixed-100.svg) | 1599 | 9.103<br>1.00x | 18.834<br>2.07x | 6.747<br>0.74x | 2.633<br>0.29x | 1.212<br>0.13x | 1.257<br>0.14x | **0.310<br>0.03x** | - |
| [text/paragraphs/1000](plots/text/paragraphs-1000.svg) | 1001 | 51.783<br>1.00x | 90.645<br>1.75x | 24.367<br>0.47x | 10.444<br>0.20x | 10.571<br>0.20x | 10.292<br>0.20x | **2.014<br>0.04x** | - |
| [text/flex_cards/1000](plots/text/flex-cards-1000.svg) | 3001 | 33.214<br>1.00x | 63.415<br>1.91x | 27.315<br>0.82x | 27.927<br>0.84x | 12.485<br>0.38x | 13.489<br>0.41x | **3.649<br>0.11x** | - |
| [text/inline_mixed/1000](plots/text/inline-mixed-1000.svg) | 16361 | 84.178<br>1.00x | 186.091<br>2.21x | 44.986<br>0.53x | 18.419<br>0.22x | 12.184<br>0.14x | 12.193<br>0.14x | **2.108<br>0.03x** | - |
| [real/wikipedia](plots/real/wikipedia.svg) | 21889 | 155.201<br>1.00x | 403.446<br>2.60x | 46.348<br>0.30x | 43.685<br>0.28x | 20.051<br>0.13x | 20.749<br>0.13x | **17.637<br>0.11x** | - |
| [real/wikipedia@1024](plots/real/wikipedia-1024.svg) | 21889 | 158.673<br>1.00x | 361.391<br>2.28x | 46.011<br>0.29x | 45.449<br>0.29x | 14.474<br>0.09x | 15.847<br>0.10x | **12.197<br>0.08x** | - |
| [real/mdn](plots/real/mdn.svg) | 2212 | 11.176<br>1.00x | 45.893<br>4.11x | 6.747<br>0.60x | 3.207<br>0.29x | 3.542<br>0.32x | 3.968<br>0.36x | **1.321<br>0.12x** | - |
| [real/mdn@1024](plots/real/mdn-1024.svg) | 2212 | 7.672<br>1.00x | 35.187<br>4.59x | 5.199<br>0.68x | 4.429<br>0.58x | 2.240<br>0.29x | 2.537<br>0.33x | **0.835<br>0.11x** | - |
| [real/rustdoc](plots/real/rustdoc.svg) | 15947 | 88.320<br>1.00x | 360.013<br>4.08x | 45.564<br>0.52x | 41.445<br>0.47x | 24.341<br>0.28x | 25.384<br>0.29x | **22.169<br>0.25x** | - |
| [real/css-flexbox-1](plots/real/css-flexbox-1.svg) | 15890 | 87.237<br>1.00x | 200.453<br>2.30x | 43.837<br>0.50x | 40.442<br>0.46x | 24.685<br>0.28x | 24.663<br>0.28x | **21.269<br>0.24x** | - |
| [real/servo-org](plots/real/servo-org.svg) | 226 | 2.193<br>1.00x | 4.547<br>2.07x | 2.179<br>0.99x | 1.348<br>0.61x | 0.433<br>0.20x | 0.575<br>0.26x | **0.244<br>0.11x** | - |
| [real/servo-org@1024](plots/real/servo-org-1024.svg) | 226 | 2.187<br>1.00x | 4.577<br>2.09x | 1.837<br>0.84x | 0.883<br>0.40x | 0.436<br>0.20x | 0.572<br>0.26x | **0.243<br>0.11x** | - |
| [real/dioxuslabs-com](plots/real/dioxuslabs-com.svg) | 158 | 3.027<br>1.00x | 15.923<br>5.26x | 2.476<br>0.82x | 0.902<br>0.30x | 0.439<br>0.15x | 0.580<br>0.19x | **0.342<br>0.11x** | - |
| [real/dioxuslabs-com@1024](plots/real/dioxuslabs-com-1024.svg) | 158 | 3.286<br>1.00x | 15.921<br>4.85x | 2.732<br>0.83x | 0.675<br>0.21x | 0.432<br>0.13x | 0.598<br>0.18x | **0.366<br>0.11x** | - |
| [real/bootstrap-dashboard](plots/real/bootstrap-dashboard.svg) | 199 | 1.647<br>1.00x | 2.771<br>1.68x | 1.597<br>0.97x | 0.942<br>0.57x | 0.597<br>0.36x | 0.765<br>0.46x | **0.546<br>0.33x** | - |
| [real/bootstrap-dashboard@1024](plots/real/bootstrap-dashboard-1024.svg) | 199 | 1.689<br>1.00x | 2.792<br>1.65x | 1.643<br>0.97x | 0.821<br>0.49x | 0.605<br>0.36x | 0.758<br>0.45x | **0.513<br>0.30x** | - |

### Construction

| case | nodes | Chrome<br>rebuildLayoutTree | Ladybird<br>tree build | Servo(1)<br>Box Tree | Servo(3)<br>Box Tree | Blitz<br>construct ( + pconstruct) | Blitz<br>construct, parallel |
|---|---:|---:|---:|---:|---:|---:|---:|
| [flex/huge_nested/1000](plots/flex/huge-nested-1000.svg) | 911 | 0.326<br>1.00x | 0.586<br>1.80x | 0.855<br>2.62x | 0.446<br>1.37x | **0.050<br>0.15x** | 0.051<br>0.16x |
| [flex/wide/1000](plots/flex/wide-1000.svg) | 1000 | 0.353<br>1.00x | 0.645<br>1.83x | 1.047<br>2.97x | 0.713<br>2.02x | 0.067<br>0.19x | **0.065<br>0.18x** |
| [flex/absolute/1000](plots/flex/absolute-1000.svg) | 1003 | 0.567<br>1.00x | 0.714<br>1.26x | 1.224<br>2.16x | 0.729<br>1.29x | **0.059<br>0.10x** | 0.064<br>0.11x |
| [flex/deep_auto/1000](plots/flex/deep-auto-1000.svg) | 767 | 0.288<br>1.00x | 0.565<br>1.96x | 1.086<br>3.77x | 1.098<br>3.81x | **0.054<br>0.19x** | 0.054<br>0.19x |
| [flex/deep_random/1000](plots/flex/deep-random-1000.svg) | 767 | 0.293<br>1.00x | 0.546<br>1.87x | 1.105<br>3.77x | 1.129<br>3.85x | 0.061<br>0.21x | **0.060<br>0.21x** |
| [flex/huge_nested/10000](plots/flex/huge-nested-10000.svg) | 9111 | 3.515<br>1.00x | 6.306<br>1.79x | 7.776<br>2.21x | 3.245<br>0.92x | 0.617<br>0.18x | **0.616<br>0.18x** |
| [flex/wide/10000](plots/flex/wide-10000.svg) | 10001 | 3.410<br>1.00x | 6.890<br>2.02x | 10.036<br>2.94x | 5.732<br>1.68x | **0.815<br>0.24x** | 0.840<br>0.25x |
| [flex/absolute/10000](plots/flex/absolute-10000.svg) | 10004 | 5.842<br>1.00x | 7.917<br>1.36x | 11.895<br>2.04x | 6.668<br>1.14x | **0.746<br>0.13x** | 0.759<br>0.13x |
| [flex/deep_auto/10000](plots/flex/deep-auto-10000.svg) | 8191 | 3.549<br>1.00x | 6.165<br>1.74x | 9.345<br>2.63x | 9.569<br>2.70x | **0.646<br>0.18x** | 0.661<br>0.19x |
| [flex/deep_random/10000](plots/flex/deep-random-10000.svg) | 8191 | 3.101<br>1.00x | 6.779<br>2.19x | 9.413<br>3.04x | 9.879<br>3.19x | 0.721<br>0.23x | **0.714<br>0.23x** |
| [flex/superdeep/50](plots/flex/superdeep-50.svg) | 151 | 0.087<br>1.00x | 0.189<br>2.17x | 0.325<br>3.73x | 0.319<br>3.66x | 0.010<br>0.12x | **0.010<br>0.11x** |
| [flex/superdeep/100](plots/flex/superdeep-100.svg) | 301 | 0.178<br>1.00x | 0.440<br>2.47x | 0.590<br>3.31x | 0.555<br>3.12x | **0.017<br>0.10x** | 0.019<br>0.10x |
| [grid/wide/31x31](plots/grid/wide-31x31.svg) | 962 | 0.322<br>1.00x | 0.643<br>2.00x | 0.890<br>2.76x | 0.935<br>2.90x | **0.046<br>0.14x** | 0.048<br>0.15x |
| [grid/wide/100x100](plots/grid/wide-100x100.svg) | 10001 | 3.261<br>1.00x | 6.888<br>2.11x | 9.493<br>2.91x | 9.915<br>3.04x | 0.997<br>0.31x | **0.961<br>0.29x** |
| [grid/deep/2x2x5](plots/grid/deep-2x2x5.svg) | 1365 | 0.560<br>1.00x | 0.958<br>1.71x | 1.420<br>2.54x | 0.688<br>1.23x | **0.094<br>0.17x** | 0.096<br>0.17x |
| [grid/deep/3x3x4](plots/grid/deep-3x3x4.svg) | 7381 | 2.728<br>1.00x | 5.097<br>1.87x | 8.232<br>3.02x | 3.118<br>1.14x | **0.518<br>0.19x** | 0.528<br>0.19x |
| [grid/superdeep/100](plots/grid/superdeep-100.svg) | 101 | 0.088<br>1.00x | 0.217<br>2.46x | 0.470<br>5.34x | 0.472<br>5.36x | 0.011<br>0.12x | **0.010<br>0.12x** |
| [pangui/expand_with_max_constraint](plots/pangui/expand-with-max-constraint.svg) | 3001 | 1.175<br>1.00x | 1.835<br>1.56x | 3.150<br>2.68x | 1.885<br>1.60x | **0.189<br>0.16x** | 0.191<br>0.16x |
| [pangui/expand_with_min_constraint](plots/pangui/expand-with-min-constraint.svg) | 3001 | 1.164<br>1.00x | 1.845<br>1.58x | 3.154<br>2.71x | 1.881<br>1.62x | **0.188<br>0.16x** | 0.194<br>0.17x |
| [pangui/fit_nesting](plots/pangui/fit-nesting.svg) | 101111 | 39.509<br>1.00x | 90.739<br>2.30x | 88.287<br>2.23x | 31.298<br>0.79x | **8.993<br>0.23x** | 9.375<br>0.24x |
| [pangui/flex_expand_equal_weights](plots/pangui/flex-expand-equal-weights.svg) | 15001 | 5.446<br>1.00x | 11.407<br>2.09x | 13.234<br>2.43x | 13.325<br>2.45x | 1.578<br>0.29x | **1.544<br>0.28x** |
| [pangui/flex_expand_weights](plots/pangui/flex-expand-weights.svg) | 15001 | 5.464<br>1.00x | 10.069<br>1.84x | 18.015<br>3.30x | 9.619<br>1.76x | 1.066<br>0.20x | **1.008<br>0.18x** |
| [pangui/nested_vertical_stack](plots/pangui/nested-vertical-stack.svg) | 10001 | 3.469<br>1.00x | 6.939<br>2.00x | 10.003<br>2.88x | 8.987<br>2.59x | **0.999<br>0.29x** | 1.021<br>0.29x |
| [pangui/padding_and_margin](plots/pangui/padding-and-margin.svg) | 101 | 0.056<br>1.00x | 0.107<br>1.91x | 0.166<br>2.96x | 0.196<br>3.50x | **0.006<br>0.10x** | 0.007<br>0.12x |
| [pangui/percentage_and_ratio](plots/pangui/percentage-and-ratio.svg) | 10001 | 3.802<br>1.00x | 6.994<br>1.84x | 9.843<br>2.59x | 8.734<br>2.30x | 1.000<br>0.26x | **0.968<br>0.25x** |
| [pangui/perpendicular_expand_with_wrap](plots/pangui/perpendicular-expand-with-wrap.svg) | 12001 | 4.203<br>1.00x | 8.431<br>2.01x | 10.241<br>2.44x | 10.962<br>2.61x | 1.219<br>0.29x | **1.179<br>0.28x** |
| [pangui/pixels_with_min_expand_constraint](plots/pangui/pixels-with-min-expand-constraint.svg) | 30001 | 11.817<br>1.00x | 22.582<br>1.91x | 36.379<br>3.08x | 19.072<br>1.61x | 2.177<br>0.18x | **2.116<br>0.18x** |
| [pangui/wide_no_wrap_simple_few](plots/pangui/wide-no-wrap-simple-few.svg) | 1001 | 0.355<br>1.00x | 0.627<br>1.77x | 0.795<br>2.24x | 0.820<br>2.31x | 0.050<br>0.14x | **0.049<br>0.14x** |
| [pangui/wide_no_wrap_simple_many](plots/pangui/wide-no-wrap-simple-many.svg) | 100001 | 36.267<br>1.00x | 94.998<br>2.62x | 128.094<br>3.53x | 88.956<br>2.45x | **12.773<br>0.35x** | 13.714<br>0.38x |
| [pangui/wide_wrapping](plots/pangui/wide-wrapping.svg) | 10001 | 3.673<br>1.00x | 6.962<br>1.90x | 10.249<br>2.79x | 8.913<br>2.43x | 0.999<br>0.27x | **0.972<br>0.26x** |
| [text/paragraphs/100](plots/text/paragraphs-100.svg) | 101 | **0.077<br>1.00x** | 0.169<br>2.20x | 14.976<br>194.50x | 14.217<br>184.63x | 8.618<br>111.92x | 1.312<br>17.04x |
| [text/flex_cards/100](plots/text/flex-cards-100.svg) | 301 | **0.166<br>1.00x** | 0.360<br>2.17x | 5.928<br>35.71x | 4.448<br>26.79x | 3.093<br>18.63x | 0.656<br>3.95x |
| [text/inline_mixed/100](plots/text/inline-mixed-100.svg) | 1599 | **0.981<br>1.00x** | 2.132<br>2.17x | 21.351<br>21.76x | 13.019<br>13.27x | 12.091<br>12.33x | 2.779<br>2.83x |
| [text/paragraphs/1000](plots/text/paragraphs-1000.svg) | 1001 | **0.571<br>1.00x** | 1.226<br>2.15x | 144.057<br>252.29x | 133.757<br>234.25x | 84.963<br>148.80x | 11.608<br>20.33x |
| [text/flex_cards/1000](plots/text/flex-cards-1000.svg) | 3001 | **1.477<br>1.00x** | 3.034<br>2.05x | 54.562<br>36.94x | 38.264<br>25.91x | 30.583<br>20.71x | 5.750<br>3.89x |
| [text/inline_mixed/1000](plots/text/inline-mixed-1000.svg) | 16361 | **10.180<br>1.00x** | 22.403<br>2.20x | 215.965<br>21.21x | 111.050<br>10.91x | 120.339<br>11.82x | 23.058<br>2.27x |
| [real/wikipedia](plots/real/wikipedia.svg) | 21889 | 19.871<br>1.00x | 55.653<br>2.80x | 186.082<br>9.36x | 69.710<br>3.51x | 60.323<br>3.04x | **15.862<br>0.80x** |
| [real/wikipedia@1024](plots/real/wikipedia-1024.svg) | 21889 | 19.885<br>1.00x | 55.373<br>2.78x | 184.972<br>9.30x | 70.019<br>3.52x | 60.461<br>3.04x | **14.555<br>0.73x** |
| [real/mdn](plots/real/mdn.svg) | 2212 | **1.405<br>1.00x** | 4.245<br>3.02x | 13.283<br>9.45x | 6.392<br>4.55x | 5.678<br>4.04x | 2.080<br>1.48x |
| [real/mdn@1024](plots/real/mdn-1024.svg) | 2212 | **0.835<br>1.00x** | 2.803<br>3.36x | 10.915<br>13.07x | 6.749<br>8.08x | 4.482<br>5.37x | 1.945<br>2.33x |
| [real/rustdoc](plots/real/rustdoc.svg) | 15947 | 12.679<br>1.00x | 33.758<br>2.66x | 112.826<br>8.90x | 47.535<br>3.75x | 49.542<br>3.91x | **11.697<br>0.92x** |
| [real/css-flexbox-1](plots/real/css-flexbox-1.svg) | 15890 | **10.785<br>1.00x** | 40.147<br>3.72x | 117.219<br>10.87x | 59.967<br>5.56x | 58.625<br>5.44x | 16.125<br>1.50x |
| [real/servo-org](plots/real/servo-org.svg) | 226 | **0.218<br>1.00x** | 0.712<br>3.27x | 3.612<br>16.57x | 2.917<br>13.38x | 0.811<br>3.72x | 0.502<br>2.30x |
| [real/servo-org@1024](plots/real/servo-org-1024.svg) | 226 | **0.212<br>1.00x** | 0.700<br>3.30x | 3.583<br>16.90x | 2.534<br>11.95x | 0.808<br>3.81x | 0.436<br>2.05x |
| [real/dioxuslabs-com](plots/real/dioxuslabs-com.svg) | 158 | **0.165<br>1.00x** | 0.239<br>1.45x | 3.062<br>18.56x | 3.758<br>22.78x | 0.320<br>1.94x | 0.262<br>1.59x |
| [real/dioxuslabs-com@1024](plots/real/dioxuslabs-com-1024.svg) | 158 | **0.165<br>1.00x** | 0.246<br>1.49x | 3.076<br>18.65x | 3.942<br>23.89x | 0.329<br>1.99x | 0.381<br>2.31x |
| [real/bootstrap-dashboard](plots/real/bootstrap-dashboard.svg) | 199 | 0.190<br>1.00x | **0.030<br>0.16x** | 2.037<br>10.72x | 1.923<br>10.12x | 0.464<br>2.44x | 0.498<br>2.62x |
| [real/bootstrap-dashboard@1024](plots/real/bootstrap-dashboard-1024.svg) | 199 | 0.187<br>1.00x | **0.029<br>0.15x** | 2.015<br>10.78x | 1.807<br>9.66x | 0.464<br>2.48x | 0.376<br>2.01x |

### Box construction + layout

| case | nodes | Chrome<br>rebuildLayoutTree + Layout | Firefox(1)<br>Reflow | Firefox<br>Reflow | Ladybird<br>tree build + layout | Servo(1)<br>Box + Fragment | Servo(3)<br>Box + Fragment | Blitz<br>construct + layout | Blitz<br>construct + layout (parallel construct) | Blitz<br>construct + layout (parallel construct + layout) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [flex/huge_nested/1000](plots/flex/huge-nested-1000.svg) | 911 | 1.238<br>1.00x | 1.277<br>1.03x | 1.339<br>1.08x | 5.113<br>4.13x | 2.084<br>1.68x | 1.308<br>1.06x | 0.661<br>0.53x | 0.670<br>0.54x | **0.618<br>0.50x** |
| [flex/wide/1000](plots/flex/wide-1000.svg) | 1000 | 1.612<br>1.00x | 2.085<br>1.29x | 2.174<br>1.35x | 6.929<br>4.30x | 2.739<br>1.70x | 2.384<br>1.48x | 1.103<br>0.68x | 1.116<br>0.69x | **0.932<br>0.58x** |
| [flex/absolute/1000](plots/flex/absolute-1000.svg) | 1003 | 1.875<br>1.00x | 2.439<br>1.30x | 2.460<br>1.31x | 4.849<br>2.59x | 2.632<br>1.40x | 2.176<br>1.16x | **0.819<br>0.44x** | 0.870<br>0.46x | 0.956<br>0.51x |
| [flex/deep_auto/1000](plots/flex/deep-auto-1000.svg) | 767 | 1.949<br>1.00x | 1.194<br>0.61x | 1.217<br>0.62x | 7.535<br>3.87x | 2.753<br>1.41x | 2.622<br>1.35x | 1.762<br>0.90x | 1.747<br>0.90x | **0.683<br>0.35x** |
| [flex/deep_random/1000](plots/flex/deep-random-1000.svg) | 767 | 1.199<br>1.00x | 1.562<br>1.30x | 1.644<br>1.37x | 6.214<br>5.18x | 2.373<br>1.98x | 2.309<br>1.93x | 0.821<br>0.68x | 0.818<br>0.68x | **0.549<br>0.46x** |
| [flex/huge_nested/10000](plots/flex/huge-nested-10000.svg) | 9111 | 12.321<br>1.00x | 12.047<br>0.98x | 13.053<br>1.06x | 50.896<br>4.13x | 19.948<br>1.62x | 10.406<br>0.84x | 6.806<br>0.55x | 6.991<br>0.57x | **2.857<br>0.23x** |
| [flex/wide/10000](plots/flex/wide-10000.svg) | 10001 | 16.229<br>1.00x | 20.823<br>1.28x | 22.130<br>1.36x | 75.922<br>4.68x | 26.688<br>1.64x | 23.077<br>1.42x | 11.857<br>0.73x | 12.005<br>0.74x | **8.139<br>0.50x** |
| [flex/absolute/10000](plots/flex/absolute-10000.svg) | 10004 | 19.759<br>1.00x | 24.045<br>1.22x | 24.398<br>1.23x | 55.028<br>2.78x | 26.632<br>1.35x | 22.539<br>1.14x | 8.752<br>0.44x | 8.807<br>0.45x | **7.215<br>0.37x** |
| [flex/deep_auto/10000](plots/flex/deep-auto-10000.svg) | 8191 | 20.912<br>1.00x | 12.149<br>0.58x | 12.456<br>0.60x | 70.017<br>3.35x | 26.927<br>1.29x | 27.702<br>1.32x | 18.706<br>0.89x | 18.468<br>0.88x | **4.983<br>0.24x** |
| [flex/deep_random/10000](plots/flex/deep-random-10000.svg) | 8191 | 11.927<br>1.00x | 15.741<br>1.32x | 16.538<br>1.39x | 61.353<br>5.14x | 22.579<br>1.89x | 23.499<br>1.97x | 8.817<br>0.74x | 8.712<br>0.73x | **4.077<br>0.34x** |
| [flex/superdeep/50](plots/flex/superdeep-50.svg) | 151 | 0.528<br>1.00x | 0.492<br>0.93x | 0.494<br>0.94x | 1.865<br>3.53x | 0.682<br>1.29x | 0.663<br>1.26x | 0.327<br>0.62x | **0.312<br>0.59x** | 0.711<br>1.35x |
| [flex/superdeep/100](plots/flex/superdeep-100.svg) | 301 | 1.048<br>1.00x | 0.940<br>0.90x | 0.942<br>0.90x | 3.478<br>3.32x | 1.341<br>1.28x | 1.257<br>1.20x | 0.631<br>0.60x | **0.626<br>0.60x** | 1.343<br>1.28x |
| [grid/wide/31x31](plots/grid/wide-31x31.svg) | 962 | 2.946<br>1.00x | 2.855<br>0.97x | 2.924<br>0.99x | 6.166<br>2.09x | 3.715<br>1.26x | 3.703<br>1.26x | **1.494<br>0.51x** | 1.513<br>0.51x | 1.960<br>0.67x |
| [grid/wide/100x100](plots/grid/wide-100x100.svg) | 10001 | 39.466<br>1.00x | 33.456<br>0.85x | 33.561<br>0.85x | 73.232<br>1.86x | 40.281<br>1.02x | 40.285<br>1.02x | 16.890<br>0.43x | **16.434<br>0.42x** | 23.069<br>0.58x |
| [grid/deep/2x2x5](plots/grid/deep-2x2x5.svg) | 1365 | 7.565<br>1.00x | 10.915<br>1.44x | 10.951<br>1.45x | 14.686<br>1.94x | 17.154<br>2.27x | 16.402<br>2.17x | 3.598<br>0.48x | 3.574<br>0.47x | **1.596<br>0.21x** |
| [grid/deep/3x3x4](plots/grid/deep-3x3x4.svg) | 7381 | 32.832<br>1.00x | 43.506<br>1.33x | 44.362<br>1.35x | 76.115<br>2.32x | 71.413<br>2.18x | 66.724<br>2.03x | 16.776<br>0.51x | 16.741<br>0.51x | **5.863<br>0.18x** |
| [grid/superdeep/100](plots/grid/superdeep-100.svg) | 101 | 1.587<br>1.00x | 10.743<br>6.77x | 10.664<br>6.72x | 2.717<br>1.71x | 204.976<br>129.16x | 197.826<br>124.65x | 0.484<br>0.30x | **0.470<br>0.30x** | 0.606<br>0.38x |
| [pangui/expand_with_max_constraint](plots/pangui/expand-with-max-constraint.svg) | 3001 | 4.750<br>1.00x | 4.222<br>0.89x | 4.396<br>0.93x | 12.221<br>2.57x | 8.508<br>1.79x | 7.382<br>1.55x | 3.534<br>0.74x | 3.521<br>0.74x | **2.505<br>0.53x** |
| [pangui/expand_with_min_constraint](plots/pangui/expand-with-min-constraint.svg) | 3001 | 4.736<br>1.00x | 4.037<br>0.85x | 4.063<br>0.86x | 12.033<br>2.54x | 8.530<br>1.80x | 7.203<br>1.52x | 3.519<br>0.74x | 3.527<br>0.74x | **2.389<br>0.50x** |
| [pangui/fit_nesting](plots/pangui/fit-nesting.svg) | 101111 | 167.505<br>1.00x | 123.095<br>0.73x | 129.757<br>0.77x | 461.121<br>2.75x | 557.658<br>3.33x | 269.350<br>1.61x | 88.505<br>0.53x | 90.517<br>0.54x | **33.072<br>0.20x** |
| [pangui/flex_expand_equal_weights](plots/pangui/flex-expand-equal-weights.svg) | 15001 | 17.535<br>1.00x | 20.727<br>1.18x | 22.194<br>1.27x | 55.534<br>3.17x | 28.964<br>1.65x | 30.549<br>1.74x | 8.823<br>0.50x | **8.662<br>0.49x** | 10.453<br>0.60x |
| [pangui/flex_expand_weights](plots/pangui/flex-expand-weights.svg) | 15001 | 16.063<br>1.00x | 32.129<br>2.00x | 32.948<br>2.05x | 47.376<br>2.95x | 37.487<br>2.33x | 30.232<br>1.88x | 12.133<br>0.76x | 11.841<br>0.74x | **7.493<br>0.47x** |
| [pangui/nested_vertical_stack](plots/pangui/nested-vertical-stack.svg) | 10001 | 10.734<br>1.00x | 20.196<br>1.88x | 21.412<br>1.99x | 41.635<br>3.88x | 24.347<br>2.27x | 24.010<br>2.24x | **8.141<br>0.76x** | 8.211<br>0.76x | 9.331<br>0.87x |
| [pangui/padding_and_margin](plots/pangui/padding-and-margin.svg) | 101 | 0.194<br>1.00x | 0.260<br>1.34x | 0.265<br>1.37x | 0.729<br>3.76x | 0.388<br>2.00x | 0.414<br>2.13x | **0.072<br>0.37x** | 0.074<br>0.38x | 0.082<br>0.42x |
| [pangui/percentage_and_ratio](plots/pangui/percentage-and-ratio.svg) | 10001 | 17.374<br>1.00x | 16.293<br>0.94x | 17.118<br>0.99x | 38.020<br>2.19x | 22.211<br>1.28x | 21.688<br>1.25x | 6.594<br>0.38x | **6.448<br>0.37x** | 6.822<br>0.39x |
| [pangui/perpendicular_expand_with_wrap](plots/pangui/perpendicular-expand-with-wrap.svg) | 12001 | 17.952<br>1.00x | 20.979<br>1.17x | 22.577<br>1.26x | 48.242<br>2.69x | 1528.515<br>85.14x | 1507.146<br>83.95x | 12.858<br>0.72x | **12.375<br>0.69x** | 14.277<br>0.80x |
| [pangui/pixels_with_min_expand_constraint](plots/pangui/pixels-with-min-expand-constraint.svg) | 30001 | 48.396<br>1.00x | 43.196<br>0.89x | 42.796<br>0.88x | 139.188<br>2.88x | 89.403<br>1.85x | 75.572<br>1.56x | 35.676<br>0.74x | 34.658<br>0.72x | **19.387<br>0.40x** |
| [pangui/wide_no_wrap_simple_few](plots/pangui/wide-no-wrap-simple-few.svg) | 1001 | 1.127<br>1.00x | 1.348<br>1.20x | 1.398<br>1.24x | 3.141<br>2.79x | 1.889<br>1.68x | 1.978<br>1.76x | 0.566<br>0.50x | **0.559<br>0.50x** | 0.888<br>0.79x |
| [pangui/wide_no_wrap_simple_many](plots/pangui/wide-no-wrap-simple-many.svg) | 100001 | 118.036<br>1.00x | 196.832<br>1.67x | 182.890<br>1.55x | 404.908<br>3.43x | 264.563<br>2.24x | 227.401<br>1.93x | **94.427<br>0.80x** | 98.403<br>0.83x | 103.803<br>0.88x |
| [pangui/wide_wrapping](plots/pangui/wide-wrapping.svg) | 10001 | 12.639<br>1.00x | 13.292<br>1.05x | 15.105<br>1.20x | 39.653<br>3.14x | 431.181<br>34.12x | 430.848<br>34.09x | 8.056<br>0.64x | **7.938<br>0.63x** | 9.889<br>0.78x |
| [text/paragraphs/100](plots/text/paragraphs-100.svg) | 101 | 5.578<br>1.00x | 5.498<br>0.99x | 5.382<br>0.96x | 9.231<br>1.65x | 17.244<br>3.09x | 15.707<br>2.82x | 9.684<br>1.74x | 2.463<br>0.44x | **1.849<br>0.33x** |
| [text/flex_cards/100](plots/text/flex-cards-100.svg) | 301 | 3.792<br>1.00x | 4.585<br>1.21x | 4.421<br>1.17x | 7.083<br>1.87x | 8.017<br>2.11x | 7.087<br>1.87x | 4.319<br>1.14x | 2.059<br>0.54x | **1.096<br>0.29x** |
| [text/inline_mixed/100](plots/text/inline-mixed-100.svg) | 1599 | 10.103<br>1.00x | 12.903<br>1.28x | 13.035<br>1.29x | 21.044<br>2.08x | 28.324<br>2.80x | 16.990<br>1.68x | 13.303<br>1.32x | 4.087<br>0.40x | **2.719<br>0.27x** |
| [text/paragraphs/1000](plots/text/paragraphs-1000.svg) | 1001 | 52.360<br>1.00x | 40.374<br>0.77x | 40.657<br>0.78x | 91.889<br>1.75x | 168.430<br>3.22x | 144.201<br>2.75x | 95.533<br>1.82x | 22.067<br>0.42x | **13.930<br>0.27x** |
| [text/flex_cards/1000](plots/text/flex-cards-1000.svg) | 3001 | 34.691<br>1.00x | 27.813<br>0.80x | 27.942<br>0.81x | 66.449<br>1.92x | 81.877<br>2.36x | 67.680<br>1.95x | 43.118<br>1.24x | 19.058<br>0.55x | **9.437<br>0.27x** |
| [text/inline_mixed/1000](plots/text/inline-mixed-1000.svg) | 16361 | 94.366<br>1.00x | 91.998<br>0.97x | 91.763<br>0.97x | 208.493<br>2.21x | 260.951<br>2.77x | 129.469<br>1.37x | 132.523<br>1.40x | 35.139<br>0.37x | **24.629<br>0.26x** |
| [real/wikipedia](plots/real/wikipedia.svg) | 21889 | 175.695<br>1.00x | 176.115<br>1.00x | 174.135<br>0.99x | 462.356<br>2.63x | 233.107<br>1.33x | 116.792<br>0.66x | 80.449<br>0.46x | **35.570<br>0.20x** | 37.835<br>0.22x |
| [real/wikipedia@1024](plots/real/wikipedia-1024.svg) | 21889 | 182.127<br>1.00x | 304.901<br>1.67x | 304.624<br>1.67x | 416.764<br>2.29x | 230.984<br>1.27x | 116.367<br>0.64x | 74.935<br>0.41x | **29.511<br>0.16x** | 30.955<br>0.17x |
| [real/mdn](plots/real/mdn.svg) | 2212 | 12.581<br>1.00x | 12.893<br>1.02x | 12.802<br>1.02x | 50.343<br>4.00x | 20.883<br>1.66x | 9.598<br>0.76x | 9.229<br>0.73x | 5.742<br>0.46x | **3.968<br>0.32x** |
| [real/mdn@1024](plots/real/mdn-1024.svg) | 2212 | 8.507<br>1.00x | 10.531<br>1.24x | 10.339<br>1.22x | 38.020<br>4.47x | 19.785<br>2.33x | 11.565<br>1.36x | 6.730<br>0.79x | 4.243<br>0.50x | **2.404<br>0.28x** |
| [real/rustdoc](plots/real/rustdoc.svg) | 15947 | 101.098<br>1.00x | 84.159<br>0.83x | 82.727<br>0.82x | 395.031<br>3.91x | 158.493<br>1.57x | 89.143<br>0.88x | 74.738<br>0.74x | 36.763<br>0.36x | **33.900<br>0.34x** |
| [real/css-flexbox-1](plots/real/css-flexbox-1.svg) | 15890 | 98.079<br>1.00x | 94.019<br>0.96x | 95.404<br>0.97x | 240.688<br>2.45x | 161.404<br>1.65x | 102.152<br>1.04x | 83.309<br>0.85x | 42.334<br>0.43x | **40.735<br>0.42x** |
| [real/servo-org](plots/real/servo-org.svg) | 226 | 2.418<br>1.00x | 4.478<br>1.85x | 4.445<br>1.84x | 5.259<br>2.17x | 5.790<br>2.39x | 4.614<br>1.91x | 1.244<br>0.51x | 1.131<br>0.47x | **0.770<br>0.32x** |
| [real/servo-org@1024](plots/real/servo-org-1024.svg) | 226 | 2.399<br>1.00x | 4.447<br>1.85x | 4.844<br>2.02x | 5.310<br>2.21x | 5.421<br>2.26x | 3.417<br>1.42x | 1.244<br>0.52x | 0.905<br>0.38x | **0.881<br>0.37x** |
| [real/dioxuslabs-com](plots/real/dioxuslabs-com.svg) | 158 | 3.197<br>1.00x | 4.986<br>1.56x | 5.012<br>1.57x | 16.165<br>5.06x | 5.638<br>1.76x | 4.698<br>1.47x | 0.760<br>0.24x | 0.750<br>0.23x | **0.641<br>0.20x** |
| [real/dioxuslabs-com@1024](plots/real/dioxuslabs-com-1024.svg) | 158 | 3.451<br>1.00x | 4.967<br>1.44x | 4.984<br>1.44x | 16.174<br>4.69x | 5.887<br>1.71x | 4.616<br>1.34x | **0.767<br>0.22x** | 0.933<br>0.27x | 1.027<br>0.30x |
| [real/bootstrap-dashboard](plots/real/bootstrap-dashboard.svg) | 199 | 1.840<br>1.00x | 2.210<br>1.20x | 2.377<br>1.29x | 2.940<br>1.60x | 3.634<br>1.97x | 3.181<br>1.73x | **1.066<br>0.58x** | 1.110<br>0.60x | 1.096<br>0.60x |
| [real/bootstrap-dashboard@1024](plots/real/bootstrap-dashboard-1024.svg) | 199 | 1.876<br>1.00x | 2.348<br>1.25x | 2.398<br>1.28x | 3.135<br>1.67x | 3.658<br>1.95x | 2.665<br>1.42x | 1.074<br>0.57x | 1.161<br>0.62x | **1.006<br>0.54x** |

### Style

| case | nodes | Chrome<br>recalcStyle | Firefox(1)<br>Styles (incl. frame construction) | Firefox<br>Styles (incl. frame construction) | Ladybird<br>update_style | Servo(1)<br>Styling | Servo(3)<br>Styling | Blitz<br>style | Blitz<br>style (parallel) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [flex/huge_nested/1000](plots/flex/huge-nested-1000.svg) | 911 | 1.467<br>1.00x | 4.271<br>2.91x | 1.818<br>1.24x | 28.907<br>19.70x | 6.794<br>4.63x | 5.307<br>3.62x | 2.239<br>1.53x | **0.881<br>0.60x** |
| [flex/wide/1000](plots/flex/wide-1000.svg) | 1000 | 1.356<br>1.00x | 4.084<br>3.01x | 2.203<br>1.62x | 32.478<br>23.95x | 6.084<br>4.49x | 3.531<br>2.60x | 1.948<br>1.44x | **1.089<br>0.80x** |
| [flex/absolute/1000](plots/flex/absolute-1000.svg) | 1003 | 1.598<br>1.00x | 4.330<br>2.71x | 2.472<br>1.55x | 38.063<br>23.82x | 6.443<br>4.03x | 3.659<br>2.29x | 2.074<br>1.30x | **1.187<br>0.74x** |
| [flex/deep_auto/1000](plots/flex/deep-auto-1000.svg) | 767 | 0.804<br>1.00x | 1.691<br>2.10x | 0.878<br>1.09x | 16.374<br>20.37x | 3.275<br>4.07x | 1.978<br>2.46x | 0.950<br>1.18x | **0.506<br>0.63x** |
| [flex/deep_random/1000](plots/flex/deep-random-1000.svg) | 767 | 0.951<br>1.00x | 2.415<br>2.54x | 1.730<br>1.82x | 23.626<br>24.84x | 6.553<br>6.89x | 2.232<br>2.35x | 1.249<br>1.31x | **0.797<br>0.84x** |
| [flex/huge_nested/10000](plots/flex/huge-nested-10000.svg) | 9111 | 14.234<br>1.00x | 43.555<br>3.06x | 15.987<br>1.12x | 259.575<br>18.24x | 61.187<br>4.30x | 56.396<br>3.96x | 22.496<br>1.58x | **8.131<br>0.57x** |
| [flex/wide/10000](plots/flex/wide-10000.svg) | 10001 | 12.992<br>1.00x | 41.522<br>3.20x | 18.121<br>1.39x | 314.202<br>24.18x | 52.860<br>4.07x | 34.064<br>2.62x | 19.224<br>1.48x | **9.593<br>0.74x** |
| [flex/absolute/10000](plots/flex/absolute-10000.svg) | 10004 | 15.681<br>1.00x | 45.639<br>2.91x | 20.304<br>1.29x | 357.634<br>22.81x | 53.318<br>3.40x | 33.260<br>2.12x | 20.029<br>1.28x | **10.016<br>0.64x** |
| [flex/deep_auto/10000](plots/flex/deep-auto-10000.svg) | 8191 | 10.200<br>1.00x | 24.404<br>2.39x | 9.294<br>0.91x | 169.786<br>16.65x | 34.876<br>3.42x | 30.703<br>3.01x | 13.784<br>1.35x | **5.331<br>0.52x** |
| [flex/deep_random/10000](plots/flex/deep-random-10000.svg) | 8191 | 9.781<br>1.00x | 30.519<br>3.12x | 14.474<br>1.48x | 233.245<br>23.85x | 37.167<br>3.80x | 19.862<br>2.03x | 14.192<br>1.45x | **8.284<br>0.85x** |
| [flex/superdeep/50](plots/flex/superdeep-50.svg) | 151 | 0.301<br>1.00x | 0.469<br>1.56x | 0.469<br>1.56x | 7.010<br>23.29x | 0.916<br>3.04x | 0.911<br>3.02x | 0.264<br>0.88x | **0.264<br>0.88x** |
| [flex/superdeep/100](plots/flex/superdeep-100.svg) | 301 | 0.535<br>1.00x | 0.858<br>1.60x | 0.871<br>1.63x | 10.603<br>19.82x | 1.648<br>3.08x | 1.591<br>2.97x | 0.514<br>0.96x | **0.507<br>0.95x** |
| [grid/wide/31x31](plots/grid/wide-31x31.svg) | 962 | 1.200<br>1.00x | 4.634<br>3.86x | 2.229<br>1.86x | 31.587<br>26.32x | 8.289<br>6.91x | 6.400<br>5.33x | 2.238<br>1.86x | **1.049<br>0.87x** |
| [grid/wide/100x100](plots/grid/wide-100x100.svg) | 10001 | 12.464<br>1.00x | 51.419<br>4.13x | 20.532<br>1.65x | 342.121<br>27.45x | 72.075<br>5.78x | 74.373<br>5.97x | 23.293<br>1.87x | **10.035<br>0.81x** |
| [grid/deep/2x2x5](plots/grid/deep-2x2x5.svg) | 1365 | 2.183<br>1.00x | 5.212<br>2.39x | 2.659<br>1.22x | 62.731<br>28.74x | 6.779<br>3.11x | 3.839<br>1.76x | 2.536<br>1.16x | **1.410<br>0.65x** |
| [grid/deep/3x3x4](plots/grid/deep-3x3x4.svg) | 7381 | 10.912<br>1.00x | 29.805<br>2.73x | 13.377<br>1.23x | 407.414<br>37.34x | 37.482<br>3.43x | 20.574<br>1.89x | 14.699<br>1.35x | **7.062<br>0.65x** |
| [grid/superdeep/100](plots/grid/superdeep-100.svg) | 101 | 0.205<br>1.00x | 0.310<br>1.51x | 0.324<br>1.58x | 6.063<br>29.58x | 0.594<br>2.90x | 0.605<br>2.95x | **0.162<br>0.79x** | 0.168<br>0.82x |
| [pangui/expand_with_max_constraint](plots/pangui/expand-with-max-constraint.svg) | 3001 | 4.523<br>1.00x | 11.358<br>2.51x | 4.493<br>0.99x | 75.749<br>16.75x | 16.235<br>3.59x | 13.178<br>2.91x | 5.957<br>1.32x | **2.322<br>0.51x** |
| [pangui/expand_with_min_constraint](plots/pangui/expand-with-min-constraint.svg) | 3001 | 4.432<br>1.00x | 11.235<br>2.53x | 4.595<br>1.04x | 75.715<br>17.08x | 16.379<br>3.70x | 13.634<br>3.08x | 6.094<br>1.37x | **2.225<br>0.50x** |
| [pangui/fit_nesting](plots/pangui/fit-nesting.svg) | 101111 | 237.304<br>1.00x | 626.303<br>2.64x | 202.382<br>0.85x | 3456.659<br>14.57x | 817.384<br>3.44x | 699.701<br>2.95x | 348.499<br>1.47x | **110.119<br>0.46x** |
| [pangui/flex_expand_equal_weights](plots/pangui/flex-expand-equal-weights.svg) | 15001 | 29.287<br>1.00x | 91.245<br>3.12x | 32.402<br>1.11x | 605.620<br>20.68x | 116.621<br>3.98x | 105.017<br>3.59x | 44.218<br>1.51x | **15.679<br>0.54x** |
| [pangui/flex_expand_weights](plots/pangui/flex-expand-weights.svg) | 15001 | 21.522<br>1.00x | 61.785<br>2.87x | 22.761<br>1.06x | 423.533<br>19.68x | 79.794<br>3.71x | 65.899<br>3.06x | 31.995<br>1.49x | **10.472<br>0.49x** |
| [pangui/nested_vertical_stack](plots/pangui/nested-vertical-stack.svg) | 10001 | 18.975<br>1.00x | 57.324<br>3.02x | 21.370<br>1.13x | 364.667<br>19.22x | 75.832<br>4.00x | 71.753<br>3.78x | 27.780<br>1.46x | **11.704<br>0.62x** |
| [pangui/padding_and_margin](plots/pangui/padding-and-margin.svg) | 101 | 0.279<br>1.00x | 0.577<br>2.07x | 0.315<br>1.13x | 6.602<br>23.66x | 0.951<br>3.41x | 0.729<br>2.61x | 0.306<br>1.10x | **0.183<br>0.66x** |
| [pangui/percentage_and_ratio](plots/pangui/percentage-and-ratio.svg) | 10001 | 21.147<br>1.00x | 59.318<br>2.81x | 22.328<br>1.06x | 372.239<br>17.60x | 76.683<br>3.63x | 70.387<br>3.33x | 29.539<br>1.40x | **9.975<br>0.47x** |
| [pangui/perpendicular_expand_with_wrap](plots/pangui/perpendicular-expand-with-wrap.svg) | 12001 | 23.389<br>1.00x | 66.668<br>2.85x | 25.658<br>1.10x | 460.373<br>19.68x | 87.337<br>3.73x | 84.603<br>3.62x | 29.792<br>1.27x | **12.150<br>0.52x** |
| [pangui/pixels_with_min_expand_constraint](plots/pangui/pixels-with-min-expand-constraint.svg) | 30001 | 44.239<br>1.00x | 130.786<br>2.96x | 43.821<br>0.99x | 984.958<br>22.26x | 164.580<br>3.72x | 131.272<br>2.97x | 64.711<br>1.46x | **20.508<br>0.46x** |
| [pangui/wide_no_wrap_simple_few](plots/pangui/wide-no-wrap-simple-few.svg) | 1001 | 1.984<br>1.00x | 5.865<br>2.96x | 2.449<br>1.23x | 34.910<br>17.60x | 7.939<br>4.00x | 7.366<br>3.71x | 3.015<br>1.52x | **1.090<br>0.55x** |
| [pangui/wide_no_wrap_simple_many](plots/pangui/wide-no-wrap-simple-many.svg) | 100001 | 229.721<br>1.00x | 625.299<br>2.72x | 223.745<br>0.97x | 12901.643<br>56.16x | 785.916<br>3.42x | 704.110<br>3.07x | 319.654<br>1.39x | **108.063<br>0.47x** |
| [pangui/wide_wrapping](plots/pangui/wide-wrapping.svg) | 10001 | 19.667<br>1.00x | 58.563<br>2.98x | 22.016<br>1.12x | 374.526<br>19.04x | 76.783<br>3.90x | 75.734<br>3.85x | 28.332<br>1.44x | **10.102<br>0.51x** |
| [text/paragraphs/100](plots/text/paragraphs-100.svg) | 101 | **0.201<br>1.00x** | 0.548<br>2.73x | 0.402<br>2.00x | 2.863<br>14.24x | 0.623<br>3.10x | 0.603<br>3.00x | 0.275<br>1.37x | 0.254<br>1.26x |
| [text/flex_cards/100](plots/text/flex-cards-100.svg) | 301 | **0.325<br>1.00x** | 0.987<br>3.04x | 0.648<br>1.99x | 4.810<br>14.80x | 1.127<br>3.47x | 0.869<br>2.67x | 0.518<br>1.59x | 0.346<br>1.06x |
| [text/inline_mixed/100](plots/text/inline-mixed-100.svg) | 1599 | 0.811<br>1.00x | 2.386<br>2.94x | 1.694<br>2.09x | 11.928<br>14.71x | 2.102<br>2.59x | 1.686<br>2.08x | 1.037<br>1.28x | **0.771<br>0.95x** |
| [text/paragraphs/1000](plots/text/paragraphs-1000.svg) | 1001 | 1.716<br>1.00x | 5.363<br>3.13x | 2.319<br>1.35x | 22.060<br>12.86x | 6.039<br>3.52x | 7.175<br>4.18x | 2.522<br>1.47x | **1.345<br>0.78x** |
| [text/flex_cards/1000](plots/text/flex-cards-1000.svg) | 3001 | 2.845<br>1.00x | 9.988<br>3.51x | 5.010<br>1.76x | 32.645<br>11.47x | 11.548<br>4.06x | 9.377<br>3.30x | 4.869<br>1.71x | **2.407<br>0.85x** |
| [text/inline_mixed/1000](plots/text/inline-mixed-1000.svg) | 16361 | 7.639<br>1.00x | 24.204<br>3.17x | 15.635<br>2.05x | 104.233<br>13.64x | 23.887<br>3.13x | 18.456<br>2.42x | 10.400<br>1.36x | **5.561<br>0.73x** |
| [real/wikipedia](plots/real/wikipedia.svg) | 21889 | 45.919<br>1.00x | 92.111<br>2.01x | 39.977<br>0.87x | 375.344<br>8.17x | 62.376<br>1.36x | 29.455<br>0.64x | 34.536<br>0.75x | **10.586<br>0.23x** |
| [real/wikipedia@1024](plots/real/wikipedia-1024.svg) | 21889 | 45.687<br>1.00x | 91.834<br>2.01x | 39.739<br>0.87x | 369.067<br>8.08x | 61.839<br>1.35x | 28.939<br>0.63x | 34.654<br>0.76x | **10.769<br>0.24x** |
| [real/mdn](plots/real/mdn.svg) | 2212 | 5.806<br>1.00x | 6.991<br>1.20x | 4.409<br>0.76x | 73.228<br>12.61x | 7.981<br>1.37x | 4.759<br>0.82x | 2.511<br>0.43x | **1.826<br>0.31x** |
| [real/mdn@1024](plots/real/mdn-1024.svg) | 2212 | 3.261<br>1.00x | 3.574<br>1.10x | 2.845<br>0.87x | 37.259<br>11.43x | 2.325<br>0.71x | 1.900<br>0.58x | 1.808<br>0.55x | **1.520<br>0.47x** |
| [real/rustdoc](plots/real/rustdoc.svg) | 15947 | 19.806<br>1.00x | 68.903<br>3.48x | 35.006<br>1.77x | 316.233<br>15.97x | 55.008<br>2.78x | 27.363<br>1.38x | 17.397<br>0.88x | **6.495<br>0.33x** |
| [real/css-flexbox-1](plots/real/css-flexbox-1.svg) | 15890 | 18.077<br>1.00x | 36.705<br>2.03x | 22.900<br>1.27x | 183.607<br>10.16x | 21.847<br>1.21x | 14.124<br>0.78x | 13.875<br>0.77x | **5.785<br>0.32x** |
| [real/servo-org](plots/real/servo-org.svg) | 226 | 0.751<br>1.00x | 1.467<br>1.95x | 1.420<br>1.89x | 15.464<br>20.59x | 1.255<br>1.67x | 1.240<br>1.65x | 0.740<br>0.99x | **0.740<br>0.98x** |
| [real/servo-org@1024](plots/real/servo-org-1024.svg) | 226 | 0.755<br>1.00x | 1.402<br>1.86x | 1.416<br>1.88x | 15.488<br>20.51x | 1.185<br>1.57x | 1.215<br>1.61x | **0.751<br>0.99x** | 0.764<br>1.01x |
| [real/dioxuslabs-com](plots/real/dioxuslabs-com.svg) | 158 | **1.005<br>1.00x** | 1.407<br>1.40x | 1.430<br>1.42x | 18.988<br>18.89x | 1.452<br>1.44x | 1.486<br>1.48x | 1.020<br>1.01x | 1.038<br>1.03x |
| [real/dioxuslabs-com@1024](plots/real/dioxuslabs-com-1024.svg) | 158 | 1.026<br>1.00x | 1.420<br>1.38x | 1.392<br>1.36x | 19.239<br>18.75x | 1.388<br>1.35x | 1.520<br>1.48x | **1.007<br>0.98x** | 1.020<br>0.99x |
| [real/bootstrap-dashboard](plots/real/bootstrap-dashboard.svg) | 199 | **0.760<br>1.00x** | 1.162<br>1.53x | 1.221<br>1.61x | 11.382<br>14.98x | 0.989<br>1.30x | 0.962<br>1.27x | 1.284<br>1.69x | 1.349<br>1.78x |
| [real/bootstrap-dashboard@1024](plots/real/bootstrap-dashboard-1024.svg) | 199 | **0.805<br>1.00x** | 1.286<br>1.60x | 1.264<br>1.57x | 11.361<br>14.11x | 0.995<br>1.24x | 0.981<br>1.22x | 1.212<br>1.51x | 1.244<br>1.55x |

### Whole pipeline (style to laid-out tree)

| case | nodes | Chrome<br>UpdateLayoutTree + Layout | Firefox(1)<br>Styles + Reflow | Firefox<br>Styles + Reflow | Ladybird<br>update_layout() | Servo(1)<br>restyle_and_build_trees | Servo(3)<br>restyle_and_build_trees | Blitz<br>resolve() | Blitz<br>resolve() (parallel style) | Blitz<br>resolve() (parallel style + construct) | Blitz<br>resolve() (parallel style + construct + layout) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [flex/huge_nested/1000](plots/flex/huge-nested-1000.svg) | 911 | 2.767<br>1.00x | 5.583<br>2.02x | 3.234<br>1.17x | 34.727<br>12.55x | 10.179<br>3.68x | 8.469<br>3.06x | 3.007<br>1.09x | 1.822<br>0.66x | 1.801<br>0.65x | **1.563<br>0.56x** |
| [flex/wide/1000](plots/flex/wide-1000.svg) | 1000 | 3.041<br>1.00x | 6.195<br>2.04x | 4.377<br>1.44x | 39.898<br>13.12x | 10.299<br>3.39x | 7.434<br>2.44x | 3.204<br>1.05x | 2.511<br>0.83x | **2.410<br>0.79x** | 2.451<br>0.81x |
| [flex/absolute/1000](plots/flex/absolute-1000.svg) | 1003 | 3.545<br>1.00x | 6.797<br>1.92x | 5.022<br>1.42x | 43.478<br>12.26x | 10.351<br>2.92x | 7.323<br>2.07x | 3.053<br>0.86x | 2.286<br>0.64x | 2.483<br>0.70x | **1.962<br>0.55x** |
| [flex/deep_auto/1000](plots/flex/deep-auto-1000.svg) | 767 | 2.803<br>1.00x | 2.905<br>1.04x | 2.137<br>0.76x | 24.402<br>8.71x | 10.399<br>3.71x | 6.133<br>2.19x | 2.802<br>1.00x | 2.457<br>0.88x | 2.482<br>0.89x | **1.471<br>0.52x** |
| [flex/deep_random/1000](plots/flex/deep-random-1000.svg) | 767 | 2.209<br>1.00x | 3.999<br>1.81x | 3.394<br>1.54x | 30.299<br>13.72x | 11.064<br>5.01x | 5.994<br>2.71x | 2.173<br>0.98x | 1.940<br>0.88x | 1.951<br>0.88x | **1.720<br>0.78x** |
| [flex/huge_nested/10000](plots/flex/huge-nested-10000.svg) | 9111 | 26.681<br>1.00x | 55.780<br>2.09x | 29.112<br>1.09x | 314.819<br>11.80x | 83.664<br>3.14x | 69.611<br>2.61x | 30.591<br>1.15x | 16.779<br>0.63x | 17.228<br>0.65x | **12.602<br>0.47x** |
| [flex/wide/10000](plots/flex/wide-10000.svg) | 10001 | 29.283<br>1.00x | 62.573<br>2.14x | 40.774<br>1.39x | 394.715<br>13.48x | 82.848<br>2.83x | 61.036<br>2.08x | 32.737<br>1.12x | 23.801<br>0.81x | 23.429<br>0.80x | **19.985<br>0.68x** |
| [flex/absolute/10000](plots/flex/absolute-10000.svg) | 10004 | 35.461<br>1.00x | 69.684<br>1.97x | 44.703<br>1.26x | 416.889<br>11.76x | 83.048<br>2.34x | 59.578<br>1.68x | 30.465<br>0.86x | 20.987<br>0.59x | 21.765<br>0.61x | **18.588<br>0.52x** |
| [flex/deep_auto/10000](plots/flex/deep-auto-10000.svg) | 8191 | 31.337<br>1.00x | 36.704<br>1.17x | 22.023<br>0.70x | 244.531<br>7.80x | 64.300<br>2.05x | 61.322<br>1.96x | 33.755<br>1.08x | 25.732<br>0.82x | 25.757<br>0.82x | **11.876<br>0.38x** |
| [flex/deep_random/10000](plots/flex/deep-random-10000.svg) | 8191 | 21.766<br>1.00x | 46.299<br>2.13x | 31.012<br>1.42x | 298.908<br>13.73x | 62.223<br>2.86x | 46.100<br>2.12x | 24.421<br>1.12x | 18.784<br>0.86x | 18.429<br>0.85x | **12.913<br>0.59x** |
| [flex/superdeep/50](plots/flex/superdeep-50.svg) | 151 | 0.887<br>1.00x | 0.965<br>1.09x | 0.968<br>1.09x | 9.092<br>10.25x | 2.929<br>3.30x | 2.890<br>3.26x | 0.628<br>0.71x | **0.603<br>0.68x** | 0.612<br>0.69x | 0.895<br>1.01x |
| [flex/superdeep/100](plots/flex/superdeep-100.svg) | 301 | 1.643<br>1.00x | 1.830<br>1.11x | 1.813<br>1.10x | 14.357<br>8.74x | 4.492<br>2.73x | 4.201<br>2.56x | 1.197<br>0.73x | **1.185<br>0.72x** | 1.188<br>0.72x | 1.804<br>1.10x |
| [grid/wide/31x31](plots/grid/wide-31x31.svg) | 962 | 4.206<br>1.00x | 7.519<br>1.79x | 5.207<br>1.24x | 38.194<br>9.08x | 16.362<br>3.89x | 11.648<br>2.77x | 3.839<br>0.91x | 2.763<br>0.66x | **2.743<br>0.65x** | 3.546<br>0.84x |
| [grid/wide/100x100](plots/grid/wide-100x100.svg) | 10001 | 52.179<br>1.00x | 84.961<br>1.63x | 54.093<br>1.04x | 420.984<br>8.07x | 115.049<br>2.20x | 118.614<br>2.27x | 41.677<br>0.80x | **29.575<br>0.57x** | 29.733<br>0.57x | 31.550<br>0.60x |
| [grid/deep/2x2x5](plots/grid/deep-2x2x5.svg) | 1365 | 9.816<br>1.00x | 16.183<br>1.65x | 13.673<br>1.39x | 78.055<br>7.95x | 25.953<br>2.64x | 21.787<br>2.22x | 6.334<br>0.65x | 5.664<br>0.58x | 5.484<br>0.56x | **3.506<br>0.36x** |
| [grid/deep/3x3x4](plots/grid/deep-3x3x4.svg) | 7381 | 43.876<br>1.00x | 73.490<br>1.67x | 57.924<br>1.32x | 486.598<br>11.09x | 111.365<br>2.54x | 89.974<br>2.05x | 32.562<br>0.74x | 25.031<br>0.57x | 25.616<br>0.58x | **15.382<br>0.35x** |
| [grid/superdeep/100](plots/grid/superdeep-100.svg) | 101 | 1.867<br>1.00x | 11.068<br>5.93x | 11.017<br>5.90x | 9.049<br>4.85x | 208.651<br>111.76x | 199.868<br>107.05x | **0.670<br>0.36x** | 0.682<br>0.37x | 0.682<br>0.37x | 0.713<br>0.38x |
| [pangui/expand_with_max_constraint](plots/pangui/expand-with-max-constraint.svg) | 3001 | 9.329<br>1.00x | 15.579<br>1.67x | 8.912<br>0.96x | 89.601<br>9.60x | 26.293<br>2.82x | 22.573<br>2.42x | 10.213<br>1.09x | 6.591<br>0.71x | 6.752<br>0.72x | **6.098<br>0.65x** |
| [pangui/expand_with_min_constraint](plots/pangui/expand-with-min-constraint.svg) | 3001 | 9.275<br>1.00x | 15.272<br>1.65x | 8.795<br>0.95x | 89.219<br>9.62x | 26.505<br>2.86x | 22.919<br>2.47x | 10.054<br>1.08x | 6.831<br>0.74x | 7.031<br>0.76x | **6.121<br>0.66x** |
| [pangui/fit_nesting](plots/pangui/fit-nesting.svg) | 101111 | 409.979<br>1.00x | 753.416<br>1.84x | 334.590<br>0.82x | 3969.771<br>9.68x | 1394.790<br>3.40x | 994.122<br>2.42x | 465.494<br>1.14x | 228.262<br>0.56x | 212.809<br>0.52x | **169.029<br>0.41x** |
| [pangui/flex_expand_equal_weights](plots/pangui/flex-expand-equal-weights.svg) | 15001 | 47.011<br>1.00x | 112.249<br>2.39x | 54.691<br>1.16x | 667.255<br>14.19x | 149.834<br>3.19x | 140.591<br>2.99x | 55.255<br>1.18x | **26.932<br>0.57x** | 29.108<br>0.62x | 27.838<br>0.59x |
| [pangui/flex_expand_weights](plots/pangui/flex-expand-weights.svg) | 15001 | 37.607<br>1.00x | 94.102<br>2.50x | 55.709<br>1.48x | 478.774<br>12.73x | 121.100<br>3.22x | 102.998<br>2.74x | 46.997<br>1.25x | 25.579<br>0.68x | 26.701<br>0.71x | **21.198<br>0.56x** |
| [pangui/nested_vertical_stack](plots/pangui/nested-vertical-stack.svg) | 10001 | 29.736<br>1.00x | 78.169<br>2.63x | 42.782<br>1.44x | 411.483<br>13.84x | 103.213<br>3.47x | 99.803<br>3.36x | 37.479<br>1.26x | 22.297<br>0.75x | **20.549<br>0.69x** | 21.763<br>0.73x |
| [pangui/padding_and_margin](plots/pangui/padding-and-margin.svg) | 101 | 0.535<br>1.00x | 0.851<br>1.59x | 0.580<br>1.08x | 7.536<br>14.09x | 2.710<br>5.06x | 2.515<br>4.70x | 0.405<br>0.76x | 0.307<br>0.57x | **0.300<br>0.56x** | 0.319<br>0.60x |
| [pangui/percentage_and_ratio](plots/pangui/percentage-and-ratio.svg) | 10001 | 38.544<br>1.00x | 76.015<br>1.97x | 40.023<br>1.04x | 414.354<br>10.75x | 101.585<br>2.64x | 95.712<br>2.48x | 37.690<br>0.98x | 18.786<br>0.49x | **18.563<br>0.48x** | 18.928<br>0.49x |
| [pangui/perpendicular_expand_with_wrap](plots/pangui/perpendicular-expand-with-wrap.svg) | 12001 | 41.363<br>1.00x | 87.691<br>2.12x | 49.326<br>1.19x | 514.259<br>12.43x | 1618.624<br>39.13x | 1604.164<br>38.78x | 44.436<br>1.07x | **27.621<br>0.67x** | 27.982<br>0.68x | 28.152<br>0.68x |
| [pangui/pixels_with_min_expand_constraint](plots/pangui/pixels-with-min-expand-constraint.svg) | 30001 | 92.657<br>1.00x | 173.982<br>1.88x | 86.617<br>0.93x | 1136.327<br>12.26x | 262.743<br>2.84x | 220.810<br>2.38x | 106.101<br>1.15x | 64.314<br>0.69x | 66.081<br>0.71x | **48.624<br>0.52x** |
| [pangui/wide_no_wrap_simple_few](plots/pangui/wide-no-wrap-simple-few.svg) | 1001 | 3.169<br>1.00x | 7.236<br>2.28x | 3.893<br>1.23x | 38.609<br>12.18x | 11.797<br>3.72x | 10.924<br>3.45x | 3.695<br>1.17x | 2.196<br>0.69x | 2.176<br>0.69x | **2.175<br>0.69x** |
| [pangui/wide_no_wrap_simple_many](plots/pangui/wide-no-wrap-simple-many.svg) | 100001 | 350.964<br>1.00x | 823.390<br>2.35x | 406.635<br>1.16x | 13366.166<br>38.08x | 1068.820<br>3.05x | 967.374<br>2.76x | 443.454<br>1.26x | **216.119<br>0.62x** | 224.566<br>0.64x | 233.909<br>0.67x |
| [pangui/wide_wrapping](plots/pangui/wide-wrapping.svg) | 10001 | 32.327<br>1.00x | 71.854<br>2.22x | 37.408<br>1.16x | 419.038<br>12.96x | 511.779<br>15.83x | 511.873<br>15.83x | 37.875<br>1.17x | **20.383<br>0.63x** | 20.929<br>0.65x | 22.051<br>0.68x |
| [text/paragraphs/100](plots/text/paragraphs-100.svg) | 101 | 5.801<br>1.00x | 6.083<br>1.05x | 5.792<br>1.00x | 12.223<br>2.11x | 17.968<br>3.10x | 16.490<br>2.84x | 9.982<br>1.72x | 10.014<br>1.73x | 3.053<br>0.53x | **2.168<br>0.37x** |
| [text/flex_cards/100](plots/text/flex-cards-100.svg) | 301 | 4.132<br>1.00x | 5.572<br>1.35x | 5.130<br>1.24x | 12.120<br>2.93x | 9.263<br>2.24x | 8.075<br>1.95x | 4.890<br>1.18x | 4.856<br>1.18x | 2.648<br>0.64x | **1.625<br>0.39x** |
| [text/inline_mixed/100](plots/text/inline-mixed-100.svg) | 1599 | 10.933<br>1.00x | 15.289<br>1.40x | 14.729<br>1.35x | 33.850<br>3.10x | 30.841<br>2.82x | 19.127<br>1.75x | 14.456<br>1.32x | 14.770<br>1.35x | 4.822<br>0.44x | **4.028<br>0.37x** |
| [text/paragraphs/1000](plots/text/paragraphs-1000.svg) | 1001 | 54.096<br>1.00x | 45.737<br>0.85x | 42.976<br>0.79x | 115.013<br>2.13x | 174.853<br>3.23x | 151.966<br>2.81x | 98.181<br>1.81x | 97.444<br>1.80x | 27.263<br>0.50x | **19.636<br>0.36x** |
| [text/flex_cards/1000](plots/text/flex-cards-1000.svg) | 3001 | 37.563<br>1.00x | 37.801<br>1.01x | 33.105<br>0.88x | 101.105<br>2.69x | 94.177<br>2.51x | 77.960<br>2.08x | 48.515<br>1.29x | 46.836<br>1.25x | 23.716<br>0.63x | **14.540<br>0.39x** |
| [text/inline_mixed/1000](plots/text/inline-mixed-1000.svg) | 16361 | 102.112<br>1.00x | 116.227<br>1.14x | 107.473<br>1.05x | 322.130<br>3.15x | 287.268<br>2.81x | 150.013<br>1.47x | 144.319<br>1.41x | 148.187<br>1.45x | 46.798<br>0.46x | **36.740<br>0.36x** |
| [real/wikipedia](plots/real/wikipedia.svg) | 21889 | 223.583<br>1.00x | 268.227<br>1.20x | 215.415<br>0.96x | 855.225<br>3.83x | 299.169<br>1.34x | 148.880<br>0.67x | 117.683<br>0.53x | 95.203<br>0.43x | 54.075<br>0.24x | **48.566<br>0.22x** |
| [real/wikipedia@1024](plots/real/wikipedia-1024.svg) | 21889 | 230.446<br>1.00x | 397.567<br>1.73x | 345.077<br>1.50x | 798.051<br>3.46x | 296.233<br>1.29x | 148.490<br>0.64x | 112.114<br>0.49x | 89.062<br>0.39x | 48.225<br>0.21x | **46.780<br>0.20x** |
| [real/mdn](plots/real/mdn.svg) | 2212 | 18.542<br>1.00x | 20.064<br>1.08x | 17.299<br>0.93x | 125.011<br>6.74x | 32.257<br>1.74x | 15.487<br>0.84x | 12.055<br>0.65x | 11.898<br>0.64x | 7.854<br>0.42x | **6.202<br>0.33x** |
| [real/mdn@1024](plots/real/mdn-1024.svg) | 2212 | 11.910<br>1.00x | 14.122<br>1.19x | 13.198<br>1.11x | 76.534<br>6.43x | 22.356<br>1.88x | 14.068<br>1.18x | 8.734<br>0.73x | 8.495<br>0.71x | 5.839<br>0.49x | **4.400<br>0.37x** |
| [real/rustdoc](plots/real/rustdoc.svg) | 15947 | 121.984<br>1.00x | 153.062<br>1.25x | 117.769<br>0.97x | 724.302<br>5.94x | 215.419<br>1.77x | 119.897<br>0.98x | 94.735<br>0.78x | 83.190<br>0.68x | 45.263<br>0.37x | **44.947<br>0.37x** |
| [real/css-flexbox-1](plots/real/css-flexbox-1.svg) | 15890 | 117.134<br>1.00x | 130.729<br>1.12x | 119.073<br>1.02x | 442.204<br>3.78x | 185.037<br>1.58x | 118.448<br>1.01x | 100.499<br>0.86x | 92.439<br>0.79x | 48.915<br>0.42x | **47.997<br>0.41x** |
| [real/servo-org](plots/real/servo-org.svg) | 226 | 3.192<br>1.00x | 5.959<br>1.87x | 5.867<br>1.84x | 20.932<br>6.56x | 7.156<br>2.24x | 5.965<br>1.87x | 2.046<br>0.64x | 2.049<br>0.64x | 1.730<br>0.54x | **1.626<br>0.51x** |
| [real/servo-org@1024](plots/real/servo-org-1024.svg) | 226 | 3.177<br>1.00x | 5.890<br>1.85x | 6.310<br>1.99x | 21.074<br>6.63x | 6.798<br>2.14x | 4.733<br>1.49x | 2.047<br>0.64x | 2.107<br>0.66x | 1.786<br>0.56x | **1.585<br>0.50x** |
| [real/dioxuslabs-com](plots/real/dioxuslabs-com.svg) | 158 | 4.226<br>1.00x | 6.442<br>1.52x | 6.441<br>1.52x | 35.370<br>8.37x | 7.274<br>1.72x | 6.278<br>1.49x | 1.828<br>0.43x | 1.845<br>0.44x | 1.795<br>0.42x | **1.643<br>0.39x** |
| [real/dioxuslabs-com@1024](plots/real/dioxuslabs-com-1024.svg) | 158 | 4.494<br>1.00x | 6.482<br>1.44x | 6.389<br>1.42x | 35.636<br>7.93x | 7.420<br>1.65x | 6.604<br>1.47x | 1.820<br>0.40x | 1.828<br>0.41x | 1.744<br>0.39x | **1.626<br>0.36x** |
| [real/bootstrap-dashboard](plots/real/bootstrap-dashboard.svg) | 199 | 2.631<br>1.00x | 3.471<br>1.32x | 3.616<br>1.37x | 15.213<br>5.78x | 4.716<br>1.79x | 4.448<br>1.69x | **2.395<br>0.91x** | 2.805<br>1.07x | 2.465<br>0.94x | 2.863<br>1.09x |
| [real/bootstrap-dashboard@1024](plots/real/bootstrap-dashboard-1024.svg) | 199 | 2.706<br>1.00x | 3.666<br>1.35x | 3.662<br>1.35x | 15.139<br>5.59x | 4.736<br>1.75x | 4.131<br>1.53x | 2.335<br>0.86x | 2.367<br>0.87x | **2.223<br>0.82x** | 2.301<br>0.85x |

### Sample spread

Median ÷ min of the samples behind each cell above (1.00 = all samples equal), per engine on blitz `layout`, blitz-par `style`, blitz-par-pcon `resolve`, blitz-par-pcon-pl `resolve`, blitz-pcon `construct`, blitz-pcon-pl `layout`, blitz-pcon-pl1 `layout`, chrome `layout`, firefox `layout`, firefox1 `layout`, ladybird `layout`, servo `fragment`, servo1 `fragment`, taffy `layout`.

| case | blitz | blitz-par | blitz-par-pcon | blitz-par-pcon-pl | blitz-pcon | blitz-pcon-pl | blitz-pcon-pl1 | chrome | firefox | firefox1 | ladybird | servo | servo1 | taffy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| flex/huge_nested/1000 | 1.03 | 1.46 | 1.17 | 1.21 | 1.06 | 1.53 | 1.04 | 1.02 | 1.07 | 1.09 | 1.03 | 1.09 | 1.05 | 1.02 |
| flex/wide/1000 | 1.02 | 1.12 | 1.14 | 1.22 | 1.09 | 1.89 | 1.16 | 1.02 | 1.07 | 1.07 | 1.02 | 1.03 | 1.06 | 1.02 |
| flex/absolute/1000 | 1.08 | 1.43 | 1.37 | 1.99 | 1.17 | 1.34 | 1.51 | 1.02 | 1.11 | 1.07 | 1.06 | 1.04 | 1.01 | 1.02 |
| flex/deep_auto/1000 | 1.02 | 1.12 | 1.16 | 1.14 | 1.07 | 1.51 | 1.14 | 1.01 | 1.06 | 1.03 | 1.06 | 1.04 | 1.14 | 1.01 |
| flex/deep_random/1000 | 1.03 | 1.37 | 1.14 | 1.13 | 1.13 | 1.32 | 1.03 | 1.02 | 1.03 | 1.05 | 1.01 | 1.12 | 1.04 | 1.01 |
| flex/huge_nested/10000 | 1.11 | 1.30 | 1.14 | 1.20 | 1.13 | 1.34 | 1.10 | 1.01 | 1.02 | 1.08 | 1.01 | 1.04 | 1.06 | 1.00 |
| flex/wide/10000 | 1.07 | 1.24 | 1.11 | 1.19 | 1.08 | 1.22 | 1.04 | 1.04 | 1.02 | 1.14 | 1.01 | 1.06 | 1.03 | 1.00 |
| flex/absolute/10000 | 1.09 | 1.21 | 1.15 | 1.23 | 1.15 | 1.21 | 1.16 | 1.06 | 1.04 | 1.03 | 1.03 | 1.05 | 1.02 | 1.00 |
| flex/deep_auto/10000 | 1.01 | 1.21 | 1.02 | 1.08 | 1.04 | 1.13 | 1.04 | 1.02 | 1.03 | 1.13 | 1.03 | 1.03 | 1.01 | 1.00 |
| flex/deep_random/10000 | 1.17 | 1.16 | 1.07 | 1.18 | 1.20 | 1.10 | 1.04 | 1.17 | 1.09 | 1.04 | 1.03 | 1.11 | 1.04 | 1.00 |
| flex/superdeep/50 | 1.17 | 1.16 | 1.11 | 1.12 | 1.24 | 1.18 | 1.23 | 1.09 | 1.22 | 1.09 | 1.02 | 1.06 | 1.03 | 1.07 |
| flex/superdeep/100 | 1.04 | 1.04 | 1.63 | 1.10 | 1.10 | 1.27 | 1.04 | 1.05 | 1.05 | 1.04 | 1.01 | 1.05 | 1.06 | 1.02 |
| grid/wide/31x31 | 1.02 | 1.26 | 1.16 | 1.20 | 1.05 | 1.68 | 1.37 | 1.04 | 1.03 | 1.02 | 1.01 | 1.02 | 1.04 | 1.01 |
| grid/wide/100x100 | 1.13 | 1.11 | 1.07 | 1.25 | 1.11 | 1.11 | 1.16 | 1.04 | 1.04 | 1.08 | 1.03 | 1.04 | 1.02 | 1.02 |
| grid/deep/2x2x5 | 1.09 | 1.16 | 1.10 | 1.24 | 1.07 | 1.42 | 1.01 | 1.03 | 1.02 | 1.01 | 1.01 | 1.01 | 1.02 | 1.04 |
| grid/deep/3x3x4 | 1.03 | 1.30 | 1.07 | 1.19 | 1.09 | 1.18 | 1.06 | 1.01 | 1.05 | 1.06 | 1.07 | 1.01 | 1.00 | 1.01 |
| grid/superdeep/100 | 1.64 | 1.20 | 1.05 | 1.05 | 1.17 | 1.91 | 1.08 | 1.04 | 1.05 | 1.03 | 1.05 | 1.01 | 1.01 | 1.07 |
| pangui/expand_with_max_constraint | 1.03 | 1.04 | 1.11 | 1.17 | 1.13 | 1.07 | 1.08 | 1.02 | 1.02 | 1.04 | 1.03 | 1.03 | 1.01 | 1.01 |
| pangui/expand_with_min_constraint | 1.06 | 1.46 | 1.16 | 1.31 | 1.06 | 1.23 | 1.01 | 1.04 | 1.04 | 1.03 | 1.10 | 1.07 | 1.02 | 1.01 |
| pangui/fit_nesting | 1.10 | 1.12 | 1.10 | 1.07 | 1.04 | 1.08 | 1.09 | 1.05 | 1.06 | 1.05 | 1.02 | 1.09 | 1.02 | 1.01 |
| pangui/flex_expand_equal_weights | 1.24 | 1.22 | 1.18 | 1.20 | 1.36 | 1.15 | 1.30 | 1.05 | 1.12 | 1.10 | 1.06 | 1.03 | 1.03 | 1.01 |
| pangui/flex_expand_weights | 1.05 | 1.17 | 1.09 | 1.18 | 1.25 | 1.16 | 1.20 | 1.07 | 1.03 | 1.13 | 1.03 | 1.08 | 1.02 | 1.00 |
| pangui/nested_vertical_stack | 1.08 | 1.08 | 1.16 | 1.09 | 1.18 | 1.25 | 1.25 | 1.08 | 1.08 | 1.09 | 1.03 | 1.03 | 1.05 | 1.01 |
| pangui/padding_and_margin | 1.34 | 1.27 | 1.10 | 2.93 | 1.33 | 1.32 | 1.08 | 1.07 | 1.10 | 1.08 | 1.03 | 1.05 | 1.13 | 1.03 |
| pangui/percentage_and_ratio | 1.11 | 1.28 | 1.21 | 1.12 | 1.13 | 1.16 | 1.27 | 1.05 | 1.06 | 1.05 | 1.03 | 1.06 | 1.04 | 1.01 |
| pangui/perpendicular_expand_with_wrap | 1.13 | 1.16 | 1.08 | 1.09 | 1.10 | 1.09 | 1.12 | 1.05 | 1.05 | 1.09 | 1.06 | 1.01 | 1.02 | 1.03 |
| pangui/pixels_with_min_expand_constraint | 1.11 | 1.11 | 1.09 | 1.11 | 1.35 | 1.29 | 1.12 | 1.03 | 1.06 | 1.15 | 1.03 | 1.08 | 1.02 | 1.01 |
| pangui/wide_no_wrap_simple_few | 1.42 | 1.89 | 1.35 | 1.43 | 1.11 | 2.11 | 1.36 | 1.05 | 1.03 | 1.06 | 1.08 | 1.05 | 1.03 | 1.02 |
| pangui/wide_no_wrap_simple_many | 1.09 | 1.09 | 1.10 | 1.06 | 1.07 | 1.18 | 1.25 | 1.05 | 1.22 | 1.08 | 1.06 | 1.06 | 1.09 | 1.03 |
| pangui/wide_wrapping | 1.10 | 1.19 | 1.18 | 1.20 | 1.11 | 1.34 | 1.08 | 1.04 | 1.02 | 1.16 | 1.04 | 1.01 | 1.01 | 1.01 |
| text/paragraphs/100 | 1.01 | 1.30 | 1.13 | 1.04 | 1.53 | 1.51 | 1.02 | 1.01 | 1.04 | 1.03 | 1.01 | 1.44 | 1.12 | - |
| text/flex_cards/100 | 1.02 | 1.37 | 1.20 | 1.18 | 1.25 | 1.52 | 1.17 | 1.09 | 1.10 | 1.04 | 1.01 | 1.59 | 1.11 | - |
| text/inline_mixed/100 | 1.04 | 1.22 | 1.31 | 1.32 | 1.44 | 1.20 | 1.17 | 1.03 | 1.07 | 1.05 | 1.03 | 1.76 | 1.04 | - |
| text/paragraphs/1000 | 1.10 | 1.10 | 1.15 | 1.10 | 1.12 | 1.28 | 1.06 | 1.07 | 1.07 | 1.04 | 1.03 | 1.11 | 1.02 | - |
| text/flex_cards/1000 | 1.10 | 1.04 | 1.15 | 1.14 | 1.16 | 1.17 | 1.19 | 1.03 | 1.08 | 1.04 | 1.03 | 1.04 | 1.04 | - |
| text/inline_mixed/1000 | 1.06 | 1.32 | 1.11 | 1.15 | 1.14 | 1.33 | 1.12 | 1.01 | 1.04 | 1.06 | 1.02 | 1.46 | 1.03 | - |
| real/wikipedia | 1.03 | 1.07 | 1.03 | 1.10 | 1.16 | 1.05 | 1.03 | 1.13 | 1.08 | 1.03 | 1.04 | 1.10 | 1.04 | - |
| real/wikipedia@1024 | 1.08 | 1.12 | 1.07 | 1.15 | 1.45 | 1.15 | 1.05 | 1.11 | 1.04 | 1.06 | 1.04 | 1.02 | 1.02 | - |
| real/mdn | 1.09 | 1.03 | 1.15 | 1.06 | 1.47 | 1.45 | 1.02 | 1.03 | 1.03 | 1.06 | 1.03 | 1.43 | 1.15 | - |
| real/mdn@1024 | 1.00 | 1.07 | 1.09 | 1.24 | 1.31 | 1.21 | 1.17 | 1.03 | 1.04 | 1.02 | 1.04 | 1.29 | 1.19 | - |
| real/rustdoc | 1.06 | 1.09 | 1.11 | 1.05 | 1.10 | 1.01 | 1.09 | 1.06 | 1.06 | 1.06 | 1.03 | 1.02 | 1.05 | - |
| real/css-flexbox-1 | 1.06 | 1.13 | 1.18 | 1.15 | 1.24 | 1.14 | 1.09 | 1.03 | 1.02 | 1.10 | 1.04 | 1.07 | 1.02 | - |
| real/servo-org | 1.04 | 1.04 | 1.02 | 1.07 | 1.44 | 1.23 | 1.25 | 1.05 | 1.16 | 1.09 | 1.01 | 2.41 | 1.12 | - |
| real/servo-org@1024 | 1.03 | 1.10 | 1.17 | 1.04 | 1.69 | 1.61 | 1.04 | 1.03 | 1.08 | 1.09 | 1.02 | 2.84 | 1.38 | - |
| real/dioxuslabs-com | 1.03 | 1.16 | 1.16 | 1.21 | 2.06 | 1.15 | 1.10 | 1.44 | 1.05 | 1.09 | 1.06 | 2.35 | 1.22 | - |
| real/dioxuslabs-com@1024 | 1.15 | 1.13 | 1.39 | 1.55 | 2.57 | 1.60 | 1.05 | 1.40 | 1.06 | 1.06 | 1.02 | 3.96 | 1.16 | - |
| real/bootstrap-dashboard | 1.05 | 1.69 | 1.30 | 1.24 | 1.90 | 1.52 | 1.02 | 1.06 | 1.03 | 1.06 | 1.08 | 2.89 | 1.38 | - |
| real/bootstrap-dashboard@1024 | 1.02 | 1.34 | 1.35 | 1.35 | 2.09 | 1.57 | 1.03 | 1.04 | 1.03 | 1.13 | 1.07 | 2.00 | 1.12 | - |
| **median case** | 1.07 | 1.16 | 1.14 | 1.17 | 1.15 | 1.24 | 1.09 | 1.04 | 1.05 | 1.06 | 1.03 | 1.06 | 1.04 | 1.01 |
| **p90 case** | 1.18 | 1.43 | 1.35 | 1.36 | 1.71 | 1.61 | 1.27 | 1.11 | 1.11 | 1.13 | 1.07 | 2.35 | 1.16 | 1.04 |
