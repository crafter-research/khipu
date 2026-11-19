"""Draw a khipu as SVG from its Khipu Field Guide workbook and the OKR colour table.

Pendants hang from the primary cord in their recorded colours (two-colour cords as stripes),
lengths to scale, and knots drawn where they were recorded: single knots as dots, long knots
as short bars sized by turns, figure-eight knots as rings."""

import re
import sqlite3
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data/okr-gh-v2.1.0/khipu.db"
KNOT_RE = re.compile(r"(\d+)([SLE]+)\(([\d.]+)")
SEG_RE = re.compile(r"([^/()]+)\(([\d.]+)-([\d.]+)\)")


def palette() -> dict[str, str]:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    rows = con.execute("select AS_COLOR_CD, R_DEC, G_DEC, B_DEC from ascher_color_dc").fetchall()
    con.close()
    return {c: "#%02x%02x%02x" % tuple(round(v * 255) for v in (r, g, b)) for c, r, g, b in rows if r is not None}


def main_color(c: str) -> str:
    segs = SEG_RE.findall(c)
    if not segs:
        return c
    span: dict[str, float] = {}
    for col, a, b in segs:
        span[col] = span.get(col, 0.0) + float(b) - float(a)
    return max(span, key=span.get)


def draw(name: str, out: Path, scale: float = 7.0, gap: float = 7.0) -> None:
    pal = palette()
    wb = openpyxl.load_workbook(ROOT / f"data/kfg/{name}.xlsx", read_only=True, data_only=True)
    rows = list(wb["Cords"].iter_rows(values_only=True))
    cords = [r for r in rows[1:] if re.fullmatch(r"p\d+", str(r[0]))]
    starts = []
    for (line,) in wb["CordGroups"].iter_rows(values_only=True):
        m = re.search(r"(?:group of \d+ pendants?|^\S+\s+\d+) \((\d+)", str(line or "").strip())
        if m:
            starts.append(int(m.group(1)))
    pad, top = 36, 46
    xs, x, prev = {}, pad, None
    for r in cords:
        n = int(str(r[0])[1:])
        if prev is not None:
            x += gap * (2.4 if n in starts else 1)
        xs[n], prev = x, n
    width = x + pad
    longest = max(float(r[4] or 0) for r in cords)
    height = top + longest * scale + pad

    def rgb(code: str) -> list[str]:
        parts = [p for p in re.split(r"[:\-]", main_color(str(code))) if p]
        return [pal.get(p, "#9aa59c") for p in parts] or ["#9aa59c"]

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" role="img" '
         f'aria-label="Khipu {name} drawn from its recorded cords">',
         f'<rect width="100%" height="100%" rx="14" fill="#0b1510"/>']
    prim = rgb(next((str(l[0]).split(":", 1)[1] for l in wb["PrimaryCord"].iter_rows(values_only=True)
                     if str(l[0]).startswith("Color:")), "W"))
    s.append(f'<line x1="{pad - 14}" x2="{width - pad + 14}" y1="{top}" y2="{top}" stroke="{prim[0]}" '
             f'stroke-width="5" stroke-linecap="round"/>')
    if len(prim) > 1:
        s.append(f'<line x1="{pad - 14}" x2="{width - pad + 14}" y1="{top}" y2="{top}" stroke="{prim[-1]}" '
                 f'stroke-width="5" stroke-dasharray="3 5" stroke-linecap="round"/>')
    for r in cords:
        n = int(str(r[0])[1:])
        cx, length = xs[n], float(r[4] or 0) * scale
        cols = rgb(r[7])
        y1 = top + length
        s.append(f'<line x1="{cx:.1f}" x2="{cx:.1f}" y1="{top}" y2="{y1:.1f}" stroke="{cols[0]}" '
                 f'stroke-width="3.2" stroke-linecap="round"/>')
        if len(cols) > 1:
            s.append(f'<line x1="{cx:.1f}" x2="{cx:.1f}" y1="{top}" y2="{y1:.1f}" stroke="{cols[1]}" '
                     f'stroke-width="3.2" stroke-dasharray="2 4"/>')
        for count, kind, pos in KNOT_RE.findall(str(r[3] or "")):
            ky = top + float(pos) * scale
            if kind == "S":
                for i in range(int(count)):
                    s.append(f'<circle cx="{cx:.1f}" cy="{ky + i * 4:.1f}" r="2.3" fill="#f3efe2"/>')
            elif kind == "L":
                s.append(f'<rect x="{cx - 2.6:.1f}" y="{ky:.1f}" width="5.2" height="{2.2 * int(count) + 2:.1f}" '
                         f'rx="2.4" fill="#f3efe2"/>')
            else:
                s.append(f'<circle cx="{cx:.1f}" cy="{ky:.1f}" r="2.6" fill="none" stroke="#f3efe2" stroke-width="1.4"/>')
    s.append("</svg>")
    out.write_text("".join(s))
    print(f"{out} {width:.0f}x{height:.0f}, {len(cords)} pendants")


if __name__ == "__main__":
    draw(sys.argv[1], Path(sys.argv[2]))
