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
