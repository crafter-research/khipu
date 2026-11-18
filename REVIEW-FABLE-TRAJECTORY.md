# Hostile review of the K1-K6 trajectory (Fable, claude-fable-5-2), 2026-11-18

Read-only review of commits, PREREGs, results, scripts and data.

## Process
- No remote: lock timestamps are not verifiable by third parties.
- Scripts were often written at the same time as the lock (K3.1 same mtime; K4 1 s; K5 22 s). The lock precedes results, not the executable design.
- K5 is the third test of the same hypothesis on the same cords (K1 T2, K2b, K5a). `robust_clean.json` showed the result on the clean subset before K5 was locked. K5 changed the prior after the lock and saw one fold.
- K6: "killed" was seen, then the fix flipped it to "survives". Color normalization was also after the lock.
- K3 needed three definitions before K3a "survived" on a trivial rule. RECONCILE-URTON is post-hoc accounting.
- About 15 tests; Holm applied only inside K1 and K2. No global correction.

## Technical (checked by the reviewer)
- **K6 is an artefact of color bands.** Summands are contiguous in 100% of relations, the total sits a median of 16 cords away. Permuting colors across the whole khipu destroys spatial autocorrelation. Under a circular-rotation null, observed 0.405 falls below the null (mean 0.421, 95% [0.408, 0.432]); per-khipu excess drops to +0.011, CI [-0.015, +0.037]. **K6 is retracted.** Independently reproduced by Kai: rotation null mean 0.422, 95% [0.411, 0.435], 200 draws.
- **K5a confounds color with layout.** Adding a local position prior (khipu, level, ordinal) cuts the gain from 0.054 to 0.036 (8 draws, all worse than real).
- **OKR and KFG are not independent**: same Harvard KDB lineage (Brezine). "KFG-verified" verifies nothing. The tens-as-hundreds bug has an external oracle (Urton Appendix B) only for KH0326.
- **The recorder check used the wrong variable**: `CREATED_BY` is who typed the data, not the field recorder. The Ascher vs Urton confound was never tested.
- Effects are 2-3% of 1.6 bits; heterogeneity by khipu not reported for K5.

## What stands, by credence
1. OKR codes tens as hundreds on KH0326 (high).
2. Urton's 367 = 359 + two imputations (high, but it is reading Urton).
3. Color predicts magnitude within a khipu, 0.036 bits after a position control (medium; may be layout or recording convention).
4. The bug on KH0472 and KH0401 (medium-low, no independent source).
5. 381 as a misprint for 281 (low-medium).
6. Color marks totals (near zero).

## Proposed next test: K7 (see PREREG-K7.md)
Local legend under a layout control, replicated separately in Ascher (AS) and Urton (UR) khipus.

## Publish?
No. First retract K6, run K7 with the lock pushed to a remote, check Urton (2017, English) p. 229, and confirm the OKR bug against a non-KFG source.
