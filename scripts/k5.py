"""K5: local color legend with a 200-draw permutation null and a calibrated model. See prereg/K5.md."""

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

N_DRAWS = 200
N_FOLDS = 5
K = 4
CKPT = OUT / "k5_ckpt"
PRIOR = [f"prior_{c}" for c in range(K)]

_DF = None
_Y = None


def permute(df: pd.DataFrame, keys: list[str], seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    out = df.copy()
    c1, fc = df["color1"].to_numpy(), df["full_color"].to_numpy()
    n1, nf = c1.copy(), fc.copy()
    for idx in df.groupby(keys).indices.values():
        p = rng.permutation(idx)
        n1[idx], nf[idx] = c1[p], fc[p]
    out["color1"], out["full_color"] = n1, nf
    return out


def _counts(frame: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    c = frame.groupby(keys + ["y"]).size().unstack(fill_value=0)
    return c.reindex(columns=range(K), fill_value=0)


def _lookup(table: pd.DataFrame, frame: pd.DataFrame, keys: list[str]) -> np.ndarray:
    idx = pd.MultiIndex.from_frame(frame[keys]) if len(keys) > 1 else pd.Index(frame[keys[0]])
    return table.reindex(idx, fill_value=0).to_numpy(dtype=float)


def local_prior(train: pd.DataFrame, ytr: np.ndarray, test: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Value-class frequencies of same (khipu, color) cords in the training fold, Laplace-smoothed.
    Training rows exclude their own cluster, mirroring held-out clusters at test time."""
    t = pd.DataFrame({"khipu_id": train["khipu_id"].to_numpy(), "cluster_id": train["cluster_id"].to_numpy(),
                      "color": train["full_color"].to_numpy(), "y": ytr})
    s = pd.DataFrame({"khipu_id": test["khipu_id"].to_numpy(), "cluster_id": test["cluster_id"].to_numpy(),
                      "color": test["full_color"].to_numpy()})
    kc, kcl_c = _counts(t, ["khipu_id", "color"]), _counts(t, ["khipu_id", "cluster_id", "color"])
    kk, kcl = _counts(t, ["khipu_id"]), _counts(t, ["khipu_id", "cluster_id"])
    glob = np.bincount(ytr, minlength=K) + 1.0
    glob /= glob.sum()

    def combine(color_cnt, khipu_cnt):
        out = np.tile(glob, (len(color_cnt), 1))
        has_k = khipu_cnt.sum(1) > 0
        out[has_k] = (khipu_cnt[has_k] + 1) / (khipu_cnt[has_k].sum(1, keepdims=True) + K)
        has_c = color_cnt.sum(1) > 0
        out[has_c] = (color_cnt[has_c] + 1) / (color_cnt[has_c].sum(1, keepdims=True) + K)
        return out

    tr_color = _lookup(kc, t, ["khipu_id", "color"]) - _lookup(kcl_c, t, ["khipu_id", "cluster_id", "color"])
    tr_khipu = _lookup(kk, t, ["khipu_id"]) - _lookup(kcl, t, ["khipu_id", "cluster_id"])
    te_color = _lookup(kc, s, ["khipu_id", "color"])
    te_khipu = _lookup(kk, s, ["khipu_id"])
    return combine(tr_color, tr_khipu), combine(te_color, te_khipu)


def fit_bits(train, test, ytr, yte, use_prior: bool) -> tuple[np.ndarray, np.ndarray]:
    feats = CAT + NUM
    tr, te = train[feats].copy(), test[feats].copy()
    num = list(NUM)
    if use_prior:
        ptr, pte = local_prior(train, ytr, test)
        tr[PRIOR], te[PRIOR] = ptr, pte
        num += PRIOR
    tr[num] = tr[num].fillna(0)
    te[num] = te[num].fillna(0)
    pre = ColumnTransformer([
        ("cat", OneHotEncoder(min_frequency=MIN_CAT, handle_unknown="infrequent_if_exist"), CAT),
        ("num", StandardScaler(), num),
    ])
    clf = make_pipeline(pre, LogisticRegression(C=1.0, max_iter=2000))
    clf.fit(tr, ytr)
    proba = np.full((len(te), K), 1e-12)
    proba[:, clf.classes_] = clf.predict_proba(te)
    proba /= proba.sum(1, keepdims=True)
    bits = -np.log2(np.clip(proba[np.arange(len(yte)), yte], 1e-12, 1))
    m = np.bincount(ytr, minlength=K) + 1.0
    m /= m.sum()
    return bits, -np.log2(m[yte])


def cv_bits(df: pd.DataFrame, y: np.ndarray, groups: np.ndarray, use_prior: bool) -> tuple[float, float]:
    bits, marg = np.zeros(len(df)), np.zeros(len(df))
    for tr, te in GroupKFold(n_splits=N_FOLDS).split(df, y, groups):
        b, m = fit_bits(df.iloc[tr], df.iloc[te], y[tr], y[te], use_prior)
        bits[te], marg[te] = b, m
    return float(bits.mean()), float(marg.mean())


def _init(df, y):
    global _DF, _Y
    _DF, _Y = df, y


def _draw(run: str, kind: str, seed: int) -> dict:
    df, y = _DF, _Y
    if kind == "K5a":
        groups = (df["khipu_id"].astype(str) + ":" + df["cluster_id"].astype(str)).to_numpy()
        data = df if seed == 0 else permute(df, ["khipu_id", "cluster_id"], seed)
        bits, marg = cv_bits(data, y, groups, use_prior=True)
    else:
        groups = df["khipu_id"].to_numpy()
        data = df if seed == 0 else permute(df, ["khipu_id"], seed)
        bits, marg = cv_bits(data, y, groups, use_prior=False)
    return {"run": run, "kind": kind, "seed": seed, "bits": bits, "marginal": marg}


def clean_khipus() -> set:
    audit = pd.read_csv(OUT / "audit_okr_kfg.csv")
    al = audit[audit["status"] == "aligned"]
    ok = set(al.loc[al["exact"] / al["pendants"] >= 0.9, "okr"])
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    ids = pd.read_sql("select KHIPU_ID khipu_id, OKR_NUM okr from khipu_main", con)
    con.close()
    return set(ids.loc[ids["okr"].isin(ok), "khipu_id"])


def run_set(name: str, df: pd.DataFrame) -> dict:
    y = value_class(df["val"])
    CKPT.mkdir(parents=True, exist_ok=True)
    results = {}
    todo = []
    for kind in ["K5a", "K5b"]:
        for seed in range(N_DRAWS + 1):
            f = CKPT / f"{name}_{kind}_{seed:03d}.json"
            if f.exists():
                results[(kind, seed)] = json.loads(f.read_text())
            else:
                todo.append((kind, seed))
    print(f"[{name}] {len(results)} from checkpoint, {len(todo)} to run", flush=True)
    t0 = time.time()
    with ProcessPoolExecutor(initializer=_init, initargs=(df, y)) as pool:
        futs = {pool.submit(_draw, name, k, s): (k, s) for k, s in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            r = fut.result()
            (CKPT / f"{name}_{r['kind']}_{r['seed']:03d}.json").write_text(json.dumps(r))
            results[(r["kind"], r["seed"])] = r
            if i % 20 == 0 or i == len(todo):
                print(f"[{name}] {i}/{len(todo)} done, {time.time() - t0:.0f}s", flush=True)
    out = {"cords": int(len(df)), "khipus": int(df["khipu_id"].nunique())}
    single = df.groupby("khipu_id")["cluster_id"].nunique()
    out["cords_in_single_cluster_khipus"] = int(df["khipu_id"].map(single).eq(1).sum())
    for kind in ["K5a", "K5b"]:
        real = results[(kind, 0)]
        null = np.array([results[(kind, s)]["bits"] for s in range(1, N_DRAWS + 1)])
        lo, hi = np.percentile(null, [2.5, 97.5])
        out[kind] = {
            "bits_real": real["bits"], "bits_marginal": real["marginal"],
            "calibration_ok": real["bits"] <= real["marginal"],
            "null_mean": float(null.mean()), "null_95": [float(lo), float(hi)],
            "gain_vs_null_mean": float(null.mean() - real["bits"]),
            "p_real_better": float((null <= real["bits"]).mean()),
            "below_null_2_5pct": bool(real["bits"] < lo),
            "inside_null_95": bool(lo <= real["bits"] <= hi),
        }
    return out


def main():
    df = load()
    res = {"all": run_set("all", df)}
    keep = clean_khipus()
    res["clean"] = run_set("clean", df[df["khipu_id"].isin(keep)].reset_index(drop=True))
    a, c = res["all"]["K5a"], res["clean"]["K5a"]
    valid = a["calibration_ok"] and c["calibration_ok"]
    res["verdict"] = {
        "K5a": ("invalid (calibration gate)" if not valid else
                "survives" if a["below_null_2_5pct"] and c["below_null_2_5pct"] else "killed"),
        "K5b": ("survives (no transfer)" if res["all"]["K5b"]["inside_null_95"]
                else "killed (transfer)" if res["all"]["K5b"]["below_null_2_5pct"]
                else "real colors worse than null"),
    }
    (OUT / "k5.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
