# Anthropic Economic Index (AEI) — country-level data: provenance & data dictionary

Downloaded 2026-09-27 from HuggingFace dataset `Anthropic/EconomicIndex`
(https://huggingface.co/datasets/Anthropic/EconomicIndex; branch `main`, commit `2ea58ff75e4247d26810c37f10c179edc2466cac`,
lastModified 2026-06-26T23:21Z). Licence: data CC-BY 4.0, code MIT. Processing script: `code/03_anthropic_country.py`.

Note: repo commit of 2026-05-21 "Append restored per-country/country-state numeric distributions (additions-only)" modified
earlier releases after their first publication; the files here are the post-2026-05-21 versions.

## 1. Releases in the repository (as of 2026-09-27; no release after 2026-06-26)

| Release folder | Report (date) | Sample window (Claude.ai) | Geography | Product scope (as labelled in file) |
|---|---|---|---|---|
| release_2025_02_10 | 1st report (2025-02-10) | Dec 2024–Jan 2025 | none (global only) | Claude.ai Free+Pro |
| release_2025_03_27 | 2nd report (2025-03-27) | Feb–Mar 2025 | none | Claude.ai Free+Pro |
| release_2025_09_15 | 3rd "Uneven geographic and enterprise AI adoption" (2025-09-15) | 2025-08-04 to 2025-08-11 (1M conv.) | country (ISO2 raw / ISO3 enriched), US state | "Claude AI (Free and Pro)" |
| release_2026_01_15 | 4th "Economic primitives" (2026-01-15) | 2025-11-13 to 2025-11-20 (1M conv.) | country, country-state (ISO 3166-2) | file label "Claude AI (Free and Pro)"; report text says Free, Pro and Max |
| release_2026_03_24 | 5th "Learning curves" (2026-03-24) | 2026-02-05 to 2026-02-12 (1M conv.) | country, country-state | "Claude AI (Free, Pro, and Max)" |
| release_2026_06_26 | 6th "Cadences" (2026-06-26) | calendar months 2026-04-01→05-01 and 2026-05-01→06-01 (report ch.1: sampled 10 Apr–10 Jun 2026, fixed number per hour) | global, country (ISO3), subregion (ISO 3166-2) | `claude_ai` = Claude chat + Cowork, consumer Free/Pro/Max accounts (Claude.ai + desktop app) |
| labor_market_impacts | "Labor market impacts" (files added 2026-03-05) | — | none (occupation/task) | — |

1P API data (`aei_*1p_api*`) exist for 2025-09-15, 2026-01-15, 2026-03-24, 2026-06-26 but are **global only** (verified: every row
`geo_level/geography == global`). The API is not geo-coded in any release. The `claude_ai` source is described only as consumer
Free/Pro(/Max) accounts (Team/Enterprise plans are not listed in any release's scope).
Free vs. paid (Pro/Max) users are **not distinguished** in any file.

## 2. Files downloaded (this folder)

| Local path | Source path on HF | Size (bytes) |
|---|---|---|
| release_2026_06_26/aei_claude_ai_2026-06-26.csv | release_2026_06_26/data/aei_claude_ai_2026-06-26.csv | 219,174,671 |
| release_2026_03_24/aei_raw_claude_ai_2026-02-05_to_2026-02-12.csv | release_2026_03_24/data/… | 103,287,181 |
| release_2026_01_15/aei_raw_claude_ai_2025-11-13_to_2025-11-20.csv | release_2026_01_15/data/intermediate/… | 94,086,309 |
| release_2026_01_15/aei_v4_appendix.pdf | release_2026_01_15/aei_v4_appendix.pdf | 6,036,245 |
| release_2025_09_15/aei_enriched_claude_ai_2025-08-04_to_2025-08-11.csv | release_2025_09_15/data/output/… | 26,840,881 |
| release_2025_09_15/aei_raw_claude_ai_2025-08-04_to_2025-08-11.csv | release_2025_09_15/data/intermediate/… | 18,894,517 |
| release_2025_09_15/working_age_pop_2024_country.csv, gdp_2024_country.csv, iso_country_codes.csv | …/data/intermediate/ | small |
| release_2025_09_15/*.py, *.ipynb | …/code/ (AUI, GDP merge, thresholds, exclusions) | small |
| docs/*.md | README.md and each release's data_documentation.md | small |
| reports/*.pdf (+ .txt via pdftotext) | report PDFs & appendices linked from anthropic.com report pages | — |
| hf_api_dataset.json, hf_tree.json | HF API listing (file list, sizes, commit) | — |
| anthropic_supported_countries_2026-09-27.json | parsed https://www.anthropic.com/supported-countries | — |

## 3. Key definitions

**Anthropic AI Usage Index (AUI)** (`usage_per_capita_index`): for geography *i*,
AUI_i = (share of Claude.ai usage in *i*) / (share of working-age population, ages 15–64, in *i*).
AUI = 1 → usage proportional to working-age population; >1 over-, <1 under-represented. Population: World Bank
`SP.POP.1564.TO`, 2024 (Taiwan from R.O.C. NDC projections); GDP: IMF WEO `NGDPD` 2024 (Sept-2025 inputs). June-2026 report fn.6
states GDP per working-age adult now uses IMF WEO 2025 estimates with WB WDI (2024)/UN WPP (2024) population.

Baseline (denominators) — verified from code and data:
* Sept-2025 (published in enriched file): shares computed over countries with ≥200 sampled conversations
  (`MIN_OBSERVATIONS_COUNTRY = 200`; US states ≥100). **Quirk:** the un-geolocated `not_classified` row (150,999 conv.,
  15.66%) passes the ≥200 filter and is included in the usage denominator but has no population, so all published
  Aug-2025 AUIs are uniformly scaled by 0.84281 (verified: published/recomputed ratio = 0.84281 for every country).
* June-2026 (published): shares computed over the set of **published countries only** (un-geolocated usage excluded).
  Verified: recomputing with WB 2024 working-age pop reproduces published AUI (median ratio 1.000, IQR 0.987–1.013; rounding).
* Nov-2025 and Feb-2026: AUI **not published** in the raw files; `aui_geo_baseline` in the panel is derived by us
  (baseline = geolocated countries with ≥200 conv.; Seychelles excluded in Nov-2025 per the Jan-2026 report fn.5).
* Level comparisons across releases should use `aui_geo_baseline` (harmonised), not the raw published Aug-2025 values.

**usage_pct**: % of all sampled Claude.ai conversations in the window (denominator includes un-geolocated conversations).
Un-geolocated share (`not_classified`): 15.66% (Aug-2025), 15.66% (Nov-2025), 18.16% (Feb-2026, plus 0.23% `NONE`).
June-2026 published countries sum to 82.03% (Apr) and 87.49% (May) of usage; the remainder is un-geolocated or below the
(undisclosed) geography sample floor.

**Geolocation**: from the conversation's IP address (ISO-3166-1; subregions ISO-3166-2); conversations from VPN, anycast or
hosting services are excluded (Sept-2025 report fn.2). Unit of observation = conversation, not user.

**Thresholds / privacy**: cells need ≥15 conversations and ≥5 unique accounts (request clusters: ≥500 conv., ≥250 accounts).
Country analyses/figures use countries with ≥200 sampled conversations. June-2026: a cell is published only if it meets the
aggregation thresholds *and* a "geography sample floor" (value not disclosed); a missing row = not published, not zero.

**Exclusions**: (i) Countries where Claude is not offered — AEI Sept-2025 code list (23, ISO2): AF, BY, CD, CF, CN, CU, ER, ET,
HK, IR, KP, LY, ML, MM, MO, NI, RU, SD, SO, SS, SY, VE, YE; plus Ukrainian regions Crimea, Donetsk, Kherson, Luhansk,
Zaporizhzhia. The official supported-regions page (accessed 2026-09-27; 185 entries, identical for API and Claude.ai) no longer
omits CD, CF, ER, ET, LY, ML, NI, SD, SO, SS; WB economies absent from it: AFG, BLR, CHN, CUB, HKG, IRN, MAC, MMR, PRK, RUS, SYR,
VEN, YEM, XKX and 20 territories (e.g. PRI, GUM, BMU, CYM). (ii) Seychelles excluded from Jan-2026 geographic analyses
(24,715 conv. = 2.47% of the Nov-2025 sample; abusive traffic); Wyoming excluded from US-state analyses (Jan-2026).

## 4. Metrics per country

| Release | Country metrics published |
|---|---|
| 2025-09-15 (raw) | usage_count, usage_pct; onet_task, request, collaboration (count, pct) + intersections |
| 2025-09-15 (enriched) | + usage_per_capita, usage_per_capita_index (AUI), usage_tier (0 = Minimal; 1–4 quartiles on ≥200-conv. countries), working_age_pop, gdp_per_working_age_capita, *_pct_index (specialisation), soc_pct, automation/augmentation pct |
| 2026-01-15, 2026-03-24 (raw) | usage_count, usage_pct; onet_task, request, collaboration, use_case (work/personal/coursework), multitasking, human_only_ability, task_success (count, pct); numeric: human_only_time, human_with_ai_time, ai_autonomy, human_education_years, ai_education_years (mean, median, sd, CIs, histogram); intersections |
| 2026-06-26 | `overall`: 52 metrics = usage_pct, usage_per_capita_index, use_case_{work,personal,coursework}_pct, collaboration_{directive,feedback_loop,task_iteration,learning,validation,none}_pct, collaboration_bucket_{automation,augmentation}_pct, multitasking_pct, human_only_ability_pct, ai_autonomy_mean (1–5), ai/human_education_years_mean, human_only_time_mean (hours), human_with_ai_time_mean (minutes), 32 artifact_*_pct. By O*NET task/DWA/IWA, request (3 levels), SOC detailed occupation: `pct` only; GWA / request-Major / SOC-major-group: all metrics. **No usage_count.** |

Collaboration buckets (Anthropic definition): automation = directive + feedback loop; augmentation = validation + task
iteration + learning; shares of classifiable conversations (excluding `none`, `not_classified`).

## 5. Output files built here

### anthropic_country_latest.csv (16,236 rows; all values published by Anthropic)
Release 2026-06-26, `claude_ai` source, country level, both months. Rows = `overall` metrics (52 × 235 country-months) +
SOC major-group task-mix shares (`breakdown = soc_major_group`, `metric_id = pct`).

| Column | Description |
|---|---|
| iso3 / iso2 / country | ISO 3166-1 alpha-3 (as published), alpha-2 and GeoNames name (Anthropic's own mapping file) |
| release | `release_2026_06_26` |
| source_id | `claude_ai (chat + Cowork; Free, Pro, Max)` |
| date_start, date_end, date_window | calendar month; date_end exclusive |
| breakdown | `overall` or `soc_major_group` |
| node, node_external_id | SOC major group name / SOC code (blank for overall) |
| metric_id | Anthropic metric name (see §4) |
| value | published value (rounded to 2 d.p. by Anthropic) |
| unit | percent / index / 1-5 scale / years / hours / minutes |
| value_source | `published` |

Coverage: 114 countries (Apr-2026), 121 (May-2026; adds BWA, COG, HTI, MOZ, NAM, TGO, TTO).

### anthropic_country_latest_wide.csv
One row per country × month (235 rows), the 52 `overall` metrics as columns.

### anthropic_country_panel.csv (long; value_source = published | derived)
Windows: 2025-08-04/11, 2025-11-13/20, 2026-02-05/12, 2026-04 (month), 2026-05 (month). Metrics: usage_count (Aug/Nov/Feb
only), usage_pct, usage_per_capita_index (published: Aug-2025, Apr/May-2026), `aui_geo_baseline` (harmonised AUI; derived for
Aug/Nov/Feb, equal to published for Apr/May), meets_200_conversation_threshold (derived), use_case_*_pct (published; Nov, Feb,
Apr, May), collaboration_bucket_*_pct (published Aug/Apr/May; derived Nov/Feb), gdp_per_working_age_capita, working_age_pop,
usage_per_capita (Aug only), human_education_years_mean, ai_autonomy_mean (Apr/May). Rows with iso3 = `not_classified`/`NONE`
are un-geolocated traffic, not countries. Column `note` explains derivations.

### anthropic_gdp_elasticity_replication.csv (our replication)
OLS of ln(AUI) on ln(GDP per working-age capita, IMF 2024 / WB 2024 pop), countries ≥200 conv. (Apr/May: all published):

| Window | N | β | s.e. | R² |
|---|---|---|---|---|
| Aug 2025 | 114 | 0.690 | 0.042 | 0.709 (= published Fig. 2.4: β = 0.690, R² = 0.709) |
| Nov 2025 | 115 | 0.700 | 0.037 | 0.755 (report: "0.7%") |
| Feb 2026 | 115 | 0.762 | 0.036 | 0.799 (not reported by Anthropic) |
| Apr 2026 | 113 | 0.779 | 0.032 | 0.840 (not reported) |
| May 2026 | 120 | 0.754 | 0.030 | 0.845 (not reported) |

## 6. Reported findings on income (verbatim or near-verbatim, with source)
* Sept-2025 report: "a 1% increase in GDP per capita being associated with a 0.7% increase in Claude usage per capita"
  (Fig. 2.4: "Power law: AUI ~ GDP^0.69", β = 0.690 (p < 0.001), R² = 0.709; countries ≥200 obs.). AUI: Israel 7.0,
  Singapore 4.57, Australia 4.10, New Zealand 4.05, South Korea 3.73, US 3.62, Canada 2.91, UK 2.67, France 1.94, Japan 1.86,
  Germany 1.84, Bolivia 0.48, Indonesia 0.36, India 0.27, Nigeria 0.2. US = 21.6% of usage.
* Jan-2026 report: "A 1% increase in GDP per capita is associated with a 0.7% increase in Claude usage per capita at the
  country level"; global concentration "essentially unchanged" Aug→Nov 2025; "no evidence that low-use countries are catching
  up"; coursework share highest in lowest-GDP countries; "Countries differ in their ability to pay for Claude, and coursework
  use cases may be better suited to free Claude usage".
* Mar-2026 report: country AUI Gini 0.48 (Aug-2025) → 0.46 (Nov-2025) → 0.50 (Feb-2026); top-20 countries' share of
  population-adjusted usage 45% → 48%; "Low adoption countries fell slightly further behind." (US-state Gini 0.37 → 0.31 → 0.29.)
* Jun-2026 report: no updated AUI–GDP elasticity; survey finds perceived current AI task coverage ~10 pp lower in
  high-income countries; weekend shift to personal use "biggest for high-income countries".
