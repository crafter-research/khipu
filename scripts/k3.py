"""K3: Santa Valley first cords vs the 1670 tribute. See PREREG-K3.md."""

import json
import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from k1 import DB, OUT  # noqa: E402

REVISITA_TOTAL = 367
PUBLISHED_SUM = 467  # 381 verso + 86 recto, FitzPatrick 2024 citing Urton 2017


def main():
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    cords = pd.read_sql("""
    select c.KHIPU_ID khipu_id, m.OKR_NUM okr, m.INVESTIGATOR_NUM inv, c.CORD_ID cord_id,
      c.CLUSTER_ID cluster_id, c.CORD_ORDINAL cord_ordinal, c.CORD_LEVEL cord_level,
      c.ATTACHMENT_TYPE attachment, c.TERMINATION termination,
      (select sum(k.knot_value_type) from knot k where k.CORD_ID = c.CORD_ID) val,
      (select count(*) from knot k where k.CORD_ID = c.CORD_ID) n_knots
    from cord c join khipu_main m on m.KHIPU_ID = c.KHIPU_ID
    where m.PROVENANCE = 'Santa'
    """, con)
    con.close()

    lvl1 = cords[cords["cord_level"] == 1]
    sizes = lvl1.groupby(["khipu_id", "cluster_id"]).size()
    six = sizes[sizes == 6].index
    groups = lvl1.set_index(["khipu_id", "cluster_id"]).loc[six].reset_index()
    first = groups.sort_values("cord_ordinal").groupby(["khipu_id", "cluster_id"]).head(1).copy()
    first["val"] = first["val"].fillna(0).astype(int)

    total = int(first["val"].sum())
    by_att = first.groupby("attachment")["val"].agg(["sum", "count"]).to_dict("index")
    verso = int(by_att.get("V", {}).get("sum", 0))
    recto = int(by_att.get("R", {}).get("sum", 0))
    n_r = int(by_att.get("R", {}).get("count", 0))
    n_v = int(by_att.get("V", {}).get("count", 0))

    per_khipu = (
        first.groupby(["okr", "inv", "attachment"])["val"].agg(["count", "sum", "min", "max"])
        .reset_index().to_dict("records")
    )
    res = {
        "santa_cords": int(len(cords)),
        "level1_cluster_sizes": {str(k): int(v) for k, v in sizes.value_counts().sort_index().items()},
        "six_cord_groups": int(len(six)),
        "first_cords_no_knots": int((first["n_knots"] == 0).sum()),
        "first_cords_broken": int((first["termination"] == "B").sum()),
        "first_cords_value_zero_with_knots": int(((first["val"] == 0) & (first["n_knots"] > 0)).sum()),
        "K3a": {
            "total": total,
            "diff_to_367": total - REVISITA_TOTAL,
            "diff_to_467": total - PUBLISHED_SUM,
            "survives": abs(total - REVISITA_TOTAL) < abs(total - PUBLISHED_SUM),
        },
        "K3b": {"verso_total": verso, "recto_total": recto,
                "survives": verso in (381, 382) and recto == 86},
        "K3c": {"groups": int(len(six)), "recto_first": n_r, "verso_first": n_v,
                "other_attachment": int(len(first) - n_r - n_v),
                "survives": len(six) == 133 and n_r == 63 and n_v == 70},
        "per_khipu": per_khipu,
        "first_cord_value_counts": {int(k): int(v) for k, v in first["val"].value_counts().sort_index().items()},
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "k3.json").write_text(json.dumps(res, indent=2, default=str))
    print(json.dumps(res, indent=2, default=str))


if __name__ == "__main__":
    main()
