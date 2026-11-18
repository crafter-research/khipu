# Data audit: OKR v2.1.0 vs Khipu Field Guide, KH0326 (UR090), 2026-11-18

Trigger: K3.1 found three-digit first-cord values on UR090 with an empty tens place (105, 202, 308...), outside the 0-13 range the papers report.

Second source: Khipu Field Guide Excel `KH0326.xlsx` (Ashok Khosla, MIT, written 2026-09-08, contributor Carrie Brezine), `Cords` sheet, `Value` column. Saved to `data/kfg/` (not committed).

## Result
- 108 pendants in both sources, matched by pendant order.
- Exact value match: 43 of 108.
- After moving the OKR hundreds digit to the tens place when the tens place is empty: 106 of 108.
- The 2 remaining cords: OKR 206 vs KFG 116, and OKR 209 vs KFG 119 (two single-knot clusters both coded as hundreds).
- Example, pendant 2: KFG knots `1S(8.0cm) = 10; 5L = 5`, value 15. OKR value 105.

## Reading
OKR v2.1.0 codes single knots in the tens position as hundreds on this khipu. Its `knot_value_type` is wrong for most UR090 cords. K3.1 totals are affected. K1 and K2 used OKR values for the whole corpus, so the size of this error across other khipus must be measured before trusting their value classes.

KFG also records a 2025 attachment change on this khipu (p91, recto to verso), which OKR v2.1.0 does not have. That may explain part of the one-cord gap in K3c.

# Corpus-wide audit (2026-11-18)

Script `scripts/audit_okr_kfg.py`, outputs `results/audit_okr_kfg.{json,csv}`. KFG workbooks for 611 of 619 OKR khipus (8 return 404). Pendants only; subsidiaries not audited.

- 545 khipus align (same pendant count in both sources), 63 do not (different pendant counts), 3 have no KFG file.
- Aligned pendants: 31,135. Same value in both sources: 30,118 (96.7%). Different: 1,017.
- 416 khipus agree on every pendant. 29 agree on under 90%.
- The tens-as-hundreds pattern explains 10% or more of pendants on only 3 khipus: KH0326 (43 to 106 of 108), KH0472 (99 to 130 of 130) and KH0401 (12 to 14 of 15). The other disagreements are of other kinds (for example KH0593, where OKR is lower on all 57 pendants, and KH0034, with 189 of 415 matching).

## Robustness of K1 and K2 (declared after the audit, not preregistered)
`scripts/robust_clean.py`, output `results/robust_clean.json`. Rerun of the surviving within-khipu tests on the 507 khipus whose pendants agree at least 90% with KFG (29,416 cords):
- K1 T2, real vs colors permuted within khipu: +0.083 bits per cord, CI [+0.066, +0.102]. Full corpus was +0.085.
- K2b, real vs colors permuted within cluster: +0.044, CI [+0.030, +0.059]. Full corpus was +0.043.

Both survive essentially unchanged. The OKR value errors do not drive the color signal.
