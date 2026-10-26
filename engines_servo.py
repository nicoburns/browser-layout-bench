"""Servo (servoshell) runner for run.py: one `servoshell --webdriver` process per round, driven over the
WebDriver HTTP endpoint with urllib. Every page gets a fresh window (`New Window`, sized with `Set Window
Rect`, which resizes the headless webview) that is closed once its reveal has been observed; a window
loaded with `about:blank` from the command line stays open so the process never runs out of windows.
Timings come from the Perfetto trace servoshell writes (`SERVO_TRACING`, parsed in run.py); this module
only records, per window, its WebDriver handle (the `webview_id` servo tags the trace's `handle_reflow`
spans with) and the wall-clock (CLOCK_REALTIME, the trace's clock) instants of the navigation, the observed
reveal and the close, which run.py uses to find the window's spans in the round's trace."""
import base64, json, os, socket, subprocess, time, urllib.error, urllib.request
from pathlib import Path

TRACING = "layout::layout_impl=trace,layout::flow::root=trace"
REVEALED_JS = "const cb=document.getElementById('cb');return !!cb&&cb.style.display!=='none'"
WAIT_SECONDS = int(os.environ.get("SERVO_WAIT_SECONDS", "600"))


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Browser:
    """One servoshell process and its WebDriver session. `cwd` is where servoshell writes servo.pftrace."""

    def __init__(self, servoshell, threads, cpus, cwd, width, height):
        self.port = free_port()
        cmd = [str(servoshell), "-z", f"--webdriver={self.port}", f"--window-size={width}x{height}",
               "--pref", f"layout_threads={threads}", "about:blank"]
        if cpus:
            cmd = ["taskset", "-c", cpus] + cmd
        # servoshell logs every WebDriver command at INFO on stdout
        self.proc = subprocess.Popen(cmd, cwd=cwd, env=dict(os.environ, SERVO_TRACING=TRACING),
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.time() + 60
        while True:
            try:
                self.request("GET", "/status")
                break
            except (urllib.error.URLError, ConnectionError):
                if self.proc.poll() is not None or time.time() > deadline:
                    self.proc.kill()
                    raise RuntimeError("servoshell did not start its WebDriver server")
                time.sleep(0.02)
        sid = self.request("POST", "/session", {"capabilities": {}})["sessionId"]
        self.session = f"/session/{sid}"
        self.blank = self.request("GET", self.session + "/window/handles")[0]

    def request(self, method, path, body=None):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}{path}", method=method,
                                     data=json.dumps(body).encode() if body is not None else None,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=WAIT_SECONDS) as r:
                return json.loads(r.read())["value"]
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"WebDriver {method} {path}: {e.code} {e.read().decode()[:300]}") from None

    def js(self, script):
        return self.request("POST", self.session + "/execute/sync", {"script": script, "args": []})

    def load(self, url, width, height):
        """Opens a new window of the given viewport, navigates it to `url` and waits for the reveal.
        Returns the window's instants as a dict for run.py's trace lookup; the window stays current."""
        handle = self.request("POST", self.session + "/window/new", {"type": "window"})["handle"]
        self.request("POST", self.session + "/window", {"handle": handle})
        rect = self.request("POST", self.session + "/window/rect", {"width": width, "height": height})
        if (rect["width"], rect["height"]) != (width, height):
            raise RuntimeError(f"servoshell window is {rect['width']}x{rect['height']}, wanted {width}x{height}")
        nav = time.time_ns()
        self.request("POST", self.session + "/url", {"url": url})
        deadline = time.time() + WAIT_SECONDS
        while self.js(REVEALED_JS) is not True:
            if time.time() > deadline:
                raise RuntimeError(f"{url}: not revealed after {WAIT_SECONDS} s")
            time.sleep(0.005)
        return dict(url=url, handle=handle, nav=nav, revealed=time.time_ns(), closed=None)

    def screenshot(self, path):
        Path(path).write_bytes(base64.b64decode(self.request("GET", self.session + "/screenshot")))

    def close(self, window):
        """Closes the current window and makes the blank one current again (a session whose window
        was just closed has no current window, so `New Window` would fail)."""
        self.request("DELETE", self.session + "/window")
        window["closed"] = time.time_ns()
        self.request("POST", self.session + "/window", {"handle": self.blank})

    def quit(self):
        # Spans are written to the trace file as they close, so killing the process loses none; a
        # servoshell with --webdriver does not exit on SIGTERM or when its last window closes.
        try:
            self.request("DELETE", self.session)
        except Exception:
            pass
        self.proc.kill()
        self.proc.wait()
