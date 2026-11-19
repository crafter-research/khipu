"""K7: local color legend under a layout control, separately in AS and UR khipus. See prereg/K7.md."""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import json
import sqlite3
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent))
from k1 import CAT, DB, MIN_CAT, NUM, OUT, value_class  # noqa: E402
from k2 import load  # noqa: E402
from k5 import K, permute  # noqa: E402

N_DRAWS = 200
N_FOLDS = 5
EXCLUDE_OKR = {"KH0323", "KH0324", "KH0325", "KH0326", "KH0327", "KH0328", "KH0472", "KH0401"}
MIN_CORDS = 30
MIN_CLUSTERS = 2
MIN_GAIN = 0.02
MIN_SHARE = 0.5
CKPT = OUT / "k7_ckpt"
_DF = _Y = None


def _counts(frame, keys):
    return frame.groupby(keys + ["y"]).size().unstack(fill_value=0).reindex(columns=range(K), fill_value=0)


def _lookup(table, frame, keys):
    idx = pd.MultiIndex.from_frame(frame[keys]) if len(keys) > 1 else pd.Index(frame[keys[0]])
    return table.reindex(idx, fill_value=0).to_numpy(dtype=float)


def prior(train, ytr, test, key: list[str]):
    """Laplace-smoothed class frequencies of training cords sharing (khipu, *key); training rows
    exclude their own cluster; fallback to the khipu marginal, then the global marginal."""
    cols = ["khipu_id", "cluster_id"] + key
    t = train[cols].copy()
    t["y"] = ytr
    s = test[cols].copy()
    full = ["khipu_id"] + key
    by_key, by_key_cl = _counts(t, full), _counts(t, ["khipu_id", "cluster_id"] + key)
    kk, kcl = _counts(t, ["khipu_id"]), _counts(t, ["khipu_id", "cluster_id"])
    glob = np.bincount(ytr, minlength=K) + 1.0
    glob /= glob.sum()

    def combine(kc, kh):
        out = np.tile(glob, (len(kc), 1))
        h = kh.sum(1) > 0
        out[h] = (kh[h] + 1) / (kh[h].sum(1, keepdims=True) + K)
        c = kc.sum(1) > 0
        out[c] = (kc[c] + 1) / (kc[c].sum(1, keepdims=True) + K)
        return out

    tr = combine(_lookup(by_key, t, full) - _lookup(by_key_cl, t, ["khipu_id", "cluster_id"] + key),
                 _lookup(kk, t, ["khipu_id"]) - _lookup(kcl, t, ["khipu_id", "cluster_id"]))
    te = combine(_lookup(by_key, s, full), _lookup(kk, s, ["khipu_id"]))
    return tr, te


def fit_bits(train, test, ytr, yte):
    feats = CAT + NUM
    tr, te = train[feats].copy(), test[feats].copy()
    num = list(NUM)
    for name, key in (("color", ["full_color"]), ("layout", ["cord_level", "cluster_ordinal"])):
        ptr, pte = prior(train, ytr, test, key)
        names = [f"{name}_prior_{c}" for c in range(K)]
        tr[names], te[names] = ptr, pte
        num += names
    tr[num], te[num] = tr[num].fillna(0), te[num].fillna(0)
    pre = ColumnTransformer([
        ("cat", OneHotEncoder(min_frequency=MIN_CAT, handle_unknown="infrequent_if_exist"), CAT),
        ("num", StandardScaler(), num),
    ])
    clf = make_pipeline(pre, LogisticRegression(C=1.0, max_iter=2000))
    clf.fit(tr, ytr)
    proba = np.full((len(te), K), 1e-12)
    proba[:, clf.classes_] = clf.predict_proba(te)
    proba /= proba.sum(1, keepdims=True)
    return -np.log2(np.clip(proba[np.arange(len(yte)), yte], 1e-12, 1))


def cv_khipu_bits(df, y) -> dict:
    groups = (df["khipu_id"].astype(str) + ":" + df["cluster_id"].astype(str)).to_numpy()
    bits = np.zeros(len(df))
    for tr, te in GroupKFold(n_splits=N_FOLDS).split(df, y, groups):
        bits[te] = fit_bits(df.iloc[tr], df.iloc[te], y[tr], y[te])
    return pd.Series(bits).groupby(df["khipu_id"].to_numpy()).mean().to_dict()


def _init(df, y):
    global _DF, _Y
    _DF, _Y = df, y


def _draw(seed: int) -> dict:
    data = _DF if seed == 0 else permute(_DF, ["khipu_id", "cluster_id"], seed)
    return {"seed": seed, "per_khipu": {str(k): v for k, v in cv_khipu_bits(data, _Y).items()}}


def subset(df: pd.DataFrame, meta: pd.DataFrame, prefix: str) -> pd.DataFrame:
    ids = meta[(meta["prefix"] == prefix) & ~meta["okr"].isin(EXCLUDE_OKR)]["khipu_id"]
    d = df[df["khipu_id"].isin(set(ids))]
    stats = d.groupby("khipu_id").agg(cords=("cord_id", "size"), clusters=("cluster_id", "nunique"))
    keep = stats[(stats["cords"] >= MIN_CORDS) & (stats["clusters"] >= MIN_CLUSTERS)].index
    return d[d["khipu_id"].isin(set(keep))].reset_index(drop=True)


def run(name: str, df: pd.DataFrame) -> dict:
    y = value_class(df["val"])
    CKPT.mkdir(parents=True, exist_ok=True)
    draws, todo = {}, []
    for s in range(N_DRAWS + 1):
        f = CKPT / f"{name}_{s:03d}.json"
        if f.exists():
            draws[s] = json.loads(f.read_text())
        else:
            todo.append(s)
    print(f"[{name}] {len(df)} cords, {df['khipu_id'].nunique()} khipus; {len(todo)} draws to run", flush=True)
    t0 = time.time()
    with ProcessPoolExecutor(initializer=_init, initargs=(df, y)) as pool:
        futs = {pool.submit(_draw, s): s for s in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            r = fut.result()
            (CKPT / f"{name}_{r['seed']:03d}.json").write_text(json.dumps(r))
            draws[r["seed"]] = r
            if i % 20 == 0 or i == len(todo):
                print(f"[{name}] {i}/{len(todo)} draws, {time.time() - t0:.0f}s", flush=True)
    khipus = sorted(draws[0]["per_khipu"])
    real = np.array([draws[0]["per_khipu"][k] for k in khipus])
    null = np.array([[draws[s]["per_khipu"][k] for k in khipus] for s in range(1, N_DRAWS + 1)])
    real_w, null_w = float(real.mean()), null.mean(1)
    gain_w = float(null_w.mean() - real_w)
    share = float(((null.mean(0) - real) > 0).mean())
    lo = float(np.percentile(null_w, 2.5))
    c1, c2, c3 = real_w < lo, gain_w >= MIN_GAIN, share > MIN_SHARE
    return {
        "cords": int(len(df)), "khipus": len(khipus),
        "real_bits_khipu_weighted": real_w, "null_mean": float(null_w.mean()),
        "null_95": [lo, float(np.percentile(null_w, 97.5))],
        "gain_khipu_weighted": gain_w, "share_khipus_positive": share,
        "criteria": {"below_null_2_5pct": bool(c1), "gain_at_least_0_02": bool(c2), "share_above_half": bool(c3)},
        "passes": bool(c1 and c2 and c3),
    }


def main():
    df = load()
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    meta = pd.read_sql("select KHIPU_ID khipu_id, OKR_NUM okr, INVESTIGATOR_NUM inv from khipu_main", con)
    con.close()
    meta["prefix"] = meta["inv"].fillna("").str.strip().str.upper().str[:2]
    res = {p: run(p, subset(df, meta, p)) for p in ("AS", "UR")}
    a, u = res["AS"]["passes"], res["UR"]["passes"]
    res["verdict"] = ("survives" if a and u else "fails in both: K5a withdrawn" if not (a or u)
                      else f"recording convention: passes only in {'AS' if a else 'UR'}")
    (OUT / "k7.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
