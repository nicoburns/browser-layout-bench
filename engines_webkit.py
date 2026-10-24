"""WebKit (Playwright's WPE MiniBrowser build) runner for run.py. Playwright exposes no raw protocol
session for WebKit, so this drives the binary itself: `MiniBrowser --inspector-pipe` speaks the
Playwright WebKit protocol as null-delimited JSON on fds 3/4, browser-level commands (`Playwright.*`,
`Target.*`) directly and the Web Inspector domains of a page wrapped in `Target.sendMessageToTarget`.

The phase times are JS-timed from a bootstrap script (`Page.setBootstrapScript`, run before any page
script) that wraps the `offsetHeight` getter the reveal script reads right after showing `#cb`:
`performance.now()` around a forced style update (`getComputedStyle`) and then the forced layout.
The Inspector `Timeline` domain gives `RecalculateStyles`/`Layout` records instead, but recording
also emits an `InvalidateLayout` record with a JS stack for every renderer, which doubles the
measured style time, so the Timeline is only used by `verify` to count layouts. `performance.now()`
is 1 ms-grained unless the page is cross-origin isolated, hence the corpus is served over localhost
HTTP with COOP/COEP headers (20 µs grain), which also makes WebKit swap the page into a new process
(a provisional Inspector target) on navigation."""
import base64, functools, http.server, json, os, subprocess, threading, time
from pathlib import Path

LAUNCH_ARGS = ["--inspector-pipe", "--headless", "--no-startup-window"]
WAIT_SECONDS = int(os.environ.get("WEBKIT_WAIT_SECONDS", "600"))
ISOLATION_HEADERS = {"Cross-Origin-Opener-Policy": "same-origin", "Cross-Origin-Embedder-Policy": "require-corp"}
BOOTSTRAP_JS = """(()=>{const d=Object.getOwnPropertyDescriptor(HTMLElement.prototype,'offsetHeight');
const now=performance.now.bind(performance);
Object.defineProperty(HTMLElement.prototype,'offsetHeight',{configurable:true,get(){
if(window.__lb||this.id!=='cb')return d.get.call(this);
const t0=now();getComputedStyle(this).display;const t1=now();const h=d.get.call(this);const t2=now();
window.__lb={style:t1-t0,layout:t2-t1,total:t2-t0};return h}})})()"""
REVEALED_JS = "!!window.__lb"


def executable():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        return Path(p.webkit.executable_path)


def available():
    try:
        return executable().exists()
    except Exception:
        return False


def skip_message():
    return "WebKit not installed (python -m playwright install webkit && python -m playwright install-deps webkit)"


@functools.cache
def isolated_server(directory):
    """The corpus over localhost HTTP with the headers that make a page cross-origin isolated. Returns the base URL."""
    class Handler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            for k, v in ISOLATION_HEADERS.items():
                self.send_header(k, v)
            super().end_headers()

        def log_message(self, *args):
            pass
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Handler, directory=str(directory)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{server.server_address[1]}"


class Browser:
    """One MiniBrowser process and its protocol pipe; pages are created in one browser context."""

    def __init__(self):
        r_in, w_in = os.pipe()
        r_out, w_out = os.pipe()

        def child():  # the child reads commands on fd 3 and writes replies and events to fd 4
            os.dup2(r_in, 100), os.dup2(w_out, 101), os.dup2(100, 3), os.dup2(101, 4)

        self.proc = subprocess.Popen([str(executable())] + LAUNCH_ARGS, preexec_fn=child, pass_fds=(3, 4),
                                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.close(r_in), os.close(w_out)
        self.w, self.r, self.buf, self.next_id, self.events = w_in, r_out, b"", 0, []
        self.send("Playwright.enable")
        self.context = self.send("Playwright.createContext")["browserContextId"]

    def close(self):
        self.proc.kill()
        self.proc.wait()
        os.close(self.w), os.close(self.r)

    def recv(self):
        """Blocks for the next message; events go to `self.events`, replies are returned."""
        while b"\0" not in self.buf:
            chunk = os.read(self.r, 1 << 16)
            if not chunk:
                raise RuntimeError("WebKit closed the inspector pipe")
            self.buf += chunk
        raw, _, self.buf = self.buf.partition(b"\0")
        msg = json.loads(raw)
        if msg.get("method") == "Target.dispatchMessageFromTarget":
            msg = json.loads(msg["params"]["message"]) | {"targetId": msg["params"]["targetId"]}
        if "id" not in msg:
            self.events.append(msg)
            return None
        return msg

    def send(self, method, params=None, page_proxy=None, target=None):
        """A command to the browser, a page proxy (`pageProxyId`) or a page's Inspector target."""
        self.next_id += 1
        want = outer = self.next_id
        msg = {"id": want, "method": method, "params": params or {}}
        if target:  # the wrapper gets its own id, and its own reply
            self.next_id = outer = self.next_id + 1
            msg = {"id": outer, "method": "Target.sendMessageToTarget",
                   "params": {"targetId": target, "message": json.dumps(msg)}}
        if page_proxy:
            msg["pageProxyId"] = page_proxy
        os.write(self.w, json.dumps(msg).encode() + b"\0")
        while True:
            reply = self.recv()
            if reply and reply["id"] in (want, outer) and "error" in reply:
                raise RuntimeError(f"{method}: {reply['error']}")
            if reply and reply["id"] == want:
                return reply.get("result", {})

    def wait_event(self, method, deadline, target=None):
        """Blocks until an event `method` (from `target`, if given) arrives; ones already received count."""
        seen = 0
        while True:
            for e in self.events[seen:]:
                if e["method"] == method and target in (None, e.get("targetId")):
                    return e
            seen = len(self.events)
            if time.monotonic() > deadline:
                raise TimeoutError(f"no {method} after {WAIT_SECONDS}s")
            self.recv()

    def new_page(self, width, height):
        """A page of the given viewport, paused at about:blank; returns (proxy, target)."""
        self.events.clear()
        proxy = self.send("Playwright.createPage", {"browserContextId": self.context})["pageProxyId"]
        target = self.wait_event("Target.targetCreated", time.monotonic() + WAIT_SECONDS)["params"]["targetInfo"]["targetId"]
        self.send("Emulation.setDeviceMetricsOverride", {"width": width, "height": height, "fixedLayout": False,
                                                         "deviceScaleFactor": 1}, page_proxy=proxy)
        return proxy, target

    def enable(self, proxy, target, timeline):
        self.send("Page.enable", page_proxy=proxy, target=target)
        self.send("Runtime.enable", page_proxy=proxy, target=target)
        self.send("Page.setBootstrapScript", {"source": BOOTSTRAP_JS}, page_proxy=proxy, target=target)
        if timeline:
            self.send("Timeline.enable", page_proxy=proxy, target=target)
            self.send("Timeline.start", {"maxCallStackDepth": 0}, page_proxy=proxy, target=target)
        self.send("Target.resume", {"targetId": target}, page_proxy=proxy)

    def navigate(self, proxy, target, url, deadline, timeline=False):
        """Loads `url` in the paused page, following the process swap its COOP header always causes (the
        page continues as a new, paused Inspector target); returns the new target once it fired `load`."""
        self.enable(proxy, target, timeline)
        frame = self.send("Page.getResourceTree", page_proxy=proxy, target=target)["frameTree"]["frame"]["id"]
        self.events.clear()
        self.send("Playwright.navigate", {"url": url, "pageProxyId": proxy, "frameId": frame})
        e = self.wait_event("Target.targetCreated", deadline)
        del self.events[:self.events.index(e) + 1]
        target = e["params"]["targetInfo"]["targetId"]
        self.enable(proxy, target, timeline)
        self.wait_event("Page.loadEventFired", deadline, target)
        return target

    def evaluate(self, js, proxy, target):
        r = self.send("Runtime.evaluate", {"expression": js, "returnByValue": True}, page_proxy=proxy, target=target)
        if r.get("wasThrown"):
            raise RuntimeError(f"evaluate: {r['result']}")
        return r["result"].get("value")


def records(events):
    """Every Timeline record, flattened: nested records (e.g. a Layout forced from a script) included."""
    out = []
    def walk(r):
        out.append(r)
        for c in r.get("children", []):
            walk(c)
    for e in events:
        if e["method"] == "Timeline.eventRecorded":
            walk(e["params"]["record"])
    return out


def run_webkit(case, iters, corpus_dir, width, height, root_rect_js, screenshot=None):
    """Samples like `run_chrome`'s: `style` and `layout` are the bootstrap script's timings of the reveal's
    forced style update and layout. With `screenshot` the last iteration also records the Timeline and
    reports its number of `Layout` records as `n_layouts`."""
    url = f"{isolated_server(corpus_dir)}/reveal/{case['file']}"
    browser, samples = Browser(), []
    try:
        for i in range(iters):
            verify = screenshot and i == iters - 1
            proxy, target = browser.new_page(width, height)
            deadline = time.monotonic() + WAIT_SECONDS
            target = browser.navigate(proxy, target, url, deadline, timeline=verify)
            while not browser.evaluate(REVEALED_JS, proxy, target):
                if time.monotonic() > deadline:
                    raise TimeoutError(f"{case['file']}: not revealed after {WAIT_SECONDS}s")
                time.sleep(0.005)
            browser.evaluate("document.body.offsetHeight", proxy, target)
            t = browser.evaluate("window.__lb", proxy, target)
            s = {"style": round(t["style"] * 1e6), "layout": round(t["layout"] * 1e6), "style+layout": round(t["total"] * 1e6),
                 "root": browser.evaluate(root_rect_js, proxy, target)}
            if verify:
                browser.send("Timeline.stop", page_proxy=proxy, target=target)
                s["n_layouts"] = sum(r["type"] == "Layout" for r in records(browser.events))
                png = browser.send("Page.snapshotRect", {"x": 0, "y": 0, "width": width, "height": height,
                                                         "coordinateSystem": "Viewport"}, page_proxy=proxy, target=target)["dataURL"]
                Path(screenshot).write_bytes(base64.b64decode(png.split(",", 1)[1]))
                s["boxes"] = [tuple(b) for b in browser.evaluate(
                    "[...document.querySelectorAll('#cb div, #cb p, #cb h3')].map(e=>{const r=e.getBoundingClientRect();return [r.x,r.y,r.width,r.height]})", proxy, target)]
                s["fonts"] = browser.evaluate("[...document.fonts].map(f=>f.status).join(',')", proxy, target)
            samples.append(s)
            browser.send("Playwright.closePage", {"pageProxyId": proxy})
    finally:
        browser.close()
    return samples
