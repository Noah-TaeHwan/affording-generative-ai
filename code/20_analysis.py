"""
20_analysis.py  --  all numbers reported in the paper are produced here.
Reads data/processed/country_panel.csv and appstore_prices_long.csv; writes output/tables/*.csv and
output/results.json (a flat dictionary of every scalar quoted in the text).
"""
import json, pathlib, warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats

warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parents[1]
PROC, TAB = ROOT / "data" / "processed", ROOT / "output" / "tables"
TAB.mkdir(parents=True, exist_ok=True)
R = {}                                                   # results dictionary
ORDER = ["High income", "Upper-middle income", "Lower-middle income", "Low income"]
SHORT = {"High income": "HIC", "Upper-middle income": "UMIC", "Lower-middle income": "LMIC", "Low income": "LIC"}
rng = np.random.default_rng(20260927)

df = pd.read_csv(PROC / "country_panel.csv", keep_default_na=False, na_values=[""])  # keep ISO2 "NA" = Namibia
df["income_group"] = pd.Categorical(df.income_group, ORDER, ordered=True)
df["grp"] = df.income_group.map(SHORT)
PRICES = {"p8": 8.0, "p20": 20.0, "p60": 60.0, "p100": 100.0, "p200": 200.0, "p300": 300.0}


def aab(price, denom):
    return 12.0 * price / denom * 100.0


def ols(formula, data, cov="HC3"):
    return smf.ols(formula, data=data).fit(cov_type=cov)


def store(prefix, res, var):
    R[f"{prefix}_b"] = float(res.params[var]); R[f"{prefix}_se"] = float(res.bse[var])
    lo, hi = res.conf_int().loc[var]; R[f"{prefix}_lo"] = float(lo); R[f"{prefix}_hi"] = float(hi)
    R[f"{prefix}_p"] = float(res.pvalues[var]); R[f"{prefix}_n"] = int(res.nobs); R[f"{prefix}_r2"] = float(res.rsquared)


# ======================================================================================= A. BURDEN
d = df[df.gni_atlas.notna()].copy()
R["n_econ_gni"] = int(len(d)); R["n_econ_gni2025"] = int((d.gni_atlas_year == 2025).sum())
for k, p in PRICES.items():
    d[f"aab_{k}"] = aab(p, d.gni_atlas)
    d[f"aabppp_{k}"] = aab(p, d.gni_ppp)
    d[f"aabhh_{k}"] = aab(p, d.hfce_pc)
# group table
rows = []
for g in ORDER:
    s = d[d.income_group == g]
    row = {"group": SHORT[g], "n": len(s), "median_gni": s.gni_atlas.median()}
    for k in PRICES:
        row[f"aab_{k}"] = s[f"aab_{k}"].median()
    row["aabppp_p20"] = s["aabppp_p20"].median(); row["aabhh_p20"] = s["aabhh_p20"].median()
    row["aab_p20_iqr_lo"] = s["aab_p20"].quantile(.25); row["aab_p20_iqr_hi"] = s["aab_p20"].quantile(.75)
    rows.append(row)
    for k in PRICES:
        R[f"aab_{k}_{SHORT[g]}"] = float(row[f"aab_{k}"])
    R[f"aabppp_p20_{SHORT[g]}"] = float(row["aabppp_p20"]); R[f"aabhh_p20_{SHORT[g]}"] = float(row["aabhh_p20"])
    R[f"median_gni_{SHORT[g]}"] = float(row["median_gni"]); R[f"n_{SHORT[g]}"] = int(len(s))
tabA = pd.DataFrame(rows); tabA.to_csv(TAB / "A1_burden_by_group.csv", index=False)
R["ratio_aab20_LIC_HIC"] = R["aab_p20_LIC"] / R["aab_p20_HIC"]
# 2% benchmark (UN Broadband Commission) and population exposure
w = d.pop1564.fillna(0)
for thr in [2, 5, 10]:
    over = d.aab_p20 > thr
    R[f"share_countries_aab20_gt{thr}"] = float(over.mean())
    R[f"share_wapop_aab20_gt{thr}"] = float((w * over).sum() / w.sum())
    R[f"n_countries_aab20_gt{thr}"] = int(over.sum())
R["threshold_gni_for_2pct_p20"] = 12 * 20 / 0.02
R["threshold_gni_for_2pct_p8"] = 12 * 8 / 0.02
R["hic_threshold_fy27"] = 14375
for g in ORDER:
    s = d[d.income_group == g]
    R[f"share_meets2pct_p20_{SHORT[g]}"] = float((s.aab_p20 <= 2).mean())
    R[f"share_meets2pct_p8_{SHORT[g]}"] = float((s.aab_p8 <= 2).mean())
# distribution-adjusted burden (quintile means approximated with survey quintile shares)
dq = d[d.q1_share.notna()].copy()
for q in ["q1", "q3", "q5"]:
    dq[f"inc_{q}"] = dq.gni_atlas * dq[f"{q}_share"] / 20.0
    dq[f"aab20_{q}"] = aab(20, dq[f"inc_{q}"])
rows = []
for g in ORDER:
    s = dq[dq.income_group == g]
    rows.append({"group": SHORT[g], "n": len(s), "aab20_q1": s.aab20_q1.median(), "aab20_q3": s.aab20_q3.median(),
                 "aab20_q5": s.aab20_q5.median(), "aab20_mean": s.aab_p20.median(),
                 "median_dist_year": s.dist_year.median()})
    for q in ["q1", "q3", "q5"]:
        R[f"aab20_{q}_{SHORT[g]}"] = float(s[f"aab20_{q}"].median())
    R[f"n_dist_{SHORT[g]}"] = int(len(s))
pd.DataFrame(rows).to_csv(TAB / "A2_burden_by_quintile.csv", index=False)
# how many countries where even the top quintile's mean income implies AAB20 > 2%
R["n_top20_gt2"] = int((dq.aab20_q5 > 2).sum()); R["n_dist"] = int(len(dq))
R["share_top20_gt2_LIC"] = float((dq[dq.grp == "LIC"].aab20_q5 > 2).mean())
R["share_top20_gt2_LMIC"] = float((dq[dq.grp == "LMIC"].aab20_q5 > 2).mean())
# comparison with ITU entry-level mobile broadband basket (% of GNI p.c., same definition)
di = d[d.mbb_2gb_pct_gni_latest_official.notna()].copy()
di["ai_over_mbb"] = di.aab_p20 / di.mbb_2gb_pct_gni_latest_official
for g in ORDER:
    s = di[di.income_group == g]
    R[f"mbb_{SHORT[g]}"] = float(s.mbb_2gb_pct_gni_latest_official.median())
    R[f"ai_over_mbb_{SHORT[g]}"] = float(s.ai_over_mbb.median())
R["ai_over_mbb_all"] = float(di.ai_over_mbb.median())
R["mbb_usd_median_all"] = float(di.mbb_2gb_usd_2024.median())

# replication of the original 24-country design (2022 GNI, purposive sample)
ORIG = ["USA", "KOR", "AUS", "SGP", "DEU", "CHL", "CHN", "BRA", "MEX", "THA", "ZAF", "COL",
        "IND", "KEN", "NGA", "BGD", "GHA", "MAR", "UGA", "RWA", "MWI", "MOZ", "MDG", "NER"]
o = df[df.iso3.isin(ORIG)].copy()
o["aab20_2022"] = aab(20, o.gni_atlas_2022); o["aab20_2025"] = aab(20, o.gni_atlas)
o["aab20_ppp2022"] = aab(20, o.gni_ppp_2022)
o.set_index("iso3").loc[ORIG, ["country_wb", "grp", "gni_atlas_2022", "gni_atlas", "gni_atlas_year", "aab20_2022",
                               "aab20_2025", "ms_q2_2026", "ms_region_imputed"]].to_csv(TAB / "F1_original24.csv")
for g in ORDER:
    s = o[o.income_group == g]
    R[f"orig_aab20_2022_{SHORT[g]}"] = float(s.aab20_2022.median())
    R[f"orig_aab20_ppp2022_{SHORT[g]}"] = float(s.aab20_ppp2022.median())
    R[f"orig_ms_mean_{SHORT[g]}"] = float(s.ms_q2_2026.mean())
    R[f"orig_ms_mean_cs_{SHORT[g]}"] = float(s[s.ms_region_imputed == 0].ms_q2_2026.mean()) if (s.ms_region_imputed == 0).any() else None
    R[f"orig_n_imputed_{SHORT[g]}"] = int(s.ms_region_imputed.sum())
R["orig_pearson"] = float(np.corrcoef(np.log(o.gni_atlas_2022), o.ms_q2_2026)[0, 1])
R["orig_spearman"] = float(stats.spearmanr(o.gni_atlas_2022, o.ms_q2_2026).correlation)
R["orig_n_imputed"] = int(o.ms_region_imputed.sum())
cs = o[o.ms_region_imputed == 0]
R["orig_pearson_cs"] = float(np.corrcoef(np.log(cs.gni_atlas_2022), cs.ms_q2_2026)[0, 1]); R["orig_n_cs"] = int(len(cs))
# the "PPP burden" equals the burden under a counterfactual PPP-indexed price p_c = p * PLR_c
d["plr"] = d.gni_atlas / d.gni_ppp
for g in ORDER:
    R[f"plr_median_{SHORT[g]}"] = float(d[d.income_group == g].plr.median())
    R[f"ppp_indexed_price20_{SHORT[g]}"] = float(20 * d[d.income_group == g].plr.median())

# ======================================================================================= B. LOCAL PRICES
lp = pd.read_csv(PROC / "appstore_prices_long.csv", keep_default_na=False, na_values=[""])
cm = df[["iso3", "iso2", "gni_atlas", "gni_ppp", "grp", "income_group", "pop1564"]].copy()
cm["storefront"] = cm.iso2.str.lower()
lp = lp.merge(cm, on="storefront", how="inner")
lp = lp[lp.gni_atlas.notna()].copy()
lp["ln_p"] = np.log(lp.price_usd); lp["ln_gni"] = np.log(lp.gni_atlas)
lp["laab"] = aab(lp.price_usd, lp.gni_atlas)
lp["usd_priced"] = (lp.currency == "USD").astype(int)
rows = []
for plan in ["chatgpt_go", "chatgpt_plus", "chatgpt_pro5x", "chatgpt_pro20x", "claude_pro", "claude_max5x",
             "gemini_plus", "gemini_pro", "gemini_ultra"]:
    s = lp[lp.plan == plan]
    res = ols("ln_p ~ ln_gni", s)
    store(f"loc_{plan}", res, "ln_gni")
    us = s[s.storefront == "us"].price_usd
    rows.append({"plan": plan, "n": int(res.nobs), "us_price": float(us.iloc[0]) if len(us) else np.nan,
                 "median_usd": s.price_usd.median(), "p10": s.price_usd.quantile(.1),
                 "p90": s.price_usd.quantile(.9), "min": s.price_usd.min(), "max": s.price_usd.max(),
                 "beta_ln_gni": res.params["ln_gni"], "se": res.bse["ln_gni"],
                 "share_usd_priced": s.usd_priced.mean(),
                 **{f"median_{SHORT[g]}": s[s.income_group == g].price_usd.median() for g in ORDER}})
    for g in ORDER:
        R[f"price_{plan}_{SHORT[g]}"] = float(s[s.income_group == g].price_usd.median())
        R[f"laab_{plan}_{SHORT[g]}"] = float(s[s.income_group == g].laab.median())
        R[f"nprice_{plan}_{SHORT[g]}"] = int((s.income_group == g).sum())
pd.DataFrame(rows).to_csv(TAB / "B1_localization.csv", index=False)
# sensitivity: cells that list more than one monthly price for the same plan -> lowest price instead of the mode
amb = lp[lp.n_distinct_monthly > 1]
R["price_ambiguous_cells"] = int(len(amb))
R["price_ambiguous_cells_lower"] = int((amb.price_usd_min_candidate < amb.price_usd - 1e-9).sum())
dmax = 0.0
for plan in sorted(amb.plan.unique()):
    s = lp[lp.plan == plan].copy(); s["ln_p"] = np.log(s.price_usd_min_candidate)
    b_alt = float(ols("ln_p ~ ln_gni", s).params["ln_gni"]); R[f"loc_{plan}_lowalt_b"] = b_alt
    dmax = max(dmax, abs(b_alt - R[f"loc_{plan}_b"]))
R["price_ambiguous_max_dbeta"] = dmax
# storefront currency & availability by income group (ChatGPT)
av = pd.read_csv(PROC / "appstore_prices_wide.csv", keep_default_na=False, na_values=[""]).merge(df[["iso3", "grp", "income_group"]], on="iso3")
for g in ORDER:
    s = av[av.income_group == g]
    R[f"store_local_chatgpt_{SHORT[g]}"] = float((s.store_chatgpt == "local_storefront").mean())
    R[f"store_none_{SHORT[g]}"] = float((s.store_chatgpt == "no_local_storefront").mean())
    R[f"store_notoffered_{SHORT[g]}"] = float((s.store_chatgpt == "app_not_offered").mean())
    s2 = s[s.store_chatgpt == "local_storefront"]
    R[f"store_usd_{SHORT[g]}"] = float((s2.store_currency == "USD").mean())
    R[f"n_store_{SHORT[g]}"] = int(len(s))
# cheapest locally listed paid tier
ch = lp[lp.plan.isin(["chatgpt_go", "gemini_plus"])].groupby("iso3").price_usd.min().rename("p_cheapest")
dd = d.merge(ch, left_on="iso3", right_index=True, how="left")
dd["laab_cheapest"] = aab(dd.p_cheapest, dd.gni_atlas)
for g in ORDER:
    s = dd[(dd.income_group == g) & dd.p_cheapest.notna()]
    R[f"cheapest_price_{SHORT[g]}"] = float(s.p_cheapest.median())
    R[f"laab_cheapest_{SHORT[g]}"] = float(s.laab_cheapest.median())
    R[f"share_cheapest_meets2_{SHORT[g]}"] = float((s.laab_cheapest <= 2).mean())
# implied burden gradient under observed localisation: d ln(LAAB)/d ln(GNI) = beta - 1
R["burden_elasticity_plus"] = R["loc_chatgpt_plus_b"] - 1
R["burden_elasticity_go"] = R["loc_chatgpt_go_b"] - 1

# ======================================================================================= C. DIFFUSION
m = df[df.ms_q2_2026.notna() & df.gni_atlas.notna()].copy()
m["ln_ms"] = np.log(m.ms_q2_2026 / 100)
m["ln_gni"] = np.log(m.gni_atlas)
mcs = m[m.ms_region_imputed == 0].copy()
R["n_ms_all"] = int(len(m)); R["n_ms_cs"] = int(len(mcs))
for g in ORDER:
    s_all, s_cs = m[m.income_group == g], mcs[mcs.income_group == g]
    R[f"ms_n_all_{SHORT[g]}"] = int(len(s_all)); R[f"ms_n_cs_{SHORT[g]}"] = int(len(s_cs))
    R[f"ms_median_all_{SHORT[g]}"] = float(s_all.ms_q2_2026.median())
    R[f"ms_median_cs_{SHORT[g]}"] = float(s_cs.ms_q2_2026.median()) if len(s_cs) else None
    R[f"ms_popw_all_{SHORT[g]}"] = float(np.average(s_all.ms_q2_2026, weights=s_all.pop1564))
    for t in ["ms_h1_2025", "ms_h2_2025", "ms_q1_2026", "ms_q2_2026"]:
        R[f"{t}_median_cs_{SHORT[g]}"] = float(s_cs[t].median()) if len(s_cs) else None
        R[f"{t}_median_all_{SHORT[g]}"] = float(s_all[t].median())
R["ms_imputed_share_LIC"] = float(m[m.grp == "LIC"].ms_region_imputed.mean())
R["ms_imputed_share_LMIC"] = float(m[m.grp == "LMIC"].ms_region_imputed.mean())
# level-log and log-log gradients
store("ms_lev_cs", ols("ms_q2_2026 ~ ln_gni", mcs), "ln_gni")
store("ms_lev_all", ols("ms_q2_2026 ~ ln_gni", m), "ln_gni")
store("ms_log_cs", ols("ln_ms ~ ln_gni", mcs), "ln_gni")
store("ms_log_all", ols("ln_ms ~ ln_gni", m), "ln_gni")
# collapse region-imputed clusters to one observation each (pop-weighted log income)
cl = m[m.ms_region_imputed == 1].groupby("ms_impute_cluster").apply(
    lambda s: pd.Series({"ln_ms": s.ln_ms.iloc[0], "ln_gni": np.average(s.ln_gni, weights=s.pop1564),
                         "ms_q2_2026": s.ms_q2_2026.iloc[0]}))
mcl = pd.concat([mcs[["ln_ms", "ln_gni", "ms_q2_2026"]], cl], ignore_index=True)
store("ms_log_collapsed", ols("ln_ms ~ ln_gni", mcl), "ln_gni")
R["pearson_lnGNI_ms_cs"] = float(np.corrcoef(mcs.ln_gni, mcs.ms_q2_2026)[0, 1])
R["spearman_GNI_ms_cs"] = float(stats.spearmanr(mcs.gni_atlas, mcs.ms_q2_2026).correlation)
# conditional gradients (complements); same sample across columns
ctrl = ["internet_pct", "tertiary_enrol", "urban_pct", "age65_pct", "fx_online_merchant_pay"]
mc = mcs.dropna(subset=ctrl + ["ln_gni", "ln_ms"]).copy()
specs = {"c1": "ln_ms ~ ln_gni", "c2": "ln_ms ~ ln_gni + internet_pct",
         "c3": "ln_ms ~ ln_gni + internet_pct + tertiary_enrol + urban_pct + age65_pct",
         "c4": "ln_ms ~ ln_gni + internet_pct + tertiary_enrol + urban_pct + age65_pct + fx_online_merchant_pay",
         "c5": "ln_ms ~ ln_gni + internet_pct + tertiary_enrol + urban_pct + age65_pct + fx_online_merchant_pay + C(region)"}
rows = []
for k, f in specs.items():
    res = ols(f, mc)
    store(f"ms_{k}", res, "ln_gni")
    row = {"spec": k, "n": int(res.nobs), "r2": res.rsquared}
    for v in ["ln_gni"] + ctrl:
        if v in res.params:
            row[v] = res.params[v]; row[v + "_se"] = res.bse[v]
    rows.append(row)
    for v in ctrl:
        if v in res.params:
            R[f"ms_{k}_{v}_b"] = float(res.params[v]); R[f"ms_{k}_{v}_se"] = float(res.bse[v])
pd.DataFrame(rows).to_csv(TAB / "C2_conditional_gradients.csv", index=False)
# connectivity decomposition: ln D = ln I + ln(D/I)
mdc = mcs[mcs.internet_pct.notna()].copy()
mdc["ln_I"] = np.log(mdc.internet_pct / 100)
mdc["ln_DI"] = mdc.ln_ms - mdc.ln_I
mdc["ai_among_online"] = (mdc.ms_q2_2026 / mdc.internet_pct).clip(upper=1)
for nm, y in [("decomp_total", "ln_ms"), ("decomp_connect", "ln_I"), ("decomp_cond", "ln_DI")]:
    store(nm, ols(f"{y} ~ ln_gni", mdc), "ln_gni")
R["decomp_share_connect"] = R["decomp_connect_b"] / R["decomp_total_b"]
rows = []
hic = mdc[mdc.grp == "HIC"]
for g in ORDER:
    s = mdc[mdc.income_group == g]
    gap_tot = s.ln_ms.mean() - hic.ln_ms.mean()
    gap_I = s.ln_I.mean() - hic.ln_I.mean()
    rows.append({"group": SHORT[g], "n": len(s), "mean_ms": s.ms_q2_2026.mean(), "mean_internet": s.internet_pct.mean(),
                 "mean_ai_among_online": s.ai_among_online.mean(), "loggap_total": gap_tot,
                 "loggap_connect": gap_I, "loggap_conditional": gap_tot - gap_I,
                 "share_connect": gap_I / gap_tot if g != "High income" else np.nan})
    R[f"ai_among_online_{SHORT[g]}"] = float(s.ai_among_online.mean())
    R[f"internet_mean_{SHORT[g]}"] = float(s.internet_pct.mean())
    R[f"n_decomp_{SHORT[g]}"] = int(len(s))
    if g != "High income":
        R[f"share_connect_gap_{SHORT[g]}"] = float(gap_I / gap_tot)
pd.DataFrame(rows).to_csv(TAB / "C3_connectivity_decomposition.csv", index=False)
# dynamics: beta- and sigma-convergence, H1-2025 -> Q2-2026
mcs["gain_pp"] = mcs.ms_q2_2026 - mcs.ms_h1_2025
mcs["growth_log"] = np.log(mcs.ms_q2_2026 / mcs.ms_h1_2025)
mcs["ln_ms0"] = np.log(mcs.ms_h1_2025 / 100)
store("conv_log", ols("growth_log ~ ln_ms0", mcs), "ln_ms0")
store("conv_pp", ols("gain_pp ~ ln_gni", mcs), "ln_gni")
store("conv_logg", ols("growth_log ~ ln_gni", mcs), "ln_gni")
for t in ["ms_h1_2025", "ms_h2_2025", "ms_q1_2026", "ms_q2_2026"]:
    R[f"sd_log_{t}"] = float(np.log(mcs[t]).std()); R[f"sd_pp_{t}"] = float(mcs[t].std())
    R[f"gap_HIC_LMIC_{t}"] = float(mcs[mcs.grp == "HIC"][t].median() - mcs[mcs.grp == "LMIC"][t].median())
for g in ORDER:
    s = mcs[mcs.income_group == g]
    if len(s):
        R[f"gain_pp_median_{SHORT[g]}"] = float(s.gain_pp.median()); R[f"growth_pct_median_{SHORT[g]}"] = float(
            (np.exp(s.growth_log) - 1).median() * 100)

# ======================================================================================= D. TWO MARGINS
a = df[df.gni_atlas.notna()].copy()
a["ln_gni"] = np.log(a.gni_atlas)
both = a[a.ms_q2_2026.notna() & (a.ms_region_imputed == 0) & a.aui_may26.notna() & (a.aui_may26 > 0)].copy()
both["ln_ms"] = np.log(both.ms_q2_2026 / 100); both["ln_aui"] = np.log(both.aui_may26)
store("tm_ms", ols("ln_ms ~ ln_gni", both), "ln_gni")
store("tm_aui", ols("ln_aui ~ ln_gni", both), "ln_gni")
long = pd.concat([both[["iso3", "ln_gni"]].assign(y=both.ln_ms, anth=0),
                  both[["iso3", "ln_gni"]].assign(y=both.ln_aui, anth=1)])
res = smf.ols("y ~ anth * ln_gni", data=long).fit(cov_type="cluster", cov_kwds={"groups": long.iso3})
store("tm_diff", res, "anth:ln_gni")
B = 2000; diffs = []
iso = both.iso3.values
for _ in range(B):
    s = both.sample(len(both), replace=True, random_state=rng.integers(1e9))
    bm = np.polyfit(s.ln_gni, s.ln_ms, 1)[0]; ba = np.polyfit(s.ln_gni, s.ln_aui, 1)[0]
    diffs.append(ba - bm)
R["tm_diff_boot_lo"], R["tm_diff_boot_hi"] = [float(x) for x in np.percentile(diffs, [2.5, 97.5])]
R["tm_ratio"] = R["tm_aui_b"] / R["tm_ms_b"]
# robustness of the two-margin comparison
both["logit_ms"] = np.log(both.ms_q2_2026 / (100 - both.ms_q2_2026))
store("tm_logit_ms", ols("logit_ms ~ ln_gni", both), "ln_gni")
nh = both[both.grp != "HIC"]
store("tm_ms_nonhic", ols("ln_ms ~ ln_gni", nh), "ln_gni"); store("tm_aui_nonhic", ols("ln_aui ~ ln_gni", nh), "ln_gni")
ctl = both.dropna(subset=["internet_pct", "tertiary_enrol", "urban_pct"])
fctl = " + internet_pct + tertiary_enrol + urban_pct"
store("tm_ms_ctl", ols("ln_ms ~ ln_gni" + fctl, ctl), "ln_gni"); store("tm_aui_ctl", ols("ln_aui ~ ln_gni" + fctl, ctl), "ln_gni")
b2 = a[a.ms_h2_2025.notna() & (a.ms_region_imputed == 0) & a.aui_aug25.notna() & (a.aui_aug25 > 0) & (a.an_ge200_aug25 == 1)].copy()
b2["ln_ms"] = np.log(b2.ms_h2_2025 / 100); b2["ln_aui"] = np.log(b2.aui_aug25)
store("tm_ms_2025", ols("ln_ms ~ ln_gni", b2), "ln_gni"); store("tm_aui_2025", ols("ln_aui ~ ln_gni", b2), "ln_gni")
b3 = a[a.ms_q2_2026.notna() & a.aui_may26.notna() & (a.aui_may26 > 0)].copy()     # incl. region-imputed MS values
b3["ln_ms"] = np.log(b3.ms_q2_2026 / 100); b3["ln_aui"] = np.log(b3.aui_may26)
store("tm_ms_allms", ols("ln_ms ~ ln_gni", b3), "ln_gni"); store("tm_aui_allms", ols("ln_aui ~ ln_gni", b3), "ln_gni")
# PPP benchmark for localisation: elasticity of the price-level ratio (Atlas/PPP) with respect to income
pl = a[a.gni_ppp.notna()].copy(); pl["ln_plr"] = np.log(pl.gni_atlas / pl.gni_ppp)
store("plr", ols("ln_plr ~ ln_gni", pl), "ln_gni")
# the Atlas/PPP ratio is a proxy: compare with the same-year GDP price-level ratio
pg = a[a.plr_gdp.notna()].copy(); pg["ln_plr_gdp"] = np.log(pg.plr_gdp)
store("plr_gdp", ols("ln_plr_gdp ~ ln_gni", pg), "ln_gni")
bo = pg[pg.gni_ppp.notna()]
rd = (bo.gni_atlas / bo.gni_ppp / bo.plr_gdp - 1).abs()
R["plr_vs_gdp_n"] = int(len(bo)); R["plr_vs_gdp_absdiff_median"] = float(rd.median())
R["plr_vs_gdp_absdiff_p90"] = float(rd.quantile(.9))
# Anthropic elasticity over time (full AUI samples)
for wv in ["aug25", "nov25", "feb26", "apr26", "may26"]:
    s = a[a[f"aui_{wv}"].notna() & (a[f"aui_{wv}"] > 0)].copy()
    if wv in ["aug25", "nov25", "feb26"]:
        s = s[s[f"an_ge200_{wv}"] == 1]
    s["ln_aui"] = np.log(s[f"aui_{wv}"])
    store(f"aui_{wv}", ols("ln_aui ~ ln_gni", s), "ln_gni")
# change in the frontier gradient on a COMMON sample of economies observed in every window
cs_ = a.copy()
ok = np.ones(len(cs_), dtype=bool)
for wv in ["aug25", "nov25", "feb26", "apr26", "may26"]:
    ok &= (cs_[f"aui_{wv}"].fillna(0) > 0).values
    if wv in ["aug25", "nov25", "feb26"]:
        ok &= (cs_[f"an_ge200_{wv}"] == 1).values
cs_ = cs_[ok]
R["aui_common_n"] = int(len(cs_))
lg = []
for wv in ["aug25", "nov25", "feb26", "apr26", "may26"]:
    t = cs_[["iso3", "ln_gni"]].copy(); t["y"] = np.log(cs_[f"aui_{wv}"]); t["w"] = wv; lg.append(t)
    store(f"aui_common_{wv}", ols("y ~ ln_gni", t), "ln_gni")
lg = pd.concat(lg)
for w0, w1 in [("aug25", "may26"), ("aug25", "feb26"), ("feb26", "may26")]:
    t = lg[lg.w.isin([w0, w1])].copy(); t["late"] = (t.w == w1).astype(int)
    res = smf.ols("y ~ late * ln_gni", data=t).fit(cov_type="cluster", cov_kwds={"groups": t.iso3})
    store(f"aui_change_{w0}_{w1}", res, "late:ln_gni")
# conditional association of AI use with internet use, holding income fixed (log-log)
mi = mcs[mcs.internet_pct.notna()].copy(); mi["ln_I"] = np.log(mi.internet_pct / 100)
res = ols("ln_ms ~ ln_gni + ln_I", mi)
store("ms_lnI_cond", res, "ln_I"); store("ms_lnI_cond_gni", res, "ln_gni")
# slope of log adoption-among-the-connected on log income outside the high-income group
nh_ = mdc[mdc.grp != "HIC"].copy()
store("di_nonhic", ols("ln_DI ~ ln_gni", nh_), "ln_gni")
# urbanisation p-values in the control specifications
for k in ["c3", "c4", "c5"]:
    res = ols(specs[k], mc)
    R[f"ms_{k}_urban_p"] = float(res.pvalues["urban_pct"])
# coursework share and income (Anthropic, May 2026)
s = a[a.an_coursework_may26.notna()].copy()
store("coursework", ols("an_coursework_may26 ~ ln_gni", s), "ln_gni")
for g in ORDER:
    R[f"coursework_{SHORT[g]}"] = float(s[s.income_group == g].an_coursework_may26.median())
    R[f"coursework_n_{SHORT[g]}"] = int((s.income_group == g).sum())
# Google ATLAS per-capita intensity quintile
s = a[a.g_intensity_q.notna()]
R["g_spearman"] = float(stats.spearmanr(s.gni_atlas, s.g_intensity_q).correlation); R["g_n"] = int(len(s))
for q in range(1, 6):
    R[f"g_median_gni_q{q}"] = float(s[s.g_intensity_q == q].gni_atlas.median())
# Microsoft vs Anthropic: which countries are over/under-represented on the frontier margin
both["resid_ms"] = ols("ln_ms ~ ln_gni", both).resid
both["resid_aui"] = ols("ln_aui ~ ln_gni", both).resid
both[["iso3", "country_wb", "grp", "gni_atlas", "ms_q2_2026", "aui_may26", "resid_ms", "resid_aui"]].to_csv(
    TAB / "D1_two_margins_sample.csv", index=False)
R["n_two_margins"] = int(len(both))
for g in ORDER:
    R[f"tm_n_{SHORT[g]}"] = int((both.income_group == g).sum())

# ======================================================================================= E. SCENARIOS
# Hulten-style illustration with proxy inputs (occupational exposure for E, population-wide use for a):
# dY/Y = sL * E_g * a_g * g_task
sL = 0.55
E = {"HIC": 0.34, "UMIC": 0.34 * (11 / 34) ** (1 / 3), "LMIC": 0.34 * (11 / 34) ** (2 / 3), "LIC": 0.11}
rows = []
for g in ["HIC", "UMIC", "LMIC", "LIC"]:
    a_g = R[f"ms_median_all_{g}"] / 100 if R.get(f"ms_median_cs_{g}") is None else R[f"ms_median_cs_{g}"] / 100
    if g == "LIC":
        a_g = R["ms_median_all_LIC"] / 100
    for gt in [0.10, 0.20, 0.30]:
        naive = a_g * gt
        hult = sL * E[g] * a_g * gt
        univ = sL * E[g] * 1.0 * gt
        at_hic = sL * E[g] * (R["ms_median_cs_HIC"] / 100) * gt
        rows.append({"group": g, "E_exposed": E[g], "a_adoption": a_g, "g_task": gt, "naive_a_g": naive,
                     "hulten": hult, "hulten_if_HIC_adoption": at_hic, "hulten_universal": univ})
        R[f"scen_{g}_{int(gt*100)}_naive"] = float(naive * 100)
        R[f"scen_{g}_{int(gt*100)}_hulten"] = float(hult * 100)
        R[f"scen_{g}_{int(gt*100)}_hicadopt"] = float(at_hic * 100)
    R[f"scen_E_{g}"] = E[g]; R[f"scen_a_{g}"] = a_g
pd.DataFrame(rows).to_csv(TAB / "E1_scenarios.csv", index=False)
# equalisation threshold: a_L* = a_H * (E_H g_H) / (E_L g_L) for g_L/g_H in {1, 1.5, 2}
for ratio in [1.0, 1.5, 2.0]:
    R[f"aLstar_ratio{ratio}"] = float(R["scen_a_HIC"] * E["HIC"] / (E["LIC"] * ratio))

# ======================================================================================= 24-country case table
case = df[df.iso3.isin(ORIG)].set_index("iso3").loc[ORIG].copy()
pw = lp.pivot_table(index="iso3", columns="plan", values="price_usd", aggfunc="first")
case = case.join(pw[["chatgpt_go", "chatgpt_plus", "gemini_plus", "gemini_pro"]], how="left")
case["aab20"] = aab(20, case.gni_atlas)
case["laab_plus"] = aab(case.chatgpt_plus, case.gni_atlas)
case["laab_go"] = aab(case.chatgpt_go, case.gni_atlas)
av2 = av.set_index("iso3")
case["store_status"] = av2.reindex(case.index)["store_chatgpt"]
case["store_currency"] = av2.reindex(case.index)["store_currency"]
case[["country_wb", "grp", "gni_atlas", "gni_atlas_year", "aab20", "chatgpt_plus", "laab_plus", "chatgpt_go",
      "laab_go", "gemini_plus", "store_status", "store_currency", "ms_q2_2026", "ms_region_imputed", "aui_may26",
      "internet_pct"]].to_csv(TAB / "T1_case_countries.csv")

json.dump({k: (round(v, 6) if isinstance(v, float) else v) for k, v in R.items()},
          open(ROOT / "output" / "results.json", "w"), indent=1)
print(f"{len(R)} results written")
