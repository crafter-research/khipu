# K1 results (2026-11-17)

Run: commit `ee39487`, output `results/k1.json`. PREREG locked in `78fab74` before any outcome analysis.

## Verdict
- **Primary belief (T1, held out by provenance): killed.** The model is worse than the marginal baseline (-0.207 bits per cord, CI [-0.275, -0.133]) and worse than the permuted-color null (-0.076, CI [-0.099, -0.052]). The color-to-value mapping learned in some provenances misleads in others.
- **Secondary (T2, within khipu): survives.** Real colors beat permuted colors by +0.085 bits per cord (CI [+0.068, +0.104], Holm-adjusted p < 0.001 with 2,000 bootstrap draws over khipus). Without position features the gain stays at +0.055 (CI [+0.041, +0.070]), so it is not only position. Accuracy: 59.7% real colors, 56.2% permuted, 46.8% marginal.
- **Units digit (T1): killed.** No model beats the marginal.
- **Recorder grouping (threat check, 12 groups):** real vs permuted colors -0.047, CI [-0.087, +0.026]. No cross-recorder signal either.

## Claim
Within a khipu, cord color carries information about the magnitude of the cord's value beyond position and structure. Across provenances there is no shared color-to-value code that a model can transfer.

Credence: moderate. Next to rule out: color acting as a proxy for cluster membership when clusters share magnitudes for numeric, not semantic, reasons.

## Deviations from PREREG
- Expected 37,206 cords with knots. 124 knot records point to cord IDs missing from the `cord` table and were dropped. 7 rows were duplicated by ties in the color join. Analyzed rows: 37,089.
- `A2_physical` (with cord length) is reported in the JSON as declared and is not part of any verdict.

## Next belief (to preregister separately, not a rescue of K1)
K2: the color code is shared within a provenance. Leave one khipu out, train only on khipus from the same provenance. If it beats the permuted null, the legend is regional; if not, each khipu has its own legend.
