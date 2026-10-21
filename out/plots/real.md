# `real/` cases

One chart per case (`./run.py plot`), a section per table of [the report](../report.md) except Layout only and Construction (their numbers are the segments of the construction+layout stack; Taffy is in the report only) and a bar per engine: bar = minimum of the samples in ms, lighter extension to the median, construction+layout and whole-pipeline bars stacked by stage where the engine records them; label = ms, multiple of the fastest browser of the section, time per node.

## real/wikipedia

21889 nodes.

![real/wikipedia](real/wikipedia.svg)

## real/mdn

2212 nodes.

![real/mdn](real/mdn.svg)

## real/rustdoc

15947 nodes.

![real/rustdoc](real/rustdoc.svg)

## real/css-flexbox-1

15890 nodes.

![real/css-flexbox-1](real/css-flexbox-1.svg)

## real/servo-org

226 nodes.

![real/servo-org](real/servo-org.svg)

## real/dioxuslabs-com

158 nodes.

![real/dioxuslabs-com](real/dioxuslabs-com.svg)

## real/bootstrap-dashboard

199 nodes.

![real/bootstrap-dashboard](real/bootstrap-dashboard.svg)
