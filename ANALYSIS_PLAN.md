# Analysis plan and scope

Written 16 October 2026 after reviewing source documentation and a six-row format probe, before computing exposure errors. This is a research log, not an externally preregistered study. The historical release can contain revisions and interpolations; chronological information restrictions do not make it a real-time vintage experiment.

Question: How much error is introduced when current residence-basis external portfolio stocks are combined with older issuer-nationality restatement matrices?

Primary benchmark: the same public release's contemporaneous Fund Holdings matrix. This is an estimated benchmark, not observed truth. Report 1, 2, 3 and 5 year staleness wherever supported. Exclude domestic residence holdings to avoid dependence on source domestic-wealth imputations. Preserve reallocated home-country exposure within the resulting external-residence book. Do not renormalize by the post-restatement foreign subtotal.

Primary book: U.S. common equities, which avoid the equity/fund-share mixture in CPIS. Extensions: U.S. corporate, government and structured bonds, and other covered investors' all-bond books. Non-U.S. equities are a secondary extension only if the source's common-equity adjustment can be reconciled. Australia is excluded from balanced-panel comparisons because its documented reporting coverage differs.

Primary endpoints: total variation distance of nationality shares, absolute error in China and Russia exposure, and reversal of the sign of the exposure change relative to the last mapped year. Report China and Russia separately, their union, and China plus Hong Kong as a sensitivity. These are specified country sets, not an estimated geopolitical bloc.

Comparators: latest investor-specific map; mean of the three latest investor-specific maps; latest equal-weight average of other available investors' maps; issuance map where comparable. No tuning on future periods. Evaluate both full-available and common-calendar support. Do not invent standard errors treating country-year observations as independent.

Decomposition: symmetric two-factor (Shapley/polar) decomposition of nationality exposure changes into residence-weight changes and within-residence mapping changes. Neither component identifies transactions versus valuation. Decompose stale error by residence route, report signed and absolute contributions, and assess concentration.

Refresh policy: rank mapping rows by current exposure weight times historical row instability calculated from earlier years only. Compare top-k row refreshes against current-weight ranking and reproducible random subsets. These are retrospective information-acquisition experiments assuming the selected current matrix rows become observable; no measured vendor costs or operational claims.

Validation: stochastic-row invariants, external-book conservation, direct-loop reconstruction independent of matrix multiplication, known synthetic edge cases, exact decomposition identities, and a comparison with published contemporaneous restated positions where definitions align. Expose missing maps and zero-position conventions explicitly. Report exceptions and unsuccessful comparators rather than selecting favorable results.

Novelty claim: a historical temporal-validation and targeted-refresh study for nationality-restated external exposure measurement, not discovery of offshore issuance, portfolio look-through, Shapley decomposition, total-variation inequalities, or financial fragmentation. Further literature review may require narrowing this claim.
