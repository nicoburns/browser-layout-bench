"""Dot plots of out/results.json in the style of arewelayoutyet.mespin.me: one SVG per suite (the
case-name prefix), report table and view mode, a row per case, a dot per engine (whisker = min to
median of its samples), log x axis, faster to the left. `./run.py plot` writes them to out/plots/."""
import html
import json
import math
import statistics
from pathlib import Path

LEFT, TOP, WIDTH, RIGHT_PAD, LANE = 270, 70, 1200, 70, 14
ENGINES = {  # engine id -> (dot label, colour)
    "chrome": ("Chrome", "#60a5fa"), "firefox1": ("Firefox(1)", "#fb923c"), "firefox": ("Firefox", "#fdba74"),
    "ladybird": ("Ladybird", "#facc15"), "servo1": ("Servo(1)", "#c084fc"), "servo": ("Servo(3)", "#e9d5ff"),
    "blitz": ("Blitz", "#34d399"), "blitz-par": ("Blitz par style", "#6ee7b7"),
    "blitz-pcon": ("Blitz par construct", "#2dd4bf"), "blitz-par-pcon": ("Blitz par style+construct", "#99f6e4"),
    "blitz-pcon-pl1": ("Blitz #1034 1 thread", "#a3e635"), "blitz-pcon-pl": ("Blitz #1034 par layout", "#bef264"),
    "blitz-par-pcon-pl": ("Blitz #1034 all parallel", "#d9f99d"), "taffy": ("Taffy", "#fb7185"),
}
MODES = {
    "per-node": ("Time per node (ns/node, log scale), faster to the left",
                 "Dots are the minimum of the samples divided by the case's node count; whiskers run to the median."),
    "relative": ("Relative to the fastest engine of the row (log scale), faster to the left",
                 "The fastest engine of each row is 1x; dots are minimums, whiskers run to the median."),
    "milliseconds": ("Time (ms, log scale), faster to the left",
                     "Dots are the minimum of the samples; whiskers run to the median."),
}


def slug(s):
    return "".join(c if c.isalnum() else "-" for c in s.lower()).strip("-")


def fmt_tick(t, mode):
    if mode == "relative":
        return f"{t:g}x"
    if mode == "milliseconds":
        return f"{t:g} ms"
    return f"{t / 1e6:g} ms/node" if t >= 1e6 else f"{t / 1e3:g} us/node" if t >= 1e3 else f"{t:g} ns/node"


def plot(results, suite, title, columns, mode, path):
    cases = [(name, data) for name, data in results.items()
             if name.split("/")[0] == suite and any(e in data["engines"] for e, _, _ in columns)]
    engines = [(e, ENGINES[e][0], ENGINES[e][1], label.replace("`", "")) for e, _, label in columns]
    rows = []
    for name, data in cases:
        pts = []
        for i, (e, key, label) in enumerate(columns):
            samples = data["engines"].get(e)
            if not samples:
                continue
            vals = sorted(s[key] for s in samples if s.get(key) is not None)
            if not vals:
                continue
            pts.append((i, vals[0], statistics.median(vals)))
        if not pts:
            continue
        nodes = data["nodes"] or 1
        fastest = min(v for _, v, _ in pts)
        div = {"per-node": nodes, "relative": fastest, "milliseconds": 1e6}[mode]
        rows.append((name, [(i, lo / div, med / div) for i, lo, med in pts]))
    values = [v for _, pts in rows for _, lo, med in pts for v in (lo, med)]
    lo_axis = min(values)
    first = 1 if mode == "relative" else 10 ** math.floor(math.log10(lo_axis))
    axis_min = min(1, lo_axis) * 0.98 if mode == "relative" else first
    maximum = max(first * 2, *values)
    ticks = [first]
    while ticks[-1] < maximum:
        ticks.append(ticks[-1] * 10)
    if len(ticks) <= 3:
        ticks = sorted({t * f for t in ticks for f in (1, 2, 5)} | {ticks[-1]})
        ticks = [t for t in ticks if t <= ticks[-1] and t >= first]
    right = WIDTH - RIGHT_PAD
    x = lambda v: LEFT + math.log(v / axis_min) / math.log(ticks[-1] / axis_min) * (right - LEFT)
    out, y = [], TOP
    body = []
    for row_index, (name, pts) in enumerate(rows):
        placed = []
        for i, lo, med in sorted(pts, key=lambda p: p[1]):
            label, c = engines[i][1], engines[i][2]
            lw = len(label) * 6.2
            px, pl, pm = x(lo), x(lo), x(med)
            on_left = pm + 12 + lw > WIDTH - 16
            start = min(pl, px - 6, px - 15 - lw if on_left else px)
            end = max(pm, px + 6, px if on_left else pm + 15 + lw)
            lane = next((k for k, e in enumerate(placed) if e + 10 <= start), len(placed))
            if lane == len(placed):
                placed.append(end)
            else:
                placed[lane] = end
            cy = y + 12 + lane * LANE
            body.append(f'<line x1="{pl:.1f}" x2="{pm:.1f}" y1="{cy}" y2="{cy}" stroke="{c}" stroke-width="2" opacity="0.7"/>'
                        f'<circle cx="{px:.1f}" cy="{cy}" r="4.5" fill="{c}"/>'
                        f'<text x="{px - 9 if on_left else pm + 9:.1f}" y="{cy + 4}" fill="{c}" font-size="11"'
                        f' text-anchor="{"end" if on_left else "start"}">{html.escape(label)}</text>')
        h = 10 + max(1, len(placed)) * LANE + 6
        out.append(f'<rect x="0" y="{y}" width="{WIDTH}" height="{h}" fill="{"#1f2937" if row_index % 2 else "#0f172a"}"/>'
                   f'<line x1="0" x2="{WIDTH}" y1="{y}" y2="{y}" stroke="#6b7280" stroke-width="1"/>')
        out.append(f'<text x="{LEFT - 12}" y="{y + 16}" fill="#f9fafb" font-size="12" font-weight="600" text-anchor="end">'
                   f'{html.escape(name.split("/", 1)[1])}</text>')
        out.extend(body)
        body = []
        y += h
    bottom = y
    out.append(f'<line x1="0" x2="{WIDTH}" y1="{bottom}" y2="{bottom}" stroke="#6b7280" stroke-width="1"/>')
    grid = []
    for t in ticks:
        tx = x(t)
        tl = fmt_tick(t, mode)
        grid.append(f'<line x1="{tx:.1f}" x2="{tx:.1f}" y1="{TOP}" y2="{bottom}" stroke="#374151" stroke-dasharray="2 4"/>'
                    f'<text x="{tx:.1f}" y="{TOP - 8}" fill="#9ca3af" font-size="11" text-anchor="middle">{tl}</text>'
                    f'<text x="{tx:.1f}" y="{bottom + 16}" fill="#9ca3af" font-size="11" text-anchor="middle">{tl}</text>')
    legend = [f'<text x="16" y="{bottom + 44 + 16 * k}" font-size="11" fill="{c}">● {html.escape(short)}: '
              f'<tspan fill="#9ca3af">{html.escape(full)}</tspan></text>' for k, (_, short, c, full) in enumerate(engines)]
    height = bottom + 60 + 16 * len(engines)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" '
           f'font-family="system-ui, -apple-system, Segoe UI, Helvetica, Arial, sans-serif">',
           f'<rect width="{WIDTH}" height="{height}" fill="#0b1120"/>',
           f'<text x="16" y="24" fill="#f9fafb" font-size="16" font-weight="600">{html.escape(f"{title}: {suite}/ cases")}</text>',
           f'<text x="16" y="42" fill="#9ca3af" font-size="11">{html.escape(MODES[mode][0])}. {html.escape(MODES[mode][1])}</text>',
           *grid, *out,
           *legend, '</svg>']
    path.write_text("\n".join(svg))


def suites(results):
    return list(dict.fromkeys(name.split("/")[0] for name in results))


def links(table, suite):
    return " · ".join(f"[{m}]({suite}/{slug(table)}-{m}.svg)" for m in MODES)


def plot_all(results, columns_by_table, out_dir):
    written = []
    for suite in suites(results):
        (out_dir / suite).mkdir(parents=True, exist_ok=True)
        for table, columns in columns_by_table:
            for mode in MODES:
                p = out_dir / suite / f"{slug(table)}-{mode}.svg"
                plot(results, suite, table, columns, mode, p)
                written.append(p)
    index = ["# Plots", "", "One SVG per suite, report table and view (`./run.py plot`); rows are cases, dots are engines "
             "(minimum of the samples, whisker to the median), log x axis, faster to the left. Views: `per-node` = ns per "
             "node of the case, `relative` = multiple of the fastest engine of the row, `milliseconds`.", "",
             "| table | " + " | ".join(f"`{s}/`" for s in suites(results)) + " |", "|---|" + "---|" * len(suites(results))]
    for table, _ in columns_by_table:
        index.append(f"| {table} | " + " | ".join(links(table, s) for s in suites(results)) + " |")
    (out_dir / "README.md").write_text("\n".join(index) + "\n")
    written.append(out_dir / "README.md")
    return written
