# Portable publication-upgrade checks

These checks are run by `run_revision.sh` (and therefore by `run_all.sh`). To run them alone, from the package root:

```bash
python -m pip install -r checks/requirements.txt
python checks/price_reliability.py
python checks/build_matched_menu_table.py --check
python checks/verify_tier_model.py
```

To regenerate the manuscript table after changing inputs, omit `--check` from the table command. `--check` leaves the manuscript table unchanged and records the comparison in `results/matched_menu_table_verification.json`. Both table modes refresh a matching table-body copy in `results/`.

`price_reliability.py` resolves the package root relative to its own file and makes no network requests. It reads the supplied processed country and listing CSVs, parsed App Store records and `extensions/baseline_results_v1.8.json`; it writes only inside `checks/results/`. It implements OLS, HC3 and currency-clustered CR1 covariance directly with NumPy and cross-checks them against statsmodels. Fourteen independent baseline quantities must match to six decimals. Historical input hashes, matching checks and other results are recorded in `price_reliability_summary.json`.

The matched-menu publication table consistently uses **HC3 SEs and normal 95% intervals for all four rows**. The manuscript's separate revision-audit price table uses **currency-clustered CR1 errors with t(G−1) intervals**. Both conventions are retained in the result CSVs; do not silently substitute one for the other. Non-USD samples contain no low-income economies. Currency fixed effects have only two informative multi-country groups, USD and EUR; their numerical slope is reported without claiming inference from 39 informative clusters. The currency-block resampling percentile range is a dependence diagnostic under severely unbalanced blocks.

Candidate-selection stability does not validate monthly SKU metadata, historical HTML, checkout eligibility, provider intent or demand effects. Prices and country income coverage remain conditional on the frozen parsed extracts. No source data or main manuscript prose is edited by these checks.

`verify_tier_model.py` writes `tier_model_verification.json`. It checks 50,000 utility-threshold comparisons and 4,000 analytic gradient components against finite differences under maintained assumptions. This verifies algebra, not empirical identification or validity of those assumptions.

`EMPIRICAL_REVIEW.md` preserves the detailed analytical review and historical task commands. Its proposed table initially used currency CR1 outside single-currency rows; the current publication table deliberately uses the uniform HC3 convention described above. The clean-room rerun of the whole pipeline is documented in `verification/README.md`; the independent upgrade script itself recomputes fourteen headline quantities and its additional price sensitivities.
