"""K4: do values at a fixed position of seriated units trend upward? See prereg/K4.md."""

import json
import re
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
KFG = ROOT / "data/kfg"
OUT = ROOT / "results"
SEED = 0
N_SHUFFLE = 2000
SANTA = {"KH0323", "KH0324", "KH0325", "KH0326", "KH0327", "KH0328"}
GROUP_RE = re.compile(r"group of (\d+) pendants? \((\d+)(?:-(\d+))?\)")


def kendall_tau(x: np.ndarray, y: np.ndarray) -> float:
    n = len(x)
    s = 0
    for i in range(n):
        dx = np.sign(x[i + 1:] - x[i])
        dy = np.sign(y[i + 1:] - y[i])
        s += int((dx * dy).sum())
    ties_y = sum(c * (c - 1) // 2 for c in np.unique(y, return_counts=True)[1])
    pairs = n * (n - 1) // 2
    denom = np.sqrt(pairs * (pairs - ties_y))
    return s / denom if denom else np.nan


def seriated_groups(path: Path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = list(wb["Cords"].iter_rows(values_only=True))
    df = pd.DataFrame(rows[1:], columns=rows[0])
    df = df[df["Cord_Name"].astype(str).str.fullmatch(r"p\d+")].copy()
    df["n"] = df["Cord_Name"].str[1:].astype(int)
    df["value"] = pd.to_numeric(df["Value"], errors="coerce").fillna(0).astype(int)
    df = df.set_index("n")
    out = []
    for (line,) in wb["CordGroups"].iter_rows(values_only=True):
        m = GROUP_RE.search(str(line or ""))
        if not m:
            continue
        a, b = int(m.group(2)), int(m.group(3) or m.group(2))
        members = [n for n in range(a, b + 1) if n in df.index]
        colors = [str(df.loc[n, "Color"]) for n in members]
        for p in range(2, 13):
            units = len(members) // p
            if units < 3:
                break
            seq = colors[: units * p]
            if all(seq[i] == seq[i + p] for i in range(len(seq) - p)):
                vals = np.array([df.loc[n, "value"] for n in members[: units * p]]).reshape(units, p)
                out.append({"p": p, "units": units, "values": vals})
                break
    return out


def mean_tau(groups, perms=None):
    taus = []
    for gi, g in enumerate(groups):
        vals = g["values"] if perms is None else g["values"][perms[gi]]
        idx = np.arange(g["units"])
        for j in range(g["p"]):
            col = vals[:, j]
            if np.all(col == col[0]):
                continue
            taus.append(kendall_tau(idx, col))
    return np.array(taus)


def analyze(groups, rng):
    obs = mean_tau(groups)
    stat = float(np.nanmean(obs))
    null = np.empty(N_SHUFFLE)
    for s in range(N_SHUFFLE):
        perms = [rng.permutation(g["units"]) for g in groups]
        null[s] = np.nanmean(mean_tau(groups, perms))
    n_const = sum(int(np.all(g["values"][:, j] == g["values"][0, j])) for g in groups for j in range(g["p"]))
    by_p = {}
    for p in sorted({g["p"] for g in groups}):
        t = mean_tau([g for g in groups if g["p"] == p])
        by_p[p] = {"groups": sum(g["p"] == p for g in groups), "series": int(len(t)),
                   "mean_tau": float(np.nanmean(t)) if len(t) else None}
    return {
        "groups": len(groups),
        "series": int(len(obs)),
        "constant_series_excluded": n_const,
        "mean_tau": stat,
        "null_mean": float(null.mean()),
        "null_p95": float(np.percentile(null, 95)),
        "p_one_sided": float((null >= stat).mean()),
        "share_tau_pos": float((obs > 0).mean()),
        "share_tau_neg": float((obs < 0).mean()),
        "by_period": by_p,
    }


def main():
    per_khipu = {}
    for path in sorted(KFG.glob("KH*.xlsx")):
        try:
            g = seriated_groups(path)
        except Exception:
            continue
        if g:
            per_khipu[path.stem] = g
    rng = np.random.default_rng(SEED)
    blind = [g for k, gs in per_khipu.items() if k not in SANTA for g in gs]
    santa = [g for k, gs in per_khipu.items() if k in SANTA for g in gs]
    res = {"khipus_with_seriated_groups": len(per_khipu),
           "confirmatory_non_santa": analyze(blind, rng),
           "non_blind_santa": analyze(santa, rng) if santa else None}
    # equal weight per khipu: mean of per-khipu mean tau
    kt = [np.nanmean(mean_tau(gs)) for k, gs in per_khipu.items() if k not in SANTA and len(mean_tau(gs))]
    res["confirmatory_khipu_weighted"] = {"khipus": len(kt), "mean_of_khipu_mean_tau": float(np.nanmean(kt)),
                                          "share_khipus_positive": float(np.mean(np.array(kt) > 0))}
    OUT.mkdir(exist_ok=True)
    (OUT / "k4.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
