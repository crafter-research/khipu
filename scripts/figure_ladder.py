"""Inline SVG: how much the colour signal shrank as each test got stricter, against the 0.02 line.
Values come from results/*.json (K1 T2, K2b, K5a, K7 averaged over AS and UR, khipu-weighted)."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "results"

STEPS = {
    "en": ["Colours shuffled inside each khipu", "Shuffled inside each group of cords",
           "Whole groups held out, 200 shuffles", "Cord position taken into account"],
    "es": ["Colores barajados dentro de cada khipu", "Barajados dentro de cada grupo de cuerdas",
           "Grupos enteros apartados, 200 barajados", "Posición de la cuerda descontada"],
}
TXT = {
    "en": {"min": "Minimum we set: 0.02", "axis": "Bits per cord gained from real colours", "label": "Colour signal per test"},
    "es": {"min": "Mínimo fijado: 0,02", "axis": "Bits por cuerda ganados con los colores reales", "label": "Señal del color por prueba"},
}


def values() -> list[float]:
    k1 = json.loads((R / "k1.json").read_text())["T2_class_within_khipu"]["M1_vs_N1"]["gain_bits_per_cord"]
    k2b = json.loads((R / "k2.json").read_text())["K2b"]["gain"]["gain_bits_per_cord"]
    k5 = json.loads((R / "k5.json").read_text())["all"]["K5a"]["gain_vs_null_mean"]
    k7j = json.loads((R / "k7.json").read_text())
    k7 = (k7j["AS"]["gain_khipu_weighted"] + k7j["UR"]["gain_khipu_weighted"]) / 2
    return [k1, k2b, k5, k7]


def svg(lang: str) -> str:
    v, t, steps = values(), TXT[lang], STEPS[lang]
    dec = (lambda x: f"{x:.3f}".replace(".", ",")) if lang == "es" else (lambda x: f"{x:.3f}")
    W, L, Rm, top, bh, gap = 720, 300, 70, 34, 26, 18
    H = top + len(v) * (bh + gap) + 40
    xmax = 0.1
    x = lambda val: L + val / xmax * (W - L - Rm)  # noqa: E731
    p = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{t["label"]}" '
         f'style="width:100%;height:auto;font-family:var(--font-sans);font-size:13px">']
    for i, (label, val) in enumerate(zip(steps, v)):
        y = top + i * (bh + gap)
        p.append(f'<text x="{L - 12}" y="{y + bh / 2 + 4:.0f}" text-anchor="end" style="fill:var(--color-text)">{label}</text>')
        p.append(f'<rect x="{L}" y="{y}" width="{x(val) - L:.1f}" height="{bh}" rx="4" '
                 f'style="fill:var(--color-accent);opacity:{1 if i == len(v) - 1 else 0.55}"/>')
        p.append(f'<text x="{x(val) + 8:.1f}" y="{y + bh / 2 + 4:.0f}" style="fill:var(--color-muted-strong)">{dec(val)}</text>')
    yb = top + len(v) * (bh + gap) - gap + 6
    p.append(f'<line x1="{x(0.02):.1f}" x2="{x(0.02):.1f}" y1="{top - 10}" y2="{yb}" '
             f'style="stroke:var(--color-muted-strong);stroke-width:1.5;stroke-dasharray:4 4"/>')
    p.append(f'<text x="{x(0.02) + 6:.1f}" y="{top - 14}" style="fill:var(--color-muted-strong)">{t["min"]}</text>')
    p.append(f'<line x1="{L}" x2="{L}" y1="{top - 6}" y2="{yb}" style="stroke:var(--color-border)"/>')
    p.append(f'<text x="{L}" y="{H - 10}" style="fill:var(--color-muted)">{t["axis"]}</text>')
    p.append("</svg>")
    return "".join(p)


if __name__ == "__main__":
    print(svg(sys.argv[1] if len(sys.argv) > 1 else "en"))
