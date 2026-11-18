"""K6: do sum cords (totals) have a color absent from their summands? See PREREG-K6.md."""

import json
import re
import sys
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
KFG = ROOT / "data/kfg"
SUMS = ROOT / "data/kfg_sums"
OUT = ROOT / "results"
N_DRAWS = 200
EXCLUDED = {"KH0326"}
GROUP_RE = re.compile(r"group of (\d+) pendants? \((\d+)(?:-(\d+))?\)")
CELL_RE = re.compile(r"(?:<b>)?(g\d+p\d+)(?:</b>)?\s*:\s*<span[^>]*><b>(-?\d+)</b></span><sub><small>([^<]*)</small></sub>")
ROW_RE = re.compile(r"<tr><td class=\"td_sum_counter\">.*?</tr>", re.S)


SEG_RE = re.compile(r"([^/()]+)\(([\d.]+)-([\d.]+)\)")


def main_color(c: str) -> str:
    """KFG pages show the color covering the longest stretch of a multi-segment cord."""
    segs = SEG_RE.findall(c)
    if not segs:
        return c
    span = {}
    for col, a, b in segs:
        span[col] = span.get(col, 0.0) + float(b) - float(a)
    return max(span, key=span.get)


def pendants(name: str):
    wb = openpyxl.load_workbook(KFG / f"{name}.xlsx", read_only=True, data_only=True)
    rows = list(wb["Cords"].iter_rows(values_only=True))
    df = pd.DataFrame(rows[1:], columns=rows[0])
    df = df[df["Cord_Name"].astype(str).str.fullmatch(r"p\d+")]
    colors = dict(zip(df["Cord_Name"].str[1:].astype(int), df["Color"].astype(str).map(main_color)))
    starts = []
    for (line,) in wb["CordGroups"].iter_rows(values_only=True):
        m = GROUP_RE.search(str(line or ""))
        if m:
            starts.append(int(m.group(2)))
    return colors, starts


def relations(name: str):
    path = SUMS / f"{name}.html"
    if not path.exists():
        return []
    html = path.read_text(errors="ignore")
    out = []
    for heading in ("Right Handed Sum Detail", "Left Handed Sum Detail"):
        i = html.find(heading)
        if i < 0:
            continue
        j, k = html.find("<table", i), html.find("</table>", i)
        for row in ROW_RE.findall(html[j:k]):
            cells = CELL_RE.findall(row)
            if len(cells) >= 3:
                out.append({"sum": cells[0], "summands": cells[1:]})
    return out


def to_pendant(gp: str, starts: list[int]) -> int | None:
    g, k = map(int, re.fullmatch(r"g(\d+)p(\d+)", gp).groups())
    if g < 1 or g > len(starts):
        return None
    return starts[g - 1] + k - 1


def stat(rel_idx, colors: np.ndarray) -> tuple[float, float]:
    d = np.array([colors[s] not in {colors[x] for x in xs} for s, xs in rel_idx], dtype=float)
    by_cord = pd.Series(d).groupby([s for s, _ in rel_idx]).mean()
    return float(d.mean()), float(by_cord.mean())


def main():
    names = sorted(p.stem for p in SUMS.glob("KH*.html"))
    per_khipu, dropped, total_rel = {}, 0, 0
    for name in names:
        if not (KFG / f"{name}.xlsx").exists():
            continue
        colors, starts = pendants(name)
        rels = relations(name)
        total_rel += len(rels)
        ok = []
        for r in rels:
            gp_all = [r["sum"]] + r["summands"]
            idx = [to_pendant(gp, starts) for gp, _, _ in gp_all]
            if any(i is None or colors.get(i) != c for i, (_, _, c) in zip(idx, gp_all)):
                dropped += 1
                continue
            ok.append((idx[0], idx[1:]))
        if ok:
            per_khipu[name] = (colors, ok)

    def pooled(keys, perm_seed=None):
        rel_all, col_all, offset = [], {}, 0
        rng = np.random.default_rng(perm_seed) if perm_seed is not None else None
        for k in keys:
            colors, ok = per_khipu[k]
            ids = sorted(colors)
            vals = np.array([colors[i] for i in ids], dtype=object)
            if rng is not None:
                vals = vals[rng.permutation(len(vals))]
            m = {i: offset + n for n, i in enumerate(ids)}
            for n, i in enumerate(ids):
                col_all[offset + n] = vals[n]
            rel_all += [(m[s], [m[x] for x in xs]) for s, xs in ok]
            offset += len(ids)
        arr = np.array([col_all[i] for i in range(offset)], dtype=object)
        return stat(rel_all, arr), len(rel_all)

    def test(keys):
        (obs, obs_cord), n = pooled(keys)
        null = np.array([pooled(keys, s)[0] for s in range(1, N_DRAWS + 1)])
        lo, hi = np.percentile(null[:, 0], [2.5, 97.5])
        lo_c, hi_c = np.percentile(null[:, 1], [2.5, 97.5])
        return {
            "khipus": len(keys), "relations": n,
            "mean_D": obs, "null_mean": float(null[:, 0].mean()), "null_95": [float(lo), float(hi)],
            "verdict": "survives" if obs > hi else "opposite pattern" if obs < lo else "killed",
            "per_cord_mean_D": obs_cord, "per_cord_null_95": [float(lo_c), float(hi_c)],
        }

    conf = [k for k in per_khipu if k not in EXCLUDED]
    res = {
        "sum_pages": len(names), "relations_parsed": total_rel, "relations_dropped_color_mismatch": dropped,
        "confirmatory": test(conf),
        "excluded_KH0326": test(["KH0326"]) if "KH0326" in per_khipu else None,
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "k6.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    sys.exit(main())
