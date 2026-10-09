#!/usr/bin/env python3
"""Independent numerical checks of the manuscript's conditional tier model.

Run with the bundled runtime:
  "$CODEX_PRIMARY_RUNTIME_PYTHON" checks/verify_tier_model.py

This verifies the algebra for the maintained model, not its empirical validity.
It writes a small JSON report alongside this script unless --output is supplied.
"""

import argparse
import json
from pathlib import Path

import numpy as np
import scipy
from scipy.special import log_ndtr


def verify(seed=20260930):
    rng = np.random.default_rng(seed)
    n = 50_000
    qf = rng.uniform(0.1, 2, n)
    qp = qf + rng.uniform(0.1, 3, n)
    tau = rng.uniform(0.1, 10, n)
    price = rng.uniform(0.1, 30, n)
    valuation = np.exp(rng.uniform(-6, 8, n))
    utilities = np.column_stack(
        (np.zeros(n), valuation * qf - tau, valuation * qp - tau - price)
    )
    choice = utilities.argmax(axis=1)
    adoption_threshold = np.minimum(tau / qf, (tau + price) / qp)
    paid_threshold = np.maximum(price / (qp - qf), (tau + price) / qp)
    adoption_mismatches = int(np.count_nonzero((choice > 0) != (valuation > adoption_threshold)))
    paid_mismatches = int(np.count_nonzero((choice == 2) != (valuation > paid_threshold)))

    # A small income perturbation stays strictly inside each threshold regime.
    finite_difference_step = 1e-5
    gradient_errors = []
    per_regime_errors = {}
    for nested in (True, False):
        errors = []
        for _ in range(1000):
            qf = float(rng.uniform(0.1, 2))
            qp = qf + float(rng.uniform(0.1, 3))
            tau = float(rng.uniform(0.1, 10))
            critical_price = tau * (qp - qf) / qf
            price = critical_price * (2 if nested else 0.5)
            mu = float(rng.uniform(-3, 3))
            sigma = float(rng.uniform(0.3, 2))
            beta = float(rng.uniform(-1, 1.5))
            eligibility_elasticity = 0.1

            def log_shares(log_income_change):
                local_price = price * np.exp(beta * log_income_change)
                td = min(tau / qf, (tau + local_price) / qp)
                tp = max(local_price / (qp - qf), (tau + local_price) / qp)
                conditional_log_shares = np.array(
                    [
                        log_ndtr((mu + log_income_change - np.log(td)) / sigma),
                        log_ndtr((mu + log_income_change - np.log(tp)) / sigma),
                    ]
                )
                return np.log(0.4) + eligibility_elasticity * log_income_change + conditional_log_shares

            def inverse_mills(z):
                return np.exp(-0.5 * z * z - 0.5 * np.log(2 * np.pi) - log_ndtr(z))

            if nested:
                analytic = np.array(
                    [
                        eligibility_elasticity + inverse_mills((mu - np.log(tau / qf)) / sigma) / sigma,
                        eligibility_elasticity
                        + (1 - beta) * inverse_mills((mu - np.log(price / (qp - qf))) / sigma) / sigma,
                    ]
                )
            else:
                z = (mu - np.log((tau + price) / qp)) / sigma
                analytic = np.repeat(
                    eligibility_elasticity + (1 - beta * price / (tau + price)) * inverse_mills(z) / sigma,
                    2,
                )
            finite = (
                log_shares(finite_difference_step) - log_shares(-finite_difference_step)
            ) / (2 * finite_difference_step)
            errors.extend(np.abs(finite - analytic))
        gradient_errors.extend(errors)
        per_regime_errors["nested" if nested else "reversed"] = float(max(errors))

    max_error = float(max(gradient_errors))
    tolerance = 1e-6
    return {
        "seed": seed,
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "scope": "Numerical verification of maintained-model algebra, not empirical assumptions",
        "utility_checks": {
            "parameter_valuation_comparisons": n,
            "adoption_threshold_mismatches": adoption_mismatches,
            "paid_threshold_mismatches": paid_mismatches,
        },
        "gradient_checks": {
            "parameter_sets": 2000,
            "parameter_sets_per_regime": 1000,
            "gradient_components": len(gradient_errors),
            "central_difference_step": finite_difference_step,
            "maximum_absolute_error": max_error,
            "maximum_absolute_error_by_regime": per_regime_errors,
            "absolute_error_tolerance": tolerance,
        },
        "passed": adoption_mismatches == 0 and paid_mismatches == 0 and max_error < tolerance,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("tier_model_verification.json"))
    args = parser.parse_args()
    result = verify()
    report = json.dumps(result, indent=2, allow_nan=False) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(report, end="")
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
