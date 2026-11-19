"""K3.1: Santa first cords vs the 1670 tribute, six-cord runs within clusters. See prereg/K3.1.md."""

import json
import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from k1 import DB, OUT  # noqa: E402

REVISITA_TOTAL = 367
PUBLISHED_SUM = 467
MU2018_TABLE1 = {"UR087": (48, 0), "UR092": (10, 0), "UR088": (0, 9),
                 "UR089": (0, 34), "UR091": (0, 15), "UR090": (5, 12)}


def main():
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    cords = pd.read_sql("""
    select m.INVESTIGATOR_NUM inv, m.OKR_NUM okr, c.KHIPU_ID khipu_id, c.CORD_ID cord_id,
      c.CLUSTER_ID cluster_id, c.CORD_ORDINAL cord_ordinal,
      c.ATTACHMENT_TYPE attachment, c.TERMINATION termination,
      (select sum(k.knot_value_type) from knot k where k.CORD_ID = c.CORD_ID) val,
      (select count(*) from knot k where k.CORD_ID = c.CORD_ID) n_knots
    from cord c join khipu_main m on m.KHIPU_ID = c.KHIPU_ID
    where m.PROVENANCE = 'Santa' and c.CORD_LEVEL = 1
    """, con)
    con.close()
    cords["val"] = cords["val"].fillna(0).astype(int)

    firsts, remainders, singles = [], [], 0
    for (_, _), g in cords.groupby(["khipu_id", "cluster_id"]):
        g = g.sort_values("cord_ordinal").reset_index(drop=True)
        if len(g) == 1:
            singles += 1
            continue
        n_full = len(g) // 6
        for i in range(n_full):
            firsts.append(g.iloc[i * 6])
        if len(g) % 6:
            remainders.append({"inv": g["inv"].iat[0], "cluster_size": len(g),
                               "remainder": len(g) % 6,
                               "ordinals": g["cord_ordinal"].iloc[n_full * 6:].tolist()})
    first = pd.DataFrame(firsts)

    total = int(first["val"].sum())
    att = first.groupby("attachment")["val"].agg(["sum", "count"])
    get = lambda a, c: int(att.loc[a, c]) if a in att.index else 0  # noqa: E731
    verso, recto, n_v, n_r = get("V", "sum"), get("R", "sum"), get("V", "count"), get("R", "count")

    per_khipu = []
    for inv, g in first.groupby("inv"):
        r = int((g["attachment"] == "R").sum())
        v = int((g["attachment"] == "V").sum())
        per_khipu.append({"inv": inv, "groups": len(g), "recto": r, "verso": v,
                          "mu2018_recto_verso": MU2018_TABLE1.get(inv), "value_sum": int(g["val"].sum()),
                          "values": g["val"].value_counts().sort_index().to_dict()})
    res = {
        "groups": int(len(first)),
        "single_cord_clusters": singles,
        "remainders": remainders,
        "first_cords_broken": int((first["termination"] == "B").sum()),
        "first_cords_no_knots": int((first["n_knots"] == 0).sum()),
        "K3a": {"total": total, "diff_to_367": total - REVISITA_TOTAL, "diff_to_467": total - PUBLISHED_SUM,
                "survives": abs(total - REVISITA_TOTAL) < abs(total - PUBLISHED_SUM)},
        "K3b": {"verso_total": verso, "recto_total": recto, "survives": verso in (381, 382) and recto == 86},
        "K3c": {"recto_first": n_r, "verso_first": n_v, "other": int(len(first) - n_r - n_v),
                "survives": n_r == 63 and n_v == 70},
        "per_khipu": per_khipu,
        "first_cord_values": {int(k): int(v) for k, v in first["val"].value_counts().sort_index().items()},
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "k3_1.json").write_text(json.dumps(res, indent=2, default=str))
    print(json.dumps(res, indent=2, default=str))


if __name__ == "__main__":
    main()
