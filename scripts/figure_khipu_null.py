"""Inline SVG: khipu-null ranking for the Santa Valley pattern, top 30 khipus, Santa highlighted.
Input: a khipu-null output directory (ranking.csv, summary.json)."""

import json
import sys
from pathlib import Path

import pandas as pd

SANTA = {"KH0323", "KH0324", "KH0325", "KH0326", "KH0327", "KH0328"}
TXT = {
    "en": {"santa": "Santa Valley khipu", "other": "Other khipus", "axis": "Rank among 328 khipus",
           "score": "Match score", "band": "Top 6 under the null"},
    "es": {"santa": "Khipu del valle de Santa", "other": "Otros khipus", "axis": "Puesto entre 328 khipus",
           "score": "Puntaje de coincidencia", "band": "Top 6 bajo el nulo"},
}


def svg(out_dir: Path, lang: str, n: int = 30) -> str:
    t = pd.read_csv(out_dir / "ranking.csv").head(n)
    s = json.loads((out_dir / "summary.json").read_text())
    tx = TXT[lang]
    W, H, L, R, T, B = 720, 300, 60, 20, 30, 60
    y0, y1 = 0.75, 1.005
    x = lambda r: L + (r - 0.5) / n * (W - L - R)  # noqa: E731
    y = lambda v: T + (y1 - v) / (y1 - y0) * (H - T - B)  # noqa: E731
    dec = (lambda v: f"{v:.2f}".replace(".", ",")) if lang == "es" else (lambda v: f"{v:.2f}")
    p = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{tx["score"]}" '
         f'style="width:100%;height:auto;font-family:var(--font-sans);font-size:13px">']
    for v in (0.8, 0.9, 1.0):
        p.append(f'<line x1="{L}" x2="{W - R}" y1="{y(v):.1f}" y2="{y(v):.1f}" style="stroke:var(--color-border)"/>')
        p.append(f'<text x="{L - 8}" y="{y(v) + 4:.1f}" text-anchor="end" style="fill:var(--color-muted)">{dec(v)}</text>')
    lo, hi = s["null_top_mean_95"]
    p.append(f'<rect x="{x(1) - 8:.1f}" y="{y(hi):.1f}" width="{x(6) - x(1) + 16:.1f}" height="{y(lo) - y(hi):.1f}" '
             f'rx="3" style="fill:var(--color-muted);opacity:0.18"/>')
    p.append(f'<text x="{x(1) - 8:.1f}" y="{y(lo) + 16:.1f}" style="fill:var(--color-muted-strong)">{tx["band"]}</text>')
    for r in t.itertuples():
        if r.score < y0:
            continue
        santa = r.khipu_id in SANTA
        style = "fill:var(--color-accent)" if santa else "fill:var(--color-muted);opacity:0.6"
        rad = 6 if santa else 4
        p.append(f'<circle cx="{x(r.rank):.1f}" cy="{y(r.score):.1f}" r="{rad}" style="{style}"><title>{r.khipu_id}</title></circle>')
    lx = W - R - 230
    p.append(f'<circle cx="{lx}" cy="{H - 18}" r="6" style="fill:var(--color-accent)"/>'
             f'<text x="{lx + 12}" y="{H - 14}" style="fill:var(--color-text)">{tx["santa"]}</text>')
    p.append(f'<circle cx="{L + 6}" cy="{H - 18}" r="4" style="fill:var(--color-muted);opacity:0.6"/>'
             f'<text x="{L + 16}" y="{H - 14}" style="fill:var(--color-text)">{tx["other"]}</text>')
    p.append(f'<text x="{(L + W - R) / 2:.0f}" y="{H - 38}" text-anchor="middle" style="fill:var(--color-muted)">{tx["axis"]}</text>')
    p.append("</svg>")
    return "".join(p)


if __name__ == "__main__":
    print(svg(Path(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else "en"))
