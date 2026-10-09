# Prospective access and workload protocol

This protocol and `access_measurement_fields.csv` implement Appendix F's proposed extension. They contain no newly collected observations. Missing prices, quota values, eligibility or billing periods remain missing.

1. Prespecify economy/channel/date coverage, provider and plan inclusion, task languages, model versions, quality scoring, deadlines, retry rules and the comparison set. Define treatment of free, institutional, API and local-model access before observation.
2. Capture full tariff evidence with UTC timestamps, source URLs, hashes, original currency, taxes, billing period, promotions, account cohort, allowances, eligibility, reset windows and overage terms. Record listing and actual checkout separately.
3. For each task attempt preserve input/output, configuration, time, scoring and billed use. Observe failures and retries, not only successful responses. Collect only information needed for the study; remove personal account data from released evidence.
4. For a prespecified workload B, quality rule q and deadline d, identify configurations that actually meet all three. Minimum cash expenditure is the infimum over that feasible set. A missing feasible configuration cannot be assigned a zero cost; distinguish failure to find one from proven infeasibility.
5. Report total cash expenditure, task count, success rate and deadlines met alongside cost per successful task. Allocate recurring fees and fixed hardware costs using a stated horizon, with alternative allocations. Convert currencies only with documented contemporaneous rates; preserve original amounts.
6. Report variation across runs, languages and task types, plus sensitivity to task composition and allocation rules. Avoid treating a metering multiplier as a speed, capability or productivity estimate.

The current manuscript estimates subscription price-to-income commitments only. This protocol specifies observations needed for a later quality- and deadline-constrained access study; it does not add those outcomes to the present empirical results.
