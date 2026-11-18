# khipu

Preregistered tests on Inka khipus by [Crafter Research](https://crafter.ing), Lima.

Question: does the colour of a khipu cord tell you anything about the number knotted on it? Short answer after seven tests: a small, consistent signal inside each khipu (0.016 bits per cord with the layout controlled), below the 0.02 minimum we fixed beforehand, so we withdrew the "colour legend" claim. Write-up: [crafter.ing/research/khipu-colour-legend](https://crafter.ing/research/khipu-colour-legend).

## Read in this order
1. `NOTE.md`: summary and the table of every test.
2. `PREREG-K*.md`: each belief, oracle, null and kill condition, committed before its analysis.
3. `RESULTS-K*.md`: verdicts, deviations and what was seen before locking.
4. `REVIEW-FABLE-D1.md`, `REVIEW-FABLE-TRAJECTORY.md`: independent reviews that changed verdicts.
5. `AUDIT-OKR-KFG.md`, `RECONCILE-URTON.md`: data audit and the Santa Valley reconciliation.

## Reproduce
Requires [uv](https://docs.astral.sh/uv/).

```bash
mkdir -p data/okr-gh-v2.1.0
curl -sL -o data/okr-gh-v2.1.0/khipu.db https://raw.githubusercontent.com/khipulab/open-khipu-repository/v2.1.0/data/khipu.db
shasum -a 256 data/okr-gh-v2.1.0/khipu.db   # 607913034a0f478c5c792025d0c3cab8a9a8f05223ed6bc9c2990122a8c1c4db
sqlite3 -readonly data/okr-gh-v2.1.0/khipu.db "select OKR_NUM from khipu_main order by 1" > data/okr_nums.txt
mkdir -p data/kfg && cp data/okr_nums.txt data/kfg/okr_nums.txt
./scripts/fetch_kfg.sh        # Khipu Field Guide workbooks, 1 request per second
./scripts/fetch_kfg_sums.sh   # Khipu Field Guide sum pages
uv run python scripts/k7.py   # or any scripts/k*.py
```

Raw data is not committed; it downloads from its public sources. Results in `results/` are the committed outputs of each run.

## Sources
- Open Khipu Repository v2.1.0 (MIT), github.com/khipulab/open-khipu-repository
- Khipu Field Guide workbooks (MIT), khipufieldguide.com
- Medrano and Urton (2018), doi 10.1215/00141801-4260638; FitzPatrick (2024), doi 10.1215/00141801-11266328; Urton (2017), *Inka History in Knots*, University of Texas Press

## License
Code MIT. Text CC BY 4.0.
