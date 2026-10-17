#!/usr/bin/env python3
"""Standard-library numerical checks of the tier model of Appendix A (version 3.1).

Run:  python3 checks/sim_check.py  [writes checks/results/sim_output.txt and prints it; run_revision.sh runs it after
      code/12_default_panel.py has written data/processed/wave2_plan_vs_default.csv, which part F reads]

Notation (v3.1): ln v ~ N(mu_c, s^2), mu_c = m + ln y_c, so v~ = v / y_c has ln v~ ~ N(m, s^2) in every market.
A threshold T has standardised distance z = (mu_c - ln T)/s; the share above it is Phi(z); h(z) = phi(z)/Phi(z).
Price increment of tier k over the option below: Delta p_k; quality increment Delta q_k; cost increment Delta c_k.
Normalised increment x = Delta p_k / (Delta q_k y_c); normalised cost chat = Delta c_k / (Delta q_k y_c).
Cost share of the increment l = Delta c_k / Delta p_k (written ell_k in the LaTeX).

Parts
  A  Proposition A.2: closed form beta = (z*+h*)/(z*+2h*-s), h* = s/(1-l), against finite differences of the numerical optimum,
     against xi/(xi+l) and 1 - l*rho (rho = cost pass-through); quoted values; strict monotonicity in l; concavity of
     Lambda in ln x (the general sufficient condition); valuation scaling y^sigma (Proposition A.2(iii)); proportional costs (beta = 1).
  B  Log-concavity facts: the lognormal density is log-convex for ln x > m + 1 - s^2; its level hazard is
     non-monotone; the demand elasticity eta(x) = h(z)/s is increasing.
  C  Proposition A.1: income gradients by finite differences; beta* illustration (0.44, 0.34, 0.58) and the pay share at
     which beta* = 0.04.
  D  The two-tier menu: separability (joint optimum = separate increments), dollar-for-dollar pass-through of p_L into p_H,
     income elasticities of p_L, of the increment and of the level p_H; the frontier price held at the default ("pinned");
     the dampening of entry-tier localisation when p_H is pinned; override gains (the condition for a fixed override cost K
     to support "entry localised, frontier at default"); the within-storefront ratio and the increment in each regime.
  E  Cross-border arbitrage with a friction chi common to tiers: cross-tier arbitrage bound; constrained optimum in a poor
     storefront; implication of the sustained entry-tier dollar gap for the $20 and $200 tiers.
  F  Descriptive check on the replication data (read-only): within-storefront dollar increment between a frontier plan and
     the capped plan of the same app, relative to the default increment, against income.
"""

import csv
import math
import os
import statistics
import random

OUT_LINES = []


def out(s=""):
    OUT_LINES.append(s)
    print(s)


SQ2 = math.sqrt(2.0)
SQ2PI = math.sqrt(2.0 * math.pi)


def Phi(z):
    return 0.5 * math.erfc(-z / SQ2)


def phi(z):
    return math.exp(-0.5 * z * z) / SQ2PI


def h(z):
    """phi(z)/Phi(z): lower-tail inverse Mills ratio; with z = (mu - ln T)/s it is s times the hazard of ln v at ln T"""
    if z < -30.0:                      # asymptotic expansion, Phi underflows further out
        a = -z
        return a + 1.0 / a - 2.0 / a ** 3
    return phi(z) / Phi(z)


def z_of_h(target, lo=None, hi=60.0):
    """solve h(z) = target (h strictly decreasing from +inf to 0; h(z) ~ -z for z -> -inf)"""
    if lo is None:
        lo = -target - 60.0
    for _ in range(400):
        mid = 0.5 * (lo + hi)
        if h(mid) > target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ------------------------------------------------------------------------------------------------ single increment
def x_star(chat, s, m=0.0):
    """optimal normalised increment: max_x (x - chat) Phi((m - ln x)/s); FOC (1 - chat/x) h(z)/s = 1, increasing in x"""
    def f(u):
        x = math.exp(u)
        return (1.0 - chat / x) * h((m - u) / s) / s - 1.0
    lo = math.log(chat) + 1e-12 if chat > 0 else m - 40.0 * s
    hi = lo + 1.0
    while f(hi) < 0:
        hi += 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
    return math.exp(0.5 * (lo + hi))


def beta_closed(l, s):
    hs = s / (1.0 - l)
    z = z_of_h(hs)
    return (z + hs) / (z + 2.0 * hs - s), z


def chat_for_share(l, s, m=0.0):
    """normalised cost increment at which the optimal increment has cost share l"""
    if l == 0:
        return 0.0
    hs = s / (1.0 - l)
    z = z_of_h(hs)
    x = math.exp(m - s * z)
    return l * x


def beta_fd(chat0, s, sigma=1.0, m=0.0, step=1e-4):
    """d ln(Delta p*) / d ln y with v = y^sigma v~: Delta p* = Delta q y^sigma x*(Delta c/(Delta q y^sigma)); Delta q = 1"""
    def lp(u):
        ys = math.exp(sigma * u)
        return math.log(ys * x_star(chat0 / ys, s, m))
    return (lp(step) - lp(-step)) / (2 * step)


def Lambda(u, s, m=0.0):
    """Lambda(x) = 1 - 1/eta(x), eta = h(z)/s, z = (m - ln x)/s, as a function of u = ln x"""
    return 1.0 - s / h((m - u) / s)


def xi_fd(x, s, m=0.0, step=1e-5):
    u = math.log(x)
    return (Lambda(u + step, s, m) - Lambda(u - step, s, m)) / (2 * step)


def part_A():
    out("=" * 100)
    out("A. Proposition A.2 (lognormal valuations)")
    out("=" * 100)
    s_grid = (0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0)
    l_grid = (0.02, 0.1, 0.25, 0.4, 0.5, 0.65, 0.8, 0.9, 0.95)
    e_fd = e_xi = e_rho = 0.0
    for s in s_grid:
        for l in l_grid:
            c0 = chat_for_share(l, s)
            xs = x_star(c0, s)
            b_cf, z = beta_closed(l, s)
            b_num = beta_fd(c0, s)
            xi = xi_fd(xs, s)
            b_xi = xi / (xi + l)
            dc = 1e-6 * max(c0, 1e-3)
            rho = (x_star(c0 + dc, s) - x_star(c0 - dc, s)) / (2 * dc)
            b_rho = 1.0 - l * rho
            e_fd = max(e_fd, abs(b_num - b_cf))
            e_xi = max(e_xi, abs(b_xi - b_cf))
            e_rho = max(e_rho, abs(b_rho - b_cf))
    out(f"max |beta(finite differences of optimum) - closed form (z*+h*)/(z*+2h*-s)| = {e_fd:.2e}")
    out(f"max |xi/(xi+l) - closed form| = {e_xi:.2e};   max |1 - l*rho - closed form| = {e_rho:.2e}")
    out("Quoted values (paper: s=1: 0.63, 0.30, 0.05; s=0.7: 0.76, 0.44, 0.09 at l = 1/4, 1/2, 4/5):")
    for s in (1.0, 0.7):
        vals = [beta_closed(l, s)[0] for l in (0.25, 0.5, 0.8)]
        out(f"   s={s}: " + ", ".join(f"{v:.4f}" for v in vals))
    # monotonicity in l on a fine grid, a wide range of s
    worst = -1.0
    n_checked = 0
    top = 0.0
    b0_err = 0.0
    for s in [0.1 * k for k in range(1, 51)]:
        prev = beta_closed(0.0, s)[0]
        b0_err = max(b0_err, abs(prev - 1.0))
        for i in range(1, 400):
            l = i / 400.0
            b = beta_closed(l, s)[0]
            worst = max(worst, b - prev)          # must stay negative
            prev = b
            n_checked += 1
        top = max(top, prev)
    out(f"strictly decreasing in l: largest step beta(l_i) - beta(l_(i-1)) over s in [0.1, 5], 399 steps each "
        f"({n_checked} steps) = {worst:.3e}  (<0 required); max |beta(0)-1| = {b0_err:.1e}; "
        f"largest beta at l=0.9975 = {top:.4f}")
    out(f"beta at l = 0.9975, s = 1: {beta_closed(0.9975, 1.0)[0]:.4f} (tends to 0 as l -> 1)")
    # sufficient condition for monotonicity in general: Lambda concave in ln x  <=>  xi decreasing in ln x
    conc_bad = 0
    for s in (0.3, 0.7, 1.0, 2.0, 4.0):
        us = [-12 * s + k * 0.01 * s for k in range(2400)]
        xis = [(Lambda(u + 1e-4, s) - Lambda(u - 1e-4, s)) / 2e-4 for u in us]
        conc_bad += sum(1 for a, b in zip(xis, xis[1:]) if b > a + 1e-9)
    out(f"Lambda concave in ln x (xi non-increasing) on grids for s in (0.3,0.7,1,2,4): violations = {conc_bad}")
    # Sampford-type bound used in the analytic proof: 0 < h(z)(z+h(z)) < 1 and z + h(z) > 0
    zs = [-25 + 0.005 * k for k in range(10001)]
    lo = min(h(z) * (z + h(z)) for z in zs)
    hi = max(h(z) * (z + h(z)) for z in zs)
    mn = min(z + h(z) for z in zs)
    out(f"on z in [-25, 25]: min h(z+h) = {lo:.3e}, max h(z+h) = {hi:.6f} (<1), min (z+h) = {mn:.3e} (>0)")
    # valuation scaling y^sigma -> beta = sigma * xi/(xi+l) (Proposition A.2(iii))
    e_sig = 0.0
    for s in (0.7, 1.0, 1.5):
        for l in (0.25, 0.5, 0.8):
            c0 = chat_for_share(l, s)
            b1 = beta_closed(l, s)[0]
            for sig in (0.0, 0.3, 0.6, 1.0):
                e_sig = max(e_sig, abs(beta_fd(c0, s, sigma=sig) - sig * b1))
    out(f"Valuation scaling v = y^sigma v~ (A.2(iii)): max |beta_fd - sigma*xi/(xi+l)| = {e_sig:.2e}")
    # costs proportional to income, or ad valorem royalties: beta = 1
    s = 1.0
    c_prop = lambda y: 0.5 * y                       # cost proportional to local income
    lp = lambda u: math.log(math.exp(u) * x_star(c_prop(math.exp(u)) / math.exp(u), s))
    b_prop = (lp(1e-4) - lp(-1e-4)) / 2e-4
    out(f"cost proportional to income (c = 0.5 y): beta = {b_prop:.6f} (=1)")
    out("")


# ------------------------------------------------------------------------------------------------ B. log-concavity
def part_B():
    out("=" * 100)
    out("B. Log-concavity facts")
    out("=" * 100)
    for s in (0.5, 1.0, 1.5):
        m = 0.0
        def lng(u):  # log density of v~ at x = e^u, as a function of x: we differentiate in x numerically
            x = math.exp(u)
            return -math.log(x) - math.log(s * SQ2PI) - (u - m) ** 2 / (2 * s * s)
        # second derivative of ln g with respect to x (not ln x)
        def d2(x, eps=1e-4):
            f = lambda xx: -math.log(xx) - math.log(s * SQ2PI) - (math.log(xx) - m) ** 2 / (2 * s * s)
            e = eps * x
            return (f(x + e) - 2 * f(x) + f(x - e)) / (e * e)
        thr = m + 1 - s * s
        below = d2(math.exp(thr - 0.5))
        above = d2(math.exp(thr + 0.5))
        formula_above = (1 / math.exp(thr + 0.5) ** 2) * (1 - (1 + m - (thr + 0.5)) / s ** 2)
        # level hazard g/(1-G) of v~ and the elasticity eta = x g/(1-G) = h(z)/s
        xs = [math.exp(-4 * s + 0.01 * k * s) for k in range(1601)]
        haz = []
        eta = []
        for x in xs:
            z = (m - math.log(x)) / s
            g = phi(z) / (s * x)
            haz.append(g / Phi(z))
            eta.append(h(z) / s)
        imax = max(range(len(haz)), key=lambda i: haz[i])
        eta_incr = all(b > a for a, b in zip(eta, eta[1:]))
        out(f"s={s}: d2 ln g/dx2 at ln x = thr-0.5: {below:+.4f}; at thr+0.5: {above:+.4f} (formula {formula_above:+.4f}); "
            f"thr = m+1-s^2 = {thr:+.2f}")
        out(f"       level hazard g/(1-G) peaks at ln x = {math.log(xs[imax]):+.2f} and then falls "
            f"({haz[imax]:.3f} -> {haz[-1]:.3f}); eta(x) strictly increasing on the grid: {eta_incr}")
    out("=> lognormal valuations are not log-concave in levels, but ln v~ (normal) has an increasing hazard, which is what")
    out("   Proposition A.2 needs (eta increasing).")
    out("")


# ------------------------------------------------------------------------------------------------ C. Proposition A.1
def part_C():
    out("=" * 100)
    out("C. Proposition A.1 (income gradients of D, P, H)")
    out("=" * 100)
    rng = random.Random(20261017)
    max_err = 0.0
    order_bad = 0
    for _ in range(2000):
        s = rng.uniform(0.3, 2.0)
        td = math.exp(rng.uniform(-1, 1.5))
        tl = td * math.exp(rng.uniform(0.05, 1.5))
        th = tl * math.exp(rng.uniform(0.05, 1.5))
        mu0 = math.log(td) + s * rng.uniform(-1, 3)
        ek = rng.uniform(-0.3, 0.5)
        bl = rng.uniform(-0.5, 1.5)
        bd = rng.uniform(-1, 1.5)

        def ls(u, bl=bl, bd=bd):
            zd = (mu0 + u - math.log(td)) / s
            zl = (mu0 + u - math.log(tl) - bl * u) / s
            zh = (mu0 + u - math.log(th) - bd * u) / s
            return [ek * u + math.log(Phi(z)) for z in (zd, zl, zh)]
        st = 1e-5
        num = [(a - b) / (2 * st) for a, b in zip(ls(st), ls(-st))]
        zd, zl, zh = [(mu0 - math.log(t)) / s for t in (td, tl, th)]
        ana = [ek + h(zd) / s, ek + (1 - bl) * h(zl) / s, ek + (1 - bd) * h(zh) / s]
        max_err = max(max_err, max(abs(a - b) for a, b in zip(num, ana)))
        u0 = [(a - b) / (2 * st) for a, b in zip(ls(st, 0.0, 0.0), ls(-st, 0.0, 0.0))]
        order_bad += int(not (u0[2] > u0[1] > u0[0]))
    out(f"max |finite difference - formula| over 2000 random parameter sets = {max_err:.2e}; "
        f"uniform-pricing ordering violations = {order_bad}")
    use = 0.23
    zd = z_of_h(1.0)  # placeholder, replaced below
    def ppf(p):
        lo, hi = -40.0, 40.0
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if Phi(mid) < p:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)
    zd = ppf(use)
    for pay in (0.10, 0.25, 0.01):
        zl = ppf(use * pay)
        out(f"beta* with 23% using and {pay:.0%} of users paying = {1 - h(zd) / h(zl):.4f}")
    lo, hi = 0.5, 0.9999
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        b = 1 - h(zd) / h(ppf(use * mid))
        if b > 0.04:
            lo = mid
        else:
            hi = mid
    out(f"beta* = 0.04 when the paying share of users is {0.5 * (lo + hi):.4f} ('about nine in ten')")
    out("")


# ------------------------------------------------------------------------------------------------ D. the menu
class Menu:
    """two paid tiers over a free tier, nested regime; prices in net-of-tax dollars; profit per eligible person.
    Calibrated so that the unconstrained optimum in the reference market (y = 1) is p_L = 8, p_H = 20."""

    def __init__(self, s, lL, lH, PL=8.0, PH=20.0, m=0.0):
        self.s, self.m = s, m
        self.PL, self.PH = PL, PH
        zl, zh = z_of_h(s / (1 - lL)), z_of_h(s / (1 - lH))
        xl, xh = math.exp(m - s * zl), math.exp(m - s * zh)
        self.dqL, self.dqH = PL / xl, (PH - PL) / xh
        self.dcL, self.dcH = lL * PL, lH * (PH - PL)
        self.convex = self.dcL / self.dqL < self.dcH / self.dqH

    def S(self, T, y):
        return Phi((self.m + math.log(y) - math.log(T)) / self.s)

    def profit(self, pL, pH, y):
        if pL <= 0 or pH <= pL:
            return -1e18
        return (pL - self.dcL) * self.S(pL / self.dqL, y) + (pH - pL - self.dcH) * self.S((pH - pL) / self.dqH, y)

    def pL_star(self, y):
        return self.dqL * y * x_star(self.dcL / (self.dqL * y), self.s, self.m)

    def dH_star(self, y):
        return self.dqH * y * x_star(self.dcH / (self.dqH * y), self.s, self.m)

    def pL_given_pH(self, pH, y):
        """conditional optimum of p_L with p_H held at pH (grid scan, then golden refinement)"""
        a, b = self.dcL * 1.0000001, pH - self.dcH * 1.0000001
        n = 800
        best = max(range(n + 1), key=lambda i: self.profit(a + (b - a) * i / n, pH, y))
        lo = a + (b - a) * max(best - 1, 0) / n
        hi = a + (b - a) * min(best + 1, n) / n
        return golden(lambda p: self.profit(p, pH, y), lo, hi)


def golden(f, a, b, tol=1e-11):
    gr = (math.sqrt(5) - 1) / 2
    c, d = b - gr * (b - a), a + gr * (b - a)
    fc, fd = f(c), f(d)
    while abs(b - a) > tol * (1 + abs(a) + abs(b)):
        if fc > fd:
            b, d, fd = d, c, fc
            c = b - gr * (b - a)
            fc = f(c)
        else:
            a, c, fc = c, d, fd
            d = a + gr * (b - a)
            fd = f(d)
    return 0.5 * (a + b)


def joint_opt(M, y):
    """joint maximisation by nested golden search, without using separability"""
    def inner(pL):
        pH = golden(lambda q: M.profit(pL, q, y), pL + M.dcH * 1.0000001, pL + 5 * M.dH_star(y))
        return pH, M.profit(pL, pH, y)
    pL = golden(lambda p: inner(p)[1], M.dcL * 1.0000001, 5 * M.pL_star(y))
    return pL, inner(pL)[0]


def ols_slope(x, yv):
    n = len(x)
    mx, my = sum(x) / n, sum(yv) / n
    return sum((a - mx) * (b - my) for a, b in zip(x, yv)) / sum((a - mx) ** 2 for a in x)


def part_D():
    out("=" * 100)
    out("D. The two-tier menu: separability, pass-through, the pinned frontier price, override gains")
    out("=" * 100)
    cals = [(1.0, 0.25, 0.50), (1.0, 0.10, 0.60), (1.2, 0.30, 0.50), (0.7, 0.30, 0.60)]
    incomes = (1.0, 0.5, 0.2, 0.1, 0.05, 0.02)
    for (s, lL, lH) in cals:
        M = Menu(s, lL, lH)
        shL = M.S(M.PL / M.dqL, 1.0)
        shH = M.S((M.PH - M.PL) / M.dqH, 1.0)
        out(f"-- calibration s={s}, cost share of entry price lL={lL}, of frontier increment lH={lH} at y=1 "
            f"(dqL={M.dqL:.3f}, dqH={M.dqH:.3f}, dcL={M.dcL:.2f}, dcH={M.dcH:.2f}; convex costs: {M.convex}; "
            f"paid share {shL:.3f}, frontier share {shH:.3f} of the eligible at y=1)")
        # separability check at three incomes
        sep = 0.0
        for y in (1.0, 0.2, 0.05):
            pLj, pHj = joint_opt(M, y)
            pLs = M.pL_star(y)
            pHs = pLs + M.dH_star(y)
            sep = max(sep, abs(pLj - pLs) / pLs, abs(pHj - pHs) / pHs)
        out(f"   joint optimum vs separate increments: max relative gap = {sep:.1e}")
        # pass-through of an exogenous p_L into the optimal p_H
        y = 0.1
        pt = []
        for pL in (3.0, 5.0, 7.0):
            pH = golden(lambda q: M.profit(pL, q, y), pL + M.dcH * 1.0000001, pL + 5 * M.dH_star(y))
            pt.append(pH - pL)
        out(f"   optimal p_H - p_L for exogenous p_L = 3, 5, 7 at y=0.1: " + ", ".join(f"{d:.6f}" for d in pt)
            + "  (constant: dp_H/dp_L = 1)")
        hdr = ("   y     | unconstrained: pL*    dH*    pH*   pH*/pL* | pinned pH=20: pLo   pLo/pL*  20/pLo  incr | "
               "gains per eligible person: gL|H=20  gH|L*   ratio")
        out(hdr)
        rows = []
        for y in incomes:
            pLs, dHs = M.pL_star(y), M.dH_star(y)
            pHs = pLs + dHs
            pLo = M.pL_given_pH(M.PH, y)
            base = M.profit(M.PL, M.PH, y)
            g_L = M.profit(pLo, M.PH, y) - base                     # override the entry tier only
            g_H_after = M.profit(pLs, pHs, y) - M.profit(pLo, M.PH, y)   # extra gain from also re-optimising the frontier
            g_Honly = M.profit(M.PL, M.PL + dHs, y) - base          # override the frontier only
            rows.append((y, pLs, dHs, pHs, pLo, g_L, g_H_after, g_Honly))
            ratio = g_H_after / g_L if g_L > 0 else float('nan')
            out(f"   {y:5.2f} |            {pLs:6.2f} {dHs:6.2f} {pHs:6.2f}  {pHs / pLs:5.2f}  |        "
                f"{pLo:6.2f}  {pLo / pLs:5.2f}   {M.PH / pLo:5.2f}  {M.PH - pLo:5.2f} |"
                f"                    {g_L:8.4f} {g_H_after:8.4f} {ratio:6.3f}")
        lny = [math.log(r[0]) for r in rows]
        b_L = ols_slope(lny, [math.log(r[1]) for r in rows])
        b_D = ols_slope(lny, [math.log(r[2]) for r in rows])
        b_H = ols_slope(lny, [math.log(r[3]) for r in rows])
        b_Lo = ols_slope(lny, [math.log(r[4]) for r in rows])
        b_Do = ols_slope(lny, [math.log(M.PH - r[4]) for r in rows])
        b_rat_u = ols_slope(lny, [math.log(r[3] / r[1]) for r in rows])
        b_rat_p = ols_slope(lny, [math.log(M.PH / r[4]) for r in rows])
        out(f"   log-log slopes over the income grid: unconstrained pL* {b_L:.3f}, increment {b_D:.3f}, level pH* {b_H:.3f}; "
            f"ratio pH/pL {b_rat_u:.3f}")
        out(f"                                        pinned pH:     pLo {b_Lo:.3f} (level pLo >= pL* everywhere), increment {b_Do:.3f} (<0), "
            f"ratio {b_rat_p:.3f}")
        # local elasticity check of the weighted-average formula at y = 0.2
        y, e = 0.2, 1e-4
        bl = (math.log(M.pL_star(y * math.exp(e))) - math.log(M.pL_star(y * math.exp(-e)))) / (2 * e)
        bd = (math.log(M.dH_star(y * math.exp(e))) - math.log(M.dH_star(y * math.exp(-e)))) / (2 * e)
        ph = lambda yy: M.pL_star(yy) + M.dH_star(yy)
        bh = (math.log(ph(y * math.exp(e))) - math.log(ph(y * math.exp(-e)))) / (2 * e)
        w = M.pL_star(y) / ph(y)
        out(f"   at y=0.2: beta_L={bl:.4f}, beta_dH={bd:.4f}, beta_H(level)={bh:.4f}, weighted average={w * bl + (1 - w) * bd:.4f};"
            f" closed forms {beta_closed(M.dcL / M.pL_star(y), s)[0]:.4f}, {beta_closed(M.dcH / M.dH_star(y), s)[0]:.4f}")
        out(f"   min over the grid of pLo/pL* = {min(r[4] / r[1] for r in rows):.6f} (>= 1: holding pH at the default "
            f"never lowers the optimal entry price)")
        out(f"   max over the grid of gH-only/gL|H=20 = {max((r[7] / r[5]) for r in rows if r[5] > 0):.3f} "
            f"(< 1: overriding the entry tier alone beats overriding the frontier tier alone)")
        ok_range = [r for r in rows if r[0] < 1 and r[6] < r[5]]
        out(f"   incomes below the reference at which a fixed override cost K can support 'entry overridden, frontier at "
            f"default' (gH|L* < gL|H=20): {[r[0] for r in ok_range]}")
        out("")
    out("-- role of the frontier cost share (s=1, lL=0.25): ratio gH|L*/gL|H=20 of the extra gain from re-optimising the")
    out("   frontier price to the gain from localising the entry tier, and the unconstrained level discount 1 - pH*/20")
    for lH in (0.30, 0.40, 0.50, 0.60, 0.70):
        M = Menu(1.0, 0.25, lH)
        cells = []
        for y in (0.5, 0.2, 0.1):
            pLs, dHs = M.pL_star(y), M.dH_star(y)
            pLo = M.pL_given_pH(M.PH, y)
            gL = M.profit(pLo, M.PH, y) - M.profit(M.PL, M.PH, y)
            gH = M.profit(pLs, pLs + dHs, y) - M.profit(pLo, M.PH, y)
            cells.append(f"y={y}: ratio {gH / gL:.3f}, level discount {1 - (pLs + dHs) / M.PH:.2f}, "
                         f"increment elasticity {beta_closed(M.dcH / dHs, 1.0)[0]:.2f}")
        out(f"   lH={lH:.2f} (convex costs {M.convex}): " + "; ".join(cells))
    out("")


# ------------------------------------------------------------------------------------------------ E. arbitrage
def part_E():
    out("=" * 100)
    out("E. Cross-border arbitrage with a friction chi common to tiers")
    out("=" * 100)
    # cross-tier bound: a home frontier buyer (v >= (P_H - P_L)/dq_H) gains at most P_L - p_Lc - chi from the foreign entry tier
    rng = random.Random(7)
    worst = -1e9
    for _ in range(200000):
        dqH = rng.uniform(0.2, 3)
        PL, PH = rng.uniform(2, 10), rng.uniform(12, 300)
        pLc = rng.uniform(0.5, PL)
        chi = rng.uniform(0, 5)
        v = (PH - PL) / dqH * math.exp(rng.uniform(0, 3))       # home frontier buyer
        gain_cross = (PH - pLc) - v * dqH - chi                   # utility gain of buying the foreign entry tier
        worst = max(worst, gain_cross - (PL - pLc - chi))
    out(f"max over 200,000 draws of [cross-tier gain - (P_L - p_L,c - chi)] = {worst:.3e} (<= 0: never more attractive "
        f"than same-tier entry arbitrage)")
    # two storefronts: reference y=1 at (8, 20); poor storefront y=0.04; arbitrage constraints p_k >= P_k - chi
    for (s, lL, lH) in ((1.0, 0.25, 0.5), (1.5, 0.3, 0.6)):
        M = Menu(s, lL, lH)
        y = 0.04
        pLs, dHs = M.pL_star(y), M.dH_star(y)
        out(f"-- s={s}, lL={lL}, lH={lH}; poor storefront y=0.04: unconstrained pL*={pLs:.2f}, pH*={pLs + dHs:.2f}")
        for chi in (1.0, 3.8, 8.0):
            # maximise over (pL, pH) subject to pL >= 8 - chi, pH >= 20 - chi: separable in (pL, increment) but the
            # constraint on pH couples them; brute force on pL, golden on pH
            fL = M.PL - chi
            fH = M.PH - chi
            def best_pH(pL):
                lo = max(fH, pL + M.dcH * 1.0000001)
                return golden(lambda q: M.profit(pL, q, y), lo, lo + 400.0)
            pL = golden(lambda p: M.profit(p, best_pH(p), y), max(fL, M.dcL * 1.0000001), M.PH - chi - M.dcH)
            pH = best_pH(pL)
            out(f"   chi={chi:4.1f}: constrained optimum pL={pL:6.2f} (floor {fL:5.2f}), pH={pH:6.2f} (floor {fH:5.2f});"
                f" dollar discounts {M.PL - pL:5.2f} and {M.PH - pH:5.2f}; percentage {100 * (1 - pL / M.PL):4.1f}% and "
                f"{100 * (1 - pH / M.PH):4.1f}%")
    out("Implication: with a friction common to tiers, binding arbitrage floors give equal DOLLAR discounts on both tiers;")
    out("a sustained entry-tier gap g_L reveals chi >= g_L, so the arbitrage floor of a tier priced P_k lies at least g_L/P_k")
    out("below its reference price: for g_L = $3.8, 19% on a $20 tier, 3.8% on $100, 1.9% on $200, 1.3% on $300.")
    out("")


# ------------------------------------------------------------------------------------------------ F. data (descriptive)
def part_F():
    out("=" * 100)
    out("F. Replication data (read-only): within-storefront increment relative to the default increment")
    out("=" * 100)
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "..", "data", "processed", "wave2_plan_vs_default.csv")
    if not os.path.exists(path):
        out("data file not found; skipped")
        return
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    by = {}
    for r in rows:
        by.setdefault(r["storefront"], {})[r["plan"]] = r
    pairs = [("chatgpt_plus", "chatgpt_go"), ("characterai_plus", "characterai_lite"), ("gemini_pro", "gemini_plus"),
             ("chatgpt_pro200", "chatgpt_plus"), ("m365_premium", "m365_personal")]
    for hi_plan, lo_plan in pairs:
        X, Y, grp = [], [], {}
        for sf, d in by.items():
            if hi_plan in d and lo_plan in d:
                a, b = d[hi_plan], d[lo_plan]
                try:
                    gni = float(a["gni"])
                    ph, pl = float(a["price_local"]), float(b["price_local"])
                    dh, dl = float(a["default_ref"]), float(b["default_ref"])
                except (ValueError, KeyError):
                    continue
                if ph <= pl or dh <= dl or gni <= 0:
                    continue
                X.append(math.log(gni))
                Y.append(math.log((ph - pl) / (dh - dl)))
                grp.setdefault(a["income_group"], []).append((ph - pl) / (dh - dl))
        if len(X) < 20:
            out(f"{hi_plan} - {lo_plan}: N={len(X)} (too few)")
            continue
        n = len(X)
        mx = sum(X) / n
        b = ols_slope(X, Y)
        a0 = sum(Y) / n - b * mx
        e = [yy - a0 - b * xx for xx, yy in zip(X, Y)]
        sxx = sum((xx - mx) ** 2 for xx in X)
        se = math.sqrt(sum(((xx - mx) ** 2) * ee ** 2 for xx, ee in zip(X, e)) / sxx ** 2 * n / (n - 2))
        med = {k: statistics.median(v) for k, v in grp.items()}
        out(f"{hi_plan} - {lo_plan}: slope of ln(increment / default increment) on ln GNI = {b:+.4f} (HC1 {se:.4f}), N={n}; "
            "median ratio by group: " + ", ".join(f"{k.split()[0]} {med[k]:.3f}" for k in
                                                  ("High income", "Upper-middle income", "Lower-middle income", "Low income")
                                                  if k in med))
    out("Reading: a negative slope (larger dollar increment in poorer storefronts) cannot be produced by an interior optimum")
    out("of the nested menu, in which the optimal increment rises with income; it requires the frontier price to be held up.")
    out("")


def main():
    part_A()
    part_B()
    part_C()
    part_D()
    part_E()
    part_F()
    here = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(here, "results"), exist_ok=True)
    with open(os.path.join(here, "results", "sim_output.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(OUT_LINES) + "\n")


if __name__ == "__main__":
    main()
