"""K3.2: Santa first cords vs the 1670 tribute, Khipu Field Guide values. See prereg/K3.2.md."""

import hashlib
import json
import re
import sys
from pathlib import Path

import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
KFG = ROOT / "data/kfg"
OUT = ROOT / "results"
SANTA = {"KH0323": "UR087", "KH0324": "UR088", "KH0325": "UR089",
         "KH0326": "UR090", "KH0327": "UR091", "KH0328": "UR092"}
MU2018_TABLE1 = {"UR087": (48, 0), "UR092": (10, 0), "UR088": (0, 9),
                 "UR089": (0, 34), "UR091": (0, 15), "UR090": (5, 12)}
GROUP_RE = re.compile(r"group of (\d+) pendants? \((\d+)(?:-(\d+))?\)")


def read(name: str):
    path = KFG / f"{name}.xlsx"
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = list(wb["Cords"].iter_rows(values_only=True))
    cords = pd.DataFrame(rows[1:], columns=rows[0])
    cords = cords[cords["Cord_Name"].astype(str).str.fullmatch(r"p\d+")].copy()
    cords["n"] = cords["Cord_Name"].str[1:].astype(int)
    cords["value"] = pd.to_numeric(cords["Value"], errors="coerce")
    groups = []
    for (line,) in wb["CordGroups"].iter_rows(values_only=True):
        m = GROUP_RE.search(str(line or ""))
        if m:
            a = int(m.group(2))
            b = int(m.group(3) or a)
            groups.append((int(m.group(1)), a, b))
    return cords.set_index("n"), groups, hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    firsts, notes, hashes = [], [], {}
    for name, inv in SANTA.items():
        cords, groups, sha = read(name)
        hashes[name] = sha
        for size, a, b in groups:
            members = [n for n in range(a, b + 1) if n in cords.index]
            if len(members) != size:
                notes.append({"khipu": inv, "group": f"{a}-{b}", "declared": size, "found": len(members)})
            if len(members) == 1:
                notes.append({"khipu": inv, "single": a})
                continue
            for i in range(len(members) // 6):
                n = members[i * 6]
                r = cords.loc[n]
                firsts.append({"inv": inv, "pendant": n, "attachment": r["Attachment"],
                               "value": r["value"], "termination": r["Termination"]})
            if len(members) % 6:
                notes.append({"khipu": inv, "group": f"{a}-{b}", "remainder": len(members) % 6})
    f = pd.DataFrame(firsts)
    missing = int(f["value"].isna().sum())
    f["value"] = f["value"].fillna(0).astype(int)
    total = int(f["value"].sum())
    att = f.groupby("attachment")["value"].agg(["sum", "count"])
    get = lambda a, c: int(att.loc[a, c]) if a in att.index else 0  # noqa: E731
    verso, recto, n_v, n_r = get("V", "sum"), get("R", "sum"), get("V", "count"), get("R", "count")
    per_khipu = []
    for inv, g in f.groupby("inv"):
        per_khipu.append({"inv": inv, "groups": len(g), "recto": int((g["attachment"] == "R").sum()),
                          "verso": int((g["attachment"] == "V").sum()),
                          "mu2018_recto_verso": MU2018_TABLE1[inv], "value_sum": int(g["value"].sum()),
                          "values": {int(k): int(v) for k, v in g["value"].value_counts().sort_index().items()}})
    res = {
        "sha256": hashes,
        "groups": int(len(f)),
        "structure_notes": notes,
        "first_cords_value_missing": missing,
        "first_cords_value_zero": int((f["value"] == 0).sum()),
        "first_cords_broken": int((f["termination"] == "B").sum()),
        "K3a": {"total": total, "diff_to_367": total - 367, "diff_to_467": total - 467,
                "survives": abs(total - 367) < abs(total - 467)},
        "K3b": {"verso_total": verso, "recto_total": recto, "survives": verso in (381, 382) and recto == 86},
        "K3c": {"recto_first": n_r, "verso_first": n_v, "other": int(len(f) - n_r - n_v),
                "survives": n_r == 63 and n_v == 70},
        "per_khipu": per_khipu,
        "first_cord_values": {int(k): int(v) for k, v in f["value"].value_counts().sort_index().items()},
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "k3_2.json").write_text(json.dumps(res, indent=2, default=str))
    print(json.dumps(res, indent=2, default=str))


if __name__ == "__main__":
    sys.exit(main())
