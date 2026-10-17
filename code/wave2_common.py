"""
wave2_common.py -- helpers shared by the second-wave scripts (09b_wave2_items.py, 12_default_panel.py, 13_relative_prices.py).
Not run on its own; the scripts in code/ import it (python code/<script>.py puts code/ on the import path).

  * constants: LMIC (low plus lower-middle income, the group of the income-group medians), SHORT (income-group abbreviations);
  * regression helpers on one regressor: ols_hc1 (slope, HC1 standard error, n), ols_hc3 (HC3), wls_hc1 (weighted, HC1) and
    ols_cr1 (HC1 and the currency-clustered CR1 standard error with the small-sample factor G/(G-1) (N-1)/(N-2));
  * Apple's default schedule as revealed by the small-developer panel: panel_points() prepares the panel's items, schedule()
    builds the ladder (modal local price per storefront and US price point) and the storefront multipliers under a tie rule of
    RULES, modal() is its helper.  MAIN is the rule of the package (the mode must be unique and have share >= 0.5).  Both
    12_default_panel.py (ladder, multiplier and deviations) and 09b_wave2_items.py (the multiplier that the annual-as-monthly
    guard needs) call these functions, so the two scripts cannot disagree on the schedule.

The definitions of the schedule are documented in the docstring of 12_default_panel.py.
"""
import collections, math
import numpy as np

NAN = float("nan")
LMIC = ("Low income", "Lower-middle income")
SHORT = {"High income": "HIC", "Upper-middle income": "UMIC", "Lower-middle income": "LMIC", "Low income": "LIC"}


# ------------------------------------------------------------------------------------------------ regression helpers
def ols_hc1(x, y):
    """Slope, HC1 standard error and n of a simple OLS regression of y on x."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    n = len(x)
    if n < 3:
        return NAN, NAN, n
    xm, ym = x.mean(), y.mean()
    sxx = ((x - xm) ** 2).sum()
    b = ((x - xm) * (y - ym)).sum() / sxx
    e = y - (ym - b * xm) - b * x
    v = ((x - xm) ** 2 * e ** 2).sum() / sxx ** 2 * n / (n - 2)
    return float(b), float(math.sqrt(v)), n


def ols_hc3(x, y):
    """Slope, HC3 standard error (squared residuals divided by (1 - leverage)^2) and n of a simple OLS regression."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    n = len(x)
    if n < 4:
        return NAN, NAN, n
    xm, ym = x.mean(), y.mean()
    sxx = ((x - xm) ** 2).sum()
    b = ((x - xm) * (y - ym)).sum() / sxx
    e = y - (ym - b * xm) - b * x
    h = 1.0 / n + (x - xm) ** 2 / sxx
    v = ((x - xm) ** 2 * e ** 2 / (1 - h) ** 2).sum() / sxx ** 2
    return float(b), float(math.sqrt(v)), n


def wls_hc1(x, y, w):
    """Slope, HC1 standard error and n of the weighted least-squares regression of y on x with weights w (the sandwich of
    statsmodels' WLS with cov_type='HC1': n / (n - 2) times the heteroskedasticity-robust variance of the weighted estimator)."""
    x, y, w = np.asarray(x, float), np.asarray(y, float), np.asarray(w, float)
    n = len(x)
    if n < 3:
        return NAN, NAN, n
    xm, ym = (w * x).sum() / w.sum(), (w * y).sum() / w.sum()
    sxx = (w * (x - xm) ** 2).sum()
    b = (w * (x - xm) * (y - ym)).sum() / sxx
    e = y - (ym - b * xm) - b * x
    v = (w ** 2 * (x - xm) ** 2 * e ** 2).sum() / sxx ** 2 * n / (n - 2)
    return float(b), float(math.sqrt(v)), n


def ols_cr1(x, y, cluster):
    """(slope, HC1 s.e., CR1 s.e., n, number of clusters) of a simple OLS regression of y on x.  CR1 clusters the scores
    (x - mean x) e by `cluster` and applies the small-sample factor G / (G - 1) * (N - 1) / (N - 2)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    n = len(x)
    if n < 3:
        return NAN, NAN, NAN, n, 0
    xm, ym = x.mean(), y.mean()
    sxx = ((x - xm) ** 2).sum()
    b = ((x - xm) * (y - ym)).sum() / sxx
    e = y - (ym - b * xm) - b * x
    hc1 = math.sqrt(((x - xm) ** 2 * e ** 2).sum() / sxx ** 2 * n / (n - 2))
    score = collections.defaultdict(float)
    for xi, ei, g in zip(x, e, cluster):
        score[g] += (xi - xm) * ei
    ng = len(score)
    if ng < 2:
        return float(b), hc1, NAN, n, ng
    cr1 = math.sqrt(sum(v * v for v in score.values()) / sxx ** 2 * (ng / (ng - 1)) * ((n - 1) / (n - 2)))
    return float(b), hc1, cr1, n, ng


# ------------------------------------------------------------------------------------------------ Apple's default schedule
# tie handling and share threshold of each rule: (what a mode shared by several prices becomes, share must exceed one half?)
MAIN = "none"                             # the rule of the package: the mode must be unique and have share >= 0.5
RULES = {"none": ("none", False),         # 50/50 ties are dropped; other entries at exactly one half are kept
         "strict": ("none", True),        # a price needs a strict majority (share > 0.5)
         "fileorder": ("first", False),   # first pass: tie -> price listed first in the raw file, share >= 0.5
         "low": ("low", False), "high": ("high", False)}


def modal(vals):
    """(prices at the highest frequency in order of first appearance, their count, number of items)."""
    c = collections.Counter(vals)
    top = max(c.values())
    return [v for v, k in c.items() if k == top], top, len(vals)


def panel_points(items):
    """The default-panel items that enter the schedule: outside the US and with a US price of the same item; adds the price
    point `us_pt` (US price rounded to cents) and the local price rounded to cents `loc_r`."""
    d = items[(items.storefront != "us") & items.us_price.notna()].copy()
    d["us_pt"] = d.us_price.round(2)
    d["loc_r"] = d.price_local.round(2)
    return d


def schedule(d, rule=MAIN, min_items=3):
    """Ladder and multipliers from the default-panel items d (storefront != us, with a US price) under a tie rule of RULES."""
    tie_rule, strict = RULES[rule]
    lad = {}
    for (sf, p), g in d.groupby(["storefront", "us_pt"], sort=True):
        if len(g) < min_items:
            continue
        tied, top, n = modal(list(g.loc_r))
        v = tied[0] if len(tied) == 1 else {"first": tied[0], "low": min(tied), "high": max(tied), "none": None}[tie_rule]
        has_mode = v is not None and (2 * top > n if strict else 2 * top >= n)
        lad[(sf, p)] = dict(n_items=n, modal_local=(v if has_mode else None), modal_share=top / n, tie=len(tied) > 1)
    mult = {}
    for sf in sorted({s for s, _ in lad}):
        ms = [e["modal_local"] / p for (s, p), e in lad.items() if s == sf and p >= 2.99 and e["modal_local"]]
        if len(ms) >= 3:
            med = float(np.median(ms))
            mult[sf] = (med, len(ms), (max(ms) - min(ms)) / med)
    return lad, mult
