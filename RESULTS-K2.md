# K2 results (2026-11-18)

PREREG locked in `464b70b`. Script `e228317` (same model and hyperparameters as K1; single-threaded fits, provenances in parallel, per-provenance checkpoints). Output `results/k2.json`. Rows: 37,082 (K1's 7 duplicate rows fixed).

## Verdict
- **K2a, regional legend: untested (reclassified 2026-11-18 after independent review, see REVIEW-FABLE-D1.md; the models score 4.2 bits on a 4-class task, worse than a uniform guess at 2.0).** Original verdict was killed. Training only on other khipus from the same provenance, real colors do not beat colors permuted within each khipu: gain -0.081 bits per cord, CI [-0.203, +0.032], Holm p = 0.93. 35 provenances, 368 khipus, 24,506 cords.
- **K2b, color beyond cluster membership: survives.** Within a khipu, real colors beat colors permuted inside each cord cluster: +0.043 bits per cord, CI [+0.031, +0.056], Holm p < 0.001. 30,258 of 37,082 cords sit in multi-cord clusters.

## Claim (combined with K1)
Inside a khipu, a cord's color carries information about the magnitude of its value, and part of that information is not explained by which cluster the cord belongs to. That information does not transfer to other khipus, not even from the same site. The evidence fits a legend local to each khipu.

Credence: moderate for K2b. K2a is a weak test (see below), so "no regional legend" is a killed belief, not a proven negative.

## Caveats
- K2a models are poorly calibrated on held-out khipus: 4.20 bits per cord with real colors and 4.12 with permuted, far above the roughly 1.6 of the marginal in K1. Small training sets overfit. The comparison is the preregistered one, but the test has little power.
- 7 leave-one-out folds had a single value class in training. Both variants used the marginal there, contributing zero difference.

## Exploratory, not a claim
Per-provenance gains (not part of the verdict): Santa +0.30 (6 khipus, 1 recorder), Nazca +0.20, Paracas +0.17, Pachacamac +0.01, Incahuasi -0.11, Ica -0.56. Santa is the valley whose khipus were matched to a 1670 census (Medrano and Urton 2018). Worth a separate preregistered look, with the single-recorder confound in mind.

## Deviations
- The first K2 run was stopped after almost 4 hours because of thread oversubscription and restarted with the performance patch. No result from the first run was read. Model, hyperparameters, seeds and splits are unchanged.
