# Blitz per-node Taffy layout cache occupancy

How many of the 1 + 9 cache slots of each Blitz node's Taffy `Cache` are populated after the initial
layout and after each relayout step, and what a lazily allocated cache would save. Report: `report.md`.

Revisions: Blitz `1c5265a8b3985e1ec05044a115b2ec6266e3fa91` (the harness pin), Taffy
`802e497b69689e1c93be2d16e9d53a973971bcb2` (Blitz's pin), instrumented with
`../patches/taffy-cache-occupancy.patch` (read-only accessors and counters, no behaviour change: the
runner's `--hash` is identical with and without it on every page).

## Reproduce

```sh
git clone https://github.com/DioxusLabs/taffy ../taffy-cache && git -C ../taffy-cache checkout 802e497b69689e1c93be2d16e9d53a973971bcb2
git -C ../taffy-cache apply "$PWD/patches/taffy-cache-occupancy.patch"
# point Blitz's Taffy at the patched checkout (don't commit this)
printf '\n[patch."https://github.com/DioxusLabs/taffy"]\ntaffy = { path = "../taffy-cache" }\n' >> Cargo.toml
cargo build --release -p layout-bench-blitz --features floats,writing-mode,cache-stats --target-dir target-instr
./run.py gen   # corpus/
cache-occupancy/collect.py target-instr/release/blitz-runner      # raw/<case>.json, one per page
cache-occupancy/report.py                                         # occupancy.csv, histograms.csv, memory.csv, table on stdout
```

`blitz-runner --cache-stats` (feature `cache-stats`) prints, after the initial `resolve()` and after
each relayout step's `resolve()`: `CACHESIZES` (`size_of` of `Cache`, its entries, `Node`,
`LayoutData`, `ElementData`), `CACHECTR` (Taffy cache hits/misses per `RunMode`, stores, in-place
updates, evictions = stores into a full measure array, uncacheable measure results, mode-change
clears, clears) accumulated during that resolve, and `CACHEHIST step=<s> kind=<k> final=<0|1|->
n=<nodes> m=<populated measure slots>:<count>,...` per node kind (`-` = the node has no `LayoutData`,
so no cache).

## Files

- `raw/*.json`: the runner's output per page, parsed.
- `occupancy.csv`: one row per page and step: node counts, cache owners, final-entry and measure-slot
  statistics (`m0..m9` = nodes by populated measure slots), counters, modelled bytes.
- `histograms.csv`: the same histograms per node kind.
- `memory.csv`: per page, bytes under each cache layout at the most-populated snapshot.
