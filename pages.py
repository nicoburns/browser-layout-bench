"""Static results site (out/pages/) from out/results.json: a landing page with the README methodology and
the caveats, and one results page with a Table and a Charts tab (one stacked bar chart per case). The
results page is a shell; `web/site.js` draws it from the exported `data.js`, so the tab, suite,
comparison, statistic and engine switches run in the browser. `./run.py pages` writes it; the Pages workflow deploys it."""
import html
import json
import re
import shutil
import statistics
from pathlib import Path

import plot

ASSETS = Path(__file__).resolve().parent / "web"
REPO = "https://github.com/nicoburns/browser-layout-bench"

ENGINE_NAMES = {
    "chrome": "Chrome", "firefox1": "Firefox (1 style thread)", "firefox": "Firefox", "ladybird": "Ladybird",
    "servo1": "Servo (1 layout thread)", "servo": "Servo (3 layout threads)", "blitz": "Blitz",
    "blitz-par": "Blitz, parallel style", "blitz-pcon": "Blitz, parallel construct",
    "blitz-par-pcon": "Blitz, parallel style + construct", "blitz-pcon-pl1": "Blitz #1034 build, 1 thread",
    "blitz-par-pcon-pl": "Blitz #1034 build, parallel style + construct + layout", "taffy": "Taffy",
}
# plot.COLOURS is tuned for its dark background; these are the same engine hues for white.
COLOURS = {
    "chrome": "#E8A100", "firefox1": "#FF7139", "firefox": "#FFA37E", "ladybird": "#7B6CF0",
    "servo1": "#2FA857", "servo": "#84D59B", "blitz": "#007672", "blitz-par": "#3E9593",
    "blitz-pcon": "#62AFAD", "blitz-par-pcon": "#88C6C4", "blitz-pcon-pl1": "#A9D8D6",
    "blitz-par-pcon-pl": "#C6E6E5", "taffy": "#E11D48",
}
# Engine/case pairs README "Running" lists as unequal work: flagged and never the fastest of a row.
UNEQUAL = {
    ("pangui/percentage_and_ratio", "servo"): "renders empty in Servo (aspect-ratio items get zero height)",
    ("pangui/percentage_and_ratio", "servo1"): "renders empty in Servo (aspect-ratio items get zero height)",
}
# README "Running", cases that cannot be made equal: shown under the case's chart.
CASE_NOTES = {
    "flex/absolute/10000": "Not equal work: percent insets on a 424,000px-wide root amplify f32 rounding, so engines place boxes up to ~170px apart (root sizes agree to 0.003%).",
    "pangui/percentage_and_ratio": "Servo renders this case empty (aspect-ratio items get zero height), so its Servo timings are not comparable.",
    "pangui/fit_nesting": "0.99px leaves: Blitz and Servo snap them to the pixel grid differently from Chrome (~11% of pixels differ; box sizes agree within 1px).",
    "pangui/flex_expand_equal_weights": "0.67px items: Blitz and Servo snap them to the pixel grid differently from Chrome (~11% of pixels differ; box sizes agree within 1px).",
}
SUITE_BLURBS = {
    "flex": "Flexbox trees from Taffy's benchmark suite (wide, deep, super-deep, absolutely positioned); no text.",
    "grid": "CSS Grid trees from Taffy's benchmark suite (wide and deep grids); no text.",
    "pangui": "The PanGUI flexbox templates from Taffy's benchmark crate; no text except where noted.",
    "text": "Hand-built prose pages set in DejaVu Sans: shaping and line breaking as well as layout.",
    "real": "Seven saved web pages frozen by real/freeze.py (scripts removed, fonts replaced, images as placeholders).",
}


def slug(text):
    """GitHub's heading anchor: lower-case, punctuation dropped, spaces to hyphens."""
    return re.sub(r"[^\w\- ]", "", text.strip().lower()).replace(" ", "-")


def section(md, heading):
    """Body of the `## heading` section of a Markdown file (up to the next `## `), or "" if absent."""
    m = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", md, re.S | re.M)
    return m.group(1).strip() if m else ""


def inline(text, base):
    """Inline Markdown (code, bold, links) to HTML; relative links point at the repo on GitHub."""
    out, pos = [], 0
    for m in re.finditer(r"`([^`]+)`", text):
        out.append(inline_plain(text[pos:m.start()], base))
        out.append(f"<code>{html.escape(m.group(1))}</code>")
        pos = m.end()
    out.append(inline_plain(text[pos:], base))
    return "".join(out)


def inline_plain(text, base):
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

    def link(m):
        href = m.group(2)
        if not re.match(r"^(https?:|#|mailto:)", href):
            href = base + href
        return f'<a href="{html.escape(href)}">{m.group(1)}</a>'
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)


def md_to_html(md, base=f"{REPO}/blob/main/", shift=0):
    """The subset of Markdown the README and CAVEATS use: headings (levels shifted by `shift`), paragraphs,
    `-` lists with indented continuation lines, pipe tables with an alignment row, fenced code."""
    out, lines, i = [], md.split("\n"), 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
        elif line.startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            out.append("<pre><code>" + html.escape("\n".join(lines[i + 1:j])) + "</code></pre>")
            i = j + 1
        elif re.match(r"^#{1,4} ", line):
            level, text = line.split(" ", 1)
            n = min(len(level) + shift, 6)
            out.append(f'<h{n} id="{slug(text)}">{inline(text, base)}</h{n}>')
            i += 1
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            aligns = ["right" if c.endswith(":") and not c.startswith(":") else "left" for c in rows[1]] if len(rows) > 1 else []
            out.append('<div class="scroll"><table class="prose">')
            out.append("<thead><tr>" + "".join(f"<th>{inline(c, base)}</th>" for c in rows[0]) + "</tr></thead><tbody>")
            for row in rows[2:]:
                out.append("<tr>" + "".join(f'<td class="{aligns[k] if k < len(aligns) else "left"}">{inline(c, base)}</td>'
                                            for k, c in enumerate(row)) + "</tr>")
            out.append("</tbody></table></div>")
        elif line.startswith("- "):
            out.append("<ul>")
            while i < len(lines) and lines[i].startswith("- "):
                item = [lines[i][2:]]
                i += 1
                while i < len(lines) and lines[i].startswith("  "):
                    item.append(lines[i].strip())
                    i += 1
                out.append(f"<li>{inline(' '.join(item), base)}</li>")
            out.append("</ul>")
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,4} |- |\||```)", lines[i]):
                para.append(lines[i].strip())
                i += 1
            out.append(f"<p>{inline(' '.join(para), base)}</p>")
    return "\n".join(out)


# ---- data export ----

def export(results, columns, count_keys):
    """The JSON `site.js` draws from: per case and engine the numeric metrics as aligned sample rows
    (ms), the report's tables (engine, metric, label), engine names/colours and the stacked-bar stages."""
    cases = []
    for name, data in results.items():
        engines = {}
        for e, samples in data["engines"].items():
            metrics = sorted({k for s in samples for k in s if k not in count_keys and isinstance(s[k], (int, float))})
            if not metrics:
                continue
            engines[e] = {"metrics": metrics,
                          "samples": [[round(s[k] / 1e6, 4) if s.get(k) is not None else None for k in metrics] for s in samples],
                          "normalized": any("chrome_norm" in s for s in samples)}
        cases.append({"name": name, "suite": name.split("/")[0], "nodes": data["nodes"], "engines": engines,
                      "note": CASE_NOTES.get(name)})
    tables = [{"title": title, "columns": [{"engine": e, "metric": m, "label": label} for e, m, label in cols]}
              for title, cols in columns]
    engines = [e for e in ENGINE_NAMES if any(e in c["engines"] for c in cases)]
    return {"cases": cases, "tables": tables, "stages": plot.STAGES,
            "engines": {e: {"name": ENGINE_NAMES[e], "colour": COLOURS[e]} for e in engines},
            "unequal": [{"case": c, "engine": e, "note": note} for (c, e), note in UNEQUAL.items()],
            "suites": [{"name": s, "blurb": SUITE_BLURBS.get(s, "")} for s in plot.suites(results)]}


def normalized_engines(results):
    return sorted({e for d in results.values() for e, samples in d["engines"].items() if any("chrome_norm" in s for s in samples)})


def norm_factor_median(results):
    factors = [s["chrome_norm"] for d in results.values() for samples in d["engines"].values() for s in samples if "chrome_norm" in s]
    return statistics.median(factors) if factors else None


# ---- pages ----

def page(title, body, active, root_url):
    nav = [("index.html", "Overview", "index"), ("results.html", "Results", "results")]
    links = "".join(f'<a href="{href}" class="{"active" if key == active else ""}">{html.escape(label)}</a>' for href, label, key in nav)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} · layout-bench</title>
<link rel="stylesheet" href="site.css">
</head>
<body>
<header class="top">
<a class="brand" href="index.html">layout-bench</a>
<nav>{links}</nav>
<a class="repo" href="{root_url}">GitHub</a>
</header>
<main>
{body}
</main>
<footer>Generated by <code>./run.py pages</code> from <a href="{root_url}/blob/main/out/results.json">out/results.json</a>;
times are minima over 9 samples unless the statistic switch says otherwise.</footer>
<script src="data.js"></script>
<script src="site.js"></script>
</body>
</html>
"""


def caveat_box(results):
    """The normalisation caveat shown next to every table and chart."""
    normalized = normalized_engines(results)
    if not normalized:
        return ""
    return (f'<p class="caveat"><strong>†</strong> The Servo and Blitz columns ({html.escape(", ".join(normalized))}) were measured in a later run '
            f"and scaled per case by Chrome's stored/new <code>style+layout</code> ratio (median {norm_factor_median(results):.2f}); "
            "differences under ~10% between them and the Chrome, Firefox, Ladybird and Taffy columns are within the normalisation's "
            'uncertainty (<a href="index.html#versions-and-methodology">methodology</a>). Rankings also carry the '
            '<a href="index.html#caveats">equal-work and sampling caveats</a>.</p>')


def controls():
    return '<div class="controls" id="controls"></div>'


def index_page(results, readme, caveats, by_suite):
    intro = md_to_html(readme.split("\n## ", 1)[0].split("\n", 1)[1])
    cards = "".join(
        f'<a class="card" href="results.html#g={s}"><h3>{s}/</h3><p>{html.escape(SUITE_BLURBS.get(s, ""))}</p>'
        f'<p class="meta">{len(cases)} cases · {min(c["nodes"] for c in cases):,}–{max(c["nodes"] for c in cases):,} nodes</p></a>'
        for s, cases in by_suite.items())
    interpret = md_to_html(section(caveats, "How to interpret the results"))
    caveats_body = md_to_html(caveats.split("\n## ", 1)[1].rsplit("\n## How to interpret", 1)[0] if "\n## " in caveats else "", shift=1)
    caveat_lead = md_to_html(caveats.split("\n## ", 1)[0].split("\n", 1)[1])
    return f"""
<section class="hero">
<h1>Layout benchmark results</h1>
{intro}
<div class="cards">{cards}<a class="card" href="results.html#g="><h3>All suites</h3><p>Every case in one table: pick a suite, a comparison table and the engines.</p><p class="meta">{len(results)} cases</p></a></div>
</section>

<section id="reading">
<h2>Reading the numbers</h2>
{caveat_box(results)}
{interpret}
</section>

<section id="versions-and-methodology">
<h2>Versions and methodology</h2>
{md_to_html(section(readme, "Versions and methodology"), shift=1)}
</section>

<section id="engines-and-phases">
<h2>Engines and phases</h2>
<details><summary>How each engine is run and which spans are compared (from the README)</summary>
{md_to_html(section(readme, "Engines and phases"), shift=1)}
</details>
</section>

<section id="caveats">
<h2>Caveats</h2>
{caveat_lead}
<details><summary>The six caveats in full (<a href="{REPO}/blob/main/CAVEATS.md">CAVEATS.md</a>)</summary>
{caveats_body}
</details>
</section>

<section id="corpus">
<h2>Corpus</h2>
<details><summary>How the pages are built (from the README)</summary>
{md_to_html(section(readme, "Corpus"), shift=1)}
</details>
</section>
"""


def results_page(results):
    return f"""
<h1>Results</h1>
<p>Pick a suite and one of the report's comparison tables. The Table tab gives the numbers; the Charts tab draws a bar
per engine for each case, stacked by stage, with the spread of the samples.</p>
{controls()}
{caveat_box(results)}
<section id="summary"></section>
<section id="table" class="results-table"></section>
<section id="charts" class="charts"></section>
"""


def build(results, columns, count_keys, root, out_dir):
    readme = (root / "README.md").read_text()
    caveats = (root / "CAVEATS.md").read_text()
    data = export(results, columns, count_keys)
    suites = plot.suites(results)
    by_suite = {s: [c for c in data["cases"] if c["suite"] == s] for s in suites}
    shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True)
    written = []

    def write(name, text):
        (out_dir / name).write_text(text)
        written.append(out_dir / name)

    write("data.js", "window.DATA = " + json.dumps(data, separators=(",", ":")) + ";\n")
    write("index.html", page("Overview", index_page(results, readme, caveats, by_suite), "index", REPO))
    write("results.html", page("Results", results_page(results), "results", REPO))
    for asset in ("site.css", "site.js"):
        shutil.copy(ASSETS / asset, out_dir / asset)
        written.append(out_dir / asset)
    write(".nojekyll", "")
    return written
