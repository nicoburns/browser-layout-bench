"""Horizontal bar charts of out/results.json: one SVG per case (out/plots/<suite>/<case>.svg) with a
section per report table and a bar per engine column — bar = minimum of the samples in ms, a lighter
extension to the median; label = ms, multiple of the fastest browser of the section, time per node —
plus one Markdown page per suite embedding its cases (out/plots/<suite>.md). `./run.py plot` writes them."""
import html
import math
import statistics

WIDTH, LEFT, RIGHT, BAR, GAP = 1000, 340, 230, 16, 6
COLOURS = {
    "chrome": "#60a5fa", "firefox1": "#fb923c", "firefox": "#fdba74", "ladybird": "#facc15", "servo1": "#c084fc",
    "servo": "#e9d5ff", "blitz": "#34d399", "blitz-par": "#6ee7b7", "blitz-pcon": "#2dd4bf", "blitz-par-pcon": "#99f6e4",
    "blitz-pcon-pl1": "#a3e635", "blitz-pcon-pl": "#bef264", "blitz-par-pcon-pl": "#d9f99d", "taffy": "#fb7185",
}


def slug(s):
    return "".join(c if c.isalnum() else "-" for c in s.lower()).strip("-")


def suites(results):
    return list(dict.fromkeys(name.split("/")[0] for name in results))


def case_path(name):
    """Path of a case's SVG relative to out/plots/, e.g. flex/wide/10000 -> flex/wide-10000.svg."""
    suite, _, rest = name.partition("/")
    return f"{suite}/{slug(rest)}.svg"


def fmt_per_node(ns):
    unit, v = ("ms", ns / 1e6) if ns >= 1e6 else ("us", ns / 1e3) if ns >= 1e3 else ("ns", ns)
    return f"{v:.3g} {unit}/node"


def axis(max_value):
    """Linear axis 0..top with a 1-2-5 tick step giving 4–8 ticks."""
    raw = max_value / 5
    mag = 10 ** math.floor(math.log10(raw))
    step = mag * next(f for f in (1, 2, 5, 10) if raw / mag <= f * 1.5)
    top = math.ceil(max_value / step) * step
    return top, [i * step for i in range(int(round(top / step)) + 1)]


def sections(data, columns_by_table):
    """[(table title, [(engine, label, min ms, median ms)])] for the columns the case has samples for."""
    out = []
    for title, columns in columns_by_table:
        bars = []
        for e, key, label in columns:
            vals = sorted(s[key] for s in data["engines"].get(e, []) if s.get(key) is not None)
            if vals:
                bars.append((e, label.replace("`", ""), vals[0] / 1e6, statistics.median(vals) / 1e6))
        if bars:
            out.append((title, bars))
    return out


def plot_case(name, data, columns_by_table, path):
    secs = sections(data, columns_by_table)
    nodes = data["nodes"] or 1
    body, y = [], 70
    for title, bars in secs:
        top, ticks = axis(max(med for _, _, _, med in bars))
        x = lambda v: LEFT + v / top * (WIDTH - LEFT - RIGHT)
        browsers = [lo for e, _, lo, _ in bars if e != "taffy"]
        fastest = min(browsers) if browsers else min(lo for _, _, lo, _ in bars)
        body.append(f'<text x="16" y="{y + 14}" fill="#f9fafb" font-size="13" font-weight="600">{html.escape(title)}</text>')
        y0 = y + 24
        height = len(bars) * (BAR + GAP) + GAP
        for t in ticks:
            tx = x(t)
            body.append(f'<line x1="{tx:.1f}" x2="{tx:.1f}" y1="{y0}" y2="{y0 + height}" stroke="#374151" stroke-dasharray="2 4"/>'
                        f'<text x="{tx:.1f}" y="{y0 + height + 14}" fill="#9ca3af" font-size="10" text-anchor="middle">{t:g}</text>')
        body.append(f'<text x="{WIDTH - RIGHT + 14}" y="{y0 + height + 14}" fill="#9ca3af" font-size="10">ms</text>')
        for k, (e, label, lo, med) in enumerate(bars):
            c, by = COLOURS.get(e, "#9ca3af"), y0 + GAP + k * (BAR + GAP)
            best = lo == fastest and e != "taffy"
            body.append(f'<text x="{LEFT - 10}" y="{by + BAR - 4}" fill="{c}" font-size="11" text-anchor="end"'
                        f'{" font-weight=\"700\"" if best else ""}>{html.escape(label)}</text>'
                        f'<rect x="{LEFT}" y="{by}" width="{max(x(lo) - LEFT, 1):.1f}" height="{BAR}" fill="{c}"/>'
                        f'<rect x="{x(lo):.1f}" y="{by}" width="{x(med) - x(lo):.1f}" height="{BAR}" fill="{c}" opacity="0.35"/>'
                        f'<text x="{x(med) + 6:.1f}" y="{by + BAR - 4}" fill="#e5e7eb" font-size="11">'
                        f'{lo:.3g} ms <tspan fill="#9ca3af">· {lo / fastest:.2f}x · {fmt_per_node(lo * 1e6 / nodes)}</tspan></text>')
        y = y0 + height + 36
    total = y + 24
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{total}" viewBox="0 0 {WIDTH} {total}" '
           f'font-family="system-ui, -apple-system, Segoe UI, Helvetica, Arial, sans-serif">',
           f'<rect width="{WIDTH}" height="{total}" fill="#0b1120"/>',
           f'<text x="16" y="24" fill="#f9fafb" font-size="16" font-weight="600">{html.escape(name)}'
           f' <tspan fill="#9ca3af" font-size="12" font-weight="400">{data["nodes"]} nodes</tspan></text>',
           '<text x="16" y="42" fill="#9ca3af" font-size="11">Bar = minimum of the samples (ms, linear axis per section), '
           'lighter extension to the median.</text>',
           '<text x="16" y="56" fill="#9ca3af" font-size="11">Label: ms · multiple of the fastest browser of the section '
           '(bold; Taffy excluded) · time per node.</text>',
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
                "[the report](../report.md) and a bar per engine: bar = minimum of the samples in ms, lighter extension "
                "to the median; label = ms, multiple of the fastest browser of the section, time per node.", ""]
        for name, data in cases:
            page += [f"## {name}", "", f"{data['nodes']} nodes.", "", f"![{name}]({case_path(name)})", ""]
        p = out_dir / f"{suite}.md"
        p.write_text("\n".join(page))
        written.append(p)
    index = ["# Plots", "", "One SVG per case, grouped per suite (`./run.py plot`): horizontal bars, a section per report "
             "table, a bar per engine (minimum of the samples in ms, lighter extension to the median).", ""]
    index += [f"- [`{s}/`]({s}.md) ({len(cases)} cases)" for s, cases in by_suite.items()]
    (out_dir / "README.md").write_text("\n".join(index) + "\n")
    written.append(out_dir / "README.md")
    return written
