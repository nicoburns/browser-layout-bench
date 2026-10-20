"""Ladybird (LibWeb) runner for run.py. One `Ladybird --headless` process per iteration; the phase
times are the `LADYBIRD_PHASE style=<ns> construct=<ns> layout=<ns> total=<ns> full_layouts=<n>`
lines that WebContent prints to stderr once per `Document::update_layout()` with
patches/ladybird-phase-timing.patch applied (see README.md). The layout-tree dump headless mode
exits as soon as the page has loaded and gives every box's position and box model, which `verify`
compares with Chrome's `getBoundingClientRect()`."""
import os, re, subprocess, tempfile
from pathlib import Path

LADYBIRD_BIN = Path(os.environ.get("LADYBIRD_BIN", Path.home() / "repos/ladybird/Build/release/bin/Ladybird"))
# Seconds the patched headless modes wait after the load event before dumping the layout tree or
# taking the screenshot: the font pages reveal from a `document.fonts` promise that resolves after
# the load event, and the screenshot needs the reveal to have been painted.
SETTLE_SECONDS = int(os.environ.get("LADYBIRD_SETTLE_SECONDS", "2"))
# `LADYBIRD_UPDATE url=<document url>` precedes each round's `LADYBIRD_PHASE k=v ...` line.
RECORD_RE = re.compile(r"^LADYBIRD_(UPDATE|PHASE) (.*)$", re.M)
# `Box <div#cb.cls> at [x,y] positioned flex-item [ml+bl+pl w pr+br+mr] [mt+bt+pt h pb+bb+mb] ...`
BOX_RE = re.compile(r"^( *)(\w+) <(\w+)([#.][^>]*)?> at \[([-\d.]+),([-\d.]+)\](?: [^\[\]]+)? "
                    r"\[([-\d.+]+) ([-\d.]+) ([-\d.+]+)\] \[([-\d.+]+) ([-\d.]+) ([-\d.+]+)\]")


def available():
    return LADYBIRD_BIN.exists()


def skip_message():
    return f"ladybird: {LADYBIRD_BIN} not found (set LADYBIRD_BIN), skipping"


def parse_phases(stderr, url):
    """The layout update rounds of the document at `url` in one process's stderr, in order, each as
    metric -> ns (the process also lays out the initial about:blank documents)."""
    rounds, current = [], None
    for kind, rest in RECORD_RE.findall(stderr):
        if kind == "UPDATE":
            current = rest.removeprefix("url=")
        elif current == url:
            rounds.append({k: int(v) for k, v in re.findall(r"(\w+)=(\d+)", rest)})
    return rounds


def parse_layout_tree(dump, root_id="cb"):
    """Border boxes (x, y, w, h) of the `div`/`p`/`h3` descendants of `#root_id` in the layout tree
    dump, in tree (= document) order, plus the number of boxes in the whole tree and the root
    child's size. The dump's `at [x,y]` is the content box; the border box adds padding and border."""
    boxes, root, n_boxes, cb_indent = [], None, 0, None
    for line in dump.splitlines():
        m = BOX_RE.match(line)
        if not m:
            continue
        n_boxes += 1
        indent, tag, ids = len(m.group(1)), m.group(3), m.group(4) or ""
        if cb_indent is not None and indent <= cb_indent:
            cb_indent = None
        if cb_indent is None:
            if tag == "div" and f"#{root_id}" in ids:
                cb_indent = indent
            continue
        if tag not in ("div", "p", "h3"):
            continue
        x, y = float(m.group(5)), float(m.group(6))
        ml, bl, pl = (float(v) for v in m.group(7).split("+"))
        pr, br, mr = (float(v) for v in m.group(9).split("+"))
        mt, bt, pt = (float(v) for v in m.group(10).split("+"))
        pb, bb, mb = (float(v) for v in m.group(12).split("+"))
        w, h = float(m.group(8)) + pl + pr + bl + br, float(m.group(11)) + pt + pb + bt + bb
        boxes.append((x - pl - bl, y - pt - bt, w, h))
        if root is None:
            root = f"{w:.1f}x{h:.1f}"
    return boxes, n_boxes, root


def run_process(url, width, height, cpus, mode, extra=(), timeout=1200):
    cmd = [str(LADYBIRD_BIN), f"--headless={mode}", f"--window-width={width}", f"--window-height={height}", *extra, url]
    if cpus:
        cmd = ["taskset", "-c", cpus] + cmd
    env = dict(os.environ)
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    with tempfile.TemporaryDirectory() as home:
        # A private config/profile per process, so no session state leaks between iterations.
        env.update(XDG_CONFIG_HOME=f"{home}/config", XDG_DATA_HOME=f"{home}/data", XDG_CACHE_HOME=f"{home}/cache",
                   XDG_RUNTIME_DIR=f"{home}/run")  # Ladybird's IPC sockets; /run/user/<uid> may not exist
        os.mkdir(f"{home}/run", 0o700)
        return subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=timeout, env=env, cwd=home)


def crop_to_viewport(path, width, height):
    """The headless screenshot is the view's backing store, which is the viewport plus a padding band
    to the right and below; keep the viewport."""
    from PIL import Image
    with Image.open(path) as im:
        im.crop((0, 0, width, height)).convert("RGB").save(path)


def run_ladybird(case, iters, cpus, reveal_dir, width, height, screenshot=None):
    """Per-iteration dicts like the other engines': `style`, `construct`, `layout`,
    `construct+layout`, `total` (the whole `update_layout()` call) from the longest layout update
    of the process (the one after the reveal; the `display:none` document's update is tiny), and
    `n_layouts`, the number of updates that ran a full layout pass."""
    url = (reveal_dir / case["file"]).resolve().as_uri()
    samples = []
    for i in range(iters):
        proc = run_process(url, width, height, cpus, "layout-tree", [f"--screenshot-delay={SETTLE_SECONDS}"])
        phases = parse_phases(proc.stderr, url)
        if not phases:
            raise RuntimeError(f"no LADYBIRD_PHASE lines for {url} on stderr (patch applied?): {proc.stderr[-500:]}")
        main = max(phases, key=lambda p: p["layout"])
        s = dict(style=main["style"], construct=main["construct"], layout=main["layout"], total=main["total"],
                 n_layouts=sum(1 for p in phases if p.get("full_layouts", 0) > 0))
        s["construct+layout"] = s["construct"] + s["layout"]
        s["boxes"], s["n_boxes"], s["root"] = parse_layout_tree(proc.stdout)
        if screenshot and i == iters - 1:
            run_process(url, width, height, cpus, "screenshot",
                        [f"--screenshot-path={screenshot}", f"--screenshot-delay={SETTLE_SECONDS}"])
            crop_to_viewport(screenshot, width, height)
        samples.append(s)
    return samples
