Times in ms, min over all rounds and iterations; second line of each cell is the multiple of the Chrome column of the same table (1.00x = Chrome); bold = fastest engine of the row, Taffy excluded. Servo(n) = `layout_threads=n`; Firefox(1) = `layout.css.stylo-threads=1` (no style worker threads). Text shaping is in the layout phase of Chrome, Firefox and Ladybird but in the construction phase of Blitz and Servo, so "Layout only" is like-for-like only among Servo/Blitz/Taffy and "Box construction + layout" is the comparable table for text-bearing cases; Firefox's Reflow (shaping + layout; its frame construction is inside Styles) is listed there. Case names link to the case's bar chart; one page of charts per suite: [flex/](plots/flex.md) · [grid/](plots/grid.md) · [pangui/](plots/pangui.md) · [text/](plots/text.md) · [real/](plots/real.md). blitz, blitz-par, blitz-par-pcon, blitz-par-pcon-pl, blitz-pcon, blitz-pcon-pl1, servo, servo1 were measured in a later run and scaled per case by Chrome's stored/new `style+layout` ratio (median 0.94; see README, Versions and methodology): differences under ~10% between those and the other columns are within the normalisation's uncertainty.

### Layout only

| case | nodes | Chrome<br>Layout (incl. shaping) | Ladybird<br>layout (incl. shaping) | Servo(1)<br>Fragment Tree | Servo(3)<br>Fragment Tree | Blitz<br>`layout` | Blitz<br>`layout` (#1034 build, 1 thread) | Blitz<br>`layout` (#1034 build, parallel) | Taffy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [flex/huge_nested/1000](plots/flex/huge-nested-1000.svg) | 911 | 0.912<br>1.00x | 4.527<br>4.96x | 1.131<br>1.24x | 0.772<br>0.85x | 0.595<br>0.65x | 1.031<br>1.13x | **0.351<br>0.38x** | 0.272<br>0.30x |
| [flex/wide/1000](plots/flex/wide-1000.svg) | 1000 | 1.238<br>1.00x | 6.245<br>5.04x | 1.590<br>1.28x | 1.679<br>1.36x | 1.073<br>0.87x | 1.460<br>1.18x | **0.758<br>0.61x** | 0.447<br>0.36x |
| [flex/absolute/1000](plots/flex/absolute-1000.svg) | 1003 | 1.308<br>1.00x | 4.135<br>3.16x | 1.369<br>1.05x | 1.489<br>1.14x | **0.777<br>0.59x** | 1.171<br>0.90x | 0.825<br>0.63x | 0.314<br>0.24x |
| [flex/deep_auto/1000](plots/flex/deep-auto-1000.svg) | 767 | 1.661<br>1.00x | 6.953<br>4.19x | 1.468<br>0.88x | 1.501<br>0.90x | 1.723<br>1.04x | 2.480<br>1.49x | **0.705<br>0.42x** | 0.921<br>0.55x |
| [flex/deep_random/1000](plots/flex/deep-random-1000.svg) | 767 | 0.906<br>1.00x | 5.626<br>6.21x | 1.101<br>1.22x | 1.159<br>1.28x | 0.808<br>0.89x | 1.257<br>1.39x | **0.439<br>0.48x** | 0.405<br>0.45x |
| [flex/huge_nested/10000](plots/flex/huge-nested-10000.svg) | 9111 | 8.736<br>1.00x | 44.358<br>5.08x | 12.021<br>1.38x | 6.865<br>0.79x | 6.184<br>0.71x | 7.382<br>0.85x | **1.972<br>0.23x** | 3.156<br>0.36x |
| [flex/wide/10000](plots/flex/wide-10000.svg) | 10001 | 12.819<br>1.00x | 69.032<br>5.39x | 16.214<br>1.26x | 17.869<br>1.39x | 12.044<br>0.94x | 14.141<br>1.10x | **7.118<br>0.56x** | 5.326<br>0.42x |
| [flex/absolute/10000](plots/flex/absolute-10000.svg) | 10004 | 13.871<br>1.00x | 47.110<br>3.40x | 15.325<br>1.10x | 15.633<br>1.13x | 9.440<br>0.68x | 11.079<br>0.80x | **6.029<br>0.43x** | 4.041<br>0.29x |
| [flex/deep_auto/10000](plots/flex/deep-auto-10000.svg) | 8191 | 17.363<br>1.00x | 63.792<br>3.67x | 16.643<br>0.96x | 17.381<br>1.00x | 17.714<br>1.02x | 22.191<br>1.28x | **4.940<br>0.28x** | 10.020<br>0.58x |
| [flex/deep_random/10000](plots/flex/deep-random-10000.svg) | 8191 | 8.826<br>1.00x | 54.558<br>6.18x | 12.537<br>1.42x | 14.261<br>1.62x | 7.789<br>0.88x | 9.925<br>1.12x | **3.058<br>0.35x** | 4.685<br>0.53x |
| [flex/superdeep/50](plots/flex/superdeep-50.svg) | 151 | 0.441<br>1.00x | 1.668<br>3.78x | 0.327<br>0.74x | 0.334<br>0.76x | **0.289<br>0.66x** | 0.538<br>1.22x | 0.604<br>1.37x | 0.146<br>0.33x |
| [flex/superdeep/100](plots/flex/superdeep-100.svg) | 301 | 0.868<br>1.00x | 3.021<br>3.48x | 0.695<br>0.80x | 0.665<br>0.77x | **0.623<br>0.72x** | 0.847<br>0.98x | 1.321<br>1.52x | 0.291<br>0.33x |
| [grid/wide/31x31](plots/grid/wide-31x31.svg) | 962 | 2.624<br>1.00x | 5.518<br>2.10x | 2.581<br>0.98x | 2.647<br>1.01x | **1.461<br>0.56x** | 2.225<br>0.85x | 2.480<br>0.95x | 0.609<br>0.23x |
| [grid/wide/100x100](plots/grid/wide-100x100.svg) | 10001 | 36.154<br>1.00x | 66.159<br>1.83x | 26.779<br>0.74x | 27.155<br>0.75x | **14.795<br>0.41x** | 20.472<br>0.57x | 17.280<br>0.48x | 8.260<br>0.23x |
| [grid/deep/2x2x5](plots/grid/deep-2x2x5.svg) | 1365 | 7.005<br>1.00x | 13.724<br>1.96x | 7.659<br>1.09x | 7.709<br>1.10x | 3.409<br>0.49x | 5.180<br>0.74x | **1.391<br>0.20x** | 2.526<br>0.36x |
| [grid/deep/3x3x4](plots/grid/deep-3x3x4.svg) | 7381 | 30.085<br>1.00x | 70.957<br>2.36x | 42.178<br>1.40x | 37.167<br>1.24x | 17.097<br>0.57x | 24.004<br>0.80x | **5.852<br>0.19x** | 12.304<br>0.41x |
| [grid/superdeep/100](plots/grid/superdeep-100.svg) | 101 | 1.492<br>1.00x | 2.484<br>1.67x | 1.199<br>0.80x | 1.222<br>0.82x | **0.454<br>0.30x** | 0.616<br>0.41x | 0.482<br>0.32x | 0.341<br>0.23x |
| [pangui/expand_with_max_constraint](plots/pangui/expand-with-max-constraint.svg) | 3001 | 3.575<br>1.00x | 10.350<br>2.90x | 4.968<br>1.39x | 5.078<br>1.42x | 3.392<br>0.95x | 4.104<br>1.15x | **2.337<br>0.65x** | 1.465<br>0.41x |
| [pangui/expand_with_min_constraint](plots/pangui/expand-with-min-constraint.svg) | 3001 | 3.572<br>1.00x | 10.188<br>2.85x | 4.907<br>1.37x | 5.336<br>1.49x | 3.250<br>0.91x | 4.219<br>1.18x | **1.983<br>0.56x** | 1.451<br>0.41x |
| [pangui/fit_nesting](plots/pangui/fit-nesting.svg) | 101111 | 127.996<br>1.00x | 366.543<br>2.86x | 327.991<br>2.56x | 132.453<br>1.03x | 81.815<br>0.64x | 86.364<br>0.67x | **24.243<br>0.19x** | 32.136<br>0.25x |
| [pangui/flex_expand_equal_weights](plots/pangui/flex-expand-equal-weights.svg) | 15001 | 11.974<br>1.00x | 44.127<br>3.69x | 14.445<br>1.21x | 14.974<br>1.25x | **7.112<br>0.59x** | 9.112<br>0.76x | 7.593<br>0.63x | 3.821<br>0.32x |
| [pangui/flex_expand_weights](plots/pangui/flex-expand-weights.svg) | 15001 | 10.599<br>1.00x | 37.216<br>3.51x | 17.287<br>1.63x | 19.175<br>1.81x | 11.088<br>1.05x | 13.260<br>1.25x | **5.404<br>0.51x** | 5.751<br>0.54x |
| [pangui/nested_vertical_stack](plots/pangui/nested-vertical-stack.svg) | 10001 | **7.265<br>1.00x** | 34.590<br>4.76x | 13.816<br>1.90x | 12.945<br>1.78x | 7.367<br>1.01x | 10.224<br>1.41x | 8.726<br>1.20x | 2.552<br>0.35x |
| [pangui/padding_and_margin](plots/pangui/padding-and-margin.svg) | 101 | 0.137<br>1.00x | 0.617<br>4.51x | 0.186<br>1.36x | 0.198<br>1.44x | **0.061<br>0.44x** | 0.074<br>0.54x | 0.087<br>0.64x | 0.019<br>0.14x |
| [pangui/percentage_and_ratio](plots/pangui/percentage-and-ratio.svg) | 10001 | 13.572<br>1.00x | 31.026<br>2.29x | 11.320<br>0.83x | 11.385<br>0.84x | **5.270<br>0.39x** | 7.608<br>0.56x | 5.454<br>0.40x | 2.521<br>0.19x |
| [pangui/perpendicular_expand_with_wrap](plots/pangui/perpendicular-expand-with-wrap.svg) | 12001 | 13.749<br>1.00x | 39.809<br>2.90x | 12.736<br>0.93x | 13.337<br>0.97x | **11.897<br>0.87x** | 15.552<br>1.13x | 12.568<br>0.91x | 3.426<br>0.25x |
| [pangui/pixels_with_min_expand_constraint](plots/pangui/pixels-with-min-expand-constraint.svg) | 30001 | 36.579<br>1.00x | 116.606<br>3.19x | 50.860<br>1.39x | 53.261<br>1.46x | 33.727<br>0.92x | 39.736<br>1.09x | **17.009<br>0.46x** | 15.520<br>0.42x |
| [pangui/wide_no_wrap_simple_few](plots/pangui/wide-no-wrap-simple-few.svg) | 1001 | 0.772<br>1.00x | 2.514<br>3.26x | 1.094<br>1.42x | 1.175<br>1.52x | **0.540<br>0.70x** | 0.718<br>0.93x | 0.689<br>0.89x | 0.182<br>0.24x |
| [pangui/wide_no_wrap_simple_many](plots/pangui/wide-no-wrap-simple-many.svg) | 100001 | 81.769<br>1.00x | 305.512<br>3.74x | 116.316<br>1.42x | 116.166<br>1.42x | 77.126<br>0.94x | 100.535<br>1.23x | **76.459<br>0.94x** | 28.808<br>0.35x |
| [pangui/wide_wrapping](plots/pangui/wide-wrapping.svg) | 10001 | 8.966<br>1.00x | 32.691<br>3.65x | 11.073<br>1.23x | 10.568<br>1.18x | **6.786<br>0.76x** | 9.574<br>1.07x | 8.440<br>0.94x | 2.524<br>0.28x |
| [text/paragraphs/100](plots/text/paragraphs-100.svg) | 101 | 5.490<br>1.00x | 9.051<br>1.65x | 2.407<br>0.44x | 1.377<br>0.25x | 0.703<br>0.13x | 0.843<br>0.15x | **0.216<br>0.04x** | - |
| [text/flex_cards/100](plots/text/flex-cards-100.svg) | 301 | 3.626<br>1.00x | 6.722<br>1.85x | 1.509<br>0.42x | 1.661<br>0.46x | 0.986<br>0.27x | 1.318<br>0.36x | **0.379<br>0.10x** | - |
| [text/inline_mixed/100](plots/text/inline-mixed-100.svg) | 1599 | 9.103<br>1.00x | 18.834<br>2.07x | 4.398<br>0.48x | 2.642<br>0.29x | 0.761<br>0.08x | 0.960<br>0.11x | **0.239<br>0.03x** | - |
| [text/paragraphs/1000](plots/text/paragraphs-1000.svg) | 1001 | 51.783<br>1.00x | 90.645<br>1.75x | 25.148<br>0.49x | 10.965<br>0.21x | 6.313<br>0.12x | 6.561<br>0.13x | **1.777<br>0.03x** | - |
| [text/flex_cards/1000](plots/text/flex-cards-1000.svg) | 3001 | 33.214<br>1.00x | 63.415<br>1.91x | 13.577<br>0.41x | 15.017<br>0.45x | 9.977<br>0.30x | 11.369<br>0.34x | **3.090<br>0.09x** | - |
| [text/inline_mixed/1000](plots/text/inline-mixed-1000.svg) | 16361 | 84.178<br>1.00x | 186.091<br>2.21x | 46.885<br>0.56x | 18.557<br>0.22x | 8.022<br>0.10x | 8.883<br>0.11x | **1.917<br>0.02x** | - |
| [real/wikipedia](plots/real/wikipedia.svg) | 21889 | 155.201<br>1.00x | 403.446<br>2.60x | 45.040<br>0.29x | 37.398<br>0.24x | 16.887<br>0.11x | 18.743<br>0.12x | **14.703<br>0.09x** | - |
| [real/mdn](plots/real/mdn.svg) | 2212 | 11.176<br>1.00x | 45.893<br>4.11x | 5.600<br>0.50x | 2.891<br>0.26x | 3.521<br>0.32x | 4.136<br>0.37x | **1.452<br>0.13x** | - |
| [real/rustdoc](plots/real/rustdoc.svg) | 15947 | 88.320<br>1.00x | 360.013<br>4.08x | 44.523<br>0.50x | 40.629<br>0.46x | 22.842<br>0.26x | 25.025<br>0.28x | **21.287<br>0.24x** | - |
| [real/css-flexbox-1](plots/real/css-flexbox-1.svg) | 15890 | 87.237<br>1.00x | 200.453<br>2.30x | 41.930<br>0.48x | 46.143<br>0.53x | **22.199<br>0.25x** | 25.311<br>0.29x | 30.263<br>0.35x | - |
| [real/servo-org](plots/real/servo-org.svg) | 226 | 2.193<br>1.00x | 4.547<br>2.07x | 1.229<br>0.56x | 0.974<br>0.44x | 0.372<br>0.17x | 0.686<br>0.31x | **0.222<br>0.10x** | - |
| [real/dioxuslabs-com](plots/real/dioxuslabs-com.svg) | 158 | 3.027<br>1.00x | 15.923<br>5.26x | 0.850<br>0.28x | 0.582<br>0.19x | 0.440<br>0.15x | 0.731<br>0.24x | **0.316<br>0.10x** | - |
| [real/bootstrap-dashboard](plots/real/bootstrap-dashboard.svg) | 199 | 1.647<br>1.00x | 2.771<br>1.68x | 0.783<br>0.48x | 0.772<br>0.47x | 0.567<br>0.34x | 0.875<br>0.53x | **0.465<br>0.28x** | - |

### Construction

| case | nodes | Chrome<br>rebuildLayoutTree | Ladybird<br>tree build | Servo(1)<br>Box Tree | Servo(3)<br>Box Tree | Blitz<br>construct ( + pconstruct) | Blitz<br>construct, parallel |
|---|---:|---:|---:|---:|---:|---:|---:|
| [flex/huge_nested/1000](plots/flex/huge-nested-1000.svg) | 911 | 0.326<br>1.00x | 0.586<br>1.80x | 0.769<br>2.36x | 0.413<br>1.27x | 0.050<br>0.15x | **0.050<br>0.15x** |
| [flex/wide/1000](plots/flex/wide-1000.svg) | 1000 | 0.353<br>1.00x | 0.645<br>1.83x | 0.931<br>2.64x | 0.679<br>1.92x | 0.074<br>0.21x | **0.068<br>0.19x** |
| [flex/absolute/1000](plots/flex/absolute-1000.svg) | 1003 | 0.567<br>1.00x | 0.714<br>1.26x | 1.136<br>2.00x | 0.695<br>1.22x | **0.060<br>0.11x** | 0.064<br>0.11x |
| [flex/deep_auto/1000](plots/flex/deep-auto-1000.svg) | 767 | 0.288<br>1.00x | 0.565<br>1.96x | 1.021<br>3.55x | 1.045<br>3.63x | **0.056<br>0.19x** | 0.057<br>0.20x |
| [flex/deep_random/1000](plots/flex/deep-random-1000.svg) | 767 | 0.293<br>1.00x | 0.546<br>1.87x | 0.993<br>3.39x | 1.070<br>3.65x | **0.065<br>0.22x** | 0.067<br>0.23x |
| [flex/huge_nested/10000](plots/flex/huge-nested-10000.svg) | 9111 | 3.515<br>1.00x | 6.306<br>1.79x | 7.074<br>2.01x | 3.064<br>0.87x | 0.584<br>0.17x | **0.535<br>0.15x** |
| [flex/wide/10000](plots/flex/wide-10000.svg) | 10001 | 3.410<br>1.00x | 6.890<br>2.02x | 10.218<br>3.00x | 5.795<br>1.70x | 0.857<br>0.25x | **0.794<br>0.23x** |
| [flex/absolute/10000](plots/flex/absolute-10000.svg) | 10004 | 5.842<br>1.00x | 7.917<br>1.36x | 11.948<br>2.05x | 6.979<br>1.19x | 0.899<br>0.15x | **0.786<br>0.13x** |
| [flex/deep_auto/10000](plots/flex/deep-auto-10000.svg) | 8191 | 3.549<br>1.00x | 6.165<br>1.74x | 9.020<br>2.54x | 9.551<br>2.69x | **0.659<br>0.19x** | 0.675<br>0.19x |
| [flex/deep_random/10000](plots/flex/deep-random-10000.svg) | 8191 | 3.101<br>1.00x | 6.779<br>2.19x | 8.889<br>2.87x | 9.665<br>3.12x | 0.789<br>0.25x | **0.714<br>0.23x** |
| [flex/superdeep/50](plots/flex/superdeep-50.svg) | 151 | 0.087<br>1.00x | 0.189<br>2.17x | 0.280<br>3.22x | 0.258<br>2.97x | **0.009<br>0.11x** | 0.010<br>0.12x |
| [flex/superdeep/100](plots/flex/superdeep-100.svg) | 301 | 0.178<br>1.00x | 0.440<br>2.47x | 0.531<br>2.98x | 0.520<br>2.92x | **0.017<br>0.10x** | 0.019<br>0.11x |
| [grid/wide/31x31](plots/grid/wide-31x31.svg) | 962 | 0.322<br>1.00x | 0.643<br>2.00x | 0.788<br>2.45x | 0.861<br>2.67x | 0.048<br>0.15x | **0.048<br>0.15x** |
| [grid/wide/100x100](plots/grid/wide-100x100.svg) | 10001 | 3.261<br>1.00x | 6.888<br>2.11x | 8.662<br>2.66x | 8.887<br>2.73x | **0.892<br>0.27x** | 0.945<br>0.29x |
| [grid/deep/2x2x5](plots/grid/deep-2x2x5.svg) | 1365 | 0.560<br>1.00x | 0.958<br>1.71x | 1.416<br>2.53x | 0.629<br>1.12x | **0.093<br>0.17x** | 0.095<br>0.17x |
| [grid/deep/3x3x4](plots/grid/deep-3x3x4.svg) | 7381 | 2.728<br>1.00x | 5.097<br>1.87x | 9.119<br>3.34x | 3.174<br>1.16x | 0.558<br>0.20x | **0.549<br>0.20x** |
| [grid/superdeep/100](plots/grid/superdeep-100.svg) | 101 | 0.088<br>1.00x | 0.217<br>2.46x | 0.435<br>4.94x | 0.449<br>5.10x | 0.010<br>0.11x | **0.010<br>0.11x** |
| [pangui/expand_with_max_constraint](plots/pangui/expand-with-max-constraint.svg) | 3001 | 1.175<br>1.00x | 1.835<br>1.56x | 2.972<br>2.53x | 1.698<br>1.45x | **0.202<br>0.17x** | 0.209<br>0.18x |
| [pangui/expand_with_min_constraint](plots/pangui/expand-with-min-constraint.svg) | 3001 | 1.164<br>1.00x | 1.845<br>1.58x | 2.953<br>2.54x | 1.824<br>1.57x | **0.202<br>0.17x** | 0.205<br>0.18x |
| [pangui/fit_nesting](plots/pangui/fit-nesting.svg) | 101111 | 39.509<br>1.00x | 90.739<br>2.30x | 86.912<br>2.20x | 29.873<br>0.76x | **9.677<br>0.24x** | 10.533<br>0.27x |
| [pangui/flex_expand_equal_weights](plots/pangui/flex-expand-equal-weights.svg) | 15001 | 5.446<br>1.00x | 11.407<br>2.09x | 12.368<br>2.27x | 12.236<br>2.25x | 1.716<br>0.32x | **1.713<br>0.31x** |
| [pangui/flex_expand_weights](plots/pangui/flex-expand-weights.svg) | 15001 | 5.464<br>1.00x | 10.069<br>1.84x | 16.231<br>2.97x | 8.877<br>1.62x | 1.170<br>0.21x | **1.099<br>0.20x** |
| [pangui/nested_vertical_stack](plots/pangui/nested-vertical-stack.svg) | 10001 | 3.469<br>1.00x | 6.939<br>2.00x | 9.720<br>2.80x | 8.202<br>2.36x | 1.086<br>0.31x | **0.978<br>0.28x** |
| [pangui/padding_and_margin](plots/pangui/padding-and-margin.svg) | 101 | 0.056<br>1.00x | 0.107<br>1.91x | 0.140<br>2.51x | 0.165<br>2.94x | **0.006<br>0.11x** | 0.007<br>0.12x |
| [pangui/percentage_and_ratio](plots/pangui/percentage-and-ratio.svg) | 10001 | 3.802<br>1.00x | 6.994<br>1.84x | 9.668<br>2.54x | 8.544<br>2.25x | **1.042<br>0.27x** | 1.102<br>0.29x |
| [pangui/perpendicular_expand_with_wrap](plots/pangui/perpendicular-expand-with-wrap.svg) | 12001 | 4.203<br>1.00x | 8.431<br>2.01x | 10.919<br>2.60x | 10.595<br>2.52x | 1.389<br>0.33x | **1.378<br>0.33x** |
| [pangui/pixels_with_min_expand_constraint](plots/pangui/pixels-with-min-expand-constraint.svg) | 30001 | 11.817<br>1.00x | 22.582<br>1.91x | 35.564<br>3.01x | 18.118<br>1.53x | 2.732<br>0.23x | **2.556<br>0.22x** |
| [pangui/wide_no_wrap_simple_few](plots/pangui/wide-no-wrap-simple-few.svg) | 1001 | 0.355<br>1.00x | 0.627<br>1.77x | 0.783<br>2.21x | 0.848<br>2.39x | 0.053<br>0.15x | **0.050<br>0.14x** |
| [pangui/wide_no_wrap_simple_many](plots/pangui/wide-no-wrap-simple-many.svg) | 100001 | 36.267<br>1.00x | 94.998<br>2.62x | 110.442<br>3.05x | 80.622<br>2.22x | **13.650<br>0.38x** | 14.068<br>0.39x |
| [pangui/wide_wrapping](plots/pangui/wide-wrapping.svg) | 10001 | 3.673<br>1.00x | 6.962<br>1.90x | 9.804<br>2.67x | 9.289<br>2.53x | 1.139<br>0.31x | **1.114<br>0.30x** |
| [text/paragraphs/100](plots/text/paragraphs-100.svg) | 101 | **0.077<br>1.00x** | 0.169<br>2.20x | 15.372<br>199.63x | 13.647<br>177.23x | 9.212<br>119.64x | 1.804<br>23.43x |
| [text/flex_cards/100](plots/text/flex-cards-100.svg) | 301 | **0.166<br>1.00x** | 0.360<br>2.17x | 6.011<br>36.21x | 5.074<br>30.57x | 3.178<br>19.14x | 0.693<br>4.17x |
| [text/inline_mixed/100](plots/text/inline-mixed-100.svg) | 1599 | **0.981<br>1.00x** | 2.132<br>2.17x | 23.044<br>23.49x | 11.993<br>12.23x | 11.948<br>12.18x | 2.373<br>2.42x |
| [text/paragraphs/1000](plots/text/paragraphs-1000.svg) | 1001 | **0.571<br>1.00x** | 1.226<br>2.15x | 149.187<br>261.27x | 131.455<br>230.22x | 83.279<br>145.85x | 11.886<br>20.82x |
| [text/flex_cards/1000](plots/text/flex-cards-1000.svg) | 3001 | **1.477<br>1.00x** | 3.034<br>2.05x | 58.191<br>39.40x | 41.561<br>28.14x | 31.474<br>21.31x | 5.772<br>3.91x |
| [text/inline_mixed/1000](plots/text/inline-mixed-1000.svg) | 16361 | **10.180<br>1.00x** | 22.403<br>2.20x | 242.820<br>23.85x | 112.187<br>11.02x | 116.695<br>11.46x | 22.765<br>2.24x |
| [real/wikipedia](plots/real/wikipedia.svg) | 21889 | 19.871<br>1.00x | 55.653<br>2.80x | 211.213<br>10.63x | 76.009<br>3.83x | 68.630<br>3.45x | **17.647<br>0.89x** |
| [real/mdn](plots/real/mdn.svg) | 2212 | **1.405<br>1.00x** | 4.245<br>3.02x | 15.195<br>10.82x | 7.098<br>5.05x | 5.959<br>4.24x | 2.433<br>1.73x |
| [real/rustdoc](plots/real/rustdoc.svg) | 15947 | **12.679<br>1.00x** | 33.758<br>2.66x | 125.008<br>9.86x | 52.910<br>4.17x | 50.386<br>3.97x | 13.632<br>1.08x |
| [real/css-flexbox-1](plots/real/css-flexbox-1.svg) | 15890 | **10.785<br>1.00x** | 40.147<br>3.72x | 133.252<br>12.36x | 73.311<br>6.80x | 58.944<br>5.47x | 16.580<br>1.54x |
| [real/servo-org](plots/real/servo-org.svg) | 226 | **0.218<br>1.00x** | 0.712<br>3.27x | 3.742<br>17.17x | 2.678<br>12.29x | 0.828<br>3.80x | 0.464<br>2.13x |
| [real/dioxuslabs-com](plots/real/dioxuslabs-com.svg) | 158 | **0.165<br>1.00x** | 0.239<br>1.45x | 3.562<br>21.59x | 4.087<br>24.77x | 0.348<br>2.11x | 0.276<br>1.67x |
| [real/bootstrap-dashboard](plots/real/bootstrap-dashboard.svg) | 199 | 0.190<br>1.00x | **0.030<br>0.16x** | 2.052<br>10.80x | 1.875<br>9.87x | 0.473<br>2.49x | 0.315<br>1.66x |

### Box construction + layout

| case | nodes | Chrome<br>rebuildLayoutTree + Layout | Firefox(1)<br>Reflow | Firefox<br>Reflow | Ladybird<br>tree build + layout | Servo(1)<br>Box + Fragment | Servo(3)<br>Box + Fragment | Blitz<br>construct + layout | Blitz<br>construct + layout (parallel construct) | Blitz<br>construct + layout (parallel construct + layout) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [flex/huge_nested/1000](plots/flex/huge-nested-1000.svg) | 911 | 1.238<br>1.00x | 1.277<br>1.03x | 1.339<br>1.08x | 5.113<br>4.13x | 1.907<br>1.54x | 1.297<br>1.05x | 0.646<br>0.52x | 0.647<br>0.52x | **0.479<br>0.39x** |
| [flex/wide/1000](plots/flex/wide-1000.svg) | 1000 | 1.612<br>1.00x | 2.085<br>1.29x | 2.174<br>1.35x | 6.929<br>4.30x | 2.565<br>1.59x | 2.381<br>1.48x | 1.148<br>0.71x | 1.087<br>0.67x | **0.914<br>0.57x** |
| [flex/absolute/1000](plots/flex/absolute-1000.svg) | 1003 | 1.875<br>1.00x | 2.439<br>1.30x | 2.460<br>1.31x | 4.849<br>2.59x | 2.505<br>1.34x | 2.184<br>1.16x | 0.839<br>0.45x | **0.830<br>0.44x** | 0.924<br>0.49x |
| [flex/deep_auto/1000](plots/flex/deep-auto-1000.svg) | 767 | 1.949<br>1.00x | 1.194<br>0.61x | 1.217<br>0.62x | 7.535<br>3.87x | 2.524<br>1.29x | 2.579<br>1.32x | 1.779<br>0.91x | 1.830<br>0.94x | **0.851<br>0.44x** |
| [flex/deep_random/1000](plots/flex/deep-random-1000.svg) | 767 | 1.199<br>1.00x | 1.562<br>1.30x | 1.644<br>1.37x | 6.214<br>5.18x | 2.102<br>1.75x | 2.229<br>1.86x | 0.873<br>0.73x | 0.876<br>0.73x | **0.632<br>0.53x** |
| [flex/huge_nested/10000](plots/flex/huge-nested-10000.svg) | 9111 | 12.321<br>1.00x | 12.047<br>0.98x | 13.053<br>1.06x | 50.896<br>4.13x | 19.800<br>1.61x | 10.002<br>0.81x | 6.769<br>0.55x | 6.241<br>0.51x | **2.753<br>0.22x** |
| [flex/wide/10000](plots/flex/wide-10000.svg) | 10001 | 16.229<br>1.00x | 20.823<br>1.28x | 22.130<br>1.36x | 75.922<br>4.68x | 26.432<br>1.63x | 23.664<br>1.46x | 12.900<br>0.79x | 11.756<br>0.72x | **8.290<br>0.51x** |
| [flex/absolute/10000](plots/flex/absolute-10000.svg) | 10004 | 19.759<br>1.00x | 24.045<br>1.22x | 24.398<br>1.23x | 55.028<br>2.78x | 27.273<br>1.38x | 22.808<br>1.15x | 10.339<br>0.52x | 9.255<br>0.47x | **7.188<br>0.36x** |
| [flex/deep_auto/10000](plots/flex/deep-auto-10000.svg) | 8191 | 20.912<br>1.00x | 12.149<br>0.58x | 12.456<br>0.60x | 70.017<br>3.35x | 26.367<br>1.26x | 27.011<br>1.29x | 18.380<br>0.88x | 18.160<br>0.87x | **5.998<br>0.29x** |
| [flex/deep_random/10000](plots/flex/deep-random-10000.svg) | 8191 | 11.927<br>1.00x | 15.741<br>1.32x | 16.538<br>1.39x | 61.353<br>5.14x | 22.245<br>1.87x | 23.926<br>2.01x | 8.673<br>0.73x | 8.570<br>0.72x | **4.019<br>0.34x** |
| [flex/superdeep/50](plots/flex/superdeep-50.svg) | 151 | 0.528<br>1.00x | 0.492<br>0.93x | 0.494<br>0.94x | 1.865<br>3.53x | 0.630<br>1.19x | 0.622<br>1.18x | 0.299<br>0.57x | **0.287<br>0.54x** | 0.615<br>1.17x |
| [flex/superdeep/100](plots/flex/superdeep-100.svg) | 301 | 1.048<br>1.00x | 0.940<br>0.90x | 0.942<br>0.90x | 3.478<br>3.32x | 1.226<br>1.17x | 1.184<br>1.13x | 0.678<br>0.65x | **0.650<br>0.62x** | 1.397<br>1.33x |
| [grid/wide/31x31](plots/grid/wide-31x31.svg) | 962 | 2.946<br>1.00x | 2.855<br>0.97x | 2.924<br>0.99x | 6.166<br>2.09x | 3.430<br>1.16x | 3.508<br>1.19x | **1.510<br>0.51x** | 1.563<br>0.53x | 2.567<br>0.87x |
| [grid/wide/100x100](plots/grid/wide-100x100.svg) | 10001 | 39.466<br>1.00x | 33.456<br>0.85x | 33.561<br>0.85x | 73.232<br>1.86x | 35.567<br>0.90x | 36.202<br>0.92x | 15.777<br>0.40x | **15.526<br>0.39x** | 18.447<br>0.47x |
| [grid/deep/2x2x5](plots/grid/deep-2x2x5.svg) | 1365 | 7.565<br>1.00x | 10.915<br>1.44x | 10.951<br>1.45x | 14.686<br>1.94x | 9.111<br>1.20x | 8.732<br>1.15x | 3.502<br>0.46x | 3.547<br>0.47x | **1.571<br>0.21x** |
| [grid/deep/3x3x4](plots/grid/deep-3x3x4.svg) | 7381 | 32.832<br>1.00x | 43.506<br>1.33x | 44.362<br>1.35x | 76.115<br>2.32x | 52.102<br>1.59x | 41.479<br>1.26x | 17.669<br>0.54x | 16.948<br>0.52x | **6.593<br>0.20x** |
| [grid/superdeep/100](plots/grid/superdeep-100.svg) | 101 | 1.587<br>1.00x | 10.743<br>6.77x | 10.664<br>6.72x | 2.717<br>1.71x | 1.667<br>1.05x | 1.672<br>1.05x | 0.465<br>0.29x | **0.436<br>0.27x** | 0.493<br>0.31x |
| [pangui/expand_with_max_constraint](plots/pangui/expand-with-max-constraint.svg) | 3001 | 4.750<br>1.00x | 4.222<br>0.89x | 4.396<br>0.93x | 12.221<br>2.57x | 8.056<br>1.70x | 6.777<br>1.43x | 3.614<br>0.76x | 3.575<br>0.75x | **2.748<br>0.58x** |
| [pangui/expand_with_min_constraint](plots/pangui/expand-with-min-constraint.svg) | 3001 | 4.736<br>1.00x | 4.037<br>0.85x | 4.063<br>0.86x | 12.033<br>2.54x | 7.959<br>1.68x | 7.160<br>1.51x | 3.457<br>0.73x | 3.569<br>0.75x | **2.399<br>0.51x** |
| [pangui/fit_nesting](plots/pangui/fit-nesting.svg) | 101111 | 167.505<br>1.00x | 123.095<br>0.73x | 129.757<br>0.77x | 461.121<br>2.75x | 421.233<br>2.51x | 162.797<br>0.97x | 92.000<br>0.55x | 92.467<br>0.55x | **36.846<br>0.22x** |
| [pangui/flex_expand_equal_weights](plots/pangui/flex-expand-equal-weights.svg) | 15001 | 17.535<br>1.00x | 20.727<br>1.18x | 22.194<br>1.27x | 55.534<br>3.17x | 26.813<br>1.53x | 27.210<br>1.55x | **8.828<br>0.50x** | 8.983<br>0.51x | 9.555<br>0.54x |
| [pangui/flex_expand_weights](plots/pangui/flex-expand-weights.svg) | 15001 | 16.063<br>1.00x | 32.129<br>2.00x | 32.948<br>2.05x | 47.376<br>2.95x | 33.518<br>2.09x | 28.052<br>1.75x | 12.284<br>0.76x | 11.555<br>0.72x | **7.183<br>0.45x** |
| [pangui/nested_vertical_stack](plots/pangui/nested-vertical-stack.svg) | 10001 | 10.734<br>1.00x | 20.196<br>1.88x | 21.412<br>1.99x | 41.635<br>3.88x | 23.536<br>2.19x | 21.382<br>1.99x | 8.453<br>0.79x | **7.695<br>0.72x** | 10.107<br>0.94x |
| [pangui/padding_and_margin](plots/pangui/padding-and-margin.svg) | 101 | 0.194<br>1.00x | 0.260<br>1.34x | 0.265<br>1.37x | 0.729<br>3.76x | 0.337<br>1.74x | 0.375<br>1.94x | **0.072<br>0.37x** | 0.075<br>0.38x | 0.103<br>0.53x |
| [pangui/percentage_and_ratio](plots/pangui/percentage-and-ratio.svg) | 10001 | 17.374<br>1.00x | 16.293<br>0.94x | 17.118<br>0.99x | 38.020<br>2.19x | 21.172<br>1.22x | 20.183<br>1.16x | **6.312<br>0.36x** | 6.341<br>0.36x | 6.694<br>0.39x |
| [pangui/perpendicular_expand_with_wrap](plots/pangui/perpendicular-expand-with-wrap.svg) | 12001 | 17.952<br>1.00x | 20.979<br>1.17x | 22.577<br>1.26x | 48.242<br>2.69x | 24.234<br>1.35x | 23.933<br>1.33x | 13.287<br>0.74x | **12.574<br>0.70x** | 14.238<br>0.79x |
| [pangui/pixels_with_min_expand_constraint](plots/pangui/pixels-with-min-expand-constraint.svg) | 30001 | 48.396<br>1.00x | 43.196<br>0.89x | 42.796<br>0.88x | 139.188<br>2.88x | 88.848<br>1.84x | 71.391<br>1.48x | 36.705<br>0.76x | 36.474<br>0.75x | **20.293<br>0.42x** |
| [pangui/wide_no_wrap_simple_few](plots/pangui/wide-no-wrap-simple-few.svg) | 1001 | 1.127<br>1.00x | 1.348<br>1.20x | 1.398<br>1.24x | 3.141<br>2.79x | 1.878<br>1.67x | 2.050<br>1.82x | **0.593<br>0.53x** | 0.593<br>0.53x | 0.792<br>0.70x |
| [pangui/wide_no_wrap_simple_many](plots/pangui/wide-no-wrap-simple-many.svg) | 100001 | 118.036<br>1.00x | 196.832<br>1.67x | 182.890<br>1.55x | 404.908<br>3.43x | 228.587<br>1.94x | 196.788<br>1.67x | **91.404<br>0.77x** | 93.773<br>0.79x | 91.732<br>0.78x |
| [pangui/wide_wrapping](plots/pangui/wide-wrapping.svg) | 10001 | 12.639<br>1.00x | 13.292<br>1.05x | 15.105<br>1.20x | 39.653<br>3.14x | 21.341<br>1.69x | 19.857<br>1.57x | 7.986<br>0.63x | **7.788<br>0.62x** | 9.658<br>0.76x |
| [text/paragraphs/100](plots/text/paragraphs-100.svg) | 101 | 5.578<br>1.00x | 5.498<br>0.99x | 5.382<br>0.96x | 9.231<br>1.65x | 18.180<br>3.26x | 15.107<br>2.71x | 9.919<br>1.78x | 2.695<br>0.48x | **2.115<br>0.38x** |
| [text/flex_cards/100](plots/text/flex-cards-100.svg) | 301 | 3.792<br>1.00x | 4.585<br>1.21x | 4.421<br>1.17x | 7.083<br>1.87x | 7.600<br>2.00x | 6.791<br>1.79x | 4.164<br>1.10x | 1.890<br>0.50x | **1.259<br>0.33x** |
| [text/inline_mixed/100](plots/text/inline-mixed-100.svg) | 1599 | 10.103<br>1.00x | 12.903<br>1.28x | 13.035<br>1.29x | 21.044<br>2.08x | 27.500<br>2.72x | 15.381<br>1.52x | 12.709<br>1.26x | 3.425<br>0.34x | **3.361<br>0.33x** |
| [text/paragraphs/1000](plots/text/paragraphs-1000.svg) | 1001 | 52.360<br>1.00x | 40.374<br>0.77x | 40.657<br>0.78x | 91.889<br>1.75x | 189.388<br>3.62x | 148.257<br>2.83x | 89.619<br>1.71x | **18.189<br>0.35x** | 19.096<br>0.36x |
| [text/flex_cards/1000](plots/text/flex-cards-1000.svg) | 3001 | 34.691<br>1.00x | 27.813<br>0.80x | 27.942<br>0.81x | 66.449<br>1.92x | 72.495<br>2.09x | 57.112<br>1.65x | 41.475<br>1.20x | 16.843<br>0.49x | **10.756<br>0.31x** |
| [text/inline_mixed/1000](plots/text/inline-mixed-1000.svg) | 16361 | 94.366<br>1.00x | 91.998<br>0.97x | 91.763<br>0.97x | 208.493<br>2.21x | 290.935<br>3.08x | 133.919<br>1.42x | 124.718<br>1.32x | 31.031<br>0.33x | **28.612<br>0.30x** |
| [real/wikipedia](plots/real/wikipedia.svg) | 21889 | 175.695<br>1.00x | 176.115<br>1.00x | 174.135<br>0.99x | 462.356<br>2.63x | 256.253<br>1.46x | 113.407<br>0.65x | 85.517<br>0.49x | **33.896<br>0.19x** | 39.406<br>0.22x |
| [real/mdn](plots/real/mdn.svg) | 2212 | 12.581<br>1.00x | 12.893<br>1.02x | 12.802<br>1.02x | 50.343<br>4.00x | 20.795<br>1.65x | 10.102<br>0.80x | 9.578<br>0.76x | 6.090<br>0.48x | **3.746<br>0.30x** |
| [real/rustdoc](plots/real/rustdoc.svg) | 15947 | 101.098<br>1.00x | 84.159<br>0.83x | 82.727<br>0.82x | 395.031<br>3.91x | 169.531<br>1.68x | 93.540<br>0.93x | 73.713<br>0.73x | 37.084<br>0.37x | **35.040<br>0.35x** |
| [real/css-flexbox-1](plots/real/css-flexbox-1.svg) | 15890 | 98.079<br>1.00x | 94.019<br>0.96x | 95.404<br>0.97x | 240.688<br>2.45x | 176.874<br>1.80x | 123.243<br>1.26x | 81.143<br>0.83x | **39.044<br>0.40x** | 57.099<br>0.58x |
| [real/servo-org](plots/real/servo-org.svg) | 226 | 2.418<br>1.00x | 4.478<br>1.85x | 4.445<br>1.84x | 5.259<br>2.17x | 4.971<br>2.06x | 3.822<br>1.58x | 1.226<br>0.51x | 0.908<br>0.38x | **0.682<br>0.28x** |
| [real/dioxuslabs-com](plots/real/dioxuslabs-com.svg) | 158 | 3.197<br>1.00x | 4.986<br>1.56x | 5.012<br>1.57x | 16.165<br>5.06x | 4.526<br>1.42x | 4.886<br>1.53x | 0.789<br>0.25x | 0.747<br>0.23x | **0.596<br>0.19x** |
| [real/bootstrap-dashboard](plots/real/bootstrap-dashboard.svg) | 199 | 1.840<br>1.00x | 2.210<br>1.20x | 2.377<br>1.29x | 2.940<br>1.60x | 2.841<br>1.54x | 2.728<br>1.48x | 1.053<br>0.57x | 0.971<br>0.53x | **0.823<br>0.45x** |

### Style

| case | nodes | Chrome<br>recalcStyle | Firefox(1)<br>Styles (incl. frame construction) | Firefox<br>Styles (incl. frame construction) | Ladybird<br>update_style | Servo(1)<br>Styling | Servo(3)<br>Styling | Blitz<br>style | Blitz<br>style (parallel) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [flex/huge_nested/1000](plots/flex/huge-nested-1000.svg) | 911 | 1.467<br>1.00x | 4.271<br>2.91x | 1.818<br>1.24x | 28.907<br>19.70x | 5.431<br>3.70x | 2.688<br>1.83x | 2.193<br>1.50x | **0.878<br>0.60x** |
| [flex/wide/1000](plots/flex/wide-1000.svg) | 1000 | 1.356<br>1.00x | 4.084<br>3.01x | 2.203<br>1.62x | 32.478<br>23.95x | 5.135<br>3.79x | 2.884<br>2.13x | 2.028<br>1.50x | **1.095<br>0.81x** |
| [flex/absolute/1000](plots/flex/absolute-1000.svg) | 1003 | 1.598<br>1.00x | 4.330<br>2.71x | 2.472<br>1.55x | 38.063<br>23.82x | 5.251<br>3.29x | 2.944<br>1.84x | 1.947<br>1.22x | **1.091<br>0.68x** |
| [flex/deep_auto/1000](plots/flex/deep-auto-1000.svg) | 767 | 0.804<br>1.00x | 1.691<br>2.10x | 0.878<br>1.09x | 16.374<br>20.37x | 2.165<br>2.69x | 1.152<br>1.43x | 0.966<br>1.20x | **0.470<br>0.58x** |
| [flex/deep_random/1000](plots/flex/deep-random-1000.svg) | 767 | 0.951<br>1.00x | 2.415<br>2.54x | 1.730<br>1.82x | 23.626<br>24.84x | 3.272<br>3.44x | 2.147<br>2.26x | 1.306<br>1.37x | **0.931<br>0.98x** |
| [flex/huge_nested/10000](plots/flex/huge-nested-10000.svg) | 9111 | 14.234<br>1.00x | 43.555<br>3.06x | 15.987<br>1.12x | 259.575<br>18.24x | 54.501<br>3.83x | 24.089<br>1.69x | 21.499<br>1.51x | **8.469<br>0.59x** |
| [flex/wide/10000](plots/flex/wide-10000.svg) | 10001 | 12.992<br>1.00x | 41.522<br>3.20x | 18.121<br>1.39x | 314.202<br>24.18x | 50.469<br>3.88x | 26.194<br>2.02x | 20.725<br>1.60x | **11.466<br>0.88x** |
| [flex/absolute/10000](plots/flex/absolute-10000.svg) | 10004 | 15.681<br>1.00x | 45.639<br>2.91x | 20.304<br>1.29x | 357.634<br>22.81x | 51.985<br>3.32x | 26.779<br>1.71x | 22.065<br>1.41x | **10.091<br>0.64x** |
| [flex/deep_auto/10000](plots/flex/deep-auto-10000.svg) | 8191 | 10.200<br>1.00x | 24.404<br>2.39x | 9.294<br>0.91x | 169.786<br>16.65x | 31.286<br>3.07x | 13.828<br>1.36x | 13.140<br>1.29x | **5.610<br>0.55x** |
| [flex/deep_random/10000](plots/flex/deep-random-10000.svg) | 8191 | 9.781<br>1.00x | 30.519<br>3.12x | 14.474<br>1.48x | 233.245<br>23.85x | 37.176<br>3.80x | 19.188<br>1.96x | 13.704<br>1.40x | **8.501<br>0.87x** |
| [flex/superdeep/50](plots/flex/superdeep-50.svg) | 151 | 0.301<br>1.00x | 0.469<br>1.56x | 0.469<br>1.56x | 7.010<br>23.29x | 0.870<br>2.89x | 0.783<br>2.60x | **0.246<br>0.82x** | 0.254<br>0.84x |
| [flex/superdeep/100](plots/flex/superdeep-100.svg) | 301 | 0.535<br>1.00x | 0.858<br>1.60x | 0.871<br>1.63x | 10.603<br>19.82x | 1.541<br>2.88x | 1.477<br>2.76x | **0.492<br>0.92x** | 0.522<br>0.98x |
| [grid/wide/31x31](plots/grid/wide-31x31.svg) | 962 | 1.200<br>1.00x | 4.634<br>3.86x | 2.229<br>1.86x | 31.587<br>26.32x | 5.991<br>4.99x | 2.902<br>2.42x | 2.164<br>1.80x | **1.171<br>0.98x** |
| [grid/wide/100x100](plots/grid/wide-100x100.svg) | 10001 | 12.464<br>1.00x | 51.419<br>4.13x | 20.532<br>1.65x | 342.121<br>27.45x | 55.851<br>4.48x | 26.515<br>2.13x | 20.751<br>1.66x | **9.208<br>0.74x** |
| [grid/deep/2x2x5](plots/grid/deep-2x2x5.svg) | 1365 | 2.183<br>1.00x | 5.212<br>2.39x | 2.659<br>1.22x | 62.731<br>28.74x | 6.811<br>3.12x | 3.781<br>1.73x | 2.496<br>1.14x | **1.519<br>0.70x** |
| [grid/deep/3x3x4](plots/grid/deep-3x3x4.svg) | 7381 | 10.912<br>1.00x | 29.805<br>2.73x | 13.377<br>1.23x | 407.414<br>37.34x | 43.948<br>4.03x | 19.878<br>1.82x | 15.231<br>1.40x | **8.211<br>0.75x** |
| [grid/superdeep/100](plots/grid/superdeep-100.svg) | 101 | 0.205<br>1.00x | 0.310<br>1.51x | 0.324<br>1.58x | 6.063<br>29.58x | 0.523<br>2.55x | 0.586<br>2.86x | 0.193<br>0.94x | **0.161<br>0.79x** |
| [pangui/expand_with_max_constraint](plots/pangui/expand-with-max-constraint.svg) | 3001 | 4.523<br>1.00x | 11.358<br>2.51x | 4.493<br>0.99x | 75.749<br>16.75x | 13.370<br>2.96x | 6.324<br>1.40x | 5.810<br>1.28x | **2.451<br>0.54x** |
| [pangui/expand_with_min_constraint](plots/pangui/expand-with-min-constraint.svg) | 3001 | 4.432<br>1.00x | 11.235<br>2.53x | 4.595<br>1.04x | 75.715<br>17.08x | 13.963<br>3.15x | 6.627<br>1.50x | 5.839<br>1.32x | **2.110<br>0.48x** |
| [pangui/fit_nesting](plots/pangui/fit-nesting.svg) | 101111 | 237.304<br>1.00x | 626.303<br>2.64x | 202.382<br>0.85x | 3456.659<br>14.57x | 729.301<br>3.07x | 290.452<br>1.22x | 327.475<br>1.38x | **101.122<br>0.43x** |
| [pangui/flex_expand_equal_weights](plots/pangui/flex-expand-equal-weights.svg) | 15001 | 29.287<br>1.00x | 91.245<br>3.12x | 32.402<br>1.11x | 605.620<br>20.68x | 96.740<br>3.30x | 46.752<br>1.60x | 41.173<br>1.41x | **15.140<br>0.52x** |
| [pangui/flex_expand_weights](plots/pangui/flex-expand-weights.svg) | 15001 | 21.522<br>1.00x | 61.785<br>2.87x | 22.761<br>1.06x | 423.533<br>19.68x | 66.698<br>3.10x | 29.363<br>1.36x | 29.181<br>1.36x | **11.048<br>0.51x** |
| [pangui/nested_vertical_stack](plots/pangui/nested-vertical-stack.svg) | 10001 | 18.975<br>1.00x | 57.324<br>3.02x | 21.370<br>1.13x | 364.667<br>19.22x | 63.974<br>3.37x | 28.784<br>1.52x | 28.337<br>1.49x | **9.993<br>0.53x** |
| [pangui/padding_and_margin](plots/pangui/padding-and-margin.svg) | 101 | 0.279<br>1.00x | 0.577<br>2.07x | 0.315<br>1.13x | 6.602<br>23.66x | 0.828<br>2.97x | 0.578<br>2.07x | 0.281<br>1.01x | **0.179<br>0.64x** |
| [pangui/percentage_and_ratio](plots/pangui/percentage-and-ratio.svg) | 10001 | 21.147<br>1.00x | 59.318<br>2.81x | 22.328<br>1.06x | 372.239<br>17.60x | 61.505<br>2.91x | 28.864<br>1.36x | 26.579<br>1.26x | **11.568<br>0.55x** |
| [pangui/perpendicular_expand_with_wrap](plots/pangui/perpendicular-expand-with-wrap.svg) | 12001 | 23.389<br>1.00x | 66.668<br>2.85x | 25.658<br>1.10x | 460.373<br>19.68x | 71.217<br>3.04x | 32.988<br>1.41x | 28.534<br>1.22x | **12.190<br>0.52x** |
| [pangui/pixels_with_min_expand_constraint](plots/pangui/pixels-with-min-expand-constraint.svg) | 30001 | 44.239<br>1.00x | 130.786<br>2.96x | 43.821<br>0.99x | 984.958<br>22.26x | 139.051<br>3.14x | 58.427<br>1.32x | 59.926<br>1.35x | **20.825<br>0.47x** |
| [pangui/wide_no_wrap_simple_few](plots/pangui/wide-no-wrap-simple-few.svg) | 1001 | 1.984<br>1.00x | 5.865<br>2.96x | 2.449<br>1.23x | 34.910<br>17.60x | 7.253<br>3.66x | 3.508<br>1.77x | 3.070<br>1.55x | **1.117<br>0.56x** |
| [pangui/wide_no_wrap_simple_many](plots/pangui/wide-no-wrap-simple-many.svg) | 100001 | 229.721<br>1.00x | 625.299<br>2.72x | 223.745<br>0.97x | 12901.643<br>56.16x | 592.361<br>2.58x | 275.137<br>1.20x | 285.742<br>1.24x | **95.565<br>0.42x** |
| [pangui/wide_wrapping](plots/pangui/wide-wrapping.svg) | 10001 | 19.667<br>1.00x | 58.563<br>2.98x | 22.016<br>1.12x | 374.526<br>19.04x | 73.776<br>3.75x | 37.047<br>1.88x | 27.741<br>1.41x | **10.947<br>0.56x** |
| [text/paragraphs/100](plots/text/paragraphs-100.svg) | 101 | **0.201<br>1.00x** | 0.548<br>2.73x | 0.402<br>2.00x | 2.863<br>14.24x | 0.564<br>2.81x | 0.423<br>2.11x | 0.288<br>1.43x | 0.250<br>1.24x |
| [text/flex_cards/100](plots/text/flex-cards-100.svg) | 301 | **0.325<br>1.00x** | 0.987<br>3.04x | 0.648<br>1.99x | 4.810<br>14.80x | 1.147<br>3.53x | 0.760<br>2.34x | 0.545<br>1.68x | 0.370<br>1.14x |
| [text/inline_mixed/100](plots/text/inline-mixed-100.svg) | 1599 | 0.811<br>1.00x | 2.386<br>2.94x | 1.694<br>2.09x | 11.928<br>14.71x | 2.049<br>2.53x | 1.312<br>1.62x | 1.015<br>1.25x | **0.725<br>0.89x** |
| [text/paragraphs/1000](plots/text/paragraphs-1000.svg) | 1001 | 1.716<br>1.00x | 5.363<br>3.13x | 2.319<br>1.35x | 22.060<br>12.86x | 5.125<br>2.99x | 2.748<br>1.60x | 2.299<br>1.34x | **1.291<br>0.75x** |
| [text/flex_cards/1000](plots/text/flex-cards-1000.svg) | 3001 | 2.845<br>1.00x | 9.988<br>3.51x | 5.010<br>1.76x | 32.645<br>11.47x | 11.452<br>4.03x | 6.524<br>2.29x | 4.850<br>1.70x | **2.702<br>0.95x** |
| [text/inline_mixed/1000](plots/text/inline-mixed-1000.svg) | 16361 | 7.639<br>1.00x | 24.204<br>3.17x | 15.635<br>2.05x | 104.233<br>13.64x | 24.265<br>3.18x | 12.475<br>1.63x | 10.073<br>1.32x | **6.157<br>0.81x** |
| [real/wikipedia](plots/real/wikipedia.svg) | 21889 | 45.919<br>1.00x | 92.111<br>2.01x | 39.977<br>0.87x | 375.344<br>8.17x | 63.843<br>1.39x | 27.532<br>0.60x | 35.400<br>0.77x | **12.128<br>0.26x** |
| [real/mdn](plots/real/mdn.svg) | 2212 | 5.806<br>1.00x | 6.991<br>1.20x | 4.409<br>0.76x | 73.228<br>12.61x | 7.276<br>1.25x | 4.997<br>0.86x | 2.480<br>0.43x | **2.029<br>0.35x** |
| [real/rustdoc](plots/real/rustdoc.svg) | 15947 | 19.806<br>1.00x | 68.903<br>3.48x | 35.006<br>1.77x | 316.233<br>15.97x | 59.740<br>3.02x | 27.403<br>1.38x | 16.490<br>0.83x | **7.427<br>0.37x** |
| [real/css-flexbox-1](plots/real/css-flexbox-1.svg) | 15890 | 18.077<br>1.00x | 36.705<br>2.03x | 22.900<br>1.27x | 183.607<br>10.16x | 23.117<br>1.28x | 13.174<br>0.73x | 14.656<br>0.81x | **6.087<br>0.34x** |
| [real/servo-org](plots/real/servo-org.svg) | 226 | **0.751<br>1.00x** | 1.467<br>1.95x | 1.420<br>1.89x | 15.464<br>20.59x | 1.229<br>1.64x | 1.228<br>1.63x | 0.781<br>1.04x | 0.759<br>1.01x |
| [real/dioxuslabs-com](plots/real/dioxuslabs-com.svg) | 158 | **1.005<br>1.00x** | 1.407<br>1.40x | 1.430<br>1.42x | 18.988<br>18.89x | 1.557<br>1.55x | 1.418<br>1.41x | 1.137<br>1.13x | 1.098<br>1.09x |
| [real/bootstrap-dashboard](plots/real/bootstrap-dashboard.svg) | 199 | **0.760<br>1.00x** | 1.162<br>1.53x | 1.221<br>1.61x | 11.382<br>14.98x | 1.041<br>1.37x | 1.044<br>1.37x | 1.246<br>1.64x | 1.385<br>1.82x |

### Whole pipeline (style to laid-out tree)

| case | nodes | Chrome<br>UpdateLayoutTree + Layout | Firefox(1)<br>Styles + Reflow | Firefox<br>Styles + Reflow | Ladybird<br>update_layout() | Servo(1)<br>restyle_and_build_trees | Servo(3)<br>restyle_and_build_trees | Blitz<br>resolve() | Blitz<br>resolve() (parallel style) | Blitz<br>resolve() (parallel style + construct) | Blitz<br>resolve() (parallel style + construct + layout) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [flex/huge_nested/1000](plots/flex/huge-nested-1000.svg) | 911 | 2.767<br>1.00x | 5.583<br>2.02x | 3.234<br>1.17x | 34.727<br>12.55x | 8.570<br>3.10x | 5.307<br>1.92x | 2.971<br>1.07x | 1.766<br>0.64x | 1.861<br>0.67x | **1.557<br>0.56x** |
| [flex/wide/1000](plots/flex/wide-1000.svg) | 1000 | 3.041<br>1.00x | 6.195<br>2.04x | 4.377<br>1.44x | 39.898<br>13.12x | 8.977<br>2.95x | 6.914<br>2.27x | 3.332<br>1.10x | 2.813<br>0.92x | 2.530<br>0.83x | **2.299<br>0.76x** |
| [flex/absolute/1000](plots/flex/absolute-1000.svg) | 1003 | 3.545<br>1.00x | 6.797<br>1.92x | 5.022<br>1.42x | 43.478<br>12.26x | 8.959<br>2.53x | 6.814<br>1.92x | 2.945<br>0.83x | **2.293<br>0.65x** | 2.399<br>0.68x | 2.636<br>0.74x |
| [flex/deep_auto/1000](plots/flex/deep-auto-1000.svg) | 767 | 2.803<br>1.00x | 2.905<br>1.04x | 2.137<br>0.76x | 24.402<br>8.71x | 5.829<br>2.08x | 5.362<br>1.91x | 2.860<br>1.02x | 2.522<br>0.90x | 2.841<br>1.01x | **1.546<br>0.55x** |
| [flex/deep_random/1000](plots/flex/deep-random-1000.svg) | 767 | 2.209<br>1.00x | 3.999<br>1.81x | 3.394<br>1.54x | 30.299<br>13.72x | 6.567<br>2.97x | 5.781<br>2.62x | 2.281<br>1.03x | 2.109<br>0.95x | 1.935<br>0.88x | **1.692<br>0.77x** |
| [flex/huge_nested/10000](plots/flex/huge-nested-10000.svg) | 9111 | 26.681<br>1.00x | 55.780<br>2.09x | 29.112<br>1.09x | 314.819<br>11.80x | 76.850<br>2.88x | 36.798<br>1.38x | 29.637<br>1.11x | 17.238<br>0.65x | 18.546<br>0.70x | **13.430<br>0.50x** |
| [flex/wide/10000](plots/flex/wide-10000.svg) | 10001 | 29.283<br>1.00x | 62.573<br>2.14x | 40.774<br>1.39x | 394.715<br>13.48x | 81.639<br>2.79x | 53.050<br>1.81x | 35.359<br>1.21x | 26.838<br>0.92x | 26.424<br>0.90x | **22.536<br>0.77x** |
| [flex/absolute/10000](plots/flex/absolute-10000.svg) | 10004 | 35.461<br>1.00x | 69.684<br>1.97x | 44.703<br>1.26x | 416.889<br>11.76x | 81.826<br>2.31x | 53.418<br>1.51x | 34.346<br>0.97x | 22.682<br>0.64x | 23.656<br>0.67x | **20.155<br>0.57x** |
| [flex/deep_auto/10000](plots/flex/deep-auto-10000.svg) | 8191 | 31.337<br>1.00x | 36.704<br>1.17x | 22.023<br>0.70x | 244.531<br>7.80x | 59.731<br>1.91x | 43.681<br>1.39x | 32.777<br>1.05x | 26.638<br>0.85x | 26.749<br>0.85x | **13.218<br>0.42x** |
| [flex/deep_random/10000](plots/flex/deep-random-10000.svg) | 8191 | 21.766<br>1.00x | 46.299<br>2.13x | 31.012<br>1.42x | 298.908<br>13.73x | 66.098<br>3.04x | 46.037<br>2.12x | 23.782<br>1.09x | 19.148<br>0.88x | 20.129<br>0.92x | **14.164<br>0.65x** |
| [flex/superdeep/50](plots/flex/superdeep-50.svg) | 151 | 0.887<br>1.00x | 0.965<br>1.09x | 0.968<br>1.09x | 9.092<br>10.25x | 2.646<br>2.98x | 2.555<br>2.88x | 0.566<br>0.64x | 0.637<br>0.72x | **0.557<br>0.63x** | 0.908<br>1.02x |
| [flex/superdeep/100](plots/flex/superdeep-100.svg) | 301 | 1.643<br>1.00x | 1.830<br>1.11x | 1.813<br>1.10x | 14.357<br>8.74x | 3.970<br>2.42x | 3.911<br>2.38x | 1.231<br>0.75x | 1.252<br>0.76x | **1.128<br>0.69x** | 1.988<br>1.21x |
| [grid/wide/31x31](plots/grid/wide-31x31.svg) | 962 | 4.206<br>1.00x | 7.519<br>1.79x | 5.207<br>1.24x | 38.194<br>9.08x | 10.676<br>2.54x | 7.773<br>1.85x | 3.799<br>0.90x | **3.183<br>0.76x** | 3.537<br>0.84x | 4.121<br>0.98x |
| [grid/wide/100x100](plots/grid/wide-100x100.svg) | 10001 | 52.179<br>1.00x | 84.961<br>1.63x | 54.093<br>1.04x | 420.984<br>8.07x | 93.444<br>1.79x | 68.838<br>1.32x | 37.890<br>0.73x | **28.510<br>0.55x** | 30.264<br>0.58x | 29.968<br>0.57x |
| [grid/deep/2x2x5](plots/grid/deep-2x2x5.svg) | 1365 | 9.816<br>1.00x | 16.183<br>1.65x | 13.673<br>1.39x | 78.055<br>7.95x | 17.219<br>1.75x | 14.444<br>1.47x | 6.198<br>0.63x | 5.548<br>0.57x | 5.618<br>0.57x | **3.572<br>0.36x** |
| [grid/deep/3x3x4](plots/grid/deep-3x3x4.svg) | 7381 | 43.876<br>1.00x | 73.490<br>1.67x | 57.924<br>1.32x | 486.598<br>11.09x | 98.902<br>2.25x | 63.903<br>1.46x | 34.216<br>0.78x | 28.130<br>0.64x | 26.515<br>0.60x | **16.697<br>0.38x** |
| [grid/superdeep/100](plots/grid/superdeep-100.svg) | 101 | 1.867<br>1.00x | 11.068<br>5.93x | 11.017<br>5.90x | 9.049<br>4.85x | 3.437<br>1.84x | 3.691<br>1.98x | 0.718<br>0.38x | 0.678<br>0.36x | 0.682<br>0.37x | **0.674<br>0.36x** |
| [pangui/expand_with_max_constraint](plots/pangui/expand-with-max-constraint.svg) | 3001 | 9.329<br>1.00x | 15.579<br>1.67x | 8.912<br>0.96x | 89.601<br>9.60x | 22.785<br>2.44x | 14.967<br>1.60x | 9.890<br>1.06x | 7.389<br>0.79x | 7.050<br>0.76x | **7.050<br>0.76x** |
| [pangui/expand_with_min_constraint](plots/pangui/expand-with-min-constraint.svg) | 3001 | 9.275<br>1.00x | 15.272<br>1.65x | 8.795<br>0.95x | 89.219<br>9.62x | 23.708<br>2.56x | 15.491<br>1.67x | 10.009<br>1.08x | 6.700<br>0.72x | 7.176<br>0.77x | **5.617<br>0.61x** |
| [pangui/fit_nesting](plots/pangui/fit-nesting.svg) | 101111 | 409.979<br>1.00x | 753.416<br>1.84x | 334.590<br>0.82x | 3969.771<br>9.68x | 1166.476<br>2.85x | 466.320<br>1.14x | 453.449<br>1.11x | 225.023<br>0.55x | 226.480<br>0.55x | **175.588<br>0.43x** |
| [pangui/flex_expand_equal_weights](plots/pangui/flex-expand-equal-weights.svg) | 15001 | 47.011<br>1.00x | 112.249<br>2.39x | 54.691<br>1.16x | 667.255<br>14.19x | 128.831<br>2.74x | 77.234<br>1.64x | 52.554<br>1.12x | 28.668<br>0.61x | 29.871<br>0.64x | **27.945<br>0.59x** |
| [pangui/flex_expand_weights](plots/pangui/flex-expand-weights.svg) | 15001 | 37.607<br>1.00x | 94.102<br>2.50x | 55.709<br>1.48x | 478.774<br>12.73x | 102.944<br>2.74x | 61.281<br>1.63x | 44.088<br>1.17x | 27.321<br>0.73x | 27.433<br>0.73x | **21.127<br>0.56x** |
| [pangui/nested_vertical_stack](plots/pangui/nested-vertical-stack.svg) | 10001 | 29.736<br>1.00x | 78.169<br>2.63x | 42.782<br>1.44x | 411.483<br>13.84x | 90.619<br>3.05x | 52.466<br>1.76x | 38.414<br>1.29x | **20.458<br>0.69x** | 20.605<br>0.69x | 23.422<br>0.79x |
| [pangui/padding_and_margin](plots/pangui/padding-and-margin.svg) | 101 | 0.535<br>1.00x | 0.851<br>1.59x | 0.580<br>1.08x | 7.536<br>14.09x | 2.284<br>4.27x | 2.237<br>4.18x | 0.371<br>0.69x | **0.285<br>0.53x** | 0.305<br>0.57x | 0.319<br>0.60x |
| [pangui/percentage_and_ratio](plots/pangui/percentage-and-ratio.svg) | 10001 | 38.544<br>1.00x | 76.015<br>1.97x | 40.023<br>1.04x | 414.354<br>10.75x | 84.826<br>2.20x | 51.730<br>1.34x | 34.371<br>0.89x | 20.682<br>0.54x | 19.584<br>0.51x | **18.768<br>0.49x** |
| [pangui/perpendicular_expand_with_wrap](plots/pangui/perpendicular-expand-with-wrap.svg) | 12001 | 41.363<br>1.00x | 87.691<br>2.12x | 49.326<br>1.19x | 514.259<br>12.43x | 97.599<br>2.36x | 59.356<br>1.44x | 43.678<br>1.06x | **28.384<br>0.69x** | 31.143<br>0.75x | 29.361<br>0.71x |
| [pangui/pixels_with_min_expand_constraint](plots/pangui/pixels-with-min-expand-constraint.svg) | 30001 | 92.657<br>1.00x | 173.982<br>1.88x | 86.617<br>0.93x | 1136.327<br>12.26x | 234.100<br>2.53x | 136.112<br>1.47x | 103.366<br>1.12x | 68.966<br>0.74x | 69.184<br>0.75x | **48.565<br>0.52x** |
| [pangui/wide_no_wrap_simple_few](plots/pangui/wide-no-wrap-simple-few.svg) | 1001 | 3.169<br>1.00x | 7.236<br>2.28x | 3.893<br>1.23x | 38.609<br>12.18x | 10.587<br>3.34x | 7.149<br>2.26x | 3.916<br>1.24x | 2.574<br>0.81x | 2.581<br>0.81x | **2.394<br>0.76x** |
| [pangui/wide_no_wrap_simple_many](plots/pangui/wide-no-wrap-simple-many.svg) | 100001 | 350.964<br>1.00x | 823.390<br>2.35x | 406.635<br>1.16x | 13366.166<br>38.08x | 829.673<br>2.36x | 483.712<br>1.38x | 406.965<br>1.16x | 212.851<br>0.61x | **196.564<br>0.56x** | 218.876<br>0.62x |
| [pangui/wide_wrapping](plots/pangui/wide-wrapping.svg) | 10001 | 32.327<br>1.00x | 71.854<br>2.22x | 37.408<br>1.16x | 419.038<br>12.96x | 97.175<br>3.01x | 59.316<br>1.83x | 37.195<br>1.15x | **22.314<br>0.69x** | 22.395<br>0.69x | 22.618<br>0.70x |
| [text/paragraphs/100](plots/text/paragraphs-100.svg) | 101 | 5.801<br>1.00x | 6.083<br>1.05x | 5.792<br>1.00x | 12.223<br>2.11x | 18.862<br>3.25x | 15.701<br>2.71x | 10.254<br>1.77x | 9.705<br>1.67x | 2.706<br>0.47x | **2.469<br>0.43x** |
| [text/flex_cards/100](plots/text/flex-cards-100.svg) | 301 | 4.132<br>1.00x | 5.572<br>1.35x | 5.130<br>1.24x | 12.120<br>2.93x | 8.828<br>2.14x | 7.669<br>1.86x | 4.785<br>1.16x | 4.673<br>1.13x | 2.354<br>0.57x | **1.706<br>0.41x** |
| [text/inline_mixed/100](plots/text/inline-mixed-100.svg) | 1599 | 10.933<br>1.00x | 15.289<br>1.40x | 14.729<br>1.35x | 33.850<br>3.10x | 29.739<br>2.72x | 17.187<br>1.57x | 14.073<br>1.29x | 13.857<br>1.27x | 4.535<br>0.41x | **4.282<br>0.39x** |
| [text/paragraphs/1000](plots/text/paragraphs-1000.svg) | 1001 | 54.096<br>1.00x | 45.737<br>0.85x | 42.976<br>0.79x | 115.013<br>2.13x | 195.547<br>3.61x | 151.396<br>2.80x | 92.230<br>1.70x | 85.801<br>1.59x | 23.689<br>0.44x | **20.552<br>0.38x** |
| [text/flex_cards/1000](plots/text/flex-cards-1000.svg) | 3001 | 37.563<br>1.00x | 37.801<br>1.01x | 33.105<br>0.88x | 101.105<br>2.69x | 84.286<br>2.24x | 64.761<br>1.72x | 46.806<br>1.25x | 43.982<br>1.17x | 20.899<br>0.56x | **14.071<br>0.37x** |
| [text/inline_mixed/1000](plots/text/inline-mixed-1000.svg) | 16361 | 102.112<br>1.00x | 116.227<br>1.14x | 107.473<br>1.05x | 322.130<br>3.15x | 317.981<br>3.11x | 149.084<br>1.46x | 136.490<br>1.34x | 133.616<br>1.31x | 43.489<br>0.43x | **36.394<br>0.36x** |
| [real/wikipedia](plots/real/wikipedia.svg) | 21889 | 223.583<br>1.00x | 268.227<br>1.20x | 215.415<br>0.96x | 855.225<br>3.83x | 326.465<br>1.46x | 143.624<br>0.64x | 126.646<br>0.57x | 95.394<br>0.43x | **50.230<br>0.22x** | 53.917<br>0.24x |
| [real/mdn](plots/real/mdn.svg) | 2212 | 18.542<br>1.00x | 20.064<br>1.08x | 17.299<br>0.93x | 125.011<br>6.74x | 28.363<br>1.53x | 16.228<br>0.88x | 12.705<br>0.69x | 12.021<br>0.65x | 8.402<br>0.45x | **6.126<br>0.33x** |
| [real/rustdoc](plots/real/rustdoc.svg) | 15947 | 121.984<br>1.00x | 153.062<br>1.25x | 117.769<br>0.97x | 724.302<br>5.94x | 232.734<br>1.91x | 123.326<br>1.01x | 93.019<br>0.76x | 79.643<br>0.65x | 46.916<br>0.38x | **44.105<br>0.36x** |
| [real/css-flexbox-1](plots/real/css-flexbox-1.svg) | 15890 | 117.134<br>1.00x | 130.729<br>1.12x | 119.073<br>1.02x | 442.204<br>3.78x | 201.490<br>1.72x | 138.142<br>1.18x | 98.218<br>0.84x | 97.928<br>0.84x | **53.765<br>0.46x** | 77.271<br>0.66x |
| [real/servo-org](plots/real/servo-org.svg) | 226 | 3.192<br>1.00x | 5.959<br>1.87x | 5.867<br>1.84x | 20.932<br>6.56x | 6.287<br>1.97x | 5.210<br>1.63x | 2.129<br>0.67x | 1.991<br>0.62x | 1.621<br>0.51x | **1.517<br>0.48x** |
| [real/dioxuslabs-com](plots/real/dioxuslabs-com.svg) | 158 | 4.226<br>1.00x | 6.442<br>1.52x | 6.441<br>1.52x | 35.370<br>8.37x | 6.249<br>1.48x | 6.864<br>1.62x | 2.072<br>0.49x | 2.018<br>0.48x | 2.131<br>0.50x | **1.966<br>0.47x** |
| [real/bootstrap-dashboard](plots/real/bootstrap-dashboard.svg) | 199 | 2.631<br>1.00x | 3.471<br>1.32x | 3.616<br>1.37x | 15.213<br>5.78x | 4.030<br>1.53x | 4.122<br>1.57x | 2.554<br>0.97x | 2.521<br>0.96x | 2.314<br>0.88x | **2.132<br>0.81x** |

### Sample spread

Median ÷ min of the samples behind each cell above (1.00 = all samples equal), per engine on blitz `layout`, blitz-par `style`, blitz-par-pcon `resolve`, blitz-par-pcon-pl `layout`, blitz-pcon `construct`, blitz-pcon-pl1 `layout`, chrome `layout`, firefox `layout`, firefox1 `layout`, ladybird `layout`, servo `fragment`, servo1 `fragment`, taffy `layout`.

| case | blitz | blitz-par | blitz-par-pcon | blitz-par-pcon-pl | blitz-pcon | blitz-pcon-pl1 | chrome | firefox | firefox1 | ladybird | servo | servo1 | taffy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| flex/huge_nested/1000 | 1.08 | 1.79 | 1.41 | 1.17 | 1.08 | 1.21 | 1.02 | 1.07 | 1.09 | 1.03 | 1.15 | 1.11 | 1.02 |
| flex/wide/1000 | 1.05 | 1.33 | 1.26 | 1.43 | 1.11 | 1.16 | 1.02 | 1.07 | 1.07 | 1.02 | 1.28 | 1.23 | 1.02 |
| flex/absolute/1000 | 1.08 | 1.71 | 1.42 | 1.50 | 1.08 | 1.32 | 1.02 | 1.11 | 1.07 | 1.06 | 1.06 | 1.04 | 1.02 |
| flex/deep_auto/1000 | 1.08 | 1.37 | 1.64 | 1.37 | 1.19 | 1.06 | 1.01 | 1.06 | 1.03 | 1.06 | 1.03 | 1.05 | 1.01 |
| flex/deep_random/1000 | 2.56 | 1.34 | 1.27 | 1.19 | 1.12 | 1.16 | 1.02 | 1.03 | 1.05 | 1.01 | 1.16 | 1.15 | 1.01 |
| flex/huge_nested/10000 | 1.18 | 1.16 | 1.12 | 1.48 | 1.30 | 1.80 | 1.01 | 1.02 | 1.08 | 1.01 | 1.26 | 1.10 | 1.00 |
| flex/wide/10000 | 1.08 | 1.27 | 1.17 | 1.24 | 1.38 | 1.18 | 1.04 | 1.02 | 1.14 | 1.01 | 1.22 | 1.14 | 1.00 |
| flex/absolute/10000 | 1.88 | 1.31 | 1.14 | 1.21 | 1.24 | 1.19 | 1.06 | 1.04 | 1.03 | 1.03 | 1.13 | 1.08 | 1.00 |
| flex/deep_auto/10000 | 1.08 | 1.16 | 1.08 | 1.91 | 1.22 | 1.25 | 1.02 | 1.03 | 1.13 | 1.03 | 1.11 | 1.11 | 1.00 |
| flex/deep_random/10000 | 1.12 | 1.21 | 1.07 | 1.25 | 1.34 | 1.18 | 1.17 | 1.09 | 1.04 | 1.03 | 1.22 | 1.23 | 1.00 |
| flex/superdeep/50 | 1.16 | 1.21 | 1.29 | 1.11 | 1.21 | 1.18 | 1.09 | 1.22 | 1.09 | 1.02 | 1.09 | 1.08 | 1.07 |
| flex/superdeep/100 | 1.14 | 1.10 | 1.23 | 1.27 | 1.19 | 1.32 | 1.05 | 1.05 | 1.04 | 1.01 | 1.10 | 1.16 | 1.02 |
| grid/wide/31x31 | 1.25 | 1.74 | 1.43 | 1.06 | 1.23 | 1.39 | 1.04 | 1.03 | 1.02 | 1.01 | 1.10 | 1.04 | 1.01 |
| grid/wide/100x100 | 1.09 | 1.19 | 1.11 | 1.24 | 1.41 | 1.27 | 1.04 | 1.04 | 1.08 | 1.03 | 1.10 | 1.09 | 1.02 |
| grid/deep/2x2x5 | 1.10 | 1.10 | 1.08 | 1.13 | 1.03 | 1.08 | 1.03 | 1.02 | 1.01 | 1.01 | 1.12 | 1.20 | 1.04 |
| grid/deep/3x3x4 | 1.06 | 1.15 | 1.14 | 1.15 | 1.14 | 1.10 | 1.01 | 1.05 | 1.06 | 1.07 | 1.30 | 1.09 | 1.01 |
| grid/superdeep/100 | 1.34 | 1.24 | 1.12 | 1.31 | 1.29 | 1.13 | 1.04 | 1.05 | 1.03 | 1.05 | 1.18 | 1.06 | 1.07 |
| pangui/expand_with_max_constraint | 1.06 | 1.84 | 1.11 | 1.35 | 1.09 | 1.09 | 1.02 | 1.02 | 1.04 | 1.03 | 1.09 | 1.10 | 1.01 |
| pangui/expand_with_min_constraint | 1.12 | 1.52 | 1.29 | 1.49 | 1.12 | 1.17 | 1.04 | 1.04 | 1.03 | 1.10 | 1.13 | 1.16 | 1.01 |
| pangui/fit_nesting | 1.06 | 1.19 | 1.14 | 1.12 | 1.02 | 1.08 | 1.05 | 1.06 | 1.05 | 1.02 | 1.08 | 1.07 | 1.01 |
| pangui/flex_expand_equal_weights | 1.29 | 1.23 | 1.07 | 1.18 | 1.27 | 1.22 | 1.05 | 1.12 | 1.10 | 1.06 | 1.22 | 1.12 | 1.01 |
| pangui/flex_expand_weights | 1.12 | 1.19 | 1.20 | 1.21 | 1.11 | 1.14 | 1.07 | 1.03 | 1.13 | 1.03 | 1.13 | 1.21 | 1.00 |
| pangui/nested_vertical_stack | 1.18 | 1.22 | 1.11 | 1.24 | 1.62 | 1.28 | 1.08 | 1.08 | 1.09 | 1.03 | 1.09 | 1.08 | 1.01 |
| pangui/padding_and_margin | 1.29 | 1.07 | 1.14 | 1.07 | 1.26 | 1.28 | 1.07 | 1.10 | 1.08 | 1.03 | 1.13 | 1.16 | 1.03 |
| pangui/percentage_and_ratio | 1.08 | 1.14 | 1.23 | 1.21 | 1.44 | 1.15 | 1.05 | 1.06 | 1.05 | 1.03 | 1.11 | 1.12 | 1.01 |
| pangui/perpendicular_expand_with_wrap | 1.10 | 1.21 | 1.26 | 1.19 | 1.28 | 1.10 | 1.05 | 1.05 | 1.09 | 1.06 | 1.20 | 1.10 | 1.03 |
| pangui/pixels_with_min_expand_constraint | 1.08 | 1.13 | 1.11 | 1.21 | 1.26 | 1.13 | 1.03 | 1.06 | 1.15 | 1.03 | 1.14 | 1.05 | 1.01 |
| pangui/wide_no_wrap_simple_few | 1.63 | 1.56 | 1.18 | 1.51 | 1.22 | 1.82 | 1.05 | 1.03 | 1.06 | 1.08 | 1.14 | 1.08 | 1.02 |
| pangui/wide_no_wrap_simple_many | 1.03 | 1.23 | 1.17 | 1.17 | 1.08 | 1.13 | 1.05 | 1.22 | 1.08 | 1.06 | 1.19 | 1.17 | 1.03 |
| pangui/wide_wrapping | 1.12 | 1.37 | 1.16 | 1.15 | 1.08 | 1.22 | 1.04 | 1.02 | 1.16 | 1.04 | 1.46 | 1.23 | 1.01 |
| text/paragraphs/100 | 1.21 | 1.15 | 1.59 | 1.24 | 1.49 | 1.34 | 1.01 | 1.04 | 1.03 | 1.01 | 1.12 | 1.28 | - |
| text/flex_cards/100 | 1.05 | 1.15 | 1.15 | 1.08 | 1.88 | 1.14 | 1.09 | 1.10 | 1.04 | 1.01 | 1.44 | 1.12 | - |
| text/inline_mixed/100 | 1.06 | 1.71 | 1.80 | 1.55 | 1.58 | 1.36 | 1.03 | 1.07 | 1.05 | 1.03 | 1.28 | 1.08 | - |
| text/paragraphs/1000 | 1.07 | 1.03 | 1.15 | 1.19 | 1.24 | 1.27 | 1.07 | 1.07 | 1.04 | 1.03 | 1.56 | 1.18 | - |
| text/flex_cards/1000 | 1.14 | 1.42 | 1.31 | 1.28 | 1.25 | 1.10 | 1.03 | 1.08 | 1.04 | 1.03 | 1.12 | 1.21 | - |
| text/inline_mixed/1000 | 1.09 | 1.23 | 1.08 | 1.47 | 1.19 | 1.13 | 1.01 | 1.04 | 1.06 | 1.02 | 1.27 | 1.12 | - |
| real/wikipedia | 1.30 | 1.16 | 1.18 | 1.18 | 1.32 | 1.14 | 1.13 | 1.08 | 1.03 | 1.04 | 1.37 | 1.42 | - |
| real/mdn | 1.08 | 1.51 | 1.24 | 1.22 | 1.15 | 1.18 | 1.03 | 1.03 | 1.06 | 1.03 | 1.53 | 1.19 | - |
| real/rustdoc | 2.12 | 1.07 | 1.19 | 1.07 | 1.19 | 1.02 | 1.06 | 1.06 | 1.06 | 1.03 | 1.66 | 1.21 | - |
| real/css-flexbox-1 | 1.11 | 1.24 | 1.18 | 1.65 | 1.36 | 1.26 | 1.03 | 1.02 | 1.10 | 1.04 | 1.21 | 1.18 | - |
| real/servo-org | 1.12 | 1.06 | 1.16 | 1.26 | 1.75 | 1.34 | 1.05 | 1.16 | 1.09 | 1.01 | 1.19 | 1.15 | - |
| real/dioxuslabs-com | 1.15 | 1.14 | 1.12 | 1.22 | 1.64 | 1.23 | 1.44 | 1.05 | 1.09 | 1.06 | 2.01 | 1.21 | - |
| real/bootstrap-dashboard | 1.09 | 1.47 | 1.72 | 1.93 | 2.62 | 1.37 | 1.06 | 1.03 | 1.06 | 1.08 | 3.24 | 1.45 | - |
| **median case** | 1.11 | 1.22 | 1.17 | 1.22 | 1.24 | 1.18 | 1.04 | 1.05 | 1.06 | 1.03 | 1.16 | 1.12 | 1.01 |
| **p90 case** | 1.52 | 1.71 | 1.52 | 1.53 | 1.64 | 1.37 | 1.09 | 1.12 | 1.13 | 1.06 | 1.55 | 1.23 | 1.04 |
