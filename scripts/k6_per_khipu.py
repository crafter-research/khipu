"""K6 per-khipu report required by prereg/K6.md (each khipu weighted equally)."""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import k6  # noqa: E402


def main():
    rows = []
    for p in sorted(k6.SUMS.glob("KH*.html")):
        n = p.stem
        if n in k6.EXCLUDED or not (k6.KFG / f"{n}.xlsx").exists():
            continue
        colors, starts = k6.pendants(n)
        rels = []
        for r in k6.relations(n):
            gp_all = [r["sum"]] + r["summands"]
            idx = [k6.to_pendant(gp, starts) for gp, _, _ in gp_all]
            if any(i is None or colors.get(i) != c for i, (_, _, c) in zip(idx, gp_all)):
                continue
            rels.append((idx[0], idx[1:]))
        if not rels:
            continue
        ids = sorted(colors)
        pos = {i: k for k, i in enumerate(ids)}
        base = np.array([colors[i] for i in ids], dtype=object)
        rel = [(pos[s], [pos[x] for x in xs]) for s, xs in rels]
        obs = np.mean([base[s] not in {base[x] for x in xs} for s, xs in rel])
        null = []
        for seed in range(1, k6.N_DRAWS + 1):
            c = base[np.random.default_rng(seed).permutation(len(base))]
            null.append(np.mean([c[s] not in {c[x] for x in xs} for s, xs in rel]))
        rows.append({"khipu": n, "relations": len(rel), "D": float(obs), "null_mean": float(np.mean(null))})
    d = np.array([r["D"] - r["null_mean"] for r in rows])
    rng = np.random.default_rng(0)
    boot = [rng.choice(d, len(d)).mean() for _ in range(2000)]
    res = {
        "khipus": len(rows),
        "mean_excess_D_per_khipu": float(d.mean()),
        "ci95_bootstrap_khipus": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
        "share_khipus_above_null": float((d > 0).mean()),
        "share_khipus_below_null": float((d < 0).mean()),
        "top5_by_relations": sorted(rows, key=lambda r: -r["relations"])[:5],
    }
    (k6.OUT / "k6_per_khipu.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
