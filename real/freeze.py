#!/usr/bin/env python3
"""Freezes saved web pages into self-contained, script-free, network-free HTML for the `real/`
corpus, so that every engine does exactly the same work on them.

    real/freeze.py fetch  [page ...]   # wget -p -k -E -H into real/raw/<page>/ (not committed)
    real/freeze.py freeze [page ...]   # real/raw/<page>/ -> real/<page>/index.html, placeholders,
                                       # real/manifest.tsv (name, dir, nodes, viewports)

Rules applied to every page (per-page rules are in PAGES[...]["rules"], see the bottom):
- `<script>`, `<noscript>`, `<template>`, inline `on*` handlers, every `<link>` (screen/all
  stylesheets are inlined into `<style>` first; print and dark-scheme sheets are dropped), `<meta http-equiv>`, `<base>`, comments and `srcset`/`sizes` go.
- `<img>`, `<picture>`, `<video>`, `<iframe>`, `<canvas>`, `<object>`, `<embed>` and inline `<svg>`
  become `<img>` placeholders of the same natural size (`ph/WxH.png`, a flat grey PNG), keeping
  the element's `width`/`height` attributes (filled in from the saved file when missing), id,
  class and style, so CSS sizing (`max-width:100%; height:auto`) still resolves the same way.
  `<audio>` is removed (its controls have no common size across engines).
- CSS: `@import` and `@font-face` are dropped, every other `url()` becomes `none` (no background
  images, masks or cursors), `text-rendering`, `scrollbar-gutter`, `transform`
  (and `translate`/`rotate`/`scale`) and `animation` declarations go, and every `font-family` / `font`
  shorthand is rewritten to "LB Sans" (or "LB Mono" when it named a monospace family), the DejaVu
  faces shipped in `fonts/`; `svg` type selectors become `img.lb-svg` to follow the replacement.
  The page gets `html{text-rendering:geometricPrecision}` (Chrome otherwise rounds glyph advances
  to whole pixels), the `@font-face` rules pointing at `../../fonts/` (same relative path in
  `real/` and in `corpus/real/`) and lowest-specificity `font-family` defaults for `html` and
  `pre`/`code`, so that elements the page leaves in the UA default font (serif, monospace) do not
  fall back to system fonts, which differ per engine (Blitz is built without any).
- `<input>` becomes an inline-block `<span class="lb-input">` (hidden inputs are removed; engines
  draw form controls with different UA padding and borders); `<select>`/`<textarea>` likewise.
- A closed `<details>` keeps only its `<summary>`, so engines without `<details>` agree.
- `<body>` gets `id="cb"` (the reveal script in run.py toggles `#cb`), its `style` attribute is
  moved into a rule.
"""
import io, os, re, shutil, struct, subprocess, sys, zlib
from pathlib import Path

from bs4 import BeautifulSoup, Comment, Doctype

REAL = Path(__file__).resolve().parent
RAW = REAL / "raw"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"

MONO_RE = re.compile(r"mono|courier|consolas|menlo|monaco|code|ui-monospace", re.I)
FONT_FACES = """@font-face{font-family:"LB Sans";font-weight:normal;font-style:normal;src:url(../../fonts/DejaVuSans.ttf)}
@font-face{font-family:"LB Sans";font-weight:bold;font-style:normal;src:url(../../fonts/DejaVuSans-Bold.ttf)}
@font-face{font-family:"LB Sans";font-weight:normal;font-style:italic;src:url(../../fonts/DejaVuSans-Oblique.ttf)}
@font-face{font-family:"LB Sans";font-weight:bold;font-style:italic;src:url(../../fonts/DejaVuSans-BoldOblique.ttf)}
@font-face{font-family:"LB Mono";font-weight:normal;font-style:normal;src:url(../../fonts/DejaVuSansMono.ttf)}
@font-face{font-family:"LB Mono";font-weight:bold;font-style:normal;src:url(../../fonts/DejaVuSansMono-Bold.ttf)}
html{text-rendering:geometricPrecision;font-family:"LB Sans"}
pre,code,kbd,samp,tt{font-family:"LB Mono"}
.lb-input{display:inline-block;box-sizing:border-box;width:170px;height:21px;border:1px solid #767676;vertical-align:middle}
"""
REPLACED = ["img", "picture", "video", "iframe", "canvas", "object", "embed", "svg"]


# ---- CSS ----

def font_shorthand(value):
    """`font: italic bold 14px/1.5 Arial, sans-serif` -> the same with the family replaced. The
    family starts after the size (the first token starting with a digit or `.`); system keywords
    (`font: menu`) and `inherit` have no family and are left alone."""
    important = ""
    if "!" in value:
        value, important = value.split("!", 1)
        important = "!" + important
    tokens = value.split()
    for i, t in enumerate(tokens):
        if t[0].isdigit() or t[0] == ".":
            family = " ".join(tokens[i + 1:])
            return " ".join(tokens[:i + 1]) + " " + lb_family(family) + important
    return value + important


def lb_family(family):
    return '"LB Mono"' if MONO_RE.search(family) else '"LB Sans"'


def freeze_declarations(css):
    """Declaration-level rewrites shared by stylesheets and `style` attributes."""
    css = re.sub(r"url\(\s*(?:\"[^\"]*\"|'[^']*'|[^)]*)\)", "none", css)
    # text-rendering is set to geometricPrecision for the whole page; scrollbar-gutter reserves a
    # platform-dependent gutter (15px in Chrome, 0 in Firefox and Blitz); transforms do not affect
    # layout but skew the screenshot and getBoundingClientRect() comparisons; animations make the
    # result depend on timing
    css = re.sub(r"(?<![\w-])(?:text-rendering|scrollbar-gutter|transform|translate|rotate|scale|animation(?:-[a-z]+)*)\s*:[^;}]*;?", "", css)
    css = re.sub(r"(?<![\w-])font-family\s*:\s*([^;}!]+)", lambda m: "font-family:" + lb_family(m.group(1)), css)
    css = re.sub(r"(?<![\w-])font\s*:\s*([^;}]+)", lambda m: "font:" + font_shorthand(m.group(1)), css)
    return css


def freeze_css(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"@charset[^;]*;|@import[^;]*;|@namespace[^;]*;", "", css)
    css = re.sub(r"@font-face\s*\{[^}]*\}", "", css)
    css = freeze_declarations(css)
    # rule preludes (the text between the previous `{`, `}` or `;` and a `{`): `svg` type selectors
    css = re.sub(r"(?<=[{};])([^{};@]*?)\{",
                 lambda m: re.sub(r"(?<![\w.#\[-])svg(?![\w-])", "img.lb-svg", m.group(1)) + "{", "\n" + css)[1:]
    return css.strip()


# ---- images ----

def png_size(data):
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])


def image_size(path):
    """Natural size of a saved image file (PNG/JPEG/GIF/WebP via Pillow, SVG from its attributes)."""
    data = path.read_bytes()
    if b"<svg" in data[:2048]:
        head = data[:4096].decode("utf-8", "replace")
        w = re.search(r"<svg[^>]*\swidth=\"([\d.]+)(?:px)?\"", head)
        h = re.search(r"<svg[^>]*\sheight=\"([\d.]+)(?:px)?\"", head)
        if w and h:
            return round(float(w.group(1))), round(float(h.group(1)))
        vb = re.search(r"viewBox=\"[\d.\-]+[ ,]+[\d.\-]+[ ,]+([\d.]+)[ ,]+([\d.]+)\"", head)
        if vb:
            return round(float(vb.group(1))), round(float(vb.group(2)))
        return None
    try:
        from PIL import Image
        with Image.open(io.BytesIO(data)) as im:
            return im.size
    except Exception:
        return png_size(data)


def placeholder_png(w, h):
    """A flat #c8c8c8 PNG of w x h (one filter byte + 3 grey bytes per pixel, deflated)."""
    def chunk(tag, body):
        return struct.pack(">I", len(body)) + tag + body + struct.pack(">I", zlib.crc32(tag + body) & 0xffffffff)
    raw = (b"\0" + b"\xc8\xc8\xc8" * w) * h
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def attr_px(el, name):
    v = el.get(name)
    if v is None:
        return None
    m = re.match(r"\s*([\d.]+)\s*(px)?\s*$", str(v))
    return round(float(m.group(1))) if m else None


class Freezer:
    def __init__(self, page, raw_html, out_dir):
        self.page, self.raw_html, self.out = page, raw_html, out_dir
        self.placeholders = {}
        self.notes = {}

    def note(self, what):
        self.notes[what] = self.notes.get(what, 0) + 1

    def local(self, ref):
        """The saved file for a (wget-rewritten) reference, or None."""
        if not ref or ref.startswith(("data:", "#", "http:", "https:", "//")):
            return None
        ref = ref.split("#")[0]
        for cand in (ref, ref.replace("%3F", "?"), ref.replace("%3F", "?").split("?")[0]):
            p = (self.raw_html.parent / cand).resolve()
            if p.is_file():
                return p
        return None

    def placeholder(self, w, h):
        w, h = max(1, min(int(w), 4000)), max(1, min(int(h), 4000))
        name = f"ph/{w}x{h}.png"
        self.placeholders[name] = (w, h)
        return name

    def natural_size(self, el):
        w, h = attr_px(el, "width"), attr_px(el, "height")
        if el.name == "svg" and (w is None or h is None):
            vb = el.get("viewBox") or el.get("viewbox")
            if vb and len(vb.replace(",", " ").split()) == 4:
                vw, vh = (float(v) for v in vb.replace(",", " ").split()[2:])
                if w is not None:
                    return w, round(w * vh / vw)
                if h is not None:
                    return round(h * vw / vh), h
                return round(vw), round(vh)
        src = el.get("src") or el.get("data") or el.get("poster")
        if el.name == "picture":
            img = el.find("img")
            src = img.get("src") if img else None
        f = self.local(src)
        size = image_size(f) if f else None
        if size:
            fw, fh = size
            if w is not None and h is None:
                return w, round(w * fh / fw)
            if h is not None and w is None:
                return round(h * fw / fh), h
            if w is None:
                return fw, fh
        if w is not None and h is not None:
            return w, h
        if el.name in ("video", "iframe", "canvas", "object", "embed", "svg"):
            # the default size of a replaced element without an intrinsic one (CSS-sized icons)
            return (w or 300), (h or 150)
        return None

    def replace_with_placeholder(self, soup, el):
        size = self.natural_size(el)
        if size is None:
            self.note(f"<{el.name}> without a known size removed")
            el.decompose()
            return
        w, h = size
        img = soup.new_tag("img", src=self.placeholder(w, h))
        if el.name == "picture":
            inner = el.find("img")
            if inner is not None:
                el = inner
        for a in ("id", "class", "style", "width", "height", "alt", "title", "hidden"):
            if el.get(a) is not None:
                img[a] = el[a]
        if el.name == "svg" or img.get("width") is None or img.get("height") is None:
            # inline SVG with only a viewBox renders at 100% width in Chrome; an <img> with its
            # natural size does not, so give it explicit dimensions like the other replacements
            img["width"], img["height"] = str(w), str(h)
        if el.name == "svg":
            img["class"] = (el.get("class") or []) + ["lb-svg"]
        img["alt"] = ""
        self.note(f"<{el.name}> -> placeholder")
        el.replace_with(img) if el.parent else None

    def run(self, rules):
        soup = BeautifulSoup(self.raw_html.read_text(encoding="utf-8", errors="replace"), "html5lib")
        head, body = soup.head, soup.body

        for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
            c.extract()
        for t in soup.find_all(["script", "noscript", "template", "base", "audio"]):
            t.decompose()
        for t in soup.find_all("meta"):
            if t.get("http-equiv") or t.get("charset"):
                t.decompose()

        # stylesheets: inline the saved files, in document order, then freeze every <style>
        for link in soup.find_all("link"):
            rel = [r.lower() for r in (link.get("rel") or [])]
            media = (link.get("media") or "all").lower()
            # print / dark-scheme sheets never apply in the light-scheme screen rendering
            if "stylesheet" in rel and self.local(link.get("href")) and media in ("all", "screen"):
                style = soup.new_tag("style")
                style.string = self.local(link["href"]).read_text(encoding="utf-8", errors="replace")
                link.replace_with(style)
            else:
                link.decompose()
        for style in soup.find_all("style"):
            style.string = freeze_css(style.string or "")
        for el in soup.find_all(style=True):
            el["style"] = freeze_declarations(el["style"])
        for el in soup.find_all(True):
            for a in list(el.attrs):
                if a.startswith("on") or a in ("srcset", "sizes", "loading", "decoding", "fetchpriority"):
                    del el[a]

        rules(soup, self)

        for el in soup.find_all(REPLACED):
            if el.parent is not None and not el.find_parent(REPLACED):
                self.replace_with_placeholder(soup, el)
        for el in soup.find_all("source"):
            el.decompose()
        for el in soup.find_all(["input", "select", "textarea", "button"]):
            if el.name == "button":
                continue
            if el.name == "input" and el.get("type", "").lower() == "hidden":
                el.decompose()
                continue
            span = soup.new_tag("span")
            for a in ("id", "class", "style", "hidden", "type", "name"):
                if el.get(a) is not None:
                    span[a] = el[a]
            span["class"] = (el.get("class") or []) + ["lb-input"]
            if el.name == "input" and el.get("type", "text").lower() in ("checkbox", "radio"):
                span["style"] = (span.get("style") or "") + ";width:13px;height:13px"
            el.replace_with(span)
            self.note(f"<{el.name}> -> span.lb-input")
        for d in soup.find_all("details"):
            if d.get("open") is None:
                for child in list(d.children):
                    if getattr(child, "name", None) != "summary":
                        child.extract()
                self.note("closed <details> emptied")

        body["id"] = "cb"
        extra = ""
        if body.get("style"):
            extra = "body{" + body["style"] + "}"
            del body["style"]
        first = soup.new_tag("style")
        first.string = FONT_FACES + extra
        head.insert(0, first)
        head.insert(0, soup.new_tag("meta", charset="utf-8"))

        if self.out.exists():
            shutil.rmtree(self.out)
        (self.out / "ph").mkdir(parents=True)
        for name, (w, h) in self.placeholders.items():
            (self.out / name).write_bytes(placeholder_png(w, h))
        html = str(soup)
        html = html.replace("\u00a0", "&nbsp;")
        (self.out / "index.html").write_text(html, encoding="utf-8")
        nodes = len(body.find_all(True))
        return nodes


# ---- per-page rules: explicit, commented edits needed for the engines to agree ----

def remove(soup, selector, why):
    n = 0
    for el in soup.select(selector):
        el.decompose()
        n += 1
    return n


def wikipedia(soup, fz):
    pass


def noop(soup, fz):
    pass


PAGES = {
    # name: (url, saved html path under raw/<name>/, viewports, rules, licence)
    "wikipedia": dict(url="https://en.wikipedia.org/wiki/Barack_Obama", html="en.wikipedia.org/wiki/Barack_Obama.html",
                      viewports=["1280x800", "1024x800"], rules=wikipedia,
                      licence="CC BY-SA 4.0 (Wikipedia article text), Wikimedia Foundation"),
    "mdn": dict(url="https://developer.mozilla.org/en-US/docs/Web/CSS/display", html="developer.mozilla.org/en-US/docs/Web/CSS/display.html",
                viewports=["1280x800", "1024x800"], rules=noop, licence="CC BY-SA 2.5 (MDN content), Mozilla Contributors"),
    "rustdoc": dict(url="https://doc.rust-lang.org/std/vec/struct.Vec.html", html="doc.rust-lang.org/std/vec/struct.Vec.html",
                    viewports=["1280x800"], rules=noop, licence="MIT / Apache-2.0 (The Rust Project Developers)"),
    "css-flexbox-1": dict(url="https://www.w3.org/TR/css-flexbox-1/", html="www.w3.org/TR/css-flexbox-1/index.html",
                          viewports=["1280x800"], rules=noop, licence="W3C Document License (copying permitted), W3C"),
    "servo-org": dict(url="https://servo.org/", html="servo.org/index.html",
                      viewports=["1280x800", "1024x800"], rules=noop, licence="MPL-2.0 (servo/servo.org), The Servo Project"),
    "dioxuslabs-com": dict(url="https://dioxuslabs.com/", html="dioxuslabs.com/index.html",
                           viewports=["1280x800", "1024x800"], rules=noop, licence="MIT / Apache-2.0 (DioxusLabs/docsite)"),
    "bootstrap-dashboard": dict(url="https://getbootstrap.com/docs/5.3/examples/dashboard/", html="getbootstrap.com/docs/5.3/examples/dashboard/index.html",
                                viewports=["1280x800", "1024x800"], rules=noop, licence="MIT (twbs/bootstrap examples)"),
}


def fetch(names):
    for name in names:
        d = RAW / name
        d.mkdir(parents=True, exist_ok=True)
        # -e robots=off: Wikipedia's robots.txt disallows load.php, which serves its stylesheets
        subprocess.run(["wget", "-q", "-e", "robots=off", "-p", "-k", "-E", "-H", "-U", UA, "-P", str(d), PAGES[name]["url"]])
        print(name, "fetched" if (d / PAGES[name]["html"]).exists() else "FAILED")


def freeze(names):
    manifest = {}
    mf = REAL / "manifest.tsv"
    if mf.exists():
        for line in mf.read_text().splitlines():
            manifest[line.split("\t")[0]] = line
    for name in names:
        p = PAGES[name]
        fz = Freezer(name, RAW / name / p["html"], REAL / name)
        nodes = fz.run(p["rules"])
        size = sum(f.stat().st_size for f in (REAL / name).rglob("*") if f.is_file())
        manifest[name] = f"{name}\t{name}\t{nodes}\t{','.join(p['viewports'])}"
        print(f"{name}: {nodes} elements under body, {size / 1e6:.2f} MB")
        for k, v in sorted(fz.notes.items()):
            print(f"  {v:5d} {k}")
    mf.write_text("".join(manifest[n] + "\n" for n in PAGES if n in manifest))


if __name__ == "__main__":
    cmd, names = sys.argv[1], sys.argv[2:] or list(PAGES)
    {"fetch": fetch, "freeze": freeze}[cmd](names)
