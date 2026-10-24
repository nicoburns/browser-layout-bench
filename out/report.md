Times in ms, min over all rounds and iterations; second line of each cell is the multiple of the Chrome column of the same table (1.00x = Chrome); bold = fastest engine of the row, Taffy excluded. Servo(n) = `layout_threads=n`. Text shaping is in the layout phase of Chrome, Firefox and Ladybird but in the construction phase of Blitz and Servo, so "Layout only" is like-for-like only among Servo/Blitz/Taffy and "Box construction + layout" is the comparable table for text-bearing cases; Firefox's Reflow (shaping + layout; its frame construction is inside Styles) is listed there. Case names link to the case's bar chart; one page of charts per suite: [flex/](plots/flex.md) · [grid/](plots/grid.md) · [pangui/](plots/pangui.md) · [text/](plots/text.md) · [real/](plots/real.md). webkit were measured in a later run and scaled per case by Chrome's stored/new `style+layout` ratio (median 1.14; see README, Versions and methodology): differences under ~10% between those and the other columns are within the normalisation's uncertainty.

### Layout only

| case | nodes | Chrome<br>Layout (incl. shaping) | Ladybird<br>layout (incl. shaping) | Servo(1)<br>Fragment Tree | Servo(3)<br>Fragment Tree | Blitz<br>`layout` | Blitz<br>`layout` (#1034 build, 1 thread) | Blitz<br>`layout` (#1034 build, parallel) | Taffy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [flex/huge_nested/1000](plots/flex/huge-nested-1000.svg) | 911 | 1.027<br>1.00x | 4.961<br>4.83x | 1.291<br>1.26x | 0.980<br>0.95x | 0.718<br>0.70x | 0.870<br>0.85x | **0.387<br>0.38x** | 0.284<br>0.28x |
| [flex/wide/1000](plots/flex/wide-1000.svg) | 1000 | 1.342<br>1.00x | 6.963<br>5.19x | 1.745<br>1.30x | 1.802<br>1.34x | 1.101<br>0.82x | 1.449<br>1.08x | **0.884<br>0.66x** | 0.493<br>0.37x |
| [flex/absolute/1000](plots/flex/absolute-1000.svg) | 1003 | 1.454<br>1.00x | 4.514<br>3.10x | 1.538<br>1.06x | 1.629<br>1.12x | 0.846<br>0.58x | 1.030<br>0.71x | **0.701<br>0.48x** | 0.331<br>0.23x |
| [flex/deep_auto/1000](plots/flex/deep-auto-1000.svg) | 767 | 1.916<br>1.00x | 7.543<br>3.94x | 1.905<br>0.99x | 1.670<br>0.87x | 1.902<br>0.99x | 2.409<br>1.26x | **0.760<br>0.40x** | 0.997<br>0.52x |
| [flex/deep_random/1000](plots/flex/deep-random-1000.svg) | 767 | 1.025<br>1.00x | 6.052<br>5.90x | 1.300<br>1.27x | 1.295<br>1.26x | 0.823<br>0.80x | 1.156<br>1.13x | **0.501<br>0.49x** | 0.420<br>0.41x |
| [flex/huge_nested/10000](plots/flex/huge-nested-10000.svg) | 9111 | 9.327<br>1.00x | 47.795<br>5.12x | 13.647<br>1.46x | 8.145<br>0.87x | 7.189<br>0.77x | 8.205<br>0.88x | **2.372<br>0.25x** | 3.407<br>0.37x |
| [flex/wide/10000](plots/flex/wide-10000.svg) | 10001 | 14.113<br>1.00x | 73.754<br>5.23x | 18.122<br>1.28x | 18.902<br>1.34x | 12.450<br>0.88x | 15.040<br>1.07x | **7.630<br>0.54x** | 5.765<br>0.41x |
| [flex/absolute/10000](plots/flex/absolute-10000.svg) | 10004 | 15.873<br>1.00x | 55.807<br>3.52x | 15.989<br>1.01x | 16.837<br>1.06x | 9.034<br>0.57x | 11.057<br>0.70x | **6.770<br>0.43x** | 4.293<br>0.27x |
| [flex/deep_auto/10000](plots/flex/deep-auto-10000.svg) | 8191 | 19.028<br>1.00x | 76.103<br>4.00x | 18.855<br>0.99x | 18.819<br>0.99x | 20.296<br>1.07x | 23.586<br>1.24x | **5.097<br>0.27x** | 11.589<br>0.61x |
| [flex/deep_random/10000](plots/flex/deep-random-10000.svg) | 8191 | 9.427<br>1.00x | 62.646<br>6.65x | 13.951<br>1.48x | 14.457<br>1.53x | 8.909<br>0.95x | 10.896<br>1.16x | **3.367<br>0.36x** | 5.015<br>0.53x |
| [flex/superdeep/50](plots/flex/superdeep-50.svg) | 151 | 0.507<br>1.00x | 1.867<br>3.68x | 0.363<br>0.72x | 0.387<br>0.76x | **0.345<br>0.68x** | 0.498<br>0.98x | 0.692<br>1.37x | 0.155<br>0.30x |
| [flex/superdeep/100](plots/flex/superdeep-100.svg) | 301 | 0.954<br>1.00x | 3.610<br>3.78x | 0.734<br>0.77x | 0.760<br>0.80x | **0.671<br>0.70x** | 0.939<br>0.98x | 1.370<br>1.44x | 0.321<br>0.34x |
| [grid/wide/31x31](plots/grid/wide-31x31.svg) | 962 | 3.034<br>1.00x | 6.289<br>2.07x | 2.900<br>0.96x | 2.903<br>0.96x | **1.580<br>0.52x** | 2.125<br>0.70x | 2.004<br>0.66x | 0.658<br>0.22x |
| [grid/wide/100x100](plots/grid/wide-100x100.svg) | 10001 | 39.768<br>1.00x | 73.161<br>1.84x | 30.999<br>0.78x | 31.918<br>0.80x | **18.264<br>0.46x** | 24.733<br>0.62x | 20.653<br>0.52x | 8.462<br>0.21x |
| [grid/deep/2x2x5](plots/grid/deep-2x2x5.svg) | 1365 | 7.491<br>1.00x | 15.487<br>2.07x | 8.183<br>1.09x | 8.606<br>1.15x | 3.915<br>0.52x | 5.352<br>0.71x | **1.693<br>0.23x** | 2.788<br>0.37x |
| [grid/deep/3x3x4](plots/grid/deep-3x3x4.svg) | 7381 | 33.134<br>1.00x | 79.885<br>2.41x | 40.368<br>1.22x | 42.765<br>1.29x | 17.870<br>0.54x | 25.173<br>0.76x | **6.612<br>0.20x** | 13.378<br>0.40x |
| [grid/superdeep/100](plots/grid/superdeep-100.svg) | 101 | 1.637<br>1.00x | 2.881<br>1.76x | 1.439<br>0.88x | 1.395<br>0.85x | **0.514<br>0.31x** | 0.689<br>0.42x | 0.608<br>0.37x | 0.388<br>0.24x |
| [pangui/expand_with_max_constraint](plots/pangui/expand-with-max-constraint.svg) | 3001 | 3.775<br>1.00x | 12.074<br>3.20x | 5.718<br>1.51x | 5.893<br>1.56x | 3.746<br>0.99x | 4.367<br>1.16x | **2.331<br>0.62x** | 1.529<br>0.41x |
| [pangui/expand_with_min_constraint](plots/pangui/expand-with-min-constraint.svg) | 3001 | 3.799<br>1.00x | 11.101<br>2.92x | 5.678<br>1.49x | 5.713<br>1.50x | 3.743<br>0.99x | 4.228<br>1.11x | **2.510<br>0.66x** | 1.572<br>0.41x |
| [pangui/fit_nesting](plots/pangui/fit-nesting.svg) | 101111 | 140.254<br>1.00x | 421.292<br>3.00x | 358.681<br>2.56x | 150.004<br>1.07x | 89.950<br>0.64x | 96.777<br>0.69x | **25.311<br>0.18x** | 42.042<br>0.30x |
| [pangui/flex_expand_equal_weights](plots/pangui/flex-expand-equal-weights.svg) | 15001 | 13.153<br>1.00x | 49.154<br>3.74x | 16.627<br>1.26x | 17.776<br>1.35x | **8.592<br>0.65x** | 10.301<br>0.78x | 9.199<br>0.70x | 4.075<br>0.31x |
| [pangui/flex_expand_weights](plots/pangui/flex-expand-weights.svg) | 15001 | 12.118<br>1.00x | 41.164<br>3.40x | 21.520<br>1.78x | 21.630<br>1.78x | 13.057<br>1.08x | 14.638<br>1.21x | **6.460<br>0.53x** | 6.174<br>0.51x |
| [pangui/nested_vertical_stack](plots/pangui/nested-vertical-stack.svg) | 10001 | 8.100<br>1.00x | 37.582<br>4.64x | 15.554<br>1.92x | 15.673<br>1.93x | **7.770<br>0.96x** | 10.426<br>1.29x | 8.725<br>1.08x | 2.615<br>0.32x |
| [pangui/padding_and_margin](plots/pangui/padding-and-margin.svg) | 101 | 0.156<br>1.00x | 0.668<br>4.28x | 0.197<br>1.26x | 0.223<br>1.43x | **0.072<br>0.46x** | 0.085<br>0.55x | 0.092<br>0.59x | 0.020<br>0.13x |
| [pangui/percentage_and_ratio](plots/pangui/percentage-and-ratio.svg) | 10001 | 15.325<br>1.00x | 33.271<br>2.17x | 13.766<br>0.90x | 13.813<br>0.90x | **6.321<br>0.41x** | 8.647<br>0.56x | 6.724<br>0.44x | 2.637<br>0.17x |
| [pangui/perpendicular_expand_with_wrap](plots/pangui/perpendicular-expand-with-wrap.svg) | 12001 | 16.162<br>1.00x | 46.200<br>2.86x | 15.134<br>0.94x | 14.140<br>0.87x | **12.759<br>0.79x** | 15.753<br>0.97x | 13.406<br>0.83x | 3.740<br>0.23x |
| [pangui/pixels_with_min_expand_constraint](plots/pangui/pixels-with-min-expand-constraint.svg) | 30001 | 40.769<br>1.00x | 121.605<br>2.98x | 57.240<br>1.40x | 60.407<br>1.48x | 38.167<br>0.94x | 50.490<br>1.24x | **20.220<br>0.50x** | 17.200<br>0.42x |
| [pangui/wide_no_wrap_simple_few](plots/pangui/wide-no-wrap-simple-few.svg) | 1001 | 0.871<br>1.00x | 2.920<br>3.35x | 1.174<br>1.35x | 1.217<br>1.40x | **0.574<br>0.66x** | 1.006<br>1.16x | 0.894<br>1.03x | 0.200<br>0.23x |
| [pangui/wide_no_wrap_simple_many](plots/pangui/wide-no-wrap-simple-many.svg) | 100001 | 93.773<br>1.00x | 361.384<br>3.85x | 147.564<br>1.57x | 139.838<br>1.49x | **91.088<br>0.97x** | 126.143<br>1.35x | 91.173<br>0.97x | 32.157<br>0.34x |
| [pangui/wide_wrapping](plots/pangui/wide-wrapping.svg) | 10001 | 10.166<br>1.00x | 35.474<br>3.49x | 11.695<br>1.15x | 11.538<br>1.13x | **8.040<br>0.79x** | 10.484<br>1.03x | 10.067<br>0.99x | 2.662<br>0.26x |
| [text/paragraphs/100](plots/text/paragraphs-100.svg) | 101 | 5.969<br>1.00x | 9.914<br>1.66x | 2.603<br>0.44x | 1.268<br>0.21x | 0.770<br>0.13x | 0.859<br>0.14x | **0.228<br>0.04x** | - |
| [text/flex_cards/100](plots/text/flex-cards-100.svg) | 301 | 4.045<br>1.00x | 7.507<br>1.86x | 1.888<br>0.47x | 2.168<br>0.54x | 1.046<br>0.26x | 1.245<br>0.31x | **0.397<br>0.10x** | - |
| [text/inline_mixed/100](plots/text/inline-mixed-100.svg) | 1599 | 10.927<br>1.00x | 21.140<br>1.93x | 7.529<br>0.69x | 2.816<br>0.26x | 0.912<br>0.08x | 0.965<br>0.09x | **0.271<br>0.02x** | - |
| [text/paragraphs/1000](plots/text/paragraphs-1000.svg) | 1001 | 56.700<br>1.00x | 102.838<br>1.81x | 27.610<br>0.49x | 11.911<br>0.21x | 7.732<br>0.14x | 8.060<br>0.14x | **1.869<br>0.03x** | - |
| [text/flex_cards/1000](plots/text/flex-cards-1000.svg) | 3001 | 37.506<br>1.00x | 69.802<br>1.86x | 16.227<br>0.43x | 16.199<br>0.43x | 11.081<br>0.30x | 11.996<br>0.32x | **3.429<br>0.09x** | - |
| [text/inline_mixed/1000](plots/text/inline-mixed-1000.svg) | 16361 | 91.325<br>1.00x | 212.138<br>2.32x | 51.054<br>0.56x | 20.331<br>0.22x | 9.322<br>0.10x | 10.258<br>0.11x | **2.343<br>0.03x** | - |
| [real/wikipedia](plots/real/wikipedia.svg) | 21889 | 173.262<br>1.00x | 475.055<br>2.74x | 54.802<br>0.32x | 43.177<br>0.25x | 18.137<br>0.10x | 19.947<br>0.12x | **15.669<br>0.09x** | - |
| [real/mdn](plots/real/mdn.svg) | 2212 | 13.027<br>1.00x | 50.931<br>3.91x | 7.719<br>0.59x | 3.007<br>0.23x | 3.431<br>0.26x | 4.110<br>0.32x | **1.569<br>0.12x** | - |
| [real/rustdoc](plots/real/rustdoc.svg) | 15947 | 99.762<br>1.00x | 410.171<br>4.11x | 52.621<br>0.53x | 46.162<br>0.46x | 26.614<br>0.27x | 27.839<br>0.28x | **22.521<br>0.23x** | - |
| [real/css-flexbox-1](plots/real/css-flexbox-1.svg) | 15890 | 96.867<br>1.00x | 231.182<br>2.39x | 48.460<br>0.50x | 44.241<br>0.46x | 24.860<br>0.26x | 25.626<br>0.26x | **22.674<br>0.23x** | - |
| [real/servo-org](plots/real/servo-org.svg) | 226 | 2.399<br>1.00x | 4.897<br>2.04x | 2.580<br>1.08x | 1.446<br>0.60x | 0.423<br>0.18x | 0.573<br>0.24x | **0.260<br>0.11x** | - |
| [real/dioxuslabs-com](plots/real/dioxuslabs-com.svg) | 158 | 3.241<br>1.00x | 17.317<br>5.34x | 3.046<br>0.94x | 1.010<br>0.31x | 0.454<br>0.14x | 0.627<br>0.19x | **0.321<br>0.10x** | - |
| [real/bootstrap-dashboard](plots/real/bootstrap-dashboard.svg) | 199 | 1.882<br>1.00x | 3.081<br>1.64x | 2.178<br>1.16x | 1.052<br>0.56x | 0.623<br>0.33x | 0.817<br>0.43x | **0.516<br>0.27x** | - |

### Construction

| case | nodes | Chrome<br>rebuildLayoutTree | Ladybird<br>tree build | Servo(1)<br>Box Tree | Servo(3)<br>Box Tree | Blitz<br>construct ( + pconstruct) | Blitz<br>construct, parallel |
|---|---:|---:|---:|---:|---:|---:|---:|
| [flex/huge_nested/1000](plots/flex/huge-nested-1000.svg) | 911 | 0.373<br>1.00x | 0.646<br>1.73x | 0.925<br>2.48x | 0.471<br>1.26x | **0.056<br>0.15x** | 0.058<br>0.16x |
| [flex/wide/1000](plots/flex/wide-1000.svg) | 1000 | 0.397<br>1.00x | 0.735<br>1.85x | 1.097<br>2.76x | 0.712<br>1.79x | 0.074<br>0.19x | **0.071<br>0.18x** |
| [flex/absolute/1000](plots/flex/absolute-1000.svg) | 1003 | 0.637<br>1.00x | 0.787<br>1.24x | 1.271<br>2.00x | 0.723<br>1.13x | **0.067<br>0.11x** | 0.071<br>0.11x |
| [flex/deep_auto/1000](plots/flex/deep-auto-1000.svg) | 767 | 0.350<br>1.00x | 0.638<br>1.82x | 1.116<br>3.19x | 1.161<br>3.32x | **0.060<br>0.17x** | 0.062<br>0.18x |
| [flex/deep_random/1000](plots/flex/deep-random-1000.svg) | 767 | 0.337<br>1.00x | 0.636<br>1.89x | 1.184<br>3.51x | 1.218<br>3.62x | **0.064<br>0.19x** | 0.066<br>0.19x |
| [flex/huge_nested/10000](plots/flex/huge-nested-10000.svg) | 9111 | 3.898<br>1.00x | 6.834<br>1.75x | 8.397<br>2.15x | 3.400<br>0.87x | **0.668<br>0.17x** | 0.676<br>0.17x |
| [flex/wide/10000](plots/flex/wide-10000.svg) | 10001 | 3.806<br>1.00x | 7.901<br>2.08x | 10.123<br>2.66x | 6.015<br>1.58x | 0.948<br>0.25x | **0.842<br>0.22x** |
| [flex/absolute/10000](plots/flex/absolute-10000.svg) | 10004 | 6.579<br>1.00x | 9.897<br>1.50x | 12.996<br>1.98x | 7.161<br>1.09x | 0.869<br>0.13x | **0.822<br>0.12x** |
| [flex/deep_auto/10000](plots/flex/deep-auto-10000.svg) | 8191 | 3.836<br>1.00x | 7.062<br>1.84x | 10.351<br>2.70x | 10.036<br>2.62x | 0.746<br>0.19x | **0.742<br>0.19x** |
| [flex/deep_random/10000](plots/flex/deep-random-10000.svg) | 8191 | 3.415<br>1.00x | 7.457<br>2.18x | 9.786<br>2.87x | 10.296<br>3.01x | 0.919<br>0.27x | **0.872<br>0.26x** |
| [flex/superdeep/50](plots/flex/superdeep-50.svg) | 151 | 0.097<br>1.00x | 0.214<br>2.21x | 0.305<br>3.15x | 0.313<br>3.23x | 0.011<br>0.12x | **0.011<br>0.12x** |
| [flex/superdeep/100](plots/flex/superdeep-100.svg) | 301 | 0.204<br>1.00x | 0.491<br>2.41x | 0.580<br>2.84x | 0.610<br>2.99x | **0.019<br>0.10x** | 0.020<br>0.10x |
| [grid/wide/31x31](plots/grid/wide-31x31.svg) | 962 | 0.374<br>1.00x | 0.696<br>1.86x | 0.891<br>2.38x | 1.019<br>2.73x | **0.052<br>0.14x** | 0.053<br>0.14x |
| [grid/wide/100x100](plots/grid/wide-100x100.svg) | 10001 | 3.680<br>1.00x | 8.151<br>2.21x | 10.817<br>2.94x | 10.550<br>2.87x | 1.161<br>0.32x | **1.085<br>0.29x** |
| [grid/deep/2x2x5](plots/grid/deep-2x2x5.svg) | 1365 | 0.594<br>1.00x | 1.047<br>1.76x | 1.523<br>2.56x | 0.722<br>1.22x | 0.104<br>0.18x | **0.101<br>0.17x** |
| [grid/deep/3x3x4](plots/grid/deep-3x3x4.svg) | 7381 | 2.988<br>1.00x | 5.898<br>1.97x | 8.757<br>2.93x | 3.385<br>1.13x | **0.578<br>0.19x** | 0.595<br>0.20x |
| [grid/superdeep/100](plots/grid/superdeep-100.svg) | 101 | 0.103<br>1.00x | 0.229<br>2.22x | 0.454<br>4.41x | 0.506<br>4.91x | **0.011<br>0.10x** | 0.012<br>0.12x |
| [pangui/expand_with_max_constraint](plots/pangui/expand-with-max-constraint.svg) | 3001 | 1.237<br>1.00x | 2.059<br>1.66x | 3.364<br>2.72x | 1.953<br>1.58x | 0.233<br>0.19x | **0.222<br>0.18x** |
| [pangui/expand_with_min_constraint](plots/pangui/expand-with-min-constraint.svg) | 3001 | 1.245<br>1.00x | 2.032<br>1.63x | 3.360<br>2.70x | 1.926<br>1.55x | 0.235<br>0.19x | **0.212<br>0.17x** |
| [pangui/fit_nesting](plots/pangui/fit-nesting.svg) | 101111 | 43.571<br>1.00x | 98.657<br>2.26x | 93.949<br>2.16x | 32.745<br>0.75x | 11.455<br>0.26x | **10.975<br>0.25x** |
| [pangui/flex_expand_equal_weights](plots/pangui/flex-expand-equal-weights.svg) | 15001 | 6.294<br>1.00x | 12.959<br>2.06x | 14.238<br>2.26x | 14.650<br>2.33x | 2.032<br>0.32x | **1.967<br>0.31x** |
| [pangui/flex_expand_weights](plots/pangui/flex-expand-weights.svg) | 15001 | 6.435<br>1.00x | 12.090<br>1.88x | 18.691<br>2.90x | 10.292<br>1.60x | 1.340<br>0.21x | **1.202<br>0.19x** |
| [pangui/nested_vertical_stack](plots/pangui/nested-vertical-stack.svg) | 10001 | 4.021<br>1.00x | 7.954<br>1.98x | 8.748<br>2.18x | 10.537<br>2.62x | **1.069<br>0.27x** | 1.082<br>0.27x |
| [pangui/padding_and_margin](plots/pangui/padding-and-margin.svg) | 101 | 0.066<br>1.00x | 0.114<br>1.72x | 0.139<br>2.10x | 0.179<br>2.71x | **0.006<br>0.09x** | 0.008<br>0.12x |
| [pangui/percentage_and_ratio](plots/pangui/percentage-and-ratio.svg) | 10001 | 4.605<br>1.00x | 7.482<br>1.62x | 9.158<br>1.99x | 9.691<br>2.10x | **1.189<br>0.26x** | 1.316<br>0.29x |
| [pangui/perpendicular_expand_with_wrap](plots/pangui/perpendicular-expand-with-wrap.svg) | 12001 | 5.458<br>1.00x | 9.701<br>1.78x | 10.910<br>2.00x | 11.174<br>2.05x | 1.476<br>0.27x | **1.417<br>0.26x** |
| [pangui/pixels_with_min_expand_constraint](plots/pangui/pixels-with-min-expand-constraint.svg) | 30001 | 14.070<br>1.00x | 23.990<br>1.71x | 39.654<br>2.82x | 20.560<br>1.46x | **3.138<br>0.22x** | 3.679<br>0.26x |
| [pangui/wide_no_wrap_simple_few](plots/pangui/wide-no-wrap-simple-few.svg) | 1001 | 0.403<br>1.00x | 0.721<br>1.79x | 0.817<br>2.03x | 0.858<br>2.13x | **0.056<br>0.14x** | 0.059<br>0.15x |
| [pangui/wide_no_wrap_simple_many](plots/pangui/wide-no-wrap-simple-many.svg) | 100001 | 43.857<br>1.00x | 105.601<br>2.41x | 138.453<br>3.16x | 92.607<br>2.11x | **16.453<br>0.38x** | 16.782<br>0.38x |
| [pangui/wide_wrapping](plots/pangui/wide-wrapping.svg) | 10001 | 4.061<br>1.00x | 7.905<br>1.95x | 9.294<br>2.29x | 9.712<br>2.39x | 1.360<br>0.34x | **1.265<br>0.31x** |
| [text/paragraphs/100](plots/text/paragraphs-100.svg) | 101 | **0.083<br>1.00x** | 0.188<br>2.27x | 16.652<br>200.62x | 15.453<br>186.17x | 9.746<br>117.43x | 1.579<br>19.02x |
| [text/flex_cards/100](plots/text/flex-cards-100.svg) | 301 | **0.188<br>1.00x** | 0.410<br>2.18x | 6.872<br>36.55x | 5.013<br>26.67x | 3.454<br>18.37x | 0.775<br>4.12x |
| [text/inline_mixed/100](plots/text/inline-mixed-100.svg) | 1599 | **1.111<br>1.00x** | 2.264<br>2.04x | 24.434<br>21.99x | 13.954<br>12.56x | 14.371<br>12.94x | 3.102<br>2.79x |
| [text/paragraphs/1000](plots/text/paragraphs-1000.svg) | 1001 | **0.592<br>1.00x** | 1.319<br>2.23x | 169.577<br>286.45x | 148.328<br>250.55x | 98.933<br>167.12x | 13.631<br>23.03x |
| [text/flex_cards/1000](plots/text/flex-cards-1000.svg) | 3001 | **1.626<br>1.00x** | 3.441<br>2.12x | 62.489<br>38.43x | 47.442<br>29.18x | 34.054<br>20.94x | 6.584<br>4.05x |
| [text/inline_mixed/1000](plots/text/inline-mixed-1000.svg) | 16361 | **11.065<br>1.00x** | 24.657<br>2.23x | 247.511<br>22.37x | 121.329<br>10.97x | 136.129<br>12.30x | 25.403<br>2.30x |
| [real/wikipedia](plots/real/wikipedia.svg) | 21889 | 22.980<br>1.00x | 64.330<br>2.80x | 214.608<br>9.34x | 81.515<br>3.55x | 69.428<br>3.02x | **18.983<br>0.83x** |
| [real/mdn](plots/real/mdn.svg) | 2212 | **1.628<br>1.00x** | 4.856<br>2.98x | 15.521<br>9.53x | 7.662<br>4.71x | 6.091<br>3.74x | 2.797<br>1.72x |
| [real/rustdoc](plots/real/rustdoc.svg) | 15947 | 14.179<br>1.00x | 36.995<br>2.61x | 125.881<br>8.88x | 52.736<br>3.72x | 57.117<br>4.03x | **13.088<br>0.92x** |
| [real/css-flexbox-1](plots/real/css-flexbox-1.svg) | 15890 | **11.698<br>1.00x** | 44.090<br>3.77x | 129.034<br>11.03x | 63.129<br>5.40x | 64.390<br>5.50x | 20.062<br>1.72x |
| [real/servo-org](plots/real/servo-org.svg) | 226 | **0.248<br>1.00x** | 0.794<br>3.20x | 4.202<br>16.95x | 3.221<br>12.99x | 0.931<br>3.75x | 0.667<br>2.69x |
| [real/dioxuslabs-com](plots/real/dioxuslabs-com.svg) | 158 | **0.185<br>1.00x** | 0.260<br>1.40x | 3.554<br>19.21x | 4.318<br>23.34x | 0.343<br>1.85x | 0.291<br>1.57x |
| [real/bootstrap-dashboard](plots/real/bootstrap-dashboard.svg) | 199 | 0.212<br>1.00x | **0.037<br>0.17x** | 2.244<br>10.59x | 1.978<br>9.33x | 0.517<br>2.44x | 0.370<br>1.75x |

### Box construction + layout

| case | nodes | Chrome<br>rebuildLayoutTree + Layout | WebKit<br>Layout (incl. shaping) | Firefox<br>Reflow | Ladybird<br>tree build + layout | Servo(1)<br>Box + Fragment | Servo(3)<br>Box + Fragment | Blitz<br>construct + layout | Blitz<br>construct + layout (parallel construct) | Blitz<br>construct + layout (parallel construct + layout) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [flex/huge_nested/1000](plots/flex/huge-nested-1000.svg) | 911 | 1.400<br>1.00x | 2.290<br>1.64x | 1.556<br>1.11x | 5.640<br>4.03x | 2.227<br>1.59x | 1.479<br>1.06x | 0.776<br>0.55x | 0.747<br>0.53x | **0.529<br>0.38x** |
| [flex/wide/1000](plots/flex/wide-1000.svg) | 1000 | 1.773<br>1.00x | 3.114<br>1.76x | 2.488<br>1.40x | 7.764<br>4.38x | 2.845<br>1.60x | 2.554<br>1.44x | 1.175<br>0.66x | 1.219<br>0.69x | **1.048<br>0.59x** |
| [flex/absolute/1000](plots/flex/absolute-1000.svg) | 1003 | 2.096<br>1.00x | 2.771<br>1.32x | 2.956<br>1.41x | 5.337<br>2.55x | 2.865<br>1.37x | 2.352<br>1.12x | 0.920<br>0.44x | 0.936<br>0.45x | **0.824<br>0.39x** |
| [flex/deep_auto/1000](plots/flex/deep-auto-1000.svg) | 767 | 2.281<br>1.00x | 2.284<br>1.00x | 1.356<br>0.59x | 8.181<br>3.59x | 4.247<br>1.86x | 2.832<br>1.24x | 1.963<br>0.86x | 1.966<br>0.86x | **0.909<br>0.40x** |
| [flex/deep_random/1000](plots/flex/deep-random-1000.svg) | 767 | 1.362<br>1.00x | 3.006<br>2.21x | 1.891<br>1.39x | 6.688<br>4.91x | 2.484<br>1.82x | 2.521<br>1.85x | 0.887<br>0.65x | 0.857<br>0.63x | **0.703<br>0.52x** |
| [flex/huge_nested/10000](plots/flex/huge-nested-10000.svg) | 9111 | 13.494<br>1.00x | 20.506<br>1.52x | 15.092<br>1.12x | 54.629<br>4.05x | 22.227<br>1.65x | 11.756<br>0.87x | 7.911<br>0.59x | 7.527<br>0.56x | **3.350<br>0.25x** |
| [flex/wide/10000](plots/flex/wide-10000.svg) | 10001 | 17.919<br>1.00x | 29.423<br>1.64x | 24.008<br>1.34x | 82.060<br>4.58x | 28.716<br>1.60x | 24.917<br>1.39x | 13.398<br>0.75x | 12.486<br>0.70x | **9.051<br>0.51x** |
| [flex/absolute/10000](plots/flex/absolute-10000.svg) | 10004 | 22.452<br>1.00x | 28.053<br>1.25x | 28.096<br>1.25x | 65.704<br>2.93x | 28.985<br>1.29x | 24.110<br>1.07x | 9.903<br>0.44x | 9.817<br>0.44x | **7.999<br>0.36x** |
| [flex/deep_auto/10000](plots/flex/deep-auto-10000.svg) | 8191 | 22.864<br>1.00x | 19.750<br>0.86x | 14.383<br>0.63x | 83.164<br>3.64x | 29.433<br>1.29x | 29.076<br>1.27x | 21.126<br>0.92x | 20.669<br>0.90x | **6.121<br>0.27x** |
| [flex/deep_random/10000](plots/flex/deep-random-10000.svg) | 8191 | 12.994<br>1.00x | 25.640<br>1.97x | 18.646<br>1.43x | 70.864<br>5.45x | 23.737<br>1.83x | 25.038<br>1.93x | 9.828<br>0.76x | 9.643<br>0.74x | **4.439<br>0.34x** |
| [flex/superdeep/50](plots/flex/superdeep-50.svg) | 151 | 0.620<br>1.00x | 0.600<br>0.97x | 0.574<br>0.93x | 2.109<br>3.40x | 0.668<br>1.08x | 0.700<br>1.13x | 0.356<br>0.57x | **0.352<br>0.57x** | 0.709<br>1.14x |
| [flex/superdeep/100](plots/flex/superdeep-100.svg) | 301 | 1.159<br>1.00x | 1.016<br>0.88x | 1.062<br>0.92x | 4.107<br>3.54x | 1.314<br>1.13x | 1.418<br>1.22x | **0.690<br>0.60x** | 0.703<br>0.61x | 1.395<br>1.20x |
| [grid/wide/31x31](plots/grid/wide-31x31.svg) | 962 | 3.447<br>1.00x | 4.281<br>1.24x | 3.522<br>1.02x | 7.022<br>2.04x | 3.791<br>1.10x | 4.006<br>1.16x | **1.633<br>0.47x** | 1.667<br>0.48x | 2.096<br>0.61x |
| [grid/wide/100x100](plots/grid/wide-100x100.svg) | 10001 | 43.562<br>1.00x | 44.783<br>1.03x | 37.842<br>0.87x | 81.500<br>1.87x | 41.816<br>0.96x | 42.467<br>0.97x | 19.425<br>0.45x | **18.784<br>0.43x** | 22.176<br>0.51x |
| [grid/deep/2x2x5](plots/grid/deep-2x2x5.svg) | 1365 | 8.085<br>1.00x | 20.099<br>2.49x | 12.652<br>1.56x | 16.605<br>2.05x | 9.774<br>1.21x | 9.329<br>1.15x | 4.019<br>0.50x | 4.047<br>0.50x | **1.908<br>0.24x** |
| [grid/deep/3x3x4](plots/grid/deep-3x3x4.svg) | 7381 | 36.122<br>1.00x | 92.966<br>2.57x | 52.625<br>1.46x | 85.783<br>2.37x | 49.418<br>1.37x | 46.151<br>1.28x | 18.450<br>0.51x | 19.476<br>0.54x | **7.498<br>0.21x** |
| [grid/superdeep/100](plots/grid/superdeep-100.svg) | 101 | 1.755<br>1.00x | 386.877<br>220.44x | 12.590<br>7.17x | 3.110<br>1.77x | 1.900<br>1.08x | 1.907<br>1.09x | **0.524<br>0.30x** | 0.552<br>0.31x | 0.622<br>0.35x |
| [pangui/expand_with_max_constraint](plots/pangui/expand-with-max-constraint.svg) | 3001 | 5.012<br>1.00x | 7.307<br>1.46x | 4.904<br>0.98x | 14.246<br>2.84x | 9.101<br>1.82x | 7.847<br>1.57x | 3.991<br>0.80x | 3.914<br>0.78x | **2.692<br>0.54x** |
| [pangui/expand_with_min_constraint](plots/pangui/expand-with-min-constraint.svg) | 3001 | 5.044<br>1.00x | 7.390<br>1.47x | 4.820<br>0.96x | 13.277<br>2.63x | 9.038<br>1.79x | 7.732<br>1.53x | 3.983<br>0.79x | 3.813<br>0.76x | **2.978<br>0.59x** |
| [pangui/fit_nesting](plots/pangui/fit-nesting.svg) | 101111 | 185.678<br>1.00x | 217.188<br>1.17x | 154.417<br>0.83x | 523.666<br>2.82x | 457.429<br>2.46x | 183.940<br>0.99x | 101.405<br>0.55x | 100.449<br>0.54x | **38.335<br>0.21x** |
| [pangui/flex_expand_equal_weights](plots/pangui/flex-expand-equal-weights.svg) | 15001 | 19.447<br>1.00x | 49.356<br>2.54x | 25.353<br>1.30x | 62.113<br>3.19x | 31.230<br>1.61x | 32.704<br>1.68x | 10.624<br>0.55x | **10.386<br>0.53x** | 11.534<br>0.59x |
| [pangui/flex_expand_weights](plots/pangui/flex-expand-weights.svg) | 15001 | 18.553<br>1.00x | 50.877<br>2.74x | 37.701<br>2.03x | 53.339<br>2.87x | 40.240<br>2.17x | 32.700<br>1.76x | 14.495<br>0.78x | 12.828<br>0.69x | **8.386<br>0.45x** |
| [pangui/nested_vertical_stack](plots/pangui/nested-vertical-stack.svg) | 10001 | 12.242<br>1.00x | 30.168<br>2.46x | 24.065<br>1.97x | 45.806<br>3.74x | 24.301<br>1.99x | 26.383<br>2.16x | **8.904<br>0.73x** | 8.930<br>0.73x | 10.124<br>0.83x |
| [pangui/padding_and_margin](plots/pangui/padding-and-margin.svg) | 101 | 0.223<br>1.00x | 0.443<br>1.99x | 0.305<br>1.37x | 0.792<br>3.55x | 0.336<br>1.50x | 0.423<br>1.89x | **0.078<br>0.35x** | 0.085<br>0.38x | 0.105<br>0.47x |
| [pangui/percentage_and_ratio](plots/pangui/percentage-and-ratio.svg) | 10001 | 19.930<br>1.00x | 27.860<br>1.40x | 19.429<br>0.97x | 40.901<br>2.05x | 22.924<br>1.15x | 23.738<br>1.19x | **7.510<br>0.38x** | 7.849<br>0.39x | 8.311<br>0.42x |
| [pangui/perpendicular_expand_with_wrap](plots/pangui/perpendicular-expand-with-wrap.svg) | 12001 | 21.664<br>1.00x | 38.692<br>1.79x | 25.686<br>1.19x | 55.902<br>2.58x | 26.415<br>1.22x | 25.314<br>1.17x | 14.297<br>0.66x | **13.881<br>0.64x** | 15.109<br>0.70x |
| [pangui/pixels_with_min_expand_constraint](plots/pangui/pixels-with-min-expand-constraint.svg) | 30001 | 54.839<br>1.00x | 84.684<br>1.54x | 50.559<br>0.92x | 145.595<br>2.65x | 96.894<br>1.77x | 80.967<br>1.48x | 41.905<br>0.76x | 43.318<br>0.79x | **25.270<br>0.46x** |
| [pangui/wide_no_wrap_simple_few](plots/pangui/wide-no-wrap-simple-few.svg) | 1001 | 1.280<br>1.00x | 2.123<br>1.66x | 1.416<br>1.11x | 3.654<br>2.85x | 1.992<br>1.56x | 2.075<br>1.62x | **0.630<br>0.49x** | 0.657<br>0.51x | 0.975<br>0.76x |
| [pangui/wide_no_wrap_simple_many](plots/pangui/wide-no-wrap-simple-many.svg) | 100001 | 139.753<br>1.00x | 244.833<br>1.75x | 227.570<br>1.63x | 467.842<br>3.35x | 286.249<br>2.05x | 232.445<br>1.66x | **107.541<br>0.77x** | 117.004<br>0.84x | 110.177<br>0.79x |
| [pangui/wide_wrapping](plots/pangui/wide-wrapping.svg) | 10001 | 14.227<br>1.00x | 21.990<br>1.55x | 14.695<br>1.03x | 43.380<br>3.05x | 21.189<br>1.49x | 21.611<br>1.52x | 9.530<br>0.67x | **8.889<br>0.62x** | 11.932<br>0.84x |
| [text/paragraphs/100](plots/text/paragraphs-100.svg) | 101 | 6.057<br>1.00x | 6.817<br>1.13x | 5.729<br>0.95x | 10.102<br>1.67x | 19.255<br>3.18x | 17.165<br>2.83x | 10.516<br>1.74x | 2.515<br>0.42x | **2.284<br>0.38x** |
| [text/flex_cards/100](plots/text/flex-cards-100.svg) | 301 | 4.236<br>1.00x | 6.979<br>1.65x | 4.792<br>1.13x | 7.938<br>1.87x | 8.919<br>2.11x | 7.606<br>1.80x | 4.519<br>1.07x | 2.052<br>0.48x | **1.329<br>0.31x** |
| [text/inline_mixed/100](plots/text/inline-mixed-100.svg) | 1599 | 12.103<br>1.00x | 21.083<br>1.74x | 14.466<br>1.20x | 23.573<br>1.95x | 32.280<br>2.67x | 16.912<br>1.40x | 15.305<br>1.26x | 4.139<br>0.34x | **3.707<br>0.31x** |
| [text/paragraphs/1000](plots/text/paragraphs-1000.svg) | 1001 | 57.328<br>1.00x | 41.322<br>0.72x | 44.974<br>0.78x | 104.229<br>1.82x | 197.976<br>3.45x | 163.367<br>2.85x | 107.130<br>1.87x | **21.522<br>0.38x** | 21.792<br>0.38x |
| [text/flex_cards/1000](plots/text/flex-cards-1000.svg) | 3001 | 39.132<br>1.00x | 41.041<br>1.05x | 30.684<br>0.78x | 73.243<br>1.87x | 78.717<br>2.01x | 63.975<br>1.63x | 45.170<br>1.15x | 18.610<br>0.48x | **11.251<br>0.29x** |
| [text/inline_mixed/1000](plots/text/inline-mixed-1000.svg) | 16361 | 102.550<br>1.00x | 111.720<br>1.09x | 102.016<br>0.99x | 236.795<br>2.31x | 299.743<br>2.92x | 142.989<br>1.39x | 145.860<br>1.42x | 34.810<br>0.34x | **34.044<br>0.33x** |
| [real/wikipedia](plots/real/wikipedia.svg) | 21889 | 196.933<br>1.00x | 313.557<br>1.59x | 184.409<br>0.94x | 542.729<br>2.76x | 270.037<br>1.37x | 130.158<br>0.66x | 87.565<br>0.44x | 36.561<br>0.19x | **35.267<br>0.18x** |
| [real/mdn](plots/real/mdn.svg) | 2212 | 14.655<br>1.00x | 21.837<br>1.49x | 13.318<br>0.91x | 55.971<br>3.82x | 23.598<br>1.61x | 11.016<br>0.75x | 9.522<br>0.65x | 7.034<br>0.48x | **4.793<br>0.33x** |
| [real/rustdoc](plots/real/rustdoc.svg) | 15947 | 114.562<br>1.00x | 168.652<br>1.47x | 95.596<br>0.83x | 447.911<br>3.91x | 178.503<br>1.56x | 101.126<br>0.88x | 83.970<br>0.73x | 39.624<br>0.35x | **37.970<br>0.33x** |
| [real/css-flexbox-1](plots/real/css-flexbox-1.svg) | 15890 | 109.022<br>1.00x | 216.685<br>1.99x | 106.832<br>0.98x | 280.888<br>2.58x | 177.494<br>1.63x | 107.371<br>0.98x | 90.130<br>0.83x | **44.296<br>0.41x** | 48.523<br>0.45x |
| [real/servo-org](plots/real/servo-org.svg) | 226 | 2.656<br>1.00x | 4.629<br>1.74x | 4.599<br>1.73x | 5.828<br>2.19x | 6.977<br>2.63x | 5.373<br>2.02x | 1.354<br>0.51x | 1.212<br>0.46x | **0.802<br>0.30x** |
| [real/dioxuslabs-com](plots/real/dioxuslabs-com.svg) | 158 | 3.426<br>1.00x | 3.227<br>0.94x | 3.549<br>1.04x | 17.676<br>5.16x | 6.780<br>1.98x | 5.536<br>1.62x | 0.802<br>0.23x | 0.801<br>0.23x | **0.617<br>0.18x** |
| [real/bootstrap-dashboard](plots/real/bootstrap-dashboard.svg) | 199 | 2.094<br>1.00x | 2.883<br>1.38x | 2.534<br>1.21x | 3.221<br>1.54x | 4.518<br>2.16x | 3.312<br>1.58x | 1.160<br>0.55x | 1.197<br>0.57x | **0.857<br>0.41x** |

### Style

| case | nodes | Chrome<br>recalcStyle | WebKit<br>RecalculateStyles (incl. render-tree construction) | Firefox<br>Styles (incl. frame construction) | Ladybird<br>update_style | Servo(1)<br>Styling | Servo(3)<br>Styling | Blitz<br>style | Blitz<br>style (parallel) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [flex/huge_nested/1000](plots/flex/huge-nested-1000.svg) | 911 | 1.682<br>1.00x | 3.645<br>2.17x | 1.613<br>0.96x | 31.368<br>18.65x | 6.690<br>3.98x | 3.052<br>1.81x | 2.459<br>1.46x | **0.944<br>0.56x** |
| [flex/wide/1000](plots/flex/wide-1000.svg) | 1000 | 1.546<br>1.00x | 3.636<br>2.35x | 2.094<br>1.35x | 36.111<br>23.36x | 9.672<br>6.26x | 3.015<br>1.95x | 2.196<br>1.42x | **1.180<br>0.76x** |
| [flex/absolute/1000](plots/flex/absolute-1000.svg) | 1003 | 1.784<br>1.00x | 4.694<br>2.63x | 2.519<br>1.41x | 42.492<br>23.82x | 6.483<br>3.63x | 3.143<br>1.76x | 2.119<br>1.19x | **1.211<br>0.68x** |
| [flex/deep_auto/1000](plots/flex/deep-auto-1000.svg) | 767 | 0.916<br>1.00x | 2.499<br>2.73x | 0.861<br>0.94x | 18.001<br>19.65x | 5.433<br>5.93x | 1.359<br>1.48x | 1.062<br>1.16x | **0.558<br>0.61x** |
| [flex/deep_random/1000](plots/flex/deep-random-1000.svg) | 767 | 1.060<br>1.00x | 2.728<br>2.57x | 1.726<br>1.63x | 25.432<br>23.99x | 5.792<br>5.46x | 2.316<br>2.19x | 1.301<br>1.23x | **0.918<br>0.87x** |
| [flex/huge_nested/10000](plots/flex/huge-nested-10000.svg) | 9111 | 15.810<br>1.00x | 33.299<br>2.11x | 15.119<br>0.96x | 287.573<br>18.19x | 58.717<br>3.71x | 25.863<br>1.64x | 25.173<br>1.59x | **9.368<br>0.59x** |
| [flex/wide/10000](plots/flex/wide-10000.svg) | 10001 | 14.279<br>1.00x | 35.422<br>2.48x | 17.356<br>1.22x | 350.997<br>24.58x | 53.507<br>3.75x | 26.712<br>1.87x | 21.521<br>1.51x | **11.417<br>0.80x** |
| [flex/absolute/10000](plots/flex/absolute-10000.svg) | 10004 | 17.300<br>1.00x | 45.998<br>2.66x | 22.210<br>1.28x | 405.686<br>23.45x | 55.639<br>3.22x | 27.758<br>1.60x | 22.028<br>1.27x | **10.575<br>0.61x** |
| [flex/deep_auto/10000](plots/flex/deep-auto-10000.svg) | 8191 | 11.320<br>1.00x | 25.858<br>2.28x | 9.171<br>0.81x | 195.067<br>17.23x | 34.919<br>3.08x | 15.666<br>1.38x | 15.318<br>1.35x | **5.925<br>0.52x** |
| [flex/deep_random/10000](plots/flex/deep-random-10000.svg) | 8191 | 10.704<br>1.00x | 26.956<br>2.52x | 13.649<br>1.28x | 260.825<br>24.37x | 39.534<br>3.69x | 21.202<br>1.98x | 15.839<br>1.48x | **9.248<br>0.86x** |
| [flex/superdeep/50](plots/flex/superdeep-50.svg) | 151 | 0.327<br>1.00x | 0.744<br>2.27x | 0.463<br>1.42x | 7.691<br>23.52x | 0.914<br>2.79x | 0.950<br>2.91x | 0.297<br>0.91x | **0.294<br>0.90x** |
| [flex/superdeep/100](plots/flex/superdeep-100.svg) | 301 | **0.576<br>1.00x** | 1.242<br>2.16x | 0.949<br>1.65x | 11.570<br>20.09x | 1.717<br>2.98x | 1.774<br>3.08x | 0.578<br>1.00x | 0.576<br>1.00x |
| [grid/wide/31x31](plots/grid/wide-31x31.svg) | 962 | 1.374<br>1.00x | 3.800<br>2.77x | 2.014<br>1.47x | 36.215<br>26.36x | 8.545<br>6.22x | 3.374<br>2.46x | 2.435<br>1.77x | **1.213<br>0.88x** |
| [grid/wide/100x100](plots/grid/wide-100x100.svg) | 10001 | 14.010<br>1.00x | 34.996<br>2.50x | 19.117<br>1.36x | 383.633<br>27.38x | 65.811<br>4.70x | 30.579<br>2.18x | 26.917<br>1.92x | **11.100<br>0.79x** |
| [grid/deep/2x2x5](plots/grid/deep-2x2x5.svg) | 1365 | 2.353<br>1.00x | 6.969<br>2.96x | 2.642<br>1.12x | 64.763<br>27.52x | 9.112<br>3.87x | 4.123<br>1.75x | 2.721<br>1.16x | **1.568<br>0.67x** |
| [grid/deep/3x3x4](plots/grid/deep-3x3x4.svg) | 7381 | 12.163<br>1.00x | 31.538<br>2.59x | 13.027<br>1.07x | 437.710<br>35.99x | 40.216<br>3.31x | 21.165<br>1.74x | 15.950<br>1.31x | **7.859<br>0.65x** |
| [grid/superdeep/100](plots/grid/superdeep-100.svg) | 101 | 0.230<br>1.00x | 1.056<br>4.59x | 0.293<br>1.27x | 6.973<br>30.32x | 0.660<br>2.87x | 0.635<br>2.76x | **0.181<br>0.79x** | 0.200<br>0.87x |
| [pangui/expand_with_max_constraint](plots/pangui/expand-with-max-constraint.svg) | 3001 | 4.818<br>1.00x | 10.205<br>2.12x | 4.451<br>0.92x | 86.042<br>17.86x | 15.366<br>3.19x | 6.907<br>1.43x | 6.344<br>1.32x | **2.685<br>0.56x** |
| [pangui/expand_with_min_constraint](plots/pangui/expand-with-min-constraint.svg) | 3001 | 4.746<br>1.00x | 10.229<br>2.16x | 5.036<br>1.06x | 82.639<br>17.41x | 15.399<br>3.24x | 7.042<br>1.48x | 6.317<br>1.33x | **2.508<br>0.53x** |
| [pangui/fit_nesting](plots/pangui/fit-nesting.svg) | 101111 | 266.734<br>1.00x | 430.055<br>1.61x | 242.727<br>0.91x | 3766.368<br>14.12x | 783.835<br>2.94x | 337.032<br>1.26x | 382.073<br>1.43x | **116.976<br>0.44x** |
| [pangui/flex_expand_equal_weights](plots/pangui/flex-expand-equal-weights.svg) | 15001 | 32.903<br>1.00x | 60.746<br>1.85x | 34.151<br>1.04x | 674.354<br>20.50x | 109.993<br>3.34x | 49.193<br>1.50x | 49.164<br>1.49x | **18.314<br>0.56x** |
| [pangui/flex_expand_weights](plots/pangui/flex-expand-weights.svg) | 15001 | 24.047<br>1.00x | 53.358<br>2.22x | 24.261<br>1.01x | 476.740<br>19.83x | 77.554<br>3.23x | 33.808<br>1.41x | 35.100<br>1.46x | **11.910<br>0.50x** |
| [pangui/nested_vertical_stack](plots/pangui/nested-vertical-stack.svg) | 10001 | 21.351<br>1.00x | 39.088<br>1.83x | 19.594<br>0.92x | 409.850<br>19.20x | 69.173<br>3.24x | 32.904<br>1.54x | 29.370<br>1.38x | **11.927<br>0.56x** |
| [pangui/padding_and_margin](plots/pangui/padding-and-margin.svg) | 101 | 0.304<br>1.00x | 0.654<br>2.15x | 0.364<br>1.20x | 7.357<br>24.20x | 0.907<br>2.98x | 0.618<br>2.03x | 0.323<br>1.06x | **0.216<br>0.71x** |
| [pangui/percentage_and_ratio](plots/pangui/percentage-and-ratio.svg) | 10001 | 23.631<br>1.00x | 39.364<br>1.67x | 24.612<br>1.04x | 413.494<br>17.50x | 72.058<br>3.05x | 33.580<br>1.42x | 30.145<br>1.28x | **13.032<br>0.55x** |
| [pangui/perpendicular_expand_with_wrap](plots/pangui/perpendicular-expand-with-wrap.svg) | 12001 | 28.131<br>1.00x | 53.401<br>1.90x | 25.586<br>0.91x | 523.892<br>18.62x | 79.536<br>2.83x | 38.224<br>1.36x | 32.139<br>1.14x | **13.813<br>0.49x** |
| [pangui/pixels_with_min_expand_constraint](plots/pangui/pixels-with-min-expand-constraint.svg) | 30001 | 51.090<br>1.00x | 113.992<br>2.23x | 50.189<br>0.98x | 1078.389<br>21.11x | 155.095<br>3.04x | 66.521<br>1.30x | 69.988<br>1.37x | **23.612<br>0.46x** |
| [pangui/wide_no_wrap_simple_few](plots/pangui/wide-no-wrap-simple-few.svg) | 1001 | 2.187<br>1.00x | 3.967<br>1.81x | 2.198<br>1.01x | 37.922<br>17.34x | 9.090<br>4.16x | 3.642<br>1.67x | 3.301<br>1.51x | **1.365<br>0.62x** |
| [pangui/wide_no_wrap_simple_many](plots/pangui/wide-no-wrap-simple-many.svg) | 100001 | 267.424<br>1.00x | 432.759<br>1.62x | 258.901<br>0.97x | 14160.638<br>52.95x | 738.166<br>2.76x | 327.916<br>1.23x | 349.194<br>1.31x | **117.201<br>0.44x** |
| [pangui/wide_wrapping](plots/pangui/wide-wrapping.svg) | 10001 | 21.316<br>1.00x | 39.955<br>1.87x | 19.685<br>0.92x | 417.139<br>19.57x | 72.667<br>3.41x | 34.067<br>1.60x | 31.955<br>1.50x | **12.651<br>0.59x** |
| [text/paragraphs/100](plots/text/paragraphs-100.svg) | 101 | **0.226<br>1.00x** | 0.730<br>3.23x | 0.366<br>1.62x | 3.084<br>13.64x | 0.549<br>2.43x | 0.467<br>2.07x | 0.317<br>1.40x | 0.234<br>1.04x |
| [text/flex_cards/100](plots/text/flex-cards-100.svg) | 301 | **0.356<br>1.00x** | 1.328<br>3.73x | 0.649<br>1.82x | 5.238<br>14.71x | 1.014<br>2.85x | 0.838<br>2.35x | 0.559<br>1.57x | 0.386<br>1.09x |
| [text/inline_mixed/100](plots/text/inline-mixed-100.svg) | 1599 | 0.883<br>1.00x | 5.737<br>6.50x | 1.700<br>1.93x | 13.055<br>14.79x | 2.331<br>2.64x | 1.521<br>1.72x | 1.167<br>1.32x | **0.829<br>0.94x** |
| [text/paragraphs/1000](plots/text/paragraphs-1000.svg) | 1001 | 1.887<br>1.00x | 6.245<br>3.31x | 2.460<br>1.30x | 23.957<br>12.70x | 5.277<br>2.80x | 3.313<br>1.76x | 2.822<br>1.50x | **1.411<br>0.75x** |
| [text/flex_cards/1000](plots/text/flex-cards-1000.svg) | 3001 | 3.173<br>1.00x | 10.868<br>3.43x | 5.324<br>1.68x | 35.847<br>11.30x | 11.486<br>3.62x | 6.991<br>2.20x | 5.419<br>1.71x | **2.687<br>0.85x** |
| [text/inline_mixed/1000](plots/text/inline-mixed-1000.svg) | 16361 | 8.473<br>1.00x | 49.037<br>5.79x | 15.581<br>1.84x | 118.669<br>14.01x | 25.251<br>2.98x | 14.056<br>1.66x | 10.936<br>1.29x | **6.538<br>0.77x** |
| [real/wikipedia](plots/real/wikipedia.svg) | 21889 | 53.049<br>1.00x | 206.526<br>3.89x | 41.720<br>0.79x | 437.067<br>8.24x | 68.712<br>1.30x | 31.945<br>0.60x | 38.234<br>0.72x | **11.912<br>0.22x** |
| [real/mdn](plots/real/mdn.svg) | 2212 | 7.190<br>1.00x | 19.089<br>2.65x | 4.585<br>0.64x | 79.683<br>11.08x | 7.799<br>1.08x | 5.223<br>0.73x | 2.627<br>0.37x | **1.900<br>0.26x** |
| [real/rustdoc](plots/real/rustdoc.svg) | 15947 | 22.966<br>1.00x | 70.926<br>3.09x | 32.204<br>1.40x | 352.882<br>15.37x | 60.563<br>2.64x | 29.676<br>1.29x | 19.310<br>0.84x | **7.459<br>0.32x** |
| [real/css-flexbox-1](plots/real/css-flexbox-1.svg) | 15890 | 19.932<br>1.00x | 73.061<br>3.67x | 23.134<br>1.16x | 203.073<br>10.19x | 22.979<br>1.15x | 11.880<br>0.60x | 15.004<br>0.75x | **6.487<br>0.33x** |
| [real/servo-org](plots/real/servo-org.svg) | 226 | 0.853<br>1.00x | 3.460<br>4.06x | 1.314<br>1.54x | 17.085<br>20.03x | 1.368<br>1.60x | 1.296<br>1.52x | 0.847<br>0.99x | **0.844<br>0.99x** |
| [real/dioxuslabs-com](plots/real/dioxuslabs-com.svg) | 158 | 1.158<br>1.00x | 7.353<br>6.35x | 1.478<br>1.28x | 21.169<br>18.28x | 1.525<br>1.32x | 1.660<br>1.43x | 1.104<br>0.95x | **1.090<br>0.94x** |
| [real/bootstrap-dashboard](plots/real/bootstrap-dashboard.svg) | 199 | **0.949<br>1.00x** | 3.120<br>3.29x | 1.281<br>1.35x | 12.554<br>13.23x | 1.259<br>1.33x | 1.094<br>1.15x | 1.390<br>1.46x | 1.428<br>1.50x |

### Whole pipeline (style to laid-out tree)

| case | nodes | Chrome<br>UpdateLayoutTree + Layout | WebKit<br>RecalculateStyles + Layout | Firefox<br>Styles + Reflow | Ladybird<br>update_layout() | Servo(1)<br>restyle_and_build_trees | Servo(3)<br>restyle_and_build_trees | Blitz<br>resolve() | Blitz<br>resolve() (parallel style) | Blitz<br>resolve() (parallel style + construct) | Blitz<br>resolve() (parallel style + construct + layout) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [flex/huge_nested/1000](plots/flex/huge-nested-1000.svg) | 911 | 3.217<br>1.00x | 6.004<br>1.87x | 3.174<br>0.99x | 37.541<br>11.67x | 14.417<br>4.48x | 6.259<br>1.95x | 3.377<br>1.05x | 2.011<br>0.63x | 2.095<br>0.65x | **1.747<br>0.54x** |
| [flex/wide/1000](plots/flex/wide-1000.svg) | 1000 | 3.383<br>1.00x | 6.750<br>2.00x | 4.693<br>1.39x | 44.664<br>13.20x | 13.988<br>4.13x | 7.149<br>2.11x | 3.670<br>1.08x | 2.791<br>0.82x | 2.821<br>0.83x | **2.640<br>0.78x** |
| [flex/absolute/1000](plots/flex/absolute-1000.svg) | 1003 | 3.960<br>1.00x | 7.510<br>1.90x | 5.649<br>1.43x | 48.355<br>12.21x | 14.326<br>3.62x | 7.006<br>1.77x | 3.272<br>0.83x | 2.632<br>0.66x | 2.347<br>0.59x | **2.278<br>0.58x** |
| [flex/deep_auto/1000](plots/flex/deep-auto-1000.svg) | 767 | 3.310<br>1.00x | 4.783<br>1.45x | 2.273<br>0.69x | 26.650<br>8.05x | 11.551<br>3.49x | 5.820<br>1.76x | 3.126<br>0.94x | 2.825<br>0.85x | 2.722<br>0.82x | **1.637<br>0.49x** |
| [flex/deep_random/1000](plots/flex/deep-random-1000.svg) | 767 | 2.488<br>1.00x | 5.734<br>2.30x | 3.678<br>1.48x | 32.626<br>13.11x | 11.018<br>4.43x | 6.325<br>2.54x | 2.295<br>0.92x | 2.272<br>0.91x | 2.261<br>0.91x | **1.942<br>0.78x** |
| [flex/huge_nested/10000](plots/flex/huge-nested-10000.svg) | 9111 | 29.541<br>1.00x | 53.940<br>1.83x | 30.348<br>1.03x | 347.116<br>11.75x | 82.972<br>2.81x | 40.105<br>1.36x | 34.572<br>1.17x | 19.148<br>0.65x | 19.481<br>0.66x | **15.477<br>0.52x** |
| [flex/wide/10000](plots/flex/wide-10000.svg) | 10001 | 32.221<br>1.00x | 65.088<br>2.02x | 41.364<br>1.28x | 437.617<br>13.58x | 84.475<br>2.62x | 55.110<br>1.71x | 36.824<br>1.14x | 28.804<br>0.89x | 26.963<br>0.84x | **22.890<br>0.71x** |
| [flex/absolute/10000](plots/flex/absolute-10000.svg) | 10004 | 39.775<br>1.00x | 74.619<br>1.88x | 51.715<br>1.30x | 477.875<br>12.01x | 87.879<br>2.21x | 56.463<br>1.42x | 33.748<br>0.85x | 23.108<br>0.58x | 24.121<br>0.61x | **20.921<br>0.53x** |
| [flex/deep_auto/10000](plots/flex/deep-auto-10000.svg) | 8191 | 34.253<br>1.00x | 45.608<br>1.33x | 23.553<br>0.69x | 282.583<br>8.25x | 66.828<br>1.95x | 47.167<br>1.38x | 37.931<br>1.11x | 30.050<br>0.88x | 28.485<br>0.83x | **14.298<br>0.42x** |
| [flex/deep_random/10000](plots/flex/deep-random-10000.svg) | 8191 | 23.999<br>1.00x | 52.836<br>2.20x | 32.313<br>1.35x | 336.617<br>14.03x | 65.502<br>2.73x | 49.194<br>2.05x | 27.197<br>1.13x | 21.311<br>0.89x | 20.506<br>0.85x | **15.823<br>0.66x** |
| [flex/superdeep/50](plots/flex/superdeep-50.svg) | 151 | 1.039<br>1.00x | 1.368<br>1.32x | 1.080<br>1.04x | 10.034<br>9.66x | 3.022<br>2.91x | 3.030<br>2.92x | 0.682<br>0.66x | **0.679<br>0.65x** | 0.703<br>0.68x | 1.058<br>1.02x |
| [flex/superdeep/100](plots/flex/superdeep-100.svg) | 301 | 1.796<br>1.00x | 2.280<br>1.27x | 2.046<br>1.14x | 16.224<br>9.03x | 7.480<br>4.16x | 4.622<br>2.57x | **1.313<br>0.73x** | 1.344<br>0.75x | 1.361<br>0.76x | 2.061<br>1.15x |
| [grid/wide/31x31](plots/grid/wide-31x31.svg) | 962 | 4.985<br>1.00x | 8.082<br>1.62x | 5.708<br>1.14x | 43.699<br>8.77x | 15.856<br>3.18x | 8.976<br>1.80x | 4.335<br>0.87x | **3.217<br>0.65x** | 3.403<br>0.68x | 3.494<br>0.70x |
| [grid/wide/100x100](plots/grid/wide-100x100.svg) | 10001 | 57.645<br>1.00x | 80.005<br>1.39x | 58.270<br>1.01x | 469.402<br>8.14x | 109.919<br>1.91x | 75.673<br>1.31x | 48.268<br>0.84x | 33.983<br>0.59x | **32.782<br>0.57x** | 37.114<br>0.64x |
| [grid/deep/2x2x5](plots/grid/deep-2x2x5.svg) | 1365 | 10.515<br>1.00x | 27.069<br>2.57x | 15.345<br>1.46x | 82.077<br>7.81x | 20.772<br>1.98x | 15.242<br>1.45x | 6.961<br>0.66x | 5.918<br>0.56x | 6.245<br>0.59x | **3.964<br>0.38x** |
| [grid/deep/3x3x4](plots/grid/deep-3x3x4.svg) | 7381 | 48.359<br>1.00x | 124.843<br>2.58x | 65.825<br>1.36x | 529.320<br>10.95x | 91.692<br>1.90x | 69.953<br>1.45x | 35.824<br>0.74x | 28.592<br>0.59x | 30.568<br>0.63x | **18.553<br>0.38x** |
| [grid/superdeep/100](plots/grid/superdeep-100.svg) | 101 | 2.054<br>1.00x | 388.028<br>188.91x | 12.883<br>6.27x | 10.356<br>5.04x | 4.164<br>2.03x | 3.972<br>1.93x | **0.738<br>0.36x** | 0.804<br>0.39x | 0.801<br>0.39x | 0.852<br>0.41x |
| [pangui/expand_with_max_constraint](plots/pangui/expand-with-max-constraint.svg) | 3001 | 9.898<br>1.00x | 17.512<br>1.77x | 9.686<br>0.98x | 102.331<br>10.34x | 26.394<br>2.67x | 16.647<br>1.68x | 10.989<br>1.11x | 7.729<br>0.78x | 7.116<br>0.72x | **6.827<br>0.69x** |
| [pangui/expand_with_min_constraint](plots/pangui/expand-with-min-constraint.svg) | 3001 | 9.854<br>1.00x | 17.619<br>1.79x | 9.914<br>1.01x | 97.413<br>9.89x | 26.029<br>2.64x | 16.692<br>1.69x | 11.272<br>1.14x | 7.506<br>0.76x | 7.696<br>0.78x | **6.238<br>0.63x** |
| [pangui/fit_nesting](plots/pangui/fit-nesting.svg) | 101111 | 453.503<br>1.00x | 648.097<br>1.43x | 397.144<br>0.88x | 4363.326<br>9.62x | 1254.798<br>2.77x | 537.874<br>1.19x | 525.292<br>1.16x | 258.607<br>0.57x | 241.991<br>0.53x | **186.914<br>0.41x** |
| [pangui/flex_expand_equal_weights](plots/pangui/flex-expand-equal-weights.svg) | 15001 | 52.374<br>1.00x | 111.291<br>2.12x | 60.534<br>1.16x | 746.650<br>14.26x | 144.031<br>2.75x | 85.399<br>1.63x | 62.889<br>1.20x | **32.966<br>0.63x** | 33.121<br>0.63x | 33.641<br>0.64x |
| [pangui/flex_expand_weights](plots/pangui/flex-expand-weights.svg) | 15001 | 42.625<br>1.00x | 104.235<br>2.45x | 61.962<br>1.45x | 537.983<br>12.62x | 122.559<br>2.88x | 70.256<br>1.65x | 52.574<br>1.23x | 29.843<br>0.70x | 31.745<br>0.74x | **24.491<br>0.57x** |
| [pangui/nested_vertical_stack](plots/pangui/nested-vertical-stack.svg) | 10001 | 33.616<br>1.00x | 69.519<br>2.07x | 44.618<br>1.33x | 460.246<br>13.69x | 95.713<br>2.85x | 62.096<br>1.85x | 40.454<br>1.20x | 23.583<br>0.70x | 24.157<br>0.72x | **23.489<br>0.70x** |
| [pangui/padding_and_margin](plots/pangui/padding-and-margin.svg) | 101 | 0.587<br>1.00x | 1.097<br>1.87x | 0.669<br>1.14x | 8.398<br>14.31x | 2.587<br>4.41x | 2.446<br>4.17x | 0.417<br>0.71x | 0.351<br>0.60x | **0.326<br>0.56x** | 0.338<br>0.58x |
| [pangui/percentage_and_ratio](plots/pangui/percentage-and-ratio.svg) | 10001 | 44.068<br>1.00x | 67.224<br>1.53x | 44.839<br>1.02x | 459.440<br>10.43x | 98.580<br>2.24x | 60.296<br>1.37x | 39.266<br>0.89x | 22.905<br>0.52x | 25.381<br>0.58x | **22.146<br>0.50x** |
| [pangui/perpendicular_expand_with_wrap](plots/pangui/perpendicular-expand-with-wrap.svg) | 12001 | 50.281<br>1.00x | 92.862<br>1.85x | 52.733<br>1.05x | 585.115<br>11.64x | 111.308<br>2.21x | 66.719<br>1.33x | 49.792<br>0.99x | **31.020<br>0.62x** | 31.449<br>0.63x | 31.157<br>0.62x |
| [pangui/pixels_with_min_expand_constraint](plots/pangui/pixels-with-min-expand-constraint.svg) | 30001 | 107.401<br>1.00x | 198.700<br>1.85x | 101.958<br>0.95x | 1236.434<br>11.51x | 260.208<br>2.42x | 155.778<br>1.45x | 119.083<br>1.11x | 78.441<br>0.73x | 80.822<br>0.75x | **59.259<br>0.55x** |
| [pangui/wide_no_wrap_simple_few](plots/pangui/wide-no-wrap-simple-few.svg) | 1001 | 3.535<br>1.00x | 6.090<br>1.72x | 3.614<br>1.02x | 42.083<br>11.90x | 13.219<br>3.74x | 7.375<br>2.09x | 4.054<br>1.15x | **2.270<br>0.64x** | 2.615<br>0.74x | 2.425<br>0.69x |
| [pangui/wide_no_wrap_simple_many](plots/pangui/wide-no-wrap-simple-many.svg) | 100001 | 407.386<br>1.00x | 679.195<br>1.67x | 486.471<br>1.19x | 14702.037<br>36.09x | 1043.497<br>2.56x | 572.122<br>1.40x | 489.897<br>1.20x | **249.650<br>0.61x** | 265.642<br>0.65x | 259.316<br>0.64x |
| [pangui/wide_wrapping](plots/pangui/wide-wrapping.svg) | 10001 | 35.566<br>1.00x | 61.945<br>1.74x | 34.380<br>0.97x | 464.868<br>13.07x | 96.473<br>2.71x | 59.659<br>1.68x | 43.530<br>1.22x | 25.561<br>0.72x | **24.151<br>0.68x** | 26.234<br>0.74x |
| [text/paragraphs/100](plots/text/paragraphs-100.svg) | 101 | 6.299<br>1.00x | 7.547<br>1.20x | 6.219<br>0.99x | 13.572<br>2.15x | 19.883<br>3.16x | 17.861<br>2.84x | 10.865<br>1.72x | 10.686<br>1.70x | 3.123<br>0.50x | **2.665<br>0.42x** |
| [text/flex_cards/100](plots/text/flex-cards-100.svg) | 301 | 4.607<br>1.00x | 8.329<br>1.81x | 5.440<br>1.18x | 13.654<br>2.96x | 10.107<br>2.19x | 8.555<br>1.86x | 5.145<br>1.12x | 5.094<br>1.11x | 2.706<br>0.59x | **1.806<br>0.39x** |
| [text/inline_mixed/100](plots/text/inline-mixed-100.svg) | 1599 | 13.112<br>1.00x | 26.868<br>2.05x | 16.166<br>1.23x | 37.836<br>2.89x | 35.002<br>2.67x | 19.300<br>1.47x | 16.669<br>1.27x | 15.998<br>1.22x | 5.615<br>0.43x | **4.790<br>0.37x** |
| [text/paragraphs/1000](plots/text/paragraphs-1000.svg) | 1001 | 59.234<br>1.00x | 47.611<br>0.80x | 47.434<br>0.80x | 129.262<br>2.18x | 204.232<br>3.45x | 167.338<br>2.83x | 110.161<br>1.86x | 105.968<br>1.79x | 27.335<br>0.46x | **23.435<br>0.40x** |
| [text/flex_cards/1000](plots/text/flex-cards-1000.svg) | 3001 | 42.325<br>1.00x | 52.001<br>1.23x | 36.170<br>0.85x | 111.133<br>2.63x | 92.624<br>2.19x | 71.367<br>1.69x | 51.256<br>1.21x | 47.540<br>1.12x | 24.544<br>0.58x | **14.828<br>0.35x** |
| [text/inline_mixed/1000](plots/text/inline-mixed-1000.svg) | 16361 | 111.339<br>1.00x | 160.757<br>1.44x | 120.458<br>1.08x | 369.098<br>3.32x | 328.068<br>2.95x | 159.301<br>1.43x | 158.963<br>1.43x | 160.623<br>1.44x | 50.971<br>0.46x | **43.741<br>0.39x** |
| [real/wikipedia](plots/real/wikipedia.svg) | 21889 | 253.016<br>1.00x | 521.688<br>2.06x | 226.129<br>0.89x | 1003.167<br>3.96x | 344.906<br>1.36x | 165.535<br>0.65x | 130.741<br>0.52x | 106.090<br>0.42x | 53.881<br>0.21x | **50.064<br>0.20x** |
| [real/mdn](plots/real/mdn.svg) | 2212 | 22.037<br>1.00x | 40.950<br>1.86x | 18.438<br>0.84x | 138.437<br>6.28x | 37.322<br>1.69x | 16.703<br>0.76x | 12.448<br>0.56x | 12.246<br>0.56x | 9.044<br>0.41x | **7.432<br>0.34x** |
| [real/rustdoc](plots/real/rustdoc.svg) | 15947 | 138.683<br>1.00x | 240.003<br>1.73x | 128.943<br>0.93x | 813.920<br>5.87x | 245.042<br>1.77x | 134.646<br>0.97x | 106.431<br>0.77x | 88.708<br>0.64x | 53.086<br>0.38x | **48.451<br>0.35x** |
| [real/css-flexbox-1](plots/real/css-flexbox-1.svg) | 15890 | 130.583<br>1.00x | 289.859<br>2.22x | 130.193<br>1.00x | 500.593<br>3.83x | 202.595<br>1.55x | 121.064<br>0.93x | 108.103<br>0.83x | 102.435<br>0.78x | **55.007<br>0.42x** | 58.562<br>0.45x |
| [real/servo-org](plots/real/servo-org.svg) | 226 | 3.542<br>1.00x | 8.089<br>2.28x | 5.980<br>1.69x | 23.115<br>6.53x | 8.462<br>2.39x | 7.035<br>1.99x | 2.292<br>0.65x | 2.367<br>0.67x | 1.937<br>0.55x | **1.765<br>0.50x** |
| [real/dioxuslabs-com](plots/real/dioxuslabs-com.svg) | 158 | 4.624<br>1.00x | 10.673<br>2.31x | 5.027<br>1.09x | 39.146<br>8.47x | 8.595<br>1.86x | 7.461<br>1.61x | 1.945<br>0.42x | 1.933<br>0.42x | 1.978<br>0.43x | **1.882<br>0.41x** |
| [real/bootstrap-dashboard](plots/real/bootstrap-dashboard.svg) | 199 | 3.069<br>1.00x | 6.263<br>2.04x | 3.827<br>1.25x | 16.760<br>5.46x | 5.878<br>1.92x | 4.648<br>1.51x | 2.599<br>0.85x | 2.735<br>0.89x | 2.513<br>0.82x | **2.407<br>0.78x** |

### Sample spread

Median ÷ min of the samples behind each cell above (1.00 = all samples equal), per engine on blitz `layout`, blitz-par `style`, blitz-par-pcon `resolve`, blitz-par-pcon-pl `layout`, blitz-pcon `construct`, blitz-pcon-pl1 `layout`, chrome `layout`, firefox `layout`, ladybird `layout`, servo `fragment`, servo1 `fragment`, taffy `layout`, webkit `layout`.

| case | blitz | blitz-par | blitz-par-pcon | blitz-par-pcon-pl | blitz-pcon | blitz-pcon-pl1 | chrome | firefox | ladybird | servo | servo1 | taffy | webkit |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| flex/huge_nested/1000 | 1.06 | 1.15 | 1.10 | 1.42 | 1.07 | 1.07 | 1.10 | 1.05 | 1.07 | 1.03 | 1.15 | 1.08 | 1.10 |
| flex/wide/1000 | 1.15 | 1.61 | 1.22 | 1.43 | 1.20 | 1.05 | 1.12 | 1.06 | 1.04 | 1.03 | 1.06 | 1.04 | 1.00 |
| flex/absolute/1000 | 1.13 | 1.33 | 1.25 | 1.33 | 1.07 | 1.39 | 1.06 | 1.06 | 1.10 | 1.09 | 1.10 | 1.08 | 1.02 |
| flex/deep_auto/1000 | 1.07 | 1.05 | 1.12 | 1.17 | 1.04 | 1.04 | 1.07 | 1.04 | 1.07 | 1.08 | 1.90 | 1.05 | 1.04 |
| flex/deep_random/1000 | 1.09 | 1.36 | 1.20 | 1.14 | 1.20 | 1.07 | 1.04 | 1.05 | 1.06 | 1.10 | 1.16 | 1.07 | 1.04 |
| flex/huge_nested/10000 | 1.04 | 1.22 | 1.21 | 1.29 | 1.14 | 1.08 | 1.13 | 1.04 | 1.04 | 1.07 | 1.02 | 1.05 | 1.01 |
| flex/wide/10000 | 1.12 | 1.15 | 1.13 | 1.12 | 1.21 | 1.24 | 1.10 | 1.10 | 1.11 | 1.05 | 1.07 | 1.05 | 1.02 |
| flex/absolute/10000 | 1.16 | 1.26 | 1.10 | 1.13 | 1.09 | 1.20 | 1.04 | 1.07 | 1.06 | 1.03 | 1.05 | 1.10 | 1.04 |
| flex/deep_auto/10000 | 1.07 | 1.23 | 1.09 | 1.10 | 1.13 | 1.09 | 1.04 | 1.04 | 1.04 | 1.09 | 1.03 | 1.10 | 1.02 |
| flex/deep_random/10000 | 1.15 | 1.10 | 1.20 | 1.21 | 1.15 | 1.08 | 1.10 | 1.05 | 1.03 | 1.04 | 1.07 | 1.02 | 1.02 |
| flex/superdeep/50 | 1.19 | 1.16 | 1.08 | 1.08 | 1.14 | 1.07 | 1.08 | 1.07 | 1.04 | 1.05 | 1.11 | 1.09 | 1.00 |
| flex/superdeep/100 | 1.12 | 1.10 | 1.07 | 1.14 | 1.15 | 1.10 | 1.08 | 1.05 | 1.08 | 1.11 | 1.15 | 1.08 | 1.07 |
| grid/wide/31x31 | 1.23 | 1.35 | 1.21 | 1.26 | 1.21 | 1.45 | 1.08 | 1.03 | 1.09 | 1.06 | 1.09 | 1.09 | 1.01 |
| grid/wide/100x100 | 1.09 | 1.32 | 1.12 | 1.19 | 1.29 | 1.09 | 1.05 | 1.08 | 1.05 | 1.04 | 1.04 | 1.05 | 1.02 |
| grid/deep/2x2x5 | 1.03 | 1.35 | 1.16 | 1.07 | 1.07 | 1.12 | 1.13 | 1.08 | 1.02 | 1.12 | 1.05 | 1.03 | 1.02 |
| grid/deep/3x3x4 | 1.04 | 1.24 | 1.09 | 1.17 | 1.16 | 1.13 | 1.07 | 1.06 | 1.08 | 1.07 | 1.06 | 1.05 | 1.09 |
| grid/superdeep/100 | 1.21 | 1.11 | 1.17 | 1.17 | 1.14 | 1.20 | 1.10 | 1.04 | 1.05 | 1.09 | 1.02 | 1.09 | 1.02 |
| pangui/expand_with_max_constraint | 1.06 | 1.60 | 1.36 | 1.18 | 1.13 | 1.17 | 1.14 | 1.06 | 1.04 | 1.05 | 1.04 | 1.04 | 1.13 |
| pangui/expand_with_min_constraint | 1.09 | 1.41 | 1.23 | 1.25 | 1.17 | 1.11 | 1.10 | 1.06 | 1.08 | 1.06 | 1.10 | 1.03 | 1.06 |
| pangui/fit_nesting | 1.07 | 1.13 | 1.17 | 1.17 | 1.09 | 1.09 | 1.04 | 1.07 | 1.04 | 1.04 | 1.02 | 1.11 | 1.02 |
| pangui/flex_expand_equal_weights | 1.10 | 1.13 | 1.11 | 1.15 | 1.16 | 1.22 | 1.09 | 1.08 | 1.05 | 1.04 | 1.03 | 1.02 | 1.02 |
| pangui/flex_expand_weights | 1.10 | 1.19 | 1.07 | 1.28 | 1.23 | 1.14 | 1.04 | 1.08 | 1.10 | 1.06 | 1.07 | 1.02 | 1.07 |
| pangui/nested_vertical_stack | 1.07 | 1.12 | 1.07 | 1.18 | 1.12 | 1.17 | 1.02 | 1.08 | 1.08 | 1.05 | 1.05 | 1.04 | 1.02 |
| pangui/padding_and_margin | 1.16 | 2.36 | 1.08 | 1.17 | 1.27 | 1.20 | 1.06 | 1.16 | 1.08 | 1.05 | 1.10 | 1.05 | 1.05 |
| pangui/percentage_and_ratio | 1.17 | 1.17 | 1.10 | 1.18 | 1.29 | 1.14 | 1.06 | 1.08 | 1.05 | 1.03 | 1.07 | 1.04 | 1.03 |
| pangui/perpendicular_expand_with_wrap | 1.19 | 1.07 | 1.25 | 1.25 | 1.16 | 1.18 | 1.05 | 1.09 | 1.04 | 1.11 | 1.06 | 1.05 | 1.01 |
| pangui/pixels_with_min_expand_constraint | 1.19 | 1.15 | 1.06 | 1.21 | 1.15 | 1.09 | 1.07 | 1.04 | 1.11 | 1.09 | 1.08 | 1.03 | 1.01 |
| pangui/wide_no_wrap_simple_few | 1.67 | 1.42 | 1.16 | 1.11 | 1.08 | 1.13 | 1.06 | 1.10 | 1.08 | 1.03 | 1.08 | 1.08 | 1.11 |
| pangui/wide_no_wrap_simple_many | 1.09 | 1.22 | 1.09 | 1.20 | 1.05 | 1.07 | 1.07 | 1.07 | 1.08 | 1.06 | 1.08 | 1.11 | 1.03 |
| pangui/wide_wrapping | 1.10 | 1.21 | 1.16 | 1.17 | 1.31 | 1.19 | 1.03 | 1.07 | 1.10 | 1.08 | 1.07 | 1.09 | 1.02 |
| text/paragraphs/100 | 1.15 | 1.72 | 1.57 | 1.16 | 1.44 | 1.18 | 1.08 | 1.06 | 1.04 | 1.35 | 1.23 | - | 1.01 |
| text/flex_cards/100 | 1.13 | 1.14 | 1.11 | 1.15 | 1.24 | 1.12 | 1.05 | 1.13 | 1.04 | 1.20 | 1.11 | - | 1.05 |
| text/inline_mixed/100 | 1.11 | 1.49 | 1.32 | 1.14 | 1.64 | 1.18 | 1.05 | 1.07 | 1.08 | 1.16 | 1.11 | - | 1.02 |
| text/paragraphs/1000 | 1.17 | 1.35 | 1.28 | 1.51 | 1.24 | 1.09 | 1.04 | 1.08 | 1.05 | 1.22 | 1.03 | - | 1.02 |
| text/flex_cards/1000 | 1.13 | 1.33 | 1.04 | 1.40 | 1.14 | 1.11 | 1.04 | 1.05 | 1.13 | 1.14 | 1.07 | - | 1.02 |
| text/inline_mixed/1000 | 1.11 | 1.17 | 1.10 | 1.15 | 1.11 | 1.12 | 1.03 | 1.06 | 1.04 | 1.09 | 1.04 | - | 1.04 |
| real/wikipedia | 1.13 | 1.13 | 1.13 | 1.08 | 1.25 | 1.08 | 1.12 | 1.10 | 1.02 | 1.13 | 1.04 | - | 1.01 |
| real/mdn | 1.18 | 1.16 | 1.12 | 1.25 | 1.22 | 1.09 | 1.07 | 1.07 | 1.09 | 1.49 | 1.13 | - | 1.04 |
| real/rustdoc | 1.06 | 1.12 | 1.12 | 1.11 | 1.12 | 1.07 | 1.06 | 1.08 | 1.06 | 1.08 | 1.03 | - | 1.01 |
| real/css-flexbox-1 | 1.06 | 1.20 | 1.08 | 1.08 | 1.13 | 1.10 | 1.16 | 1.10 | 1.08 | 1.09 | 1.06 | - | 1.07 |
| real/servo-org | 1.08 | 1.09 | 1.11 | 1.18 | 1.35 | 1.12 | 1.10 | 1.03 | 1.09 | 2.43 | 1.13 | - | 1.02 |
| real/dioxuslabs-com | 1.03 | 1.12 | 1.11 | 1.23 | 3.21 | 1.08 | 1.24 | 1.07 | 1.05 | 1.44 | 1.15 | - | 1.03 |
| real/bootstrap-dashboard | 1.12 | 1.34 | 1.40 | 2.00 | 2.73 | 1.23 | 1.08 | 1.04 | 1.05 | 1.88 | 1.06 | - | 1.07 |
| **median case** | 1.11 | 1.20 | 1.12 | 1.17 | 1.16 | 1.12 | 1.07 | 1.07 | 1.06 | 1.08 | 1.07 | 1.05 | 1.02 |
| **p90 case** | 1.19 | 1.56 | 1.30 | 1.41 | 1.40 | 1.22 | 1.13 | 1.10 | 1.10 | 1.41 | 1.15 | 1.10 | 1.09 |
