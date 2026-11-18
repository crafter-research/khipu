# Khipu colors carry a local legend: notes from six preregistered tests (draft, private)

Crafter Research, frontier stream. 2026-11-17 to 2026-11-18. Not published. Every claim below points to a locked PREREG, a script commit and a results file in this repository.

## Summary
- Within a khipu, a cord's color predicts the magnitude of its knot value better than the same colors shuffled, and the signal is not explained by which cluster the cord sits in. It does not transfer across provenances; whether it is shared within a site is still untested. K5 confirms it against a 200-draw permutation null with a calibrated model and whole held-out clusters (+0.054 bits per cord, every null draw worse), also on KFG-verified values.
- The best-known khipu decipherment, the Santa Valley match to a 1670 tribute census, reproduces in structure. Its exact total of 367 pesos depends on imputing two broken cords onto a measured 359. A moiety total quoted in the literature (381 or 382) is most likely a misprint for 281 or 282.
- The Open Khipu Repository (OKR) v2.1.0 agrees with the Khipu Field Guide on 96.7% of 31,135 comparable pendant values. On three khipus it codes the tens place as hundreds.

## Data
- OKR v2.1.0 (MIT), SQLite from the GitHub tag `v2.1.0`, sha256 `607913034a0f...`. 619 khipus, 54,403 cords, 110,677 knots.
- Khipu Field Guide (KFG) workbooks (MIT, Ashok Khosla), 611 of 619 khipus, downloaded 2026-11-18.
- Medrano and Urton (2018), FitzPatrick (2024), and Urton (2017, Spanish edition, chapter 12 and Appendix B).

## Method
Each belief was written as a falsifiable sentence with an oracle, a null and a decision rule, and committed before any outcome was computed. Deviations and anything seen beforehand are declared in each PREREG. Killed beliefs are reported with the same weight as surviving ones.

## Results
| ID | Belief | Verdict | Key number |
|---|---|---|---|
| K1 T1 | Non-numeric attributes predict value classes on khipus from unseen provenances | Killed | -0.207 bits per cord vs marginal |
| K1 T2 | The same, within a khipu | Survives | +0.085 bits vs colors shuffled within khipu, CI [+0.068, +0.104] |
| K2a | The color legend is shared within a provenance | Untested (models worse than uniform guessing) | -0.081, CI [-0.203, +0.032] |
| K2b | Color beats colors shuffled within each cluster | Survives | +0.043, CI [+0.031, +0.056] |
| K3 | Santa first cords match the 1670 tribute (OKR clusters as groups) | Not testable | group definition found 39 of 133 groups |
| K3.1 | Same, six-cord runs, OKR values | Killed | total 749, inflated by OKR coding on UR090 |
| K3.2 | Same, KFG values | K3a survives, K3b and K3c killed | total 398; moieties 278/118 vs 381/86; attachment 63/69 vs 63/70 |
| K4 | Values at a fixed position of seriated units trend upward | Killed | mean tau -0.071; 828 of 862 groups were single-color |
| K5a | Local legend: color beats 200 within-cluster shuffles on held-out clusters, calibrated model | Survives (both runs) | +0.054 bits (null 95% [1.145, 1.152] vs real 1.094); clean +0.060 |
| K5b | No color code transfers across khipus | Third outcome: real worse than null | -0.016; a cross-khipu code misleads |
| K6 | Totals (sum cords) carry a color absent from their summands | Survives | 0.405 vs null [0.360, 0.383]; khipu-weighted +0.062, CI [+0.031, +0.091]; heterogeneous |

Robustness (declared after the audit): on the 507 khipus whose pendants agree at least 90% with KFG, K1 T2 gives +0.083 and K2b +0.044.

## The Santa Valley case
- Urton's Appendix B gives position-1 sums per khipu of 48, 80, 101, 84, 36 and 10, total 359. Imputing two broken cords (4 or 5, and 4) gives 367/8. Fourteen first cords are zero; the other twelve stay at zero.
- Our 398 equals 359 plus 29 from our own run definition on UR90 (its bands of 38 and 52 pendants are not multiples of six) and 10 from two single-cord transcription differences (UR87 and UR92).
- With recto 86 and total 367/8, verso must be 281/282. FitzPatrick (2024, note 14) cites 381/382 from the English edition, p. 229. Confirming the misprint needs that page.

## Limits
- One transcription per source; recorder conventions differ.
- The local-legend result is statistical. It does not say what any color means.
- K2a had little power: small provenances overfit.
- Cord spacing is almost never recorded (0.008% of OKR pendants), so units cannot be defined by spacing. Running totals cannot be tested properly without new digitization.

## Next
1. Confirm 381 vs 281 in the English edition of Urton (2017), p. 229.
2. Report the OKR coding issue on KH0326, KH0472 and KH0401 to the maintainers (pending approval).
3. Santa as a key: test whether the color of each six-cord group maps to pachaca or person in the 1670 padron.
4. Digitization (catalog item D2): record cord spacing from photographs to unlock unit-level tests.
