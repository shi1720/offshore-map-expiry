# When Portfolio Maps Go Stale

Reproducible research by **Shivam Gupta**, Independent Researcher, India.

The paper studies the error from applying old issuer-nationality restatement matrices to current residence-based external portfolio positions. It uses real public financial data, not simulated market observations. Its main benchmark is an estimated contemporaneous map; results are not causal estimates of fragmentation.

- [Paper](paper/When_Portfolio_Maps_Go_Stale_Shivam_Gupta.pdf)
- [Initial analysis plan](ANALYSIS_PLAN.md)
- [Literature and design record](RESEARCH_NOTES.md)
- [Saved aggregate results](results/)
- [Independent verification](results/independent_verification.json)
- [Input provenance](data/sources.json)

## Main findings

For U.S. common equity, mean three-year staleness error is **3.12 percentage points** of total-variation distance; corporate bonds average **6.46 points**. Government bonds average **0.26 points**. China common-equity adjustment retains its direction in all eleven three-year comparisons, whereas several corporate-bond changes reverse direction. Updating five rows selected with earlier instability reduces common-equity mean error from **2.79 to 1.48 points** in the eight cases eligible for the refresh experiment.

The code includes 385 mathematical/accounting tests. A separate sparse-dictionary implementation verifies 495 historical comparisons and 1,980 country-exposure errors. Read the paper for definitions, source limitations, negative-position handling, and unfavorable comparator results.

## Reproduce

Use Python 3.9–3.12 and an internet connection for the initial source downloads. The study was executed with Python 3.9.6 on macOS; package versions are pinned.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/download_data.py
python src/analyze.py
python src/additional.py
python src/verify_independent.py
python -m pytest tests -q
python src/report.py
cd paper
tectonic main.tex
cp main.pdf When_Portfolio_Maps_Go_Stale_Shivam_Gupta.pdf
```

The GCAP input files total approximately 172 MB uncompressed. The downloader uses a compressed archive for the large matrix file, verifies source hashes, and excludes raw data from Git. Existing correct files are reused. A changed upstream file fails validation rather than silently substituting a new release. `tectonic` is needed only to compile the manuscript; the data analysis does not depend on LaTeX. An ordinary LaTeX distribution can also compile `main.tex` with two passes.

`make reproduce PYTHON=.venv/bin/python` runs the analysis, independent verification, tests and report generation after the downloads. The random seed is 1720406. The random refresh comparator averages 200 subsets per case and update budget.

## Audit another portfolio

`src/audit_exposure.py` accepts JSON with `weights`, `matrix`, `target_indices`, and `radii`. Weights are nonnegative and sum to one. Matrix rows are probability vectors. Radii are **explicit user assumptions** about row total-variation drift, not automatically calibrated confidence limits.

```json
{
  "weights": [0.7, 0.3],
  "matrix": [[0.8, 0.2], [0.1, 0.9]],
  "target_indices": [0],
  "radii": [0.05, 0.2]
}
```

```bash
python src/audit_exposure.py portfolio.json --refresh-count 1
```

This gives a sharp exposure interval under independent row TV restrictions and ranks equal-cost exact updates by the interval width they remove. It is a research reference implementation, without validated operational acquisition costs or future coverage guarantees.

## Files and definitions

| File | Contents |
|---|---|
| `results/errors.csv` | All dated-map comparators, distances, support and signed-position sensitivities |
| `results/targets.csv` | China, Russia, their union, and China plus Hong Kong; level errors and reversals |
| `results/decomposition.csv` | Exact annual residence-weight / within-residence-map accounting |
| `results/routes.csv` | Residence-row contributions to three-year error envelopes |
| `results/refresh.csv` | Selective refresh experiments and infeasible ex post reference |
| `results/reconciliation.csv` | Comparison with the source's ex-domestic restated positions |
| `results/enhanced.csv` | Alternative enhanced-fund map sensitivity |
| `results/route_sensitivity.csv` | Center-only and territorial-code exclusions |
| `results/fed_comparison.csv` | Independent common-stock comparison through 2024 |
| `results/audit.json` | Source hashes, row counts, cleaning ledger, and experiment dimensions |

The principal sample contains eleven books across eight investor economies/regions, each observed for 2007–2020. “External” is defined by issuer residence before restatement. Reassigned home-nationality exposure stays in the same book. Non-U.S. equities and Australia are excluded for documented comparability reasons. The euro-area book excludes a fixed end-2020 nineteen-country residence set. Missing entire map rows use identity and are explicitly measured; omitted sparse cells are zero. Negative positions are clipped only in the nonnegative baseline and retained in the signed sensitivity.

## Sources and rights

These data are based on the work in Coppola, Maggiori, Neiman and Schreger (2021) and were obtained from [the Global Capital Allocation Project](https://www.globalcapitalallocation.com/data). The independent U.S. comparison comes from [Bertaut, Bressler and Curcuru (2019), December 2025 update](https://www.federalreserve.gov/econres/notes/feds-notes/globalization-and-the-geography-of-capital-flows-20190906.html).

The MIT license covers this repository's original software only. Original GCAP data remain restricted to academic research and educational use; the derived research records are supplied for that purpose and do not confer commercial rights to the source data. Source papers retain their original copyrights. Commercial deployment of the methods requires appropriate data licenses. No patentability or acceptance claim is made.

## Citation

```bibtex
@unpublished{gupta2026portfoliomaps,
  author = {Gupta, Shivam},
  title = {When Portfolio Maps Go Stale: Offshore Restatement and Measured External Adjustment},
  year = {2026},
  note = {Research manuscript},
  url = {https://github.com/shi1720/offshore-map-expiry}
}
```
