window.__lb = window.__lb || {};
(() => {
  const cb = document.getElementById('cb');
  const root = cb.tagName === 'BODY' ? cb : cb.firstElementChild;
  const leaves = [...cb.querySelectorAll('*')].filter(e => !e.firstElementChild);
  const depth = e => { let d = 0; for (let p = e; p && p !== cb; p = p.parentElement) d++; return d; };
  const maxDepth = Math.max(...leaves.map(depth));
  const deepest = leaves.filter(e => depth(e) === maxDepth);
  // read every width first, then write: a read after a write forces a layout per element
  const widen = els => { const saved = els.map(e => e.style.width); const w = els.map(e => e.getBoundingClientRect().width); els.forEach((e, i) => { e.style.width = (w[i] + 1) + 'px'; }); return () => els.forEach((e, i) => { e.style.width = saved[i]; }); };
  const steps = {
    root_width: () => { const w = root.style.width, px = root.getBoundingClientRect().width; root.style.width = Math.round(px * 0.8) + 'px'; return () => { root.style.width = w; }; },
    leaf_1: () => widen([deepest[deepest.length >> 1]]),
    leaf_10pct: () => widen(leaves.filter((_, i) => i % 10 === 0)),
    leaf_all: () => widen(leaves),
    append: () => { const n = Math.max(1, root.children.length / 10 | 0); const clones = [...root.children].slice(-n).map(c => c.cloneNode(true)); clones.forEach(c => root.appendChild(c)); return () => clones.forEach(c => c.remove()); },
  };
  let undo = null;
  const now = performance.now.bind(performance);
  window.__lb.steps = {};
  window.__lb.relayout = (name, phase) => {
    if (phase === 'apply') {
      performance.mark('lb:' + name + ':prepare'); undo = steps[name](); performance.mark('lb:' + name + ':start');
      // in-page timing for engines without a usable trace (WebKit): style flush, then layout
      const t0 = now(); getComputedStyle(root).display; const t1 = now(); document.body.offsetHeight; const t2 = now();
      performance.mark('lb:' + name + ':end');
      window.__lb.steps[name] = { style: t1 - t0, layout: t2 - t1, total: t2 - t0 };
    }
    else { undo(); undo = null; document.body.offsetHeight; }
    return { leaves: leaves.length, depth: maxDepth };
  };
})();
