# PREREG K6: do totals have their own color?

Status: LOCKED 2026-11-18. Approved by the author. Committed before the K6 analysis ran.

## Why
K5 showed that color carries khipu-local information about value magnitude, but not what it encodes. K6 asks one concrete question with an arithmetic oracle: is a cord that records the sum of other cords marked by a color that differs from the cords it sums?

## Belief
Within a khipu, a pendant that is the sum of other pendants has a color that is absent from its summands more often than it would be if colors were assigned at random within the khipu.

## Oracle: sum relations from the Khipu Field Guide
- Source: the KFG "Pendant Pendant Sums" page of each khipu (`notebook/fieldmarks/pendant_pendant_sum/html/<KH>.html`), right-handed and left-handed tables. The KFG finds these relations from knot values alone, so they do not depend on color. Using its published list avoids choosing our own thresholds.
- Each relation gives a sum cord and its summands, both as `g<group>p<k>` with color.
- Cord names map to pendants as p = (first pendant of group) + k - 1, using the `CordGroups` sheet. A relation where any mapped pendant's color disagrees with the page is dropped and counted.

## Seen before this draft (declared)
- KH0326: its sum page, including that the 172-valued RB cord sums cords of other colors. KH0326 is excluded from the confirmatory set.
- KH0100: only that its page is nearly empty. No other sum page was read.

## Statistic
- For each relation, D = 1 if the sum cord's color appears in none of its summands, else 0.
- Primary statistic: mean D over all relations in the confirmatory set.
- Also reported: the same statistic counting each sum cord once (mean over its relations), and per khipu.

## Null and decision rule
- Null: permute pendant colors within each khipu, keeping relations fixed, and recompute the statistic. 200 draws, seeds 1 to 200.
- Survives if the observed statistic is above the 97.5th percentile of the null. Killed if inside the null's 95% interval. Below the 2.5th percentile is reported as the opposite pattern (totals share their summands' colors).

## Threats
- Small values produce sums by chance. The KFG's lists may include coincidental relations. These add noise to D and weaken the test; they cannot create a color difference under the null.
- Overlapping relations: one cord can be a sum in several relations. Reported with the per-cord version.
- Color codes vary by recorder. Permutation is within khipu, so a recorder's color vocabulary is preserved.
