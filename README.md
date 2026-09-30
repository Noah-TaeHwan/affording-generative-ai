# Affording Generative AI Across Countries: Uniform Prices, Unequal Burdens

**TaeHwan Oh** · Independent researcher · [ORCID 0009-0004-4111-4802](https://orcid.org/0009-0004-4111-4802)\
Working paper, version 2.0 (30 September 2026)

- **Paper:** [English (PDF)](paper_en/main.pdf) · [Korean (PDF)](paper_ko/main.pdf), a translation of the version 2.0 text (1 October 2026)
- **SSRN:** [abstract 7535900](https://ssrn.com/abstract=7535900) · DOI [10.2139/ssrn.7535900](https://doi.org/10.2139/ssrn.7535900)
- **Replication package (archived):** Zenodo, DOI [10.5281/zenodo.23006365](https://doi.org/10.5281/zenodo.23006365) (all versions; version 2.0, DOI [10.5281/zenodo.23057976](https://doi.org/10.5281/zenodo.23057976), matches this repository except the Korean edition added on 1 October 2026)

## Abstract

Consumer generative AI is sold on a subscription menu that is nearly identical across countries, while national incomes differ by two orders of magnitude. This paper measures how far local prices adjust to that difference. I audit the tax-inclusive local prices listed for nine plans of ChatGPT, Claude and Gemini in 170 national Apple App Store storefronts on a single day, and compute the annual cost of each plan as a share of GNI per capita for 201 economies. Standard \$20 plans are priced almost uniformly: the income slope of the local dollar price is 0.03–0.04, against 0.23 if prices tracked local price levels. Only OpenAI's entry tier is partly localised (slope 0.14), and every low-income storefront prices in U.S. dollars. A \$20 plan therefore costs 0.65% of per-capita income a year in the median high-income economy and 29% in the median low-income economy, and 60% of the working-age population of the covered economies lives where it exceeds the 2% benchmark used for broadband. Two public usage indicators differ in their income gradients, 0.37 for any generative-AI use and 0.71 for per-capita Claude activity, a contrast consistent with, though not a test of, a model in which free tiers detach initial adoption from the paid price. Larger productivity gains for less-skilled users, moreover, do not imply convergence across countries unless exposure and adoption keep pace. The audit is a one-day snapshot of listed prices; the paper sets out what the evaluation of pricing and access policies would require.

## Replication package

This package reproduces every table, figure and in-text number of the English manuscript (version 2.0), and of its Korean
edition (a translation of the version 2.0 text, added after the Zenodo version 2.0 deposit; see the end of this file). It follows the structure of the Social Science Data Editors' README template
(https://social-science-data-editors.github.io/template_README/). The changes since version 1.8 are listed at the end.

## How to cite

- Oh, TaeHwan (2026). *Replication package for "Affording Generative AI Across Countries: Uniform Prices, Unequal Burdens"*,
  version 2.0 [data and code]. Zenodo. https://doi.org/10.5281/zenodo.23006365
- Oh, TaeHwan (2026). *Affording Generative AI Across Countries: Uniform Prices, Unequal Burdens.* Working paper, version 2.0
  (30 September 2026). SSRN. https://doi.org/10.2139/ssrn.7535900

## Overview

The code (i) downloads World Bank indicators and third-party usage datasets, (ii) scrapes local App Store prices of ChatGPT,
Claude and Gemini in every storefront, (iii) builds a country-level panel (`data/processed/country_panel.csv`), (iv) runs the
analysis (`output/results.json`, `output/tables/*.csv`), (v) draws the figures, (vi) writes LaTeX table bodies, and (vii) runs
the additional analyses of version 2.0 — currency-clustered inference, the within-storefront Go/Plus comparison, plan-matching
checks, benchmark and income-vintage sensitivities, the \$500 reference-fee scenario, a numerical check of the model in
Appendix A, and an audit of every number printed in the prose. From the shipped raw extracts, steps (iii)–(vii) run in about
20 seconds (`bash run_all.sh`); `bash build_papers.sh` then compiles the manuscripts.

## Data availability and provenance statements

All data are publicly available. The author has legitimate access to all data used in this manuscript and the package includes
the inputs used by `run_all.sh`, including derived Anthropic and ITU country files. The large Anthropic release files
(approximately 450 MB) and the ITU workbook are not bundled. `code/00_download_sources.sh` retrieves the Anthropic files at the
pinned commit and the ITU workbook from the dated provider URL so that the country-level extractions can also be rebuilt. A dated
provider URL is not an immutable version guarantee.

| Source | Provider / URL | Version used | Licence | Files in package |
|---|---|---|---|---|
| World Development Indicators; Global Findex 2025; country classification FY2027 | World Bank API `api.worldbank.org/v2` | extracted 27 Sep 2026 (WDI last updated 13 Jul 2026) | CC BY 4.0 | `data/raw/wb/` |
| AI Diffusion dataset (AI User Share H1 2025–Q2 2026) and reports | Microsoft AI Economy Institute, `github.com/microsoft/ai-diffusion-report` | commit 507c316 (20 Sep 2026) | MIT | `data/raw/ms_repo/data/AI_Diffusion_Q22026_Update.csv`; copy in `revision_audit/microsoft_pinned.csv` |
| Technical paper (region-imputed flags) | Misra et al. (2025), arXiv:2511.02781 | v1 | arXiv | cited; flags reproduced in code |
| Anthropic Economic Index, country level | `huggingface.co/datasets/Anthropic/EconomicIndex` | commit 2ea58ff (26 Jun 2026) | data CC-BY, code MIT | derived: `data/raw/anthropic/anthropic_country_*.csv`; raw via script |
| Google AI & Economy ATLAS v1.0 | `ai.google/economy/atlas` | April 2026 sample, published 23 Jul 2026 | see provider | `data/raw/google_atlas/` |
| ITU ICT Price Baskets 2008–2025 | ITU, `itu.int/en/ITU-D/Statistics/Pages/ICTprices` | December 2025 release | ITU terms (attribution) | derived CSVs; workbook via script |
| App Store in-app purchase prices | Apple App Store product pages (`apps.apple.com/<cc>/app/id<app>`) | scraped 27 Sep 2026 (UTC) | public web pages; factual data | `data/raw/appstore/appstore_iap_raw.jsonl` |
| Exchange rates | open.er-api.com (ExchangeRate-API, attribution required); cross-check: fawazahmed0 currency-api | 27 Sep 2026 | provider terms | `data/raw/fx/` |
| OpenAI tariff change of 29 Sep 2026 (Section 2.1, Appendix E) | OpenAI Help Center pages cited in the manuscript | retrieved 29–30 Sep 2026 | provider terms | `revision_audit/pricing_sources/` (manifest and capture record; the \$500 fee is the only number used) |

Notes. (1) The App Store scrape and exchange rates are point-in-time snapshots; re-running `02_scrape_appstore_prices.py` today
will give different prices. The archive stores the parsed listing records, not the original HTML (Appendix B). (2) Microsoft
pools 36 economies into regional aggregates; `10_build_dataset.py` flags them (`ms_region_imputed`). (3) Anthropic's August-2025
published AUI includes un-geolocated traffic in the denominator; `03_anthropic_country.py` builds a harmonised index
(`aui_geo_baseline`). (4) Namibia's ISO2 code is the string `NA`, which pandas reads as missing by default; every script therefore
reads CSV files with `keep_default_na=False, na_values=[""]`. (5) The World Bank API no longer serves `PA.NUS.PPPC.RF`; the GDP
price-level ratio is computed as `NY.GDP.PCAP.CD / NY.GDP.PCAP.PP.CD` in the year of the GNI data (`plr_gdp`).

## Computational requirements

- Tested with Python 3.11.15, pandas 3.0.2, numpy 2.4.4, statsmodels 0.15.0, scipy 1.17.1, matplotlib 3.10.9, requests 2.33.1,
  openpyxl 3.1.5. Install with `pip install -r requirements.txt` (`revision_audit/requirements_revision.txt` and
  `publication_upgrade/requirements.txt` list the same libraries for the version 2.0 scripts).
- Fonts for figures: Liberation Sans (English labels) and NanumGothic (Korean labels; Debian/Ubuntu package `fonts-nanum`).
  Where they are missing the scripts fall back to Arial/AppleGothic or DejaVu Sans; the figures then look slightly different
  and are not byte-identical to the shipped files.
- Platforms: on other operating systems the CSV outputs can differ in the last printed digit (floating-point formatting);
  `output/results.json` and the LaTeX tables, which are rounded, are unaffected.
- LaTeX (TeX Live 2023): `pdflatex` + `bibtex` (English; packages geometry, mathptmx, amsmath/amsthm, booktabs, threeparttable,
  tabularx, multirow, natbib, tikz, enumitem, hyperref, xurl); `xelatex` + `bibtex` with `xetexko` (Korean), using the system
  fonts Liberation Serif/Sans/Mono and Noto Serif/Sans CJK KR. The English bibliography style `paper_en/apalike-doi.bst` is
  shipped. `build_papers.sh` fixes `SOURCE_DATE_EPOCH` so that rebuilds are byte-identical.
- Randomness: the bootstrap in `20_analysis.py` (2,000 draws, seed 20260927) and the currency-block resampling in
  `publication_upgrade/price_reliability.py` (19,999 draws, seed 20260930).
- Runtime: downloads ≈ 10–20 min (App Store scrape: 654 requests); analysis ≈ 20 s; manuscripts ≈ 1 min.

## Package contents

Included: all programs; every raw extract that `run_all.sh` reads; the derived Anthropic and ITU country files; processed data;
results, tables and figures; LaTeX sources, `.bbl` files and compiled PDFs of the English manuscript (identified and anonymised
copies, separate title page) and of the Korean edition; the verification record. The journal submission files
(`submission/`, generated by `code/53_flatten_submission.py`) are distributed separately and are not part of the deposited package.
Not included (re-downloadable at pinned versions with `code/00_download_sources.sh`): the Anthropic release CSVs (≈450 MB), the
ITU workbook, and Microsoft's report PDFs and repository history.

| Folder | Contents |
|---|---|
| `code/`, `run_all.sh`, `run_revision.sh`, `build_papers.sh`, `check_release.sh` | Pipeline (see *Description of programs*) |
| `data/raw/`, `data/processed/` | Frozen source extracts; analysis panel and price files |
| `output/` | `results.json` (865 scalars), `tables/*.csv`, `figures/*.pdf, *.png` |
| `paper_en/` | English manuscript: `main.tex`, `titlepage.tex`, `references.bib`, `apalike-doi.bst`, `tables/`, `figures/`, `main.pdf`, `main_anon.pdf`, `titlepage.pdf`, build record |
| `paper_ko/` | Korean edition of the version 2.0 manuscript (translation; same tables, figures, references and numbers): `main.tex`, `references.bib`, `apalike-doi.bst`, `tables/`, `figures/`, `main.pdf`, build record |
| `revision_audit/` | Version 2.0 analyses: `audit_extensions.py` (clustered inference, sensitivities, headline re-checks), `figure_price_ratio.py`, `build_revision_tables.py`, and their Korean counterparts `figure_price_ratio_ko.py` and `build_revision_tables_ko.py`; outputs in `audit_output/`; `baseline_results_v1.8.json` (frozen baseline); `upstream_validation/` (provider-file re-download checks); `pricing_sources/` (tariff-change capture record); `AUDIT_REPORT.md` (audit-stage record) |
| `publication_upgrade/` | Plan-matching and currency-sample checks (`price_reliability.py`), the Go/Plus table (`build_matched_menu_table.py`), numerical verification of Appendix A (`verify_tier_model.py`), the access-conditions field dictionary and protocol of Appendix F |
| `verification/` | `README.md` (clean-room replication record), `prose_number_audit.py` (292 checks of the numbers printed in the prose) and `en_ko_number_check.py` (the Korean edition prints the same numbers as the English text) |
| `submission/` (not deposited) | Generated by `code/53_flatten_submission.py`: anonymised and identified PDFs, title page, self-contained LaTeX sources and figure files; the hand-written highlights, cover letter, declarations and checklist travel with the separate submission archive |
| `research/refs_verified.csv` | Crossref/arXiv check of bibliographic metadata |
| `README_v1_8.md` | README of the working-paper package (version history 1.1–1.8) |

## Licence

The code (`code/`, `revision_audit/*.py`, `publication_upgrade/*.py`, `verification/*.py`, the shell scripts) is released under
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
| `code/03_anthropic_country.py` | Country-level Anthropic panel; harmonised AUI | `data/raw/anthropic/anthropic_country_*.csv` |
| `code/05_itu_price_baskets.py` | Tidy ITU price baskets | `data/raw/itu/itu_affordability_latest.csv` |
| `code/06_verify_references.py` | Crossref/arXiv check of bibliographic metadata | `research/refs_verified.csv` |
| `code/09_appstore_prices.py` | Monthly local prices, USD conversion, storefront status | `data/processed/appstore_prices_*.csv` |
| `code/10_build_dataset.py` | Merge all sources | `data/processed/country_panel.csv` |
| `code/11_data_dictionary.py` | Variable descriptions | `data/processed/data_dictionary.csv` |
| `code/20_analysis.py` | Baseline estimates | `output/results.json`, `output/tables/*.csv` |
| `code/30_figures.py` | Figures 1, 2, 4, 5, 6 (English and Korean labels) | `output/figures/*.pdf, *.png` |
| `code/40_tables_tex.py` | Baseline LaTeX table bodies | `paper_en/tables/`, `paper_ko/tables/` |
| `revision_audit/audit_extensions.py` | Independent headline re-checks; currency-clustered price slopes; within-storefront ratios; gradient-gap robustness; benchmark, vintage and broadband-price sensitivities; \$500 scenario | `revision_audit/audit_output/*.csv, audit_results.json` |
| `revision_audit/figure_price_ratio.py` | Figure 3 | `paper_en/figures/fig_price_ratio_en.pdf`, `output/figures/fig_price_ratio_en.png` |
| `revision_audit/build_revision_tables.py` | Bodies of Tables 3, 4, 5, 8, 12, 16 (`--check` verifies without writing) | `paper_en/tables/tab_{burden_compact,quintile,thresholds,price_revision,gap_revision,500_scenario}.tex` |
| `revision_audit/build_revision_tables_ko.py` | Korean bodies of Tables 3, 4, 5, 8, 9, 12, 16: the English bodies with translated row labels only (`--check` verifies) | `paper_ko/tables/` |
| `revision_audit/figure_price_ratio_ko.py` | Figure 3 with Korean labels | `paper_ko/figures/fig_price_ratio_ko.pdf`, `output/figures/fig_price_ratio_ko.png` |
| `publication_upgrade/price_reliability.py` | Plan-candidate audit; currency-sample, leave-one-currency-out and block-resampling checks of the Go/Plus ratio; NumPy re-implementation of HC3/CR1 | `publication_upgrade/results/*.csv, price_reliability_summary.json` |
| `publication_upgrade/build_matched_menu_table.py` | Body of Table 9 (`--check` verifies) | `paper_en/tables/tab_matched_menu_sensitivity.tex` |
| `publication_upgrade/verify_tier_model.py` | Numerical check of the thresholds and gradients of Appendix A | `publication_upgrade/tier_model_verification.json` |
| `verification/prose_number_audit.py` | Compares every number in the prose of `paper_en/main.tex` with the pipeline outputs (exit 1 on any mismatch) | console report |
| `verification/en_ko_number_check.py` | Compares, part by part, the numbers written in the Korean and English manuscripts; differences that come from the language alone are listed with reasons (exit 1 on any other difference) | console report |
| `run_all.sh` | Steps 09–40, figures, then `run_revision.sh --analysis-only` | all of the above |
| `run_revision.sh` | The version 2.0 analyses (and, without `--analysis-only`, the manuscripts and submission files) | as listed |
| `build_papers.sh` | Compile `paper_en` (`main.pdf`, anonymised `main_anon.pdf`, `titlepage.pdf`) and `paper_ko`; check for identifying strings in the anonymised copy; record the sources of each PDF | `paper_*/main.pdf`, `paper_*/main.pdf.sources.sha256` |
| `code/53_flatten_submission.py` | Self-contained LaTeX sources (tables and bibliography inlined), compiled standalone and compared with the PDFs; assembles `submission/` | `submission/` |
| `check_release.sh` | Pre-release check: PDFs current, anonymised copy clean, files named here present | exit status |
| `code/50_make_docx.py` | Optional Word version of a manuscript (`python code/50_make_docx.py ko [file.docx]`); needs pandoc, python-docx, TeX Live and poppler-utils; intermediate files go to a temporary folder | `output/*.docx` |

## Instructions to replicators

```bash
pip install -r requirements.txt
bash code/00_download_sources.sh          # optional: only needed to rebuild Anthropic/ITU derived files
python code/03_anthropic_country.py        # optional (requires the raw Anthropic files)
python code/05_itu_price_baskets.py        # optional (requires the ITU workbook)
# python code/01_download_wb.py            # re-downloads World Bank data (will reflect later WDI updates)
# python code/02_scrape_appstore_prices.py # re-scrapes prices (will differ from the 27 Sep 2026 snapshot)
bash run_all.sh                            # processed data, results.json, figures, table bodies, version 2.0 analyses, prose audit
bash build_papers.sh                       # paper_en (pdflatex: main.pdf, main_anon.pdf, titlepage.pdf) and paper_ko (xelatex)
python code/53_flatten_submission.py       # optional: self-contained sources and the submission folder (not part of the deposit)
bash check_release.sh                      # fails if a PDF is older than its sources, the anonymised copy identifies the author, or a file named here is missing
```

`build_papers.sh` stops if references are unresolved, a line runs into the margin by more than 5pt, or an identifying string
appears in the anonymised copy. The anonymised copy is built from the same `main.tex` with the `\ifanon` switch
(`pdflatex -jobname=main_anon "\newif\ifanon\anontrue\input{main.tex}"`).

## List of tables and figures (English manuscript, version 2.0)

| Exhibit | Program | Output |
|---|---|---|
| Table 1 (price ladder), Table 2 (data sources) | manual, sources in notes | `paper_en/main.tex` |
| Table 3 (burdens by group) | `20_analysis.py` → `build_revision_tables.py` | `output/tables/A1_burden_by_group.csv`, `tables/tab_burden_compact.tex` |
| Table 4 (quintiles, broadband) | same, with `audit_extensions.py` (dollar price ratio) | `A2_burden_by_quintile.csv`, `audit_output/broadband_price_comparison.csv`, `tab_quintile.tex` |
| Table 5 (benchmark sensitivity) | `audit_extensions.py` → `build_revision_tables.py` | `audit_output/burden_threshold_sensitivity.csv`, `tab_thresholds.tex` |
| Table 6 (local prices) | `20_analysis.py` → `40_tables_tex.py` | `B1_localization.csv`, `tab_local.tex` |
| Table 7 (storefronts) | same | `results.json`, `tab_store.tex` |
| Table 8 (clustered price slopes) | `audit_extensions.py` → `build_revision_tables.py` | `audit_output/local_price_robustness.csv`, `within_storefront_price_ratios.csv`, `tab_price_revision.tex` |
| Table 9 (Go/Plus by currency sample) | `price_reliability.py` → `build_matched_menu_table.py` | `publication_upgrade/results/matched_menu_currency_sensitivity.csv`, `tab_matched_menu_sensitivity.tex` |
| Table 10 (diffusion gradients) | `20_analysis.py` → `40_tables_tex.py` | `C2_conditional_gradients.csv`, `tab_diffusion.tex` |
| Table 11 (two margins) | same | `D1_two_margins_sample.csv`, `tab_twomargins.tex` |
| Table 12 (gradient-gap sensitivity) | `audit_extensions.py` → `build_revision_tables.py` | `audit_output/cross_provider_gradient_robustness.csv`, `tab_gap_revision.tex` |
| Table 13 (connectivity decomposition) | `20_analysis.py` → `40_tables_tex.py` | `C3_connectivity_decomposition.csv`, `tab_decomp.tex` |
| Table 14 (controls), Table 15 (AUI over time) | same | `tab_controls.tex`, `tab_aui_time.tex` |
| Table 16 (\$500 scenario) | `audit_extensions.py` → `build_revision_tables.py` | `audit_output/pro500_reference_scenario.csv`, `tab_500_scenario.tex` |
| Figures 1, 2, 4, 5, 6 | `30_figures.py` | `output/figures/fig_{burden,prices,dynamics,two_margins,decomp}_en.pdf` |
| Figure 3 | `revision_audit/figure_price_ratio.py` | `paper_en/figures/fig_price_ratio_en.pdf` |

The Korean edition uses the same exhibits: `40_tables_tex.py` and `30_figures.py` write its baseline table bodies and Figures 1, 2,
4, 5 and 6 with Korean labels; `revision_audit/build_revision_tables_ko.py` copies the version 2.0 table bodies from `paper_en/tables/`
with translated row labels, and `revision_audit/figure_price_ratio_ko.py` draws Figure 3.

## References

See the manuscript's reference list; bibliographic metadata were verified against Crossref and arXiv (`research/refs_verified.csv`).

## Changes after version 2.0 (1 October 2026) — Korean edition; not yet deposited

- `paper_ko/main.tex` is now a translation of the version 2.0 English manuscript, which remains the original: same structure,
  labels, tables, figures, references and numbers (xelatex; 34 pages). It replaces the version 1.8 Korean text.
- New: `revision_audit/build_revision_tables_ko.py` (+ `--check`), `revision_audit/figure_price_ratio_ko.py` and
  `verification/en_ko_number_check.py` (29 parts; 666 numbers in the English text; 55 listed language-only differences such as
  month names and number words; no other difference). `run_revision.sh` runs all three.
- `code/30_figures.py`: Korean legend of Figure 6 now reads "AI 이용자/인터넷 이용자 비율"; `code/40_tables_tex.py`: the Korean
  label of the collapsed-pool sample in Table 10 is "합침" (it read "군집", the word used for clustered standard errors). English
  figures and tables unchanged.
- The translation was read against the English text paragraph by paragraph by a second reviewer; one ambiguous sentence (usage
  caps "rather than" withholding frontier models) and 18 minor wording, hedge or terminology points were corrected.
- `code/50_make_docx.py`: version 2.0 table headers and Korean theorem labels; figures rendered with `pdftoppm` (PyMuPDF is no
  longer needed); intermediate files in a temporary folder, so the manuscript folders are not modified.
- `build_papers.sh` and `check_release.sh`: the Korean build record now covers `apalike-doi.bst`.
- The English manuscript, the data and every English output are unchanged; the English PDFs are byte-identical to version 2.0.
  Clean-room rerun: all 245 files of the working copy, including the 30 in `paper_ko/`, are byte-identical after deleting every
  generated file and rerunning the pipeline (`verification/README.md`).

## Changes in version 2.0 (30 September 2026)

Manuscript (English), relative to version 1.8 (the SSRN working paper):

- Title shortened to *Affording Generative AI Across Countries: Uniform Prices, Unequal Burdens*; abstract rewritten (248 words);
  keywords and JEL codes unchanged. The introduction states the contribution (a dated multi-provider audit of local prices)
  and four findings, and relates the paper to Sathish et al. (2024), Kanzamanova and Myeong (2026) and the ITU affordability convention.
- New Section 2.1 on the OpenAI tariff change of 29 September 2026 (two days after the audit): Pro 500 tier, revised Pro 200
  allowance; treated as a separate event, with a \$500 reference-fee scenario (Appendix E, Table 16) and a protocol for
  recording access conditions (Appendix F; field dictionary in `publication_upgrade/access_measurement_fields.csv`).
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

Numbers: all version 1.8 estimates are unchanged (`output/results.json` is identical; `revision_audit/baseline_results_v1.8.json`
is the frozen copy). The only corrected exhibit is the broadband column of Table 4 (see above). (The −0.027 (0.012)
convergence slope printed in versions up to 1.6 was corrected to −0.026 (0.011) in version 1.7, before the SSRN posting.)

Package:

- `run_all.sh` now chains the baseline pipeline and the version 2.0 analyses (`run_revision.sh`), whose table bodies
  supersede the baseline where they overlap (`tab_quintile.tex`); `build_papers.sh` also builds the anonymised copy and the
  title page and rejects identifying strings; `check_release.sh` covers the new files; `code/53_flatten_submission.py` added
  (its output folder `submission/` is distributed separately); `verification/prose_number_audit.py` (292 checks) added and run by
  `run_revision.sh`.
- `revision_audit/`, `publication_upgrade/` and `revision_audit/upstream_validation/` (fresh re-downloads of the Microsoft,
  Anthropic and ITU sources, byte-identical derived files) are the audit and extension scripts written at the revision stage;
  `revision_audit/figure_price_ratio.py` now writes a timestamp-free PDF so that rebuilds are byte-identical.
- Word exports and the intermediate review copies of the revision stage are not shipped; the LaTeX PDFs are the manuscript.
- Clean-room rerun: all 133 generated files (processed data, results.json, table bodies, figures, audit outputs, the four
  PDFs and the submission sources) are byte-identical to the shipped ones (`verification/README.md`).

Version history 1.1–1.8 (28 September 2026): see `README_v1_8.md`.
