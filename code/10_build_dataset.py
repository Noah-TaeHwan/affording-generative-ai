"""
10_build_dataset.py
Assemble the country-level analysis dataset (one row per World Bank economy).

Inputs (data/raw):
  wb/country_metadata.csv, wb/wb_indicators_long.csv      World Bank API (FY2027 classification; WDI; Findex 2025)
  ms_repo/data/AI_Diffusion_Q22026_Update.csv            Microsoft AI Economy Institute, AI User Share H1-2025..Q2-2026
  anthropic/anthropic_country_panel.csv                   Anthropic Economic Index, country AUI (harmonised)
  google_atlas/atlas_v1_geography_intensity.csv           Google ATLAS v1.0 (Apr 2026)
  itu/itu_affordability_latest.csv                        ITU ICT Price Baskets (Dec 2025 release)
Output:
  data/processed/country_panel.csv  and  data/processed/data_dictionary.csv
"""
import pathlib
import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW, PROC = ROOT / "data" / "raw", ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- World Bank
cm = pd.read_csv(RAW / "wb" / "country_metadata.csv", keep_default_na=False)
cm = cm[cm.region_id != "NA"].copy()          # drop aggregates
cm["income_group"] = cm["income_group_current"].replace({"Upper middle income": "Upper-middle income",
                                                          "Lower middle income": "Lower-middle income"})
ORDER = ["High income", "Upper-middle income", "Lower-middle income", "Low income"]
wb = pd.read_csv(RAW / "wb" / "wb_indicators_long.csv")
wb = wb[wb.iso3.isin(cm.iso3) & wb.value.notna()]


def latest(code, maxyear=2025, minyear=2010):
    d = wb[(wb.indicator == code) & wb.year.between(minyear, maxyear)].sort_values("year")
    d = d.groupby("iso3").tail(1)[["iso3", "value", "year"]]
    return d.set_index("iso3")


def year(code, y):
    d = wb[(wb.indicator == code) & (wb.year == y)][["iso3", "value"]]
    return d.set_index("iso3")["value"]


df = cm[["iso3", "iso2", "country_wb", "region", "income_group", "lending"]].set_index("iso3")
# income denominators
g25 = latest("NY.GNP.PCAP.CD", 2025, 2022)
df["gni_atlas"] = g25["value"]; df["gni_atlas_year"] = g25["year"]
p25 = latest("NY.GNP.PCAP.PP.CD", 2025, 2022)
df["gni_ppp"] = p25["value"]; df["gni_ppp_year"] = p25["year"]
# GDP price-level ratio (PPP conversion factor / market exchange rate) = GDP p.c. in US$ / GDP p.c. in PPP $, taken in
# the year of GNI per capita (Atlas) so that it is comparable with the Atlas/PPP GNI ratio
gdpw = wb[wb.indicator.isin(["NY.GDP.PCAP.CD", "NY.GDP.PCAP.PP.CD"])].pivot_table(
    index=["iso3", "year"], columns="indicator", values="value").dropna()
gyr = df["gni_atlas_year"].dropna().astype(int)
gg = gdpw.loc[[k for k in zip(gyr.index, gyr.values) if k in gdpw.index]]
df["plr_gdp"] = pd.Series({i: r["NY.GDP.PCAP.CD"] / r["NY.GDP.PCAP.PP.CD"] for (i, y), r in gg.iterrows()})
df["plr_gdp_year"] = pd.Series({i: y for (i, y) in gg.index})
df["gni_atlas_2022"] = year("NY.GNP.PCAP.CD", 2022)
df["gni_ppp_2022"] = year("NY.GNP.PCAP.PP.CD", 2022)
pop = latest("SP.POP.TOTL", 2025, 2020)
df["pop"] = pop["value"]
df["pop1564"] = latest("SP.POP.1564.TO", 2025, 2020)["value"]
hf = wb[wb.indicator == "NE.CON.PRVT.CD"].merge(
    wb[wb.indicator == "SP.POP.TOTL"][["iso3", "year", "value"]], on=["iso3", "year"], suffixes=("", "_pop"))
hf = hf[hf.year.between(2022, 2025)].sort_values("year").groupby("iso3").tail(1)
df["hfce_pc"] = (hf.set_index("iso3")["value"] / hf.set_index("iso3")["value_pop"])
df["hfce_pc_year"] = hf.set_index("iso3")["year"]
# distribution (quintile shares, latest survey since 2010)
for code, nm in [("SI.DST.FRST.20", "q1_share"), ("SI.DST.02ND.20", "q2_share"), ("SI.DST.03RD.20", "q3_share"),
                 ("SI.DST.04TH.20", "q4_share"), ("SI.DST.05TH.20", "q5_share"), ("SI.POV.GINI", "gini")]:
    l = latest(code, 2025, 2010)
    df[nm] = l["value"]
    if nm == "q1_share":
        df["dist_year"] = l["year"]
# complements / controls
for code, nm, miny in [("IT.NET.USER.ZS", "internet_pct", 2018), ("EG.ELC.ACCS.ZS", "electricity_pct", 2018),
                       ("IT.NET.BBND.P2", "fixed_bb_per100", 2018), ("SE.TER.ENRR", "tertiary_enrol", 2012),
                       ("SP.URB.TOTL.IN.ZS", "urban_pct", 2018), ("SP.POP.65UP.TO.ZS", "age65_pct", 2018),
                       ("SL.EMP.WORK.ZS", "wage_emp_pct", 2015), ("SL.SRV.EMPL.ZS", "services_emp_pct", 2015)]:
    l = latest(code, 2025, miny)
    df[nm] = l["value"]; df[nm + "_year"] = l["year"]
# Global Findex 2025 (survey year 2024; fall back to 2021 wave)
for code, nm in [("account.t.d", "fx_account"), ("fin10", "fx_credit_card"), ("fin2.t.d", "fx_debit_card"),
                 ("fin27a", "fx_online_merchant_pay"), ("g20.made", "fx_made_digital_pay"),
                 ("con9a", "fx_smartphone"), ("Internet", "fx_internet_access")]:
    l = latest(code, 2025, 2021)
    df[nm] = l["value"]; df[nm + "_year"] = l["year"]

# ---------------------------------------------------------------- Microsoft AI diffusion
ms = pd.read_csv(RAW / "ms_repo" / "data" / "AI_Diffusion_Q22026_Update.csv", encoding="mac_roman")
ms.columns = ["economy", "ms_h1_2025", "ms_h2_2025", "ms_q1_2026", "ms_q2_2026"]
for c in ms.columns[1:]:
    ms[c] = ms[c].astype(str).str.replace("%", "").astype(float)
MAP = {"South Korea": "KOR", "Czech Republic": "CZE", "Vietnam": "VNM", "Slovakia": "SVK", "Türkiye": "TUR",
       "Egypt": "EGY", "Iran": "IRN", "Gambia": "GMB", "Venezuela": "VEN", "Kyrgyzstan": "KGZ", "Russia": "RUS",
       "Congo": "COG", "Congo (DRC)": "COD", "Laos": "LAO", "Somalia": "SOM", "Syria": "SYR",
       "Taiwan": "TWN", "French Guiana": "GUF"}
name2iso = {n.lower(): i for n, i in zip(cm.country_wb, cm.iso3)}
ms["iso3"] = [MAP.get(e, name2iso.get(e.lower())) for e in ms.economy]
assert ms.iso3.notna().all(), ms[ms.iso3.isna()]
# Region-imputed economies: Microsoft pools economies with insufficient telemetry into regional aggregates
# (Misra et al. 2025, Sec. 2.4 and Appendix Table 2, marked with a dagger). They are identifiable as groups of
# economies sharing an identical four-period series; the 36 economies found this way coincide with the dagger list.
key = ms[["ms_h1_2025", "ms_h2_2025", "ms_q1_2026", "ms_q2_2026"]].round(2).astype(str).agg("|".join, axis=1)
sizes = key.map(key.value_counts())
ms["ms_region_imputed"] = (sizes > 1).astype(int)
ms["ms_impute_cluster"] = np.where(sizes > 1, key, "")
ms_iso = ms.set_index("iso3")
df = df.join(ms_iso[["economy", "ms_h1_2025", "ms_h2_2025", "ms_q1_2026", "ms_q2_2026",
                     "ms_region_imputed", "ms_impute_cluster"]], how="left")
df.rename(columns={"economy": "ms_economy_name"}, inplace=True)
missing_ms = sorted(set(ms.iso3) - set(df.index))
print("Microsoft economies not in WB list (dropped):", missing_ms)

# ---------------------------------------------------------------- Anthropic AUI
an = pd.read_csv(RAW / "anthropic" / "anthropic_country_panel.csv")
an = an[an.iso3.isin(df.index)]
WIN = {"2025-08-04": "aug25", "2025-11-13": "nov25", "2026-02-05": "feb26", "2026-04-01": "apr26", "2026-05-01": "may26"}
an["win"] = an.date_start.map(WIN)
for metric, nm in [("aui_geo_baseline", "aui"), ("usage_count", "an_n"), ("use_case_coursework_pct", "an_coursework"),
                   ("use_case_work_pct", "an_work"), ("collaboration_bucket_automation_pct", "an_automation")]:
    w = an[an.metric_id == metric].pivot_table(index="iso3", columns="win", values="value", aggfunc="first")
    w.columns = [f"{nm}_{c}" for c in w.columns]
    df = df.join(w, how="left")
thr = an[an.metric_id == "meets_200_conversation_threshold"].pivot_table(index="iso3", columns="win", values="value",
                                                                          aggfunc="first")
thr.columns = [f"an_ge200_{c}" for c in thr.columns]
df = df.join(thr, how="left")

# ---------------------------------------------------------------- Google ATLAS v1.0 (April 2026)
ga = pd.read_csv(RAW / "google_atlas" / "atlas_v1_geography_intensity.csv", keep_default_na=False, na_values=[""])
ga = ga[ga.geo_level == "country"][["geo_id", "work_share_pct", "intensity_quintile"]]
ga = ga.merge(cm[["iso2", "iso3"]], left_on="geo_id", right_on="iso2", how="inner").set_index("iso3")
df = df.join(ga[["work_share_pct", "intensity_quintile"]].rename(
    columns={"work_share_pct": "g_work_share", "intensity_quintile": "g_intensity_q"}), how="left")

# ---------------------------------------------------------------- ITU ICT price baskets
itu = pd.read_csv(RAW / "itu" / "itu_affordability_latest.csv").set_index("iso3")
df = df.join(itu[["mbb_2gb_pct_gni_latest_official", "mbb_2gb_latest_year", "mbb_5gb_pct_gni_2025",
                  "fbb_5gb_pct_gni_latest_official", "fbb_5gb_latest_year", "mbb_2gb_usd_2024",
                  "mbb_5gb_usd_2025"]], how="left")

# ---------------------------------------------------------------- App Store local prices (from 09_appstore_prices.py)
pp = PROC / "appstore_prices_wide.csv"
if pp.exists():
    pr = pd.read_csv(pp, keep_default_na=False, na_values=[""]).set_index("iso3")
    df = df.join(pr, how="left")

# ---------------------------------------------------------------- derived
df["income_group"] = pd.Categorical(df["income_group"], categories=ORDER, ordered=True)
df["ln_gni"] = np.log(df.gni_atlas)
df["ln_gni_ppp"] = np.log(df.gni_ppp)
df["ppp_ratio"] = df.gni_ppp / df.gni_atlas            # >1: local prices below US level (Balassa-Samuelson)
df["in_ms"] = df.ms_q2_2026.notna().astype(int)
df["ms_country_specific"] = ((df.in_ms == 1) & (df.ms_region_imputed == 0)).astype(int)
df.reset_index().to_csv(PROC / "country_panel.csv", index=False)
print("rows:", len(df), "| in Microsoft:", int(df.in_ms.sum()), "| country-specific MS:",
      int(df.ms_country_specific.sum()), "| with AUI May-26:", int(df["aui_may26"].notna().sum()))
print(df.groupby("income_group", observed=True).agg(n=("gni_atlas", "size"), n_ms=("in_ms", "sum"),
                                                    n_ms_cs=("ms_country_specific", "sum")))
