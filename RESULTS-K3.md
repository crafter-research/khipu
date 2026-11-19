# K3 results (2026-11-18)

PREREG locked in `bfcac9e`, script `00d41b6`, output `results/k3.json`.

## Verdict: the test did not run as intended
The preregistered definition of a six-cord group (an OKR `CLUSTER_ID` with exactly six level-1 cords) does not reconstruct the groups in the papers. OKR has 39 such clusters, not 133. Most Santa level-1 cords sit in larger clusters of 12, 24, 36, 42, 48, 54, 60 or 66 cords, which are multiples of six, plus two clusters of 38 and 52 and 20 single cords. OKR seems to record the color bands that span several six-cord groups as one cluster.

- K3c (structure): killed as stated. 39 groups, 34 recto and 5 verso first cords.
- K3a and K3b: not interpretable. The rule says K3a survives (total 55, closer to 367 than to 467), but 55 comes from 39 of 133 groups. No claim is made about 367 or 467.

## What the run did show
- The 34 recto first cords found, all on UR087, have value 1. This agrees with Medrano and Urton (2018), who say every first cord on UR087 records 1.
- Data quality on those first cords: 0 without knots, 1 broken.

## Deviation and next step
A new PREREG (K3.1) is needed with a group definition that chunks clusters into consecutive runs of six cords by `CORD_ORDINAL`. Seen before writing it: the cluster size distribution above and the 39 first-cord values. Both must be declared there.
