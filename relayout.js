window.__lb = window.__lb || {};
(() => {
  const cb = document.getElementById('cb');
  const root = cb.tagName === 'BODY' ? cb : cb.firstElementChild;
  const all = [...cb.querySelectorAll('*')];
  const rendered = e => e.getClientRects().length > 0;
  // only elements with a box take part (real pages have display:none subtrees and <script>s whose mutation lays out
  // nothing), and leaves are the innermost block-level elements (no block-level element child): `width` on a
  // non-replaced inline changes no geometry, and Blitz gives inline elements no node layout to mutate.
  // Each element costs two layout queries (a reflow each in Servo), so the harness runs this once per engine and
  // page and hands later documents the result as indices into `cb.querySelectorAll('*')` (`init(selection)`).
  const select = () => {
    const block = new Map();
    const blockLevel = e => {
      let b = block.get(e);
      if (b === undefined) { b = rendered(e) && getComputedStyle(e).display !== 'inline'; block.set(e, b); }
      return b;
    };
    const leaves = [];
    all.forEach((e, i) => { if (blockLevel(e) && ![...e.children].some(blockLevel)) leaves.push(i); });
    const depth = e => { let d = 0; for (let p = e; p && p !== cb; p = p.parentElement) d++; return d; };
    const depths = leaves.map(i => depth(all[i]));
    const maxDepth = depths.reduce((a, b) => Math.max(a, b), 0);
    return { leaves, deepest: leaves.filter((_, k) => depths[k] === maxDepth), depth: maxDepth };
  };
  window.__lb.key = navigator.userAgent + ' ' + location.pathname;
  window.__lb.init = selection => {
    const sel = window.__lb.selection = selection || select();
    const leaves = sel.leaves.map(i => all[i]), deepest = sel.deepest.map(i => all[i]);
    // read every width first, then write: a read after a write forces a layout per element
    const widen = els => { const saved = els.map(e => e.style.width); const w = els.map(e => e.getBoundingClientRect().width); els.forEach((e, i) => { e.style.width = (w[i] + 1) + 'px'; }); return { undo: () => els.forEach((e, i) => { e.style.width = saved[i]; }), probe: els[els.length - 1] }; };
    const steps = {
      root_width: () => { const w = root.style.width, px = root.getBoundingClientRect().width; root.style.width = Math.round(px * 0.8) + 'px'; return { undo: () => { root.style.width = w; }, probe: root }; },
      leaf_1: () => widen([deepest[deepest.length >> 1]]),
      leaf_10pct: () => widen(leaves.filter((_, i) => i % 10 === 0)),
      leaf_all: () => widen(leaves),
      append: () => { const kids = [...root.children].filter(rendered); const n = Math.max(1, kids.length / 10 | 0); const clones = kids.slice(-n).map(c => c.cloneNode(true)); clones.forEach(c => root.appendChild(c)); return { undo: () => clones.forEach(c => c.remove()), probe: clones[0] }; },
    };
    let undo = null;
    const now = performance.now.bind(performance);
    window.__lb.steps = {};
    window.__lb.relayout = (name, phase) => {
      if (phase === 'apply') {
        performance.mark('lb:' + name + ':prepare'); const step = steps[name](); undo = step.undo; performance.mark('lb:' + name + ':start');
        // in-page timing for engines without a usable trace (WebKit): style flush, then layout. The style probe must be a
        // mutated element: WebKit's getComputedStyle only flushes style when the element itself needs a recalc.
        const t0 = now(); getComputedStyle(step.probe).display; const t1 = now(); document.body.offsetHeight; const t2 = now();
        performance.mark('lb:' + name + ':end');
        window.__lb.steps[name] = { style: t1 - t0, layout: t2 - t1, total: t2 - t0 };
      }
      else { undo(); undo = null; document.body.offsetHeight; }
      return { leaves: leaves.length, depth: sel.depth };
    };
  };
})();
