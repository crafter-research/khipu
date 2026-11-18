"""Robustness check (declared after the audit, not preregistered): rerun the surviving
within-khipu tests (K1 T2 and K2b) only on khipus whose OKR pendant values agree with KFG."""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import json
import sys
from pathlib import Path

import pandas as pd
from sklearn.model_selection import KFold

sys.path.insert(0, str(Path(__file__).resolve().parent))
from k1 import N_FOLDS, OUT, SEED, boot_gain, run, value_class  # noqa: E402
from k2 import FEATS, load, permute  # noqa: E402

MIN_EXACT = 0.9


def main():
    audit = pd.read_csv(OUT / "audit_okr_kfg.csv")
    al = audit[audit["status"] == "aligned"].copy()
    al["rate"] = al["exact"] / al["pendants"]
    clean = set(al.loc[al["rate"] >= MIN_EXACT, "okr"])

    import sqlite3
    from k1 import DB
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    ids = pd.read_sql("select KHIPU_ID khipu_id, OKR_NUM okr from khipu_main", con)
    con.close()
    keep = set(ids.loc[ids["okr"].isin(clean), "khipu_id"])

    df = load()
    df = df[df["khipu_id"].isin(keep)].reset_index(drop=True)
    y = value_class(df["val"])
    kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    variants = {
        "real": (df, FEATS),
        "perm_khipu": (permute(df, ["khipu_id"]), FEATS),
        "perm_cluster": (permute(df, ["khipu_id", "cluster_id"]), FEATS),
    }
    bits, _ = run(df, y, 4, kf, df["khipu_id"].to_numpy(), variants)
    g = df["khipu_id"].to_numpy()
    res = {
        "min_exact_rate": MIN_EXACT,
        "khipus": int(df["khipu_id"].nunique()),
        "cords": int(len(df)),
        "bits": {k: float(v.mean()) for k, v in bits.items()},
        "T2_real_vs_perm_khipu": boot_gain(bits["perm_khipu"], bits["real"], g),
        "K2b_real_vs_perm_cluster": boot_gain(bits["perm_cluster"], bits["real"], g),
    }
    (OUT / "robust_clean.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
