"""
15_vintage_test.py   (no network; run after 12_default_panel.py)
Vintage test of the deviations from the estimated Apple default schedule.

Idea.  Apple does not re-equalise auto-renewable subscriptions after later tax or exchange-rate changes (Apple Developer Help,
"Manage pricing for auto-renewable subscriptions": "Retail price changes initiated by Apple due to tax changes and significant
foreign exchange rate movements will exclude auto-renewable subscriptions"; Apple Developer News of 6 Feb 2025, 16 May 2025, 30 Oct
2025 and 11 May 2026: "Prices won't change in any region if your In-App Purchase is an auto-renewable subscription", and of 27 Aug
2026: "Excludes auto-renewable subscriptions"; read on 16 Oct 2026, see apple_policy_sources.md of the revision files).  The local
price of a subscription is therefore the comparable price that App Store Connect generated on the day the developer set (or last
reset) it.  Both the 30-app panel (93% subscriptions) and the AI plans are auto-renewable subscriptions, so their local prices carry
different vintages.  If the frontier plans are priced by the platform's schedule and their deviations from the revealed schedule are
vintage noise, then (a) the deviations are centred on zero, (b) they are larger in storefronts whose currency has moved more against
the US dollar since March 2024, and (c) they are small in storefronts priced in US dollars (no exchange-rate vintage).  The income
slope of the deviations is estimated with and without a control for the currency movement.  The entry tier (ChatGPT Go) is shown for
contrast: its deviation is a price decision, not a vintage.

Inputs   data/processed/wave2_plan_vs_default.csv (12_default_panel.py)
         data/raw/fx_hist/usd_<date>.json   fawazahmed0 currency-api rates (units per US$) on 2024-03-06, 2024-10-15, 2025-04-15,
                                            2025-10-15, 2026-04-15 and 2026-10-15
Outputs  output/tables/W14_vintage.csv         one row per sample (pooled frontier plans, ChatGPT Go, the ten frontier plans)
         output/tables/W14b_fx_movement.csv    FX movement of each storefront currency
         output/results_wave2.json             vint_<group>_<statistic> (group: frontier, go, or a plan key) and vint_* counts

Definitions.
  * FX movement of a currency = the range of ln(units per US$) over the six dates (max - min); 0 for the US dollar; a storefront whose
    currency is missing on any of the six dates has no movement and drops out of every statistic (none does).
  * Sample of a group: its plan x storefront rows of wave2_plan_vs_default.csv with a deviation (dev = ln(local price / default
    reference)), income data and an FX movement; the US is not in the file.  "frontier" pools ChatGPT Plus and Pro 200, Claude Pro and
    Max 20x, Google AI Pro and Ultra, Perplexity Pro, SuperGrok and SuperGrok Heavy and Microsoft 365 Premium (ten plans); "go" is
    ChatGPT Go.  Rows of the same storefront appear once per plan in the pooled sample.
  * (i) slope: OLS of dev on ln(GNI per capita); (ii) slope_ctrl and coef_fx: OLS of dev on ln(GNI per capita) and the FX movement;
    (iii) absdev_fx: OLS of |dev| on the FX movement; HC1 standard errors (n / (n - k)), each with a constant.
    Supplementary: the same standard errors clustered by storefront currency (all storefronts priced in US dollars form one
    cluster; statsmodels' CR1 with the small-sample factor G / (G - 1) (N - 1) / (N - k)), written as *_cl, and clustered by
    storefront (*_sf; the pooled sample has ten rows per storefront): the movement is a property of the currency and the rows of a
    storefront share its vintage, so the HC1 errors of the pooled regressions are too small.
  * median_dev, mean_dev; the share of rows with |dev| <= 0.03 among storefronts priced in US dollars (usd), among local-currency
    storefronts whose currency moved by at most ln 1.1 (stable) and among storefronts whose currency moved by more than ln 1.3
    (moved), with the numbers of rows.
"""
import os
for _v in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ[_v] = "1"                                   # fixed order of summation: the output is byte-identical between runs
import json, math, pathlib
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROC, TAB, RAW = ROOT / "data" / "processed", ROOT / "output" / "tables", ROOT / "data" / "raw" / "fx_hist"
DATES = ["2024-03-06", "2024-10-15", "2025-04-15", "2025-10-15", "2026-04-15", "2026-10-15"]
FRONT = ["chatgpt_plus", "chatgpt_pro200", "claude_pro", "claude_max20x", "gemini_pro", "gemini_ultra", "perplexity_pro", "supergrok",
         "supergrok_heavy", "m365_premium"]
GROUPS = [("frontier", FRONT), ("go", ["chatgpt_go"])] + [(p, [p]) for p in FRONT]
STABLE, MOVED, BAND = math.log(1.1), math.log(1.3), 0.03
INT_KEYS = ("n", "n_currencies", "n_storefronts", "n_usd", "n_stable", "n_moved")
NAN = float("nan")
R = {}

# ================================================================================================ FX movement of each currency
FX = {}
for dt in DATES:
    j = json.load(open(RAW / f"usd_{dt}.json"))
    assert j["date"] == dt, f"usd_{dt}.json is the snapshot of {j['date']}"
    FX[dt] = j["usd"]


def movement(cur):
    """Range of ln(units per US$) over the six dates; 0 for the US dollar; None if the currency is missing on any date."""
    if cur == "USD":
        return 0.0
    v = [FX[dt].get(cur.lower()) for dt in DATES]
    if any(x is None for x in v):
        return None
    lv = [math.log(x) for x in v]
    return max(lv) - min(lv)


pvd = pd.read_csv(PROC / "wave2_plan_vs_default.csv", keep_default_na=False, na_values=[""])
pvd = pvd[(pvd.storefront != "us") & pvd.dev_log.notna() & pvd.gni.notna()].copy()
move = {c: movement(c) for c in sorted(pvd.currency.unique())}
pvd["move"] = pvd.currency.map(move)
n_missing_fx = int(pvd.move.isna().sum())
pvd = pvd[pvd.move.notna()].copy()


def ols(y, X, cluster, cluster_sf):
    """(coefficients, HC1 s.e., currency-clustered s.e., storefront-clustered s.e.) of the OLS of y on a constant and the columns
    of X."""
    X = sm.add_constant(np.asarray(X, float))
    m = sm.OLS(np.asarray(y, float), X)
    h = m.fit(cov_type="HC1")
    c = m.fit(cov_type="cluster", cov_kwds={"groups": cluster})
    f = m.fit(cov_type="cluster", cov_kwds={"groups": cluster_sf})
    return h.params, h.bse, c.bse, f.bse


def share(a):
    return (float((a <= BAND).mean()) if len(a) else NAN), int(len(a))


# ================================================================================================ the samples
rows = []
for group, plans in GROUPS:
    g = pvd[pvd.plan.isin(plans)]
    dev, ad, lg, mv = g.dev_log.values, g.dev_log.abs().values, np.log(g.gni.values), g.move.values
    cl, sf = pd.factorize(g.currency)[0], pd.factorize(g.storefront)[0]
    b1, s1, c1, f1 = ols(dev, lg, cl, sf)
    b2, s2, c2, f2 = ols(dev, np.column_stack([lg, mv]), cl, sf)
    b3, s3, c3, f3 = ols(ad, mv, cl, sf)
    usd, stable, moved = (share(ad[(g.currency == "USD").values]), share(ad[((g.currency != "USD") & (g.move <= STABLE)).values]),
                          share(ad[(g.move > MOVED).values]))
    rec = dict(group=group, plans=";".join(plans), n=len(g), n_currencies=int(g.currency.nunique()), n_storefronts=int(g.storefront.nunique()),
               slope=b1[1], se=s1[1], se_cl=c1[1], se_sf=f1[1],
               slope_ctrl=b2[1], se_ctrl=s2[1], se_ctrl_cl=c2[1], se_ctrl_sf=f2[1], coef_fx=b2[2], se_fx=s2[2], se_fx_cl=c2[2], se_fx_sf=f2[2],
               absdev_fx=b3[1], absdev_fx_se=s3[1], absdev_fx_se_cl=c3[1], absdev_fx_se_sf=f3[1],
               median_dev=float(np.median(dev)), mean_dev=float(dev.mean()),
               within3_usd=usd[0], n_usd=usd[1], within3_stable=stable[0], n_stable=stable[1], within3_moved=moved[0], n_moved=moved[1])
    rows.append(rec)
    for k, v in rec.items():
        if k not in ("group", "plans") and v == v:                          # a missing share (no rows in the class) is not written
            R[f"vint_{group}_{k}"] = int(v) if k in INT_KEYS else float(v)
w14 = pd.DataFrame(rows)
w14.round(10).to_csv(TAB / "W14_vintage.csv", index=False)

# storefront currencies and their movement; storefronts of the three classes in the ChatGPT Go sample (all storefronts with a deviation)
go = pvd[pvd.plan == "chatgpt_go"]
cls = np.where(go.currency == "USD", "usd", np.where(go.move > MOVED, "moved", np.where(go.move <= STABLE, "stable", "intermediate")))
fxm = (pvd.drop_duplicates(["storefront"]).groupby("currency").agg(storefronts=("storefront", "size"), movement=("move", "first")).reset_index())
fxm["class"] = np.where(fxm.currency == "USD", "usd", np.where(fxm.movement > MOVED, "moved", np.where(fxm.movement <= STABLE, "stable", "intermediate")))
fxm.sort_values(["movement", "currency"], ascending=[False, True]).round(10).to_csv(TAB / "W14b_fx_movement.csv", index=False)
R.update(vint_fx_dates=len(DATES), vint_currencies=int(fxm.shape[0]), vint_dropped_missing_fx=n_missing_fx,
         vint_storefronts=int(len(go)), vint_storefronts_usd=int((cls == "usd").sum()), vint_storefronts_stable=int((cls == "stable").sum()),
         vint_storefronts_moved=int((cls == "moved").sum()), vint_storefronts_intermediate=int((cls == "intermediate").sum()),
         vint_currencies_moved=int((fxm["class"] == "moved").sum()))

res = json.load(open(ROOT / "output" / "results_wave2.json"))
for k in [k for k in res if k.startswith("vint_") and k not in R]:
    del res[k]                                                             # stale keys of an earlier version
res.update({k: (round(v, 6) if isinstance(v, float) else v) for k, v in R.items()})
json.dump(res, open(ROOT / "output" / "results_wave2.json", "w"), indent=1)

f = w14.set_index("group")
for g in ["frontier", "go"]:
    r = f.loc[g]
    print(f"{g}: N = {r.n}, income slope {r.slope:.4f} ({r.se:.4f}) [{r.se_cl:.4f}], with FX control {r.slope_ctrl:.4f} ({r.se_ctrl:.4f}) [{r.se_ctrl_cl:.4f}], "
          f"coef. on FX movement {r.coef_fx:.3f} ({r.se_fx:.3f}) [{r.se_fx_cl:.3f}], |dev| on movement {r.absdev_fx:.3f} ({r.absdev_fx_se:.3f}) "
          f"[{r.absdev_fx_se_cl:.3f}], median dev {r.median_dev:.4f}; within 3%: US$ {r.within3_usd:.3f} (n = {r.n_usd}), stable "
          f"{r.within3_stable:.3f} ({r.n_stable}), moved {r.within3_moved:.3f} ({r.n_moved})   [clustered by currency, {r.n_currencies} clusters]")
print(f"storefronts in the ChatGPT Go sample: {len(go)} ({R['vint_storefronts_usd']} priced in US$, {R['vint_storefronts_stable']} stable, "
      f"{R['vint_storefronts_intermediate']} intermediate, {R['vint_storefronts_moved']} moved: "
      f"{', '.join(sorted(go[go.move > MOVED].storefront))}); currencies that moved by more than 30%: "
      f"{', '.join(fxm[fxm['class'] == 'moved'].currency)}; rows dropped for a missing rate: {n_missing_fx}")
