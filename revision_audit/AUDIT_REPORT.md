# Replication audit and descriptive extensions

> Record of the audit stage between package versions 1.8 and 2.0. It describes the environment and files of that stage; the scripts it names are now run by `run_revision.sh`, and the clean-room verification of the version 2.0 package is in `verification/README.md`. The Word manuscript and the `manuscript/` folder that this stage produced are not part of version 2.0.

Audit date: 30 September 2026 (Korea time). Manuscript: TaeHwan Oh, *Affording Generative AI*, working-paper version dated 28 September 2026. Original replication package: v1.8, Zenodo DOI https://doi.org/10.5281/zenodo.23006366.

## What was actually verified

The Zenodo archive was retrieved through its public API. The 4,449,098-byte file has MD5 `399295b8c6aefc9a4c2bea8790893872`, identical to the repository metadata. The archive contains the manuscript sources, parsed App Store extracts, WDI extracts, derived Anthropic and ITU files, analysis code and results.

A separate copy of the archive was used to run `bash run_all.sh`; originals were preserved. The run completed with exit code 0. All 865 keys and values in `output/results.json` matched the deposited version. All 22 English/Korean LaTeX table bodies were byte-identical. The four processed CSV files matched within absolute/relative tolerance 1e-10. Figures were regenerated, although missing Korean fonts produced glyph warnings; manuscript typesetting was not part of this audit. Fourteen headline scalar values were independently recomputed using direct NumPy formulas, including HC3 covariance calculations, rather than invoking the author's analysis functions; all matched the reported values to six decimals.

Runtime: Python 3.12.14, NumPy 2.3.5, pandas 2.2.3, SciPy 1.17.0, statsmodels 0.15.0. Detailed evidence is in `audit_output/rerun_comparison.json` and `audit_output/independent_headline_checks.csv`.

The Microsoft Q2 2026 CSV was also freshly downloaded at full commit `507c31611c2af77abf44de43036f3ea1d599c248`; it was byte-identical to the deposited file (SHA256 `4a076d6aded6d8c9e60ddfff8a28476a72bb94e5293ae8feaa40c6bda06bd92a`).

**Upstream extension:** After the initial bundled-input run, all four pinned Anthropic release CSVs and three supporting population/GDP/ISO files were freshly downloaded, and the original full country-construction script was rerun. All four derived Anthropic outputs, including the 6,920-row five-window panel, were byte-identical to the deposit. The original ITU workbook was also freshly downloaded and its 41,853-row long file and 221-row country file were reconstructed byte-identically. An independent raw-data selection matched all 120 World Bank-matched May AUI values exactly and reproduced the n=96 slope (0.711136928; HC3 SE 0.035923227). Download hashes and comparisons are in `upstream_validation/upstream_verification.json`. **Remaining scope limit:** This is not a fresh reconstruction of every data source: historical App Store HTML and the World Bank upstream extraction were not independently reproduced. App Store records contain parsed names, prices, timestamps, URLs and HTTP status; the original HTML is explicitly not archived. Consequently the historical page extraction cannot be independently replayed from the deposit. Neither successful numerical reproduction nor the archived author's own verification record establishes the validity of all original upstream measurements.

## Main corrections and interpretation changes

### Broadband price ratios use different denominators in the original text

The reported AI/broadband ratios divide the 2025-GNI-based AI burden by the ITU's published burden, which uses its own older income denominator. This is a ratio of normalised burdens, not a direct ratio of dollar prices. Calling the low-income value 6.1 "times as much" in dollar cost is therefore imprecise.

| Income group | Original burden ratio | Direct $20 / 2024 2GB price | Direct $20 / 2025 5GB price |
|---|---:|---:|---:|
| High income | 1.519 | 1.701 | 1.441 |
| Upper-middle income | 2.248 | 2.639 | 2.337 |
| Lower-middle income | 4.468 | 5.064 | 3.052 |
| Low income | 6.072 | 6.431 | 3.676 |

Use direct dollar ratios when discussing costs. The 2025 comparison is the newer basket but has a different allowance and should be explicitly labelled. The 2024 and 2025 series also use historical exchange rates rather than September 2026 rates. Source: `audit_output/broadband_price_comparison.csv`.

### AUI measures a vendor's per-capita conversation volume

Write `AUI_c = K * D_c * S_c * M_c`, where `D_c` is the fraction using any AI, `S_c` the fraction of those users who use Claude, `M_c` conversations per Claude user, and `K` a common normalisation. This is a conceptual decomposition; its pieces cannot all be separately observed in the supplied data, and periods must match for a literal exact identity. Thus the log-slope gap between AUI and any use can reflect both vendor selection and intensity. It does not identify paid subscriptions, use conditional on adoption, or frontier capability consumed. Price effects cannot be isolated with these cross sections.

The direct regression of log(AUI / any-use-share) reproduces the baseline slope difference: 0.340256, HC3 SE 0.034259, 95% normal interval [0.273109, 0.407403], n=96. This interval differs slightly from the original stacked cluster estimator because its small-sample covariance adjustment differs. Preserve estimator labels. Do not describe either interval as including provider-estimation uncertainty.

| Specification | n | Any-use slope | AUI slope | Difference | HC3 SE of difference |
|---|---:|---:|---:|---:|---:|
| Baseline | 96 | 0.371 | 0.711 | 0.340 | 0.034 |
| 2025 GNI only | 92 | 0.374 | 0.729 | 0.356 | 0.034 |
| Non-high-income | 54 | 0.334 | 0.688 | 0.354 | 0.085 |
| Region fixed effects | 96 | 0.406 | 0.672 | 0.266 | 0.050 |
| Internet, education, urbanisation | 92 | 0.315 | 0.547 | 0.232 | 0.068 |
| Working-age population weighted | 96 | 0.261 | 0.737 | 0.476 | 0.086 |

Population weighting changes the estimand rather than simply improving the original estimate. Leave-one-economy-out differences range from 0.329162 to 0.350756. China and Russia are already absent from this common sample, so the exclusion check is mechanically unchanged and should not be advertised as additional robustness. See `cross_provider_gradient_robustness.csv` and `gradient_gap_leave_one_out.csv`.

### Connectivity accounting is numerically intact

The original code clips the displayed arithmetic ratio D/I at one but computes its log-decomposition without clipping. The cap never binds in the 109-observation decomposition sample: the largest ratio is 0.777732, and the maximum numerical identity residual is 4.4e-16. Remove clipping to clarify the definition; no estimate changes. The AI-use denominator is ages 15–64 and the internet-use denominator is total population. The ratio therefore remains an accounting comparison, not an observed conditional probability.

## Added pricing robustness

### Shared currencies and standard errors

Currency-clustered CR1 covariance with Student t critical values using G−1 degrees of freedom widens uncertainty substantially. For ChatGPT Plus, the slope remains 0.039384, but SE rises from HC3 0.005660 to currency-clustered 0.019566; its interval is [−0.000226, 0.078994]. ChatGPT Go remains 0.143454, with clustered SE 0.014423 and interval [0.114256, 0.172652]. The small slopes for several standard/high-usage tiers cease to differ from zero at conventional levels under this sensitivity.

These intervals themselves require caution: the ChatGPT sample has 39 currency clusters, consisting of 102 USD storefronts, 25 EUR storefronts and 37 singletons. The number of labels overstates the balance of independent information. Present clustering as a sensitivity, not a definitive inference procedure. Currency-fixed-effects estimates in the CSV are exploratory; small within-currency SEs should not be emphasized because the identifying variation is concentrated in a few groups. Source: `local_price_robustness.csv`.

### Within-storefront plan ratios

The ratio of Go to Plus in the same storefront cancels the common exchange rate and, under a common proportional tax rate for both plans, the tax factor. It also helps distinguish entry-tier discounts from common storefront price premia. The result is descriptive and does not identify consumer demand or the effect of discounts on adoption.

| Ratio | n | Log-income slope | HC3 SE | Currency-cluster SE | Currency-cluster 95% t interval |
|---|---:|---:|---:|---:|---:|
| ChatGPT Go / Plus | 164 | 0.104070 | 0.005750 | 0.007258 | [0.089377, 0.118762] |
| Google Plus / Pro | 160 | −0.011931 | 0.003014 | 0.006816 | [−0.025730, 0.001868] |
| ChatGPT Pro 5x / Plus | 164 | −0.020670 | 0.004371 | 0.011233 | [−0.043411, 0.002071] |

The clustering caveat above applies. Figure `fig_price_ratio_en` plots Go/Plus in log scales with an OLS fitted line and no confidence ribbon. Source: `within_storefront_price_ratios.csv`.

### Match PPP comparisons to the estimation sample

The original 0.228 price-level-proxy slope uses a broader sample than the Go regression. On the 164 storefronts with Go/Plus prices and income/PPP data, the corresponding slope is 0.242627 (HC3 SE 0.015750). Go's slope is 59.1% of this matched benchmark, compared with the original approximately 63% of the full-sample benchmark. Plus is 16.2% of the matched benchmark. On the same sample, the Go-minus-PPP slope is −0.099173 (HC3 SE 0.016127), and Plus-minus-PPP is −0.203242 (0.016826). The benchmark remains a hypothetical pricing rule, not a measure of actual disposable purchasing power for dollar-priced services. Source: `same_sample_ppp_comparison.csv`.

## Vintage, thresholds and plan-label audit

There are 201 nonmissing GNI observations: 182 from 2025, 16 from 2024, two from 2023 and one from 2022. Atlas and PPP GNI years match for every observation with both measures. Restricting to 2025 changes median $20 burdens from 0.6483 to 0.6654 in high-income economies, from 8.7273 to 8.8749 in lower-middle-income economies, and leaves the other two group medians unchanged. The high-income sample falls from 75 to 59, so the sample composition change should be stated. `burden_threshold_sensitivity.csv` reports 1%, 2%, 5% and 10% reference thresholds for several plan prices; the 2% broadband reference is not a validated AI welfare threshold.

The three retained multi-price monthly-plan cells are all Gemini Pro: Benin (USD 19.99 vs 49.99, including a higher-storage variant), India (INR 1,649 vs 1,950), and Türkiye (TRY 539.99 vs 869.99). The original modal choice is deterministic, but it does not establish checkout eligibility of an individual price. The deposited output reports the lowest-price sensitivity; it reproduces in the full rerun. Four Gemini Plus cells (Guinea-Bissau, Montenegro, Palau and Tonga) are dropped as presumed annual-only listings on the basis of price magnitude; billing period is not directly verified by the archived price strings. The archived Ultra names all read `Google AI Ultra (30 TB)`, so no 5TB/30TB Ultra-name mix was observed in these extracts. The heuristic monthly/annual filter should remain explicit. Source: `ambiguous_plan_cells.csv` and the original `09_appstore_prices.py`.

No evidence of a numerical discrepancy was found in the reproduced headline estimates. The corrections concern measurement interpretation, matched comparisons, uncertainty and the limits of historical source reconstruction.

## Reproduction

From the revised package root:

```bash
python revision_audit/audit_extensions.py
python revision_audit/figure_price_ratio.py
```

The first command reads the package's frozen data files, compares independent headline calculations with `revision_audit/baseline_results_v1.8.json`, and writes `revision_audit/audit_output/`. The second writes the new figure to `paper_en/figures/`. It does not regenerate original result tables or edit manuscript prose. `rerun_comparison.json` records the completed original-code rerun; it is historical evidence, not automatically regenerated by these two commands.
