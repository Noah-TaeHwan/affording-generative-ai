"""
03_anthropic_country.py
Build tidy country-level files from the Anthropic Economic Index (AEI) HuggingFace dataset
(https://huggingface.co/datasets/Anthropic/EconomicIndex, repo commit 2ea58ff7..., last modified 2026-06-26).

Inputs (downloaded 2026-09-27 into data/raw/anthropic/):
  release_2026_06_26/aei_claude_ai_2026-06-26.csv                  (monthly: Apr 2026, May 2026)
  release_2026_03_24/aei_raw_claude_ai_2026-02-05_to_2026-02-12.csv
  release_2026_01_15/aei_raw_claude_ai_2025-11-13_to_2025-11-20.csv
  release_2025_09_15/aei_enriched_claude_ai_2025-08-04_to_2025-08-11.csv
  release_2025_09_15/working_age_pop_2024_country.csv  (WB SP.POP.1564.TO 2024 + Taiwan NDC; Anthropic's own input)
  release_2025_09_15/gdp_2024_country.csv              (IMF WEO NGDPD 2024; Anthropic's own input)
  release_2025_09_15/iso_country_codes.csv             (GeoNames ISO2/ISO3/name)

Outputs (data/raw/anthropic/):
  anthropic_country_latest.csv       tidy long: June-2026 release, country x month, all 'overall' metrics
                                     + SOC major-group task-mix shares (pct). All values PUBLISHED by Anthropic.
  anthropic_country_latest_wide.csv  one row per country x month, 'overall' metrics as columns (published).
  anthropic_country_panel.csv        tidy long panel of 5 windows (Aug-2025, Nov-2025, Feb-2026, Apr-2026, May-2026)
                                     for a core metric set; column value_source = 'published' | 'derived'.
  anthropic_gdp_elasticity_replication.csv   our log-log OLS of AUI on GDP per working-age capita by window.
"""
import pathlib
import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
A = ROOT / "data" / "raw" / "anthropic"

rd = lambda p: pd.read_csv(p, keep_default_na=False, na_values=[""], low_memory=False)  # keep "NA" = Namibia

iso = rd(A / "release_2025_09_15/iso_country_codes.csv")
iso2_to_iso3 = dict(zip(iso.iso_alpha_2, iso.iso_alpha_3))
iso3_to_iso2 = dict(zip(iso.iso_alpha_3, iso.iso_alpha_2))
iso3_to_name = dict(zip(iso.iso_alpha_3, iso.country_name))
pop = rd(A / "release_2025_09_15/working_age_pop_2024_country.csv").set_index("iso_alpha_3").working_age_pop
gdp = rd(A / "release_2025_09_15/gdp_2024_country.csv").set_index("iso_alpha_3").gdp_total
gdp_pwa = (gdp / pop).dropna()  # GDP per working-age (15-64) capita, USD, 2024 -- Anthropic's definition

UNITS = {"usage_pct": "percent of global Claude.ai usage", "usage_per_capita_index": "index (1 = proportional to working-age pop)",
         "ai_autonomy_mean": "1-5 scale", "ai_education_years_mean": "years", "human_education_years_mean": "years",
         "human_only_time_mean": "hours", "human_with_ai_time_mean": "minutes", "pct": "percent of the country's conversations"}
unit = lambda m: UNITS.get(m, "percent")

# --------------------------------------------------------------------------------------------
# 1. Latest release (2026-06-26): published country metrics
# --------------------------------------------------------------------------------------------
REL = "release_2026_06_26"
j = rd(A / REL / "aei_claude_ai_2026-06-26.csv")
jc = j[j.geo_level == "country"].copy()
keep = (jc.category_name == "overall") | (
    (jc.category_name == "soc_occupation") & (jc.hierarchy_level == 1) & (jc.metric_id == "pct"))
lat = jc[keep].copy()
lat["iso3"] = lat.geo_id
lat["iso2"] = lat.iso3.map(iso3_to_iso2)
lat["country"] = lat.iso3.map(iso3_to_name)
lat["release"] = REL
lat["source_id"] = "claude_ai (chat + Cowork; Free, Pro, Max)"
lat["date_window"] = lat.date_start + " to " + lat.date_end + " (end exclusive)"
lat["breakdown"] = np.where(lat.category_name == "overall", "overall", "soc_major_group")
lat["node"] = np.where(lat.category_name == "overall", "", lat.node_name)
lat["unit"] = lat.metric_id.map(unit)
lat["value_source"] = "published"
cols = ["iso3", "iso2", "country", "release", "source_id", "date_start", "date_end", "date_window",
        "breakdown", "node", "node_external_id", "metric_id", "value", "unit", "value_source"]
lat.loc[lat.breakdown == "overall", "node_external_id"] = ""
lat = lat[cols].sort_values(["date_start", "iso3", "breakdown", "node", "metric_id"])
lat.to_csv(A / "anthropic_country_latest.csv", index=False)

wide = (lat[lat.breakdown == "overall"]
        .pivot_table(index=["iso3", "iso2", "country", "release", "date_start", "date_end"], columns="metric_id",
                     values="value").reset_index())
first = ["iso3", "iso2", "country", "release", "date_start", "date_end", "usage_pct", "usage_per_capita_index"]
wide = wide[first + [c for c in wide.columns if c not in first]]
wide.to_csv(A / "anthropic_country_latest_wide.csv", index=False)

# --------------------------------------------------------------------------------------------
# 2. Panel across windows (core metrics)
# --------------------------------------------------------------------------------------------
rows = []


SPECIAL = {"not_classified": "Un-geolocated / filtered conversations (not a country)",
           "NONE": "Geo code NONE (not a country)"}


def add(iso3, rel, ds, de, metric, value, src, note=""):
    rows.append(dict(iso3=iso3, iso2=iso3_to_iso2.get(iso3), country=iso3_to_name.get(iso3, SPECIAL.get(iso3)),
                     release=rel, date_start=ds, date_end=de, metric_id=metric, value=value, value_source=src, note=note))


AUTO, AUG = ["directive", "feedback loop"], ["validation", "task iteration", "learning"]


EXCLUDE = {"release_2026_01_15": ["SYC"]}  # Jan-2026 report fn.5: Seychelles excluded (abusive traffic)
AUI_GEO_NOTE = ("harmonised AUI (derived): usage share among GEOLOCATED baseline countries / working-age-pop share "
                "among same countries; baseline = countries with >=200 sampled conv. and WB pop; excludes the "
                "'not_classified' (un-geolocated) row, which the published Sept-2025 AUI kept in the usage denominator")


def aui(counts, min_obs=200, exclude=()):
    """Harmonised AUI: (usage share / working-age-pop share), both shares computed over the baseline set of
    geolocated countries with >= min_obs sampled conversations (threshold from the Sept-2025 code,
    aei_report_v3_preprocessing_claude_ai.ipynb). Unlike that code, the un-geolocated 'not_classified' row is
    NOT counted in the usage denominator (the June-2026 release's published AUI also excludes it)."""
    c = counts[counts.index.isin(pop.index) & ~counts.index.isin(list(exclude))]
    base = c[c >= min_obs].index
    us, ps = c / c[base].sum(), pop[c.index] / pop[base].sum()
    return us / ps, set(base)


# 2a. Aug 2025 (release_2025_09_15, enriched file = published AUI, GDP, tiers, automation/augmentation)
REL = "release_2025_09_15"
e = rd(A / REL / "aei_enriched_claude_ai_2025-08-04_to_2025-08-11.csv")
ds, de = e.date_start.iloc[0], e.date_end.iloc[0]
ce = e[(e.geography == "country") & (e.facet == "country")]
for _, r in ce.iterrows():
    if r.variable == "usage_tier":
        continue
    add(r.geo_id, REL, ds, de, r.variable, r.value, "published",
        "zero rows = countries with WB population but no sampled usage (added by Anthropic)" if r.variable in ("usage_count", "usage_pct") and r.value == 0 else "")
aa = e[(e.geography == "country") & (e.facet == "collaboration_automation_augmentation")]
for _, r in aa.iterrows():
    add(r.geo_id, REL, ds, de, f"collaboration_bucket_{r.cluster_name}_pct", r.value, "published",
        "share of classifiable collaboration (excl. none/not_classified); only countries with >=200 conv.")
cnt = ce[ce.variable == "usage_count"].set_index("geo_id").value
for g in cnt.index:
    if g in pop.index:
        add(g, REL, ds, de, "meets_200_conversation_threshold", float(cnt[g] >= 200), "derived", "AEI MIN_OBSERVATIONS_COUNTRY = 200")
idx, base = aui(cnt[cnt > 0])
for g, v in idx.items():
    add(g, REL, ds, de, "aui_geo_baseline", round(v, 6), "derived", AUI_GEO_NOTE + "; = published AUI / 0.84281")

# 2b/2c. Nov 2025 and Feb 2026 raw files (ISO2 codes; AUI NOT published -> derived here)
for REL, fn in [("release_2026_01_15", "aei_raw_claude_ai_2025-11-13_to_2025-11-20.csv"),
                ("release_2026_03_24", "aei_raw_claude_ai_2026-02-05_to_2026-02-12.csv")]:
    r_ = rd(A / REL / fn)
    ds, de = r_.date_start.iloc[0], r_.date_end.iloc[0]
    cr = r_[r_.geography == "country"].copy()
    cr["iso3"] = cr.geo_id.map(lambda g: g if g in SPECIAL else iso2_to_iso3.get(g))
    unm = cr[cr.iso3.isna()].geo_id.unique()
    if len(unm):
        print(REL, "unmapped ISO2:", unm)
    cr = cr.dropna(subset=["iso3"])
    cf = cr[cr.facet == "country"]
    exc = EXCLUDE.get(REL, [])
    for _, r in cf.iterrows():
        add(r.iso3, REL, ds, de, r.variable, r.value, "published",
            "EXCLUDED by Anthropic from geographic analyses (abusive traffic)" if r.iso3 in exc else "")
    counts = cf[cf.variable == "usage_count"].set_index("iso3").value
    idx, base = aui(counts, exclude=exc)
    for g, v in idx.items():
        add(g, REL, ds, de, "aui_geo_baseline", round(v, 6), "derived", AUI_GEO_NOTE)
    for g in counts.index:
        if g in pop.index and g not in exc:
            add(g, REL, ds, de, "meets_200_conversation_threshold", float(counts[g] >= 200), "derived", "AEI threshold 200")
    uc = cr[(cr.facet == "use_case") & (cr.variable == "use_case_pct")]
    for _, r in uc.iterrows():
        if r.cluster_name in ("work", "personal", "coursework"):
            add(r.iso3, REL, ds, de, f"use_case_{r.cluster_name}_pct", r.value, "published",
                "percent of all conversations in the country (denominator includes not_classified/none)")
    col = cr[(cr.facet == "collaboration") & (cr.variable == "collaboration_count")]
    for g, x in col.groupby("iso3"):
        s = x.set_index("cluster_name").value
        a_, b_ = s.reindex(AUTO).fillna(0).sum(), s.reindex(AUG).fillna(0).sum()
        if a_ + b_ > 0 and counts.get(g, 0) >= 200 and g in pop.index and g not in exc:
            add(g, REL, ds, de, "collaboration_bucket_automation_pct", round(100 * a_ / (a_ + b_), 2), "derived",
                "directive+feedback loop over classifiable patterns (excl. none/not_classified); Anthropic definition")
            add(g, REL, ds, de, "collaboration_bucket_augmentation_pct", round(100 * b_ / (a_ + b_), 2), "derived",
                "validation+task iteration+learning over classifiable patterns; Anthropic definition")

# 2d. Apr and May 2026 (release_2026_06_26): published AUI and shares
core = ["usage_pct", "usage_per_capita_index", "use_case_work_pct", "use_case_personal_pct", "use_case_coursework_pct",
        "collaboration_bucket_automation_pct", "collaboration_bucket_augmentation_pct", "human_education_years_mean",
        "ai_autonomy_mean"]
for _, r in lat[(lat.breakdown == "overall") & (lat.metric_id.isin(core))].iterrows():
    add(r.iso3, r.release, r.date_start, r.date_end, r.metric_id, r.value, "published",
        "AUI baseline = published countries only (verified: reproduces published values within rounding)"
        if r.metric_id == "usage_per_capita_index" else "")
    if r.metric_id == "usage_per_capita_index":  # same definition as the harmonised series
        add(r.iso3, r.release, r.date_start, r.date_end, "aui_geo_baseline", r.value, "published",
            "= published usage_per_capita_index (June-2026 definition already excludes un-geolocated usage)")

panel = pd.DataFrame(rows)
panel = panel.sort_values(["iso3", "date_start", "metric_id"])
panel.to_csv(A / "anthropic_country_panel.csv", index=False)

# --------------------------------------------------------------------------------------------
# 3. Replicate AUI-GDP elasticity (log-log OLS), countries with >=200 conversations (or published)
# --------------------------------------------------------------------------------------------
def ols(x, y):
    X = np.column_stack([np.ones_like(x), x])
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ b
    n = len(y)
    s2 = res @ res / (n - 2)
    se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
    r2 = 1 - res @ res / ((y - y.mean()) @ (y - y.mean()))
    return b[1], se[1], r2, n


out = []
P = panel[panel.metric_id == "aui_geo_baseline"]
T = panel[panel.metric_id == "meets_200_conversation_threshold"]
for (rel, ds), x in P.groupby(["release", "date_start"]):
    x = x.set_index("iso3").value
    thr = T[(T.release == rel) & (T.date_start == ds)].set_index("iso3").value
    if len(thr):
        x = x[x.index.isin(thr[thr == 1].index)]
    x = x[(x > 0) & x.index.isin(gdp_pwa.index)]
    b, se, r2, n = ols(np.log(gdp_pwa[x.index].values), np.log(x.values))
    out.append(dict(release=rel, date_start=ds, n_countries=n, elasticity=round(b, 3), se=round(se, 3), r2=round(r2, 3),
                    sample="countries >=200 conv." if len(thr) else "all published countries (sample floor applied by Anthropic)",
                    gdp="IMF WEO NGDPD 2024 / WB working-age pop 2024 (Anthropic Sept-2025 inputs)"))
el = pd.DataFrame(out)
el.to_csv(A / "anthropic_gdp_elasticity_replication.csv", index=False)
print(el.to_string(index=False))
print("latest rows:", len(lat), "wide rows:", len(wide), "panel rows:", len(panel))
