#!/usr/bin/env python3
"""Independent numerical checks of the tier model of Section 3 and Appendix A (version 3.1 of the manuscript).

Run:  python checks/verify_tier_model.py [--output PATH]

The script verifies the algebra of the maintained model, not its empirical validity.  It has three parts.

(i) Choice rule (Appendix A, "Demand: four options and nested thresholds").  A consumer with valuation v chooses among
    non-use (u_0 = 0), the free tier F (u_F = v q_F - tau), the capped entry tier L (u_L = v q_L - tau - p_L) and the frontier
    tier H (u_H = v q_H - tau - p_H).  For random parameters that satisfy the nested condition
        tau/q_F < p_L/(q_L - q_F) < (p_H - p_L)/(q_H - q_L)
    the brute-force argmax over the four utilities is compared with the interval rule (non-use below T_D = tau/q_F, F on
    [T_D, T_L), L on [T_L, T_H), H above T_H), at valuations spread over many orders of magnitude and at valuations just
    below and above each of the three thresholds.  Three statements of the text are checked as well: the entry tier is never
    chosen when T_L > T_H; the free tier is never chosen when T_D > T_L; the any-use threshold min_k (tau + p_k)/q_k equals
    tau/q_F, and does not move with p_L or p_H, in the nested regime but moves with p_L when the free tier is dominated.

(ii) Proposition A.1.  The income gradients of the shares using any tier, a paid tier and the frontier tier,
        eps_D = eps_kappa + h(z_D)/s,  eps_P = eps_kappa + (1 - beta_L) h(z_L)/s,  eps_H = eps_kappa + (1 - beta_Delta) h(z_H)/s,
    with h = phi/Phi the lower-tail inverse Mills ratio, are compared with central finite differences of the logarithms of the
    shares D_c = kappa_c Phi(z_D), P_c = kappa_c Phi(z_L), H_c = kappa_c Phi(z_H).  Also checked, by finite differences: the
    ordering eps_H > eps_P > eps_D under uniform pricing; beta* = 1 - h(z_D)/h(z_L) lies in (0, 1), makes eps_P = eps_D at
    beta_L = beta*, and eps_P > eps_D below it and eps_P < eps_D above it; with a uniform frontier price and a localised entry
    price, beta_Delta = -p_L beta_L/(p_H - p_L) < 0 and eps_H exceeds its uniform-pricing value; the bridge to the activity
    index, eps_m = theta_c (eps_P - eps_D) with theta_c in (0, 1), for conversations per user m_c = (1 - pi_c) m_F + pi_c m_P.
    The illustration of beta* in Appendix A (beta* = 0.44, 0.34, 0.58 when 23% of the eligible use AI and 10%, 25%, 1% of the
    users pay; beta* falls to the observed standard-tier slope of 0.04 only if about nine in ten users pay) is confirmed to two
    decimals from the closed form and from the root of the finite-difference gap eps_P - eps_D in beta_L (and, when
    paper_en/main.tex is present, must be the numbers printed in that sentence).

(iii) Proposition A.2.  For lognormal valuations the monopolist's first-order condition for the price increment is solved
    numerically on a grid of cost shares of the increment L (ell_k in the v3.1 notation, set through the cost increment) and
    dispersions s.  The income elasticity of the optimal increment, beta = d ln(Delta p*)/d ln y, is computed by central finite
    differences of the numerical solution and compared with xi/(xi + L), xi = d Lambda/d ln x at the optimum (Lerner index of the
    demand curve, differentiated numerically), and with the closed form, written here in the hazard notation of the v3.0 appendix,
        beta = lambda'(z*) / [lambda'(z*) + lambda(z*) (lambda(z*) - s)],  lambda' = lambda (lambda - z),  lambda(z*) = s/(1 - L),
    lambda = phi/(1 - Phi) the standard normal hazard; with the v3.1 sign convention z = (mu - ln T)/s and h = phi/Phi this is the
    same number as (z* + h*)/(z* + 2h* - s) with h* = s/(1 - L) (checks/sim_check.py, part A, evaluates that form).  The values
    quoted in the text (s = 1: 0.63, 0.30, 0.05 and s = 0.7: 0.76, 0.44, 0.09 at L = 1/4, 1/2, 4/5) are confirmed to two decimals
    from both routes (and, when paper_en/main.tex is present, must be the numbers printed in that sentence); beta(L = 0) = 1;
    beta tends to zero as L -> 1; lambda' < 1; and beta is strictly decreasing in L on a fine grid of L for every s in S_RANGE,
    which is the monotonicity that the proof refers to.

A deterministic JSON report (fixed seed, no timestamps; the numpy and scipy versions, the seed and every tolerance of the script
under "tolerances" are part of it) is written next to this script unless --output is given and printed.  Exit code 0 if every
check passes ("passed": true), 1 otherwise.
"""

import argparse
import json
import re
from pathlib import Path

import numpy as np
import scipy
from scipy.optimize import brentq
from scipy.special import log_ndtr
from scipy.stats import norm

SEED = 20260930
S_RANGE = (0.3, 2.0)                       # dispersions s over which the monotonicity of beta(L) is verified (Appendix A: s in [0.3, 2])
QUOTED_L = (0.25, 0.5, 0.8)                # cost shares of the illustration in Appendix A: one quarter, one half, four fifths
QUOTED = {1.0: (0.63, 0.30, 0.05), 0.7: (0.76, 0.44, 0.09)}      # beta quoted in Appendix A at QUOTED_L for s = 1 and s = 0.7
QUOTED_ANCHOR = "For $s=1$ the elasticity is"      # sentence of paper_en/main.tex that carries the quoted values
QUOTED_BSTAR_ANCHOR = "gives $\\beta^*="    # sentence of paper_en/main.tex that carries the quoted values of beta*
SHARE_USE = 0.23                           # share of the eligible who use any tier in the illustration of beta* in Appendix A
QUOTED_BSTAR = {0.10: 0.44, 0.25: 0.34, 0.01: 0.58}      # beta* quoted in Appendix A for these shares of users who pay
BSTAR_SLOPE = 0.04                         # observed standard-tier slope below which beta* falls "only if more than about nine in ten users pay"
BSTAR_PAY_SHARE = (0.85, 0.95)             # "about nine in ten": the share of payers at which beta* = BSTAR_SLOPE must lie in this interval
FD_STEP = 1e-5                             # step of the central differences in ln y
# every tolerance of the script; the report carries them under "tolerances"
TOL_GRADIENT = 1e-6                        # absolute tolerance for gradients (central differences with step FD_STEP)
TOL_BETA = 1e-6                            # absolute tolerance for the elasticity of the optimal price (finite differences of the numerical optimum vs the formulas)
TOL_BETA_STAR = 1e-6                       # absolute tolerance for beta* (root of the finite-difference gap eps_P - eps_D vs the closed form)
TOL_ANY_USE = 1e-12                        # relative gap between min_k (tau + p_k)/q_k and tau/q_F in the nested regime
TOL_OPTIMUM_Z = 1e-6                       # |ln(x*)/s - z*|: numerical optimum vs the hazard equation lambda(z*) = s/(1 - L)
TOL_BETA_AT_ZERO = 1e-10                   # |beta(L = 0) - 1|
BETA_AT_TOP_MAX = 0.01                     # beta on the top of the L grid (L = 0.999) must be below this: beta -> 0 as L -> 1
ROUND_GUARD = 1e-12                        # added before rounding a computed beta to two decimals (guards exact halves)
TOL_UNIT = 1e-12                           # beta <= 1 + TOL_UNIT on the grid (floating-point rounding at L = 0)
OFFSET_NEAR_THRESHOLD = 1e-7               # relative distance of the valuations placed just below and above each threshold
TOLERANCES = {
    "gradient_absolute": TOL_GRADIENT,
    "central_difference_step": FD_STEP,
    "elasticity_of_optimal_price_absolute": TOL_BETA,
    "beta_star_absolute": TOL_BETA_STAR,
    "any_use_threshold_relative": TOL_ANY_USE,
    "optimum_z_absolute": TOL_OPTIMUM_Z,
    "beta_at_zero_cost_absolute": TOL_BETA_AT_ZERO,
    "beta_at_top_of_cost_share_grid_below": BETA_AT_TOP_MAX,
    "rounding_guard_for_two_decimals": ROUND_GUARD,
    "beta_not_above_one_by_more_than": TOL_UNIT,
    "valuation_offset_at_thresholds_relative": OFFSET_NEAR_THRESHOLD,
    "lambda_prime_below": 1.0,
    "pay_share_interval_for_about_nine_in_ten": list(BSTAR_PAY_SHARE),
}


# ------------------------------------------------------------------------------------------------ special functions
def mills_lower(z):
    """h(z) = phi(z) / Phi(z), the lower-tail inverse Mills ratio (strictly decreasing)"""
    return np.exp(norm.logpdf(z) - log_ndtr(z))


def hazard(z):
    """lambda(z) = phi(z) / (1 - Phi(z)), the standard normal hazard"""
    return np.exp(norm.logpdf(z) - norm.logsf(z))


def beta_closed(L, s):
    """closed form (A.8): z* solves lambda(z*) = s / (1 - L); beta = lambda' / (lambda' + lambda (lambda - s))"""
    z = brentq(lambda t: hazard(t) - s / (1.0 - L), -60.0, 1e7, xtol=1e-14, rtol=1e-14)
    lam = float(hazard(z))
    lam1 = lam * (lam - z)
    return lam1 / (lam1 + lam * (lam - s)), z


def manuscript_text():
    """text of paper_en/main.tex, or None in a copy of the package that lacks it"""
    tex = Path(__file__).resolve().parents[1] / "paper_en" / "main.tex"
    return tex.read_text(encoding="utf-8") if tex.exists() else None


# ------------------------------------------------------------------------------------------------ (i) choice rule
def nested_draws(rng, n):
    """n parameter vectors (q_F, q_L, q_H, tau, p_L, p_H) with 0 < q_F < q_L < q_H, 0 < p_L < p_H that satisfy the nested condition
    (rejection sampling)"""
    out = []
    got = 0
    while got < n:
        m = 4 * n
        qf = rng.uniform(0.1, 2, m)
        ql = qf + rng.uniform(0.1, 3, m)
        qh = ql + rng.uniform(0.1, 3, m)
        tau = rng.uniform(0.1, 10, m)
        pl = rng.uniform(0.1, 30, m)
        ph = pl + rng.uniform(0.1, 60, m)
        ok = (tau / qf < pl / (ql - qf)) & (pl / (ql - qf) < (ph - pl) / (qh - ql))
        out.append(np.column_stack([qf, ql, qh, tau, pl, ph])[ok])
        got += int(ok.sum())
    return np.vstack(out)[:n]


def free_draws(rng, n):
    """n unrestricted parameter vectors (no nested condition)"""
    qf = rng.uniform(0.1, 2, n)
    ql = qf + rng.uniform(0.1, 3, n)
    qh = ql + rng.uniform(0.1, 3, n)
    return np.column_stack([qf, ql, qh, rng.uniform(0.1, 10, n), rng.uniform(0.1, 30, n), rng.uniform(0.1, 30, n) + 30])


def utilities(par, v):
    qf, ql, qh, tau, pl, ph = par.T
    return np.column_stack([np.zeros(len(v)), v * qf - tau, v * ql - tau - pl, v * qh - tau - ph])


def choice_checks(rng):
    n = 40_000
    par = nested_draws(rng, n)
    qf, ql, qh, tau, pl, ph = par.T
    td, tl, th = tau / qf, pl / (ql - qf), (ph - pl) / (qh - ql)
    # (a) valuations spread over many orders of magnitude, (b) valuations just below and above each threshold
    v_wide = np.exp(rng.uniform(-6, 8, n))
    cases = [("wide", v_wide)]
    for name, t in (("T_D", td), ("T_L", tl), ("T_H", th)):
        cases.append((name + "-", t * (1 - OFFSET_NEAR_THRESHOLD)))
        cases.append((name + "+", t * (1 + OFFSET_NEAR_THRESHOLD)))
    mismatches, per_case, counts = 0, {}, np.zeros(4, dtype=int)
    for name, v in cases:
        brute = utilities(par, v).argmax(axis=1)
        rule = (v >= td).astype(int) + (v >= tl).astype(int) + (v >= th).astype(int)
        bad = int(np.count_nonzero(brute != rule))
        per_case[name] = bad
        mismatches += bad
        counts += np.bincount(brute, minlength=4)
    # the any-use threshold in the nested regime is tau/q_F, whatever the paid prices
    t_any = np.minimum.reduce([tau / qf, (tau + pl) / ql, (tau + ph) / qh])
    any_gap = float(np.max(np.abs(t_any / (tau / qf) - 1)))
    bump = 1e-3
    t_any_bumped = np.minimum.reduce([tau / qf, (tau + pl * (1 + bump)) / ql, (tau + ph * (1 + bump)) / qh])
    nested_moves = int(np.count_nonzero(t_any_bumped != t_any))
    # regimes in which the nested condition fails
    fr = free_draws(rng, 4 * n)
    qf2, ql2, qh2, tau2, pl2, ph2 = fr.T
    td2, tl2, th2 = tau2 / qf2, pl2 / (ql2 - qf2), (ph2 - pl2) / (qh2 - ql2)
    v2 = np.exp(rng.uniform(-6, 8, len(fr)))
    brute2 = utilities(fr, v2).argmax(axis=1)
    entry_fail = tl2 > th2
    free_fail = td2 > tl2
    entry_chosen = int(np.count_nonzero(brute2[entry_fail] == 2))
    free_chosen = int(np.count_nonzero(brute2[free_fail] == 1))
    # any use = choice > 0 exactly when v exceeds min_k (tau + p_k)/q_k, in every regime
    t_any2 = np.minimum.reduce([tau2 / qf2, (tau2 + pl2) / ql2, (tau2 + ph2) / qh2])
    any_bad = int(np.count_nonzero((brute2 > 0) != (v2 > t_any2)))
    # when the free tier is dominated the any-use threshold moves with the paid price
    dom = free_fail & ((tau2 + pl2) / ql2 < (tau2 + ph2) / qh2)       # the entry tier gives the lowest any-use threshold
    bumped = np.minimum.reduce([tau2 / qf2, (tau2 + pl2 * (1 + bump)) / ql2, (tau2 + ph2 * (1 + bump)) / qh2])
    moves = int(np.count_nonzero((bumped > t_any2)[dom]))
    n_dom = int(np.count_nonzero(dom))
    return {
        "nested_parameter_sets": n,
        "valuation_cases": [name for name, _ in cases],
        "comparisons": n * len(cases),
        "choice_rule_mismatches": mismatches,
        "choice_rule_mismatches_by_case": per_case,
        "option_counts_non_use_F_L_H": [int(c) for c in counts],
        "nested_any_use_threshold_max_relative_gap": any_gap,
        "nested_any_use_threshold_moves_with_paid_prices": nested_moves,
        "failing_condition_draws": int(len(fr)),
        "entry_tier_fails_draws": int(entry_fail.sum()),
        "entry_tier_chosen_when_it_fails": entry_chosen,
        "free_tier_fails_draws": int(free_fail.sum()),
        "free_tier_chosen_when_it_fails": free_chosen,
        "any_use_threshold_rule_mismatches": any_bad,
        "free_tier_dominated_draws_with_paid_threshold": n_dom,
        "of_which_threshold_moves_with_p_L": moves,
        "passed": bool(mismatches == 0 and nested_moves == 0 and any_gap < TOL_ANY_USE and entry_chosen == 0 and free_chosen == 0
                       and any_bad == 0 and moves == n_dom and n_dom > 0 and all(c > 0 for c in counts)),
    }


# ------------------------------------------------------------------------------------------------ (ii) Proposition A.1
class Market:
    """one parameter set: thresholds, shares and their log-derivatives with respect to ln y_c (x = ln(y_c/y_0))"""

    def __init__(self, rng):
        self.s = float(rng.uniform(0.3, 2))
        self.t_d = float(np.exp(rng.uniform(-1, 1.5)))
        self.t_l = self.t_d * float(np.exp(rng.uniform(0.05, 1.5)))
        self.t_h = self.t_l * float(np.exp(rng.uniform(0.05, 1.5)))
        z_d = float(rng.uniform(-1.0, 3.0))
        self.mu0 = float(np.log(self.t_d) + self.s * z_d)
        self.eps_k = float(rng.uniform(-0.3, 0.5))
        self.beta_l = float(rng.uniform(-0.5, 1.5))
        self.beta_d = float(rng.uniform(-1.0, 1.5))
        self.m_f = float(rng.uniform(0.2, 2))
        self.m_p = self.m_f * float(rng.uniform(1.1, 6))

    def thresholds(self, x, beta_l=None, beta_d=None):
        bl = self.beta_l if beta_l is None else beta_l
        bd = self.beta_d if beta_d is None else beta_d
        return self.t_d, self.t_l * np.exp(bl * x), self.t_h * np.exp(bd * x)

    def z(self, x, **kw):
        t_d, t_l, t_h = self.thresholds(x, **kw)
        return [(self.mu0 + x - np.log(t)) / self.s for t in (t_d, t_l, t_h)]

    def log_shares(self, x, **kw):
        lk = self.eps_k * x
        return [lk + log_ndtr(z) for z in self.z(x, **kw)]


def fd(f, step=FD_STEP):
    return (np.asarray(f(step)) - np.asarray(f(-step))) / (2 * step)


def gradient_checks(rng):
    n_sets = 2000
    errs, ordering_bad, star_bad, star_order_bad, star_range_bad, bridge_err, bridge_range_bad = [], 0, 0, 0, 0, [], 0
    star_zero_err, uniform_front_bad, beta_delta_err, eps_h_err = [], 0, [], []
    for _ in range(n_sets):
        m = Market(rng)
        z_d, z_l, z_h = m.z(0.0)
        s = m.s
        analytic = np.array([m.eps_k + mills_lower(z_d) / s,
                             m.eps_k + (1 - m.beta_l) * mills_lower(z_l) / s,
                             m.eps_k + (1 - m.beta_d) * mills_lower(z_h) / s])
        numeric = fd(lambda e: m.log_shares(e))
        errs.extend(np.abs(numeric - analytic))
        # uniform pricing: eps_H > eps_P > eps_D
        gu = fd(lambda e: m.log_shares(e, beta_l=0.0, beta_d=0.0))
        ordering_bad += int(not (gu[2] > gu[1] > gu[0]))
        # beta* = 1 - h(z_D)/h(z_L)
        star = 1 - mills_lower(z_d) / mills_lower(z_l)
        star_range_bad += int(not (0 < star < 1))
        g_star = fd(lambda e: m.log_shares(e, beta_l=star))
        star_zero_err.append(abs(g_star[1] - g_star[0]))
        g_below = fd(lambda e: m.log_shares(e, beta_l=star - 0.1))
        g_above = fd(lambda e: m.log_shares(e, beta_l=star + 0.1))
        star_order_bad += int(not (g_below[1] > g_below[0] and g_above[1] < g_above[0]))
        # frontier price uniform (beta_H = 0), entry price localised (beta_L > 0): beta_Delta = -p_L beta_L / (p_H - p_L) < 0
        bl = float(abs(m.beta_l)) + 0.05
        p_l0 = m.t_l * 1.0                                   # price scale q_L - q_F = 1
        d0 = m.t_h * 1.0                                     # (p_H - p_L)/(q_H - q_L) with q_H - q_L = 1
        p_h0 = p_l0 + d0                                     # the frontier price is held fixed in income

        def shares_front_fixed(e):
            t_l = p_l0 * np.exp(bl * e)
            t_h = p_h0 - t_l
            zs = [(m.mu0 + e - np.log(t)) / s for t in (m.t_d, t_l, t_h)]
            return [m.eps_k * e + log_ndtr(z) for z in zs]

        bd_formula = -p_l0 * bl / (p_h0 - p_l0)
        bd_numeric = float(fd(lambda e: np.log(p_h0 - p_l0 * np.exp(bl * e))))
        beta_delta_err.append(abs(bd_numeric - bd_formula))
        g_front = fd(shares_front_fixed)
        z_h0 = (m.mu0 - np.log(d0)) / s
        eps_h_formula = m.eps_k + (1 - bd_formula) * mills_lower(z_h0) / s
        eps_h_err.append(abs(g_front[2] - eps_h_formula))
        uniform_front_bad += int(not (bd_formula < 0 and g_front[2] > m.eps_k + mills_lower(z_h0) / s))
        # bridge to the activity index: eps_m = theta_c (eps_P - eps_D)
        def log_m(e):
            ls = m.log_shares(e)
            pi = np.exp(ls[1] - ls[0])
            return np.log((1 - pi) * m.m_f + pi * m.m_p)

        ls0 = m.log_shares(0.0)
        pi0 = float(np.exp(ls0[1] - ls0[0]))
        theta = pi0 * (m.m_p - m.m_f) / ((1 - pi0) * m.m_f + pi0 * m.m_p)
        eps_m_formula = theta * (analytic[1] - analytic[0])
        bridge_err.append(abs(float(fd(log_m)) - eps_m_formula))
        bridge_range_bad += int(not (0 < theta < 1))
    max_err = float(max(errs))
    bstar = beta_star_checks()
    return {
        "parameter_sets": n_sets,
        "gradient_components": len(errs),
        "central_difference_step": FD_STEP,
        "maximum_absolute_error": max_err,
        "absolute_error_tolerance": TOL_GRADIENT,
        "uniform_pricing_ordering_violations": ordering_bad,
        "beta_star_outside_unit_interval": star_range_bad,
        "beta_star_max_abs_gap_eps_P_minus_eps_D": float(max(star_zero_err)),
        "beta_star_ordering_violations": star_order_bad,
        "uniform_frontier_max_abs_error_beta_delta": float(max(beta_delta_err)),
        "uniform_frontier_max_abs_error_eps_H": float(max(eps_h_err)),
        "uniform_frontier_violations": uniform_front_bad,
        "bridge_max_abs_error": float(max(bridge_err)),
        "bridge_theta_outside_unit_interval": bridge_range_bad,
        "beta_star_illustration": bstar,
        "passed": bool(bstar["passed"] and max_err < TOL_GRADIENT and ordering_bad == 0 and star_range_bad == 0 and max(star_zero_err) < TOL_GRADIENT
                       and star_order_bad == 0 and max(beta_delta_err) < TOL_GRADIENT and max(eps_h_err) < TOL_GRADIENT
                       and uniform_front_bad == 0 and max(bridge_err) < TOL_GRADIENT and bridge_range_bad == 0),
    }


def beta_star_closed(share_use, pay_share):
    """beta* = 1 - h(z_D)/h(z_L) with Phi(z_D) = share_use and Phi(z_L) = pay_share * share_use (Proposition A.1)"""
    return 1.0 - float(mills_lower(norm.ppf(share_use)) / mills_lower(norm.ppf(share_use * pay_share)))


def beta_star_numerical(share_use, pay_share, s=1.0, step=FD_STEP):
    """the entry-price elasticity beta_L at which the finite-difference income gradients of ln D_c and ln P_c coincide
    (eps_P = eps_D), the thresholds sitting at Phi(z_D) = share_use and Phi(z_L) = pay_share * share_use; the derivative of the
    log shares is taken numerically, the formula h(z_D)/h(z_L) is not used (eps_kappa cancels in the difference)"""
    z_d, z_l = norm.ppf(share_use), norm.ppf(share_use * pay_share)

    def gap(beta_l):
        ln_d = lambda x: log_ndtr(z_d + x / s)                       # z_D(x) = z_D + x/s
        ln_p = lambda x: log_ndtr(z_l + (1 - beta_l) * x / s)        # z_L(x) = z_L + (1 - beta_L) x/s
        return float((ln_p(step) - ln_p(-step)) / (2 * step) - (ln_d(step) - ln_d(-step)) / (2 * step))

    return brentq(gap, -1.0, 2.0, xtol=1e-14, rtol=1e-14)


def beta_star_checks():
    """the numerical illustration of beta* in Appendix A (23% of the eligible use AI; 10%, 25% or 1% of users pay) and the statement
    that beta* falls below the observed standard-tier slope only if about nine in ten users pay"""
    rows, gaps, ok = [], [], True
    for pay, q in QUOTED_BSTAR.items():
        b_cf, b_fd = beta_star_closed(SHARE_USE, pay), beta_star_numerical(SHARE_USE, pay)
        agree = round(b_cf + ROUND_GUARD, 2) == q and round(b_fd + ROUND_GUARD, 2) == q
        ok &= agree and 0 < b_cf < 1
        gaps.append(abs(b_cf - b_fd))
        rows.append({"share_of_users_who_pay": pay, "quoted": q, "beta_star_closed_form": b_cf, "beta_star_finite_differences": b_fd,
                     "agree_to_two_decimals": bool(agree)})
    pi_star = brentq(lambda pi: beta_star_numerical(SHARE_USE, pi) - BSTAR_SLOPE, 0.5, 0.999999, xtol=1e-12)
    pi_ok = BSTAR_PAY_SHARE[0] < pi_star < BSTAR_PAY_SHARE[1]
    # beta* decreases in the share of payers (the more of the users pay, the closer the two margins are)
    grid = np.linspace(0.01, 0.99, 99)
    decreasing = bool(np.all(np.diff([beta_star_closed(SHARE_USE, pi) for pi in grid]) < 0))
    manuscript = {"found": False}
    txt = manuscript_text()
    if txt is not None:
        i = txt.find(QUOTED_BSTAR_ANCHOR)
        sent = txt[i:txt.find(";", i)] if i >= 0 else ""
        nums = re.findall(r"\b\d\.\d\d\b", sent)
        want = [f"{q:.2f}" for q in QUOTED_BSTAR.values()]
        manuscript = {"found": True, "sentence_found": i >= 0, "printed_values": nums, "equal_to_QUOTED_BSTAR": nums == want}
        ok &= nums == want
    return {
        "share_using_any_tier": SHARE_USE,
        "quoted_values": rows,
        "max_abs_gap_closed_form_vs_finite_differences": float(max(gaps)),
        "tolerance": TOL_BETA_STAR,
        "observed_standard_tier_slope": BSTAR_SLOPE,
        "share_of_users_who_pay_at_which_beta_star_equals_the_slope": float(pi_star),
        "interval_for_about_nine_in_ten": list(BSTAR_PAY_SHARE),
        "beta_star_strictly_decreasing_in_share_of_payers": decreasing,
        "manuscript_sentence": manuscript,
        "passed": bool(ok and max(gaps) < TOL_BETA_STAR and pi_ok and decreasing),
    }


# ------------------------------------------------------------------------------------------------ (iii) Proposition A.2
def optimal_increment(c, s):
    """income-normalised optimal price increment x* for lognormal valuations (ln v~ = N(0, s^2), v = y v~), solving the first-order
    condition [1 - G(x)] - (x - c) g(x) = 0 of max_x (x - c)[1 - G(x)] with c = Delta c / (Delta q y), written as
    1 - (x - c) lambda(z) / (s x) = 0 with z = ln(x)/s (divided by 1 - G, which keeps it well conditioned in the far tail)"""
    def foc(x):
        return 1.0 - (x - c) * hazard(np.log(x) / s) / (s * x)

    hi = c + 1.0
    while foc(hi) > 0:
        hi *= 2
    return brentq(foc, c * (1 + 1e-13), hi, xtol=1e-15, rtol=1e-14)


def cost_for_share(L, s):
    """cost increment c at which the optimal increment has marginal-cost share L = c / x*(c)"""
    def gap(u):
        c = np.exp(u)
        return c / optimal_increment(c, s) - L

    return float(np.exp(brentq(gap, -60.0, 120.0, xtol=1e-13)))


def beta_numerical(c0, s, step=1e-5):
    """d ln(Delta p*) / d ln y by central differences, ln Delta p* = ln y + ln x*(c0 y0 / y)"""
    def lp(u):
        return u + np.log(optimal_increment(c0 * np.exp(-u), s))
    return (lp(step) - lp(-step)) / (2 * step)


def xi_numerical(x, s, step=1e-5):
    """xi = d Lambda / d ln x at x, Lambda = 1 - 1/eta, eta = x g(x) / [1 - G(x)] (demand elasticity of the lognormal), by central
    differences; eta is evaluated in logs so that it stays finite in the far tail"""
    def lerner(u):
        xx = np.exp(u)
        z = u / s
        eta = np.exp(np.log(xx) + norm.logpdf(z) - np.log(s * xx) - norm.logsf(z))
        return 1 - 1 / eta
    u = np.log(x)
    return (lerner(u + step) - lerner(u - step)) / (2 * step)


def supply_checks():
    s_grid = (0.3, 0.4, 0.5, 0.7, 0.85, 1.0, 1.25, 1.5, 1.75, 2.0)            # dispersions of the lognormal valuations, S_RANGE included
    l_grid = (0.02, 0.05, 0.1, 0.25, 0.4, 0.5, 0.65, 0.8, 0.9, 0.95)         # marginal-cost shares L = Delta c / Delta p*
    rows, e_xi, e_cf, e_z = [], [], [], []
    for s in s_grid:
        for L in l_grid:
            c0 = cost_for_share(L, s)
            xs = optimal_increment(c0, s)
            L_num = c0 / xs
            b_num = beta_numerical(c0, s)
            xi = xi_numerical(xs, s)
            b_xi = xi / (xi + L_num)
            b_cf, z_cf = beta_closed(L_num, s)
            e_xi.append(abs(b_num - b_xi))
            e_cf.append(abs(b_num - b_cf))
            e_z.append(abs(np.log(xs) / s - z_cf))
            rows.append({"s": s, "L": round(L_num, 9), "beta_numerical": b_num, "beta_xi_formula": b_xi, "beta_closed_form": b_cf})
    # values quoted in Appendix A, confirmed to two decimals by both routes
    quoted_rows, quoted_ok = [], True
    for s, vals in QUOTED.items():
        for L, q in zip(QUOTED_L, vals):
            c0 = cost_for_share(L, s)
            b_num = beta_numerical(c0, s)
            b_cf, _ = beta_closed(L, s)
            ok = round(b_num + ROUND_GUARD, 2) == q and round(b_cf + ROUND_GUARD, 2) == q
            quoted_ok &= ok
            quoted_rows.append({"s": s, "L": L, "quoted": q, "beta_numerical": b_num, "beta_closed_form": b_cf, "agree_to_two_decimals": bool(ok)})
    # the quoted sentence of the manuscript, when the manuscript is present (anonymised or partial copies of the package skip it)
    txt = manuscript_text()
    manuscript = {"found": txt is not None}
    if txt is not None:
        i = txt.find(QUOTED_ANCHOR)
        sent = re.split(r"\.\s+[A-Z]", txt[i:txt.find("\n", i)], maxsplit=1)[0] if i >= 0 else ""
        nums = re.findall(r"\b\d\.\d\d\b", sent)
        want = [f"{q:.2f}" for vals in QUOTED.values() for q in vals]
        manuscript.update({"sentence_found": i >= 0, "printed_values": nums, "equal_to_QUOTED": nums == want})
        quoted_ok &= nums == want
    # limits and monotonicity on a fine grid
    s_mono = sorted(set(np.round(np.linspace(S_RANGE[0], S_RANGE[1], 18), 6)) | {0.7, 1.0})
    l_fine = np.concatenate([np.linspace(0.0, 0.99, 100), np.linspace(0.99, 0.999, 10)[1:]])
    mono_ok, beta0_err, beta_end, in_unit = True, 0.0, 0.0, True
    min_step = np.inf
    for s in s_mono:
        b = np.array([beta_closed(L, s)[0] for L in l_fine])
        d = np.diff(b)
        mono_ok &= bool(np.all(d < 0))
        min_step = min(min_step, float(-d.max()))
        beta0_err = max(beta0_err, abs(b[0] - 1.0))
        beta_end = max(beta_end, float(b[-1]))
        in_unit &= bool(np.all((b > 0) & (b <= 1 + TOL_UNIT)))
    zg = np.linspace(-10, 10, 8001)
    lam_prime_sup = float(np.max(hazard(zg) * (hazard(zg) - zg)))
    max_err = float(max(max(e_xi), max(e_cf)))
    return {
        "grid_dispersions": list(s_grid),
        "grid_cost_shares": list(l_grid),
        "grid_points": len(rows),
        "max_abs_gap_numerical_vs_xi_formula": float(max(e_xi)),
        "max_abs_gap_numerical_vs_closed_form": float(max(e_cf)),
        "max_abs_gap_optimum_z_vs_hazard_equation": float(max(e_z)),
        "tolerance": TOL_BETA,
        "quoted_values": quoted_rows,
        "quoted_values_confirmed_to_two_decimals": bool(quoted_ok),
        "manuscript_sentence": manuscript,
        "monotonicity": {
            "dispersion_range": list(S_RANGE),
            "dispersions_checked": int(len(s_mono)),
            "cost_shares_per_dispersion": int(len(l_fine)),
            "strictly_decreasing_in_L": bool(mono_ok),
            "smallest_decrease_between_grid_points": float(min_step),
            "beta_in_unit_interval": bool(in_unit),
            "beta_at_L_0_max_abs_gap_to_one": float(beta0_err),
            "top_of_L_grid": float(l_fine[-1]),
            "largest_beta_at_top_of_L_grid": float(beta_end),
            "z_grid_for_lambda_prime": [-10, 10],
            "lambda_prime_supremum_on_z_grid": lam_prime_sup,
        },
        "passed": bool(max_err < TOL_BETA and max(e_z) < TOL_OPTIMUM_Z and quoted_ok and mono_ok and in_unit
                       and beta0_err < TOL_BETA_AT_ZERO and beta_end < BETA_AT_TOP_MAX and lam_prime_sup < 1),
    }


# ------------------------------------------------------------------------------------------------ driver
def verify(seed=SEED):
    rng = np.random.default_rng(seed)
    utility = choice_checks(rng)
    gradient = gradient_checks(rng)
    supply = supply_checks()
    return {
        "seed": seed,
        "numpy_version": np.__version__,
        "scipy_version": scipy.__version__,
        "scope": "Numerical verification of maintained-model algebra (Section 3, Appendix A), not empirical assumptions",
        "tolerances": TOLERANCES,
        "utility_checks": utility,
        "gradient_checks": gradient,
        "supply_checks": supply,
        "passed": bool(utility["passed"] and gradient["passed"] and supply["passed"]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
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
