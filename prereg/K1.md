# PREREG K1: non-numeric cord attributes and knot values

Status: LOCKED 2026-11-17. Approved by the author. Committed before any outcome analysis.

## Belief
The non-numeric attributes of a cord (color, twist, attachment, hierarchy level, position) predict its knot value better than the value distribution alone, on khipus the model never saw.

## Data
- Open Khipu Repository v2.1.0, `data/khipu.db` from the GitHub tag `v2.1.0` (MIT).
- sha256 `607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db`.
- Counts reproduced: 619 khipus, 54,403 cords, 110,677 knots.
- Unit: a cord with at least one knot (37,206 cords). Cord value = sum of `knot.knot_value_type` over its knots.
- Looked at before this draft (marginals only, no attribute-by-value table): value range 0 to 320,535; 17,380 cords below 10, 13,781 two-digit, 4,728 three-digit, 1,317 four or more. Field coverage: twist recorded on 53,232 cords (8,261 of them `U`), color on 53,782 cords.

## Target
Primary: the value class of each cord in four bins: 0-9, 10-99, 100-999, 1000+.
Secondary: units digit (0-9) for cords with value under 100.

## Features allowed
Color (`ascher_cord_color.FULL_COLOR` and its first code), twist, attachment type, `CORD_LEVEL`, is-subsidiary, cluster ordinal, cord ordinal within cluster, fiber, termination.

## Features forbidden (leakage)
- Anything derived from knots: count, type, direction, turns, position.
- `CORD_LENGTH`, `ATTACH_POS`, `THICKNESS`: longer cords can physically hold more knots. Reported only as a separate ablation, never in the primary model.
- Values of other cords. Within-khipu sums (a top cord equal to the sum of pendants) would leak the answer.

## Split
- Primary (T1): grouped cross-validation by provenance. Khipus with empty or `unknown` provenance (218) form one group each. Fold count fixed in code before running.
- Secondary (T2): within-khipu. Hold out cords inside each khipu, to test whether color works as a local legend.

## Models
- Baseline B0: training-fold marginal of the target.
- Model M1: gradient-boosted trees on the allowed features.
- Null N1: M1 retrained with colors permuted within each khipu. Breaks the color-value link and keeps everything else.

## Metric
Mean log loss in bits per cord on held-out cords. Report also accuracy and per-class calibration.

## Decision rule
- Survives if M1 beats B0 and N1 in bits per cord, with a 95% bootstrap CI over held-out groups that excludes zero.
- Killed if the CI includes zero, or if the gain disappears when cluster ordinal and cord ordinal are removed (it would then be position, not attribute meaning).
- Either outcome is published in the claim ledger.

## Threats
- Recording conventions differ by investigator (Ascher, Harvard KDB, others). Check whether the gain survives grouping by `CREATED_BY`.
- Missing twist (`U`) and color codes vary by recorder.
- Museum collection bias (see arXiv 2607.00185, Section 4.1).
- Multiple comparisons between T1, T2 and the secondary target: Holm correction.

## Prior work checked
arXiv 2607.00185 (Contreras, 2026) works at khipu level (provenance classification, clustering, Santa Valley moiety replication). It lists positional value decoding and sequence models over knots as future work. It does not predict cord values from non-numeric attributes.
