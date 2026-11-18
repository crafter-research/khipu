"""K2: regional color legend (K2a) and color beyond cluster membership (K2b). See PREREG-K2.md."""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import json
import sqlite3
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, LeaveOneGroupOut

sys.path.insert(0, str(Path(__file__).resolve().parent))
from k1 import (  # noqa: E402
    CAT, DB, N_FOLDS, NUM, OUT, SEED,
    bits_marginal, bits_model, boot_gain, holm, run, value_class,
)

FEATS = CAT + NUM


def load() -> pd.DataFrame:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    cords = pd.read_sql("""
    with v as (select CORD_ID, sum(knot_value_type) val from knot group by CORD_ID)
    select c.CORD_ID cord_id, c.KHIPU_ID khipu_id, c.CLUSTER_ID cluster_id, v.val,
      c.TWIST twist, c.ATTACHMENT_TYPE attachment, c.FIBER fiber, c.TERMINATION termination,
      c.CORD_LEVEL cord_level, c.CLUSTER_ORDINAL cluster_ordinal, c.CORD_ORDINAL cord_ordinal,
      c.CREATED_BY created_by, k.PROVENANCE provenance
    from cord c join v on v.CORD_ID = c.CORD_ID
    join khipu_main k on k.KHIPU_ID = c.KHIPU_ID
    """, con)
    colors = pd.read_sql(
        "select rowid rid, color_id, CORD_ID cord_id, COLOR_CD_1 color1, FULL_COLOR full_color from ascher_cord_color",
        con,
    )
    con.close()
    colors = colors.sort_values(["cord_id", "color_id", "rid"]).drop_duplicates("cord_id")
    df = cords.merge(colors[["cord_id", "color1", "full_color"]], on="cord_id", how="left")
    assert df["cord_id"].is_unique
    df["is_subsidiary"] = (df["cord_level"] > 1).astype(int)
    for c in CAT:
        df[c] = df[c].fillna("").astype(str).str.strip().replace("", "NA")
    df["prov"] = df["provenance"].fillna("").str.strip()
    return df.reset_index(drop=True)


def permute(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    out = df.copy()
    c1, fc = df["color1"].to_numpy(), df["full_color"].to_numpy()
    new1, newf = c1.copy(), fc.copy()
    for idx in df.groupby(keys).indices.values():
        p = rng.permutation(idx)
        new1[idx], newf[idx] = c1[p], fc[p]
    out["color1"], out["full_color"] = new1, newf
    return out


CKPT = OUT / "k2a_checkpoint"


def provenance_fold(data: pd.DataFrame, perm: pd.DataFrame, y: np.ndarray):
    data, perm = data.reset_index(drop=True), perm.reset_index(drop=True)
    real, null = np.zeros(len(data)), np.zeros(len(data))
    single = 0
    groups = data["khipu_id"].to_numpy()
    for tr, te in LeaveOneGroupOut().split(data, groups=groups):
        if len(np.unique(y[tr])) < 2:
            single += 1
            b, _ = bits_marginal(y[tr], y[te], 4)
            real[te], null[te] = b, b
            continue
        real[te], _ = bits_model(data.iloc[tr], data.iloc[te], y[tr], y[te], FEATS, 4)
        null[te], _ = bits_model(perm.iloc[tr], perm.iloc[te], y[tr], y[te], FEATS, 4)
    return real, null, single


def k2a(df: pd.DataFrame) -> dict:
    known = df[~df["prov"].isin(["", "unknown"])]
    per_prov = known.groupby("prov")["khipu_id"].nunique()
    eligible = per_prov[per_prov >= 2].index
    data = known[known["prov"].isin(eligible)].reset_index(drop=True)
    perm = permute(data, ["khipu_id"])
    y = value_class(data["val"])
    real, null = np.zeros(len(data)), np.zeros(len(data))
    single_class_folds = 0
    CKPT.mkdir(parents=True, exist_ok=True)
    jobs = {}
    with ProcessPoolExecutor() as pool:
        for i, prov in enumerate(eligible):
            pidx = np.flatnonzero(data["prov"].to_numpy() == prov)
            f = CKPT / f"{i:03d}.npz"
            if f.exists():
                z = np.load(f)
                real[pidx], null[pidx] = z["real"], z["null"]
                single_class_folds += int(z["single"])
                print(f"[K2a] {i + 1}/{len(eligible)} {prov}: from checkpoint", flush=True)
                continue
            fut = pool.submit(provenance_fold, data.iloc[pidx], perm.iloc[pidx], y[pidx])
            jobs[fut] = (i, prov, pidx, f)
        for fut in as_completed(jobs):
            i, prov, pidx, f = jobs[fut]
            r, n, single = fut.result()
            np.savez(f, real=r, null=n, single=single)
            real[pidx], null[pidx] = r, n
            single_class_folds += single
            print(f"[K2a] {i + 1}/{len(eligible)} {prov}: done ({len(pidx)} cords)", flush=True)
    by_prov = {}
    for prov in eligible:
        m = data["prov"].to_numpy() == prov
        by_prov[prov] = {
            "khipus": int(per_prov[prov]),
            "cords": int(m.sum()),
            "gain_bits_per_cord": float(null[m].mean() - real[m].mean()),
            "recorders": sorted(data.loc[m, "created_by"].fillna("NA").unique().tolist()),
        }
    return {
        "provenances": int(len(eligible)),
        "khipus": int(data["khipu_id"].nunique()),
        "cords": int(len(data)),
        "single_class_train_folds": single_class_folds,
        "bits_real": float(real.mean()),
        "bits_null": float(null.mean()),
        "gain": boot_gain(null, real, data["khipu_id"].to_numpy()),
        "by_provenance": by_prov,
    }


def k2b(df: pd.DataFrame) -> dict:
    perm = permute(df, ["khipu_id", "cluster_id"])
    y = value_class(df["val"])
    kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    print("[K2b] running 5 folds x 2 variants", flush=True)
    bits, _ = run(df, y, 4, kf, df["khipu_id"].to_numpy(), {"real": (df, FEATS), "null": (perm, FEATS)})
    size = df.groupby(["khipu_id", "cluster_id"])["cord_id"].transform("size")
    return {
        "cords": int(len(df)),
        "cords_in_multicord_clusters": int((size > 1).sum()),
        "bits_real": float(bits["real"].mean()),
        "bits_null": float(bits["null"].mean()),
        "gain": boot_gain(bits["null"], bits["real"], df["khipu_id"].to_numpy()),
    }


def main():
    df = load()
    print(f"[load] {len(df)} rows", flush=True)
    res = {"rows": int(len(df)), "K2a": k2a(df)}
    res["K2b"] = k2b(df)
    res["holm"] = holm({"K2a": res["K2a"]["gain"]["p_one_sided"], "K2b": res["K2b"]["gain"]["p_one_sided"]})
    OUT.mkdir(exist_ok=True)
    (OUT / "k2.json").write_text(json.dumps(res, indent=2))
    print(json.dumps({k: v for k, v in res.items() if k != "K2a"} | {"K2a_gain": res["K2a"]["gain"]}, indent=2))


if __name__ == "__main__":
    main()
