"""Corpus-wide audit: OKR v2.1.0 pendant values vs Khipu Field Guide workbooks."""

import json
import sqlite3
import sys
from pathlib import Path

import openpyxl
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from k1 import DB, OUT  # noqa: E402

KFG = Path(__file__).resolve().parent.parent / "data/kfg"


def shift(v: int) -> int:
    """Move the hundreds digit to the tens place when the tens place is empty."""
    h, t = v // 100 % 10, v // 10 % 10
    return v - h * 90 if t == 0 and h > 0 else v


def kfg_pendants(path: Path) -> pd.Series | None:
    try:
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        rows = list(wb["Cords"].iter_rows(values_only=True))
    except Exception:
        return None
    df = pd.DataFrame(rows[1:], columns=rows[0])
    df = df[df["Cord_Name"].astype(str).str.fullmatch(r"p\d+")]
    vals = pd.to_numeric(df["Value"], errors="coerce").fillna(0).astype(int)
    return pd.Series(vals.to_numpy(), index=df["Cord_Name"].str[1:].astype(int)).sort_index()


def main():
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    okr = pd.read_sql("""
    select m.OKR_NUM okr, c.CORD_ORDINAL o,
      (select coalesce(sum(knot_value_type), 0) from knot k where k.CORD_ID = c.CORD_ID) v
    from cord c join khipu_main m on m.KHIPU_ID = c.KHIPU_ID
    where c.CORD_LEVEL = 1
    """, con)
    con.close()
    rows = []
    for name, g in okr.groupby("okr"):
        path = KFG / f"{name}.xlsx"
        if not path.exists():
            rows.append({"okr": name, "status": "no_kfg"})
            continue
        k = kfg_pendants(path)
        if k is None:
            rows.append({"okr": name, "status": "unreadable"})
            continue
        o = g.sort_values("o")["v"].to_numpy()
        if len(o) != len(k):
            rows.append({"okr": name, "status": "count_mismatch", "okr_pendants": len(o), "kfg_pendants": len(k)})
            continue
        kv = k.to_numpy()
        exact = int((o == kv).sum())
        shifted = int((pd.Series(o).map(shift).to_numpy() == kv).sum())
        rows.append({"okr": name, "status": "aligned", "pendants": len(o), "exact": exact,
                     "after_shift": shifted, "okr_gt_kfg": int((o > kv).sum()), "okr_lt_kfg": int((o < kv).sum())})
    df = pd.DataFrame(rows)
    al = df[df["status"] == "aligned"].copy()
    al["exact_rate"] = al["exact"] / al["pendants"]
    al["shift_gain"] = (al["after_shift"] - al["exact"]) / al["pendants"]
    summary = {
        "khipus": int(len(df)),
        "status_counts": df["status"].value_counts().to_dict(),
        "aligned_pendants": int(al["pendants"].sum()),
        "aligned_exact": int(al["exact"].sum()),
        "aligned_after_shift": int(al["after_shift"].sum()),
        "khipus_exact_100pct": int((al["exact_rate"] == 1).sum()),
        "khipus_exact_below_90pct": int((al["exact_rate"] < 0.9).sum()),
        "khipus_shift_explains_10pct_plus": int((al["shift_gain"] >= 0.1).sum()),
        "worst_20": al.sort_values("exact_rate").head(20)[
            ["okr", "pendants", "exact", "after_shift", "okr_gt_kfg", "okr_lt_kfg"]].to_dict("records"),
    }
    OUT.mkdir(exist_ok=True)
    df.to_csv(OUT / "audit_okr_kfg.csv", index=False)
    (OUT / "audit_okr_kfg.json").write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
