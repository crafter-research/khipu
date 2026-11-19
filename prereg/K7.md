# PREREG K7: the local color legend under a layout control, replicated by recording tradition

Status: LOCKED 2026-11-18. Design by Fable's hostile review (`REVIEW-FABLE-TRAJECTORY.md`); thresholds approved by the author (0.02 bits and 50%). Not pushed to a remote: the repository was kept local, so the lock time is only verifiable from local history.

## Belief
Cord color predicts value class on held-out clusters beyond the local layout, and it does so separately in khipus recorded in the Ascher tradition (AS) and in the Urton tradition (UR).

## Data
- OKR v2.1.0 (same sha256), `k2.load()`, four value classes.
- Subsets by the upper-cased prefix of `khipu_main.INVESTIGATOR_NUM`: AS and UR. Other prefixes (HP, JC, QU, LL) excluded.
- Also excluded: the Santa khipus (KH0323 to KH0328), KH0472 and KH0401 (suspected OKR coding issue), and khipus with fewer than 30 knotted cords or fewer than 2 clusters (thresholds from the review).

## Model
- As in K5 (`k5.fit_bits`: logistic regression, K1 allowed features, local color prior keyed by (khipu, full color), leave-own-cluster-out for training rows).
- Plus a **local layout prior**: the same construction keyed by (khipu, `cord_level`, `CLUSTER_ORDINAL`). `CLUSTER_ORDINAL` is the cord's position inside its cluster (checked on KH0001: it runs 1..n within each cluster). This is the review's "(khipu, level, ordinal)" read as position within the cluster, since a key on the khipu-wide ordinal would be unique per cord.
- 5-fold GroupKFold by (khipu, cluster), run separately inside each subset.

## Null
Colors permuted within each (khipu, cluster), 200 draws (seeds 1 to 200), same model and folds.

## Statistic
Mean bits per cord per khipu, then averaged with equal weight per khipu.

## Decision rule
K7 survives only if, in AS **and** in UR:
1. the real khipu-weighted bits are below the 2.5th percentile of the null,
2. the khipu-weighted gain (null mean minus real) is at least 0.02 bits per cord, and
3. more than half of the khipus have a positive gain (their own null mean minus their real bits).

Kill: if it fails in one subset, the legend is a recording convention of the other tradition. If it fails in both, K5a is withdrawn.

## Seen before locking (declared)
- K5a aggregate gain 0.054 on the full corpus.
- Reviewer's check: 0.036 with a position prior (8 draws, full corpus).
- `robust_clean.json` (K1 T2 and K2b on a KFG-agreeing subset).
- Santa +0.30 (exploratory, K2a).
- No per-khipu or per-tradition breakdown of K5a has been seen.
