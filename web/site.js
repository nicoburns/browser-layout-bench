// Draws the result tables and charts of the static site from window.DATA (written by pages.py).
// State (table, statistic, unit, scale, hidden engines) is kept in the URL hash and localStorage.
"use strict";
(function () {
  const D = window.DATA;
  const SVGNS = "http://www.w3.org/2000/svg";
  const UNITS = { ms: "ms", chrome: "× Chrome", fastest: "× fastest", node: "per node" };
  const DEFAULTS = { v: "table", g: "", t: D.tables.findIndex(t => t.title.startsWith("Box construction")), s: "min", u: "ms", x: "lin", off: [] };
  const caseId = name => name.replace(/[^\w]+/g, "-");
  const unequal = new Map(D.unequal.map(u => [u.case + "|" + u.engine, u.note]));

  // ---- state ----
  function loadState() {
    let st = Object.assign({}, DEFAULTS);
    try { Object.assign(st, JSON.parse(localStorage.getItem("layout-bench") || "{}")); } catch (e) { /* ignore */ }
    const h = new URLSearchParams(location.hash.includes("=") ? location.hash.slice(1) : "");
    if (h.has("t")) st.t = +h.get("t");
    for (const k of ["v", "g", "s", "u", "x"]) if (h.has(k)) st[k] = h.get(k);
    const anchored = D.cases.find(c => "#" + caseId(c.name) === location.hash);
    if (anchored) Object.assign(st, { g: anchored.suite, v: "charts" });
    if (st.v !== "charts") st.v = "table";
    if (st.x !== "log") st.x = "lin";
    if (!D.suites.some(s => s.name === st.g)) st.g = "";
    if (h.has("off")) st.off = h.get("off").split(",").filter(Boolean);
    if (!(st.t >= 0 && st.t < D.tables.length)) st.t = DEFAULTS.t;
    return st;
  }
  const state = loadState();
  // The hash carries the state only after a control change, so case anchors (#flex-wide-1000) keep working.
  function saveState(toHash) {
    localStorage.setItem("layout-bench", JSON.stringify(state));
    if (!toHash) return;
    const h = new URLSearchParams({ v: state.v, g: state.g, t: state.t, s: state.s, u: state.u });
    if (state.v === "charts") h.set("x", state.x);
    if (state.off.length) h.set("off", state.off.join(","));
    history.replaceState(null, "", "#" + h.toString());
  }

  // ---- numbers ----
  function samples(c, engine, metric) {
    const e = c.engines[engine];
    if (!e) return [];
    const k = e.metrics.indexOf(metric);
    if (k < 0) return [];
    return e.samples.map((row, i) => ({ v: row[k], i })).filter(s => s.v != null).sort((a, b) => a.v - b.v);
  }
  function quantile(sorted, q) {
    if (!sorted.length) return null;
    const pos = (sorted.length - 1) * q, lo = Math.floor(pos), hi = Math.ceil(pos);
    return sorted[lo] + (sorted[hi] - sorted[lo]) * (pos - lo);
  }
  // One engine column of one case: statistic value, spread and the sample whose stages are stacked.
  function cell(c, col) {
    const s = samples(c, col.engine, col.metric);
    if (!s.length) return null;
    const vals = s.map(x => x.v);
    const median = quantile(vals, 0.5);
    const pick = state.s === "median" ? s[Math.floor((s.length - 1) / 2)] : s[0];
    return {
      col, value: state.s === "median" ? median : vals[0], vals, min: vals[0], max: vals[vals.length - 1], median,
      q1: quantile(vals, 0.25), q3: quantile(vals, 0.75), sample: pick.i,
      normalized: c.engines[col.engine].normalized, unequal: unequal.get(c.name + "|" + col.engine),
    };
  }
  function stages(c, cl) {
    const spec = D.stages[cl.col.metric];
    if (!spec) return [];
    const e = c.engines[cl.col.engine], row = e.samples[cl.sample];
    const parts = [];
    for (const [key, label] of spec) {
      const k = e.metrics.indexOf(key);
      if (k >= 0 && row[k] != null) parts.push([label, row[k]]);
    }
    const total = row[e.metrics.indexOf(cl.col.metric)];
    const rest = total - parts.reduce((a, p) => a + p[1], 0);
    if (parts.length && rest > 1e-3) parts.push(["other", rest]);
    // Scale to the statistic (the median of an even sample count is not one sample).
    const f = total ? cl.value / total : 1;
    return parts.map(([l, v]) => [l, v * f]);
  }
  const visible = cols => cols.filter(col => !state.off.includes(col.engine) && D.engines[col.engine]);
  // Row context: every visible column's cell plus the references the units divide by.
  function row(c, cols) {
    const cells = cols.map(col => cell(c, col));
    const contenders = cells.filter(x => x && x.col.engine !== "taffy" && !x.unequal);
    const fastest = contenders.length ? Math.min(...contenders.map(x => x.value)) : null;
    const chromeCol = D.tables[state.t].columns.find(col => col.engine === "chrome");
    const chrome = chromeCol ? cell(c, chromeCol) : null;
    return { c, cells, fastest, chrome: chrome && chrome.value };
  }
  function inUnit(v, r) {
    if (v == null) return null;
    if (state.u === "chrome") return r.chrome ? v / r.chrome : null;
    if (state.u === "fastest") return r.fastest ? v / r.fastest : null;
    if (state.u === "node") return v * 1e6 / (r.c.nodes || 1); // ns per node
    return v;
  }
  function fmt(v) {
    if (v == null) return "-";
    return v >= 100 ? v.toFixed(0) : v >= 10 ? v.toFixed(1) : v >= 1 ? v.toFixed(2) : v >= 0.01 ? v.toFixed(3) : v.toPrecision(2);
  }
  function fmtNode(ns) {
    return ns >= 1e3 ? fmt(ns / 1e3) + " µs/node" : fmt(ns) + " ns/node";
  }
  function fmtUnit(v) {
    if (v == null) return "-";
    if (state.u === "node") return fmtNode(v);
    if (state.u === "ms") return fmt(v) + " ms";
    return v.toFixed(2) + "×";
  }
  // Secondary text next to the ms figure: the chosen ratio (× Chrome in ms mode, as in report.md).
  function secondary(v, r) {
    if (state.u === "node") return fmtNode(v * 1e6 / (r.c.nodes || 1));
    if (state.u === "fastest") return r.fastest ? (v / r.fastest).toFixed(2) + "× fastest" : "";
    return r.chrome ? (v / r.chrome).toFixed(2) + "× Chrome" : "";
  }
  function tip(c, cl) {
    const lines = [`${c.name} · ${D.engines[cl.col.engine].name}: ${cl.col.label.replace(/`/g, "")}`,
      `${cl.vals.length} samples: min ${fmt(cl.min)} · p25 ${fmt(cl.q1)} · median ${fmt(cl.median)} · p75 ${fmt(cl.q3)} · max ${fmt(cl.max)} ms`,
      `median ÷ min ${(cl.median / cl.min).toFixed(2)}`];
    if (cl.normalized) lines.push("† measured in a later run, Chrome-normalised (~10% uncertainty)");
    if (cl.unequal) lines.push("‡ not equal work: " + cl.unequal);
    return lines.join("\n");
  }

  // ---- DOM helpers ----
  function el(tag, attrs, ...kids) {
    const n = tag.startsWith("svg:") ? document.createElementNS(SVGNS, tag.slice(4)) : document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v == null || v === false) continue;
      if (k === "on") for (const [ev, f] of Object.entries(v)) n.addEventListener(ev, f);
      else n.setAttribute(k, v);
    }
    for (const k of kids.flat()) if (k != null) n.append(k);
    return n;
  }
  const svg = (tag, attrs, ...kids) => el("svg:" + tag, attrs, ...kids);
  // ---- scales ----
  function niceLinear(max) {
    const raw = max / 5, mag = Math.pow(10, Math.floor(Math.log10(raw)));
    const step = mag * [1, 2, 5, 10].find(f => raw / mag <= f * 1.5);
    const top = Math.ceil(max / step) * step;
    const ticks = [];
    for (let t = 0; t <= top + step / 2; t += step) ticks.push(+t.toPrecision(12));
    return { lo: 0, hi: top, ticks, f: v => v / top };
  }
  function niceLog(min, max) {
    const lo = Math.pow(10, Math.floor(Math.log10(min))), hi = Math.pow(10, Math.ceil(Math.log10(max)));
    const ticks = [];
    for (let d = lo; d <= hi * 1.001; d *= 10) for (const m of [1, 2, 5]) if (d * m >= lo && d * m <= hi * 1.001) ticks.push(+(d * m).toPrecision(6));
    const L = Math.log10(lo), H = Math.log10(hi);
    return { lo, hi, ticks, f: v => (Math.log10(Math.max(v, lo)) - L) / (H - L), log: true };
  }
  const isLog = () => state.x === "log";
  const unitAxisLabel = () => state.u === "node" ? "ns per node" : state.u === "ms" ? "ms" : UNITS[state.u];

  // ---- controls ----
  function renderControls() {
    const box = document.getElementById("controls");
    if (!box) return;
    const seg = (key, options, onPick) => el("span", { class: "seg", role: "group" }, Object.entries(options).map(([v, label]) =>
      el("button", { type: "button", "aria-pressed": String(state[key] === v), on: { click: () => { state[key] = v; onPick && onPick(); update(); } } }, label)));
    const inTable = new Set(D.tables[state.t].columns.map(c => c.engine));
    const chips = [...inTable].filter(e => D.engines[e]).map(e => {
      const info = D.engines[e], on = !state.off.includes(e);
      return el("button", { type: "button", class: "chip", style: `--c:${info.colour}`, "aria-pressed": String(on), title: e, on: { click: () => {
        state.off = on ? state.off.concat(e) : state.off.filter(x => x !== e); update(); } } }, el("i"), info.name);
    });
    const tableSel = el("select", { on: { change: ev => { state.t = +ev.target.value; update(); } } },
      D.tables.map((t, i) => el("option", { value: i, selected: i === state.t ? "" : null }, t.title)));
    const suiteSel = el("select", { on: { change: ev => { state.g = ev.target.value; update(); } } },
      el("option", { value: "", selected: state.g === "" ? "" : null }, `All suites (${D.cases.length} cases)`),
      D.suites.map(s => el("option", { value: s.name, selected: s.name === state.g ? "" : null },
        `${s.name}/ (${D.cases.filter(c => c.suite === s.name).length} cases)`)));
    const tabs = el("span", { class: "tabs", role: "tablist" }, Object.entries({ table: "Table", charts: "Charts" }).map(([v, label]) =>
      el("button", { type: "button", role: "tab", "aria-selected": String(state.v === v), on: { click: () => { state.v = v; update(); } } }, label)));
    box.replaceChildren(tabs,
      el("label", {}, "Suite", suiteSel),
      el("label", {}, "Comparison", tableSel),
      el("label", {}, "Statistic", seg("s", { min: "min", median: "median" })),
      el("label", {}, "Unit", seg("u", UNITS)),
      ...(state.v === "charts" ? [el("label", {}, "Scale", seg("x", { lin: "linear", log: "log" }))] : []),
      el("span", { class: "engines" }, chips,
        el("button", { type: "button", class: "chip", on: { click: () => { state.off = []; update(); } } }, "all")));
  }

  // Shows a case's chart: switches to the Charts tab, then scrolls to the chart once drawn.
  function openCase(ev, c) {
    ev.preventDefault();
    state.v = "charts";
    update();
    const target = document.getElementById(caseId(c.name));
    if (target) target.scrollIntoView();
  }
  const pickSuite = (ev, suite) => { ev.preventDefault(); state.g = suite; update(); window.scrollTo(0, 0); };

  // ---- table ----
  function renderTable(host, cases) {
    const table = D.tables[state.t], cols = visible(table.columns);
    const thead = el("thead", {}, el("tr", {}, el("th", { class: "case" }, "case"), el("th", {}, "nodes"),
      cols.map(col => {
        const [engine, ...phase] = col.label.split(" ");
        const norm = cases.some(c => c.engines[col.engine] && c.engines[col.engine].normalized);
        return el("th", { class: norm ? "norm" : null, title: col.engine + " · " + col.metric }, engine,
          el("small", {}, phase.join(" ").replace(/`/g, "").replace(/\+/g, " + ")));
      })));
    const tbody = el("tbody");
    let suite = null;
    for (const c of cases) {
      if (!state.g && c.suite !== suite) {
        const s = suite = c.suite;
        tbody.append(el("tr", { class: "group" }, el("th", { colspan: 2 }, el("a", { href: "#g=" + s, on: { click: ev => pickSuite(ev, s) } }, s + "/")),
          el("td", { colspan: cols.length })));
      }
      const r = row(c, cols);
      tbody.append(el("tr", {}, el("th", { class: "case" }, el("a", { href: "#" + caseId(c.name), on: { click: ev => openCase(ev, c) } },
        state.g ? c.name.slice(c.suite.length + 1) : c.name)),
        el("td", {}, c.nodes.toLocaleString("en")),
        r.cells.map(cl => {
          if (!cl) return el("td", { class: "na" }, "–");
          const best = cl.value === r.fastest && cl.col.engine !== "taffy" && !cl.unequal;
          return el("td", { class: best ? "best" : null, title: tip(c, cl) }, fmt(cl.value) + (cl.unequal ? " ‡" : ""), el("span", { class: "s" }, secondary(cl.value, r)));
        })));
    }
    const caption = el("p", { class: "legend" }, `${table.title}: ${state.s} of the samples in ms; second line ${state.u === "node" ? "time per node" : state.u === "fastest" ? "multiple of the fastest shown engine of the row" : "multiple of the Chrome column (1.00× = Chrome)"}; bold = fastest shown browser of the row (Taffy and ‡ unequal-work cells excluded); † = Chrome-normalised later run. Hover a cell for its sample spread.`);
    host.replaceChildren(el("h2", {}, table.title), caption, el("div", { class: "scroll" }, el("table", { class: "results" }, thead, tbody)));
  }

  // ---- per-case bar chart ----
  const W = 1000, LEFT = 300, RIGHT = 240, BAR = 16, GAP = 6;
  function caseChart(c) {
    const table = D.tables[state.t], cols = visible(table.columns);
    const r = row(c, cols);
    const bars = r.cells.filter(Boolean);
    if (!bars.length) return el("p", { class: "empty" }, "No samples for this comparison.");
    const conv = v => inUnit(v, r);
    const maxV = Math.max(...bars.map(b => conv(b.max)).filter(v => v != null));
    const minV = Math.min(...bars.map(b => conv(b.min)).filter(v => v != null));
    if (!isFinite(maxV)) return el("p", { class: "empty" }, "No Chrome value to divide by.");
    const log = isLog();
    const sc = log ? niceLog(minV, maxV) : niceLinear(maxV);
    const X = v => LEFT + sc.f(v) * (W - LEFT - RIGHT);
    const h = bars.length * (BAR + GAP) + GAP, top = 4, H = top + h + 22;
    const g = svg("svg", { class: "chart", viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": `${c.name}: ${table.title}` });
    for (const t of sc.ticks) {
      g.append(svg("line", { class: "grid", x1: X(t), x2: X(t), y1: top, y2: top + h }),
        svg("text", { class: "tick", x: X(t), y: top + h + 14, "text-anchor": "middle" }, fmt(t)));
    }
    g.append(svg("text", { class: "tick", x: W - RIGHT + 30, y: top + h + 14 }, unitAxisLabel()));
    if (state.u === "chrome" || state.u === "fastest") g.append(svg("line", { class: "ref", x1: X(1), x2: X(1), y1: top, y2: top + h }));
    bars.forEach((b, k) => {
      const info = D.engines[b.col.engine], y = top + GAP + k * (BAR + GAP), my = y + BAR / 2;
      const best = b.value === r.fastest && b.col.engine !== "taffy" && !b.unequal;
      const grp = svg("g", { class: "row" }, svg("title", {}, tip(c, b)));
      grp.append(svg("text", { class: "label" + (best ? " best" : ""), x: LEFT - 10, y: y + BAR - 4, "text-anchor": "end" },
        b.col.label.replace(/`/g, "") + (b.normalized ? " †" : "") + (b.unequal ? " ‡" : "")));
      const parts = log ? [] : stages(c, b);
      const x0 = X(sc.lo);
      if (parts.length) {
        let at = 0;
        parts.forEach(([stage, v], i) => {
          const a = X(conv(at)), z = X(Math.min(conv(at + v), conv(b.value)));
          const fill = stage === "other" ? "#8c959f" : info.colour;
          const op = stage === "other" ? 1 : [1, 0.7, 0.45, 0.3][Math.min(i, 3)];
          grp.append(svg("rect", { x: a, y, width: Math.max(z - a, 0), height: BAR, fill, opacity: op },
            svg("title", {}, `${stage}: ${fmt(v)} ms`)));
          if (z - a > 30) {
            const txt = z - a > 14 + 6 * (stage.length + 6) ? `${stage} ${fmt(v)}` : fmt(v);
            grp.append(svg("text", { class: "seg-label", x: (a + z) / 2, y: y + BAR - 4.5, "text-anchor": "middle",
              fill: i === 0 || stage === "other" ? "#fff" : "#1f2328", style: i === 0 || stage === "other" ? null : "fill:#1f2328" }, txt));
          }
          at += v;
        });
      } else {
        grp.append(svg("rect", { x: x0, y, width: Math.max(X(conv(b.value)) - x0, 1), height: BAR, fill: info.colour }));
      }
      const lo = X(conv(b.min)), hi = X(conv(b.max));
      grp.append(svg("line", { class: "whisker", x1: lo, x2: hi, y1: my, y2: my }),
        svg("line", { class: "iqr", x1: X(conv(b.q1)), x2: X(conv(b.q3)), y1: my, y2: my }),
        svg("line", { class: "whisker", x1: X(conv(b.median)), x2: X(conv(b.median)), y1: y + 1, y2: y + BAR - 1, "stroke-width": 2 }),
        svg("line", { class: "whisker", x1: hi, x2: hi, y1: y + 4, y2: y + BAR - 4 }));
      const ratio = state.u === "chrome" ? (r.chrome ? ` · ${(b.value / r.chrome).toFixed(2)}× Chrome` : "")
        : r.fastest ? ` · ${(b.value / r.fastest).toFixed(2)}× fastest` : "";
      grp.append(svg("text", { class: "value", x: hi + 6, y: y + BAR - 4 }, `${fmt(b.value)} ms`,
        svg("tspan", {}, `${ratio} · ${fmtNode(b.value * 1e6 / (c.nodes || 1))}`)));
      g.append(grp);
    });
    return g;
  }
  function renderCharts(host, cases) {
    const table = D.tables[state.t];
    const stacked = !isLog() && visible(table.columns).some(col => D.stages[col.metric]);
    let suite = null;
    host.replaceChildren(el("h2", {}, table.title),
      el("p", { class: "legend" }, `Bar = ${state.s} of the samples, x axis in ${unitAxisLabel()} (${isLog() ? "log; stacks are drawn as plain bars" : "linear"}, per case); whisker = all samples (thick: p25–p75, tick: median). ` +
        (stacked ? "Composite bars are stacked by the stages the engine records (solid → faint, pipeline order; grey = rest of the span). " : "") +
        `Label: ms · multiple of ${state.u === "chrome" ? "the Chrome bar" : "the fastest shown browser (bold)"} · time per node.`),
      ...cases.flatMap(c => {
        const heading = !state.g && c.suite !== suite ? el("h2", { class: "suite" }, el("code", {}, (suite = c.suite) + "/")) : null;
        return [heading, el("article", { id: caseId(c.name) },
          el("h3", {}, el("code", {}, c.name), " ", el("span", { class: "muted" }, c.nodes.toLocaleString("en") + " nodes")),
          c.note ? el("p", { class: "caveat" }, c.note) : null,
          caseChart(c))];
      }));
  }

  const shownCases = () => state.g ? D.cases.filter(c => c.suite === state.g) : D.cases;

  function update(initial) {
    saveState(!initial);
    renderControls();
    const sum = document.getElementById("summary");
    const s = D.suites.find(x => x.name === state.g);
    sum.replaceChildren(s ? el("p", {}, el("strong", {}, el("code", {}, s.name + "/")), " " + s.blurb + " ",
      el("a", { href: "#g=", on: { click: ev => pickSuite(ev, "") } }, "All suites")) : "");
    const t = document.getElementById("table"), ch = document.getElementById("charts");
    t.hidden = state.v !== "table";
    ch.hidden = state.v !== "charts";
    if (state.v === "table") renderTable(t, shownCases());
    else renderCharts(ch, shownCases());
  }
  if (document.getElementById("controls")) {
    update(true);
    const target = !location.hash.includes("=") && location.hash.length > 1 && document.getElementById(location.hash.slice(1));
    if (target) target.scrollIntoView();
  }
})();
