"""Horizontal bar charts of out/results.json: one SVG per case (out/plots/<suite>/<case>.svg) with a
section per report table except the two that the stacked bars already show (SKIPPED_TABLES) and a bar per engine column — bar = minimum of the samples in ms with a
whisker over all samples (p25–p75 thick, median tick), composite metrics stacked by stage (STAGES); label = ms, multiple of the fastest browser of the section, time per node —
plus one Markdown page per suite embedding its cases (out/plots/<suite>.md). `./run.py plot` writes them."""
import html
import math
import statistics

WIDTH, LEFT, RIGHT, BAR, GAP = 1000, 340, 230, 16, 6
# Composite metrics drawn as a stack of their recorded stages (left to right); the part of the
# composite the stages do not cover is drawn as "other". Metrics not listed are a plain bar.
STAGES = {
    "construct+layout": [("construct", "construct"), ("layout", "layout")],
    "box+fragment": [("box", "construct"), ("fragment", "layout")],
    "style+layout": [("style", "style"), ("construct", "construct"), ("layout", "layout")],
    "restyle_and_build": [("style", "style"), ("box", "construct"), ("fragment", "layout")],
    "resolve": [("style", "style"), ("construct", "construct"), ("layout", "layout")],
    "total": [("style", "style"), ("construct", "construct"), ("layout", "layout")],
}
STAGE_OPACITY = [1.0, 0.65, 0.4, 0.25]
COLOURS = {
    "chrome": "#FBBC04", "webkit": "#4DA3FF", "firefox": "#FF7139", "ladybird": "#7B6CF0",
    "servo1": "#42BE65", "servo": "#84d59b", "blitz": "#3E9593", "blitz-par": "#5ba5a3",
    "blitz-pcon": "#78b5b3", "blitz-par-pcon": "#95c5c4", "blitz-pcon-pl1": "#a8cfce",
    "blitz-par-pcon-pl": "#cfe4e4", "taffy": "#fb7185"
}


def slug(s):
    return "".join(c if c.isalnum() else "-" for c in s.lower()).strip("-")


def suites(results):
    return list(dict.fromkeys(name.split("/")[0] for name in results))


def case_path(name):
    """Path of a case's SVG relative to out/plots/, e.g. flex/wide/10000 -> flex/wide-10000.svg."""
    suite, _, rest = name.partition("/")
    return f"{suite}/{slug(rest)}.svg"


def fmt(v):
    """3 significant digits, never in exponent notation (`:.3g` would write 1.52e+03 and 8.88e-16)."""
    return f"{v:.0f}" if v >= 100 else f"{v:.3g}" if v >= 1e-3 else "0"


def fmt_per_node(ns):
    unit, v = ("ms", ns / 1e6) if ns >= 1e6 else ("us", ns / 1e3) if ns >= 1e3 else ("ns", ns)
    return f"{fmt(v)} {unit}/node"


def axis(max_value):
    """Linear axis 0..top with a 1-2-5 tick step giving 4–8 ticks."""
    raw = max_value / 5
    mag = 10 ** math.floor(math.log10(raw))
    step = mag * next(f for f in (1, 2, 5, 10) if raw / mag <= f * 1.5)
    top = math.ceil(max_value / step) * step
    return top, [i * step for i in range(int(round(top / step)) + 1)]


def stages(sample, key):
    """[(stage label, ms)] making up `sample[key]`, from the stages the sample records plus "other"."""
    parts = [(label, sample[k] / 1e6) for k, label in STAGES.get(key, []) if sample.get(k) is not None]
    rest = sample[key] / 1e6 - sum(v for _, v in parts)
    if parts and rest > 1e-3:  # below 1 us it is floating-point residue, not a stage
        parts.append(("other", rest))
    return parts


# Their bars are the construct / layout segments of the "Box construction + layout" stack (Taffy, which only has a
# layout number, is therefore in the report tables only).
SKIPPED_TABLES = ("Layout only", "Construction")


def sections(data, columns_by_table):
    """[(table title, [(engine, label, min ms, sorted sample ms, stages of the min sample)])] for the columns the case has samples for."""
    out = []
    for title, columns in columns_by_table:
        if title in SKIPPED_TABLES:
            continue
        bars = []
        for e, key, label in columns:
            samples = sorted((s for s in data["engines"].get(e, []) if s.get(key) is not None), key=lambda s: s[key])
            if samples:
                vals = [s[key] for s in samples]
                bars.append((e, label.replace("`", ""), vals[0] / 1e6, [v / 1e6 for v in vals], stages(samples[0], key)))
        if bars:
            out.append((title, bars))
    return out


def plot_case(name, data, columns_by_table, path):
    secs = sections(data, columns_by_table)
    nodes = data["nodes"] or 1
    body, y = [], 70
    for title, bars in secs:
        top, ticks = axis(max(vals[-1] for _, _, _, vals, _ in bars))
        x = lambda v: LEFT + v / top * (WIDTH - LEFT - RIGHT)
        browsers = [lo for e, _, lo, _, _ in bars if e != "taffy"]
        # WebKit's timeline has 20 us resolution, so a tiny relayout can record as 0 ms: the reference is the fastest non-zero
        fastest = min((lo for lo in browsers if lo > 0), default=0) or min((lo for _, _, lo, _, _ in bars if lo > 0), default=1)
        body.append(f'<text x="16" y="{y + 14}" fill="#f9fafb" font-size="13" font-weight="600">{html.escape(title)}</text>')
        if any(parts for *_, parts in bars):
            y += 16
            body.append(f'<text x="16" y="{y + 14}" fill="#9ca3af" font-size="11">Bars are stacked by stage where the engine '
                        'records them, left to right in pipeline order (solid → faint); grey = rest of the span; hover a segment for its value.</text>')
        y0 = y + 24
        height = len(bars) * (BAR + GAP) + GAP
        for t in ticks:
            tx = x(t)
            body.append(f'<line x1="{tx:.1f}" x2="{tx:.1f}" y1="{y0}" y2="{y0 + height}" stroke="#374151" stroke-dasharray="2 4"/>'
                        f'<text x="{tx:.1f}" y="{y0 + height + 14}" fill="#9ca3af" font-size="10" text-anchor="middle">{t:g}</text>')
        body.append(f'<text x="{WIDTH - RIGHT + 14}" y="{y0 + height + 14}" fill="#9ca3af" font-size="10">ms</text>')
        for k, (e, label, lo, vals, parts) in enumerate(bars):
            c, by = COLOURS.get(e, "#9ca3af"), y0 + GAP + k * (BAR + GAP)
            best = lo == fastest and e != "taffy"
            body.append(f'<text x="{LEFT - 10}" y="{by + BAR - 4}" fill="{c}" font-size="11" text-anchor="end"'
                        f'{" font-weight=\"700\"" if best else ""}>{html.escape(label)}</text>')
            if parts:
                at = 0.0
                for i, (stage, v) in enumerate(parts):
                    x0, x1 = x(at), x(min(at + v, lo))
                    fill, op = ("#6b7280", 1.0) if stage == "other" else (c, STAGE_OPACITY[min(i, len(STAGE_OPACITY) - 1)])
                    body.append(f'<rect x="{x0:.1f}" y="{by}" width="{max(x1 - x0, 0):.1f}" height="{BAR}" fill="{fill}" opacity="{op}"'
                                f'><title>{html.escape(stage)}: {fmt(v)} ms</title></rect>')
                    if x1 - x0 >= 26:
                        text = f"{stage} {fmt(v)}" if x1 - x0 >= 14 + 6.5 * len(f"{stage} {fmt(v)}") else fmt(v)
                        body.append(f'<text x="{(x0 + x1) / 2:.1f}" y="{by + BAR - 4}" fill="{"#e5e7eb" if stage == "other" else "#0b1120"}" '
                                    f'font-size="10" text-anchor="middle">{html.escape(text)}</text>')
                    at += v
            else:
                body.append(f'<rect x="{LEFT}" y="{by}" width="{max(x(lo) - LEFT, 1):.1f}" height="{BAR}" fill="{c}"/>')
            q1, med, q3 = statistics.quantiles(vals, n=4, method="inclusive") if len(vals) > 1 else (lo, lo, lo)
            hi, my = vals[-1], by + BAR / 2
            body.append(f'<g stroke="#e5e7eb" fill="none"><title>{len(vals)} samples: min {fmt(lo)} · p25 {fmt(q1)} · median {fmt(med)} '
                        f'· p75 {fmt(q3)} · max {fmt(hi)} ms</title>'
                        f'<line x1="{x(lo):.1f}" y1="{my}" x2="{x(hi):.1f}" y2="{my}" stroke-width="1"/>'
                        f'<line x1="{x(q1):.1f}" y1="{my}" x2="{x(q3):.1f}" y2="{my}" stroke="#9ca3af" stroke-width="5" opacity="0.35"/>'
                        f'<line x1="{x(med):.1f}" y1="{by + 1}" x2="{x(med):.1f}" y2="{by + BAR - 1}" stroke-width="2"/>'
                        f'<line x1="{x(hi):.1f}" y1="{by + 4}" x2="{x(hi):.1f}" y2="{by + BAR - 4}" stroke-width="1"/></g>'
                        f'<text x="{x(hi) + 6:.1f}" y="{by + BAR - 4}" fill="#e5e7eb" font-size="11">'
                        f'{fmt(lo)} ms <tspan fill="#9ca3af">· {lo / fastest:.2f}x · {fmt_per_node(lo * 1e6 / nodes)}</tspan></text>')
        y = y0 + height + 36
    total = y + 24
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{total}" viewBox="0 0 {WIDTH} {total}" '
           f'font-family="system-ui, -apple-system, Segoe UI, Helvetica, Arial, sans-serif">',
           f'<rect width="{WIDTH}" height="{total}" fill="#0b1120"/>',
           f'<text x="16" y="24" fill="#f9fafb" font-size="16" font-weight="600">{html.escape(name)}'
           f' <tspan fill="#9ca3af" font-size="12" font-weight="400">{data["nodes"]} nodes</tspan></text>',
           '<text x="16" y="42" fill="#9ca3af" font-size="11">Bar = minimum of the samples (ms, linear axis per section), '
           'whisker = all samples (thick: p25–p75, tick: median).</text>',
           '<text x="16" y="56" fill="#9ca3af" font-size="11">Label: ms · multiple of the fastest browser of the section '
           '(bold) · time per node.</text>',
           *body, '</svg>']
    path.write_text("\n".join(svg))


def plot_all(results, columns_by_table, out_dir):
    written = []
    by_suite = {}
    for name, data in results.items():
        p = out_dir / case_path(name)
        p.parent.mkdir(parents=True, exist_ok=True)
        plot_case(name, data, columns_by_table, p)
        written.append(p)
        by_suite.setdefault(name.split("/")[0], []).append((name, data))
    for suite, cases in by_suite.items():
        page = [f"# `{suite}/` cases", "", "One chart per case (`./run.py plot`), a section per table of "
                "[the report](../report.md) except Layout only and Construction (their numbers are the segments of the "
                "construction+layout stack; Taffy is in the report only) and a bar per engine: bar = minimum of the samples in ms, whisker = all samples (thick p25–p75, median tick), construction+layout and whole-pipeline bars stacked by stage where the engine records them; label = ms, "
                "multiple of the fastest browser of the section, time per node.", ""]
        for name, data in cases:
            page += [f"## {name}", "", f"{data['nodes']} nodes.", "", f"![{name}]({case_path(name)})", ""]
        p = out_dir / f"{suite}.md"
        p.write_text("\n".join(page))
        written.append(p)
    index = ["# Plots", "", "One SVG per case, grouped per suite (`./run.py plot`): horizontal bars, a section per report "
             "table except Layout only and Construction (covered by the stacked construction+layout bars; Taffy is in the report only), a bar per engine (minimum of the samples in ms, whisker = all samples (thick p25–p75, median tick)).", ""]
    index += [f"- [`{s}/`]({s}.md) ({len(cases)} cases)" for s, cases in by_suite.items()]
    (out_dir / "README.md").write_text("\n".join(index) + "\n")
    written.append(out_dir / "README.md")
    return written
