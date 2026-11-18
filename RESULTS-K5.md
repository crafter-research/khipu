# K5 results (2026-11-18)

PREREG locked in `d567355`. Script commit after the lock (local prior made leave-own-cluster-out for training rows and vectorized before the first run). Output `results/k5.json`, per-draw checkpoints in `results/k5_ckpt/` (not committed). Runtime about 10 minutes.

Declared: a timing check before the run printed the real-color bits of one K5a fold (1.072 vs marginal 1.583). Nothing in the design changed after it.

## Verdict
- **K5a, local legend: survives, in both runs.**
  - All khipus (593, 37,082 cords): real 1.094 bits per cord; the 200-draw null has mean 1.148 and 95% interval [1.145, 1.152]. Every null draw is worse than real (p < 0.005). Gain +0.054 bits per cord.
  - KFG-verified khipus (507, 29,416 cords): real 1.072; null mean 1.132, interval [1.128, 1.136]. Gain +0.060.
  - Calibration gate passed: the model beats the marginal (1.59 to 1.60 bits) in both runs.
- **K5b, no transfer across khipus: not survived as stated, but in the belief's direction.**
  - Real colors are worse than shuffled colors when khipus are held out: gain -0.016 (all) and -0.011 (clean), above the null's 95% interval. The PREREG named two outcomes (inside the interval: survives; below it: killed); this is a third.
  - Reading: a color code learned on other khipus does not merely fail to transfer, it misleads. This agrees with K1 T1.

## Claim
Within a khipu, cord color predicts the magnitude of the cord's value beyond cluster and position. The test uses whole held-out clusters, a calibrated model and a 200-draw permutation null, and holds on KFG-verified values. A color code learned across khipus is worse than no code.

Credence: high for K5a; moderate for the cross-khipu reading.

## Size
The color-specific gain is about 0.05 to 0.06 bits per cord, roughly 3.5% of the marginal's 1.6 bits. Real, consistent, small.
