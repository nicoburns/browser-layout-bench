#!/usr/bin/env python3
"""Compare two runs of collect.py (two raw/ directories): layout hashes, cache misses and evictions per page."""
import json
import sys
from pathlib import Path

STEPS = ["initial", "root_width", "leaf_1", "leaf_10pct", "leaf_all", "append"]
KEYS = ["measure_misses", "layout_misses", "measure_evictions", "measure_stores"]


def load(d):
    return {p.stem: json.loads(p.read_text()) for p in sorted(Path(d).glob("*.json"))}


def main():
    a, b = load(sys.argv[1]), load(sys.argv[2])
    tot = {k: [0, 0] for k in KEYS}
    print("| page | hash | " + " | ".join(f"{k} A / B" for k in KEYS) + " | slots A / B (initial) |")
    print("|---|---|" + "---:|" * (len(KEYS) + 1))
    for name in a:
        if name not in b:
            continue
        ra, rb = a[name], b[name]
        same = "same" if ra["hash"] == rb["hash"] else "DIFF"
        cells = []
        for k in KEYS:
            sa = sum(ra["steps"][s]["counters"][k] for s in STEPS if s in ra["steps"])
            sb = sum(rb["steps"][s]["counters"][k] for s in STEPS if s in rb["steps"])
            tot[k][0] += sa
            tot[k][1] += sb
            cells.append(f"{sa} / {sb}" + (f" ({sb - sa:+d})" if sb != sa else ""))
        slots = lambda r: sum(int(i) * c for e in r["steps"]["initial"]["hist"] for i, c in e["m"].items())
        print(f"| {ra['case']['name']} | {same} | " + " | ".join(cells) + f" | {slots(ra)} / {slots(rb)} |")
    print("| **total** | | " + " | ".join(f"{v[0]} / {v[1]} ({v[1] - v[0]:+d})" for v in tot.values()) + " | |")
    print("sizes A:", a[next(iter(a))]["sizes"], "\nsizes B:", b[next(iter(b))]["sizes"])


if __name__ == "__main__":
    main()
