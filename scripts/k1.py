"""K1: do non-numeric cord attributes predict knot values? See prereg/K1.md."""

import json
import sqlite3
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import GroupKFold, KFold

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data/okr-gh-v2.1.0/khipu.db"
OUT = ROOT / "results"
SEED = 0
N_FOLDS = 5
N_BOOT = 2000
MIN_CAT = 20
MAX_CAT = 250

CAT = ["color1", "full_color", "twist", "attachment", "fiber", "termination"]
NUM = ["cord_level", "is_subsidiary", "cluster_ordinal", "cord_ordinal"]
POSITION = ["cluster_ordinal", "cord_ordinal"]
PHYSICAL = ["cord_length", "attach_pos", "thickness"]


def load() -> pd.DataFrame:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    q = """
    with v as (select CORD_ID, sum(knot_value_type) val from knot group by CORD_ID),
    col as (
      select a.CORD_ID, a.COLOR_CD_1, a.FULL_COLOR from ascher_cord_color a
      join (select CORD_ID, min(color_id) mid from ascher_cord_color group by CORD_ID) m
        on a.CORD_ID = m.CORD_ID and a.color_id = m.mid
    )
    select c.CORD_ID cord_id, c.KHIPU_ID khipu_id, v.val,
      col.COLOR_CD_1 color1, col.FULL_COLOR full_color,
      c.TWIST twist, c.ATTACHMENT_TYPE attachment, c.FIBER fiber, c.TERMINATION termination,
      c.CORD_LEVEL cord_level, c.CLUSTER_ORDINAL cluster_ordinal, c.CORD_ORDINAL cord_ordinal,
      c.CORD_LENGTH cord_length, c.ATTACH_POS attach_pos, c.THICKNESS thickness,
      c.CREATED_BY created_by, k.PROVENANCE provenance
    from cord c join v on v.CORD_ID = c.CORD_ID
    left join col on col.CORD_ID = c.CORD_ID
    join khipu_main k on k.KHIPU_ID = c.KHIPU_ID
    """
    df = pd.read_sql(q, con)
    con.close()
    df["is_subsidiary"] = (df["cord_level"] > 1).astype(int)
    for c in CAT:
        df[c] = df[c].fillna("").astype(str).str.strip().replace("", "NA")
    prov = df["provenance"].fillna("").str.strip()
    unknown = prov.isin(["", "unknown"])
    df["group_prov"] = np.where(unknown, "khipu_" + df["khipu_id"].astype(str), prov)
    rec = df.groupby("khipu_id")["created_by"].agg(lambda s: s.mode().iat[0] if s.notna().any() else "NA")
    df["group_rec"] = df["khipu_id"].map(rec)
    return df


def value_class(v: pd.Series) -> np.ndarray:
    return np.digitize(v.to_numpy(), [10, 100, 1000])


def permute_colors(df: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    out = df.copy()
    for _, idx in out.groupby("khipu_id").indices.items():
        p = rng.permutation(idx)
        out.iloc[idx, out.columns.get_loc("color1")] = df["color1"].to_numpy()[p]
        out.iloc[idx, out.columns.get_loc("full_color")] = df["full_color"].to_numpy()[p]
    return out


def encode(train: pd.DataFrame, test: pd.DataFrame, cats: list[str]):
    tr, te = train.copy(), test.copy()
    for c in cats:
        counts = tr[c].value_counts()
        keep = list(counts[counts >= MIN_CAT].index[:MAX_CAT])
        m = {k: i for i, k in enumerate(keep)}
        tr[c] = tr[c].map(m).fillna(len(keep)).astype(int)
        te[c] = te[c].map(m).fillna(len(keep)).astype(int)
    return tr, te


def bits_model(train, test, ytr, yte, feats, n_cls):
    cats = [f for f in feats if f in CAT]
    tr, te = encode(train[feats], test[feats], cats)
    clf = HistGradientBoostingClassifier(
        categorical_features=[f in cats for f in feats], random_state=SEED, max_iter=300
    )
    clf.fit(tr, ytr)
    proba = np.full((len(te), n_cls), 1e-12)
    proba[:, clf.classes_] = clf.predict_proba(te)
    proba /= proba.sum(1, keepdims=True)
    p = np.clip(proba[np.arange(len(yte)), yte], 1e-12, 1)
    return -np.log2(p), proba.argmax(1)


def bits_marginal(ytr, yte, n_cls):
    f = np.bincount(ytr, minlength=n_cls) + 1.0
    f /= f.sum()
    return -np.log2(f[yte]), np.full(len(yte), f.argmax())


def run(df, y, n_cls, splitter, groups, variants):
    bits = {k: np.zeros(len(df)) for k in variants}
    pred = {k: np.zeros(len(df), dtype=int) for k in variants}
    for tr, te in splitter.split(df, y, groups):
        for k, (data, feats) in variants.items():
            if feats is None:
                b, p = bits_marginal(y[tr], y[te], n_cls)
            else:
                b, p = bits_model(data.iloc[tr], data.iloc[te], y[tr], y[te], feats, n_cls)
            bits[k][te], pred[k][te] = b, p
    return bits, pred


def boot_gain(a, b, groups):
    """Gain in bits per cord of b over a (a minus b), bootstrapped over groups."""
    g = pd.Series(groups).astype("category").cat.codes.to_numpy()
    ng = g.max() + 1
    sa, sb, n = (np.bincount(g, w, ng) for w in (a, b, np.ones_like(a)))
    rng = np.random.default_rng(SEED)
    draws = rng.integers(0, ng, (N_BOOT, ng))
    gains = (sa[draws].sum(1) - sb[draws].sum(1)) / n[draws].sum(1)
    point = (a.sum() - b.sum()) / len(a)
    return {
        "gain_bits_per_cord": float(point),
        "ci95": [float(np.percentile(gains, 2.5)), float(np.percentile(gains, 97.5))],
        "p_one_sided": float((gains <= 0).mean()),
    }


def holm(ps: dict) -> dict:
    items = sorted(ps.items(), key=lambda kv: kv[1])
    m, out, running = len(items), {}, 0.0
    for i, (k, p) in enumerate(items):
        running = max(running, min(1.0, (m - i) * p))
        out[k] = running
    return out


def summary(bits, pred, y):
    return {k: {"bits_per_cord": float(b.mean()), "accuracy": float((pred[k] == y).mean())} for k, b in bits.items()}


def experiment(df, y, n_cls, splitter, groups):
    perm = permute_colors(df)
    feats = CAT + NUM
    no_pos = [f for f in feats if f not in POSITION]
    variants = {
        "B0": (df, None),
        "M1": (df, feats),
        "N1": (perm, feats),
        "M1_no_position": (df, no_pos),
        "N1_no_position": (perm, no_pos),
        "A2_physical": (df, feats + PHYSICAL),
    }
    bits, pred = run(df, y, n_cls, splitter, groups, variants)
    return {
        "n": int(len(y)),
        "n_groups": int(pd.Series(groups).nunique()),
        "summary": summary(bits, pred, y),
        "M1_vs_B0": boot_gain(bits["B0"], bits["M1"], groups),
        "M1_vs_N1": boot_gain(bits["N1"], bits["M1"], groups),
        "noPos_vs_B0": boot_gain(bits["B0"], bits["M1_no_position"], groups),
        "noPos_vs_N1": boot_gain(bits["N1_no_position"], bits["M1_no_position"], groups),
    }


def main():
    sys.setrecursionlimit(10000)
    df = load()
    y = value_class(df["val"])
    gkf = GroupKFold(n_splits=N_FOLDS)
    res = {"db_rows": int(len(df))}
    res["T1_class_by_provenance"] = experiment(df, y, 4, gkf, df["group_prov"].to_numpy())
    res["T1_class_by_recorder"] = experiment(df, y, 4, gkf, df["group_rec"].to_numpy())
    kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    res["T2_class_within_khipu"] = experiment(df, y, 4, kf, df["khipu_id"].to_numpy())
    small = df[df["val"] < 100].reset_index(drop=True)
    yd = (small["val"] % 10).to_numpy()
    res["T1_units_digit_by_provenance"] = experiment(small, yd, 10, gkf, small["group_prov"].to_numpy())
    res["holm_M1_vs_N1"] = holm({
        k: res[k]["M1_vs_N1"]["p_one_sided"]
        for k in ["T1_class_by_provenance", "T2_class_within_khipu", "T1_units_digit_by_provenance"]
    })
    OUT.mkdir(exist_ok=True)
    (OUT / "k1.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
