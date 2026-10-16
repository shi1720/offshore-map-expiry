# Literature, design decisions, and limits

Research date: 16 October 2026. This is a focused literature and design record, not an externally preregistered protocol or a systematic-review claim.

## Contribution selected

**Question:** When current residence-basis portfolio stocks are combined with an older issuer-nationality composition, how large is the resulting measurement error, when does it reverse measured external adjustment, and can a limited number of map updates reduce it?

The new research object is the temporal validation and maintenance of public nationality-restatement matrices. Neither offshore issuance, the residence/nationality distinction, time variation in the matrices, probability-distance bounds, nor Shapley decomposition is new. The historical validation and selective-refresh experiment are the paper's narrow proposed contribution. The search did not locate an earlier study executing the same experiment. Unindexed or unpublished prior work remains possible.

## Closest literature and the boundary of this paper

| Work | Established contribution relevant here | What this paper adds or keeps distinct |
|---|---|---|
| [Coppola, Maggiori, Neiman and Schreger (2021)](https://doi.org/10.1093/qje/qjab014) | Investor-specific nationality restatement and explicit time-varying matrices | Evaluates the error from carrying a dated matrix forward; does not claim discovery of varying offshore composition |
| [GCAP matrix documentation](https://globalcapitalallocation.s3.us-east-2.amazonaws.com/RestatementMatrices_ReadMe.pdf) and [position documentation](https://globalcapitalallocation.s3.us-east-2.amazonaws.com/Restated_Bilateral_External_Portfolios_ReadMe.pdf) | Release coverage, methodology variants, source units, sparse representation, and missing-position conventions | Uses a pinned release, reports missing-map support and negative-position handling, and validates reconstruction |
| [Bertaut, Bressler and Curcuru (2019), updated data](https://www.federalreserve.gov/econres/notes/feds-notes/globalization-and-the-geography-of-capital-flows-20190906.html) | Independent security-level U.S. nationality estimates | Separates contemporaneous benchmark disagreement from mapping age; updates context through 2024 |
| [Jiang, Richmond and Zhang (2022), Appendix B.1.1](https://www.federalreserve.gov/econres/ifdp/files/ifdp1366.pdf) | Documents constant-map extensions before 2007 and after 2017 | Provides a historical diagnostic of this type of input extension; does not rerun their demand system or claim to overturn their conclusions |
| [Hudecz et al. (2024), Annex 3.1, p. 89](https://www.esm.europa.eu/publications/geoeconomic-fragmentation-implications-euro-area-and-asean3-regions) | Documents use of the 2021 map for 2022–2023 positions | Motivates a practically used extrapolation; our 2007–2020 study does not estimate their post-2022 error |
| [Beck et al. (February 2026)](https://globalcapitalallocation.s3.us-east-2.amazonaws.com/GCAP_ECB_OOFCs.pdf) | Jointly unwinds fund ownership and issuer nationality in the euro area | Our extension uses older issuer-side maps and does not reproduce ultimate-holder consolidation |
| [Airaudo et al. (2025)](https://doi.org/10.20955/r.2025.12) | Sensitivity of fragmentation conclusions to geopolitical distance measurement | Holds country sets explicit and studies a different input: the dated economic composition of residence positions |
| [Gourinchas and Rey (2007)](https://doi.org/10.1086/521966) and [Jiang et al. (2024)](https://doi.org/10.1111/jofi.13333) | External adjustment, portfolios, and global imbalances | Our accounting does not identify transaction versus valuation channels or estimate a full national external constraint |
| [Shorrocks (2013)](https://doi.org/10.1007/s10888-011-9214-z) | Established Shapley decomposition framework | Uses its symmetric two-factor specialization with no mathematical-priority claim |

Searches combined terms such as “stale reallocation matrices,” “nationality look-through out-of-sample,” “portfolio mapping drift,” “fragmentation reallocation matrices,” “offshore nationality measurement error,” and “restatement matrices temporal.” The original CMNS paper, its current documentation, the 2026 Beck revision, and the ESM annex were inspected directly. Several searches returned unrelated work; their absence of a match is not proof of novelty.

## Earlier work screened

Fifty-three earlier top-level manuscripts supplied by the author were screened by title, first-page text/abstract, and topic keywords. The closest themes concern financial-model routing, delegated deposit withdrawals, and trade-allocation measurement. The present input data, macroeconomic question, dated nationality-map experiment, and contribution differ from those themes. Earlier manuscripts and personal documents are not included in this public package.

## Design record

The initial plan is retained unchanged in `ANALYSIS_PLAN.md`. It was written before exposure-error calculations, after documentation review and a small source-format probe. It was not registered with an external service. It specified the primary book, four horizons, country targets, map comparators, exact accounting checks, and selective refresh. Later additions were:

1. **Negative-position treatment:** the first panel build found negative source positions. The nonnegative baseline clips them to zero and saves a cleaning ledger; the signed-input sensitivity remains in every error record. There are 61 negative cells in the selected books. The primary equity book is unaffected.
2. **Common-support sensitivity:** explicitly removes residence rows absent from either dated map rather than relying solely on the identity-row convention.
3. **Enhanced-fund comparison:** assesses sensitivity to the source's broader institutional coverage for supported U.S. books.
4. **Financial-center and territorial-code sensitivity:** isolates a narrower map convention and checks the legacy Netherlands Antilles/successor-code routes. This was added after inspecting route contributions and is not labeled a primary test.
5. **Independent common-stock context:** uses the December 2025 Federal Reserve update. It compares separate estimates; it does not extend or validate the historical frozen-map experiment after 2020.

Map projection was implemented with an explicit NumPy contraction after platform BLAS emitted floating-status warnings. The final calculations are finite and agree with a separate sparse-dictionary implementation. This is an implementation detail, not a change to the estimand.

## Practical application and market context

Existing commercial systems already provide fund look-through and exposure aggregation; for example, [Charles River Development's technical article](https://www.crd.com/wp-content/uploads/2018/01/BobsGuide-CRD_FundLookthroughImprovesBuysideRiskEvaluation.pdf) describes these uses. The practical extension here is an auditable data-maintenance layer: identify the map vintage, show sensitivity for the target query, and prioritize rows for acquisition. Potential users include official-statistics teams, portfolio-risk groups and financial-data vendors.

No customer interviews, willingness-to-pay study, revenue estimate, paid vendor comparison, patent search, or measured acquisition-cost experiment was performed. The five-row results concern information acquired, not labor savings. Source-data restrictions must be resolved before any commercial deployment. The original software is reusable under its license, but that does not relicense the underlying financial data.

## Workshop fit and submission requirements

The [official SNB–ECB call](https://www.ecb.europa.eu/press/conferences/html/20270702_workshop_on_intl_macroeconomics_and_finance.en.html) invites completed PDFs by email to `international-workshop@snb.ch`, due 31 January 2027. The workshop is in Zurich on 2 July 2027, with acceptance notices by 15 March. Its exposure-measurement, external-adjustment and multinational-financing themes fit this paper directly. The public call specifies no account, template, page limit, fee, or institutional-affiliation eligibility condition. Absence of a stated affiliation restriction does not establish travel-funding eligibility.

The call allows requests for travel funding for academic presenters and discussants but states no maximum and supplies no separate grant form. A submission can request consideration for the maximum support allowed by workshop policy, conditional on the author's eligibility, without inventing an amount or an academic employment claim.

## Material limits for a reviewer

- The benchmark is estimated from covered fund holdings. Its sampling error cannot be recovered from the public matrix release.
- Historical data are revised and include some imputed positions. This is not a real-time vintage backtest.
- The main sample ends in 2020. It does not measure the error made in post-2022 fragmentation studies.
- Direction errors concern specified portfolio shares, not causal policy effects, capital flows, sanctions jurisdiction, or a full national net foreign asset position.
- Refresh rows are acquired exactly at equal unit cost in the experiment. Real acquisition costs and feasible partial updates can differ.
- A historical instability score is a heuristic. The sharp intervals require explicit assumptions about current row drift; no future confidence coverage is claimed.
- Partial refresh can break beneficial error cancellation. The ex post ranking minimizes an additive row envelope, not aggregate TV.
- The primary result is descriptive and reproducible; acceptance at a selective policy workshop remains uncertain.
