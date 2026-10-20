#!/usr/bin/env python3
"""Driver: generates the corpus, runs each engine on every page in interleaved rounds, and
writes results.json + a Markdown report. See README.md for the measurement model."""
import argparse, json, os, re, shutil, statistics, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CORPUS = ROOT / "corpus"
REVEAL = CORPUS / "reveal"
OUT = ROOT / "out"
GEN = ROOT / "target/release/gen"
BLITZ = ROOT / "target/release/blitz-runner"
SERVOSHELL = Path(os.environ.get("SERVOSHELL", Path.home() / "repos/servo/target/release/servoshell"))
WIDTH, HEIGHT = 1280, 800
ENGINES = ["taffy", "blitz", "blitz-par", "servo1", "servo", "chrome"]

REVEAL_SCRIPT = ("<script>var cb=document.getElementById('cb');cb.style.display='block';"
                 "cb.offsetHeight;</script>\n")


def sh(cmd, cpus=None, **kw):
    if cpus:
        cmd = ["taskset", "-c", cpus] + cmd
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw).stdout


def read_manifest():
    cases = []
    for line in (CORPUS / "manifest.tsv").read_text().splitlines():
        name, file, w, h, nodes = line.split("\t")
        cases.append(dict(name=name, file=file, cb_w=float(w), cb_h=float(h), nodes=int(nodes)))
    return cases


def cmd_gen(args):
    if CORPUS.exists():
        shutil.rmtree(CORPUS)
    sh([str(GEN), "html", str(CORPUS)])
    REVEAL.mkdir()
    for c in read_manifest():
        html = (CORPUS / c["file"]).read_text()
        html = html.replace('<div id="cb">', '<div id="cb" style="display:none">')
        html = html.replace("</body>", REVEAL_SCRIPT + "</body>")
        (REVEAL / c["file"]).write_text(html)
    print(f"wrote {len(read_manifest())} pages to {CORPUS}")


# ---- engines: each returns a list of per-iteration dicts of metric -> ns ----

def run_taffy(case, iters, cpus):
    out = sh([str(GEN), "bench", case["name"], "--iters", str(iters)], cpus)
    samples = []
    for line in out.splitlines():
        eng, name, ns = line.split("\t")
        if name == case["name"]:
            samples.append({"layout": int(ns)})
    return samples


def run_blitz(case, iters, cpus, parallel=False, screenshot=None):
    cmd = [str(BLITZ), str(CORPUS / case["file"]), "--width", str(WIDTH), "--height", str(HEIGHT), "--iters", str(iters), "--hash"]
    if parallel:
        cmd.append("--parallel")
    if screenshot:
        cmd += ["--screenshot", str(screenshot)]
    out = sh(cmd, cpus)
    samples, phases = [], None
    for line in out.splitlines():
        if line.startswith("PHASES"):
            phases = {k: int(v) for k, v in re.findall(r"(\w+)=(\d+)", line.split("|", 1)[1])}
        elif line.startswith("BLITZ"):
            kv = {k: int(v) for k, v in re.findall(r"(\w+)=(\d+)", line)}
            s = dict(style=phases["style"], construct=phases["construct"], layout=phases["layout"],
                     paint_tree=phases["paint_tree"], resolve=kv["resolve"], parse=kv["parse"])
            s["construct+layout"] = s["construct"] + s["layout"]
            samples.append(s)
        elif line.startswith("HASH"):
            samples[-1]["hash"] = line.split()[1]
        elif line.startswith("ROOT"):
            samples[-1]["root"] = line.split()[1]
    return samples


def parse_servo_trace(path):
    from perfetto.trace_processor import TraceProcessor
    tp = TraceProcessor(trace=str(path))
    rows = list(tp.query("select id, parent_id, name, dur, ts from slice"))
    tp.close()
    by_id = {r.id: r for r in rows}
    restyles = [r for r in rows if r.name == "restyle_and_build_trees"]
    if not restyles:
        raise RuntimeError(f"no restyle_and_build_trees span in {path}")
    main = max(restyles, key=lambda r: r.dur)
    reflow = by_id[main.parent_id]

    children = {}
    for r in rows:
        children.setdefault(r.parent_id, []).append(r)

    def descendants(root_id):
        out, stack = [], [root_id]
        while stack:
            for r in children.get(stack.pop(), []):
                out.append(r)
                stack.append(r.id)
        return out

    def total(root_id, name):
        return sum(r.dur for r in descendants(root_id) if r.name == name)

    s = dict(style=total(main.id, "Styling"), box=total(main.id, "Box Tree Construction"),
             fragment=total(main.id, "Fragment Tree Construction"), restyle_and_build=main.dur,
             stacking_context=total(reflow.id, "Stacking Context Tree Construction"),
             display_list=total(reflow.id, "Display List Construction"), reflow=reflow.dur,
             n_reflows=len(restyles))
    s["box+fragment"] = s["box"] + s["fragment"]
    return s


def run_servo(case, iters, cpus, threads, screenshot=None):
    samples = []
    url = (REVEAL / case["file"]).resolve().as_uri()
    env = dict(os.environ, SERVO_TRACING="layout=trace,script=trace")
    for i in range(iters):
        with tempfile.TemporaryDirectory() as d:
            cmd = [str(SERVOSHELL), "-z", "-x", f"--window-size={WIDTH}x{HEIGHT}", "--pref", f"layout_threads={threads}"]
            if screenshot and i == iters - 1:
                cmd += ["-o", str(screenshot)]
            cmd.append(url)
            subprocess.run((["taskset", "-c", cpus] if cpus else []) + cmd, check=True, cwd=d, env=env,
                           capture_output=True, text=True, timeout=600)
            samples.append(parse_servo_trace(Path(d) / "servo.pftrace"))
    return samples


def run_chrome(case, iters, cpus, screenshot=None):
    from playwright.sync_api import sync_playwright
    url = (REVEAL / case["file"]).resolve().as_uri()
    samples = []
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        for i in range(iters):
            page = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT})
            cdp = page.context.new_cdp_session(page)
            events, done = [], []
            cdp.on("Tracing.dataCollected", lambda e: events.extend(e["value"]))
            cdp.on("Tracing.tracingComplete", lambda e: done.append(True))
            cdp.send("Tracing.start", {"traceConfig": {"includedCategories": ["devtools.timeline", "disabled-by-default-devtools.timeline"]}})
            page.goto(url, wait_until="load", timeout=600_000)
            page.evaluate("document.body.offsetHeight")
            root = page.evaluate("(()=>{const r=document.getElementById('cb').firstElementChild.getBoundingClientRect();return r.width.toFixed(1)+'x'+r.height.toFixed(1)})()")
            cdp.send("Tracing.end")
            while not done:
                page.wait_for_timeout(50)
            layouts = [e for e in events if e.get("name") == "Layout" and e.get("ph") == "X"]
            styles = [e for e in events if e.get("name") == "UpdateLayoutTree" and e.get("ph") == "X"]
            main = max(layouts, key=lambda e: e["dur"])
            s = dict(layout=main["dur"] * 1000, style=max(e["dur"] for e in styles) * 1000,
                     n_layouts=len(layouts), root=root, total_objects=main.get("args", {}).get("beginData", {}).get("totalObjects"))
            s["style+layout"] = s["style"] + s["layout"]
            if screenshot and i == iters - 1:
                page.screenshot(path=str(screenshot))
            samples.append(s)
            page.close()
        browser.close()
    return samples


def run_engine(engine, case, iters, cpus, screenshot=None):
    if engine == "taffy":
        return run_taffy(case, iters, cpus)
    if engine == "blitz":
        return run_blitz(case, iters, cpus, screenshot=screenshot)
    if engine == "blitz-par":
        return run_blitz(case, iters, None, parallel=True, screenshot=screenshot)
    if engine == "servo1":
        return run_servo(case, iters, cpus, 1, screenshot=screenshot)
    if engine == "servo":
        return run_servo(case, iters, None, 3, screenshot=screenshot)
    if engine == "chrome":
        return run_chrome(case, iters, None, screenshot=screenshot)
    raise ValueError(engine)


# ---- bench / report ----

def agg(values, how):
    values = [v for v in values if v is not None]
    if not values:
        return None
    return min(values) if how == "min" else statistics.median(values)


def fmt_ms(ns):
    return "-" if ns is None else f"{ns / 1e6:.3f}"


COLUMNS = [
    ("Layout only", [("taffy", "layout", "Taffy"), ("blitz", "layout", "Blitz `layout`"),
                     ("servo1", "fragment", "Servo(1) Fragment Tree"), ("servo", "fragment", "Servo(3) Fragment Tree"),
                     ("chrome", "layout", "Chrome Layout")]),
    ("Box construction + layout", [("blitz", "construct+layout", "Blitz construct+layout"),
                                   ("servo1", "box+fragment", "Servo(1) Box+Fragment"), ("servo", "box+fragment", "Servo(3) Box+Fragment"),
                                   ("chrome", "layout", "Chrome Layout")]),
    ("Style", [("blitz", "style", "Blitz style"), ("blitz-par", "style", "Blitz style (parallel)"),
               ("servo1", "style", "Servo(1) Styling"), ("servo", "style", "Servo(3) Styling"),
               ("chrome", "style", "Chrome UpdateLayoutTree")]),
    ("Whole pipeline (style to paint tree / display list)", [
        ("blitz", "resolve", "Blitz resolve()"), ("servo1", "reflow", "Servo(1) handle_reflow"),
        ("servo", "reflow", "Servo(3) handle_reflow"), ("chrome", "style+layout", "Chrome Style+Layout")]),
]


def report(results, how, engines):
    lines = [f"Times in ms, {how} over all rounds and iterations. Servo(n) = `layout_threads=n`.", ""]
    for title, cols in COLUMNS:
        cols = [c for c in cols if c[0] in engines]
        if not cols:
            continue
        lines += [f"### {title}", "", "| case | nodes | " + " | ".join(c[2] for c in cols) + " |",
                  "|---|---:|" + "---:|" * len(cols)]
        for name, data in results.items():
            cells = [fmt_ms(agg([s.get(m) for s in data["engines"].get(e, [])], how)) for e, m, _ in cols]
            lines.append(f"| {name} | {data['nodes']} | " + " | ".join(cells) + " |")
        lines.append("")
    return "\n".join(lines)


def cmd_bench(args):
    cases = [c for c in read_manifest() if args.filter in c["name"]]
    engines = args.engines.split(",")
    results = {c["name"]: dict(nodes=c["nodes"], engines={e: [] for e in engines}) for c in cases}
    OUT.mkdir(exist_ok=True)
    for r in range(args.rounds):
        order = engines if r % 2 == 0 else engines[::-1]
        for c in cases:
            for e in order:
                try:
                    samples = run_engine(e, c, args.iters, args.cpus)
                except Exception as ex:
                    print(f"round {r} {c['name']} {e}: FAILED {ex}", file=sys.stderr)
                    continue
                results[c["name"]]["engines"][e] += samples
                best = agg([list(s.values())[0] for s in samples], "min")
                print(f"round {r} {c['name']:24s} {e:10s} {len(samples)} samples, min first metric {fmt_ms(best)} ms", flush=True)
        (OUT / "results.json").write_text(json.dumps(results, indent=1))
    md = report(results, args.agg, engines)
    (OUT / "report.md").write_text(md)
    print(md)


def cmd_verify(args):
    from PIL import Image, ImageChops
    cases = [c for c in read_manifest() if args.filter in c["name"]]
    engines = args.engines.split(",")
    shots = OUT / "shots"
    shots.mkdir(parents=True, exist_ok=True)
    print("| case | nodes | " + " | ".join(f"{e} vs {engines[0]}" for e in engines[1:]) + " | notes |")
    for c in cases:
        imgs, notes = {}, []
        for e in engines:
            path = shots / f"{c['file'][:-5]}.{e}.png"
            try:
                samples = run_engine(e, c, 1, args.cpus, screenshot=path)
            except Exception as ex:
                notes.append(f"{e} failed: {ex}")
                continue
            imgs[e] = Image.open(path).convert("RGB")
            s = samples[-1]
            if "total_objects" in s:
                notes.append(f"chrome objects={s['total_objects']} layouts={s['n_layouts']}")
            if "n_reflows" in s:
                notes.append(f"{e} reflows={s['n_reflows']}")
            if "hash" in s:
                notes.append(f"{e} hash={s['hash'][:8]}")
            if "root" in s:
                notes.append(f"{e} root={s['root']}")
        cells = []
        for e in engines[1:]:
            if e in imgs and engines[0] in imgs:
                diff = ImageChops.difference(imgs[e], imgs[engines[0]]).convert("L").point(lambda v: 255 if v > 24 else 0)
                frac = diff.histogram()[255] / (diff.width * diff.height)
                cells.append(f"{frac * 100:.2f}% px")
            else:
                cells.append("-")
        print(f"| {c['name']} | {c['nodes']} | " + " | ".join(cells) + " | " + "; ".join(notes) + " |", flush=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("gen")
    b = sub.add_parser("bench")
    b.add_argument("--engines", default=",".join(ENGINES))
    b.add_argument("--rounds", type=int, default=3)
    b.add_argument("--iters", type=int, default=3)
    b.add_argument("--filter", default="")
    b.add_argument("--cpus", default=None, help="taskset CPU list for the single-threaded runners (taffy, blitz, servo1)")
    b.add_argument("--agg", default="min", choices=["min", "median"])
    v = sub.add_parser("verify")
    v.add_argument("--engines", default="chrome,blitz,servo1")
    v.add_argument("--filter", default="")
    v.add_argument("--cpus", default=None)
    args = ap.parse_args()
    {"gen": cmd_gen, "bench": cmd_bench, "verify": cmd_verify}[args.cmd](args)


if __name__ == "__main__":
    main()
