#!/usr/bin/env python3
"""Driver: generates the corpus, runs each engine on every page in interleaved rounds, and
writes results.json + a Markdown report. See README.md for the measurement model."""
import argparse, functools, http.server, json, os, re, shutil, statistics, subprocess, sys, tempfile, threading, time
from pathlib import Path

import engines_ladybird
import engines_servo
import engines_webkit
import pages
import plot

ROOT = Path(__file__).resolve().parent
CORPUS = ROOT / "corpus"
REVEAL = CORPUS / "reveal"
REAL = ROOT / "real"
OUT = ROOT / "out"
GEN = ROOT / "target/release/gen"
BLITZ = ROOT / "target/release/blitz-runner"
# `cargo build --release -p layout-bench-blitz --features floats,writing-mode,parallel-construct --target-dir target-pcon`
BLITZ_PCON = ROOT / "target-pcon/release/blitz-runner"
# `cargo build --release --manifest-path blitz-runner-pl/Cargo.toml --target-dir target-pl` (see blitz-runner-pl/Cargo.toml)
BLITZ_PL = ROOT / "target-pl/release/blitz-runner"
SERVOSHELL = Path(os.environ.get("SERVOSHELL", Path.home() / "repos/servo/target/release/servoshell"))
WIDTH, HEIGHT = 1280, 800
ENGINES = ["taffy", "blitz", "blitz-par", "blitz-pcon", "blitz-par-pcon", "blitz-pcon-pl1", "blitz-par-pcon-pl",
           "servo1", "servo", "chrome", "webkit", "firefox", "ladybird"]

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

# Relayout scenarios: after the first layout, `relayout.js` applies each mutation as one batch, forces one layout
# (bracketed by `performance.mark`s `lb:<step>:start`/`end`) and reverts it (layout discarded) before the next step.
CHECK = False  # pass --check to blitz-runner, see run_blitz
RELAYOUT_STEPS = ["root_width", "leaf_1", "leaf_10pct", "leaf_all", "append"]
RELAYOUT_JS = (ROOT / "relayout.js").read_text()
RELAYOUT_METRICS = ["style", "construct", "layout", "style+layout"]


SELECTIONS = {}


def run_relayout_steps(evaluate, times=None):
    """Drives the scenario steps through `evaluate(js)` (the install script, or an expression whose value it
    returns); returns the script's {leaves, depth} info. The leaf selection costs two layout queries per
    element (seconds per document on the 100k-node pages in Servo), so it is computed in the first document
    an engine opens of a page and handed to its later ones (`SELECTIONS`, keyed by user agent and path).
    `times`, if given, collects each step's apply call as a (t0, t1) `time.time_ns()` interval."""
    evaluate(RELAYOUT_JS)
    key = evaluate("window.__lb.key")
    selection = SELECTIONS.get(key)
    evaluate(f"window.__lb.init({json.dumps(selection)})")
    if selection is None:
        SELECTIONS[key] = evaluate("window.__lb.selection")
    info = None
    for step in RELAYOUT_STEPS:
        t0 = time.time_ns()
        info = evaluate(f"window.__lb.relayout({step!r}, 'apply')")
        if times is not None:
            times[step] = (t0, time.time_ns())
        evaluate(f"window.__lb.relayout({step!r}, 'revert')")
    return info


def chrome_relayout(events):
    """Per step: the trace's style/construct/layout work between the step's user-timing marks (ns)."""
    marks = {e["name"]: e["ts"] for e in events if e.get("cat") == "blink.user_timing" and e.get("name", "").startswith("lb:")}
    xs = [e for e in events if e.get("ph") == "X"]
    out = {}
    for step in RELAYOUT_STEPS:
        a, b = marks.get(f"lb:{step}:start"), marks.get(f"lb:{step}:end")
        if a is None or b is None:
            continue
        within = lambda name: sum(e["dur"] for e in xs if e["name"] == name and a <= e["ts"] <= b) * 1000
        r = dict(style=within("Document::recalcStyle"), construct=within("Document::rebuildLayoutTree"), layout=within("Layout"))
        r["style+layout"] = within("UpdateLayoutTree") + r["layout"]
        if (n := sum(1 for e in xs if e["name"] == "Layout" and a <= e["ts"] <= b)) != 1:
            print(f"warning: {n} Layout events in relayout step {step}", file=sys.stderr)
        out[step] = r
    return out



def sh(cmd, cpus=None, **kw):
    if cpus:
        cmd = ["taskset", "-c", cpus] + cmd
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw).stdout


def read_manifest():
    cases = []
    for line in (CORPUS / "manifest.tsv").read_text().splitlines():
        name, file, w, h, nodes, engine, *rest = line.split("\t")
        # optional 7th column: viewport `WxH` (defaults to the global 1280x800)
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
    per page and viewport listed in `real/manifest.tsv`: `real/<page>` at 1280x800, `real/<page>@<w>` for any other width."""
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
        eng, name, *rest = line.split("\t")
        if name != case["name"]:
            continue
        if eng == "taffy":
            samples.append({"layout": int(rest[0])})
        else:  # taffy-relayout <case> <step> <ns>, after the iteration's `taffy` line
            step, ns = rest
            samples[-1][f"relayout/{step}/layout"] = int(ns)
    return samples


def run_blitz(case, iters, cpus, parallel=False, screenshot=None, binary=BLITZ, env=None):
    if not binary.exists():
        raise FileNotFoundError(f"{binary.relative_to(ROOT)} not built, see README")
    cmd = [str(binary), str(CORPUS / case["file"]), "--width", str(case["width"]), "--height", str(case["height"]), "--iters", str(iters), "--hash", "--relayout"]
    if CHECK:
        cmd.append("--check")
    if parallel:
        cmd.append("--parallel")
    if screenshot:
        cmd += ["--screenshot", str(screenshot), "--boxes"]
    out = sh(cmd, cpus, env=dict(os.environ, **env) if env else None)
    samples, phases = [], None
    for line in out.splitlines():
        if line.startswith("PHASES"):
            phases = {k: int(v) for k, v in re.findall(r"(\w+)=(\d+)", line.split("|", 1)[1])}
        elif line.startswith("RELAYOUT "):
            kv = dict(re.findall(r"(\w+)=(\w+)", line))
            samples[-1].setdefault("relayout", {})[kv["step"]] = dict(
                style=phases["style"], damage=phases.get("damage", 0), construct=phases["construct"] + phases["pconstruct"], layout=phases["layout"],
                resolve=int(kv["resolve"]))
        elif line.startswith("CHECK"):
            # --check: the incremental layout vs a forced full restyle (`full`) and vs a fresh
            # layout of the serialised document (`fresh`), each "ok" or "mismatch"
            kv = dict(re.findall(r"(\w+)=(\w+)", line))
            check = {k: kv[k] for k in ("full", "fresh")}
            if any(v != "ok" for v in check.values()):
                print(f"  CHECK {kv['step']}: {line.strip()[:300]}", file=sys.stderr)
            if kv["step"] != "initial":
                samples[-1].setdefault("relayout", {}).setdefault(kv["step"], {})["check"] = check
        elif line.startswith("BLITZ"):
            kv = {k: int(v) for k, v in re.findall(r"(\w+)=(\d+)", line)}
            # pconstruct = the deferred tasks that run between box construction and layout, where
            # Blitz builds the Parley layouts, i.e. shapes the text; it belongs with construction
            s = dict(style=phases["style"], damage=phases.get("damage", 0), construct=phases["construct"] + phases["pconstruct"], layout=phases["layout"],
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


SERVO_SPANS = {"handle_reflow", "prepare_stylist_for_reflow", "restyle_and_build_trees", "Styling", "Box Tree Construction",
               "Fragment Tree Construction", "Stacking Context Tree Construction", "Display List Construction"}


def servo_trace_rows(path):
    """Spans of servoshell's perfetto trace, decoded packet by packet straight from the protobuf: a
    round's trace runs to GBs (every layout query a page script makes - `getClientRects`,
    `getComputedStyle`, 10^5 per relayout step on the large pages - is a `handle_reflow` span of its
    own), past protobuf's 2 GB limit on one message. Only the spans the samples use (SERVO_SPANS) are
    kept, and a `handle_reflow` only if it encloses one of them, i.e. laid something out; a
    `handle_reflow` keeps its `webview_id` field (servo/servo#49259) as `webview`. tracing_perfetto writes a span's BEGIN and END packets together when it closes, children before
    their parent, so they pair up per track as read; the rows are nested by time afterwards."""
    from perfetto.protos.perfetto.trace.perfetto_trace_pb2 import TracePacket, TrackEvent
    threads, rows, open_spans, last_kept = {}, [], {}, {}
    for packet in servo_trace_packets(path):
        if packet.HasField("track_descriptor"):
            threads[packet.track_descriptor.uuid] = packet.track_descriptor.thread.thread_name
            continue
        if not packet.HasField("track_event"):
            continue
        event, ts = packet.track_event, packet.timestamp
        stack = open_spans.setdefault(event.track_uuid, [])
        if event.type == TrackEvent.TYPE_SLICE_BEGIN:
            webview = next((str(getattr(a, a.WhichOneof("value"))) for a in event.debug_annotations
                            if a.name == "webview_id" and a.WhichOneof("value")), None)
            stack.append((event.name, ts, webview))
        elif event.type == TrackEvent.TYPE_SLICE_END and stack:
            name, begin, webview = stack.pop()
            if name not in SERVO_SPANS or (name == "handle_reflow" and last_kept.get(event.track_uuid, -1) < begin):
                continue
            last_kept[event.track_uuid] = begin
            rows.append(dict(name=name, ts=begin, dur=ts - begin, track=event.track_uuid,
                             thread=threads.get(event.track_uuid, ""), webview=webview))
    # Nest per track: a span's parent is the innermost span enclosing it (spans ending at ts do not
    # enclose one beginning at ts, as in the trace processor).
    rows.sort(key=lambda r: (r["track"], r["ts"], -r["dur"]))
    stack = []
    for i, row in enumerate(rows):
        while stack and (stack[-1]["track"] != row["track"] or stack[-1]["ts"] + stack[-1]["dur"] <= row["ts"]):
            stack.pop()
        row["id"], row["parent_id"] = i, stack[-1]["id"] if stack else None
        stack.append(row)
    return rows


def servo_trace_packets(path, chunk=64 << 20):
    """The TracePackets of a perfetto trace file, streamed: a Trace is a sequence of length-delimited
    `packet` fields (tag 0x0a)."""
    from perfetto.protos.perfetto.trace.perfetto_trace_pb2 import TracePacket
    buf = b""
    with open(path, "rb") as f:
        while True:
            data = f.read(chunk)
            if not data:
                break
            buf += data
            n, i = len(buf), 0
            while True:
                j = i
                while j < n and buf[j] & 0x80:
                    j += 1
                if j + 1 >= n:
                    break
                length, shift, j = 0, 0, j + 1
                while True:
                    b = buf[j]
                    j += 1
                    length |= (b & 0x7F) << shift
                    shift += 7
                    if not b & 0x80:
                        break
                if j + length > n:
                    break
                yield TracePacket.FromString(buf[j:j + length])
                i = j + length
            buf = buf[i:]


def servo_sample(rows, main, n_reflows):
    """The sample for the `restyle_and_build_trees` span `main` and its enclosing `handle_reflow`. The
    phases are the spans within a span's time on any track: with `layout_threads` > 1 the box and
    fragment passes run on a rayon worker (`StyleThread#N`), nested under nothing."""
    by_id = {r["id"]: r for r in rows}

    def total(root_id, name):
        root = by_id[root_id]
        end = root["ts"] + root["dur"]
        return sum(r["dur"] for r in rows if r["name"] == name and root["ts"] <= r["ts"] and r["ts"] + r["dur"] <= end)

    reflow = by_id[main["parent_id"]]

    s = dict(style=total(main["id"], "Styling"), box=total(main["id"], "Box Tree Construction"),
             fragment=total(main["id"], "Fragment Tree Construction"), restyle_and_build=main["dur"],
             stacking_context=total(reflow["id"], "Stacking Context Tree Construction"),
             display_list=total(reflow["id"], "Display List Construction"), reflow=reflow["dur"],
             n_reflows=n_reflows)
    s["box+fragment"] = s["box"] + s["fragment"]
    return s


def servo_relayout_steps(browser):
    """Runs the scenario steps in the current window; returns {step: (t0, t1)} wall-clock intervals (the trace
    clock) of each step's apply call, so its reflow can be found among the window's later reflows."""
    steps = {}
    run_relayout_steps(lambda js: browser.js("return " + js if js.startswith("window.__lb.") else js), times=steps)
    return steps


def servo_window_sample(rows, window):
    """The reveal reflow of one WebDriver window: its `handle_reflow` spans are the ones whose `webview`
    is the window's WebDriver handle (servo prints a WebViewId the same way in both). Of the window's
    `restyle_and_build_trees` spans up to the observed reveal, the reveal's is the one that built the
    tree: the others laid the page out with `#cb` hidden (0 to 4 of them, one per 20 ms of parsing) or
    relaid a wide page out for its scrollbar right after the reveal, 0.01-0.02 ms of box construction
    each, so neither their count nor their order tells them apart."""
    reflows = {r["id"] for r in rows if r["name"] == "handle_reflow" and r["webview"] == window["handle"]}
    if not reflows:
        raise RuntimeError(f"{window['url']}: no reflow of webview {window['handle']} in the trace "
                           "(a servoshell without servo/servo#49259?)")
    # A reflow still open when servoshell is killed at the end of the round (it waits on the painter
    # after a page's last restyle) has no `handle_reflow` parent; the reveal's reflow is complete,
    # as the reveal script's `offsetHeight` forced it.
    restyles = [r for r in rows if r["name"] == "restyle_and_build_trees" and r["parent_id"] in reflows
                and window["nav"] <= r["ts"] <= window["revealed"]]
    if not restyles:
        raise RuntimeError(f"{window['url']}: no reflow before the reveal")
    sample = max((servo_sample(rows, r, len(restyles)) for r in restyles), key=lambda s: s["box+fragment"])
    sample["relayout"] = {}
    for step, (t0, t1) in window.get("steps", {}).items():
        spans = [r for r in rows if r["name"] == "restyle_and_build_trees" and r["parent_id"] in reflows
                 and t0 <= r["ts"] <= t1]
        if spans:
            sample["relayout"][step] = servo_sample(rows, max(spans, key=lambda r: r["dur"]), len(spans))
    return sample


def corpus_server():
    """Servo's fetch rejects `file://` fonts (CORS mode, opaque origin), so it gets the corpus over
    localhost HTTP instead. Returns the base URL."""
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Handler, directory=str(CORPUS)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{server.server_address[1]}"


def run_servo_round(cases, iters, cpus, threads, screenshot=None, warmup=True):
    """One servoshell per call (= per round, for every case of the round) driven over WebDriver
    (engines_servo), a fresh window per iteration (`?i=N`, closed once revealed) so every sample is
    still a first layout, but in a warm process like Chrome's, WebKit's and Firefox's. Each case first
    loads its page as a discarded warm-up (`?warmup`). Returns {case name: samples}."""
    windows = {}
    with tempfile.TemporaryDirectory() as d:
        browser = engines_servo.Browser(SERVOSHELL, threads, cpus, d, WIDTH, HEIGHT)
        try:
            for case in cases:
                url = f"{corpus_server()}/reveal/{case['file']}"
                if warmup:
                    browser.close(browser.load(url + "?warmup", case["width"], case["height"]))
                windows[case["name"]] = []
                for i in range(iters):
                    w = browser.load(f"{url}?i={i}", case["width"], case["height"])
                    w["root"] = browser.js("return " + ROOT_RECT_JS)
                    w["steps"] = servo_relayout_steps(browser)
                    if screenshot and i == iters - 1:
                        browser.screenshot(screenshot)
                        w["boxes"] = [tuple(b) for b in browser.js(
                            "return [...document.querySelectorAll('#cb div, #cb p, #cb h3')].map(e=>{const r=e.getBoundingClientRect();return [r.x,r.y,r.width,r.height]})")]
                        w["fonts"] = browser.js("return [...document.fonts].map(f=>f.status).join(',')")
                    browser.close(w)
                    windows[case["name"]].append(w)
        finally:
            browser.quit()
        rows = servo_trace_rows(Path(d) / "servo.pftrace")
    results = {}
    for name, ws in windows.items():
        results[name] = []
        for w in ws:
            s = servo_window_sample(rows, w)
            s.update({k: w[k] for k in ("root", "boxes", "fonts") if k in w})
            results[name].append(s)
    return results


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
            cdp.send("Tracing.start", {"traceConfig": {"includedCategories": ["devtools.timeline", "disabled-by-default-devtools.timeline", "blink", "blink_style", "blink.user_timing"]}})
            page.goto(url, wait_until="load", timeout=600_000)
            page.wait_for_function("document.getElementById('cb').style.display !== 'none'", timeout=600_000)
            page.evaluate("document.body.offsetHeight")
            root = page.evaluate(ROOT_RECT_JS)
            run_relayout_steps(page.evaluate)
            cdp.send("Tracing.end")
            while not done:
                page.wait_for_timeout(50)
            # the first layout's metrics come from the events before the first relayout mark: a step's
            # recalcStyle/Layout can outlast the reveal's (e.g. `leaf_all` on real pages)
            cut = min((e["ts"] for e in events if e.get("cat") == "blink.user_timing" and e.get("name", "").startswith("lb:")),
                      default=float("inf"))
            initial = [e for e in events if e.get("ph") == "X" and e.get("ts", 0) < cut]
            def longest(name):
                return max(e["dur"] for e in initial if e.get("name") == name) * 1000
            layouts = [e for e in initial if e.get("name") == "Layout"]
            main = max(layouts, key=lambda e: e["dur"])
            # `UpdateLayoutTree` = `Document::recalcStyle` (style) + `Document::rebuildLayoutTree`
            # (LayoutObject construction); `Layout` is fragment-tree work only.
            s = dict(layout=main["dur"] * 1000, style=longest("Document::recalcStyle"),
                     construct=longest("Document::rebuildLayoutTree"), update_layout_tree=longest("UpdateLayoutTree"),
                     n_layouts=len(layouts), root=root, total_objects=main.get("args", {}).get("beginData", {}).get("totalObjects"))
            s["construct+layout"] = s["construct"] + s["layout"]
            s["style+layout"] = s["update_layout_tree"] + s["layout"]
            s["relayout"] = chrome_relayout(events)
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


def parse_firefox_profile(profile, url):
    """Marker intervals of the content process that loaded `url`, from the decoded profile JSON: Styles
    (style traversal and frame construction), Reflow (layout), DoFlushPendingNotifications (the flush
    containing both) and DisplayList. Times are ms floats; returned in ns like the other engines."""
    for proc in profile.get("processes", []):
        window_ids = {pg["innerWindowID"] for pg in proc.get("pages", []) if pg["url"] == url}
        if window_ids:
            break
    else:
        raise RuntimeError(f"no content process for {url} in {path}")
    thread = next(t for t in proc["threads"] if t["name"] == "GeckoMain")
    strings = thread["stringTable"]
    schema = thread["markers"]["schema"]
    intervals, open_starts, marks = {}, {}, {}
    for row in thread["markers"]["data"]:
        name, start, end, phase = (row[schema[k]] for k in ("name", "startTime", "endTime", "phase"))
        name = strings[name]
        data = row[schema["data"]] if len(row) > schema["data"] else None
        if name.startswith("Reflow"):
            name = "Reflow"
        if data and "innerWindowID" in data and data["innerWindowID"] not in window_ids:
            continue
        if name == "UserTiming" and data and data.get("entryType") == "mark":
            marks[data["name"]] = start
            continue
        if phase == 1:
            intervals.setdefault(name, []).append((end - start, data, start))
        elif phase == 2:
            open_starts.setdefault(name, []).append(start)
        elif phase == 3 and open_starts.get(name):
            start = open_starts[name].pop()
            intervals.setdefault(name, []).append((end - start, data, start))

    # the first layout's metrics come from the intervals before the first relayout mark (a step's
    # Reflow/Styles can outlast the reveal's); the steps are read from the full set below
    cut = min(marks.values(), default=float("inf"))
    initial = {k: [i for i in v if i[2] < cut] for k, v in intervals.items()}

    def longest(name, within=None):
        """Longest interval of `name` before the relayout steps, inside `within` = (dur, data, start) if given."""
        cands = initial.get(name, [])
        if within:
            cands = [i for i in cands if i[2] >= within[2] and i[2] + i[0] <= within[2] + within[0]]
        return max(cands, key=lambda i: i[0], default=(None, None, None))

    # The measured reflow is the longest; style and flush are taken from the flush that contains it
    # (the one the reveal triggers), not the longest anywhere: Firefox restyles the page again after
    # load (`:visited`, image state) and on a warm process that restyle can outlast the main traversal.
    reflow = longest("Reflow")
    flush = min((i for i in initial.get("DoFlushPendingNotifications", [])
                 if reflow[2] is not None and i[2] <= reflow[2] and i[2] + i[0] >= reflow[2] + reflow[0]),
                key=lambda i: i[0], default=None)
    style, style_data, _ = longest("Styles", flush) if flush else longest("Styles")
    reflows = [d for d, _, _ in initial.get("Reflow", [])]
    ms = lambda v: None if v is None else int(v * 1e6)
    s = dict(layout=ms(reflow[0]), style=ms(style), flush=ms(flush[0] if flush else longest("DoFlushPendingNotifications")[0]),
             display_list=ms(longest("DisplayList")[0]), layout_sum=ms(sum(reflows)), n_reflows=len(reflows),
             styled=style_data["elementsTraversed"] if style_data else None)
    s["style+layout"] = s["style"] + s["layout"]
    def within(name, a, b):
        return sum(d for d, _, st in intervals.get(name, []) if a <= st <= b)
    s["relayout"] = {}
    for step in RELAYOUT_STEPS:
        a, b = marks.get(f"lb:{step}:start"), marks.get(f"lb:{step}:end")
        if a is not None and b is not None:
            r = dict(style=ms(within("Styles", a, b)), layout=ms(within("Reflow", a, b)))
            r["style+layout"] = r["style"] + r["layout"]
            s["relayout"][step] = r
    return s


def launch_firefox(p, exe, env, attempts=3):
    """Headless Firefox segfaults at launch now and then (5 of 306 launches in a bench run, none in
    80 back-to-back launches with or without the profiler); retry rather than lose the whole case."""
    from playwright.sync_api import Error
    for attempt in range(attempts):
        try:
            return p.firefox.launch(executable_path=exe, env=env)
        except Error as ex:
            if attempt == attempts - 1 or "Failed to launch" not in str(ex):
                raise
            print(f"firefox: launch failed (attempt {attempt + 1}), retrying", file=sys.stderr)


def run_firefox(case, iters, screenshot=None):
    return run_firefox_round([case], iters, screenshot)[case["name"]]


def run_firefox_round(cases, iters, screenshot=None):
    """One Firefox process per call (= per round, for every case of the round), a fresh tab per iteration,
    all tabs in one content process (see `keep` below). The process's first page load gets an extra full
    reflow ~200 ms after the reveal (no elements restyled; 105 ms on Wikipedia, 64 ms on rustdoc) and
    cold font/text caches, so each case first loads its page as a discarded warm-up (`?warmup`); the
    measured tabs load `?i=N`, which is how their windows are told apart in the profile. Tabs 1–4 of a
    process measured within 1% of each other on flex/wide/10000 and Wikipedia; a cold process is 10–20%
    slower on text-heavy pages. Returns {case name: samples}."""
    from playwright.sync_api import sync_playwright
    results = {}
    with sync_playwright() as p, tempfile.TemporaryDirectory() as d:
        exe = p.firefox.executable_path
        blank = Path(d) / "blank.html"
        blank.write_text("<!doctype html>\n")
        profile = Path(d) / "profile.json"
        env = dict(os.environ, **FIREFOX_PROFILER_ENV, MOZ_PROFILER_SHUTDOWN=str(profile))
        browser = launch_firefox(p, exe, env)

        def load(case, page_url):
            page = browser.new_page(viewport={"width": case["width"], "height": case["height"]})
            page.goto(page_url, wait_until="load", timeout=600_000)
            page.wait_for_function("document.getElementById('cb').style.display !== 'none'", timeout=600_000)
            return page

        # Each new_page() is a new context, and the file content process exits with its last tab, so
        # this first file:// page stays open to keep every tab (warm-up included) in that one process;
        # without it each tab gets a fresh, cold process.
        keep = browser.new_page()
        keep.goto(blank.as_uri(), wait_until="load")
        roots = {}
        for case in cases:
            url = (REVEAL / case["file"]).resolve().as_uri()
            load(case, url + "?warmup").close()
            roots[case["name"]] = []
            for i in range(iters):
                page = load(case, f"{url}?i={i}")
                page.evaluate("document.body.offsetHeight")
                roots[case["name"]].append(page.evaluate(ROOT_RECT_JS))
                run_relayout_steps(page.evaluate)
                if screenshot and i == iters - 1:
                    page.screenshot(path=str(screenshot))
                page.close()
        browser.close()
        profile = json.loads(profile.read_text())
        for case in cases:
            url = (REVEAL / case["file"]).resolve().as_uri()
            samples = results[case["name"]] = []
            for i, root in enumerate(roots[case["name"]]):
                s = parse_firefox_profile(profile, f"{url}?i={i}")
                s["root"] = root
                samples.append(s)
    return results

# Engines measured one process per round for all of the round's cases (`run_engine_round`) instead of one
# process per case: Firefox's launch, warm-up, profile dump and decode, servoshell's launch, warm-up and trace
# decode, and Ladybird's WebDriver server and UI process start are then paid once per round.
BATCH_ENGINES = {"firefox", "servo1", "servo", "ladybird"}


def run_engine_round(engine, cases, iters, cpus):
    if engine == "firefox":
        return run_firefox_round(cases, iters)
    if engine == "servo1":
        return run_servo_round(cases, iters, cpus, 1)
    if engine == "servo":
        return run_servo_round(cases, iters, None, 3)
    if engine == "ladybird":
        return engines_ladybird.run_ladybird_round(cases, iters, REVEAL, ROOT_RECT_JS, relayout=run_relayout_steps, steps=RELAYOUT_STEPS)
    raise ValueError(engine)


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
    if engine == "blitz-par-pcon-pl":
        return run_blitz(case, iters, None, parallel=True, screenshot=screenshot, binary=BLITZ_PL)
    if engine == "servo1":
        return run_servo_round([case], iters, cpus, 1, screenshot=screenshot)[case["name"]]
    if engine == "servo":
        return run_servo_round([case], iters, None, 3, screenshot=screenshot)[case["name"]]
    if m := re.fullmatch(r"servo(\d+)", engine):  # ad-hoc `layout_threads=N` sweeps, not in ENGINES
        return run_servo_round([case], iters, None, int(m.group(1)), screenshot=screenshot)[case["name"]]
    if engine == "chrome":
        return run_chrome(case, iters, None, screenshot=screenshot)
    if engine == "webkit":
        return engines_webkit.run_webkit(case, iters, CORPUS, case["width"], case["height"], ROOT_RECT_JS, screenshot=screenshot,
                                         relayout=run_relayout_steps)
    if engine == "firefox":
        return run_firefox(case, iters, screenshot=screenshot)
    if engine == "ladybird":
        return engines_ladybird.run_ladybird(case, iters, REVEAL, ROOT_RECT_JS, screenshot=screenshot)
    raise ValueError(engine)


def available_engines(engines):
    if any(e.startswith("firefox") for e in engines) and not firefox_installed():
        print("firefox: Playwright's Firefox is not installed (python -m playwright install firefox); skipping",
              file=sys.stderr)
        engines = [e for e in engines if not e.startswith("firefox")]
    if any(re.fullmatch(r"servo\d*", e) for e in engines) and not SERVOSHELL.exists():
        print(f"servo: {SERVOSHELL} not found (set SERVOSHELL to a servoshell built with --features tracing-perfetto); skipping",
              file=sys.stderr)
        engines = [e for e in engines if not re.fullmatch(r"servo\d*", e)]
    if "webkit" in engines and not engines_webkit.available():
        print(engines_webkit.skip_message(), file=sys.stderr)
        engines = [e for e in engines if e != "webkit"]
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


# Column order within every table: Chrome, WebKit, Firefox, Servo, Blitz, Taffy; the Chrome column is the
# reference for the multipliers.
COLUMNS = [
    ("Layout only", [("chrome", "layout", "Chrome Layout (incl. shaping)"), ("ladybird", "layout", "Ladybird layout (incl. shaping)"),
                     ("servo1", "fragment", "Servo(1) Fragment Tree"), ("servo", "fragment", "Servo(3) Fragment Tree"),
                     ("blitz", "layout", "Blitz `layout`"), ("blitz-par-pcon", "layout", "Blitz `layout` (parallel style+construct)"),
                     ("blitz-pcon-pl1", "layout", "Blitz `layout` (#1034 build, 1 thread)"),
                     ("blitz-par-pcon-pl", "layout", "Blitz `layout` (#1034 build, parallel)"),
                     ("taffy", "layout", "Taffy")]),
    ("Construction", [("chrome", "construct", "Chrome rebuildLayoutTree"), ("ladybird", "construct", "Ladybird tree build"),
                      ("servo1", "box", "Servo(1) Box Tree"), ("servo", "box", "Servo(3) Box Tree"),
                      ("blitz", "construct", "Blitz construct (+pconstruct)"), ("blitz-pcon", "construct", "Blitz construct, parallel"),
                      ("blitz-par-pcon", "construct", "Blitz construct, parallel (parallel style)")]),
    ("Box construction + layout", [("chrome", "construct+layout", "Chrome rebuildLayoutTree+Layout"),
                                   ("webkit", "layout", "WebKit Layout (incl. shaping)"),
                                   ("firefox", "layout", "Firefox Reflow"),
                                   ("ladybird", "construct+layout", "Ladybird tree build+layout"),
                                   ("servo1", "box+fragment", "Servo(1) Box+Fragment"), ("servo", "box+fragment", "Servo(3) Box+Fragment"),
                                   ("blitz", "construct+layout", "Blitz construct+layout"),
                                   ("blitz-pcon", "construct+layout", "Blitz construct+layout (parallel construct)"),
                                   ("blitz-par-pcon", "construct+layout", "Blitz construct+layout (parallel style+construct)"),
                                   ("blitz-par-pcon-pl", "construct+layout", "Blitz construct+layout (parallel construct+layout)")]),
    ("Style", [("chrome", "style", "Chrome recalcStyle"), ("webkit", "style", "WebKit RecalculateStyles (incl. render-tree construction)"),
               ("firefox", "style", "Firefox Styles (incl. frame construction)"), ("ladybird", "style", "Ladybird update_style"),
               ("servo1", "style", "Servo(1) Styling"), ("servo", "style", "Servo(3) Styling"),
               ("blitz", "style", "Blitz style"), ("blitz-par", "style", "Blitz style (parallel)"),
               ("blitz-par-pcon", "style", "Blitz style (parallel style+construct)")]),
    ("Whole pipeline (style to laid-out tree)", [
        ("chrome", "style+layout", "Chrome UpdateLayoutTree+Layout"),
        ("webkit", "style+layout", "WebKit RecalculateStyles+Layout"),
        ("firefox", "style+layout", "Firefox Styles+Reflow"),
        ("ladybird", "total", "Ladybird update_layout()"),
        ("servo1", "restyle_and_build", "Servo(1) restyle_and_build_trees"), ("servo", "restyle_and_build", "Servo(3) restyle_and_build_trees"),
        ("blitz", "resolve", "Blitz resolve()"), ("blitz-par", "resolve", "Blitz resolve() (parallel style)"),
        ("blitz-par-pcon", "resolve", "Blitz resolve() (parallel style+construct)"),
        ("blitz-par-pcon-pl", "resolve", "Blitz resolve() (parallel style+construct+layout)")]),
]

# Relayout scenarios (see RELAYOUT_STEPS): the same engines' layout and whole-pipeline phases for the step's
# incremental layout. Servo's incremental reflows run no box/fragment spans, so only its whole pipeline is listed.
RELAYOUT_LABELS = {"root_width": "root width 0.8x", "leaf_1": "1 leaf +1px", "leaf_10pct": "10% of leaves +1px",
                   "leaf_all": "all leaves +1px", "append": "append 10% more children"}
for _step, _label in RELAYOUT_LABELS.items():
    _k = f"relayout/{_step}/"
    COLUMNS += [
        (f"Relayout ({_label}): layout", [
            ("taffy", _k + "layout", "Taffy compute_layout"),
            ("chrome", _k + "layout", "Chrome Layout"), ("webkit", _k + "layout", "WebKit Layout"),
            ("firefox", _k + "layout", "Firefox Reflow"), ("ladybird", _k + "layout", "Ladybird layout"),
            ("blitz", _k + "layout", "Blitz `layout`"), ("blitz-par-pcon", _k + "layout", "Blitz `layout` (parallel style+construct)"),
            ("blitz-par-pcon-pl", _k + "layout", "Blitz `layout` (#1034 build, parallel)")]),
        (f"Relayout ({_label}): whole pipeline", [
            ("chrome", _k + "style+layout", "Chrome UpdateLayoutTree+Layout"), ("webkit", _k + "style+layout", "WebKit RecalculateStyles+Layout"),
            ("firefox", _k + "style+layout", "Firefox Styles+Reflow"), ("ladybird", _k + "total", "Ladybird update_layout()"),
            ("servo1", _k + "restyle_and_build", "Servo(1) restyle_and_build_trees"), ("servo", _k + "restyle_and_build", "Servo(3) restyle_and_build_trees"),
            ("blitz", _k + "resolve", "Blitz resolve()"), ("blitz-par-pcon", _k + "resolve", "Blitz resolve() (parallel style+construct)"),
            ("blitz-par-pcon-pl", _k + "resolve", "Blitz resolve() (parallel style+construct+layout)")]),
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
             "of the same table (1.00x = Chrome); bold = fastest engine of the row, Taffy excluded. Servo(n) = `layout_threads=n`. "
             "Text shaping is in the layout phase of Chrome, "
             "Firefox and Ladybird but in the construction phase of Blitz and Servo, so \"Layout only\" is like-for-like only among "
             "Servo/Blitz/Taffy and \"Box construction + layout\" is the comparable table for text-bearing cases; Firefox's Reflow "
             "(shaping + layout; its frame construction is inside Styles) is listed there. Case names link to the case's bar chart; "
             "one page of charts per suite: " + " · ".join(f"[{s}/](plots/{s}.md)" for s in plot.suites(results)) + "."
             + normalized_note(results), ""]
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
            lines.append(f"| [{name}](plots/{plot.case_path(name)}) | {data['nodes']} | "
                         + " | ".join(fmt_cell(v, ref, v == best and e != "taffy") for (e, _, _), v in zip(cols, values)) + " |")
        lines.append("")
    lines += spread_section(results, engines)
    return "\n".join(lines)


def normalized_note(results):
    """Sentence for the report header when some engines' samples were folded in by `normalize`."""
    per_engine = {}
    for data in results.values():
        for e, samples in data["engines"].items():
            per_engine.setdefault(e, []).extend(s["chrome_norm"] for s in samples if "chrome_norm" in s)
    normalized = {e: v for e, v in per_engine.items() if v}
    if not normalized:
        return ""
    return (" " + ", ".join(sorted(normalized)) + " were measured in a later run and scaled per case by Chrome's stored/new "
            "`style+layout` ratio (median " + f"{statistics.median([f for v in normalized.values() for f in v]):.2f}"
            "; see README, Versions and methodology): differences under ~10% between those and the other columns are within "
            "the normalisation's uncertainty.")


def spread_section(results, engines):
    """One table of median / min over the samples of each cell, so the spread behind the `min` figures is
    visible: 1.00 = all samples equal. Each engine is shown on its first metric in COLUMNS (its layout
    metric where it has one). Last two rows: median over the cases and the p90 case."""
    cols = []
    for e in engines:
        m = next((m for _, cs in COLUMNS for ce, m, _ in cs if ce == e), None)
        if m:
            cols.append((e, m))
    lines = ["### Sample spread", "", "Median ÷ min of the samples behind each cell above (1.00 = all samples equal), per engine on "
             + ", ".join(f"{e} `{m}`" for e, m in cols) + ".", "",
             "| case | " + " | ".join(e for e, _ in cols) + " |", "|---|" + "---:|" * len(cols)]
    per_engine = {e: [] for e, _ in cols}
    for name, data in results.items():
        cells = []
        for e, m in cols:
            v = [x.get(m) for x in data["engines"].get(e, []) if x.get(m) is not None]
            r = statistics.median(v) / min(v) if len(v) >= 2 else None
            if r is not None:
                per_engine[e].append(r)
            cells.append("-" if r is None else f"{r:.2f}")
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    for label, pick in (("**median case**", statistics.median), ("**p90 case**", lambda v: statistics.quantiles(v, n=10)[8] if len(v) >= 10 else max(v))):
        lines.append(f"| {label} | " + " | ".join(f"{pick(per_engine[e]):.2f}" if per_engine[e] else "-" for e, _ in cols) + " |")
    return lines + [""]


def cmd_report(args):
    """Rewrite out/report.md from out/results.json without re-measuring."""
    results = json.loads((OUT / "results.json").read_text())
    md = report(results, args.agg, sorted({e for d in results.values() for e in d["engines"]}))
    (OUT / "report.md").write_text(md)
    print(md)


def cmd_bench(args):
    global CHECK
    CHECK = args.check
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
    def record(r, name, e, samples):
        for s in samples:  # `relayout/<step>/<metric>` keys: plain metrics for the tables, pages and normalize
            for step, metrics in s.pop("relayout", {}).items():
                s.update({f"relayout/{step}/{m}": v for m, v in metrics.items()})
        results[name]["engines"][e] += samples
        best = agg([list(s.values())[0] for s in samples], "min")
        print(f"round {r} {name:24s} {e:10s} {len(samples)} samples, min first metric {fmt_ms(best)} ms", flush=True)

    def run_batch(r, e):
        try:
            per_case = run_engine_round(e, cases, args.iters, args.cpus)
        except Exception as ex:
            print(f"round {r} {e}: FAILED {ex}", file=sys.stderr)
            return
        for name, samples in per_case.items():
            record(r, name, e, samples)

    for r in range(args.rounds):
        order = engines if r % 2 == 0 else engines[::-1]
        # batch engines keep their place in the round's engine order: those listed before the first
        # per-case engine run before the per-case loop, the rest after it
        first = next((i for i, e in enumerate(order) if e not in BATCH_ENGINES), len(order))
        for e in order[:first]:
            run_batch(r, e)
        for c in cases:
            for e in order[first:]:
                if e in BATCH_ENGINES:
                    continue
                if e == "taffy" and not c["taffy"]:
                    continue
                try:
                    samples = run_engine(e, c, args.iters, args.cpus)
                except Exception as ex:
                    print(f"round {r} {c['name']} {e}: FAILED {ex}", file=sys.stderr)
                    continue
                record(r, c["name"], e, samples)
        for e in order[first:]:
            if e in BATCH_ENGINES:
                run_batch(r, e)
        (OUT / args.out).write_text(json.dumps(results, indent=1))
    if args.out != "results.json":
        return
    md = report(results, args.agg, sorted({e for d in results.values() for e in d["engines"]}))
    (OUT / "report.md").write_text(md)
    print(md)


def cmd_compare(args):
    """Calibration: the min of each metric in out/<file> (a `bench --out` run) against out/results.json."""
    stored = json.loads((OUT / "results.json").read_text())
    fresh = json.loads((OUT / args.file).read_text())
    print("| case | engine | metric | stored ms | fresh ms | fresh/stored |\n|---|---|---|---|---|---|")
    for name, data in fresh.items():
        for e, samples in data["engines"].items():
            old = stored.get(name, {}).get("engines", {}).get(e)
            if not samples or not old:
                continue
            for metric in [m for m in samples[0] if isinstance(samples[0][m], int)]:
                a = agg([s[metric] for s in old if metric in s], "min")
                b = agg([s[metric] for s in samples if metric in s], "min")
                print(f"| {name} | {e} | {metric} | {fmt_ms(a)} | {fmt_ms(b)} | {b / a:.2f} |")


# Sample keys that are counts or identities, not durations; everything else in a sample is ns.
COUNT_KEYS = {"n_reflows", "n_layouts", "n_boxes", "total_objects", "root", "hash", "boxes", "chrome_norm"}


def cmd_normalize(args):
    """Fold a later run (`bench --out`, Chrome included) into out/results.json for the given engines,
    scaling every duration of a case by the stored/new ratio of Chrome's `style+layout` minimum on that
    case, so the VM's speed on the two days cancels to the extent Chrome tracks it (phase factors of one
    case agree within ~2%, so one factor per case). The factor is kept in each sample as `chrome_norm`."""
    stored = json.loads((OUT / "results.json").read_text())
    fresh = json.loads((OUT / args.file).read_text())
    engines = args.engines.split(",")
    factors = []
    for name, data in fresh.items():
        if name not in stored or "chrome" not in data["engines"] or "chrome" not in stored[name]["engines"]:
            print(f"{name}: no Chrome reference in both runs, skipped", file=sys.stderr)
            continue
        f = agg([s[args.metric] for s in stored[name]["engines"]["chrome"]], "min") / agg([s[args.metric] for s in data["engines"]["chrome"]], "min")
        factors.append(f)
        for e in engines:
            if e not in data["engines"]:
                continue
            stored[name]["engines"][e] = [{k: round(v * f) if k not in COUNT_KEYS and isinstance(v, int) else v for k, v in s.items()}
                                          | {"chrome_norm": round(f, 4)} for s in data["engines"][e]]
        print(f"{name:40s} chrome {args.metric} stored/new {f:.3f}")
    print(f"median factor {statistics.median(factors):.3f} over {len(factors)} cases", file=sys.stderr)
    (OUT / "results.json").write_text(json.dumps(stored, indent=1))
    md = report(stored, "min", sorted({e for d in stored.values() for e in d["engines"]}))
    (OUT / "report.md").write_text(md)


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


def cmd_plot(args):
    """Bar charts of out/results.json (one SVG per case, one Markdown page per suite) into out/plots/."""
    results = json.loads((OUT / "results.json").read_text())
    for p in plot.plot_all(results, COLUMNS, OUT / "plots"):
        print(p.relative_to(ROOT))


def cmd_pages(args):
    """Static site of out/results.json (landing, per-suite and comparison pages) into out/pages/."""
    results = json.loads((OUT / "results.json").read_text())
    for p in pages.build(results, COLUMNS, COUNT_KEYS, ROOT, OUT / "pages"):
        print(p.relative_to(ROOT))


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
                notes.append(f"{e} fonts={s['fonts']}")
            if "total_objects" in s:
                notes.append(f"chrome objects={s['total_objects']} layouts={s['n_layouts']}")
            elif "n_layouts" in s:
                notes.append(f"{e} layouts={s['n_layouts']}")
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
    b.add_argument("--engines", default=",".join(ENGINES),
                   help="comma-separated engine ids (servoN = N layout threads); firefox, servo1 and servo run one "
                        "browser per round for all of the round's cases")
    b.add_argument("--rounds", type=int, default=3)
    b.add_argument("--iters", type=int, default=3)
    b.add_argument("--check", action="store_true", help="Blitz: compare each relayout step with a full restyle and a fresh layout")
    b.add_argument("--filter", default="")
    b.add_argument("--cpus", default=None, help="taskset CPU list for the single-threaded runners (taffy, blitz, servo1)")
    b.add_argument("--agg", default="min", choices=["min", "median"])
    b.add_argument("--merge", action="store_true", help="keep other engines' samples from out/results.json")
    b.add_argument("--out", default="results.json", help="write samples to out/<file> instead (no report); e.g. a calibration run")
    r = sub.add_parser("report", help="rewrite out/report.md from out/results.json")
    r.add_argument("--agg", default="min", choices=["min", "median"])
    sub.add_parser("plot")
    sub.add_parser("pages", help="write the static results site to out/pages/")
    v = sub.add_parser("verify")
    v.add_argument("--engines", default="chrome,webkit,blitz,servo1,firefox")
    v.add_argument("--filter", default="")
    v.add_argument("--cpus", default=None)
    cmp_ = sub.add_parser("compare", help="min per metric of a `bench --out` run vs out/results.json")
    cmp_.add_argument("file")
    n = sub.add_parser("normalize", help="fold a `bench --out` run into out/results.json, scaled per case by Chrome's stored/new ratio")
    n.add_argument("file")
    n.add_argument("--engines", required=True, help="engines of the run to take (Chrome itself stays as stored)")
    n.add_argument("--metric", default="style+layout", help="Chrome metric whose per-case minimum gives the factor")
    args = ap.parse_args()
    {"gen": cmd_gen, "bench": cmd_bench, "report": cmd_report, "verify": cmd_verify, "plot": cmd_plot, "compare": cmd_compare,
     "normalize": cmd_normalize, "pages": cmd_pages}[args.cmd](args)


if __name__ == "__main__":
    main()
