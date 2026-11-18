"""Inline SVG for the K7 result: bits saved over 200 color shuffles, per tradition, with the
preregistered minimum. Colors come from the site's CSS tokens so the figure follows the theme."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LABELS = {
    "en": {"AS": "Ascher khipus (56)", "UR": "Urton khipus (202)", "obs": "Observed", "null": "200 colour shuffles",
           "min": "Minimum we set: 0.02", "axis": "Bits per cord saved over shuffled colours"},
    "es": {"AS": "Khipus Ascher (56)", "UR": "Khipus Urton (202)", "obs": "Observado", "null": "200 barajados de color",
           "min": "Mínimo fijado: 0,02", "axis": "Bits por cuerda ahorrados frente a colores barajados"},
}
W, H, L, R = 720, 250, 170, 30
X0, X1 = -0.015, 0.025


def x(v: float) -> float:
    return L + (v - X0) / (X1 - X0) * (W - L - R)


def svg(lang: str) -> str:
    t = LABELS[lang]
    data = json.loads((ROOT / "results/k7_figure_data.json").read_text())
    fmt = (lambda v: f"{v:+.3f}".replace(".", ",")) if lang == "es" else (lambda v: f"{v:+.3f}")
    tick = (lambda v: f"{v:.2f}".replace(".", ",")) if lang == "es" else (lambda v: f"{v:.2f}")
    p = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{t["axis"]}" '
         f'style="width:100%;height:auto;font-family:var(--font-sans);font-size:13px">']
    for v in (-0.01, 0.0, 0.01, 0.02):
        p.append(f'<line x1="{x(v):.1f}" x2="{x(v):.1f}" y1="30" y2="200" style="stroke:var(--color-border);stroke-width:1"/>')
        p.append(f'<text x="{x(v):.1f}" y="218" text-anchor="middle" style="fill:var(--color-muted)">{tick(v)}</text>')
    p.append(f'<line x1="{x(0.02):.1f}" x2="{x(0.02):.1f}" y1="30" y2="200" '
             f'style="stroke:var(--color-muted-strong);stroke-width:1.5;stroke-dasharray:4 4"/>')
    p.append(f'<text x="{x(0.02) - 6:.1f}" y="24" text-anchor="end" style="fill:var(--color-muted-strong)">{t["min"]}</text>')
    for row, (sub, y) in enumerate((("AS", 85), ("UR", 155))):
        p.append(f'<text x="0" y="{y + 4}" style="fill:var(--color-text);font-weight:600">{t[sub]}</text>')
        for i, g in enumerate(data[sub]["null_gain"]):
            dy = ((i * 7) % 11 - 5) * 2.2
            p.append(f'<circle cx="{x(g):.1f}" cy="{y + dy:.1f}" r="2.5" style="fill:var(--color-muted);opacity:0.55"/>')
        rg = data[sub]["real_gain"]
        p.append(f'<rect x="{x(rg) - 2:.1f}" y="{y - 16}" width="4" height="32" rx="2" style="fill:var(--color-accent)"/>')
        p.append(f'<text x="{x(rg) - 8:.1f}" y="{y - 20}" text-anchor="end" style="fill:var(--color-text)">{t["obs"]} {fmt(rg)}</text>')
        if row == 0:
            p.append(f'<text x="{x(0):.1f}" y="{y + 30}" text-anchor="middle" style="fill:var(--color-muted)">{t["null"]}</text>')
    p.append(f'<text x="{(L + W - R) / 2:.1f}" y="242" text-anchor="middle" style="fill:var(--color-muted)">{t["axis"]}</text>')
    p.append("</svg>")
    return "".join(p)


if __name__ == "__main__":
    print(svg(sys.argv[1] if len(sys.argv) > 1 else "en"))
