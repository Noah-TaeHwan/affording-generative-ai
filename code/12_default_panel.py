"""
12_default_panel.py   (no network; run after 09b_wave2_items.py)
Apple's default price schedule, revealed by a panel of small-developer subscription apps, and the deviation of AI and benchmark
plans from it.

Idea.  An app that sets only a US price tier is converted by Apple to every other storefront's currency using Apple's own
schedule (exchange rate, local taxes, rounding to the local price points).  The 30 apps of the default panel (small
developers without a pricing team; 02b_scrape_wave2.py, run "default") have no reason to price individual countries, so the
local price that the majority of them show at a given US price is taken to be the schedule itself.  A plan whose local
price differs from that schedule is read as having been priced actively.

Inputs   data/processed/wave2_default_items_long.csv, wave2_plan_rows.csv, wave2_items_long.csv (09b_wave2_items.py), country_panel.csv
         data/raw/appstore_wave2/fx/er_api_usd_20261016.json
Outputs  data/processed/wave2_default_ladder.csv      storefront x US price point: modal local price over the panel items
         data/processed/wave2_default_multiplier.csv  storefront multiplier (local currency per US$ of base price)
         data/processed/wave2_plan_vs_default.csv     plan x storefront: local price, reference from the schedule, deviation
         output/tables/W4_default_schedule.csv        per plan: deviation statistics (first row: the schedule itself)
         output/tables/W1_wave2_plans.csv             the matched-sample columns, the exact/extrapolated split and the robustness
                                                      columns are added to the file written by 09b
         output/tables/W13_tax_absorption.csv         plans in the US$-priced storefronts whose default embeds a tax
         output/results_wave2.json                    the default-panel and per-plan scalars are added, with the first-pass
                                                      numbers (tie -> price listed first) under the suffix _fileorder and the
                                                      tie-rule sensitivity under default_tie_<rule>_*
         data/processed/wave2_data_dictionary.csv     the descriptions of the files above are added

Definitions (those of the stdlib script analyze_default.py that produced the first pass of the results, not part of this package;
the order of the rows in wave2_default_items_long.csv is the order of the raw file):
  * Price point = US monthly price of the same app and item name, rounded to cents.  Ladder entry (storefront, price point) =
    the modal local price (rounded to cents) over the panel items at that point, if there are >= 3 such items, the mode is
    UNIQUE and its share is >= 0.5.  Of the 2,414 entries of 16 Oct 2026, 1,551 have such a price.  Of the other 863, 841 have a
    most frequent price below one half and 22 split 50/50 between two prices (a tie; neither price is taken).  `tie` flags every entry in which several prices are equally frequent (546: those 22 and 524 below one half).
    Entries without a price have no exact point: plans there are compared with multiplier x US price, and they do not enter
    the multiplier.
    The first pass resolved a 50/50 tie in favour of the price listed first in the raw file (the order of the rows in
    wave2_default_items_long.csv is that of the raw file).  results_wave2.json gives the first-pass numbers under the suffix
    _fileorder, and the headline numbers under five rules as default_tie_<rule>_*: fileorder (as above), low and high (the 50/50
    tie goes to the lower or higher price), none (the rule of this package: 50/50 ties dropped) and strict (a price needs a
    strict majority, share > 0.5, which also drops the 320 untied entries with a most frequent price at exactly one half).
  * Multiplier = median over price points >= US$2.99 with a mode of (modal local price / US price); needs >= 3 points;
    spread = (max - min) / median of those ratios; "clean" storefronts have spread < 0.2.  tax_factor = multiplier / fx, the
    US$ value of US$1 of base price after Apple's conversion, local taxes and rounding (fx = currency units per US$,
    open.er-api.com, 16 Oct 2026).  Income slope of the schedule = HC1 OLS slope of ln(tax_factor) on ln(GNI per capita).
  * Reference for a plan in a storefront (not the US) = the exact ladder entry for the plan's US price if there is one, else
    multiplier x US price.  Deviation = ln(local price / reference); 0.03 = the plan is 3% above the schedule.
  * Per plan: HC1 slope of the deviation on ln(GNI), share within +-3% (|dev| <= 0.03), share more than 10% below the schedule
    (dev < -0.10), median deviation in low- and lower-middle-income storefronts ("LMIC") and its percent equivalent
    100 (e^dev - 1); the same on the clean subsample; HC1 slope of ln(ratio to US) on ln(GNI) at both FX sources, on the same
    storefronts.  Plans with fewer than 30 storefronts are not reported.  W4 also gives, per plan, the number of LMIC storefronts
    and the share of them with dev < -0.10 (lmic_n, lmic_share_below10; lmic_share_ratio_lt090: local price below 90% of the
    reference), the number of high-income storefronts (hic_n) and the number of storefronts at the reference (|dev| <= 0.005,
    at_default_n).  results_wave2.json quotes them for ChatGPT Go and Plus (go_lmic_share_below10, go_hic_median_dev,
    plus_hic_median_dev, go_exact_default_n).
  * Exact versus extrapolated reference.  The reference of a plan in a storefront is exact if the storefront's ladder has an
    entry for the plan's US price and extrapolated (multiplier x US price) otherwise.  Per plan: the numbers of storefronts with
    each kind of reference (n_exact, n_extrap) and the share within +-3% of the reference in each (within3_exact,
    within3_extrap).
  * Robustness of the deviation slope: (i) storefronts not priced in US$ only (dev_slope_nonusd, dev_se_nonusd, dev_n_nonusd);
    (ii) weighted least squares with the population aged 15-64 as weights, HC1 (dev_slope_popw, dev_se_popw); (iii) HC3
    standard error of the main regression (dev_se_hc3).  All are written for every plan to W1_wave2_plans.csv and, as
    <plan>_<column>, to results_wave2.json.
  * Tax absorption (W13_tax_absorption.csv).  US$-priced storefronts whose schedule embeds a tax, tax_factor > 1.05 (16;
    n_lmic / at_us_lmic: the same counts in the low- and lower-middle-income storefronts among them; round_*: the number of
    those storefronts, and of the dollar storefronts whose tax factor is one, in which Claude Pro and Perplexity Pro, two
    $20.00 plans of different vendors, are listed at the same price, at $25.00, $22.00 or $20.00
    storefronts): for seven plans, the number of those storefronts in which the plan is listed at the U.S. price (|price in US$ /
    U.S. price - 1| < 0.006) and the number in which it is within +-3% of the reference.  Keys taxabs_*.
  * Consistency of the guard: 09b_wave2_items.py computes the multiplier of its annual-as-monthly guard with the same function
    (wave2_common.schedule); this script asserts that guard_ref in wave2_items_long.csv equals multiplier x U.S. price.
"""
import json, math, pathlib
import numpy as np
import pandas as pd
from wave2_common import LMIC, NAN, MAIN, RULES, ols_hc1, ols_hc3, wls_hc1, panel_points, schedule      # shared with 09b_wave2_items.py

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW2 = ROOT / "data" / "raw" / "appstore_wave2"
PROC, TAB = ROOT / "data" / "processed", ROOT / "output" / "tables"
RATES = json.load(open(RAW2 / "fx" / "er_api_usd_20261016.json"))["rates"]
panel = pd.read_csv(PROC / "country_panel.csv", keep_default_na=False, na_values=[""])[["iso2", "gni_atlas", "income_group", "pop1564"]].copy()
panel["sf"] = panel.iso2.str.lower()
GNI, GRP, POP = dict(zip(panel.sf, panel.gni_atlas)), dict(zip(panel.sf, panel.income_group)), dict(zip(panel.sf, panel.pop1564))
R = {}

# the tie rules (MAIN, RULES) and the construction of the ladder and the multipliers (modal, schedule) are in wave2_common.py
SENSITIVITY = ["fileorder", "low", "high", "none", "strict"]       # order of the default_tie_* keys


def pct(x):
    return float(100 * (math.exp(x) - 1)) if x == x else NAN


def analyse(rule):
    """Schedule under `rule`, the plans against it and all statistics (nothing is written)."""
    lad, mult = schedule(d, rule)
    ladder = pd.DataFrame([dict(storefront=sf, us_price=p, **e) for (sf, p), e in lad.items()])
    mrows = []
    for sf, (m, k, spread) in mult.items():
        fx = RATES.get(cur.get(sf))
        mrows.append(dict(storefront=sf, currency=cur.get(sf), multiplier=m, n_points=k, spread=spread, fx=(fx if fx else NAN),
                          tax_factor=(m / fx if fx else NAN), gni=GNI.get(sf, NAN), income_group=GRP.get(sf)))
    mdf = pd.DataFrame(mrows)
    ok = mdf[mdf.tax_factor.notna() & mdf.gni.notna() & (mdf.gni > 0)]
    b0, s0, n0 = ols_hc1(np.log(ok.gni), np.log(ok.tax_factor))

    pr = PLAN_ROWS.copy()
    ref, exact = [], []
    for r in pr.itertuples():
        e = lad.get((r.storefront, round(r.us_price, 2)))
        ex = e["modal_local"] if e else None
        if ex:
            ref.append(ex)
            exact.append(True)
        elif r.storefront in mult:
            ref.append(mult[r.storefront][0] * r.us_price)
            exact.append(False)
        else:
            ref.append(NAN)
            exact.append(False)
    pr["default_ref"], pr["default_exact"] = ref, exact
    pr["dev_log"] = np.log(pr.price_local / pr.default_ref)
    clean_sf = {sf for sf, v in mult.items() if v[2] < 0.2}
    pr["clean_schedule"] = pr.storefront.isin(clean_sf)

    w4 = [dict(plan="default_schedule", label="Apple default schedule (tax factor)", n=n0, usd_slope=b0, usd_se=s0)]
    stats, extra = {}, {}
    for plan in w1.plan:
        c = pr[(pr.plan == plan) & pr.dev_log.notna() & pr.gni.notna()]
        if len(c) < 30:
            continue
        b, se, n = ols_hc1(np.log(c.gni), c.dev_log)
        cu = c[c.ratio_us.notna() & c.ratio_us_alt_fx.notna()]             # USD slopes on the same storefronts (all have a rate)
        bu, seu, _ = ols_hc1(np.log(cu.gni), np.log(cu.ratio_us))
        ba, sea, _ = ols_hc1(np.log(cu.gni), np.log(cu.ratio_us_alt_fx))
        cl = c[c.clean_schedule]
        bc, sec, nc = ols_hc1(np.log(cl.gni), cl.dev_log)
        lm, lic, hic = c[c.income_group.isin(LMIC)].dev_log, c[c.income_group == "Low income"].dev_log, c[c.income_group == "High income"].dev_log
        clm = cl[cl.income_group.isin(LMIC)].dev_log
        s = dict(plan=plan, label=label[plan], n=n, n_exact=int(c.default_exact.sum()), dev_slope=b, dev_se=se,
                 within3=float((c.dev_log.abs() <= 0.03).mean()), below10=float((c.dev_log < -0.10).mean()),
                 med_lmic_dev=float(lm.median()) if len(lm) else NAN, med_lmic_pct=pct(float(lm.median())) if len(lm) else NAN,
                 med_lic_dev=float(lic.median()) if len(lic) else NAN, med_hic_dev=float(hic.median()) if len(hic) else NAN,
                 usd_slope=bu, usd_se=seu, usd_slope_altfx=ba, usd_se_altfx=sea,
                 clean_n=nc, clean_dev_slope=bc, clean_dev_se=sec, clean_within3=float((cl.dev_log.abs() <= 0.03).mean()),
                 clean_below10=float((cl.dev_log < -0.10).mean()),
                 clean_med_lmic_dev=float(clm.median()) if len(clm) else NAN,
                 lmic_n=int(len(lm)), lmic_share_below10=float((lm < -0.10).mean()) if len(lm) else NAN,
                 lmic_share_ratio_lt090=float((lm < math.log(0.9)).mean()) if len(lm) else NAN,
                 hic_n=int(len(hic)), at_default_n=int((c.dev_log.abs() <= 0.005).sum()))
        stats[plan] = s
        w4.append(s)
        # exact versus extrapolated reference; robustness of the deviation slope (not in W4)
        ce, cx = c[c.default_exact], c[~c.default_exact]
        nu = c[c.currency != "USD"]                                        # storefronts not priced in US$
        bn, sen, nn = ols_hc1(np.log(nu.gni), nu.dev_log)
        pop = c.storefront.map(POP)
        assert pop.notna().all(), "storefront without population aged 15-64"
        bw, sew, _ = wls_hc1(np.log(c.gni), c.dev_log, pop)
        extra[plan] = dict(n_exact=int(len(ce)), n_extrap=int(len(cx)),
                           within3_exact=float((ce.dev_log.abs() <= 0.03).mean()) if len(ce) else NAN,
                           within3_extrap=float((cx.dev_log.abs() <= 0.03).mean()) if len(cx) else NAN,
                           above3=float((c.dev_log > 0.03).mean()), above10=float((c.dev_log > 0.10).mean()),   # storefront-specific prices above the schedule
                           dev_slope_nonusd=bn, dev_se_nonusd=sen, dev_n_nonusd=nn, dev_slope_popw=bw, dev_se_popw=sew,
                           dev_se_hc3=ols_hc3(np.log(c.gni), c.dev_log)[1])
    return dict(rule=rule, lad=lad, mult=mult, ladder=ladder, mdf=mdf, b0=b0, s0=s0, n0=n0, pr=pr, stats=stats, extra=extra, w4=w4)


STAT_KEYS = ["n", "usd_slope", "usd_se", "usd_slope_altfx", "dev_slope", "dev_se", "within3", "below10", "med_lmic_dev",
             "med_lmic_pct", "med_lic_dev", "med_hic_dev", "clean_n", "clean_dev_slope", "clean_within3"]
# the plans quoted in the text and the benchmark items
QUOTED = ["chatgpt_go", "chatgpt_plus", "chatgpt_pro100", "chatgpt_pro200", "claude_pro", "claude_max5x", "claude_max20x",
          "gemini_pro", "gemini_ultra", "perplexity_pro", "supergrok", "supergrok_lite", "m365_personal", "m365_premium",
          "youtube_premium", "chatgpt_pro500", "supergrok_heavy", "youtubemusic_music", "x_premium", "x_premium_basic",
          "x_premium_plus", "characterai_lite", "characterai_plus", "gemini_plus", "youtube_premium_lite", "m365_family",
          "googleone_aiplus2tb", "gemini_100gb", "x_creator", "supergrok_plus", "m365_basic", "youtube_premium_family",
          "youtubemusic_family"]
# columns added to W1 and written for every plan as <plan>_<column> to results_wave2.json (a missing value is not written)
EXTRA_KEYS = ["n_exact", "n_extrap", "within3_exact", "within3_extrap", "above3", "above10", "dev_slope_nonusd", "dev_se_nonusd", "dev_n_nonusd",
              "dev_slope_popw", "dev_se_popw", "dev_se_hc3"]
EXTRA_INT = ("n_exact", "n_extrap", "dev_n_nonusd")
# plans of the tax-absorption test (W13)
TAX_PLANS = ["chatgpt_plus", "gemini_pro", "gemini_ultra", "m365_premium", "claude_pro", "perplexity_pro", "supergrok"]


# plans and statistics of the first-pass report, kept under the suffix _fileorder (with the default_* and the Go/Plus keys)
FIRST_PASS = {f"{p}_{k}" for p in ["chatgpt_go", "chatgpt_plus", "chatgpt_pro200", "claude_pro", "claude_max20x", "gemini_pro",
                                   "gemini_ultra", "perplexity_pro", "supergrok", "m365_personal", "m365_premium", "youtube_premium"]
              for k in ["n", "dev_slope", "dev_se", "within3", "below10", "med_lmic_dev", "med_lmic_pct", "clean_n", "clean_dev_slope",
                        "clean_within3"]}


def scalars(a, suffix=""):
    """The scalars of results_wave2.json that depend on the tie rule; `suffix` is appended to every key.  With a suffix only
    the first-pass keys are returned (FIRST_PASS, default_*, go_*, plus_*)."""
    L, M, st = a["ladder"], a["mdf"], a["stats"]
    out = {"default_ladder_entries": int(len(L)), "default_ladder_points": int(L.modal_local.notna().sum()),
           "default_ladder_tied_points": int((L.tie & (L.modal_share == 0.5)).sum()),      # two prices at one half each
           "default_ladder_half_points": int((L.modal_share == 0.5).sum()),                # modal share exactly one half
           "default_multiplier_storefronts": int(len(M)),
           "default_clean_storefronts": int((M.spread < 0.2).sum()), "default_slope": a["b0"], "default_slope_se": a["s0"],
           "default_slope_n": a["n0"], "default_spread_median": float(M.spread.median())}
    for plan in QUOTED:
        for k in STAT_KEYS:
            out[f"{plan}_{k}"] = int(st[plan][k]) if k in ("n", "clean_n") else float(st[plan][k])
    go, plus = st["chatgpt_go"], st["chatgpt_plus"]
    out.update(go_lmic_n=go["lmic_n"], go_lmic_share_below10=go["lmic_share_below10"],      # below10: ln(local / default) < -0.10
               go_lmic_share_ratio_lt090=go["lmic_share_ratio_lt090"],                       # local price below 90% of the default
               go_hic_median_dev=go["med_hic_dev"], plus_hic_median_dev=plus["med_hic_dev"],
               go_exact_default_n=go["at_default_n"], go_exact_default_share=go["at_default_n"] / go["n"])   # |dev| <= 0.005
    if suffix:
        out = {k: v for k, v in out.items() if k in FIRST_PASS or k.startswith(("default_", "go_", "plus_"))}
    return {k + suffix: v for k, v in out.items()}


def extra_scalars(a):
    """<plan>_<column> for the EXTRA_KEYS of every plan (exact/extrapolated split and robustness of the deviation slope)."""
    return {f"{plan}_{k}": (int(x[k]) if k in EXTRA_INT else float(x[k])) for plan, x in a["extra"].items()
            for k in EXTRA_KEYS if x[k] == x[k]}


# ================================================================================================ the schedule
items = pd.read_csv(PROC / "wave2_default_items_long.csv", keep_default_na=False, na_values=[""])
cur = {}
for sf, c in zip(items.storefront, items.currency):
    if isinstance(c, str):
        cur[sf] = c                                           # a storefront has one currency (checked below)
assert all(g.currency.nunique() == 1 for _, g in items.groupby("storefront")), "storefront with several currencies"
d = panel_points(items)
PLAN_ROWS = pd.read_csv(PROC / "wave2_plan_rows.csv", keep_default_na=False, na_values=[""])
PLAN_ROWS = PLAN_ROWS[(PLAN_ROWS.storefront != "us") & PLAN_ROWS.us_price.notna()].copy()
w1 = pd.read_csv(TAB / "W1_wave2_plans.csv", keep_default_na=False, na_values=[""])
label = dict(zip(w1.plan, w1.label))

A = {rule: analyse(rule) for rule in RULES}
main = A[MAIN]
lad, mult, ladder, mdf, pr = main["lad"], main["mult"], main["ladder"], main["mdf"], main["pr"]
b0, s0, n0, stats = main["b0"], main["s0"], main["n0"], main["stats"]
ladder.to_csv(PROC / "wave2_default_ladder.csv", index=False)
mdf.to_csv(PROC / "wave2_default_multiplier.csv", index=False)
pr.to_csv(PROC / "wave2_plan_vs_default.csv", index=False)
pd.DataFrame(main["w4"]).to_csv(TAB / "W4_default_schedule.csv", index=False)

# the annual-as-monthly guard of 09b_wave2_items.py uses this schedule's multipliers (same function, wave2_common.schedule)
gi = pd.read_csv(PROC / "wave2_items_long.csv", usecols=["storefront", "us_price", "guard_ref"], keep_default_na=False, na_values=[""])
has_ref = gi.storefront.isin(mdf.storefront) & gi.us_price.notna()
assert (has_ref == gi.guard_ref.notna()).all(), "guard_ref missing or present where the schedule has no multiplier"
assert np.allclose(gi.guard_ref[has_ref], (gi.storefront.map(mdf.set_index("storefront").multiplier) * gi.us_price)[has_ref],
                   rtol=1e-12, atol=0), "guard_ref differs from multiplier x U.S. price"

# W1: the unconditional columns from 09b plus the matched-sample columns
MATCHED = ["n", "usd_slope", "usd_se", "usd_slope_altfx", "dev_slope", "dev_se", "within3", "below10", "med_lmic_dev",
           "med_lmic_pct", "clean_n", "clean_dev_slope", "clean_within3"]
w1 = w1[[c for c in w1.columns if c not in MATCHED + EXTRA_KEYS]]
w1 = w1[w1.plan.isin(stats)]                                  # plans without storefront rows (googleone_100gb, discord_nitro) drop out
w1 = w1.merge(pd.DataFrame(stats.values())[["plan"] + MATCHED], on="plan", how="left")
w1 = w1.merge(pd.DataFrame([dict(plan=p, **x) for p, x in main["extra"].items()])[["plan"] + EXTRA_KEYS], on="plan", how="left")
w1.to_csv(TAB / "W1_wave2_plans.csv", index=False)

# W13: tax absorption in the US$-priced storefronts whose default schedule embeds a tax
tax_sf = sorted(mdf[(mdf.currency == "USD") & (mdf.tax_factor > 1.05)].storefront)
tax_lmic = [sf for sf in tax_sf if GRP.get(sf) in LMIC]                   # the low- and lower-middle-income storefronts among them
w13 = []
for plan in TAX_PLANS:
    t = pr[(pr.plan == plan) & pr.storefront.isin(tax_sf) & pr.price_usd.notna()]
    tl = t[t.storefront.isin(tax_lmic)]
    at_us = (t.price_usd / t.us_price - 1).abs() < 0.006
    w13.append(dict(plan=plan, label=label[plan], us_price=float(t.us_price.iloc[0]), n=int(len(t)), at_us=int(at_us.sum()),
                    at_default=int((t.dev_log.notna() & (t.dev_log.abs() <= 0.03)).sum()),
                    n_lmic=int(len(tl)), at_us_lmic=int(((tl.price_usd / tl.us_price - 1).abs() < 0.006).sum())))
pd.DataFrame(w13).to_csv(TAB / "W13_tax_absorption.csv", index=False)
# round-number listings that different vendors share in dollar storefronts (platform rounding rather than vendor pricing?):
# the two $20.00 tiers (Claude Pro, Perplexity Pro) listed at the same price in a storefront, in the taxed dollar storefronts and in
# the dollar storefronts whose panel tax factor is one
p20 = pr[pr.plan.isin(["claude_pro", "perplexity_pro"]) & pr.price_usd.notna()].pivot(index="storefront", columns="plan", values="price_usd").dropna()
same20 = p20[(p20.claude_pro - p20.perplexity_pro).abs() < 0.006]
usd_tf1 = set(mdf[(mdf.currency == "USD") & ((mdf.tax_factor - 1).abs() < 0.005)].storefront)
same20_tax = same20[same20.index.isin(tax_sf)]
same20_tf1 = same20[same20.index.isin(usd_tf1)]
ROUND = dict(round_usd16_n=len(tax_sf), round_usd16_both_n=int(len(same20_tax)),
             round_usd16_both25_n=int((same20_tax.claude_pro.round(2) == 25.00).sum()),
             round_tf1_usd_n=len(usd_tf1), round_tf1_both_n=int(len(same20_tf1)),
             round_tf1_both22_n=int((same20_tf1.claude_pro.round(2) == 22.00).sum()),
             round_tf1_both20_n=int((same20_tf1.claude_pro.round(2) == 20.00).sum()))

# ================================================================================================ results_wave2.json
R.update(scalars(main))
R.update(extra_scalars(main))
R["taxabs_n_storefronts"], R["taxabs_n_lmic_storefronts"] = len(tax_sf), len(tax_lmic)
for r in w13:
    for k in ("n", "at_us", "at_default", "n_lmic", "at_us_lmic"):
        R[f"taxabs_{r['plan']}_{k}"] = r[k]
R.update(ROUND)
R.update(scalars(A["fileorder"], "_fileorder"))               # the numbers of the first pass (tie -> price listed first)
for rule in SENSITIVITY:                                      # sensitivity of the headline numbers to the tie rule
    a = A[rule]
    R[f"default_tie_{rule}_ladder_points"] = int(a["ladder"].modal_local.notna().sum())
    R[f"default_tie_{rule}_multiplier_storefronts"] = int(len(a["mdf"]))
    R[f"default_tie_{rule}_clean_storefronts"] = int((a["mdf"].spread < 0.2).sum())
    R[f"default_tie_{rule}_slope"], R[f"default_tie_{rule}_slope_n"] = a["b0"], a["n0"]
    for plan, short in [("chatgpt_go", "go"), ("chatgpt_plus", "plus")]:
        for k in ("dev_slope", "within3", "below10", "med_lmic_dev"):
            R[f"default_tie_{rule}_{short}_{k}"] = float(a["stats"][plan][k])

res = json.load(open(ROOT / "output" / "results_wave2.json"))
res.update({k: (round(v, 6) if isinstance(v, float) else v) for k, v in R.items()})
json.dump(res, open(ROOT / "output" / "results_wave2.json", "w"), indent=1)


# ================================================================================================ data dictionary
def rows(file, frame, desc, source):
    return [dict(file=file, variable=c, description=desc[c], source=source.get(c, "derived"), non_missing=int(frame[c].notna().sum()))
            for c in frame.columns]


APP = "Apple App Store default-panel pages, 16 Oct 2026 (02b_scrape_wave2.py)"
SRC_P = {c: APP for c in ["plan", "storefront", "app", "name", "currency", "price_local", "n_variants", "us_price"]}
SRC_P.update(price_usd="derived; open.er-api.com, 16 Oct 2026", price_usd_alt_fx="derived; fawazahmed0 currency-api, 15 Oct 2026",
             gni="World Bank WDI via country_panel.csv", income_group="World Bank FY2027 via country_panel.csv")
SRC_M = dict(currency=APP, fx="open.er-api.com, 16 Oct 2026", gni=SRC_P["gni"], income_group=SRC_P["income_group"], storefront=APP)
D_LAD = {"storefront": "App Store storefront code", "us_price": "US monthly price point (US$, rounded to cents) of the panel items",
         "n_items": "Panel items (app x item name) at this price point in this storefront",
         "modal_local": "Modal local price (local currency, rounded to cents); empty if the mode is not unique or its share is below 0.5",
         "modal_share": "Share of the n_items at the most frequent local price (0.5 for a tie between two prices)",
         "tie": "True if two or more local prices were equally frequent; such an entry has no unique mode, so modal_local is empty"}
D_MUL = {"storefront": "App Store storefront code", "currency": "Storefront currency",
         "multiplier": "Median over price points >= US$2.99 of modal local price / US price (local currency per US$ of base price)",
         "n_points": "Price points used (>= 3)", "spread": "(max - min) / median of the ratios; clean storefront if < 0.2",
         "fx": "Currency units per US$ (open.er-api.com, 16 Oct 2026)",
         "tax_factor": "multiplier / fx: US$ value of US$1 of base price after Apple's conversion, taxes and rounding",
         "gni": "GNI per capita, Atlas method, current US$", "income_group": "World Bank income group FY2027"}
D_PVD = {"plan": "Plan key", "storefront": "App Store storefront code", "app": "App key", "name": "Item name",
         "currency": "Storefront currency", "price_local": "Modal monthly price, local currency",
         "price_usd": "price_local / units per US$ (open.er-api.com)", "price_usd_alt_fx": "price_local / units per US$ (fawazahmed0)",
         "n_variants": "Prices listed for this name on the page", "us_price": "US price of the same item (US$)",
         "ratio_us": "price_usd / us_price", "ratio_us_alt_fx": "price_usd_alt_fx / us_price", "gni": "GNI per capita, Atlas method, US$",
         "income_group": "World Bank income group FY2027",
         "default_ref": "Local price the Apple default schedule gives for the plan's US price (exact ladder entry, else multiplier x US price)",
         "default_exact": "True if default_ref is an exact ladder entry", "dev_log": "ln(price_local / default_ref)",
         "clean_schedule": "True if the storefront's schedule has spread < 0.2"}
new = (rows("wave2_default_ladder.csv", ladder, D_LAD, {"storefront": APP, "us_price": APP}) +
       rows("wave2_default_multiplier.csv", mdf, D_MUL, SRC_M) + rows("wave2_plan_vs_default.csv", pr, D_PVD, SRC_P))
dpath = PROC / "wave2_data_dictionary.csv"
old = pd.read_csv(dpath, keep_default_na=False, na_values=[""]) if dpath.exists() else pd.DataFrame(columns=["file", "variable", "description", "source", "non_missing"])
mine = {"wave2_default_ladder.csv", "wave2_default_multiplier.csv", "wave2_plan_vs_default.csv"}
pd.concat([old[~old.file.isin(mine)], pd.DataFrame(new)], ignore_index=True).to_csv(dpath, index=False)

print(f"default schedule: {R['default_multiplier_storefronts']} storefronts with a multiplier, {R['default_clean_storefronts']} clean; "
      f"income slope {b0:.4f} (s.e. {s0:.4f}), N = {n0}")
print("tie rule sensitivity (ladder points / clean storefronts / slope / Go deviation slope): "
      + "; ".join(f"{r} {R[f'default_tie_{r}_ladder_points']} / {R[f'default_tie_{r}_clean_storefronts']} / "
                  f"{R[f'default_tie_{r}_slope']:.4f} / {R[f'default_tie_{r}_go_dev_slope']:.4f}" for r in SENSITIVITY))
for plan in ["chatgpt_go", "chatgpt_plus", "gemini_pro", "youtube_premium"]:
    s = stats[plan]
    print(f"{plan}: N {s['n']}, deviation slope {s['dev_slope']:.3f} ({s['dev_se']:.3f}), within 3% {s['within3']:.3f}, "
          f"below 10% {s['below10']:.3f}, median LMIC deviation {s['med_lmic_dev']:.3f} ({s['med_lmic_pct']:.1f}%)")
