# K4 results (2026-11-18)

PREREG locked in `115e1b0`, script `c4aa8bc`, output `results/k4.json`.

## Verdict: killed, and the definition did not capture what it meant to
- Confirmatory set (non-Santa): 862 groups, 1,272 non-constant series. Mean Kendall tau **-0.071**; the shuffled-order null averages +0.0002 with a 95th percentile of +0.027. One-sided p for an upward trend = 1.0. **Killed.**
- Weighted by khipu (162 khipus): mean tau -0.10; 35% of khipus positive.
- Santa (non-blind): mean tau +0.012, p = 0.45.

## Why the test is weaker than intended
844 of the 862 groups were detected with period 2, and 828 of those are groups of a single color. A uniform color sequence repeats with any period, so "smallest period = 2" turned plain single-color groups into two-cord "units". Only 16 period-2 groups truly alternate colors, and 18 groups have periods 3 to 12. The Santa six-cord units are also uniform in color inside a band, so the color-repeat definition could not find them either.

So K4 mostly measured the order of values along single-color groups, not running totals inside seriated units.

## What it did show (exploratory, not preregistered in this direction)
Values tend to **decrease** along cords within these groups (tau -0.07, far below the null). Descending arrangements may already be known in the khipu literature; check before claiming anything.

The few true seriated groups with periods 3, 4 and 12 have positive mean tau (0.10, 0.50, 0.35 on 21, 15 and 24 series). Far too few to conclude.

## Next
A running-totals test needs units defined by spacing or by the six-cord structure, not by color repetition. Candidate: the KFG `Position` and cord spacing data, or Urton-style unit sizes. New PREREG required.
