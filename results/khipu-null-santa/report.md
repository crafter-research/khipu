# khipu-null report: santa-valley-six-cord-tribute

khipu-null 0.1.0. 328 khipus scored, 1094 null draws each.

Tested features (field:null): first_cord_range (value:within_khipu).
Untested features (structure or whole-khipu distributions; they rank but cannot reach a low p): group_size.

Top 6 mean score 0.994. Picking the top 6 from null versions of every khipu gives [0.954, 0.986] (95%), p = 0.001.
Khipus with q <= 0.05 (Benjamini-Hochberg): 0.

| Rank | Khipu | Cords | Score | Null mean | p | q |
|---:|---|---:|---:|---:|---:|---:|
| 1 | KH0324 | 54 | 1.000 | 0.735 | 0.003 | 0.150 |
| 2 | KH0327 | 90 | 1.000 | 0.880 | 0.081 | 1.000 |
| 3 | KH0109 | 66 | 1.000 | 0.967 | 0.588 | 1.000 |
| 4 | KH0328 | 60 | 1.000 | 1.000 | 1.000 | 1.000 |
| 5 | KH0325 | 206 | 0.995 | 0.861 | 0.001 | 0.075 |
| 6 | KH0323 | 306 | 0.971 | 0.939 | 0.047 | 0.851 |
| 7 | KH0384 | 96 | 0.969 | 0.985 | 0.932 | 1.000 |
| 8 | KH0630 | 33 | 0.955 | 0.954 | 0.995 | 1.000 |
| 9 | KH0488 | 62 | 0.935 | 0.889 | 0.479 | 1.000 |
| 10 | KH0527 | 35 | 0.929 | 0.908 | 0.851 | 1.000 |

## What this does not prove

- A low p-value says the match is unlikely under this null, given the structure of each khipu. It does not say what the khipu means.
- Each feature is tested against its own null, which keeps groups, positions and levels fixed and moves only the field it reads. Structural features and whole-khipu distributions cannot be tested this way; they rank but never reach a low p-value.
- Colours are rotated along the khipu by default, which keeps colour bands intact. Shuffling colours cord by cord breaks bands and makes chance matches look rare.
- Choosing the best 5 of many khipus inflates scores. Read the top-k test and the q-values, not the raw scores.

If you use khipu-null, please cite it (see CITATION.cff): Crafter Research (2026), khipu-null, https://github.com/crafter-research/khipu-null
