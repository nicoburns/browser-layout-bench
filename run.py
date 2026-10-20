#!/usr/bin/env python3
"""Driver: generates the corpus, runs each engine on every page in interleaved rounds, and
writes results.json + a Markdown report. See README.md for the measurement model."""
import argparse, functools, http.server, json, os, re, shlex, shutil, statistics, subprocess, sys, tempfile, threading
from pathlib import Path

import engines_ladybird

ROOT = Path(__file__).resolve().parent
CORPUS = ROOT / "corpus"
REVEAL = CORPUS / "reveal"
REAL = ROOT / "real"
OUT = ROOT / "out"
GEN = ROOT / "target/release/gen"
BLITZ = ROOT / "target/release/blitz-runner"
# `cargo build --release -p layout-bench-blitz --features parallel-construct --target-dir target-pcon`
BLITZ_PCON = ROOT / "target-pcon/release/blitz-runner"
# `cargo build --release --manifest-path blitz-runner-pl/Cargo.toml --target-dir target-pl` (see blitz-runner-pl/Cargo.toml)
BLITZ_PL = ROOT / "target-pl/release/blitz-runner"
SERVOSHELL = Path(os.environ.get("SERVOSHELL", Path.home() / "repos/servo/target/release/servoshell"))
WIDTH, HEIGHT = 1280, 800
ENGINES = ["taffy", "blitz", "blitz-par", "blitz-pcon", "blitz-par-pcon", "blitz-pcon-pl1", "blitz-pcon-pl", "blitz-par-pcon-pl",
           "servo1", "servo", "chrome", "firefox1", "firefox", "ladybird"]

REVEAL_SCRIPT = ("<script>var cb=document.getElementById('cb');cb.style.display='block';"
                 "cb.offsetHeight;</script>\n")
# Pages with web fonts reveal the tree only once every @font-face has loaded, so the single timed
# layout shapes with the right font instead of a fallback (followed by a second layout). Chrome loads
# fonts lazily, so they are requested explicitly; Servo loads them eagerly and lacks
# FontFaceSet.load(), so there `document.fonts.ready` is awaited instead.
FONT_REVEAL_SCRIPT = ("<script>var F=document.fonts;(F.load?Promise.all([...F].map(f=>f.load())):F.ready).then(()=>{"
                      "var cb=document.getElementById('cb');cb.style.display='block';cb.offsetHeight;});</script>\n")
# Size of the tree's root: the first child of `#cb`, or the document's scrollable size when `#cb` is
# the `<body>` (real pages; their body is often `height: 100%`)
ROOT_RECT_JS = ("(()=>{const cb=document.getElementById('cb');const d=document.documentElement;"
                "if(cb===document.body)return d.getBoundingClientRect().width.toFixed(1)+'x'+d.scrollHeight.toFixed(1);"
                "const r=cb.firstElementChild.getBoundingClientRect();return r.width.toFixed(1)+'x'+r.height.toFixed(1)})()")
# Gecko profiler: started at launch, no stack sampling or marker stacks, main threads only; the
# parent writes the profile (with the content processes' exit profiles) to MOZ_PROFILER_SHUTDOWN.
FIREFOX_PROFILER_ENV = dict(MOZ_PROFILER_STARTUP="1", MOZ_PROFILER_STARTUP_FEATURES="nostacksampling,nomarkerstacks",
                            MOZ_PROFILER_STARTUP_FILTERS="GeckoMain")


def sh(cmd, cpus=None, **kw):
    if cpus:
        cmd = ["taskset", "-c", cpus] + cmd
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw).stdout


def read_manifest():
    cases = []
    for line in (CORPUS / "manifest.tsv").read_text().splitlines():
        name, file, w, h, nodes, engine, *rest = line.split("\t")
        # optional 7th column: viewport `WxH` (the real pages have 1024px variants)
        vw, vh = (int(v) for v in rest[0].split("x")) if rest else (WIDTH, HEIGHT)
        cases.append(dict(name=name, file=file, cb_w=float(w), cb_h=float(h), nodes=int(nodes), taffy=engine == "taffy",
                          width=vw, height=vh))
    return cases


def cmd_gen(args):
    if CORPUS.exists():
        shutil.rmtree(CORPUS)
    sh([str(GEN), "html", str(CORPUS)])
    gen_real()
    REVEAL.mkdir(exist_ok=True)
    for c in read_manifest():
        html = (CORPUS / c["file"]).read_text()
        html = html.replace('<div id="cb">', '<div id="cb" style="display:none">')
        body_tag = re.search(r"<body[^>]*>", html).group()
        if 'id="cb"' in body_tag:
            html = html.replace(body_tag, body_tag[:-1] + ' style="display:none">')
        script = FONT_REVEAL_SCRIPT if "@font-face" in html else REVEAL_SCRIPT
        if 'id="cb"' in body_tag:
            # the real pages hide the `<body>` itself; revealing must restore its stylesheet display
            script = script.replace("cb.style.display='block'", "cb.style.display=''")
        html = html.replace("</body>", script + "</body>")
        html = html.replace("url(fonts/", "url(../fonts/")
        html = html.replace("url(../../fonts/", "url(../../../fonts/")  # real pages, one level deeper
        (REVEAL / c["file"]).write_text(html)
    print(f"wrote {len(read_manifest())} pages to {CORPUS}")


def gen_real():
    """Copies the frozen pages from real/ (see real/freeze.py) into corpus/real/ and corpus/reveal/real/
    (the reveal copy needs the page's placeholder images next to it) and appends one manifest line
    per page and viewport: `real/<page>` at 1280x800 and `real/<page>@1024` at 1024x800."""
    for font in (ROOT / "fonts").glob("DejaVuSansMono*.ttf"):
        shutil.copy(font, CORPUS / "fonts" / font.name)
    with (CORPUS / "manifest.tsv").open("a") as manifest:
        for line in (REAL / "manifest.tsv").read_text().splitlines():
            name, d, nodes, viewports = line.split("\t")
            for target in (CORPUS / "real" / d, REVEAL / "real" / d):
                shutil.copytree(REAL / d, target)
            for vp in viewports.split(","):
                w, h = (int(v) for v in vp.split("x"))
                suffix = "" if (w, h) == (WIDTH, HEIGHT) else f"@{w}"
                manifest.write(f"real/{name}{suffix}\treal/{d}/index.html\t{w}\t0\t{nodes}\t-\t{vp}\n")


# ---- engines: each returns a list of per-iteration dicts of metric -> ns ----

def run_taffy(case, iters, cpus):
    out = sh([str(GEN), "bench", case["name"], "--iters", str(iters)], cpus)
    samples = []
    for line in out.splitlines():
        eng, name, ns = line.split("\t")
        if name == case["name"]:
            samples.append({"layout": int(ns)})
    return samples


def run_blitz(case, iters, cpus, parallel=False, screenshot=None, binary=BLITZ, env=None):
    if not binary.exists():
        raise FileNotFoundError(f"{binary.relative_to(ROOT)} not built, see README")
    cmd = [str(binary), str(CORPUS / case["file"]), "--width", str(case["width"]), "--height", str(case["height"]), "--iters", str(iters), "--hash"]
    if parallel:
        cmd.append("--parallel")
    if screenshot:
        cmd += ["--screenshot", str(screenshot), "--boxes"]
    out = sh(cmd, cpus, env=dict(os.environ, **env) if env else None)
    samples, phases = [], None
    for line in out.splitlines():
        if line.startswith("PHASES"):
            phases = {k: int(v) for k, v in re.findall(r"(\w+)=(\d+)", line.split("|", 1)[1])}
        elif line.startswith("BLITZ"):
            kv = {k: int(v) for k, v in re.findall(r"(\w+)=(\d+)", line)}
            # pconstruct = the deferred tasks that run between box construction and layout, where
            # Blitz builds the Parley layouts, i.e. shapes the text; it belongs with construction
            s = dict(style=phases["style"], construct=phases["construct"] + phases["pconstruct"], layout=phases["layout"],
                     paint_tree=phases["paint_tree"], resolve=kv["resolve"], parse=kv["parse"])
            s["construct+layout"] = s["construct"] + s["layout"]
            samples.append(s)
        elif line.startswith("HASH"):
            samples[-1]["hash"] = line.split()[1]
        elif line.startswith("ROOT"):
            samples[-1]["root"] = line.split()[1]
        elif line.startswith("BOX"):
            samples[-1].setdefault("boxes", []).append(tuple(float(v) for v in line.split()[1:]))
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

    # The reflow that laid the page out, i.e. the one after the reveal: the longest span is not
    # always it, as the first (`display:none`) reflow's `prepare_stylist_for_reflow` can outlast the
    # whole layout of a small page.
    main = max(restyles, key=lambda r: total(r.id, "Box Tree Construction") + total(r.id, "Fragment Tree Construction"))
    reflow = by_id[main.parent_id]

    s = dict(style=total(main.id, "Styling"), box=total(main.id, "Box Tree Construction"),
             fragment=total(main.id, "Fragment Tree Construction"), restyle_and_build=main.dur,
             stacking_context=total(reflow.id, "Stacking Context Tree Construction"),
             display_list=total(reflow.id, "Display List Construction"), reflow=reflow.dur,
             n_reflows=len(restyles))
    s["box+fragment"] = s["box"] + s["fragment"]
    return s


@functools.cache
def corpus_server():
    """Servo's fetch rejects `file://` fonts (CORS mode, opaque origin), so it gets the corpus over
    localhost HTTP instead. Returns the base URL."""
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Handler, directory=str(CORPUS)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{server.server_address[1]}"


def run_servo(case, iters, cpus, threads, screenshot=None):
    samples = []
    url = f"{corpus_server()}/reveal/{case['file']}"
    env = dict(os.environ, SERVO_TRACING="layout::layout_impl=trace,layout::flow::root=trace")
    for i in range(iters):
        with tempfile.TemporaryDirectory() as d:
            cmd = [str(SERVOSHELL), "-z", "-x", f"--window-size={case['width']}x{case['height']}", "--pref", f"layout_threads={threads}"]
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
            page = browser.new_page(viewport={"width": case["width"], "height": case["height"]})
            cdp = page.context.new_cdp_session(page)
            events, done = [], []
            cdp.on("Tracing.dataCollected", lambda e: events.extend(e["value"]))
            cdp.on("Tracing.tracingComplete", lambda e: done.append(True))
            cdp.send("Tracing.start", {"traceConfig": {"includedCategories": ["devtools.timeline", "disabled-by-default-devtools.timeline", "blink", "blink_style"]}})
            page.goto(url, wait_until="load", timeout=600_000)
            page.wait_for_function("document.getElementById('cb').style.display !== 'none'", timeout=600_000)
            page.evaluate("document.body.offsetHeight")
            root = page.evaluate(ROOT_RECT_JS)
            cdp.send("Tracing.end")
            while not done:
                page.wait_for_timeout(50)
            def longest(name):
                return max(e["dur"] for e in events if e.get("name") == name and e.get("ph") == "X") * 1000
            layouts = [e for e in events if e.get("name") == "Layout" and e.get("ph") == "X"]
            main = max(layouts, key=lambda e: e["dur"])
            # `UpdateLayoutTree` = `Document::recalcStyle` (style) + `Document::rebuildLayoutTree`
            # (LayoutObject construction); `Layout` is fragment-tree work only.
            s = dict(layout=main["dur"] * 1000, style=longest("Document::recalcStyle"),
                     construct=longest("Document::rebuildLayoutTree"), update_layout_tree=longest("UpdateLayoutTree"),
                     n_layouts=len(layouts), root=root, total_objects=main.get("args", {}).get("beginData", {}).get("totalObjects"))
            s["construct+layout"] = s["construct"] + s["layout"]
            s["style+layout"] = s["update_layout_tree"] + s["layout"]
            if screenshot and i == iters - 1:
                page.screenshot(path=str(screenshot))
                s["boxes"] = [tuple(b) for b in page.evaluate(
                    "[...document.querySelectorAll('#cb div, #cb p, #cb h3')].map(e=>{const r=e.getBoundingClientRect();return [r.x,r.y,r.width,r.height]})")]
                s["fonts"] = page.evaluate("[...document.fonts].map(f=>f.status).join(',')")
            samples.append(s)
            page.close()
        browser.close()
    return samples


def firefox_installed():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        return Path(p.firefox.executable_path).exists()


def parse_firefox_profile(path, url):
    """Marker intervals of the content process that loaded `url`: Styles (style traversal and frame
    construction), Reflow (layout), DoFlushPendingNotifications (the flush containing both) and
    DisplayList. Times are ms floats; returned in ns like the other engines."""
    profile = json.loads(path.read_text())
    for proc in profile.get("processes", []):
        window_ids = {pg["innerWindowID"] for pg in proc.get("pages", []) if pg["url"] == url}
        if window_ids:
            break
    else:
        raise RuntimeError(f"no content process for {url} in {path}")
    thread = next(t for t in proc["threads"] if t["name"] == "GeckoMain")
    strings = thread["stringTable"]
    schema = thread["markers"]["schema"]
    intervals, open_starts = {}, {}
    for row in thread["markers"]["data"]:
        name, start, end, phase = (row[schema[k]] for k in ("name", "startTime", "endTime", "phase"))
        name = strings[name]
        data = row[schema["data"]] if len(row) > schema["data"] else None
        if name.startswith("Reflow"):
            name = "Reflow"
        if data and "innerWindowID" in data and data["innerWindowID"] not in window_ids:
            continue
        if phase == 1:
            intervals.setdefault(name, []).append((end - start, data))
        elif phase == 2:
            open_starts.setdefault(name, []).append(start)
        elif phase == 3 and open_starts.get(name):
            intervals.setdefault(name, []).append((end - open_starts[name].pop(), data))

    def longest(name):
        return max(intervals.get(name, []), key=lambda i: i[0], default=(None, None))

    reflows = [d for d, _ in intervals.get("Reflow", [])]
    style, style_data = longest("Styles")
    ms = lambda v: None if v is None else int(v * 1e6)
    s = dict(layout=ms(longest("Reflow")[0]), style=ms(style), flush=ms(longest("DoFlushPendingNotifications")[0]),
             display_list=ms(longest("DisplayList")[0]), layout_sum=ms(sum(reflows)), n_reflows=len(reflows),
             styled=style_data["elementsTraversed"] if style_data else None)
    s["style+layout"] = s["style"] + s["layout"]
    return s


def pin_content_processes(parent_pid, cpus):
    """Pin Firefox's tab content processes (descendants of the parent whose command line ends in
    `tab`) with taskset. Pinning the whole browser would put the parent process and compositor
    on the same CPUs as the page's main thread, which inflated its reflow 3x on a single CPU."""
    children = {}
    for stat in Path("/proc").glob("[0-9]*/stat"):
        try:
            ppid = int(stat.read_text().rsplit(")", 1)[1].split()[1])
            children.setdefault(ppid, []).append(int(stat.parent.name))
        except (OSError, ValueError):
            continue
    pinned, stack = [], [parent_pid]
    while stack:
        for pid in children.get(stack.pop(), []):
            stack.append(pid)
            try:
                cmdline = Path(f"/proc/{pid}/cmdline").read_bytes()
            except OSError:  # exited between the /proc scan and now
                continue
            if cmdline.replace(b"\0", b" ").split()[-1:] == [b"tab"]:
                subprocess.run(["taskset", "-a", "-p", "-c", cpus, str(pid)], check=True, capture_output=True)
                pinned.append(pid)
    if not pinned:
        raise RuntimeError("no Firefox content process found to pin")
    return pinned


def launch_firefox(p, exe, env, prefs, attempts=3):
    """Headless Firefox segfaults at launch now and then (5 of 306 launches in a bench run, none in
    80 back-to-back launches with or without the profiler); retry rather than lose the whole case."""
    from playwright.sync_api import Error
    for attempt in range(attempts):
        try:
            return p.firefox.launch(executable_path=exe, env=env, firefox_user_prefs=prefs)
        except Error as ex:
            if attempt == attempts - 1 or "Failed to launch" not in str(ex):
                raise
            print(f"firefox: launch failed (attempt {attempt + 1}), retrying", file=sys.stderr)


def run_firefox(case, iters, cpus, stylo_threads=None, screenshot=None):
    from playwright.sync_api import sync_playwright
    url = (REVEAL / case["file"]).resolve().as_uri()
    prefs = {} if stylo_threads is None else {"layout.css.stylo-threads": stylo_threads}
    samples = []
    with sync_playwright() as p, tempfile.TemporaryDirectory() as d:
        exe = p.firefox.executable_path
        pidfile, blank = Path(d) / "firefox.pid", Path(d) / "blank.html"
        if cpus:
            # exec keeps the wrapper's pid, so the pidfile names the parent Firefox process
            wrapper = Path(d) / "firefox-with-pid"
            wrapper.write_text(f"#!/bin/sh\necho $$ > {shlex.quote(str(pidfile))}\nexec {shlex.quote(exe)} \"$@\"\n")
            wrapper.chmod(0o755)
            exe = str(wrapper)
            blank.write_text("<!doctype html>\n")
        for i in range(iters):
            profile = Path(d) / f"profile-{i}.json"
            env = dict(os.environ, **FIREFOX_PROFILER_ENV, MOZ_PROFILER_SHUTDOWN=str(profile))
            browser = launch_firefox(p, exe, env, prefs)
            page = browser.new_page(viewport={"width": case["width"], "height": case["height"]})
            if cpus:
                # a first file:// page puts the tab in its file content process; pin that, then load the case
                page.goto(blank.as_uri(), wait_until="load")
                pin_content_processes(int(pidfile.read_text()), cpus)
            page.goto(url, wait_until="load", timeout=600_000)
            page.wait_for_function("document.getElementById('cb').style.display !== 'none'", timeout=600_000)
            page.evaluate("document.body.offsetHeight")
            root = page.evaluate(ROOT_RECT_JS)
            if screenshot and i == iters - 1:
                page.screenshot(path=str(screenshot))
            browser.close()
            s = parse_firefox_profile(profile, url)
            s["root"] = root
            samples.append(s)
    return samples


def run_engine(engine, case, iters, cpus, screenshot=None):
    if engine == "taffy":
        return run_taffy(case, iters, cpus)
    if engine == "blitz":
        return run_blitz(case, iters, cpus, screenshot=screenshot)
    if engine == "blitz-par":
        return run_blitz(case, iters, None, parallel=True, screenshot=screenshot)
    if engine == "blitz-pcon":
        return run_blitz(case, iters, None, screenshot=screenshot, binary=BLITZ_PCON)
    if engine == "blitz-par-pcon":
        return run_blitz(case, iters, None, parallel=True, screenshot=screenshot, binary=BLITZ_PCON)
    # the parallel-layout prototype build (blitz#1034): `pl1` runs its layout batches on a dedicated
    # 1-thread pool, i.e. the feature's bookkeeping without the parallelism, pinned like `blitz`
    if engine == "blitz-pcon-pl1":
        return run_blitz(case, iters, cpus, screenshot=screenshot, binary=BLITZ_PL, env={"BLITZ_PARALLEL_LAYOUT_THREADS": "1"})
    if engine == "blitz-pcon-pl":
        return run_blitz(case, iters, None, screenshot=screenshot, binary=BLITZ_PL)
    if engine == "blitz-par-pcon-pl":
        return run_blitz(case, iters, None, parallel=True, screenshot=screenshot, binary=BLITZ_PL)
    if engine == "servo1":
        return run_servo(case, iters, cpus, 1, screenshot=screenshot)
    if engine == "servo":
        return run_servo(case, iters, None, 3, screenshot=screenshot)
    if engine == "chrome":
        return run_chrome(case, iters, None, screenshot=screenshot)
    if engine == "firefox1":
        return run_firefox(case, iters, cpus, stylo_threads=1, screenshot=screenshot)
    if engine == "firefox":
        return run_firefox(case, iters, None, screenshot=screenshot)
    if engine == "ladybird":
        return engines_ladybird.run_ladybird(case, iters, None, REVEAL, case["width"], case["height"], screenshot=screenshot)
    raise ValueError(engine)


def available_engines(engines):
    if any(e.startswith("firefox") for e in engines) and not firefox_installed():
        print("firefox: Playwright's Firefox is not installed (python -m playwright install firefox); skipping",
              file=sys.stderr)
        engines = [e for e in engines if not e.startswith("firefox")]
    if "ladybird" in engines and not engines_ladybird.available():
        print(engines_ladybird.skip_message(), file=sys.stderr)
        engines = [e for e in engines if e != "ladybird"]
    return engines


# ---- bench / report ----

def agg(values, how):
    values = [v for v in values if v is not None]
    if not values:
        return None
    return min(values) if how == "min" else statistics.median(values)


def fmt_ms(ns):
    return "-" if ns is None else f"{ns / 1e6:.3f}"


# Column order within every table: Chrome, Firefox, Servo, Blitz, Taffy; the Chrome column is the
# reference for the multipliers.
COLUMNS = [
    ("Layout only", [("chrome", "layout", "Chrome Layout"), ("firefox1", "layout", "Firefox(1) Reflow"),
                     ("firefox", "layout", "Firefox Reflow"), ("ladybird", "layout", "Ladybird layout"),
                     ("servo1", "fragment", "Servo(1) Fragment Tree"), ("servo", "fragment", "Servo(3) Fragment Tree"),
                     ("blitz", "layout", "Blitz `layout`"), ("blitz-pcon-pl1", "layout", "Blitz `layout` (#1034 build, 1 thread)"),
                     ("blitz-pcon-pl", "layout", "Blitz `layout` (parallel layout)"), ("taffy", "layout", "Taffy")]),
    ("Box construction + layout", [("chrome", "construct+layout", "Chrome rebuildLayoutTree+Layout"),
                                   ("ladybird", "construct+layout", "Ladybird tree build+layout"),
                                   ("servo1", "box+fragment", "Servo(1) Box+Fragment"), ("servo", "box+fragment", "Servo(3) Box+Fragment"),
                                   ("blitz", "construct+layout", "Blitz construct+layout"),
                                   ("blitz-pcon", "construct+layout", "Blitz construct+layout (parallel construct)"),
                                   ("blitz-pcon-pl", "construct+layout", "Blitz construct+layout (parallel construct+layout)")]),
    ("Construction", [("chrome", "construct", "Chrome rebuildLayoutTree"), ("ladybird", "construct", "Ladybird tree build"),
                      ("servo1", "box", "Servo(1) Box Tree"), ("servo", "box", "Servo(3) Box Tree"),
                      ("blitz", "construct", "Blitz construct (+pconstruct)"), ("blitz-pcon", "construct", "Blitz construct, parallel")]),
    ("Style", [("chrome", "style", "Chrome recalcStyle"),
               ("firefox1", "style", "Firefox(1) Styles (incl. frame construction)"),
               ("firefox", "style", "Firefox Styles (incl. frame construction)"), ("ladybird", "style", "Ladybird update_style"),
               ("servo1", "style", "Servo(1) Styling"), ("servo", "style", "Servo(3) Styling"),
               ("blitz", "style", "Blitz style"), ("blitz-par", "style", "Blitz style (parallel)")]),
    ("Whole pipeline (style to paint tree / display list)", [
        ("chrome", "style+layout", "Chrome UpdateLayoutTree+Layout"),
        ("firefox1", "style+layout", "Firefox(1) Styles+Reflow"), ("firefox", "style+layout", "Firefox Styles+Reflow"),
        ("ladybird", "total", "Ladybird update_layout()"),
        ("servo1", "reflow", "Servo(1) handle_reflow"), ("servo", "reflow", "Servo(3) handle_reflow"),
        ("blitz", "resolve", "Blitz resolve()"), ("blitz-par", "resolve", "Blitz resolve() (parallel style)"),
        ("blitz-par-pcon", "resolve", "Blitz resolve() (parallel style+construct)"),
        ("blitz-par-pcon-pl", "resolve", "Blitz resolve() (parallel style+construct+layout)")]),
]


def fmt_cell(ns, ref, best=False):
    """`ms` and, on a second line, the multiple of the Chrome value of the same row (omitted when Chrome has
    none); the fastest engine of the row (Taffy excluded, it is not a browser) is bold."""
    if ns is None:
        return "-"
    cell = f"{ns / 1e6:.3f}"
    if ref:
        cell += f"<br>{ns / ref:.2f}x"
    return f"**{cell}**" if best else cell


def header(label):
    """Column header that can wrap: engine name on its own line, spaces around `+`."""
    engine, _, phase = label.partition(" ")
    return f"{engine}<br>{phase.replace('+', ' + ')}" if phase else engine


def report(results, how, engines):
    lines = [f"Times in ms, {how} over all rounds and iterations; second line of each cell is the multiple of the Chrome column "
             "of the same table (1.00x = Chrome); bold = fastest engine of the row, Taffy excluded. Servo(n) = `layout_threads=n`; "
             "Firefox(1) = `layout.css.stylo-threads=1` (no style worker threads).", ""]
    for title, cols in COLUMNS:
        cols = [c for c in cols if c[0] in engines]
        if not cols:
            continue
        lines += [f"### {title}", "", "| case | nodes | " + " | ".join(header(c[2]) for c in cols) + " |",
                  "|---|---:|" + "---:|" * len(cols)]
        ref_col = next((c for c in cols if c[0] == "chrome"), None)
        for name, data in results.items():
            values = [agg([s.get(m) for s in data["engines"].get(e, [])], how) for e, m, _ in cols]
            ref = values[cols.index(ref_col)] if ref_col else None
            contenders = [v for (e, _, _), v in zip(cols, values) if v is not None and e != "taffy"]
            best = min(contenders) if contenders else None
            lines.append(f"| {name} | {data['nodes']} | "
                         + " | ".join(fmt_cell(v, ref, v == best and e != "taffy") for (e, _, _), v in zip(cols, values)) + " |")
        lines.append("")
    return "\n".join(lines)


def cmd_report(args):
    """Rewrite out/report.md from out/results.json without re-measuring."""
    results = json.loads((OUT / "results.json").read_text())
    md = report(results, args.agg, sorted({e for d in results.values() for e in d["engines"]}))
    (OUT / "report.md").write_text(md)
    print(md)


def cmd_bench(args):
    cases = [c for c in read_manifest() if args.filter in c["name"]]
    engines = available_engines(args.engines.split(","))
    results = {c["name"]: dict(nodes=c["nodes"], engines={e: [] for e in engines}) for c in cases}
    OUT.mkdir(exist_ok=True)
    if args.merge:
        # Re-measure only `--engines`, keeping the other engines' samples from the previous run.
        for name, data in json.loads((OUT / "results.json").read_text()).items():
            kept = {e: v for e, v in data["engines"].items() if e not in engines or name not in results}
            results.setdefault(name, dict(nodes=data["nodes"], engines={}))["engines"].update(kept)
        order = [c["name"] for c in read_manifest()]
        results = dict(sorted(results.items(), key=lambda kv: order.index(kv[0]) if kv[0] in order else len(order)))
    for r in range(args.rounds):
        order = engines if r % 2 == 0 else engines[::-1]
        for c in cases:
            for e in order:
                if e == "taffy" and not c["taffy"]:
                    continue
                try:
                    samples = run_engine(e, c, args.iters, args.cpus)
                except Exception as ex:
                    print(f"round {r} {c['name']} {e}: FAILED {ex}", file=sys.stderr)
                    continue
                results[c["name"]]["engines"][e] += samples
                best = agg([list(s.values())[0] for s in samples], "min")
                print(f"round {r} {c['name']:24s} {e:10s} {len(samples)} samples, min first metric {fmt_ms(best)} ms", flush=True)
        (OUT / "results.json").write_text(json.dumps(results, indent=1))
    md = report(results, args.agg, sorted({e for d in results.values() for e in d["engines"]}))
    (OUT / "report.md").write_text(md)
    print(md)


def compare_boxes(a, b, tol=1.0):
    """Border boxes (x, y, w, h) of the same elements from two engines: how many have a size or a
    position differing by more than `tol` px, and the largest size difference. Blitz rounds layout to
    whole pixels, hence the tolerance; a size difference shifts the position of everything below it."""
    if len(a) != len(b):
        return f"{len(a)} vs {len(b)} boxes"
    size = [max(abs(ba[2] - bb[2]), abs(ba[3] - bb[3])) for ba, bb in zip(a, b)]
    pos = [max(abs(ba[0] - bb[0]), abs(ba[1] - bb[1])) for ba, bb in zip(a, b)]
    return (f"{sum(d > tol for d in size)}/{len(a)} box sizes differ >{tol:g}px (max {max(size, default=0):.1f}px), "
            f"{sum(d > tol for d in pos)} positions")


def bg_bands(img, x=1):
    """(colour, top, height) of the runs of non-white pixels down column `x` of the screenshot: on the
    text pages that column is inside the padding of the paragraphs/cards, so the bands are the leaf
    boxes' vertical extents, i.e. their line counts, independent of glyph anti-aliasing. Lets line
    breaking be compared with engines that give no box output (Servo)."""
    data = img.load()
    bands = []
    for y in range(img.height):
        px = data[x, y]
        if px == (255, 255, 255):
            continue
        if bands and bands[-1][0] == px and bands[-1][1] + bands[-1][2] == y:
            bands[-1][2] += 1
        else:
            bands.append([px, y, 1])
    return bands


def cmd_verify(args):
    from PIL import Image, ImageChops
    cases = [c for c in read_manifest() if args.filter in c["name"]]
    engines = available_engines(args.engines.split(","))
    shots = OUT / "shots"
    shots.mkdir(parents=True, exist_ok=True)
    lines = ["| case | nodes | " + " | ".join(f"{e} vs {engines[0]}" for e in engines[1:]) + " | notes |",
             "|---|---:|" + "---|" * (len(engines) - 1) + "---|"]
    print(lines[0])
    for c in cases:
        imgs, boxes, notes = {}, {}, []
        for e in engines:
            path = shots / f"{c['name'].replace('/', '_')}.{e}.png"
            try:
                samples = run_engine(e, c, 1, args.cpus, screenshot=path)
            except Exception as ex:
                notes.append(f"{e} failed: {ex}")
                continue
            imgs[e] = Image.open(path).convert("RGB")
            s = samples[-1]
            if "boxes" in s:
                boxes[e] = s["boxes"]
            if "fonts" in s and s["fonts"]:
                notes.append(f"chrome fonts={s['fonts']}")
            if "total_objects" in s:
                notes.append(f"chrome objects={s['total_objects']} layouts={s['n_layouts']}")
            if "styled" in s:
                notes.append(f"{e} styled={s['styled']} reflows={s['n_reflows']} (sum {s['layout_sum'] / s['layout']:.2f}x longest)")
            elif "n_reflows" in s:
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
                cell = f"{frac * 100:.2f}% px"
                if e in boxes and engines[0] in boxes:
                    cell += ", " + compare_boxes(boxes[e], boxes[engines[0]])
                if c["name"].startswith("text/"):
                    ref, got = bg_bands(imgs[engines[0]]), bg_bands(imgs[e])
                    same = sum(a == b for a, b in zip(ref, got))
                    cell += f", {same}/{len(ref)} bg bands equal"
                    if len(got) != len(ref):
                        cell += f" ({len(got)} bands)"
                    elif same != len(ref):
                        cell += " (" + "; ".join(f"band {i}: {g[1]}+{g[2]} vs {r[1]}+{r[2]}" for i, (g, r) in enumerate(zip(got, ref)) if g != r) + ")"
                cells.append(cell)
            else:
                cells.append("-")
        lines.append(f"| {c['name']} | {c['nodes']} | " + " | ".join(cells) + " | " + "; ".join(notes) + " |")
        print(lines[-1], flush=True)
    OUT.mkdir(exist_ok=True)
    (OUT / "verify.md").write_text("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("gen")
    b = sub.add_parser("bench")
    b.add_argument("--engines", default=",".join(ENGINES))
    b.add_argument("--rounds", type=int, default=3)
    b.add_argument("--iters", type=int, default=3)
    b.add_argument("--filter", default="")
    b.add_argument("--cpus", default=None, help="taskset CPU list for the single-threaded runners (taffy, blitz, servo1, firefox1)")
    b.add_argument("--agg", default="min", choices=["min", "median"])
    b.add_argument("--merge", action="store_true", help="keep other engines' samples from out/results.json")
    r = sub.add_parser("report", help="rewrite out/report.md from out/results.json")
    r.add_argument("--agg", default="min", choices=["min", "median"])
    v = sub.add_parser("verify")
    v.add_argument("--engines", default="chrome,blitz,servo1,firefox1")
    v.add_argument("--filter", default="")
    v.add_argument("--cpus", default=None)
    args = ap.parse_args()
    {"gen": cmd_gen, "bench": cmd_bench, "report": cmd_report, "verify": cmd_verify}[args.cmd](args)


if __name__ == "__main__":
    main()
