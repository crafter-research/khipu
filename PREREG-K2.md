# PREREG K2: is the color legend regional, and is it more than cluster membership?

Status: LOCKED 2026-11-17. Approved by the author. Committed before any K2 analysis.

## Context
K1 (`RESULTS.md`, commit `4984767`): no color-to-value code transfers across provenances; within a khipu, real colors beat permuted colors by +0.085 bits per cord. K2 asks two new questions. It does not reuse K1's verdicts.

## Beliefs
- **K2a, regional legend.** A model trained only on other khipus from the same provenance predicts a held-out khipu's value classes better with real colors than with colors permuted within each khipu.
- **K2b, more than cluster membership.** Within a khipu, real colors beat colors permuted *within each cord cluster*. That null keeps which colors sit in which cluster and breaks only the color-value link inside the cluster. If real colors still win, color carries information beyond marking the group.

## Data
- Same database and sha256 as K1.
- Fix from K1: one color row per cord, chosen by lowest `color_id` and then lowest rowid, so no duplicate rows.
- Cords whose IDs are missing from `cord` are dropped, as in K1.
- K2a eligible set: khipus with a known provenance (not empty, not `unknown`) whose provenance has at least two khipus with knots, since leave-one-out needs one khipu to train on. Measured before this draft: 35 provenances, 368 khipus. No outcomes were looked at.
- K2b: all cords with knots. `CLUSTER_ID` is recorded for every cord (14,843 clusters).

## Target, features, model, metric
As in K1: four value classes (0-9, 10-99, 100-999, 1000+), the same allowed and forbidden features, the same gradient-boosted trees and hyperparameters, bits per cord as the metric.

## Splits and nulls
- K2a: within each eligible provenance, leave one khipu out, training only on the other khipus of that provenance. Real colors vs colors permuted within each khipu, applied to train and test.
- K2b: the K1 T2 split (5-fold over cords, seed 0). Real colors vs colors permuted within each `(khipu, cluster)`.

## Decision rule
- For each belief, gain = null bits minus real bits per cord, with a 95% bootstrap CI over khipus (2,000 draws, seed 0).
- Survives if the CI excludes zero after Holm correction across K2a and K2b. Killed otherwise. Both outcomes go in the claim ledger.

## Threats
- K2a: small provenances give tiny training sets. Report the gain per provenance and the pooled gain. The verdict uses only the pooled gain.
- K2b: clusters of one cord cannot be permuted, so they contribute no difference. Report how many cords are in multi-cord clusters.
- Recorder effects: a provenance often has a single recorder, so a regional effect could be a recording effect. Report the recorders per provenance.
