#!/usr/bin/env python3
"""Run the instrumented Blitz runner (`--cache-stats`, Taffy patched with `patches/taffy-cache-occupancy.patch`)
over the corpus and write one JSON per case to cache-occupancy/raw/.

usage: collect.py <runner-binary> [case-substring...]
"""
import json, re, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "corpus"
RAW = Path(__file__).resolve().parent / "raw"


def cases():
    for line in (CORPUS / "manifest.tsv").read_text().splitlines():
        name, file, w, h, nodes, engine, *rest = line.split("\t")
        vw, vh = (int(v) for v in rest[0].split("x")) if rest else (1280, 800)
        yield dict(name=name, file=file, nodes=int(nodes), width=vw, height=vh)


def parse(out):
    steps, sizes, hash_, root = {}, None, None, None
    for line in out.splitlines():
        kv = dict(re.findall(r"(\w+)=(\S+)", line))
        if line.startswith("CACHESIZES"):
            sizes = {k: int(v) for k, v in kv.items()}
        elif line.startswith("CACHECTR"):
            step = steps.setdefault(kv.pop("step"), {"hist": []})
            step["counters"] = {k: int(v) for k, v in kv.items()}
        elif line.startswith("CACHENODES"):
            steps[kv["step"]]["nodes"] = int(kv["nodes"])
        elif line.startswith("CACHEHIST"):
            m = {int(a): int(b) for a, b in (x.split(":") for x in kv["m"].split(","))} if kv["m"] else {}
            steps[kv["step"]]["hist"].append(dict(kind=kv["kind"], final=kv["final"], n=int(kv["n"]), m=m))
        elif line.startswith("HASH"):
            hash_ = line.split()[1]
        elif line.startswith("ROOT"):
            root = line.split()[1]
    return dict(sizes=sizes, steps=steps, hash=hash_, root=root)


def main():
    binary = Path(sys.argv[1])
    filters = sys.argv[2:]
    RAW.mkdir(exist_ok=True)
    for c in cases():
        if filters and not any(f in c["name"] for f in filters):
            continue
        cmd = [str(binary), str(CORPUS / c["file"]), "--width", str(c["width"]), "--height", str(c["height"]),
               "--iters", "1", "--hash", "--relayout", "--cache-stats"]
        t = time.time()
        out = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout
        data = parse(out)
        data.update(case=c, wall_s=round(time.time() - t, 2))
        (RAW / (c["name"].replace("/", "_") + ".json")).write_text(json.dumps(data, indent=1))
        print(f"{c['name']}\t{data['hash']}\t{data['root']}\t{data['wall_s']}s", flush=True)


if __name__ == "__main__":
    main()
