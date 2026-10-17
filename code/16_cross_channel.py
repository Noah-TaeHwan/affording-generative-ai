"""
16_cross_channel.py   (no network; run after 12_default_panel.py)
Cross-channel check of the App Store prices: the Microsoft 365 web store (locale pages) and the
in-app purchase ranges that Google Play shows for ChatGPT, Claude and Gemini, all collected on 16 October 2026, against the App
Store prices of the second price wave.  The question is whether the App Store price of a plan is specific to the App Store channel
or the price the vendor sets for the country in every channel: the same price on the web, on Google Play and in the App Store points
to the second, a different price to the first (an in-app price list that adds the channel's own tax or fee).

Inputs   data/raw/web/ms365_web_prices.csv, play_iap_ranges.csv   (see data/raw/web/README.md)
         data/raw/fx_hist/usd_2026-10-15.json                      US$ conversion of the Google Play prices (rates of 15 Oct 2026)
         data/processed/wave2_plan_vs_default.csv (12_default_panel.py), country_panel.csv
Outputs  output/tables/W15_cross_channel.csv         summary rows (the keys column gives the results_wave2.json keys)
         output/tables/W15b_play_countries.csv       Google Play lowest in-app price, ChatGPT and Claude, by country (richest first; the
                                                     US row carries the App Store price of the plan and no log difference: it is the anchor)
         output/results_wave2.json                   xch_* scalars (xch_* keys of an earlier run that are not written again are removed)

Definitions.
  (a) Microsoft web store, monthly prices.  Personal relative to Premium within a country, relative to the same ratio in the US:
      y_c = ln(Personal_c / Premium_c) - ln(Personal_US / Premium_US), in countries other than the US with both plans on the page and
      income data (GNI per capita, Atlas); same currency and same tax treatment within a country, so no exchange rate and no default
      is involved.  Slope of y on ln(GNI), HC1; median of y in low and lower-middle income countries (LMIC) and in high-income
      countries as 100 (e^m - 1) percent.  Web against App Store: for the same product (Premium, Personal) and country, where the
      web currency equals the currency of the App Store storefront, ln(web price / App Store price) (the App Store price is the
      modal monthly price of 12_default_panel.py's plan rows, m365_premium and m365_personal), in the countries of (a): number,
      median, share within 5% (|ln ratio| <= 0.05).
  (b) Google Play, lowest in-app item.  For ChatGPT and Claude, the minimum of the in-app price range shown on the Google Play web page
      (30 countries including the US).  In the US the minimum is the price of the cheapest plan (ChatGPT Go, $8.00; Claude Pro,
      $20.00; checked against the App Store below), so it is compared with the App Store price of that plan: ln(Play minimum / App
      Store price) where the currency of the Play page equals that of the storefront (the US is the anchor and not compared);
      number, median and share within 5% of these comparisons.  The minimum in US$ at the rates of 15 Oct 2026 relative to the US
      minimum, median over the LMIC countries that also have an App Store storefront in the second wave (Bangladesh has none, so it
      is not in this median; the median over all World Bank LMIC countries of the Play sample is given as *_lmic_ratio_wb).  The Play
      range covers all in-app items, not a plan, so only the minimum is used and only for the two apps where it is a plan price;
      Gemini shows no range in any country (per the collection notes, its subscriptions are sold through Google One).
"""
import os
for _v in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ[_v] = "1"                                   # fixed order of summation: the output is byte-identical between runs
import collections, json, math, pathlib
import numpy as np
import pandas as pd
from wave2_common import LMIC, NAN, ols_hc1

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROC, TAB, WEB, FXH = ROOT / "data" / "processed", ROOT / "output" / "tables", ROOT / "data" / "raw" / "web", ROOT / "data" / "raw" / "fx_hist"
PLAYS = [("ChatGPT", "chatgpt", "chatgpt_go"), ("Claude", "claude", "claude_pro")]          # Play app, key of the results, App Store plan
BAND = 0.05
R, ROWS = {}, []


def read(path, **kw):
    return pd.read_csv(path, keep_default_na=False, na_values=[""], **kw)


def py(v):
    return v.item() if isinstance(v, np.generic) else v


def put(stat, description, note="", **cells):
    """Add the W15 row `stat` and the xch_* keys.  cells: column (value, se, n, numerator, denominator) -> (key suffix, number)."""
    row = dict(statistic=stat, description=description, value=NAN, se=NAN, n=NAN, numerator=NAN, denominator=NAN, note=note)
    keys = []
    for col, (suffix, x) in cells.items():
        x = py(x)
        row[col] = x
        if x is not None and x == x:
            R[f"xch_{suffix}"] = x
            keys.append(f"{col}={'xch_' + suffix}")
    row["keys"] = ";".join(keys)
    ROWS.append(row)


panel = read(PROC / "country_panel.csv")[["iso2", "country_wb", "income_group", "gni_atlas"]].copy()
panel["sf"] = panel.iso2.str.lower()
GNI, NAME, GROUP = dict(zip(panel.sf, panel.gni_atlas)), dict(zip(panel.sf, panel.country_wb)), dict(zip(panel.sf, panel.income_group))
pvd = read(PROC / "wave2_plan_vs_default.csv")
APP = {plan: g.set_index("storefront") for plan, g in pvd.groupby("plan")}                # App Store rows by plan and storefront
STOREFRONTS = set(pvd.storefront)                                                          # storefronts with an App Store listing in wave 2
fxj = json.load(open(FXH / "usd_2026-10-15.json"))
assert fxj["date"] == "2026-10-15"
FX = fxj["usd"]

# ================================================================================================ (a) Microsoft web store
ms = read(WEB / "ms365_web_prices.csv")
m = ms[ms.period == "monthly"]
assert (m.groupby(["iso2", "product"]).price.nunique() == 1).all() and (m.groupby(["iso2", "product"]).currency.nunique() == 1).all(), \
    "a country has two different monthly prices or currencies for one product"
MS = collections.defaultdict(dict)
for r in m.itertuples():
    MS[r.iso2.lower()][r.product] = (float(r.price), r.currency)
PERS, PREM = "Microsoft 365 Personal", "Microsoft 365 Premium"
us_ratio = MS["us"][PERS][0] / MS["us"][PREM][0]
sample = [c for c in sorted(MS) if c != "us" and PERS in MS[c] and PREM in MS[c] and GNI.get(c, NAN) > 0]
y = np.array([math.log(MS[c][PERS][0] / MS[c][PREM][0]) - math.log(us_ratio) for c in sample])
b, se, n = ols_hc1(np.log([GNI[c] for c in sample]), y)
grp = np.array([GROUP[c] for c in sample])
lm, hi = y[np.isin(grp, LMIC)], y[grp == "High income"]
pct = lambda v: float(100 * (math.exp(float(np.median(v))) - 1))
put("ms_slope", "Microsoft web store: income slope of ln(Personal / Premium) relative to the US ratio", value=("ms_slope", b), se=("ms_slope_se", se),
    n=("ms_slope_n", n))
put("ms_lmic", "Microsoft web store: median Personal / Premium relative to the US ratio in low and lower-middle income countries, percent",
    value=("ms_lmic_pct", pct(lm)), n=("ms_lmic_n", len(lm)), note=" ".join(sorted(np.array(sample)[np.isin(grp, LMIC)])))
put("ms_hic", "The same in high-income countries, percent", value=("ms_hic_pct", pct(hi)), n=("ms_hic_n", len(hi)))
put("ms_countries", "Countries with Microsoft 365 web prices; with Personal and Premium (US included); locale pages",
    n=("ms_countries", ms.iso2.nunique()), numerator=("ms_both", sum(1 for c in MS if PERS in MS[c] and PREM in MS[c])),
    denominator=("ms_locales", ms.locale.nunique()))
for key, plan, product in [("premium", "m365_premium", PREM), ("personal", "m365_personal", PERS)]:
    ld = np.array([math.log(MS[c][product][0] / APP[plan].price_local[c]) for c in sample
                   if c in APP[plan].index and APP[plan].currency[c] == MS[c][product][1]])
    base = f"ms_web_vs_app_{key}"
    put(f"{base}_median", f"Microsoft web vs App Store, {product}, same currency: median ln(web / App Store)", value=(f"{base}_median", float(np.median(ld))),
        n=(f"{base}_n", len(ld)))
    put(f"{base}_within5", f"The same: share within 5%", value=(f"{base}_within5", float((np.abs(ld) <= BAND).mean())),
        numerator=(f"{base}_within5_n", int((np.abs(ld) <= BAND).sum())), denominator=(f"{base}_n", len(ld)),
        note="not comparable (currency differs or no storefront): " + " ".join(c for c in sample if not (
            c in APP[plan].index and APP[plan].currency[c] == MS[c][product][1])))
    comparable = [c for c in sample if c in APP[plan].index and APP[plan].currency[c] == MS[c][product][1]]
    same_cent = [c for c in comparable if abs(MS[c][product][0] - float(APP[plan].price_local[c])) < 0.005]
    put(f"{base}_exact", "The same: share identical to the cent (|web - App Store| < 0.005 in the storefront's currency)",
        value=(f"{base}_exact", len(same_cent) / len(ld)), numerator=(f"{base}_exact_n", len(same_cent)), denominator=(f"{base}_n", len(ld)),
        note="not identical: " + " ".join(c for c in comparable if c not in same_cent))
    widest = comparable[int(np.argmax(np.abs(ld)))]
    put(f"{base}_within05", "The same: share within 0.5% (|ln difference| < 0.005)",
        value=(f"{base}_within05", float((np.abs(ld) < 0.005).mean())), numerator=(f"{base}_within05_n", int((np.abs(ld) < 0.005).sum())),
        denominator=(f"{base}_n", len(ld)))
    put(f"{base}_maxgap", "The same: widest gap between the two channels, percent of the App Store price (note: the country)",
        value=(f"{base}_maxgap_pct", float(100 * (math.exp(float(np.max(np.abs(ld)))) - 1))), note=widest)

# ================================================================================================ (b) Google Play lowest in-app item
play = read(WEB / "play_iap_ranges.csv")
play["sf"] = play.country.str.lower()
detail = []
for app, key, plan in PLAYS:
    p = play[(play.app == app) & play["min"].notna()].set_index("sf", drop=False)
    us_min = float(p.loc["us", "min"])
    us_app = float(APP[plan].us_price.iloc[0])
    assert abs(us_min - us_app) < 1e-9, f"{app}: the US Play minimum {us_min} is not the App Store price {us_app} of {plan}"
    recs = []
    for c, r in p.iterrows():
        cur = r.currency_jsonld
        usd = float(r["min"]) / FX[cur.lower()]
        a = APP[plan].loc[c] if c in APP[plan].index else None              # the US is not a row of the plan file: its price is us_app
        price, a_cur = (us_app, "USD") if c == "us" else (float(a.price_local), a.currency) if a is not None else (NAN, "")
        same = a_cur == cur
        cmp_ = same and c != "us"                                            # the US is the anchor of the identification, not a comparison
        recs.append(dict(app=app, country=c, country_name=NAME[c], income_group=GROUP[c], gni_atlas=GNI[c], currency=cur,
                         play_min=float(r["min"]), play_max=float(r["max"]), usd_at_fx=usd, usd_ratio_to_us=usd / us_min, app_store_plan=plan,
                         app_store_price=price, app_store_currency=a_cur, same_currency=bool(same), compared=bool(cmp_),
                         log_diff=math.log(float(r["min"]) / price) if cmp_ else NAN, app_store_storefront=c in STOREFRONTS or c == "us",
                         lmic=GROUP[c] in LMIC))
    t = pd.DataFrame(recs)
    t["lmic_in_median"] = t.lmic & t.app_store_storefront
    t = t.sort_values(["gni_atlas", "country"], ascending=[False, True], kind="stable").reset_index(drop=True)      # richest first; the US is first
    detail.append(t)
    comp = t.log_diff.dropna().values
    in5 = int((np.abs(comp) <= BAND).sum())
    lmv, lma = t[t.lmic_in_median].usd_ratio_to_us.values, t[t.lmic].usd_ratio_to_us.values
    base = f"play_{key}"
    put(f"{base}_n", f"Google Play, {app}: countries with an in-app price range (US included); with an App Store price in the same currency",
        n=(f"{base}_n", len(t)), numerator=(f"{base}_same_currency", len(comp)),
        note="no comparison: " + " ".join(sorted(t[~t.same_currency].country)))
    put(f"{base}_median", f"Google Play, {app}: median ln(Play minimum / App Store price of {plan}), same currency",
        value=(f"{base}_median", float(np.median(comp))), n=(f"{base}_same_currency", len(comp)))
    put(f"{base}_within5", "The same: share within 5%", value=(f"{base}_within5", in5 / len(comp)),
        numerator=(f"{base}_within5_n", in5), denominator=(f"{base}_same_currency", len(comp)))
    put(f"{base}_exact", "The same: share identical (|ln difference| < 0.005)", value=(f"{base}_exact", float((np.abs(comp) < 0.005).mean())),
        numerator=(f"{base}_exact_n", int((np.abs(comp) < 0.005).sum())), denominator=(f"{base}_same_currency", len(comp)))
    put(f"{base}_lmic_ratio", f"Google Play, {app}: median minimum in US$ relative to the US minimum, LMIC countries with an App Store storefront",
        value=(f"{base}_lmic_ratio", float(np.median(lmv))), n=(f"{base}_lmic_n", len(lmv)), note=" ".join(sorted(t[t.lmic_in_median].country)))
    put(f"{base}_lmic_ratio_wb", f"The same over all World Bank LMIC countries of the Play sample (adds countries without an App Store storefront)",
        value=(f"{base}_lmic_ratio_wb", float(np.median(lma))), n=(f"{base}_lmic_n_wb", len(lma)), note=" ".join(sorted(t[t.lmic].country)))
gem = play[play.app == "Gemini"]
put("play_gemini", "Google Play, Gemini: countries with an in-app price range (of the countries in the Play sample)",
    n=("play_gemini_with_range", int(gem["min"].notna().sum())), denominator=("play_gemini_n", len(gem)))
put("play_sample", "Google Play: apps and countries collected", n=("play_countries", play.country.nunique()), denominator=("play_apps", play.app.nunique()))

# ================================================================================================ output
cols = ["statistic", "description", "value", "se", "n", "numerator", "denominator", "note", "keys"]
pd.DataFrame(ROWS, columns=cols).round(10).to_csv(TAB / "W15_cross_channel.csv", index=False)
pd.concat(detail, ignore_index=True).round(10).to_csv(TAB / "W15b_play_countries.csv", index=False)

res = json.load(open(ROOT / "output" / "results_wave2.json"))
for k in [k for k in res if k.startswith("xch_") and k not in R]:
    del res[k]                                                             # stale keys of an earlier version
res.update({k: (round(v, 6) if isinstance(v, float) else v) for k, v in R.items()})
json.dump(res, open(ROOT / "output" / "results_wave2.json", "w"), indent=1)

print(f"Microsoft web: Personal/Premium relative to the US, slope on ln GNI {b:.4f} ({se:.4f}), N = {n}; LMIC median {pct(lm):.1f}% (n = {len(lm)}: "
      f"{', '.join(np.array(sample)[np.isin(grp, LMIC)])}); high-income median {pct(hi):.1f}% (n = {len(hi)})")
for key in ("premium", "personal"):
    print(f"  web vs App Store, {key}: {R[f'xch_ms_web_vs_app_{key}_n']} comparisons, median {R[f'xch_ms_web_vs_app_{key}_median']:.3f}, "
          f"within 5%: {R[f'xch_ms_web_vs_app_{key}_within5']:.2f}")
for app, key, plan in PLAYS:
    print(f"Google Play {app}: {R[f'xch_play_{key}_n']} countries, {R[f'xch_play_{key}_same_currency']} same-currency comparisons with {plan}, median "
          f"{R[f'xch_play_{key}_median']:.3f}, within 5%: {R[f'xch_play_{key}_within5']:.2f} ({R[f'xch_play_{key}_within5_n']}); LMIC median ratio to the US "
          f"{R[f'xch_play_{key}_lmic_ratio']:.2f} (n = {R[f'xch_play_{key}_lmic_n']}), with Bangladesh {R[f'xch_play_{key}_lmic_ratio_wb']:.2f} "
          f"(n = {R[f'xch_play_{key}_lmic_n_wb']})")
