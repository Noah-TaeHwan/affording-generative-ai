# Replication package — *Localised Entry, Global Frontier: How Generative-AI Subscriptions Are Priced Across Countries*

TaeHwan Oh (independent researcher; ORCID https://orcid.org/0009-0004-4111-4802) · package version 3.1 · 17 October 2026 ·
DOI https://doi.org/10.5281/zenodo.23006365 (all versions of the record; version 3.1, https://doi.org/10.5281/zenodo.23428432, accompanies the revised manuscript together with the two page archives `appstore_wave2_page_archive_2026-10-16.zip` and `cross_channel_page_archive_2026-10-16.zip`; versions 2.1, 2.0 and 1.8 of the record belong to earlier versions of the paper; the working-paper version circulated under the title *Affording Generative AI Across Countries: Uniform Prices, Unequal Burdens*)

This package reproduces every table, figure and in-text number of the English manuscript (version 3.1). The Korean edition of
version 3.1 follows later: `paper_ko/` now holds only the Korean table bodies written by `code/40_tables_tex.py`, and the
version 2.1 Korean edition is in the version 2.1 record. The package follows the structure of the Social Science Data Editors' README template
(https://social-science-data-editors.github.io/template_README/). The changes since version 1.8 are listed at the end.

## How to cite

- Oh, TaeHwan (2026). *Replication package for "Localised Entry, Global Frontier: How Generative-AI Subscriptions Are Priced
  Across Countries"*, version 3.1 [data and code]. Zenodo. https://doi.org/10.5281/zenodo.23006365 (all versions; version 3.1:
  https://doi.org/10.5281/zenodo.23428432)
- Oh, TaeHwan (2026). *Localised Entry, Global Frontier: How Generative-AI Subscriptions Are Priced Across Countries.* Manuscript,
  version 3.1, October 2026. An earlier version circulated as SSRN working paper 7535900 (29 September 2026) under the title
  *Affording Generative AI Across Countries: Uniform Prices, Unequal Burdens*.

## Overview

The code (i) downloads World Bank indicators and third-party usage datasets, (ii) scrapes local App Store prices in every
storefront in two waves — ChatGPT, Claude and Gemini on 27 September 2026, and 34 apps on 16 October 2026 (the second audit),
together with a panel of 30 small-developer apps whose prices are used to estimate Apple's automatic (default) price schedule —
and, on the same day as the second wave, the Google Play in-app price ranges of 12 apps in 30 countries and Microsoft's web-store
prices in 57 countries (frozen extracts in `data/raw/web/`), (iii) builds a country-level panel (`data/processed/country_panel.csv`)
and the item-level files of the second wave, (iv) runs the analysis (`output/results.json`, `output/results_wave2.json`,
`output/tables/*.csv`): the within-firm, within-storefront relative prices (pairs, stacked fixed-effect regressions with
randomisation inference, cross-vendor references), the deviation of each plan from the estimated schedule, the validation of the
schedule (split-half, leave-one-app-out, strict and subscription-only rules, exact coincidence), the vintage test against historical
exchange rates (`data/raw/fx_hist/`), the within-storefront increment test, the tax-absorption check and the cross-channel
comparison, (v) draws the figures, (vi) writes LaTeX table bodies, and (vii) runs the additional analyses — currency-clustered
inference, the within-storefront Go/Plus comparison, plan-matching checks, benchmark and income-vintage sensitivities, the
descriptive ChatGPT Go rollout comparison (Appendix F), the price-schedule counterfactuals (Table E.7), numerical checks of the
model of Appendix A (`checks/verify_tier_model.py`, `checks/sim_check.py`), and an audit of every number printed in the prose
(1,952 checks). From the shipped raw extracts, steps (iii)–(vii) run in a little over two minutes (`bash run_all.sh`; the 300 split-half draws of `code/14_default_validation.py` take about 70 s of that); `bash build_papers.sh`
then compiles the manuscript.

## Data availability and provenance statements

All data are publicly available. The author has legitimate access to all data used in this manuscript and the package includes
the inputs used by `run_all.sh`, including derived Anthropic and ITU country files. The large Anthropic release files
(approximately 450 MB) and the ITU workbook are not bundled. `code/00_download_sources.sh` retrieves the Anthropic files at the
pinned commit and the ITU workbook from the dated provider URL so that the country-level extractions can also be rebuilt. A dated
provider URL is not an immutable version guarantee.

| Source | Provider / URL | Version used | Licence | Files in package |
|---|---|---|---|---|
| World Development Indicators; Global Findex 2025; country classification FY2027 | World Bank API `api.worldbank.org/v2` | extracted 27 Sep 2026 (WDI last updated 13 Jul 2026) | CC BY 4.0 | `data/raw/wb/` |
| AI Diffusion dataset (AI User Share H1 2025–Q2 2026) and reports | Microsoft AI Economy Institute, `github.com/microsoft/ai-diffusion-report` | commit 507c316 (20 Sep 2026) | MIT | `data/raw/ms_repo/data/AI_Diffusion_Q22026_Update.csv`; copy in `extensions/microsoft_pinned.csv` |
| Technical paper (region-imputed flags) | Misra et al. (2025), arXiv:2511.02781 | v1 | arXiv | cited; flags reproduced in code |
| Anthropic Economic Index, country level | `huggingface.co/datasets/Anthropic/EconomicIndex` | commit 2ea58ff (26 Jun 2026) | data CC-BY, code MIT | derived: `data/raw/anthropic/anthropic_country_*.csv`; raw via script |
| Google AI & Economy ATLAS v1.0 | `ai.google/economy/atlas` | April 2026 sample, published 23 Jul 2026 | see provider | `data/raw/google_atlas/` |
| ITU ICT Price Baskets 2008–2025 | ITU, `itu.int/en/ITU-D/Statistics/Pages/ICTprices` | December 2025 release | ITU terms (attribution) | derived CSVs; workbook via script |
| App Store in-app purchase prices | Apple App Store product pages (`apps.apple.com/<cc>/app/id<app>`) | scraped 27 Sep 2026 (UTC) | public web pages; factual data | `data/raw/appstore/appstore_iap_raw.jsonl` |
| App Store in-app purchase prices, second wave: 34 apps (AI and non-AI subscriptions) × 218 storefront codes, and a 30-app small-developer panel × 167 storefronts | Apple App Store product pages (`apps.apple.com/<cc>/app/id<app>`) | scraped 16 Oct 2026 (UTC); the in-app purchase list is served as HTML, no longer as embedded JSON | public web pages; factual data | `data/raw/appstore_wave2/` (JSONL, app lists, `README.md`); gzipped page archive deposited separately as `appstore_wave2_page_archive_2026-10-16.zip` (109 MB) |
| Exchange rates | open.er-api.com (ExchangeRate-API, attribution required); cross-check: fawazahmed0 currency-api | 27 Sep 2026 (wave 1); 16 Oct 2026 and 15 Oct 2026 (wave 2) | provider terms | `data/raw/fx/`, `data/raw/appstore_wave2/fx/` |
| Historical exchange rates (vintage test, Section 5.3) | fawazahmed0 currency-api snapshots of 6 Mar 2024, 15 Oct 2024, 15 Apr 2025, 15 Oct 2025, 15 Apr 2026 and 15 Oct 2026 | retrieved 16 Oct 2026 | provider terms (CC0) | `data/raw/fx_hist/` (with `README.md` and SHA-256) |
| Google Play in-app price ranges, 12 apps × 30 countries; Microsoft 365 web-store prices, 63 locales in 57 countries (Appendix C) | Google Play product pages (`play.google.com/store/apps/details?id=<pkg>&gl=<cc>`); Microsoft Store compare page (`microsoft.com/<locale>/microsoft-365/buy/compare-all-microsoft-365-products`) | retrieved 16 Oct 2026 (UTC); each row carries the SHA-256 of its page; the page archive is deposited separately as `cross_channel_page_archive_2026-10-16.zip` (487 files, 77 MB) | public web pages; factual data | `data/raw/web/` (with `README.md`) |
| OpenAI tariff change of 29 Sep 2026 (Section 2.1, Appendix G) | OpenAI Help Center pages cited in the manuscript | retrieved 29–30 Sep 2026 | provider terms | `extensions/pricing_sources/` (manifest and capture record; the \$500 fee is the only number used) |

Notes. (1) The App Store scrape and exchange rates are point-in-time snapshots; re-running `02_scrape_appstore_prices.py` today
will give different prices. The wave-1 archive stores the parsed listing records, not the original HTML (Appendix B). (2) Microsoft
pools 36 economies into regional aggregates; `10_build_dataset.py` flags them (`ms_region_imputed`). (3) Anthropic's August-2025
published AUI includes un-geolocated traffic in the denominator; `03_anthropic_country.py` builds a harmonised index
(`aui_geo_baseline`). (4) Namibia's ISO2 code is the string `NA`, which pandas reads as missing by default; every script therefore
reads CSV files with `keep_default_na=False, na_values=[""]`. (5) The World Bank API no longer serves `PA.NUS.PPPC.RF`; the GDP
price-level ratio is computed as `NY.GDP.PCAP.CD / NY.GDP.PCAP.PP.CD` in the year of the GNI data (`plr_gdp`). (6) The second price wave
(16 Oct 2026) stores the parsed records as in wave 1, plus the SHA-256 of each page as received (`sha256`); the gzipped pages
themselves are deposited with the record of version 3.1 as `appstore_wave2_page_archive_2026-10-16.zip` (12,860 files for the
12,225 pages with HTTP 200, 109 MB), and `sha256` is the link between a record and its page (`data/raw/appstore_wave2/README.md`).

## Computational requirements

- Tested with Python 3.11.15, pandas 3.0.2, numpy 2.4.4, statsmodels 0.15.0, scipy 1.17.1, matplotlib 3.10.9, requests 2.33.1,
  openpyxl 3.1.5. Install with `pip install -r requirements.txt` (`extensions/requirements_revision.txt` and
  `checks/requirements.txt` list the same libraries for the version 2.0 scripts).
- Fonts for figures: Liberation Sans (English labels) and NanumGothic (Korean labels; Debian/Ubuntu package `fonts-nanum`).
  Where they are missing the scripts fall back to Arial/AppleGothic or DejaVu Sans; the figures then look slightly different
  and are not byte-identical to the shipped files.
- Platforms: on other operating systems the CSV outputs can differ in the last printed digit (floating-point formatting);
  `output/results.json` and the LaTeX tables, which are rounded, are unaffected.
- LaTeX (TeX Live 2023): `pdflatex` + `bibtex` (English; packages geometry, mathptmx, amsmath/amsthm, booktabs, threeparttable,
  tabularx, multirow, natbib, tikz, enumitem, hyperref, xurl); `xelatex` + `bibtex` with `xetexko` (Korean edition, built only when `paper_ko/main.tex` is present; version 3.0 and version 3.1 ship the English
  manuscript only), using the system fonts Liberation Serif/Sans/Mono and Noto Serif/Sans CJK KR. The English bibliography style `paper_en/apalike-doi.bst` is
  shipped. `build_papers.sh` fixes `SOURCE_DATE_EPOCH` so that rebuilds are byte-identical.
- Randomness: the bootstrap in `20_analysis.py` (2,000 draws, seed 20260927) and the currency-block resampling in
  `checks/price_reliability.py` (19,999 draws, seed 20260930).
- Runtime: downloads ≈ 10–20 min (App Store scrape: 654 requests; second wave: 12,422 requests, about 2 h); analysis ≈ 20 s plus ≈ 10 s for the wave-2 steps; manuscripts ≈ 1 min.

## Package contents

Included: all programs; every raw extract that `run_all.sh` reads; the derived Anthropic and ITU country files; processed data;
results, tables and figures; LaTeX sources, `.bbl` files and compiled PDFs of the English manuscript (identified and anonymised
copies, separate title page); the Korean table bodies; the verification record. The submission files
(`submission/`, generated by `code/53_flatten_submission.py`) are distributed separately and are not part of the deposited package.
Not included (re-downloadable at pinned versions with `code/00_download_sources.sh`): the Anthropic release CSVs (≈450 MB), the
ITU workbook, and Microsoft's report PDFs and repository history.

| Folder | Contents |
|---|---|
| `code/`, `run_all.sh`, `run_revision.sh`, `build_papers.sh`, `check_release.sh` | Pipeline (see *Description of programs*) |
| `data/raw/`, `data/processed/` | Frozen source extracts (including `data/raw/openai/chatgpt_go_rollout.csv`, the dated rollout record with sources; `data/raw/appstore_wave2/`, the second App Store wave of 16 Oct 2026; `data/raw/web/`, the Google Play and Microsoft web-store extracts of the same day; `data/raw/fx_hist/`, six historical exchange-rate snapshots used by the vintage test); analysis panel and price files (wave 2: `data/processed/wave2_*.csv`) |
| `output/` | `results.json` (865 scalars), `results_wave2.json` (2,620 scalars of the second price wave, the estimated schedule and its checks, the relative prices and the cross-channel comparison), `tables/*.csv` (W1–W15b for the second wave), `figures/*.pdf, *.png` |
| `paper_en/` | English manuscript: `main.tex`, `titlepage.tex`, `references.bib`, `apalike-doi.bst`, `tables/`, `figures/`, `main.pdf`, `main_anon.pdf`, `titlepage.pdf`, build record |
| `paper_ko/` | The Korean table bodies written by `code/40_tables_tex.py` (`tables/`) only; the Korean edition of version 3.1 follows later, and the version 2.1 Korean edition is in the version 2.1 record |
| `extensions/` | Analyses added in versions 2.0–3.1: `audit_extensions.py` (clustered inference, sensitivities, headline re-checks), `figure_price_ratio.py` (Figure 4), `build_revision_tables.py` (Tables E.2, E.5, E.6, D.5), `go_rollout_analysis.py` (Appendix F, Table F.1; a descriptive record; the specification without region fixed effects was fixed in the script before the outcomes were computed, not externally registered; the region-fixed-effects specification, added afterwards, is the one reported first), `policy_counterfactuals.py` (Table E.7), `figure_rollout.py` (Figure F.1), and the Korean counterparts `figure_price_ratio_ko.py` and `build_revision_tables_ko.py` (run only when the Korean edition is present); outputs in `audit_output/`; `baseline_results_v1.8.json` (frozen baseline); `upstream_validation/` (provider-file re-download checks); `pricing_sources/` (tariff-change capture record); `AUDIT_REPORT.md` (audit-stage record) |
| `checks/` | Plan-matching and currency-sample checks (`price_reliability.py`), the Go/Plus table (`build_matched_menu_table.py`), numerical verification of the four-option model of Appendix A (`verify_tier_model.py`: Propositions A.1 and A.2; `sim_check.py`: Propositions A.1–A.4, the regimes of Table A.1 and the increment test, output in `results/sim_output.txt`), the access-conditions field dictionary and protocol of Appendix G |
| `verification/` | `README.md` (clean-room replication record), `prose_number_audit.py` (1,952 checks of the numbers printed in the prose), `identifying_strings.txt` (strings that must not appear in the anonymised copies) and `en_ko_number_check.py` (the Korean edition prints the same numbers as the English text; run only when the Korean edition is present) |
| `submission/` (not deposited) | Generated by `code/53_flatten_submission.py`: anonymised and identified PDFs, title page, self-contained LaTeX sources and figure files; the hand-written highlights, cover letter, declarations and checklist travel with the separate submission archive |
| `research/refs_verified.csv` | Crossref/arXiv check of bibliographic metadata |
| `README_v1_8.md` | README of the working-paper package (version history 1.1–1.8) |

### Wave 2 (16 October 2026)

A second App Store collection extends wave 1 (27 September 2026, ChatGPT, Claude and Gemini) in two directions. The core run lists
the in-app purchases of 34 apps in 218 storefront codes (7,412 requests; 7,218 pages, 5,688 of them with local prices; 30,817
storefront × app × item prices in 173 storefronts): the three core apps, five further AI apps, Microsoft 365 with Copilot, four apps with
AI features inside a general subscription and 21 non-AI subscription apps as benchmarks. The default panel lists the in-app purchases
of 30 small-developer apps, which have no pricing team of their own, in the 167 storefronts with a local ChatGPT page (5,007 pages);
the unique modal local price (share at least one half; a 50/50 tie gives no price) at a given US price is taken to be the platform's default price schedule, against which the AI plans are compared
(`code/12_default_panel.py`; the headline numbers under five tie rules — first pass, lower price, higher price, none (the rule of the package) and strict majority — are in `results_wave2.json`, keys `default_tie_<rule>_*`; `code/14_default_validation.py` validates the schedule and `code/15_vintage_test.py` tests its vintage). Version 3.1 adds three data rules to `code/09b_wave2_items.py`: Apple's product page lists at most ten in-app purchases (4,632 of 5,566 non-empty lists are full), so a monthly price recorded above three times the platform's reference for the item's US monthly price is treated as a censored list and dropped (the annual-as-monthly guard: 151 of 21,938 item × storefront cells, `output/tables/W6_annual_guard.csv`, `W6b_annual_guard_cells.csv`); items listed by the same firm under two apps or two spellings are counted once (five of 152 items, `W7_dedup.csv`); and the class-level statistics are complemented by an app-level incidence test (`W5b_applevel.csv`). Between the two waves Apple changed the page format (embedded JSON → HTML) and renamed the ChatGPT tiers
`Pro 5x`/`Pro 20x` to `Pro 100`/`Pro 200` (a `Pro 500` was added); the 1,586 plan × storefront prices present in both waves are
identical. The gzipped page archive is deposited with the record of version 3.1 (`appstore_wave2_page_archive_2026-10-16.zip`,
12,860 files, 109 MB; the SHA-256 of every page is in the package); the `sha256` field of each record links to it. `run_all.sh` rebuilds all wave-2 files from the shipped JSONL (about 90 s, 70 s of which are the split-half draws of `code/14_default_validation.py`); the scraper
`code/02b_scrape_wave2.py` is not part of it. `data/raw/appstore_wave2/README.md` documents the raw files.

| New processed file or output | Contents |
|---|---|
| `data/processed/wave2_items_long.csv` | 30,817 rows: storefront × app × item, modal monthly price, currency, US\$ at two exchange-rate sources, price of the same item in the US, ratio to it, GNI, income group |
| `data/processed/wave2_default_items_long.csv` | 22,744 rows: the same for the default-panel apps |
| `data/processed/wave2_plan_rows.csv` | 5,350 rows: plan × storefront for the AI plans (ChatGPT Go to Pro 500, Claude, Gemini, Perplexity, SuperGrok, Microsoft 365) and the benchmark items (YouTube, X, Character.AI, Telegram, Duolingo, Snapchat+, Google One) |
| `data/processed/wave2_item_slopes.csv` | 147 items listed in at least 60 storefronts after de-duplication: HC1 slope of ln(price / US price) on ln(GNI per capita), standard error, median ratios, class and type |
| `data/processed/wave2_stability.csv` | 1,586 wave-1 plan × storefront prices against wave 2 (identical if within 0.5%) |
| `data/processed/wave2_default_ladder.csv`, `wave2_default_multiplier.csv` | Apple's default schedule: unique modal local price (share at least one half) at each US price point per storefront (2,414 storefront × price-point entries, 1,551 with a price); storefront multiplier, spread and tax factor (164 storefronts, 111 with spread below 0.2) |
| `data/processed/wave2_plan_vs_default.csv` | 5,311 rows: plan × storefront, reference price from the schedule, deviation (ln) |
| `data/processed/wave2_relative_long.csv` | 3,015 plan × storefront rows of the within-firm relative-price analysis (`code/13_relative_prices.py`): local price relative to the reference plan of the same firm, net of the same ratio in the US |
| `data/processed/wave2_data_dictionary.csv` | Variable descriptions of the files above |
| `output/tables/W1_wave2_plans.csv` … `W15b_play_countries.csv` | Plans (W1), benchmark items (W2), stability (W3), deviations from the default schedule (W4), slopes by class of app (W5) and app-level incidence (W5b), the annual-as-monthly guard (W6, W6b), de-duplication (W7), within-firm relative prices (W8 pairs, W9 stacked regressions, W10 cross-vendor references), validation of the schedule (W11, W11b weak storefronts), the increment test (W12), tax absorption (W13), the vintage test (W14, W14b exchange-rate movements) and the cross-channel comparison (W15, W15b Google Play by country) |
| `output/results_wave2.json` | Every scalar of the second wave quoted in the text (2,620) |
| `paper_en/tables/tab_{wave2_plans,benchmarks,classes,stability,afford,relative_pairs,relative_stacked,cross_vendor,increment,annual_guard,tax_absorption,default_validation,weak_storefronts,vintage,cross_channel,play_countries}.tex`, `paper_en/figures/fig_{relative,default_dev,benchmarks}_en.pdf` | Table bodies and figures (programs `41_tables_wave2.py`, `42_tables_relative.py`, `31_figures_wave2.py`) |

## Licence

The code (`code/`, `extensions/*.py`, `checks/*.py`, `verification/*.py`, the shell scripts) is released under
the MIT License. Data compiled by the author — the App Store price extraction and the author's contributions to the processed
files — are released under Creative Commons Attribution 4.0 International (CC BY 4.0). Values taken from third-party sources
remain subject to the providers' licences listed above; Microsoft's MIT licence is in `data/raw/ms_repo/LICENSE.md`. The
English and Korean manuscripts (PDF and LaTeX prose) are copyright 2026 TaeHwan Oh, all rights reserved; they are not covered by
the MIT or CC BY grants. Generated tables and figures retain the terms applicable to their underlying code and data. See
`LICENSE.txt`.

## Description of programs

| Program | Purpose | Main outputs |
|---|---|---|
| `code/00_download_sources.sh` | Microsoft, Anthropic, Google ATLAS, ITU files at pinned versions | `data/raw/...` |
| `code/01_download_wb.py` | World Bank metadata, WDI and Findex indicators | `data/raw/wb/*.csv` |
| `code/02_scrape_appstore_prices.py` | App Store in-app purchase lists for 218 storefront codes × 3 apps | `data/raw/appstore/appstore_iap_raw.jsonl` |
| `code/02b_scrape_wave2.py` | Second App Store wave (not run by `run_all.sh`): 34 apps × 218 storefront codes and a 30-app default panel × 167 storefronts; reads both the JSON and the HTML page format; page archive with SHA-256 | `data/raw/appstore_wave2/core/appstore_iap_raw_wave2.jsonl`, `default_panel/appstore_iap_raw_wave2_default.jsonl` |
| `code/03_anthropic_country.py` | Country-level Anthropic panel; harmonised AUI | `data/raw/anthropic/anthropic_country_*.csv` |
| `code/05_itu_price_baskets.py` | Tidy ITU price baskets | `data/raw/itu/itu_affordability_latest.csv` |
| `code/06_verify_references.py` | Crossref/arXiv check of bibliographic metadata | `research/refs_verified.csv` |
| `code/09_appstore_prices.py` | Monthly local prices, USD conversion, storefront status | `data/processed/appstore_prices_*.csv` |
| `code/wave2_common.py` | Shared functions of the wave-2 programs: the modal monthly price of an item, the schedule rule of the default panel, HC1 and currency-clustered OLS, the income-group labels | (imported by 09b, 12–16, 31, 41, 42) |
| `code/09b_wave2_items.py` | Wave 2: item-level monthly prices, USD at two exchange-rate sources, the annual-as-monthly guard (Apple's ten-item list cap), de-duplication of items listed under two apps or spellings, plan rows, item income slopes (HC1), classes of app, app-level incidence, stability against wave 1 | `data/processed/wave2_{items_long,default_items_long,plan_rows,item_slopes,stability}.csv`, `output/tables/W{1,2,3,5,5b,6,6b,7}_*.csv`, `output/results_wave2.json` |
| `code/10_build_dataset.py` | Merge all sources | `data/processed/country_panel.csv` |
| `code/11_data_dictionary.py` | Variable descriptions | `data/processed/data_dictionary.csv` |
| `code/12_default_panel.py` | Wave 2: the platform's default price schedule estimated from the small-developer panel (ladder, multiplier, tax factor, income slope), the deviation of each plan from it with HC1, HC3, currency-clustered, non-USD and population-weighted slopes, exact and extrapolated references, and the tax-absorption check | `data/processed/wave2_default_{ladder,multiplier}.csv`, `wave2_plan_vs_default.csv`, `output/tables/W4_default_schedule.csv`, `W1_wave2_plans.csv`, `W13_tax_absorption.csv`, `output/results_wave2.json` |
| `code/13_relative_prices.py` | Wave 2: within-firm, within-storefront relative prices (21 pairs with HC1 and currency-clustered errors and randomisation inference within firm), the stacked regression with firm × storefront and item fixed effects (two-way clustered, exact randomisation inference), the cross-vendor references (ChatGPT Plus; median of the three \$19.99 frontier plans) and the within-storefront increment test | `data/processed/wave2_relative_long.csv`, `output/tables/W{8,9,10,12}_*.csv`, `output/results_wave2.json` |
| `code/14_default_validation.py` | Wave 2: validation of the estimated schedule — rebuild, strict-majority and subscription-only rules, leave-one-app-out, 300 split-half draws, exact coincidence of frontier plans with the panel's modal price, ladder strength and the weak lower-income storefronts | `output/tables/W11_default_validation.csv`, `W11b_weak_storefronts.csv`, `output/results_wave2.json` |
| `code/15_vintage_test.py` | Wave 2: the vintage test — deviations from the schedule against the movement of each storefront currency since March 2024 (`data/raw/fx_hist/`), with and without the currency control, HC1 and currency-clustered errors | `output/tables/W14_vintage.csv`, `W14b_fx_movement.csv`, `output/results_wave2.json` |
| `code/16_cross_channel.py` | Cross-channel comparison: Microsoft's web-store prices and Google Play's lowest in-app item (`data/raw/web/`) against the App Store prices of the same day | `output/tables/W15_cross_channel.csv`, `W15b_play_countries.csv`, `output/results_wave2.json` |
| `code/20_analysis.py` | Baseline estimates | `output/results.json`, `output/tables/*.csv` |
| `code/30_figures.py` | Figures 2, 5, D.1, D.2 and D.3 (English and Korean labels; it still writes `fig_scen`, which the version 3.1 text does not use) | `output/figures/*.pdf, *.png` |
| `code/31_figures_wave2.py` | Wave 2: Figure 1 (within-firm relative prices), Figure 3 (deviation from the estimated schedule, four plans) and Figure E.1 (income slopes of the benchmark items within firms); English labels | `paper_en/figures/fig_{relative,default_dev,benchmarks}_en.pdf`, `output/figures/*.png` |
| `code/40_tables_tex.py` | Baseline LaTeX table bodies: Tables D.1, D.2, D.3, D.4, D.6, E.1 and E.4 (and, no longer used in the text, `tab_burden`, `tab_case`, `tab_scen`); English and Korean | `paper_en/tables/`, `paper_ko/tables/` |
| `code/41_tables_wave2.py` | Wave 2: bodies of Tables 5, 6, 8, C.1, C.2, E.8, E.9, E.12, E.14 and E.15 (plans, validation of the schedule, consolidated affordability, cross-channel, product classes, within-firm benchmarks, stability, weak storefronts, vintage; run by `run_revision.sh` after `policy_counterfactuals.py` and after 14–16; `--check` verifies without writing) | `paper_en/tables/tab_{wave2_plans,default_validation,afford,cross_channel,play_countries,classes,benchmarks,stability,weak_storefronts,vintage}.tex` |
| `code/42_tables_relative.py` | Wave 2: bodies of Tables 3, 4, 7, E.10, E.11 and E.13 (relative-price pairs, stacked regressions, increments, cross-vendor references, annual-as-monthly guard, tax absorption; `--check` verifies) | `paper_en/tables/tab_{relative_pairs,relative_stacked,increment,cross_vendor,annual_guard,tax_absorption}.tex` |
| `extensions/audit_extensions.py` | Independent headline re-checks; currency-clustered price slopes; within-storefront ratios; gradient-gap robustness; benchmark, vintage and broadband-price sensitivities; \$500 scenario (still computed, no longer used in the text) | `extensions/audit_output/*.csv, audit_results.json` |
| `extensions/figure_price_ratio.py` | Figure 4 (the Go-to-Plus ratio within storefronts) | `paper_en/figures/fig_price_ratio_en.pdf`, `output/figures/fig_price_ratio_en.png` |
| `extensions/build_revision_tables.py` | Bodies of Tables E.2, E.5, E.6 and D.5 (`--check` verifies without writing); `tab_burden_compact` and `tab_500_scenario` are still written but not used in the version 3.1 text | `paper_en/tables/tab_{price_revision,quintile,thresholds,gap_revision,burden_compact,500_scenario}.tex` |
| `extensions/go_rollout_analysis.py` | Appendix F, Table F.1: descriptive comparison around the ChatGPT Go rollouts (specification recorded in `audit_output/go_rollout_spec.json`; the region-fixed-effects contrast, added afterwards, is printed first; no causal interpretation) | `audit_output/go_rollout_*.csv`, `audit_results_rollout.json`, `paper_en/tables/tab_rollout.tex` |
| `extensions/policy_counterfactuals.py` | Table E.7: burden of the \$20 tier under five price schedules (uniform, the entry tier's US-dollar slope, its deviation slope, price level, proportional) and the subsidy to the 2% benchmark | `audit_output/policy_counterfactuals*.csv`, `audit_results_policy.json`, `paper_en/tables/tab_policy.tex` |
| `extensions/figure_rollout.py` | Figure F.1 (English; Korean only when the Korean edition is present) | `paper_*/figures/fig_rollout_*.pdf`, `output/figures/fig_rollout_*.png` |
| `extensions/build_revision_tables_ko.py` | Korean bodies of the revision tables: the English bodies with translated row labels only (`--check` verifies); run only when `paper_ko/main.tex` is present | `paper_ko/tables/` |
| `extensions/figure_price_ratio_ko.py` | Figure 4 with Korean labels (run only when the Korean edition is present) | `paper_ko/figures/fig_price_ratio_ko.pdf`, `output/figures/fig_price_ratio_ko.png` |
| `checks/price_reliability.py` | Plan-candidate audit; currency-sample, leave-one-currency-out and block-resampling checks of the Go/Plus ratio; NumPy re-implementation of HC3/CR1 | `checks/results/*.csv, price_reliability_summary.json` |
| `checks/build_matched_menu_table.py` | Body of Table E.3 (`--check` verifies) | `paper_en/tables/tab_matched_menu_sensitivity.tex` |
| `checks/verify_tier_model.py` | Numerical check of the four-option model of Appendix A: the nested thresholds, the income gradients of Proposition A.1, and the income elasticity of the optimal price increment of Proposition A.2 (closed form, quoted illustrations, monotonicity in the cost share for dispersion s in [0.3, 2]) | `checks/tier_model_verification.json` |
| `checks/sim_check.py` | Standard-library checks of Appendix A (version 3.1): Proposition A.2 against finite differences, log-concavity facts, Proposition A.1, the menu of Proposition A.3 (separability, pass-through, the held frontier price), the arbitrage bounds of Proposition A.4, and the increment test on the replication data (part F) | `checks/results/sim_output.txt` |
| `verification/prose_number_audit.py` | Compares every number in the prose of `paper_en/main.tex` with the pipeline outputs, 1,952 checks (exit 1 on any mismatch; `run_revision.sh` runs it with `--strict`) | console report |
| `verification/en_ko_number_check.py` | Compares, part by part, the numbers written in the Korean and English manuscripts; differences that come from the language alone are listed with reasons (exit 1 on any other difference); run only when the Korean edition is present | console report |
| `run_all.sh` | Steps 09–40, the wave-2 steps (09b, 12, 13, 14, 15, 16, 31), figures, then `run_revision.sh --analysis-only` (which also runs `code/41_tables_wave2.py` and `42_tables_relative.py`, because Table 8 needs the policy counterfactuals) | all of the above |
| `run_revision.sh` | The revision analyses (`extensions/`, `checks/`, the prose audit) and, without `--analysis-only`, the manuscripts and submission files | as listed |
| `build_papers.sh` | Compile `paper_en` (`main.pdf`, anonymised `main_anon.pdf`, `titlepage.pdf`) and, if present, `paper_ko`; check for identifying strings in the anonymised copy; record the sources of each PDF | `paper_*/main.pdf`, `paper_*/main.pdf.sources.sha256` |
| `code/53_flatten_submission.py` | Self-contained LaTeX sources (tables and bibliography inlined), compiled standalone and compared with the PDFs; figure files renamed in order of appearance (`Figure_1.pdf` …, appendix figures `Figure_C1.pdf`); writes the submission title page from `paper_en/titlepage.tex` with the corresponding author's postal address (`submission/postal_address.txt`) and the journal-specific lines (`submission/title_page_journal.tex`) inserted, both kept outside the deposited package, which therefore names no journal (`--check-titlepage` verifies); assembles `submission/` | `submission/` |
| `code/54_anonymised_package.py` | Anonymised copy of the replication package for double-anonymised review (`submission/Replication_package_anonymised.zip`): resolves the `\ifanon` switch in `main.tex`, drops the Korean edition, title page, citation file and identified README, redacts the remaining names, links and identifiers, and fails if any string listed in `verification/identifying_strings.txt` survives (`--check` verifies an existing zip) | `submission/Replication_package_anonymised.zip` |
| `check_release.sh` | Pre-release check: PDFs current, anonymised copy and anonymised package free of the strings in `verification/identifying_strings.txt`, submission folder complete, deposited package free of journal names and submission history (`submission/journal_strings.txt`) and of the postal address, files named here present | exit status |
| `code/50_make_docx.py` | Optional Word version of a manuscript (`python code/50_make_docx.py ko [file.docx]`); needs pandoc, python-docx, TeX Live and poppler-utils; intermediate files go to a temporary folder | `output/*.docx` |

## Instructions to replicators

```bash
pip install -r requirements.txt
bash code/00_download_sources.sh          # optional: only needed to rebuild Anthropic/ITU derived files
python code/03_anthropic_country.py        # optional (requires the raw Anthropic files)
python code/05_itu_price_baskets.py        # optional (requires the ITU workbook)
# python code/01_download_wb.py            # re-downloads World Bank data (will reflect later WDI updates)
# python code/02_scrape_appstore_prices.py # re-scrapes prices (will differ from the 27 Sep 2026 snapshot)
# python code/02b_scrape_wave2.py both     # re-scrapes the second wave (12,422 requests; will differ from the 16 Oct 2026 snapshot)
bash run_all.sh                            # processed data, results.json, results_wave2.json, figures, table bodies, revision analyses, prose audit
bash build_papers.sh                       # paper_en (pdflatex: main.pdf, main_anon.pdf, titlepage.pdf) and, if present, paper_ko (xelatex)
python code/53_flatten_submission.py       # optional: self-contained sources and the submission folder (not part of the deposit)
bash check_release.sh                      # fails if a PDF is older than its sources, the anonymised copy identifies the author, or a file named here is missing
```

`build_papers.sh` stops if references are unresolved, a line runs into the margin by more than 5pt, or an identifying string
appears in the anonymised copy. The anonymised copy is built from the same `main.tex` with the `\ifanon` switch
(`pdflatex -jobname=main_anon "\newif\ifanon\anontrue\input{main.tex}"`).

## List of tables and figures (English manuscript, version 3.1)

Table and figure bodies are in `paper_en/tables/` and `paper_en/figures/`; `output/figures/` holds the PNG previews and, for
the figures drawn by `30_figures.py`, the PDFs that `run_all.sh` copies to `paper_en/figures/`.

| Exhibit | Program | Output |
|---|---|---|
| Table 1 (consumer price ladder of three leading AI assistants, September 2026), Table 2 (data sources) | manual, sources in notes | `paper_en/main.tex` |
| Table 3 (within-firm, within-storefront relative prices, 21 pairs), Table 4 (stacked regression with firm × storefront and item fixed effects) | `13_relative_prices.py` → `42_tables_relative.py` | `W8_relative_pairs.csv`, `W9_relative_stacked.csv`, `data/processed/wave2_relative_long.csv`, `tab_relative_pairs.tex`, `tab_relative_stacked.tex` |
| Table 5 (localisation of AI plans in U.S. dollars and relative to the estimated platform schedule, 16 October 2026) | `09b_wave2_items.py`, `12_default_panel.py` → `41_tables_wave2.py` | `W1_wave2_plans.csv`, `data/processed/wave2_plan_vs_default.csv`, `tab_wave2_plans.tex` |
| Table 6 (validation of the estimated schedule) | `14_default_validation.py` → `41_tables_wave2.py` | `W11_default_validation.csv`, `tab_default_validation.tex` |
| Table 7 (the within-storefront dollar increment between a frontier tier and the capped tier below it) | `13_relative_prices.py` → `42_tables_relative.py` | `W12_increment.csv`, `tab_increment.tex` |
| Table 8 (affordability of the \$20 tier and of the localised entry tier by income group) | `20_analysis.py`, `policy_counterfactuals.py` → `41_tables_wave2.py` | `A1_burden_by_group.csv`, `A2_burden_by_quintile.csv`, `audit_output/policy_counterfactuals_groups.csv`, `tab_afford.tex` |
| Table A.1 (predictions of the tier model by the constraint that binds on the frontier price) | manual (checked by `checks/sim_check.py`) | `paper_en/main.tex` |
| Table B.1 (Anthropic Economic Index releases used) | manual, from `data/raw/anthropic/DATA_DICTIONARY.md` | `paper_en/main.tex` |
| Table C.1 (cross-channel comparison of listed prices), Table C.2 (Google Play's lowest in-app price and the App Store price by country) | `16_cross_channel.py` → `41_tables_wave2.py` | `W15_cross_channel.csv`, `W15b_play_countries.csv`, `tab_cross_channel.tex`, `tab_play_countries.tex` |
| Table D.1 (income gradient of generative-AI use, Microsoft AI User Share, Q2 2026), Table D.2 (income gradient of AI use with controls), Table D.3 (accounting split of the AI-use gap), Table D.4 (income elasticities of any use and of per-capita Claude activity), Table D.6 (income elasticity of the Anthropic AI Usage Index over time) | `20_analysis.py` → `40_tables_tex.py` | `results.json`, `C2_conditional_gradients.csv`, `C3_connectivity_decomposition.csv`, `D1_two_margins_sample.csv`, `tab_{diffusion,controls,decomp,twomargins,aui_time}.tex` |
| Table D.5 (sensitivity of the difference between the two usage-indicator income elasticities) | `audit_extensions.py` → `build_revision_tables.py` | `audit_output/cross_provider_gradient_robustness.csv`, `tab_gap_revision.tex` |
| Table E.1 (local prices and localisation slopes by plan, first wave), Table E.4 (storefront availability, currency and the cheapest locally listed paid tier) | `20_analysis.py` → `40_tables_tex.py` | `B1_localization.csv`, `results.json`, `tab_local.tex`, `tab_store.tex` |
| Table E.2 (first-wave price slopes under alternative standard-error assumptions) | `audit_extensions.py` → `build_revision_tables.py` | `audit_output/local_price_robustness.csv`, `within_storefront_price_ratios.csv`, `tab_price_revision.tex` |
| Table E.3 (the Go-to-Plus price ratio by currency sample) | `price_reliability.py` → `build_matched_menu_table.py` | `checks/results/matched_menu_currency_sensitivity.csv`, `tab_matched_menu_sensitivity.tex` |
| Table E.5 (burden of a \$20 plan by income quintile, and comparison with mobile broadband), Table E.6 (share of economies and population above alternative benchmarks) | `audit_extensions.py` → `build_revision_tables.py` | `A2_burden_by_quintile.csv`, `audit_output/broadband_price_comparison.csv`, `burden_threshold_sensitivity.csv`, `tab_quintile.tex`, `tab_thresholds.tex` |
| Table E.7 (burden of the \$20 tier under alternative price schedules, and the subsidy under uniform pricing) | `policy_counterfactuals.py` | `audit_output/policy_counterfactuals_groups.csv`, `tab_policy.tex` |
| Table E.8 (income slopes of local prices by product class), Table E.9 (within-firm contrasts: income slopes of AI and other products of the same firm), Table E.12 (local prices of the first-wave plans in both waves) | `09b_wave2_items.py`, `12_default_panel.py` → `41_tables_wave2.py` | `W5_item_classes.csv`, `W5b_applevel.csv`, `W2_benchmarks.csv`, `W3_stability.csv`, `tab_{classes,benchmarks,stability}.tex` |
| Table E.10 (relative prices against a common frontier reference), Table E.11 (item-storefront cells dropped by the annual-as-monthly guard), Table E.13 (frontier tiers in U.S.-dollar storefronts whose schedule embeds a tax) | `09b_wave2_items.py`, `12_default_panel.py`, `13_relative_prices.py` → `42_tables_relative.py` | `W10_cross_vendor.csv`, `W6_annual_guard.csv`, `W13_tax_absorption.csv`, `tab_{cross_vendor,annual_guard,tax_absorption}.tex` |
| Table E.14 (storefronts in which the estimated schedule is weak), Table E.15 (vintage test) | `14_default_validation.py`, `15_vintage_test.py` → `41_tables_wave2.py` | `W11b_weak_storefronts.csv`, `W14_vintage.csv`, `tab_weak_storefronts.tex`, `tab_vintage.tex` |
| Table F.1 (changes in use around the first rollouts of ChatGPT Go) | `go_rollout_analysis.py` | `audit_output/go_rollout_summary.csv`, `go_rollout_robustness.csv`, `tab_rollout.tex` |
| Table G.1 (fields of a record of access conditions) | manual; field dictionary `checks/access_measurement_fields.csv` | `paper_en/main.tex` |
| Figure 1 (income gradients of relative prices within firm and storefront) | `31_figures_wave2.py` | `paper_en/figures/fig_relative_en.pdf` |
| Figure 2 (local App Store prices of ChatGPT Plus and ChatGPT Go against income) | `30_figures.py` | `fig_prices_en.pdf` |
| Figure 3 (deviation of listed prices from the estimated platform schedule, 16 October 2026) | `31_figures_wave2.py` | `paper_en/figures/fig_default_dev_en.pdf` |
| Figure 4 (the ChatGPT Go-to-Plus price ratio within storefronts) | `extensions/figure_price_ratio.py` | `paper_en/figures/fig_price_ratio_en.pdf` |
| Figure 5 (burden of a \$20 plan across the income distribution), Figures D.1, D.2, D.3 (diffusion dynamics; accounting split of the log gap in AI use; income gradients in two differently measured AI-use indicators) | `30_figures.py` | `output/figures/fig_{burden,dynamics,decomp,two_margins}_en.pdf` |
| Figure E.1 (income slopes of local dollar prices for AI and other products of the same firms) | `31_figures_wave2.py` | `paper_en/figures/fig_benchmarks_en.pdf` |
| Figure F.1 (usage indicators around the first rollouts of ChatGPT Go) | `extensions/figure_rollout.py` | `paper_en/figures/fig_rollout_en.pdf` |

Written by the pipeline but not used in the version 3.1 text: `tab_burden`, `tab_burden_compact`, `tab_case`, `tab_scen`,
`tab_500_scenario` and `fig_scen`.

The Korean edition of version 3.1 follows later. `40_tables_tex.py` and `30_figures.py` still write Korean table bodies
(`paper_ko/tables/`) and Korean-label figures (`output/figures/*_ko.pdf`); `extensions/build_revision_tables_ko.py`,
`figure_price_ratio_ko.py` and `figure_rollout.py ko` run only when `paper_ko/main.tex` is present.

## References

See the manuscript's reference list; bibliographic metadata were verified against Crossref and arXiv (`research/refs_verified.csv`).

## Changes in version 3.1 (17 October 2026) — revised manuscript

Version 3.1 revises the version 3.0 manuscript after an internal audit (an AI review tool, an independent fresh-eyes
report, a mathematical audit of Appendix A, a numbers audit and a literature audit) and adds the analyses that the revision
required. The first-wave data, `data/processed/country_panel.csv`, `output/results.json` and every baseline estimate are
unchanged; the second-wave item files change where the data rules below apply.

Manuscript (English; 24 pages of main text including the title and abstract page, 65 pages in all; abstract 250 words):

- Results now open with evidence that needs no estimate of the platform's schedule: within the same firm and the same storefront,
  the price of one product relative to another cancels currency, tax and the platform's conversion (Section 5.1, Table 3: 21
  within-firm pairs with HC1 and currency-clustered standard errors and randomisation inference, every plan of Table 4 relative
  to its firm's standard frontier tier; Table 4: stacked regression of 22 plans with firm × storefront and item fixed effects, two-way
  clustered, exact randomisation inference over 252,000 relabellings; Figure 1). The relative prices of the frontier
  tiers vary little with income (absolute slopes at most 0.022, against 0.15–0.34 for YouTube and X Premium); products without an AI allowance rise with
  income 0.20 log points per log point faster than the same firm's frontier tiers (randomisation p = 0.0005), products with a
  small allowance 0.12 faster (p < 0.0001); capped AI tiers as a group do not differ (0.04, p = 0.41). The same firms' storage
  plans, family variants and X's creator subscription, excluded from the stacked regression by its inclusion rule (footnote in
  Section 5.1), are listed in Table E.9 with their slopes. The decomposition against the estimated schedule is the
  second layer (Section 5.3), with a validation subsection (Table 6: rebuild, strict and subscription-only rules, leave-one-app-out,
  300 split-half draws, exact coincidence), Apple's non-re-equalisation of subscriptions and a vintage test (Table E.15), a
  statement of where the schedule is exact (\$4.99, \$9.99, \$19.99) and extrapolated (\$8, \$20, \$100–500) and of the six
  lower-income storefronts where it is weak (Table E.14), and a cross-channel check (Appendix C: Google Play, Microsoft's web store).
  Where vendors override the platform's tax-inclusive price in dollar storefronts they choose the U.S. dollar price (Google AI Pro
  in all ten low- and lower-middle-income storefronts among the 16 taxed dollar storefronts, ChatGPT Plus in five; Table E.13),
  which the text reads as evidence for a uniform-dollar policy or segmented frontier demand rather than for the override cost;
  the mechanism is stated as consistent with the data, not established by it, and the four candidate explanations are set side
  by side in Section 7.1. Identical round listings of different vendors ($25.00 for both $20.00 plans in all 16 taxed dollar
  storefronts, $22.00 in the same eight dollar storefronts with a tax factor of one) are read as the platform's conversion.
- Claims restated at the strength the data support: frontier tiers are "on or near" the schedule with deviations centred on zero
  (not "exactly" or "zero slope"); every localised AI tier is a capped entry tier, but not every capped tier is localised (Google
  AI Plus and SuperGrok Lite stay at the schedule); the 38% discount and the 2.5× → 4× ratio are attributed to ChatGPT Go; the
  "31% of non-AI items against 7% of AI items" headline is dropped (at the app level 8 of 21 against 2 of 8, Fisher p = 0.67, Table
  E.8); prediction P2 is one-sided; Microsoft 365 Personal is described as moderately localised; the 19-day stability check is
  stated for the ten plans observed twice. The usage-indicator section is shortened to what the affordability argument needs
  (tables and figures in Appendix D); the connectivity split is presented as an accounting identity that backs out Microsoft's
  internet scaling; the rollout appendix leads with the region-fixed-effects contrasts.
- Model: Appendix A replaced by the audited version (notation χ, K, Π, ℓ_k; one sign convention for z; Proposition A.1 demand
  gradients; Proposition A.2 increments with the lognormal closed form; Proposition A.3 menu separability, pass-through and the
  frontier price level; Proposition A.4 override and arbitrage; Table A.1 regimes; predictions P1–P5 restated conditionally).
  Arbitrage caps the dollar gap on every tier, so the sustained ChatGPT Go gap of \$3–4 bounds the friction and leaves 15–20% room on
  \$20 tiers and 1–4% on \$100–300 tiers; an unconstrained vendor would pass the entry discount into the frontier level, so the
  within-storefront increment test (Table 7: slope of ln(increment / schedule increment) −0.047, s.e. 0.005, N = 161; in dollars
  −0.010, s.e. 0.007) is the implication that separates a held frontier price from an unconstrained one. Section 3 and the
  main-text sentences that the audit listed (R1–R14) are revised accordingly.
- Data rules (Section 4, Appendix B): the annual-as-monthly guard (Apple lists at most ten purchases per page; 151 of 21,938 cells
  dropped; Super Duolingo 0.045 → −0.076, Headspace Plus −0.104 → 0.202, Gemini 100 GB −0.150 → 0.033, Character.AI+ −0.092 → 0.034,
  Evernote Plus 0.046 → 0.032, Table E.11), de-duplication of items listed under two apps or spellings (five of 152), the sample
  flow (218 codes, 173 active storefronts, 167 in the default panel, 164 with a multiplier, 161 in the deviation regressions), one
  standard-error convention (HC1) with currency-clustered errors for the headline slopes, non-USD and population-weighted
  robustness, and the number of USD-denominated storefronts (102–104, all low-income storefronts among them).
- Numbers corrected from the audit: the Go/Plus sign (the Go-to-Plus slope is +0.104; Figure 4 is the Go-to-Plus ratio); N
  harmonised between the plan and benchmark tables with the filters stated; labels of raw U.S.-dollar and deviation slopes; the
  policy counterfactual reported with the vendor's deviation slope 0.110 (median low-income burden 17.3%) alongside the
  U.S.-dollar slope 0.143 (14.8%), Table E.7; "21 general subscription apps and four apps with embedded AI features"; Table 8
  columns on one sample and tax convention (tax-inclusive ChatGPT Plus burdens 0.75%, 3.27%, 8.89%, 28.90%); "within 0.5% of the
  default in 18 storefronts"; "observed in both waves" (1,586 of 1,587); 162–165 storefronts with income in the first wave;
  165–169 geolocated economies; ×, minus signs, "percent", p-values printed to four decimals (Table F.1).
- Literature: Enache, Friberg and Wiklander (2023), Colbjørnsen et al. (2022), Cabolis et al. (2007), Chellappa and Mehra (2018),
  Jones and Mendelson (2011), Essegaier, Gupta and Zhang (2002), Johnson and Myatt (2003), Bergemann, Bonatti and Smolin (2025),
  Demirer, Fradkin and Tadelis (2025, 2026), Korinek and Vipra (2025), Gans (2026), Massenkoff (2026, Cadences), Sampford (1953),
  Bagnoli and Bergstrom (2005), Weyl and Fabinger (2013), Goldberg and Verboven (2001), Gopinath et al. (2011), Malueg and Schwartz
  (1994), Valletti (2006), Apple's subscription-pricing and price-update pages and X's Premium page; "Lahiri, Dewan and Freimer
  (2017)", which does not exist, is not cited. Novelty claims softened to the multi-market margin.
- The generative-AI declaration names Gemini among the tools, the AI browser agent's collection of the second-wave, default-panel
  and cross-channel prices, the AI subagents' numerical, mathematical and bibliographic audits, and the AI review tool's feedback
  on two earlier versions. JEL codes: L11, L15, L81, L86, D42, O33.

Data and code:

- New raw extracts: `data/raw/web/` (Microsoft 365 web-store prices in 57 countries, Google Play in-app price ranges of 12 apps in
  30 countries, 16 October 2026, with the SHA-256 of every page; the page archive, `cross_channel_page_archive_2026-10-16.zip`, 487
  files, 77 MB, is deposited with the record of version 3.1) and `data/raw/fx_hist/` (six exchange-rate snapshots, March 2024 to
  October 2026, for the vintage test). The page archives of the second audit (`appstore_wave2_page_archive_2026-10-16.zip`,
  12,860 files, 109 MB) and of the cross-channel extracts are deposited with the record of version 3.1; their fingerprints are in
  the package.
- New programs: `code/wave2_common.py`, `code/13_relative_prices.py`, `code/14_default_validation.py`, `code/15_vintage_test.py`,
  `code/16_cross_channel.py`, `code/42_tables_relative.py`, `checks/sim_check.py`. Changed: `code/09b_wave2_items.py` (guard,
  de-duplication, list cap, app-level incidence, new plan rows for YouTube Premium Lite and Microsoft 365 Family),
  `code/12_default_panel.py` (HC3, non-USD and population-weighted slopes, exact and extrapolated references, tax absorption, the
  shares above 3% and below 10%), `code/31_figures_wave2.py` (Figure 1; 19-row benchmark figure), `code/30_figures.py` (Figure 2
  labels), `code/40_tables_tex.py`, `code/41_tables_wave2.py`, `extensions/build_revision_tables.py`,
  `extensions/go_rollout_analysis.py`, `extensions/policy_counterfactuals.py`, `extensions/figure_price_ratio.py` (typography,
  labels, the new columns), `run_all.sh`, `run_revision.sh`.
- New outputs: `data/processed/wave2_relative_long.csv`; `output/tables/W5b`, `W6`, `W6b`, `W7`, `W8`–`W15b`; `output/results_wave2.json`
  now holds 2,131 scalars (2,630 after the second verification pass); `paper_en/tables/tab_{relative_pairs,relative_stacked,cross_vendor,increment,annual_guard,
  tax_absorption,default_validation,weak_storefronts,vintage,cross_channel,play_countries}.tex`; `paper_en/figures/fig_relative_en.pdf`;
  `checks/results/sim_output.txt`.
- `verification/prose_number_audit.py` is rewritten for the version 3.1 text: 1,817 checks, 0 mismatches, full coverage
  (see the second verification pass below for the current count; `run_revision.sh` runs it with `--strict`). `checks/verify_tier_model.py` still parses the two sentences of Appendix A that quote
  the β* illustration and the s = 1 / s = 0.7 elasticities.
- Numbers that differ from the independent re-analyses that prompted the revision, with the reason: the guard flags 151 cells (the
  external script, which lacked the fallback rule for storefronts without a multiplier, 149); the Gemini 100 GB slope after the
  guard is 0.033 (0.062 with the multiplier rule alone); Google AI Plus relative to AI Pro −0.012 (−0.023 before the guard removed
  four cells); the Character.AI+ − Lite increment slope −0.059 (−0.21 before the guard); app-level incidence 8 of 21 against 2 of
  8 after the guard (7 of 21 before, p = 1.0); Microsoft's web-store medians −31.0% and −9.0% (−31.1% and −9.1% when rounded
  before the median); the Google Play lower-income ratios exclude Bangladesh, which has no App Store storefront (0.63 and 1.05;
  0.64 and 1.07 with it); X Corp contributes six items to the stacked regression, not seven; no consumables-only schedule exists
  (no storefront has three consumable price points), so that check reports zero multipliers.

### Second verification pass (17 October 2026)

A second internal verification pass over the first-round files led to the following revisions of the manuscript and the
generators; no data were added.

- Claims aligned with the data: Section 5.5 no longer calls ChatGPT Go the only tier below 3% of income (Google AI Plus is 2.1%
  in the median lower-middle-income economy, from a low U.S. price point); every frontier-versus-frontier pair of the same firm
  is in Table 3 and Table E.10, every pair is oriented the same way (the plan relative to its firm's standard frontier tier),
  and the headline is stated in magnitude terms (absolute slopes at most 0.022; higher tier relative to the standard tier between
  −0.022 and 0.011, with both directions named in Section 5.1); the cross-channel check is stated as
  what it shows (Google Play's lowest ChatGPT item within 5% of the App Store Go price in 22 of 25 same-currency countries and
  within 0.5% in 20; Claude Pro within 5% in 12 of 25; Microsoft's web prices within 5% of the App Store's for both Personal and
  Premium in all 49 same-currency countries and identical to the cent in 37 of 49 for each plan; Play shows only the lowest item, so it is silent on OpenAI's and Google's frontier
  tiers); the opening paragraph no longer claims that digital goods are usually priced to market (8 of 21 general apps localise any
  plan) and states the question.
- Mechanism recast: the increment test rejects only the unconstrained optimum of the nested menu; Table E.13's overrides (Google AI
  Pro at $19.99 in all ten low- and lower-middle-income taxed dollar storefronts, ChatGPT Plus in five) are confronted in Section
  5.3 and read as a uniform-dollar policy or segmented frontier demand; Section 7.1 sets the four explanations (inference-cost share
  with an override cost; arbitrage, binding for the $100–500 tiers; a uniform-dollar policy or anchoring; segmented demand) side by
  side with the evidence that speaks to each and says the cross-section cannot separate them; Table A.1 and the conclusion say
  "consistent with"; the storage plans and X's creator subscription are reported as supportive, not decisive.
- Within-firm design: one inclusion rule for Tables 3 and 4 (every named monthly consumer plan of the five firms at $4 or more in at
  least 60 storefronts, excluding annual and family variants, storage plans and X's creator and post-promotion products), stated in
  a footnote and applied literally: Table 4 stacks 22 items (ChatGPT Pro 100, Pro 500 and SuperGrok Plus added; Microsoft 365
  Family, a family variant, removed; 3,253 observations, 252,000 exact relabellings) and Table 3 reports 21 pairs. The excluded
  same-firm items appear in Table E.9 with their slopes (Google One 100 GB 0.033, Microsoft 365 Basic 0.029, X creator 0.032;
  YouTube Premium Family 0.36, YouTube Music Family 0.38, Microsoft 365 Family 0.056). One classification everywhere (frontier,
  capped, small AI allowance, no AI allowance, storage; Figure 1 and Figure E.1 are coloured by it; SuperGrok Lite capped, X Premium
  small allowance, Microsoft 365 "office"); Table 7's title and the Section 5.4 sentence say that the Microsoft 365 increment is 15%
  wider in poorer storefronts; the Section 5.1 signs follow Table 3; the vintage regression is also clustered by storefront
  (Table E.15); the round-number check of Section 5.3 (both $20 plans at $25.00 in all 16 taxed dollar storefronts, $22.00 in the
  same eight) attributes above-reference deviations to the platform's conversion; P2's market-size implication is stated as untested.
- Abstract rewritten (250 words after the final polish), highlights rewritten (five, at most 85 characters), introduction's findings paragraph cut to
  three findings, Section 6 condensed; the main text ends on page 24 (title and abstract page included). Three menu-cost
  references added (Levy et al. 1997; Zbaracki et al. 2004; Anderson and Simester 2010). Availability statements cite the version DOI of
  3.1 and the two deposited page archives.
- Package hygiene: no file of the public or anonymised package describes the review history (analyses are described by content);
  `code/54_anonymised_package.py` and `check_release.sh` fail on eight case-insensitive patterns (the author's surname in
  citation form, the author's time zone and location phrases, review-history wording and item codes; listed in the two
  scripts; "Korea" and "Korean" as such are allowed, since South Korea is a storefront); the anonymised package omits the
  Korean-edition files and the Zenodo file size and MD5; the anonymised manuscript carries no "for review" line.
- Generators: `code/09b_wave2_items.py` (plan rows for Google One 100 GB, SuperGrok Plus, Microsoft 365 Basic, X's creator
  subscription, YouTube Premium Family and YouTube Music Family; group labels), `code/12_default_panel.py` (low- and
  lower-middle-income counts of the tax-absorption test, round-number counts), `code/13_relative_prices.py` (21 pairs, 22 items,
  frontier-pair summary keys, batched exact randomisation), `code/15_vintage_test.py` (storefront-clustered errors),
  `code/16_cross_channel.py` (identical-price counts), `code/31_figures_wave2.py` and `code/41_tables_wave2.py` (groups),
  `code/42_tables_relative.py` (notes).

### Third verification pass (17 October 2026)

- Cross-channel wording for Microsoft stated as the pipeline measures it: the web prices of Microsoft 365 Personal and Premium are
  within 5% of the App Store prices in all 49 same-currency countries for each plan, identical to the cent in 37 of 49 and within
  0.5% in 45 (widest gap Sweden, 4.3% for Personal, 2.4% for Premium); `code/16_cross_channel.py` now writes these counts
  (`xch_ms_web_vs_app_<plan>_exact_n`, `_within05_n`, `_maxgap_pct`) and Table C.1 reports them.
- One orientation for every pair of Table 3: plan A relative to its firm's standard frontier tier B (ChatGPT Plus, Google AI
  Pro, Claude Pro, SuperGrok, Microsoft 365 Premium, Character.AI+), whether A is a lower or a higher tier; the six OpenAI,
  Google and Anthropic frontier pairs were reversed accordingly (keys `pro100_plus`, `pro200_plus`, `pro500_plus`,
  `ultra_aipro`, `max5_claudepro`, `max20_claudepro`), Table E.10 was already in this orientation, and Figure 1 follows. The
  nine frontier pairs then have slopes between −0.022 and 0.011; the abstract, introduction, Section 5.1, conclusion and
  highlights state the headline as a magnitude (absolute slopes at most 0.022) and Section 5.1 names both directions with their
  randomisation p-values.
- The Google One app's second listing of Google AI Plus (2 TB) is labelled a capped AI tier in Table E.9 and Figure E.1 and
  stays outside Table 4 as a duplicate listing; Cabolis et al. (2007) is cited among the empirical studies; the high-usage tiers
  are "$100–500" throughout, with the arbitrage arithmetic restated (0.6–4% of a $100–500 tier); Table A.1's arbitrage cell
  matches Section 7.1; the storage-plan sentence of Section 5.1 and the conclusion say "consistent with" and "products that
  are costly to serve, among them the frontier AI tiers".
- Hygiene: `check_release.sh` and `code/54_anonymised_package.py` also fail on the collection time zone written as a UTC offset
  or by its name, on two phrases that would describe verification rounds, and on the publisher's name (the Crossref publisher
  field of `research/refs_verified.csv` is exempt in the public package; the patterns are listed in the two scripts);
  in the anonymised copy the collection time zone of the audit notes reads "local time" and the two web-store extracts lose
  their local-time column (`fetch_kst`; the public extracts are unchanged); verification notes describe verification passes,
  not review rounds. `output/results_wave2.json` holds 2,630 scalars; `verification/prose_number_audit.py` makes 1,952
  checks (1,935 in the anonymised copy), 0 mismatches, full coverage.
- Final polish: the conclusion and the cover letter describe the frontier tiers' deviations from the schedule by their
  Table 5 range ("no income-graded localisation, slopes between −0.016 and 0.004") rather than as unrelated to income; the
  conclusion's firm-versus-product statement is phrased as "consistent with"; Appendix C names both localised AI tiers
  (ChatGPT Go, Character.AI Lite) and says that only ChatGPT is among the Google Play apps collected; the abstract says
  "closely match"; `submission/README.md` lists the identified manuscript and package as the files to submit.

## Changes in version 3.0 (16 October 2026) — revised manuscript

Version 3.0 is a substantially revised English manuscript built on a second data collection. The first-wave data, the processed
files, `output/results.json` (865 scalars, identical to the frozen version 1.8 baseline `extensions/baseline_results_v1.8.json`)
and every baseline estimate they contain are unchanged; the English PDFs of version 2.1 are superseded.

Manuscript (English; 41 pages, abstract 249 words):

- Same title. Abstract, introduction, discussion and conclusion rewritten around which part of the subscription menu vendors
  price for local markets, what the platform sets automatically, and why. The \$20 standard tiers and the \$100–300 high-usage tiers
  of every AI vendor sit on Apple's default price schedule: net of the platform's tax-and-exchange-rate conversion their income
  slope is zero, and 55–87% of storefronts list a price within 3% of the default. Only capability-capped entry tiers are localised
  (ChatGPT Go: 38% below the default in the median poorer storefront), so the standard plan costs 2.5 times the entry plan in the
  United States and about 4 times in the median low-income storefront. The prices of the ten AI plans observed in both audits were
  all unchanged (1,586 of 1,586).
- New structure. Section 2: institutional background (the price menu; how App Store prices are set). Section 3: a model with a
  supply side — inference as a positive marginal cost, cross-border arbitrage, a four-option menu (non-use, free tier, capped entry
  tier L, frontier tier H); Propositions A.1 (demand-side gradients) and A.2 (income elasticity of the optimal price) are in
  Appendix A — and five testable predictions P1–P5. Section 5 (results): 5.1 income slopes of listed prices; 5.2 deviations from
  Apple's default schedule; 5.3 the within-storefront Plus-to-Go ratio (2.5 in the United States, about 4 in the median
  low-income storefront); 5.4 benchmarks and within-firm contrasts (YouTube against Google AI Pro and Ultra, X Premium against
  SuperGrok, Microsoft 365 Personal against Microsoft 365 Premium); 5.5 price stability; 5.6 the affordability burden (0.65% of
  per-capita income in the median high-income economy, 29% in the median low-income one). Section 6, the public usage indicators,
  is now descriptive.
- Removed or moved. The ChatGPT Go rollout comparison (version 2.1 Section 5.5) is now Appendix E, a descriptive record without
  causal language (Table E.1, Figure E.1); the version 2.1 policy counterfactuals section is gone and its table of price
  schedules and subsidies remains as Appendix Table D.7; the convergence proposition of version 2.1 Section 6.2 and the \$500
  scenario appendix are removed.
- Literature added: DellaVigna and Gentzkow (2019), Simonovska (2015), Krugman (1986), Atkeson and Burstein (2008), Deneckere and
  McAfee (1996), Bhargava and Choudhary (2001, 2008), Sundararajan (2004), Shiller and Waldfogel (2011), Waldfogel (2020), Danzon
  and Chao (2000), Wang and Wright (2017) and Apple's App Store Connect Help page "Set a price" (2026); the bibliographic metadata
  were checked against Crossref and arXiv. The DOIs of Goldberg and Knetter (1997) and Varian (1985), which could not be
  verified, were removed; the entry for the Google ATLAS report (Iscenko et al., 2026) lists all 18 authors; arXiv entries use the
  arXiv format.
- Consistency and presentation corrections: denominators, the bracketed prices and the Max rows of Table 1, notation, the "No
  store" label, decimal precision, rounding statements, the units of Table D.7, and `et al.` and DOI formats in the references.
- The generative-AI declaration is extended (an AI browser agent executed the second-wave collection scripts under the author's
  direction; feedback from an AI review tool on an earlier version was consulted; the author verified all results).
- Title page, highlights, cover letter, declarations and `submission/README.md` rewritten (`submission/`, distributed
  separately).
- Korean edition. Not part of this version: `paper_ko/` now holds only the Korean table bodies written by
  `code/40_tables_tex.py`; the version 2.1 Korean edition is in the version 2.1 record, and a Korean edition of version 3.0
  follows later. `run_all.sh`, `run_revision.sh`, `build_papers.sh` and `check_release.sh` skip the Korean steps when
  `paper_ko/main.tex` is absent.

Data and code:

- Second App Store audit, 16 October 2026 (19 days after the first): 34 apps × 218 storefront codes (7,412 requests; 173
  storefronts with a local price list) — the plans of ChatGPT, Claude and Gemini, six other AI assistants and 25 general
  subscription apps — and a panel of 30 small-developer apps in 167 storefronts that reveals Apple's default price schedule. New
  raw data: `data/raw/appstore_wave2/` (core and default-panel JSONL, exchange-rate files, app lists, `README.md`). Every page
  carries its SHA-256 fingerprint in the package; the page archive is deposited with the record of version 3.1
  (`appstore_wave2_page_archive_2026-10-16.zip`).
- New programs: `code/02b_scrape_wave2.py` (not run by `run_all.sh`), `code/09b_wave2_items.py`, `code/12_default_panel.py`,
  `code/41_tables_wave2.py`, `code/31_figures_wave2.py`. New files: `data/processed/wave2_*.csv`, `output/tables/W1`–`W5`,
  `output/results_wave2.json` (774 scalars), `paper_en/tables/tab_{wave2_plans,benchmarks,classes,stability,afford}.tex` and
  `paper_en/figures/fig_{default_dev,benchmarks}_en.pdf` (see *Wave 2* above).
- `checks/verify_tier_model.py` is extended from the three-option model to the four-option model and Proposition A.2 (the closed
  form of the income elasticity of the optimal price, the quoted illustrations and its monotonicity in the cost share for
  dispersions between 0.3 and 2).
- `verification/prose_number_audit.py` is rewritten for the version 3.0 text: 1,184 checks, 0 mismatches (`run_revision.sh` runs
  it with `--strict`).
- `build_papers.sh` fixes `SOURCE_DATE_EPOCH` at 1792108800 (16 October 2026) by default, so that rebuilds are byte-identical.
- Unchanged baseline numbers that the version 3.0 text repeats: first-wave income slopes of ChatGPT Plus (0.039) and Go (0.143),
  the slope of the Go-to-Plus ratio (0.104), the burden medians of the \$20 plan (0.65%, 3.09%, 8.73% and 28.9% across the four
  income groups), the elasticity of any use (0.370), of per-capita Claude activity (0.711) and their difference (0.340).

## Changes in version 2.1 (8 October 2026) — revised manuscript

Version 2.1 is a substantially revised manuscript. Data, processed files, `output/results.json`
and every version 2.0 table body and figure are unchanged; the English PDFs of version 2.0 are superseded.

Manuscript (English):

- New title, *Localised Entry, Global Frontier: How Generative-AI Subscriptions Are Priced Across Countries*; abstract (246 words),
  introduction and conclusion rewritten in non-technical language around one question: which part of the menu vendors price
  for local incomes, and whether a cheaper local tier brings more people into use.
- Results reordered: Section 5.1 (what vendors localise) now leads and reports the within-storefront Plus-to-Go multiple
  (2.5 in the United States; medians 2.9, 3.3, 3.8 and 4.0 across the four income groups); burdens follow in 5.2.
- New Section 5.5, a case comparison (design fixed in the script before the outcomes were computed; not externally registered) around the first rollouts of ChatGPT Go (India, Indonesia, sixteen Asian
  economies) with permutation inference, Table 13 and Figure 6; new Section 5.6, policy counterfactuals (Table 14: four price
  schedules and the subsidy to the 2% benchmark). Section 4 documents the rollout record and Section 4.1 the design.
- The convergence proposition moved from the framework to Discussion 6.2 and its arithmetic labelled illustrative; Section 5.4
  retitled "comparison with any-product adoption"; the condition β < β* stated where Proposition 2 is invoked, with a numerical
  note in Appendix A; redirect outcomes and the arbitrage explanation reworded as retrieval outcomes and one possible explanation;
  Appendix B adds a table of the Anthropic releases and the rollout record; the Argentina/Türkiye classification and the
  Anthropic sampling are described precisely. Three references added.
- Title page, highlights, cover letter and `submission/README.md` rewritten (`submission/`, distributed separately).
- Formatting (8 October 2026, same day): appendix tables, figures and equations are numbered per appendix
  (Table B.1, Figure C.1, Eq. (A.1); main-text numbering unchanged); the submission figure files are named in order of appearance
  (`Figure_1.pdf` … `Figure_6.pdf`, `Figure_C1.pdf`); the data-availability statement no longer describes earlier versions by their
  submission history; the anonymised review copy states that an anonymised copy of this package accompanies the submission.

Package:

- `data/raw/openai/chatgpt_go_rollout.csv` (dated rollout record with sources); `extensions/go_rollout_analysis.py`,
  `policy_counterfactuals.py`, `figure_rollout.py`; `run_revision.sh` runs them; `build_revision_tables_ko.py` covers the two new
  tables; `verification/prose_number_audit.py` extended to 367 checks.
- New `code/54_anonymised_package.py` builds the anonymised copy of the package for double-anonymised review (`submission/`, not
  deposited); `verification/identifying_strings.txt` lists the strings that `build_papers.sh`, `check_release.sh` and that script
  must not find in the anonymised copies; `run_all.sh`, `run_revision.sh` and `build_papers.sh` skip the Korean edition and the
  title page when those files are absent, so the anonymised copy runs with the same scripts.
- Folders renamed to neutral names: `revision_audit/` is now `extensions/` and `publication_upgrade/` is now `checks/` (every
  path in the scripts, this README and the manuscripts follows; the version 2.0 deposit keeps the old names).
- Conventions settled after an external read of version 2.1: percentage changes quoted from Table 13 are $e^{\Delta}-1$ of the
  log differences (2.5%, 4.9%, 16.5%, 15.3%); the Appendix A proposition is numbered A.1 so that Proposition 1 is the one
  stated in Section 6.2; the rollout design is described as fixed in the script before the outcomes were computed and not
  registered externally; Table 14 states its economy count against Table 4.
- Korean edition (`paper_ko/main.tex`, 39 pages) synchronised with the version 2.1 English text, including the new sections, tables
  and Figure 6 (`figure_rollout.py ko`); `verification/en_ko_number_check.py` now compares 31 parts (880 numbers in the English
  text; 117 listed language-only differences; no other difference).

## Changes after version 2.0 (1 October 2026) — Korean edition

- `paper_ko/main.tex` is now a translation of the version 2.0 English manuscript, which remains the original: same structure,
  labels, tables, figures, references and numbers (xelatex; 34 pages). It replaces the version 1.8 Korean text.
- New: `extensions/build_revision_tables_ko.py` (+ `--check`), `extensions/figure_price_ratio_ko.py` and
  `verification/en_ko_number_check.py` (29 parts; 666 numbers in the English text; 55 listed language-only differences such as
  month names and number words; no other difference). `run_revision.sh` runs all three.
- `code/30_figures.py`: Korean legend of Figure 6 now reads "AI 이용자/인터넷 이용자 비율"; `code/40_tables_tex.py`: the Korean
  label of the collapsed-pool sample in Table 10 is "합침" (it read "군집", the word used for clustered standard errors). English
  figures and tables unchanged.
- The translation was read against the English text paragraph by paragraph by a second reader; one ambiguous sentence (usage
  caps "rather than" withholding frontier models) and 18 minor wording, hedge or terminology points were corrected.
- `code/50_make_docx.py`: version 2.0 table headers and Korean theorem labels; figures rendered with `pdftoppm` (PyMuPDF is no
  longer needed); intermediate files in a temporary folder, so the manuscript folders are not modified.
- `build_papers.sh` and `check_release.sh`: the Korean build record now covers `apalike-doi.bst`.
- The English manuscript, the data and every English output are unchanged; the English PDFs are byte-identical to version 2.0.
  Clean-room rerun: all 245 files of the working copy, including the 30 in `paper_ko/`, are byte-identical after deleting every
  generated file and rerunning the pipeline (`verification/README.md`).

## Changes in version 2.0 (30 September 2026) — revised version

Manuscript (English), relative to version 1.8 (the SSRN working paper):

- Title shortened to *Affording Generative AI Across Countries: Uniform Prices, Unequal Burdens*; abstract rewritten (248 words);
  keywords and JEL codes unchanged. The introduction states the contribution (a dated multi-provider audit of local prices)
  and four findings, and relates the paper to Sathish et al. (2024), Kanzamanova and Myeong (2026) and the ITU affordability convention.
- New Section 2.1 on the OpenAI tariff change of 29 September 2026 (two days after the audit): Pro 500 tier, revised Pro 200
  allowance; treated as a separate event, with a \$500 reference-fee scenario (Appendix E, Table 16) and a protocol for
  recording access conditions (Appendix F; field dictionary in `checks/access_measurement_fields.csv`).
- Framework: Remark 1 explains what a PPP denominator measures (the PPP-based ratio equals the burden under prices indexed to
  local price levels); Proposition 1 (access-conditional equalisation) and the "AI access paradox" are restated with the
  proxies used for exposure and adoption; Section 3.4 sets out what the two public usage indicators identify (the AUI pools
  free and paid accounts; the gradient difference decomposes into vendor share and conversations per user); the model of
  Appendix A is presented as organising the evidence, not as tested.
- Section 4.1 (estimands and inference) added: the burden slope is β − 1 by construction; HC3 errors are conditional on the
  published indicators; currency-clustered errors for the price regressions; country-clustered and bootstrap intervals for the
  gradient difference.
- Results: Table 4's last column is now the dollar price ratio of the \$20 plan to the ITU broadband basket (1.7/2.6/5.1/6.4)
  instead of the ratio of burdens with different income vintages (1.5/2.2/4.5/6.1 in version 1.8); Table 5 (benchmark
  sensitivity: 85.6/60.1/44.6/16.7% of the covered working-age population above 1/2/5/10%) and the 2025-GNI-only medians
  added; Section 5.2 adds currency-clustered inference (Table 8), the within-storefront Go-to-Plus ratio (slope 0.104,
  Table 9, Figure 3) and the plan-matching checks; Section 5.4 adds the direct estimation of the gradient difference
  (Table 12: 0.340 baseline; 0.356/0.266/0.232/0.476 under alternatives; leave-one-out 0.329–0.351).
- Discussion reorganised (what the evidence shows; a feasible evaluation agenda; four policy implications ordered by margin;
  consolidated limitations). Conclusion rewritten.
- Bibliography in an APA-like author–date style with DOIs (`apalike-doi.bst`); references to Sathish et al. (2024) LLeMpower,
  André et al. (2025), Callaway and Sant'Anna (2021), Kanzamanova and Myeong (2026) and the OpenAI tariff pages added.
- Declarations section: generative-AI declaration, data availability (Zenodo DOI; withheld in the anonymised copy),
  funding and competing interests. Separate title page (`paper_en/titlepage.tex`) with CRediT roles for double-anonymised review.

Numbers: all version 1.8 estimates are unchanged (`output/results.json` is identical; `extensions/baseline_results_v1.8.json`
is the frozen copy). The only corrected exhibit is the broadband column of Table 4 (see above). (The −0.027 (0.012)
convergence slope printed in versions up to 1.6 was corrected to −0.026 (0.011) in version 1.7, before the SSRN posting.)

Package:

- `run_all.sh` now chains the baseline pipeline and the version 2.0 analyses (`run_revision.sh`), whose table bodies
  supersede the baseline where they overlap (`tab_quintile.tex`); `build_papers.sh` also builds the anonymised copy and the
  title page and rejects identifying strings; `check_release.sh` covers the new files; `code/53_flatten_submission.py` added
  (its output folder `submission/` is distributed separately); `verification/prose_number_audit.py` (292 checks) added and run by
  `run_revision.sh`.
- `extensions/`, `checks/` and `extensions/upstream_validation/` (fresh re-downloads of the Microsoft,
  Anthropic and ITU sources, byte-identical derived files) are the audit and extension scripts written at the revision stage;
  `extensions/figure_price_ratio.py` now writes a timestamp-free PDF so that rebuilds are byte-identical.
- Word exports and the intermediate review copies of the revision stage are not shipped; the LaTeX PDFs are the manuscript.
- Clean-room rerun: all 133 generated files (processed data, results.json, table bodies, figures, audit outputs, the four
  PDFs and the submission sources) are byte-identical to the shipped ones (`verification/README.md`).

Version history 1.1–1.8 (28 September 2026): see `README_v1_8.md`.
