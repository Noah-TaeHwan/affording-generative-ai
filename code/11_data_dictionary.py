"""
11_data_dictionary.py -- writes data/processed/data_dictionary.csv for country_panel.csv.
"""
import pathlib, re
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"
d = pd.read_csv(P / "country_panel.csv", keep_default_na=False, na_values=[""])  # keep ISO2 "NA" = Namibia
WB, FX, MS, AN = "World Bank WDI (API, 27 Sep 2026)", "Global Findex 2025 (WB API source 28)", \
    "Microsoft AI Economy Institute, AI Diffusion Q2 2026 dataset", "Anthropic Economic Index (HF commit 2ea58ff)"
D = {
    "iso3": ("ISO 3166-1 alpha-3 code", "World Bank"), "iso2": ("ISO 3166-1 alpha-2 code", "World Bank"),
    "country_wb": ("Economy name (World Bank)", "World Bank"), "region": ("World Bank region", "World Bank"),
    "income_group": ("World Bank income group, FY2027 (effective 1 Jul 2026, based on 2025 GNI p.c.)", "World Bank"),
    "lending": ("World Bank lending category", "World Bank"),
    "gni_atlas": ("GNI per capita, Atlas method, current US$ (2025; latest 2022-2024 if missing)", WB),
    "gni_ppp": ("GNI per capita, PPP, current international $ (2025; latest 2022-2024 if missing)", WB),
    "gni_atlas_2022": ("GNI per capita, Atlas method, 2022 (current WDI vintage)", WB),
    "gni_ppp_2022": ("GNI per capita, PPP, 2022 (current WDI vintage)", WB),
    "pop": ("Population, total (latest 2020-2025)", WB), "pop1564": ("Population ages 15-64 (latest 2020-2025)", WB),
    "hfce_pc": ("Household final consumption expenditure per capita, current US$ (latest 2022-2025)", WB),
    "q1_share": ("Income/consumption share of poorest 20% (%), latest survey 2010-2025", WB),
    "q2_share": ("Income share, second quintile (%)", WB), "q3_share": ("Income share, third quintile (%)", WB),
    "q4_share": ("Income share, fourth quintile (%)", WB), "q5_share": ("Income share, richest 20% (%)", WB),
    "dist_year": ("Survey year of quintile shares", WB), "gini": ("Gini index (latest)", WB),
    "internet_pct": ("Individuals using the Internet (% of population), latest 2018-2025", WB + " / ITU"),
    "electricity_pct": ("Access to electricity (% of population)", WB),
    "fixed_bb_per100": ("Fixed broadband subscriptions per 100 people", WB),
    "tertiary_enrol": ("School enrolment, tertiary (% gross), latest 2012-2025", WB),
    "urban_pct": ("Urban population (% of total)", WB), "age65_pct": ("Population ages 65+ (% of total)", WB),
    "wage_emp_pct": ("Wage and salaried workers (% of employment)", WB),
    "services_emp_pct": ("Employment in services (% of employment)", WB),
    "fx_account": ("Account ownership (% age 15+)", FX), "fx_credit_card": ("Owns a credit card (% age 15+)", FX),
    "fx_debit_card": ("Owns a debit card (% age 15+)", FX),
    "fx_online_merchant_pay": ("Made a digital online merchant payment for an online purchase (% age 15+)", FX),
    "fx_made_digital_pay": ("Made a digital payment (% age 15+)", FX),
    "fx_smartphone": ("Main mobile phone is a smartphone (% age 15+)", FX),
    "fx_internet_access": ("Has access to the Internet (% age 15+)", FX),
    "ms_economy_name": ("Economy name in the Microsoft dataset", MS),
    "ms_h1_2025": ("AI User Share H1 2025 (% of population 15-64)", MS),
    "ms_h2_2025": ("AI User Share H2 2025 (%)", MS), "ms_q1_2026": ("AI User Share Q1 2026 (%)", MS),
    "ms_q2_2026": ("AI User Share Q2 2026 (%)", MS),
    "ms_region_imputed": ("1 = value is a regional aggregate (economy shares an identical series with a pool)", MS + "; Misra et al. (2025) App. Table 2"),
    "ms_impute_cluster": ("Identifier of the regional pool (the pooled series)", "derived"),
    "g_work_share": ("Share of Gemini conversation volume classified as work (%)", "Google ATLAS v1.0 (Apr 2026)"),
    "g_intensity_q": ("Per-capita Gemini adoption quintile (1 = very low, 5 = very high)", "Google ATLAS v1.0 (Apr 2026)"),
    "mbb_2gb_pct_gni_latest_official": ("ITU data-only mobile broadband basket (>=2 GB) price, % of monthly GNI p.c., latest official year", "ITU ICT Price Baskets (Dec 2025)"),
    "mbb_2gb_latest_year": ("Year of the preceding variable", "ITU"),
    "mbb_5gb_pct_gni_2025": ("ITU data-only mobile broadband basket (>=5 GB), % of GNI p.c., 2025", "ITU"),
    "fbb_5gb_pct_gni_latest_official": ("ITU fixed-broadband basket (5 GB), % of GNI p.c., latest official year", "ITU"),
    "fbb_5gb_latest_year": ("Year of the preceding variable", "ITU"),
    "mbb_2gb_usd_2024": ("ITU mobile broadband 2 GB basket, US$ per month, 2024", "ITU"),
    "mbb_5gb_usd_2025": ("ITU mobile broadband 5 GB basket, US$ per month, 2025", "ITU"),
    "storefront": ("Apple App Store storefront code", "Apple App Store"),
    "store_currency": ("Currency of the local App Store storefront", "Apple App Store, 27 Sep 2026"),
    "ln_gni": ("log of gni_atlas", "derived"), "ln_gni_ppp": ("log of gni_ppp", "derived"),
    "ppp_ratio": ("gni_ppp / gni_atlas (inverse of the Atlas-to-PPP income ratio, a price-level proxy)", "derived"),
    "plr_gdp": ("GDP price-level ratio: GDP p.c. current US$ / GDP p.c. PPP, in the year of gni_atlas", WB),
    "plr_gdp_year": ("Year of plr_gdp", WB),
    "in_ms": ("1 = economy appears in the Microsoft dataset", "derived"),
    "ms_country_specific": ("1 = Microsoft value is a country-specific estimate", "derived"),
}
WIN = {"aug25": "4-11 Aug 2025", "nov25": "13-20 Nov 2025", "feb26": "5-12 Feb 2026", "apr26": "Apr 2026", "may26": "May 2026"}
rows = []
for c in d.columns:
    if c in D:
        desc, src = D[c]
    elif c.endswith("_year"):
        desc, src = f"Year of {c[:-5]}", "derived"
    elif c.startswith("aui_"):
        desc, src = f"Anthropic AI Usage Index, harmonised (usage share / working-age population share), {WIN[c[4:]]}", AN
    elif c.startswith("an_n_"):
        desc, src = f"Number of sampled Claude.ai conversations, {WIN[c[5:]]}", AN
    elif c.startswith("an_ge200_"):
        desc, src = f"1 = at least 200 sampled conversations, {WIN[c[9:]]}", "derived from " + AN
    elif c.startswith("an_"):
        k, w = c[3:].rsplit("_", 1)
        desc, src = f"Share of Claude.ai conversations: {k} (%), {WIN[w]}", AN
    elif c.startswith("p_"):
        desc, src = f"Local monthly App Store price, US$ at market FX (27 Sep 2026): {c[2:]}", "Apple App Store; open.er-api.com"
    elif c.startswith("store_"):
        desc, src = f"Storefront status for {c[6:]}: local_storefront / no_local_storefront / app_not_offered", "Apple App Store"
    else:
        desc, src = "", ""
    rows.append({"variable": c, "description": desc, "source": src, "non_missing": int(d[c].notna().sum())})
pd.DataFrame(rows).to_csv(P / "data_dictionary.csv", index=False)
print("dictionary:", len(rows), "variables;", sum(1 for r in rows if not r["description"]), "undocumented")
