# PREREG K4: running totals in seriated cord groups

Status: LOCKED 2026-11-18. Approved by the author. Committed before the K4 analysis ran.

## Where the idea came from (declared)
In Urton (2017) Appendix B, on UR90 (Santa), position 2 of consecutive six-cord groups rises down a band (15, 22, 28, 34, 38, 46, 52, 59), and position 4 rises too. I also saw parts of the same appendix for UR91, UR92, UR87, UR89 and UR88. **The Santa khipus generated the hypothesis, so they cannot test it.** They are excluded from the confirmatory test and reported separately as non-blind.

Prior work: Radicati (1964) described "seriation" in khipus, and seriated groups (a color pattern that repeats with a fixed period) are a known structure. What is not established, as far as I know, is whether values at a fixed position inside the repeating unit trend upward across units, as running totals would.

## Belief
In seriated pendant groups outside Santa, the value at a fixed position of the repeating unit tends to increase from one unit to the next more than it would if the units were in random order.

## Data
Khipu Field Guide workbooks already downloaded (611 khipus), pendants only (`p<n>`), groups from `CordGroups`, values from `Value`, colors from `Color`.

## Definitions (fixed now)
- Seriated group: a KFG group whose pendant color sequence repeats exactly with some period p between 2 and 12, with at least 3 complete repeats. Use the smallest such p. Pendants past the last complete unit are dropped.
- Series: for a seriated group and a position j in 1..p, the sequence of values at position j across units.
- Trend of a series: Kendall tau between unit index and value. Series that are constant are excluded (tau undefined) and counted.
- Statistic: mean tau over all included series.

## Null and decision rule
- Null: shuffle the order of units within each group (one permutation per group, applied to all its positions, so the structure inside a unit is kept). 2,000 shuffles, seed 0.
- Survives if the observed mean tau is above the null in at least 95% of shuffles (one-sided p < 0.05). Killed otherwise.
- Also reported: the share of series with tau > 0 and with tau < 0, and the result per period p.

## Secondary, non-blind
The same statistic on the six Santa khipus, labeled as non-blind.

## Threats
- Colors are recorded by different investigators, and exact repetition may miss real seriation. Report how many groups qualify.
- A few large khipus could dominate. Report the result with each khipu weighted equally as well.
- An upward trend can come from sorting, not accumulation. K4 tests the trend only. Whether increments equal other cords would need a later belief.
