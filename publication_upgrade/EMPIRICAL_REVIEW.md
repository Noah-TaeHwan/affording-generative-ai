# Independent empirical review and price-audit upgrade

The Go-to-Plus listing-price ratio provides the cleanest price contribution. It is a same-provider, same-storefront, same-payment-channel contrast. Its log-income slope remains positive within USD listings and when the two dominant currencies are excluded. This is substantially better evidence of differential entry-tier menu pricing than a comparison of separate, unmatched regressions. It does not measure demand, effective service quality, checkout costs or the effects of a discount.

## Reproduction and independent validation

- The inherited `code/20_analysis.py` was rerun in an isolated copy using the bundled Python 3.12.14. All **865 scalar values** match `baseline_results_v1.8.json` exactly, including its six-decimal rounding.
- `run_revision.sh --analysis-only` completed. Its six revised table bodies and separate $500 scenario CSV were unchanged before rewriting in the isolated copy. Fourteen independently implemented headline burden/usage checks passed.
- The new script implements OLS, HC3 and currency-clustered CR1 covariance with NumPy and verifies the new results against statsmodels to an absolute tolerance of 1e-12. The source data and manuscript are never edited.
- Local task dependencies installed: statsmodels 0.15.0, patsy 1.0.3. The bundled runtime already supplied NumPy 2.3.5, pandas 2.2.3, SciPy 1.17.0 and matplotlib 3.10.8.
- Input SHA256 hashes, executed outputs and machine-readable validation records are included. This is computation conditional on the deposited source extracts, not authentication of unarchived historical App Store pages.

## Exact new results

All regressions below use log local-currency Go/Plus price as the outcome and log Atlas GNI as the predictor. The local-currency and dollar ratios are numerically identical: same-storefront FX cancels. Neither a common currency factor nor an identical proportional tax factor can by itself generate their difference.

| Sample | N | Currencies | Low-income N | Slope | SE used | 95% interval |
|---|---:|---:|---:|---:|---:|---|
| All matched storefronts | 164 | 39 | 15 | 0.104070 | Currency CR1 0.007258 | [0.089377, 0.118762] |
| 2025 GNI only | 155 | 38 | 14 | 0.103401 | Currency CR1 0.007599 | [0.088004, 0.118797] |
| USD only | 102 | 1 | 15 | 0.112585 | HC3 0.007641 | [0.097609, 0.127560] |
| EUR only | 25 | 1 | 0 | 0.083358 | HC3 0.033420 | [0.017856, 0.148860] |
| Exclude USD | 62 | 38 | 0 | 0.112064 | Currency CR1 0.019677 | [0.072195, 0.151933] |
| Exclude USD and EUR | 37 | 37 | 0 | 0.125115 | Currency CR1 0.021894 | [0.080711, 0.169519] |

CR1 intervals use t critical values with G-1 degrees of freedom. Single-currency rows use normal HC3 intervals because currency-clustered inference cannot be estimated with one cluster. In the 37-currency exclusion sample every currency is a singleton, so CR1 is HC1 with a t36 reference; HC3 instead gives SE 0.023480 and interval [0.079094, 0.171136]. The interval convention must be identified in any published table.

The matched Go slope is 0.143454 and matched Plus slope is 0.039384; their contrast is exactly 0.104070. Estimating the ratio directly accounts for correlated residuals rather than summing separate variances. Full-sample ratio HC3 SE is 0.005750. The small positive absolute Plus slope itself has currency CR1 SE 0.019566 and interval [-0.000226, 0.078994]; p=0.051254. Do not describe this standard-tier slope as definitively different from zero under all dependence assumptions.

Leaving out each currency in turn yields Go/Plus slopes from **0.102141 to 0.112123**. A 19,999-draw currency-block resampling exercise, seed 20260930, has a central 95% percentile range of **[0.087416, 0.148161]**, with all draws positive. This is a dependence diagnostic, not a calibrated confidence interval under balanced-cluster asymptotics. Resampled sample sizes range from 39 to 818 countries because USD and EUR are large blocks. It should receive at most a sentence or supplement note; the exclusion samples are easier to interpret.

Currency fixed effects yield a slope of **0.110854**. This appears corroborative but must not be paired with an attractive CR1 SE as though all 39 currencies supply within-currency information. **Only USD and EUR, 127 countries total, identify this slope; 37 singleton currency groups supply none.** The USD-only and EUR-only descriptive fits are more transparent.

## Candidate matching audit

The 164 income-matched Go cells and 164 income-matched Plus cells all have one surviving candidate price. Choosing the minimum surviving candidate or excluding multiple surviving candidates therefore changes neither sample nor slope. Independently re-parsing named raw entries with annual-price exclusion cutoffs of 3x, 5x and 8x reproduces every selected Go/Plus local price exactly.

**This stability is not monthly SKU validation.** The raw Go and Plus product names contain no explicit monthly label. A single surviving candidate only means the heuristic makes an unambiguous selection from the deposited parsed list. The original HTML, SKU identifiers, billing-period metadata, eligibility, promotions and checkout evidence are absent. The revision should keep this limitation visible and release a contemporaneous collection protocol that archives these fields. Confirming a future scrape cannot retroactively authenticate a September 27 historical quote.

Google AI Pro has three multiple-candidate cells: Benin (USD), India (INR) and Türkiye (TRY). Benin mixes 5 TB and 10 TB products; India and Türkiye show different prices for the same displayed 5 TB label. The standard Pro slope is **0.036985** in 165 economies. Using the lowest candidate gives **0.036879**; dropping all three cells gives **0.037424** in 162 economies. Corresponding HC3 SEs are 0.005003, 0.005189 and 0.005045. Thus the standard-tier gradient is numerically insensitive to these three cells, while the plan-identity limitation remains. The Google Plus/Pro ratio slope is -0.011931 (N=160) and -0.012720 after the exclusions (N=157); both currency-clustered intervals include zero. The stronger Go/Plus result should not be generalised to all entry tiers.

## Suggested replacement/addition in the price-results section

> To distinguish entry-tier menu pricing from common currency schedules, we use matched Go and Plus listings within each storefront. The log Go-to-Plus ratio has a log-income slope of 0.104 (currency-clustered SE 0.007; N=164), exactly the difference between the two separate slopes when they use the same country sample. The slope remains 0.113 within the 102 USD storefronts (HC3 SE 0.008), 0.112 after excluding USD (currency-clustered SE 0.020; N=62), and 0.125 after excluding both USD and EUR (SE 0.022; N=37). The last two samples contain no low-income economies and therefore provide sensitivity evidence within observed middle- and high-income markets. Same-storefront ratios cancel exchange-rate conversion and any common proportional tax factor, but do not cancel differences in plan eligibility, promotions, platform markups or product matching. These results document differential menu pricing, not a demand response to regional prices.

> Candidate-selection sensitivity does not alter this result: each matched Go and Plus cell has one surviving candidate, and annual-price exclusion cutoffs of three, five and eight times the lowest named price select the same listings. This is a stability check on the extraction heuristic, not authentication of monthly SKU metadata. For Google AI Pro, removing the three multiple-candidate storefronts changes the income slope from 0.0370 to 0.0374. These checks reduce concerns about the particular selection rule while leaving historical listing, billing-period and checkout validation unresolved.

Suggested table body: `results/tab_matched_menu_sensitivity.tex`. Header: `Sample & N & Currencies & Low-income N & Slope & SE & 95\% interval`. Footnote: `Outcome is log Go/Plus local listing-price ratio; predictor is log Atlas GNI. Currency CR1 SEs with t(G-1) intervals except USD-only, which uses HC3 with a normal reference. Exclusion samples contain no low-income economies. These are descriptive menu-price associations; no demand or household-affordability parameter is estimated.`

## Consequential issues still open

1. The price contribution is conditional on an Apple listing-channel sample and an inferred monthly billing period. At checkout prices may differ. Do not equate no retrieved listing with no access to the service.
2. All low-income Go/Plus observations use USD. Excluding USD helps test concentration in the pricing pattern but simultaneously eliminates low-income coverage. It cannot validate conclusions about low-income countries on a separate currency sample.
3. Currency fixed effects nominally have many categories but only two informative multi-country groups. Their small clustered SE is not reliable evidence based on 39 within-currency contrasts.
4. Neither the listing gradient nor reference-price accounting establishes household exclusion, valuation, task completion costs, provider strategy or a causal effect of price on usage. Provider sampling/estimation uncertainty is outside the regression SEs.
5. Public AI usage samples remain selective, dates precede the price collection, and subscription status is unobserved. The manuscript's corrected descriptive usage language should be preserved.

## Executed commands

All commands were issued from `/workspace/scratch/10299588172c`; all outputs are confined to `paper_upgrade/empirical/`.

```bash
"$CODEX_PRIMARY_RUNTIME_PYTHON" -m pip install --target /workspace/scratch/10299588172c/paper_upgrade/empirical/deps statsmodels==0.15.0 --no-deps
"$CODEX_PRIMARY_RUNTIME_PYTHON" -m pip install --target /workspace/scratch/10299588172c/paper_upgrade/empirical/deps patsy --no-deps
PYTHONPATH=/workspace/scratch/10299588172c/paper_upgrade/empirical/deps MPLCONFIGDIR=/workspace/scratch/10299588172c/paper_upgrade/empirical/mplconfig REVISION_PYTHON="$CODEX_PRIMARY_RUNTIME_PYTHON" bash paper_upgrade/empirical/isolated_replication/run_revision.sh --analysis-only
PYTHONPATH=/workspace/scratch/10299588172c/paper_upgrade/empirical/deps "$CODEX_PRIMARY_RUNTIME_PYTHON" paper_upgrade/empirical/isolated_replication/code/20_analysis.py
PYTHONPATH=/workspace/scratch/10299588172c/paper_upgrade/empirical/deps "$CODEX_PRIMARY_RUNTIME_PYTHON" paper_upgrade/empirical/price_reliability.py
```

The three frozen-data rebuilding scripts were also executed sequentially by a short `subprocess.run` driver using the same executable: `code/09_appstore_prices.py`, `code/10_build_dataset.py`, `code/11_data_dictionary.py`. Their logs and processed-data byte-comparison record are included. The dependency installation was local to the task and did not change the primary runtime.
