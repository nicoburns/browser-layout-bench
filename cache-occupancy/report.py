#!/usr/bin/env python3
"""Summarise cache-occupancy/raw/*.json: per-page table (occupancy.csv, report tables on stdout),
full histograms (histograms.csv) and memory models (memory.csv).

usage: report.py [case-substring...]
"""
import csv, json, statistics, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
STEPS = ["initial", "root_width", "leaf_1", "leaf_10pct", "leaf_all", "append"]
# steps whose node set is the original document (append adds clones that are removed afterwards)
STEADY_STEPS = ["initial", "root_width", "leaf_1", "leaf_10pct", "leaf_all"]
ORDER = ["real/", "pangui/", "flex/", "grid/", "text/"]


def load(filters):
    pages = []
    for f in sorted(RAW.glob("*.json")):
        d = json.loads(f.read_text())
        name = d["case"]["name"]
        if filters and not any(x in name for x in filters):
            continue
        pages.append(d)
    pages.sort(key=lambda d: (next((i for i, p in enumerate(ORDER) if d["case"]["name"].startswith(p)), 9), d["case"]["name"]))
    return pages


def quantile(values, q):
    if not values:
        return 0
    values = sorted(values)
    i = min(len(values) - 1, int(round(q * (len(values) - 1))))
    return values[i]


def step_summary(d, step):
    """Counts over all DOM nodes for one snapshot"""
    s = d["steps"][step]
    sizes = d["sizes"]
    nodes = s["nodes"]
    owners = owners_any = final_pop = final_only = with_measure = 0
    elements = 0
    slots = []  # populated measure slots, one value per cache owner
    slot_hist = [0] * 10
    by_kind = {}
    for h in s["hist"]:
        kind = h["kind"]
        if kind not in ("text", "comment", "document"):
            elements += h["n"]
        k = by_kind.setdefault(kind, dict(nodes=0, owners=0, any=0, final=0, slots=[0] * 10))
        k["nodes"] += h["n"]
        if h["final"] == "-":
            continue
        owners += h["n"]
        k["owners"] += h["n"]
        fin = h["final"] == "1"
        for m, c in h["m"].items():
            m = int(m)
            slots.extend([m] * c)
            slot_hist[m] += c
            k["slots"][m] += c
            if fin:
                final_pop += c
                k["final"] += c
                if m == 0:
                    final_only += c
            if fin or m > 0:
                owners_any += c
                k["any"] += c
            if m > 0:
                with_measure += c
    return dict(
        step=step, nodes=nodes, elements=elements, owners=owners, owners_any=owners_any, owners_empty=owners - owners_any,
        final_populated=final_pop, final_only=final_only, with_measure=with_measure,
        slots_mean=statistics.fmean(slots) if slots else 0, slots_median=statistics.median(slots) if slots else 0,
        slots_p90=quantile(slots, 0.9), slots_max=max(slots) if slots else 0, slots_total=sum(slots), slot_hist=slot_hist,
        by_kind=by_kind, counters=s["counters"], sizes=sizes,
    )


def memory_models(summary):
    """Bytes of cache storage under the eager layout and the lazy layouts described in the report"""
    z = summary["sizes"]
    cache, final_e, measure_e = z["cache"], z["final_entry"], z["measure_entry"]
    owners, any_, with_measure, total = summary["owners"], summary["owners_any"], summary["with_measure"], summary["slots_total"]
    hist = summary["slot_hist"]
    # inline part of a lazy cache: final entry + pointer to the measure array + bookkeeping (u16/u8/bool/mode) padded to 8
    inline = final_e + 8 + 8
    return {
        "eager": owners * cache,
        # whole Cache boxed on first store (8 B Option<Box<Cache>> per owner)
        "lazy_box_cache": owners * 8 + any_ * cache,
        # final entry inline, measure array boxed as a whole (9 slots) on the first measure store
        "lazy_box_measures": owners * inline + with_measure * 9 * measure_e,
        # final entry inline, measure array exactly as large as populated (lower bound; ignores allocator rounding)
        "lazy_exact": owners * inline + total * measure_e,
        # final entry inline, SmallVec-like 1 inline slot, spill to a boxed 9-slot array above 1
        "lazy_small1": owners * (inline + 1 * measure_e) + sum(hist[2:]) * 9 * measure_e,
        # 2 inline slots
        "lazy_small2": owners * (inline + 2 * measure_e) + sum(hist[3:]) * 9 * measure_e,
        # 3 inline slots
        "lazy_small3": owners * (inline + 3 * measure_e) + sum(hist[4:]) * 9 * measure_e,
    }


def node_memory(summary):
    """Node bytes we can account for: Node + boxed ElementData + boxed LayoutData (not strings, styles, Parley layouts)"""
    z = summary["sizes"]
    return summary["nodes"] * z["node"] + summary["elements"] * z["element_data"] + summary["owners"] * z["layout_data"]


def fmt_bytes(b):
    return f"{b / 1024:.0f} KB" if b < 10 * 1024 * 1024 else f"{b / 1024 / 1024:.1f} MB"


def main():
    pages = load(sys.argv[1:])
    rows, hist_rows, mem_rows = [], [], []
    md = []
    md.append("| page | DOM nodes | cache owners | owners with ≥1 entry (initial / steady) | final only | measure slots mean / median / p90 / max (steady) | evictions (initial / Σ relayout) | cache bytes today | lazy: box measures | lazy: exact | saving vs today | saving vs node mem |")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for d in pages:
        name = d["case"]["name"]
        sums = {step: step_summary(d, step) for step in STEPS if step in d["steps"]}
        for step, s in sums.items():
            m = memory_models(s)
            rows.append(dict(page=name, step=step, nodes=s["nodes"], elements=s["elements"], cache_owners=s["owners"],
                             owners_any_entry=s["owners_any"], owners_empty=s["owners_empty"], final_populated=s["final_populated"],
                             final_only=s["final_only"], with_measure=s["with_measure"], slots_mean=round(s["slots_mean"], 3),
                             slots_median=s["slots_median"], slots_p90=s["slots_p90"], slots_max=s["slots_max"], slots_total=s["slots_total"],
                             **{f"m{i}": c for i, c in enumerate(s["slot_hist"])}, **s["counters"], **m, node_memory=node_memory(s)))
            for kind, k in sorted(s["by_kind"].items()):
                hist_rows.append(dict(page=name, step=step, kind=kind, nodes=k["nodes"], cache_owners=k["owners"], any_entry=k["any"],
                                      final_populated=k["final"], **{f"m{i}": c for i, c in enumerate(k["slots"])}))
        # steady state: the most-populated snapshot of the original node set (lazy allocations never shrink)
        steady = max((sums[s] for s in STEADY_STEPS if s in sums), key=lambda s: (s["owners_any"], s["slots_total"]))
        init = sums["initial"]
        peak_mem = {k: max(memory_models(sums[s])[k] for s in STEADY_STEPS if s in sums) for k in memory_models(init)}
        mem_rows.append(dict(page=name, nodes=init["nodes"], cache_owners=init["owners"], node_memory=node_memory(init), **peak_mem))
        ev_init = init["counters"]["measure_evictions"]
        ev_relayout = sum(sums[s]["counters"]["measure_evictions"] for s in STEPS[1:] if s in sums)
        saving = peak_mem["eager"] - peak_mem["lazy_box_measures"]
        md.append(f"| {name} | {init['nodes']} | {init['owners']} ({init['owners'] / init['nodes']:.0%}) | {init['owners_any']} / {steady['owners_any']} ({steady['owners_any'] / max(init['owners'], 1):.0%} of owners) | {steady['final_only']} | {steady['slots_mean']:.2f} / {steady['slots_median']:.0f} / {steady['slots_p90']} / {steady['slots_max']} | {ev_init} / {ev_relayout} | {fmt_bytes(peak_mem['eager'])} | {fmt_bytes(peak_mem['lazy_box_measures'])} | {fmt_bytes(peak_mem['lazy_exact'])} | {fmt_bytes(saving)} ({saving / max(peak_mem['eager'], 1):.0%}) | {saving / node_memory(init):.1%} |")
    with open(HERE / "occupancy.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    with open(HERE / "histograms.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(hist_rows[0].keys()))
        w.writeheader(); w.writerows(hist_rows)
    with open(HERE / "memory.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(mem_rows[0].keys()))
        w.writeheader(); w.writerows(mem_rows)
    print("\n".join(md))


if __name__ == "__main__":
    main()
