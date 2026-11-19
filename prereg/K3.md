# PREREG K3: do the Santa Valley first cords add up to the 1670 tribute?

Status: LOCKED 2026-11-18. Approved by the author. Committed before any Santa cord value was computed.

## Context
- Six khipus from the Santa Valley (OKR KH0323 to KH0328, UR087 to UR092, Museo Temple Radicati) were matched to a 1670 revisita of San Pedro de Corongo (Medrano and Urton 2018, doi 10.1215/00141801-4260638; FitzPatrick 2024, doi 10.1215/00141801-11266328).
- The revisita states 132 tributaries (130 named, in six pachacas) and a total tribute of 367 pesos.
- Urton (2017, as quoted by FitzPatrick 2024) says the knot values of the first cord of the 133 six-cord groups add up to a total that "closely matches" 367 pesos.
- FitzPatrick 2024 (citing Urton 2017: 229) gives moiety totals of 381 or 382 pesos (verso) and 86 pesos (recto). Those add up to 467 or 468, not 367.
- arXiv 2607.00185 reproduced the recto/verso pattern from OKR and left the numeric match as future work.
- K1 and K2 found that cord color carries khipu-local information about value magnitude. K3 tests a published decipherment with an external oracle and does not reuse those results.

What I read before this draft: the two papers above. I have not computed any value, sum or count from the Santa cords.

## Beliefs
- **K3a, total.** The first-cord values of the six-cord groups, decoded from OKR, add up closer to 367 (the revisita total) than to 467 (the sum of the published moiety totals).
- **K3b, moieties.** Split by the attachment of the first cord, the verso total reproduces 381 or 382 and the recto total reproduces 86.
- **K3c, structure.** OKR contains 133 six-cord groups across the six khipus, with 63 recto and 70 verso first cords (Medrano and Urton 2018, table 1).

## Definitions (fixed now)
- Santa khipus: `khipu_main.PROVENANCE = 'Santa'` (KHIPU_ID 1000270 to 1000275).
- Six-cord group: a `CLUSTER_ID` on one of those khipus with exactly six level-1 cords (`CORD_LEVEL = 1`).
- First cord: the cord with the lowest `CORD_ORDINAL` in its group.
- Cord value: sum of `knot.knot_value_type` over the cord's knots. A first cord with no knots has value 0 and is counted separately.
- Attachment: `cord.ATTACHMENT_TYPE` of the first cord, with the codes read from `attachment_dc`.

## Decision rules
- K3a survives if |sum - 367| < |sum - 467|. Report the exact sum and both differences.
- K3b survives if the verso total is 381 or 382 and the recto total is 86. Otherwise report the actual totals.
- K3c survives if both counts match exactly. Otherwise report what OKR contains.
- Every outcome goes in the claim ledger, including the case where the published figures cannot be reproduced from the public database.

## Threats
- OKR may define clusters differently from the papers' six-cord groups. Report the size distribution of all Santa clusters.
- Broken cords: FitzPatrick notes the verso total is uncertain because of broken cords. Report first cords marked broken or with missing knots.
- Decoding: a value of 0 may be a real zero or missing data. Report both counts.
- Currency: 1 peso = 8 reales. Values are read as pesos, as in Urton 2017.
