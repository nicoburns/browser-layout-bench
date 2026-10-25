"""Ladybird (LibWeb) runner for run.py. One Ladybird per round, driven over its WebDriver server
(`WebDriver --headless`, plain HTTP with `urllib`): a fresh window per iteration, closed afterwards,
with the session's initial about:blank window kept open. The phase times are the `LADYBIRD_PHASE
pid=<pid> style=<ns> construct=<ns> layout=<ns> total=<ns> full_layouts=<n>` lines that WebContent
prints to stderr once per `Document::update_layout()` with patches/ladybird-phase-timing.patch
applied (see README.md); the `LADYBIRD_UPDATE pid=<pid> url=<url> reason=<reason>` line the same
process printed before names the document and the trigger of that update, and the window's URL
(`?i=N`) says which iteration it was."""
import base64, json, os, re, socket, subprocess, tempfile, time, urllib.error, urllib.request
from pathlib import Path

LADYBIRD_BIN = Path(os.environ.get("LADYBIRD_BIN", Path.home() / "repos/ladybird/Build/release/bin/Ladybird"))
WEBDRIVER_BIN = LADYBIRD_BIN.parent / "WebDriver"
WAIT_SECONDS = int(os.environ.get("LADYBIRD_WAIT_SECONDS", "600"))
# fontconfig rescans the system fonts in every process unless its cache under XDG_CACHE_HOME persists.
CACHE_DIR = Path(__file__).resolve().parent / "out/ladybird-cache"
# Every window gets its own WebContent process (`iframe`, Ladybird's default); `disable` would put all
# of the round's windows in one process, so each sample would run in a warm process.
SITE_ISOLATION = "iframe"
# A case's first load in a fresh browser is 14-18 % slower in `layout` on the real pages (the UI process's
# font service, which hands WebContent the system fonts, is cold) and within 2 % on the synthetic pages
# (one font), so only the real pages get a discarded warm-up load.
WARMUP_PREFIX = "real/"
RECORD_RE = re.compile(r"^LADYBIRD_(UPDATE|PHASE) pid=(\d+) (.*)$", re.M)
REVEALED_JS = "return document.getElementById('cb').style.display !== 'none'"
BOXES_JS = ("return [...document.querySelectorAll('#cb div, #cb p, #cb h3')]"
            ".map(e=>{const r=e.getBoundingClientRect();return [r.x,r.y,r.width,r.height]})")
FONTS_JS = "return [...document.fonts].map(f=>f.status).join(',')"


def available():
    return LADYBIRD_BIN.exists() and WEBDRIVER_BIN.exists()


def skip_message():
    return f"ladybird: {LADYBIRD_BIN} or {WEBDRIVER_BIN} not found (set LADYBIRD_BIN; build the `WebDriver` target), skipping"


def parse_updates(stderr):
    """{document url: [update, ...]} in order, each update the metric -> ns dict of a `LADYBIRD_PHASE`
    line plus its `reason`. Lines of the round's WebContent processes interleave on stderr, so a
    `PHASE` line belongs to the last `UPDATE` line with the same pid."""
    pending, updates = {}, {}
    for kind, pid, rest in RECORD_RE.findall(stderr):
        if kind == "UPDATE":
            url, reason = re.fullmatch(r"url=(\S+) reason=(\S+)", rest).groups()
            pending[pid] = (url, reason)
        elif pid in pending:
            url, reason = pending[pid]
            updates.setdefault(url, []).append({k: int(v) for k, v in re.findall(r"(\w+)=(\d+)", rest)} | {"reason": reason})
    return updates


def reveal_update(updates):
    """The update the reveal script's `cb.offsetHeight` forced right after showing `#cb`: the first full
    layout of the revealed tree (the `display:none` document's own updates come before it, later ones
    are relayouts)."""
    for u in updates:
        if u["reason"] == "HTMLElementOffsetHeight" and u["full_layouts"] > 0:
            return u
    raise RuntimeError("no HTMLElementOffsetHeight layout update (patch applied?)")


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Session:
    """One `WebDriver --headless` server and the one Ladybird (UI process) it launches for the session."""

    def __init__(self, home):
        self.port = free_port()
        env = dict(os.environ)
        env.setdefault("QT_QPA_PLATFORM", "offscreen")
        # A private config/profile per browser, so no session state leaks between rounds.
        env.update(XDG_CONFIG_HOME=f"{home}/config", XDG_DATA_HOME=f"{home}/data", XDG_CACHE_HOME=str(CACHE_DIR),
                   XDG_RUNTIME_DIR=f"{home}/run")  # Ladybird's IPC sockets; /run/user/<uid> may not exist
        os.mkdir(f"{home}/run", 0o700)
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.stderr_path = Path(home) / "stderr.txt"
        self.stderr = self.stderr_path.open("w")  # inherited by Ladybird and its WebContent processes
        self.proc = subprocess.Popen([str(WEBDRIVER_BIN), "--headless", "--port", str(self.port), f"--site-isolation={SITE_ISOLATION}",
                                      f"--profiles-directory={home}"], env=env, cwd=home, stdin=subprocess.DEVNULL,
                                     stdout=subprocess.DEVNULL, stderr=self.stderr)
        deadline = time.monotonic() + 30
        while True:
            try:
                self.request("GET", "/status")
                break
            except (urllib.error.URLError, ConnectionError, RuntimeError):
                if self.proc.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError(f"WebDriver did not start: {self.stderr_path.read_text()[-500:]}")
                time.sleep(0.02)
        self.id = self.request("POST", "/session", {"capabilities": {"alwaysMatch": {}}})["sessionId"]
        self.request("POST", f"/session/{self.id}/timeouts", {"pageLoad": WAIT_SECONDS * 1000, "script": WAIT_SECONDS * 1000})
        self.blank = self.request("GET", f"/session/{self.id}/window/handles")[0]

    def close(self):
        try:
            self.request("DELETE", f"/session/{self.id}")
        finally:
            self.proc.terminate()
            self.proc.wait(timeout=30)
            self.stderr.close()

    def request(self, method, path, body=None):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}{path}", method=method,
                                     data=json.dumps(body).encode() if body is not None else None,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=WAIT_SECONDS) as resp:
                return json.loads(resp.read())["value"]
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"{method} {path}: {e.code} {e.read()[:300]}")

    def command(self, name, body=None):
        return self.request("POST", f"/session/{self.id}/{name}", body if body is not None else {})

    def execute(self, script):
        return self.command("execute/sync", {"script": script, "args": []})

    def load(self, url, width, height):
        """`url` in a new window of the given viewport, after its `load` event and the reveal."""
        handle = self.command("window/new", {"type": "tab"})["handle"]
        self.command("window", {"handle": handle})
        self.command("window/rect", {"width": width, "height": height})
        self.command("url", {"url": url})
        deadline = time.monotonic() + WAIT_SECONDS
        while not self.execute(REVEALED_JS):
            if time.monotonic() > deadline:
                raise TimeoutError(f"{url}: not revealed after {WAIT_SECONDS}s")
            time.sleep(0.005)

    def close_window(self):
        self.request("DELETE", f"/session/{self.id}/window")
        self.command("window", {"handle": self.blank})


def run_ladybird(case, iters, reveal_dir, root_rect_js, screenshot=None):
    return run_ladybird_round([case], iters, reveal_dir, root_rect_js, screenshot=screenshot)[case["name"]]


def run_ladybird_round(cases, iters, reveal_dir, root_rect_js, screenshot=None):
    """One browser per call (= per round, for every case of the round), a fresh window (and WebContent
    process) per iteration; the real pages get a discarded warm-up load first (`?warmup`), the measured
    windows load `?i=N`. Per-iteration dicts like the other engines': `style`, `construct`, `layout`,
    `construct+layout`, `total` (the whole `update_layout()` call) of the reveal's layout update,
    `n_layouts`, the number of the document's updates that ran a full layout pass, and `root`.
    Returns {case name: samples}."""
    extra, results = {}, {}
    with tempfile.TemporaryDirectory() as home:
        session = Session(home)
        try:
            for case in cases:
                url = (reveal_dir / case["file"]).resolve().as_uri()
                if case["name"].startswith(WARMUP_PREFIX):
                    session.load(url + "?warmup", case["width"], case["height"])
                    session.close_window()
                for i in range(iters):
                    session.load(f"{url}?i={i}", case["width"], case["height"])
                    session.execute("return document.body.offsetHeight")
                    e = extra[f"{url}?i={i}"] = {"root": session.execute("return " + root_rect_js)}
                    if screenshot and i == iters - 1:
                        Path(screenshot).write_bytes(base64.b64decode(session.request("GET", f"/session/{session.id}/screenshot")))
                        e["boxes"] = [tuple(b) for b in session.execute(BOXES_JS)]
                        e["fonts"] = session.execute(FONTS_JS)
                    session.close_window()
        finally:
            session.close()
        updates = parse_updates(session.stderr_path.read_text())
    for case in cases:
        url = (reveal_dir / case["file"]).resolve().as_uri()
        samples = results[case["name"]] = []
        for i in range(iters):
            page = updates.get(f"{url}?i={i}")
            if not page:
                raise RuntimeError(f"no LADYBIRD_PHASE lines for {url}?i={i} on stderr (patch applied?)")
            main = reveal_update(page)
            s = dict(style=main["style"], construct=main["construct"], layout=main["layout"], total=main["total"],
                     n_layouts=sum(1 for u in page if u["full_layouts"] > 0))
            s["construct+layout"] = s["construct"] + s["layout"]
            s.update(extra[f"{url}?i={i}"])
            samples.append(s)
    return results
