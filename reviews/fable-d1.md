# Independent review of card D1 (Fable, claude-fable-5-2), 2026-11-18

Reviewer read PREREG, PREREG-K2, scripts, results JSON and the audit. It did not read RESULTS or NOTE files.

## Verdict
- D1 is killed on its own terms for what was tested: K1 T1 gain is negative (-0.207 vs marginal, -0.076 vs null).
- The instrument is weak. Checked against the code:
  - `scripts/k1.py:88-90`: default `HistGradientBoostingClassifier`, early stopping on a random in-distribution split, no shrinkage. The model loses to the marginal under shift: miscalibration, not evidence of absence.
  - `scripts/k1.py:64-71`: one color permutation (seed 0). The CIs are a bootstrap over groups, not the permutation-null interval the card names.
  - 218 of 260 "provenance" groups are unknown-provenance singletons, and site names are not normalized.
  - Knot direction (in the card) was excluded as leakage; the target is 4 classes.
- **K2a is an artefact, not a kill**: `bits_real` 4.20 on a four-class task where a uniform guess costs 2.0. Reclassified as untested.
- Survivors (K1 T2, K2b) are real but small, about 3% of 1.3 bits, and their significance also rests on a single permutation draw.

## Restated card (proposed next test, K5)
- Belief: within a khipu, cord color predicts value magnitude beyond cluster membership and position; no color code transfers across khipus.
- Oracle: bits per cord on held-out whole clusters, against a distribution of at least 200 within-cluster permutations, with a model calibrated to be no worse than the marginal.
- Killed if: the real gain falls inside the null's 95% interval, or vanishes on KFG-verified values.
