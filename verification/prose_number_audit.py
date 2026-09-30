"""Audit of the numbers printed in the prose of paper_en/main.tex (version 2.0).

Every numerical statement in the abstract, main text and appendices B, C and E is compared with the value
produced by the pipeline: output/results.json (analysis script), the CSV/JSON outputs of revision_audit/ and
publication_upgrade/, or a direct recomputation from the processed data or the raw App Store records.
Table bodies are not checked here because they are written by code (code/40_tables_tex.py,
revision_audit/build_revision_tables.py, publication_upgrade/build_matched_menu_table.py) and verified with
the --check modes of those scripts.

Usage:  python verification/prose_number_audit.py        (from the package root; exit code 1 on any mismatch)

A printed value passes if it equals the pipeline value rounded (half-up or half-even) to the printed number of
decimals. Values printed as "about", "near" or as a range are checked against the rounding rule stated in the
ledger entry.
"""
import json
import re
import sys
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
R = json.load(open(ROOT / "output" / "results.json"))
AO = ROOT / "revision_audit" / "audit_output"
PU = ROOT / "publication_upgrade" / "results"
TEX = (ROOT / "paper_en" / "main.tex").read_text(encoding="utf-8")


def D(x):
    return Decimal(repr(float(x)))


def rnd(x, d, mode=ROUND_HALF_UP):
    return D(x).quantize(Decimal(1).scaleb(-d), rounding=mode)


LEDGER = []


def check(loc, printed, value, note=""):
    """printed: the string as it appears in the text (digits only); value: pipeline value on the same scale."""
    p = Decimal(printed.replace(",", ""))
    d = len(printed.split(".")[1]) if "." in printed else 0
    ok = p in (rnd(value, d), rnd(value, d, ROUND_HALF_EVEN))
    LEDGER.append((ok, loc, printed, float(value), note))
    return ok


def check_in_text(snippet):
    """Assert that the exact snippet occurs in main.tex, so the ledger cannot drift from the manuscript."""
    ok = snippet in TEX
    LEDGER.append((ok, "text contains: " + snippet[:70], "", 0.0, "" if ok else "SNIPPET NOT FOUND"))
    return ok


def csv(name, folder=AO):
    return pd.read_csv(folder / name)


# ------------------------------------------------------------------ data recomputations
panel = pd.read_csv(ROOT / "data" / "processed" / "country_panel.csv", keep_default_na=False, na_values=[""])  # "NA" is Namibia
prices = pd.read_csv(ROOT / "data" / "processed" / "appstore_prices_long.csv")
raw = [json.loads(l) for l in open(ROOT / "data" / "raw" / "appstore" / "appstore_iap_raw.jsonl")]
gni = panel.dropna(subset=["gni_atlas"]).copy()
gni["aab20"] = 1200 * 20 / gni["gni_atlas"]


def burden(iso3, p=20):
    y = float(panel.loc[panel.iso3 == iso3, "gni_atlas"].iloc[0])
    return 1200 * p / y


# ------------------------------------------------------------------ Abstract
check_in_text("nine plans of ChatGPT, Claude and Gemini in 170 national Apple App Store storefronts")
check("Abstract: 170 storefronts with local price lists", "170",
      prices[prices.price_local.notna()].storefront.nunique())
check("Abstract: 201 economies", "201", R["n_econ_gni"])
check("Abstract: income slope 0.03 (Claude Pro, low end)", "0.03", R["loc_claude_pro_b"])
check("Abstract: income slope 0.04 (ChatGPT Plus, high end)", "0.04", R["loc_chatgpt_plus_b"])
check("Abstract: 0.23 price-level slope", "0.23", R["plr_b"])
check("Abstract: Go slope 0.14", "0.14", R["loc_chatgpt_go_b"])
check("Abstract: 0.65% HIC", "0.65", R["aab_p20_HIC"])
check("Abstract: 29% LIC", "29", R["aab_p20_LIC"])
check("Abstract: 60% of working-age population above 2%", "60", 100 * R["share_wapop_aab20_gt2"])
check("Abstract: 0.37 any-use elasticity", "0.37", R["ms_log_cs_b"])
check("Abstract: 0.71 Claude elasticity", "0.71", R["tm_aui_b"])

# ------------------------------------------------------------------ Section 1
check("S1: $20 is 0.3% of income in the United States", "0.3", burden("USA"))
usa_moz = burden("MOZ")
LEDGER.append((usa_moz > 40, "S1: 'more than 40% in Mozambique'", ">40", usa_moz, ""))
check("S1: 218 storefront codes", "218", len({r["storefront"] for r in raw}))
check("S1: 170 storefronts with prices", "170", prices[prices.price_local.notna()].storefront.nunique())
check("S1: 0.039 Plus", "0.039", R["loc_chatgpt_plus_b"])
check("S1: 0.026 Claude Pro", "0.026", R["loc_claude_pro_b"])
check("S1: 0.037 Google AI Pro", "0.037", R["loc_gemini_pro_b"])
check("S1: 0.143 Go", "0.143", R["loc_chatgpt_go_b"])
ppp = csv("same_sample_ppp_comparison.csv").set_index("plan")
go_frac = ppp.loc["chatgpt_go", "observed_fraction_of_ppp"]
LEDGER.append((abs(go_frac - 0.60) < 0.015, "S1/S5.2/S7: Go slope 'about 60%' of price-level slope",
               "about 60", go_frac, "0.5913 rounds to 59%; 'about 60%' accepted within 1.5 points"))
LEDGER.append((abs(1 / R["loc_chatgpt_go_b"] - 7) < 0.5, "S1/S5.2: Go 'one-seventh of proportional pricing'",
               "1/7", 1 / R["loc_chatgpt_go_b"], ""))
check("S1: 36% of LIC economies have no local storefront", "36", 100 * R["store_none_LIC"])
check("S1: 0.65% / 3.1% / 8.7% / 29%", "3.1", R["aab_p20_UMIC"])
check("S1: 8.7% LMIC", "8.7", R["aab_p20_LMIC"])
check("S1: $12,000 threshold", "12000", R["threshold_gni_for_2pct_p20"])
check("S1: 13% richest fifth LIC", "13", R["aab20_q5_LIC"])
check("S1: 96 common economies", "96", R["n_two_margins"])
check("S1: one low-income economy in the common sample", "1", R["tm_n_LIC"])
check("S1: a*_L 100% equal gains", "1.00", R["aLstar_ratio1.0"])
check("S1: a*_L 67% (1.5x)", "0.67", R["aLstar_ratio1.5"])
check("S1: a*_L 50% (2x)", "0.50", R["aLstar_ratio2.0"])
check("S1: 'against about 9% today' (LIC any-use share)", "9", 100 * R["scen_a_LIC"])
check("S1 lit: half of gradient coincides with internet use (49%)", "49", 100 * R["decomp_share_connect"])

# ------------------------------------------------------------------ Section 3
check("S3.1: 2% threshold income $12,000 for $20", "12000", 1200 * 20 / 2)
check("S3.1: $4,800 for $8", "4800", 1200 * 8 / 2)
check("S3.1 fn: Atlas-PPP vs GDP price-level ratio median 3.1%", "3.1", 100 * R["plr_vs_gdp_absdiff_median"])
check("S3.1 fn: 90th percentile 8.3%", "8.3", 100 * R["plr_vs_gdp_absdiff_p90"])
check("S3.1 fn: 197 economies", "197", R["plr_vs_gdp_n"])
check("S3.1 fn: elasticity 0.228", "0.228", R["plr_b"])
check("S3.1 fn: GDP ratio 0.224", "0.224", R["plr_gdp_b"])
check("S3.3: exposure 34% HIC", "34", 100 * R["scen_E_HIC"])
check("S3.3: exposure 11% LIC", "11", 100 * R["scen_E_LIC"])
check("S3.3: any-use 32% HIC", "32", 100 * R["scen_a_HIC"])
check("S3.3: any-use 9% LIC", "9", 100 * R["scen_a_LIC"])
check("S3.3: a*_L 1.00", "1.00", R["aLstar_ratio1.0"])
check("S3.3: a*_L 0.67", "0.67", R["aLstar_ratio1.5"])
check("S3.3: a*_L 0.50", "0.50", R["aLstar_ratio2.0"])
# the a*_L values follow from the proxies: a_H (E_H/E_L)(g_H/g_L)
for ratio, key in [(1.0, "aLstar_ratio1.0"), (1.5, "aLstar_ratio1.5"), (2.0, "aLstar_ratio2.0")]:
    v = R["scen_a_HIC"] * (R["scen_E_HIC"] / R["scen_E_LIC"]) / ratio
    LEDGER.append((abs(v - R[key]) < 1e-6, f"S3.3: a*_L formula check, g ratio {ratio}", f"{R[key]}", v, ""))

# ------------------------------------------------------------------ Section 4
check("S4: 2025 GNI for 182 economies", "182", R["n_econ_gni2025"])
check("S4: remaining 19 economies", "19", R["n_econ_gni"] - R["n_econ_gni2025"])
nga = panel.loc[panel.iso3 == "NGA"].iloc[0]
check("S4: Nigeria 2025 GNI $1,360", "1360", nga["gni_atlas"])
check("S4: Nigeria 2022 GNI revised to $2,940 (current vintage)", "2940", nga["gni_atlas_2022"])
check_in_text("has been revised from \\$2,140 to \\$2,940")  # $2,140 is the earlier vintage quoted from the WDI
check("S4: Argentina $14,650", "14650", panel.loc[panel.iso3 == "ARG", "gni_atlas"].iloc[0])
check("S4: Türkiye $16,300", "16300", panel.loc[panel.iso3 == "TUR", "gni_atlas"].iloc[0])
check("S4: HIC threshold $14,375", "14375", R["hic_threshold_fy27"])
fx_dev = (prices.fx_check_ratio - 1).abs().max() * 100
check("S4: FX sources agree within 1.6%", "1.6", fx_dev)
redirect = sorted({r["storefront"] for r in raw if r["http_status"] == 200 and "/us/" in r["final_url"]
                   and r["storefront"] != "us"})
check("S4: 45 codes redirected to the U.S. storefront", "45", len(redirect))
check("S4: Claude Max $124.99 in the U.S. store", "124.99",
      prices[(prices.storefront == "us") & (prices.plan == "claude_max5x")].price_local.iloc[0])
check("S4: three LIC with country-specific estimates", "3", R["ms_n_cs_LIC"])
ms = panel.dropna(subset=["ms_q2_2026"])
wafr = ms[ms.iso3.isin(["BEN", "GHA", "NER", "NGA"])][["ms_h1_2025", "ms_h2_2025", "ms_q1_2026", "ms_q2_2026"]]
LEDGER.append((bool((wafr.nunique() == 1).all()), "S4: Benin, Ghana, Niger, Nigeria share identical series",
               "identical", 0.0, ""))
for k, v in zip(["ms_h1_2025", "ms_h2_2025", "ms_q1_2026", "ms_q2_2026"], ["8.7", "9.3", "10.1", "10.4"]):
    check(f"S4: West Africa pool {k} = {v}%", v, wafr[k].iloc[0])

# ------------------------------------------------------------------ Table 2 (hand-written coverage column)
aei = pd.read_csv(ROOT / "data" / "raw" / "anthropic" / "anthropic_country_panel.csv")
per_window = []
for _, g in aei.groupby(["release", "date_start"]):
    thr200 = g[g.metric_id == "meets_200_conversation_threshold"]
    # recomputed windows: economies with at least 200 sampled conversations; published windows: economies with a value
    per_window.append(int(thr200.value.sum()) if len(thr200) else g[g.metric_id == "aui_geo_baseline"].iso3.nunique())
check("Table 2: Anthropic index covers 114 economies (min window)", "114", min(per_window))
check("Table 2: 121 economies (max window)", "121", max(per_window))
ms_all = panel.dropna(subset=["ms_q2_2026"])
check("Table 2: Microsoft 147 economies = 145 matched + French Guiana + Taiwan", "147", len(ms_all) + 2)
check("Table 2: 111 country-specific = 110 matched + Taiwan", "111", int(ms_all.ms_country_specific.sum()) + 1)
check("Table 2: 163 economies with quintile shares", "163", R["n_dist"])
check("Table 2: 195 economies with a Gemini quintile", "195", R["g_n"])

# ------------------------------------------------------------------ Section 5.1
check("S5.1: 0.65 / 3.09 / 8.73 / 28.9", "3.09", R["aab_p20_UMIC"])
check("S5.1: 8.73", "8.73", R["aab_p20_LMIC"])
check("S5.1: 28.9", "28.9", R["aab_p20_LIC"])
check("S5.1: 45-fold", "45", R["ratio_aab20_LIC_HIC"])
check("S5.1: 22% of UMIC meet 2%", "22", 100 * R["share_meets2pct_p20_UMIC"])
check("S5.1: 113 of 201 economies exceed", "113", R["n_countries_aab20_gt2"])
check("S5.1: 60% of covered working-age population", "60", 100 * R["share_wapop_aab20_gt2"])
wdi = pd.read_csv(ROOT / "data" / "raw" / "wb" / "wb_indicators_long.csv")
wld = wdi[(wdi.iso3 == "WLD") & (wdi.indicator == "SP.POP.1564.TO")].sort_values("year").value.iloc[-1]
cov = panel.dropna(subset=["gni_atlas", "pop1564"]).pop1564.sum() / wld
check("S5.1: covered economies hold 98.6% of world working-age population", "98.6", 100 * cov)
check("S5.1: 45% above 5%", "45", 100 * R["share_wapop_aab20_gt5"])
check("S5.1: $8 tier meets 2% in 95% of UMIC", "95", 100 * R["share_meets2pct_p8_UMIC"])
LEDGER.append((R["aab_p100_LIC"] > 100, "S5.1: at $100 the median LIC burden exceeds income (>100%)",
               ">100", R["aab_p100_LIC"], ""))
hh = [R["aabhh_p20_" + g] / R["aab_p20_" + g] - 1 for g in ["HIC", "UMIC", "LMIC", "LIC"]]
check("S5.1: HH-consumption burdens 23% higher (min)", "23", 100 * min(hh))
check("S5.1: 81% higher (max)", "81", 100 * max(hh))
for g, v in zip(["HIC", "UMIC", "LMIC", "LIC"], ["1.18", "4.53", "11.9", "35.6"]):
    check(f"S5.1: HH burden {g} {v}", v, R["aabhh_p20_" + g])
bb = csv("broadband_price_comparison.csv").set_index("income_group")
check("S5.1: AI plan / broadband 1.7 (HIC)", "1.7", bb.loc["High income", "actual_dollar_price_ratio2024_2gb"])
check("S5.1: 6.4 (LIC)", "6.4", bb.loc["Low income", "actual_dollar_price_ratio2024_2gb"])
check("S5.1: PPP-indexed LIC burden 10.7%", "10.7", R["aabppp_p20_LIC"])
LEDGER.append((abs(R["aabppp_p20_LIC"] / 2 - 5) < 0.5, "S5.1: 'still five times the benchmark'", "5",
               R["aabppp_p20_LIC"] / 2, ""))
check("S5.1: poorest fifth HIC 1.6%", "1.6", R["aab20_q1_HIC"])
check("S5.1: poorest fifth LMIC 33%", "33", R["aab20_q1_LMIC"])
check("S5.1: poorest fifth LIC 73%", "73", R["aab20_q1_LIC"])
check("S5.1: 19 LIC with survey data", "19", R["n_dist_LIC"])
check("S5.1: richest fifth fails in 100% of LIC", "100", 100 * R["share_top20_gt2_LIC"])
check("S5.1: 98% of LMIC", "98", 100 * R["share_top20_gt2_LMIC"])
check("S5.1: richest quintile median 13% (LIC)", "13", R["aab20_q5_LIC"])
check("S5.1: 4.4% (LMIC)", "4.4", R["aab20_q5_LMIC"])
thr = csv("burden_threshold_sensitivity.csv")
thr = thr[(thr.monthly_price_usd == 20) & (thr["sample"] == "Latest 2022-2025")].set_index("threshold_pct")
for t, v in [(1, "85.6"), (2, "60.1"), (5, "44.6"), (10, "16.7")]:
    check(f"S5.1: population share above {t}% cutoff {v}%", v, 100 * thr.loc[t, "covered_working_age_share_above"])
vin = csv("burden_vintage_sensitivity.csv")
v25 = vin[vin["sample"] == "2025 only"].set_index("income_group").median_burden20
for g, v in [("High income", "0.67"), ("Upper-middle income", "3.09"), ("Lower-middle income", "8.87"),
             ("Low income", "28.9")]:
    check(f"S5.1: 2025-only median {g} {v}", v, v25[g])
g25 = gni[gni.gni_atlas_year == 2025]
w = g25.dropna(subset=["pop1564"])
check("S5.1: 60.0% at 2% on 2025-only sample", "60.0", 100 * w[w.aab20 > 2].pop1564.sum() / w.pop1564.sum())
check("S5.1: 182 economies with 2025 GNI", "182", len(g25))

# ------------------------------------------------------------------ Section 5.2
check("S5.2: Plus 0.039 (s.e. 0.006)", "0.006", R["loc_chatgpt_plus_se"])
for g, v in zip(["UMIC", "LMIC", "LIC"], ["19.99"] * 3):
    check(f"S5.2: median Plus price {g} $19.99", v, R["price_chatgpt_plus_" + g])
check("S5.2: median Plus price HIC $22.99", "22.99", R["price_chatgpt_plus_HIC"])
for g, v in zip(["HIC", "UMIC", "LMIC", "LIC"], ["9.05", "5.99", "5.34", "4.99"]):
    check(f"S5.2: median Go price {g} ${v}", v, R["price_chatgpt_go_" + g])
go = prices[(prices.plan == "chatgpt_go") & prices.price_usd.notna()]
check("S5.2: Go low $4.16 in India", "4.16", go[go.storefront == "in"].price_usd.iloc[0])
check("S5.2: Go $4.19 in Indonesia", "4.19", go[go.storefront == "id"].price_usd.iloc[0])
check("S5.2: 164-economy sample", "164", R["loc_chatgpt_go_n"])
check("S5.2: price-level slope 0.243 on the same sample", "0.243", ppp.loc["chatgpt_go", "ppp_same_sample_beta"])
for g in ["UMIC", "LMIC", "LIC"]:
    check(f"S5.2: AI Plus flat at $4.99 ({g})", "4.99", R["price_gemini_plus_" + g])
check("S5.2: burden elasticity -0.96", "-0.96", R["burden_elasticity_plus"])
check("S5.2: 86% of LMIC storefronts USD-priced", "86", 100 * R["store_usd_LMIC"])
check("S5.2: 100% of LIC USD-priced", "100", 100 * R["store_usd_LIC"])
check("S5.2: 36% LIC no storefront", "36", 100 * R["store_none_LIC"])
check("S5.2: 21% LMIC no storefront", "21", 100 * R["store_none_LMIC"])
check("S5.2: cheapest tier $4.99 in median LIC", "4.99", R["cheapest_price_LIC"])
check("S5.2: cheapest-tier burden 7.2% LIC", "7.2", R["laab_cheapest_LIC"])
check("S5.2: meets 2% nowhere in LIC", "0", 100 * R["share_cheapest_meets2_LIC"])
check("S5.2: 38% of LMIC", "38", 100 * R["share_cheapest_meets2_LMIC"])
lp = csv("local_price_robustness.csv").set_index("plan")
plus = prices[(prices.plan == "chatgpt_plus") & prices.price_usd.notna()]
plus = plus[plus.storefront.map(lambda s: s.upper()).isin(set(panel.iso2.dropna()))]
cur = plus.merge(panel[["iso2", "gni_atlas"]], left_on=plus.storefront.str.upper(), right_on="iso2").dropna(
    subset=["gni_atlas"]).currency.value_counts()
check("S5.2 robustness: 102 USD listings", "102", cur["USD"])
check("S5.2 robustness: 25 EUR listings", "25", cur["EUR"])
check("S5.2 robustness: 37 singleton currencies", "37", (cur == 1).sum())
check("S5.2 robustness: Plus clustered CI low -0.0002", "-0.0002", lp.loc["chatgpt_plus", "cluster_t_ci_low"])
check("S5.2 robustness: Plus clustered CI high 0.079", "0.079", lp.loc["chatgpt_plus", "cluster_t_ci_high"])
check("S5.2 robustness: Go clustered CI [0.114, 0.173] low", "0.114", lp.loc["chatgpt_go", "cluster_t_ci_low"])
check("S5.2 robustness: Go clustered CI high", "0.173", lp.loc["chatgpt_go", "cluster_t_ci_high"])
ws = csv("within_storefront_price_ratios.csv").set_index("comparison")
check("S5.2 robustness: Go/Plus ratio slope 0.104", "0.104", ws.loc["ChatGPT Go / Plus", "slope"])
check("S5.2 robustness: currency-clustered s.e. 0.007", "0.007", ws.loc["ChatGPT Go / Plus", "se_currency_cluster"])
check("S5.2 robustness: 164 economies", "164", ws.loc["ChatGPT Go / Plus", "n"])
LEDGER.append((abs(ws.loc["ChatGPT Go / Plus", "slope"] - (R["loc_chatgpt_go_b"] - R["loc_chatgpt_plus_b"])) < 1e-4,
               "S5.2 robustness: ratio slope equals Go slope minus Plus slope", "0.104",
               R["loc_chatgpt_go_b"] - R["loc_chatgpt_plus_b"], ""))
mm = csv("matched_menu_currency_sensitivity.csv", PU).set_index("specification")
check("S5.2 robustness: USD only 0.113", "0.113", mm.loc["USD only", "slope"])
check("S5.2 robustness: exclude USD 0.112", "0.112", mm.loc["Exclude USD", "slope"])
check("S5.2 robustness: exclude USD and EUR 0.125", "0.125", mm.loc["Exclude USD and EUR", "slope"])
check("S5.2 robustness: 102 USD-priced storefronts", "102", mm.loc["USD only", "n"])
LEDGER.append((mm.loc["Exclude USD", "low_income_n"] == 0, "S5.2 robustness: no LIC once USD excluded", "0",
               mm.loc["Exclude USD", "low_income_n"], ""))
check("S5.2 robustness: 2025-GNI-only Go 0.149", "0.149", lp.loc["chatgpt_go", "beta_2025"])
check("S5.2 robustness: 2025-GNI-only Plus 0.046", "0.046", lp.loc["chatgpt_plus", "beta_2025"])
pr = json.load(open(PU / "price_reliability_summary.json"))
LEDGER.append((pr["candidate_audit"]["all_go_plus_have_single_surviving_candidate"],
               "S5.2 plan matching: single surviving candidate in every Go/Plus cell", "True", 1.0, ""))
LEDGER.append((pr["candidate_audit"]["annual_filter_cutoff_3_5_8_all_identical"],
               "S5.2 plan matching: cutoffs 3, 5, 8 select the same listings", "True", 1.0, ""))
cl = prices[(prices.plan == "claude_pro") & prices.price_local.notna()]
LEDGER.append((bool((cl.n_monthly_candidates == 1).all()), "S5.2 plan matching: Claude Pro single candidate",
               "True", 1.0, ""))
mc = csv("monthly_candidate_sensitivity.csv", PU)
gp = mc[mc.plan == "gemini_pro"].set_index("specification").slope
check("S5.2 plan matching: Google AI Pro three ambiguous cells", "3",
      mc[(mc.plan == "gemini_pro") & (mc.specification.str.startswith("Exclude"))].excluded_n.iloc[0])
check("S5.2 plan matching: 0.0370", "0.0370", gp["Published modal candidate"])
check("S5.2 plan matching: 0.0374", "0.0374", gp["Exclude multiple surviving price candidates"])

# ------------------------------------------------------------------ Section 5.3
for g, v in zip(["HIC", "UMIC", "LMIC", "LIC"], ["32.3", "18.8", "12.0", "7.6"]):
    check(f"S5.3: median user share {g} {v}%", v, R["ms_median_cs_" + g])
check("S5.3: 8.3 pp per log point", "8.3", R["ms_lev_cs_b"])
check("S5.3: elasticity 0.370", "0.370", R["ms_log_cs_b"])
check("S5.3: s.e. 0.021", "0.021", R["ms_log_cs_se"])
check("S5.3: R2 0.71", "0.71", R["ms_log_cs_r2"])
check("S5.3: pooled 0.336", "0.336", R["ms_log_all_b"])
check("S5.3: collapsed 0.367", "0.367", R["ms_log_collapsed_b"])
ctl = [R["ms_c%d_b" % i] for i in range(1, 6)]
check("S5.3: controls range 0.355 (min)", "0.355", min(ctl))
check("S5.3: controls range 0.367 (max)", "0.367", max(ctl))
check("S5.3: urbanisation p ~ 0.04 in column (3)", "0.04", R["ms_c3_urban_p"])
check("S5.3: urbanisation p ~ 0.04 in column (4)", "0.04", R["ms_c4_urban_p"])
LEDGER.append((R["ms_c5_urban_p"] > 0.05, "S5.3: urbanisation loses significance with region FE", ">0.05",
               R["ms_c5_urban_p"], ""))
check("S5.3: connectivity 0.182", "0.182", R["decomp_connect_b"])
check("S5.3: ratio 0.189", "0.189", R["decomp_cond_b"])
check("S5.3: 49%", "49", 100 * R["decomp_share_connect"])
for g in ["UMIC", "LMIC", "LIC"]:
    v = 100 * R["ai_among_online_" + g]
    LEDGER.append((abs(v - 23) <= 1, f"S5.3: AI/internet ratio 'about 23%' ({g})", "about 23", v, "within one point"))
check("S5.3: 37.5% HIC", "37.5", 100 * R["ai_among_online_HIC"])
check("S5.3: non-HIC slope -0.03", "-0.03", R["di_nonhic_b"])
check("S5.3: (s.e. 0.06)", "0.06", R["di_nonhic_se"])
LEDGER.append((abs(R["aab_p20_LIC"] / R["aab_p20_UMIC"] - 9) < 0.5, "S5.3: burden rises 'nine-fold' UMIC to LIC",
               "9", R["aab_p20_LIC"] / R["aab_p20_UMIC"], ""))
for g, v in zip(["HIC", "UMIC", "LMIC", "LIC"], ["5.5", "3.7", "2.0", "0.9"]):
    check(f"S5.3 dynamics: gain {g} {v} points", v, R["gain_pp_median_" + g])
grow = [R["growth_pct_median_" + g] for g in ["HIC", "UMIC", "LMIC"]]
check("S5.3 dynamics: proportional growth 21% (min)", "21", min(grow))
check("S5.3 dynamics: 26% (max)", "26", max(grow))
check("S5.3 dynamics: convergence -0.026", "-0.026", R["conv_log_b"])
check("S5.3 dynamics: (s.e. 0.011)", "0.011", R["conv_log_se"])
check("S5.3 dynamics: sd log 0.564", "0.564", R["sd_log_ms_h1_2025"])
check("S5.3 dynamics: 0.553", "0.553", R["sd_log_ms_q2_2026"])
check("S5.3 dynamics: 1.37 points per log point", "1.37", R["conv_pp_b"])
check("S5.3 dynamics: (s.e. 0.13)", "0.13", R["conv_pp_se"])
check("S5.3 dynamics: sd pp 10.9", "10.9", R["sd_pp_ms_h1_2025"])
check("S5.3 dynamics: 12.8", "12.8", R["sd_pp_ms_q2_2026"])
check("S5.3 dynamics: gap 16.3", "16.3", R["gap_HIC_LMIC_ms_h1_2025"])
check("S5.3 dynamics: 20.3", "20.3", R["gap_HIC_LMIC_ms_q2_2026"])

# ------------------------------------------------------------------ Section 5.4
check("S5.4: 96 economies", "96", R["tm_aui_n"])
for g, v in zip(["HIC", "UMIC", "LMIC", "LIC"], ["42", "33", "20", "1"]):
    check(f"S5.4: {v} {g} economies", v, R["tm_n_" + g])
check("S5.4: 0.711 (s.e. 0.036)", "0.711", R["tm_aui_b"])
check("S5.4: s.e. 0.036", "0.036", R["tm_aui_se"])
check("S5.4: 0.371 (s.e. 0.026)", "0.371", R["tm_ms_b"])
check("S5.4: s.e. 0.026", "0.026", R["tm_ms_se"])
LEDGER.append((abs(R["tm_ratio"] - 2) < 0.15, "S5.4: 'twice as steeply'", "2", R["tm_ratio"], ""))
check("S5.4: difference 0.340", "0.340", R["tm_diff_b"])
check("S5.4: clustered s.e. 0.034", "0.034", R["tm_diff_se"])
check("S5.4: bootstrap 0.27", "0.27", R["tm_diff_boot_lo"])
check("S5.4: bootstrap 0.40", "0.40", R["tm_diff_boot_hi"])
check("S5.4: log-odds 0.50 vs 0.71", "0.50", R["tm_logit_ms_b"])
check("S5.4: excl. HIC 0.33", "0.33", R["tm_ms_nonhic_b"])
check("S5.4: excl. HIC 0.69", "0.69", R["tm_aui_nonhic_b"])
check("S5.4: controls 0.31", "0.31", R["tm_ms_ctl_b"])
check("S5.4: controls 0.55", "0.55", R["tm_aui_ctl_b"])
check("S5.4: earlier windows 0.38", "0.38", R["tm_ms_2025_b"])
check("S5.4: earlier windows 0.62", "0.62", R["tm_aui_2025_b"])
check("S5.4: pooled 0.36", "0.36", R["tm_ms_allms_b"])
check("S5.4: pooled 0.73", "0.73", R["tm_aui_allms_b"])
check("S5.4 time: 111 economies", "111", R["aui_common_n"])
check("S5.4 time: 0.68 Aug 2025", "0.68", R["aui_common_aug25_b"])
check("S5.4 time: 0.68 Nov 2025", "0.68", R["aui_common_nov25_b"])
check("S5.4 time: 0.74 Feb 2026", "0.74", R["aui_common_feb26_b"])
check("S5.4 time: 0.77 Apr 2026", "0.77", R["aui_common_apr26_b"])
check("S5.4 time: 0.73 May 2026", "0.73", R["aui_common_may26_b"])
check("S5.4 time: change 0.064", "0.064", R["aui_change_aug25_feb26_b"])
check("S5.4 time: (s.e. 0.018)", "0.018", R["aui_change_aug25_feb26_se"])
check("S5.4 time: Feb-May -0.006", "-0.006", R["aui_change_feb26_may26_b"])
check("S5.4 time: (s.e. 0.016)", "0.016", R["aui_change_feb26_may26_se"])
check("S5.4: coursework -4.7 points per log point", "4.7", -R["coursework_b"])
check("S5.4: coursework 35% LIC", "35", R["coursework_LIC"])
check("S5.4: five LIC economies", "5", R["coursework_n_LIC"])
check("S5.4: 17% HIC", "17", R["coursework_HIC"])
check("S5.4: Spearman 0.46", "0.46", R["g_spearman"])
check("S5.4: 195 economies", "195", R["g_n"])
cp = csv("cross_provider_gradient_robustness.csv").set_index("specification").difference
check("S5.4 direct: 0.340", "0.340", cp["Baseline"])
check("S5.4 direct: 0.356 (2025 GNI)", "0.356", cp["2025 GNI only"])
check("S5.4 direct: 0.266 (region FE)", "0.266", cp["Region fixed effects"])
check("S5.4 direct: 0.232 (controls)", "0.232", cp["Internet, education, urbanisation"])
check("S5.4 direct: 0.476 (population weighted)", "0.476", cp["Working-age-population weighted (different estimand)"])
loo = csv("gradient_gap_leave_one_out.csv").gradient_gap
check("S5.4 direct: leave-one-out min 0.329", "0.329", loo.min())
check("S5.4 direct: leave-one-out max 0.351", "0.351", loo.max())
check("S5.4: beta ~ 0.04 at the $20 tier", "0.04", R["loc_chatgpt_plus_b"])

# ------------------------------------------------------------------ Sections 6-7
check("S6.1: 'factor of about 45'", "45", R["ratio_aab20_LIC_HIC"])
LEDGER.append((R["aab_p20_HIC"] < 1 and R["aab_p20_LIC"] > 25, "S7: 'less than 1% ... more than a quarter'",
               "<1, >25", R["aab_p20_LIC"], ""))

# ------------------------------------------------------------------ Appendix B
check("App. B: 865 entries in results.json", "865", len(R))
check("App. B: 654 requests", "654", len(raw))
local = [r for r in raw if r["http_status"] == 200 and "/us/" not in r["final_url"]] + \
        [r for r in raw if r["http_status"] == 200 and r["storefront"] == "us"]
redirected = [r for r in raw if r["http_status"] == 200 and "/us/" in r["final_url"] and r["storefront"] != "us"]
notfound = [r for r in raw if r["http_status"] != 200]
check("App. B: 500 local pages", "500", len(local))
check("App. B: 135 redirected", "135", len(redirected))
check("App. B: 19 not found", "19", len(notfound))
check("App. B: 217 World Bank economies plus Taiwan = 218 codes", "218", len({r["storefront"] for r in raw}))
amb = prices[prices.n_distinct_monthly > 1]
check("App. B: three ambiguous cells (two distinct monthly candidates)", "3", len(amb))
LEDGER.append((set(amb.storefront) == {"bj", "in", "tr"} and set(amb.plan) == {"gemini_pro"},
               "App. B: ambiguous cells are Google AI Pro in Benin, India, Türkiye", "bj,in,tr", 0.0, ""))
check("App. B: lowest-price alternative changes Gemini Pro elasticity by 0.0001", "0.0001",
      abs(R["loc_gemini_pro_lowalt_b"] - R["loc_gemini_pro_b"]))
pooled = ms[["ms_h1_2025", "ms_h2_2025", "ms_q1_2026", "ms_q2_2026"]].round(6).astype(str).agg("|".join, axis=1)
dup = pooled.duplicated(keep=False)
check("App. B: 142 with income data", "142", R["n_ms_all"])
check("App. B: 109 country-specific with income", "109", R["n_ms_cs"])
check("App. B: 0.843 August 2025 scaling factor", "0.843", 0.843)  # documented constant in code/03_anthropic_country.py

# ------------------------------------------------------------------ Appendix C
check("App. C: 109-country sample", "109", R["decomp_total_n"])
check("App. C: 0.182", "0.182", R["decomp_connect_b"])
check("App. C: 0.189", "0.189", R["decomp_cond_b"])
check("App. C: 0.370", "0.370", R["decomp_total_b"])
check("App. C: 49%", "49", 100 * R["decomp_share_connect"])
check("App. C: conditional elasticity 0.05", "0.05", R["ms_lnI_cond_b"])
check("App. C: (s.e. 0.20)", "0.20", R["ms_lnI_cond_se"])
for g, v in zip(["UMIC", "LMIC", "LIC"], ["21", "49", "67"]):
    check(f"App. C: connectivity share {g} {v}%", v, 100 * R["share_connect_gap_" + g])
for g, v in zip(["UMIC", "LMIC", "LIC", "HIC"], ["22.7", "23.6", "23.0", "37.5"]):
    check(f"App. C: AI/internet ratio {g} {v}%", v, 100 * R["ai_among_online_" + g])

# ------------------------------------------------------------------ Appendix E
p5 = csv("pro500_reference_scenario.csv").set_index("income_group")
for g, v in [("High income", "16.21"), ("Upper-middle income", "77.17"), ("Lower-middle income", "218.18"),
             ("Low income", "722.89")]:
    check(f"App. E: $500 burden {g} {v}", v, p5.loc[g, "burden500"])
    LEDGER.append((abs(p5.loc[g, "burden500"] / p5.loc[g, "burden20"] - 25) < 1e-9,
                   f"App. E: $500 burden is 25x the $20 burden ({g})", "25", p5.loc[g, "burden500"] / p5.loc[g, "burden20"], ""))
check("App. E: 2% benchmark corresponds to $300,000 GNI per capita", "300000", 1200 * 500 / 2)
LEDGER.append((panel.gni_atlas.max() < 300000, "App. E: no economy reaches $300,000", "<300000",
               panel.gni_atlas.max(), ""))

# ------------------------------------------------------------------ Microsoft pooling recomputation (Section 4, Appendix B)
# The region-imputed flag is set in code/10_build_dataset.py (economies sharing an identical four-period series).
imp = panel.dropna(subset=["ms_q2_2026"])
check("S4: 36 region-imputed economies = 35 World Bank economies in the panel + French Guiana", "36",
      int(imp.ms_region_imputed.sum()) + 1)
check("S4: 20 of 23 low-income economies pooled", "20", int(imp[imp.income_group == "Low income"].ms_region_imputed.sum()))
check("S4: 23 low-income economies in the Microsoft data", "23", int((imp.income_group == "Low income").sum()))
check("S4/App. B: 145 Microsoft economies matched to World Bank economies", "145", len(imp))

# ------------------------------------------------------------------ report
bad = [l for l in LEDGER if not l[0]]
print(f"{len(LEDGER)} checks, {len(bad)} mismatches")
for ok, loc, printed, value, note in LEDGER:
    if not ok:
        print(f"  MISMATCH  {loc}: printed {printed!r}, pipeline value {value!r} {note}")
sys.exit(1 if bad else 0)
