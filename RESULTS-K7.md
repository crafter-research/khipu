# K7 results (2026-11-18)

PREREG locked in `b9486c6` (local only, no remote). Script committed after the lock. Output `results/k7.json`, draws in `results/k7_ckpt/` (not committed). Runtime about 3 minutes.

## Verdict: fails in both subsets. K5a is withdrawn as a claim.
| | AS (Ascher tradition) | UR (Urton tradition) |
|---|---|---|
| Khipus / cords | 56 / 5,306 | 202 / 23,230 |
| Real bits per cord (khipu-weighted) | 0.991 | 1.021 |
| Null mean, 95% interval | 1.007, [1.000, 1.013] | 1.037, [1.033, 1.041] |
| 1. Below the null's 2.5th percentile | yes | yes |
| 2. Gain at least 0.02 bits | **no** (0.016) | **no** (0.016) |
| 3. Over half of khipus positive | yes (75%) | yes (58%) |
| Passes | no | no |

## Reading
- With the layout controlled, color still beats the 200 shuffles in both traditions, and in most khipus. So a signal exists, and it is not a convention of only one tradition.
- But its size, about 0.016 bits per cord (roughly 1.5% of the 1 bit the model spends per cord), is below the 0.02 we fixed before running. By our own rule the claim "each khipu has a color legend" is withdrawn. We do not move the threshold after seeing the result.
- What can be said: color carries a small, consistent amount of khipu-local information about value magnitude beyond position, in both recording traditions. Too small to call a legend.

## Status of the trajectory
- Withdrawn: K5a (local legend), K6 (totals marked by color, band artefact).
- Standing: the OKR tens-as-hundreds coding on KH0326 (confirmed against Urton's Appendix B); Urton's 367 = 359 + two imputed broken cords.
- Open: whether the 381 in the literature is a misprint for 281 (needs the English edition, p. 229).
