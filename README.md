# Replication package — *Localised Entry, Global Frontier: How Generative-AI Subscriptions Are Priced Across Countries*

TaeHwan Oh (independent researcher; ORCID https://orcid.org/0009-0004-4111-4802) · package version 2.1 · 8 October 2026 ·
DOI https://doi.org/10.5281/zenodo.23006365 (all versions of the record; version 2.1 accompanies the revised manuscript; versions 2.0 and 1.8 are earlier versions of the paper, which carried the title *Affording Generative AI Across Countries: Uniform Prices, Unequal Burdens*)

This package reproduces every table, figure and in-text number of the English manuscript (version 2.1) and
of its Korean edition (a translation of the same text). It follows the structure of the Social Science Data Editors' README template
(https://social-science-data-editors.github.io/template_README/). The changes since version 1.8 are listed at the end.

## How to cite

- Oh, TaeHwan (2026). *Replication package for "Localised Entry, Global Frontier: How Generative-AI Subscriptions Are Priced
  Across Countries"*, version 2.1 [data and code]. Zenodo. https://doi.org/10.5281/zenodo.23006365
- Oh, TaeHwan (2026). *Localised Entry, Global Frontier: How Generative-AI Subscriptions Are Priced Across Countries.* Manuscript,
  version 2.1, 8 October 2026. An earlier version circulated as SSRN working paper 7535900 (29 September 2026) under the title
  *Affording Generative AI Across Countries: Uniform Prices, Unequal Burdens*.

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
| AI Diffusion dataset (AI User Share H1 2025–Q2 2026) and reports | Microsoft AI Economy Institute, `github.com/microsoft/ai-diffusion-report` | commit 507c316 (20 Sep 2026) | MIT | `data/raw/ms_repo/data/AI_Diffusion_Q22026_Update.csv`; copy in `extensions/microsoft_pinned.csv` |
| Technical paper (region-imputed flags) | Misra et al. (2025), arXiv:2511.02781 | v1 | arXiv | cited; flags reproduced in code |
| Anthropic Economic Index, country level | `huggingface.co/datasets/Anthropic/EconomicIndex` | commit 2ea58ff (26 Jun 2026) | data CC-BY, code MIT | derived: `data/raw/anthropic/anthropic_country_*.csv`; raw via script |
| Google AI & Economy ATLAS v1.0 | `ai.google/economy/atlas` | April 2026 sample, published 23 Jul 2026 | see provider | `data/raw/google_atlas/` |
| ITU ICT Price Baskets 2008–2025 | ITU, `itu.int/en/ITU-D/Statistics/Pages/ICTprices` | December 2025 release | ITU terms (attribution) | derived CSVs; workbook via script |
| App Store in-app purchase prices | Apple App Store product pages (`apps.apple.com/<cc>/app/id<app>`) | scraped 27 Sep 2026 (UTC) | public web pages; factual data | `data/raw/appstore/appstore_iap_raw.jsonl` |
| Exchange rates | open.er-api.com (ExchangeRate-API, attribution required); cross-check: fawazahmed0 currency-api | 27 Sep 2026 | provider terms | `data/raw/fx/` |
| OpenAI tariff change of 29 Sep 2026 (Section 2.1, Appendix E) | OpenAI Help Center pages cited in the manuscript | retrieved 29–30 Sep 2026 | provider terms | `extensions/pricing_sources/` (manifest and capture record; the \$500 fee is the only number used) |

Notes. (1) The App Store scrape and exchange rates are point-in-time snapshots; re-running `02_scrape_appstore_prices.py` today
will give different prices. The archive stores the parsed listing records, not the original HTML (Appendix B). (2) Microsoft
pools 36 economies into regional aggregates; `10_build_dataset.py` flags them (`ms_region_imputed`). (3) Anthropic's August-2025
published AUI includes un-geolocated traffic in the denominator; `03_anthropic_country.py` builds a harmonised index
(`aui_geo_baseline`). (4) Namibia's ISO2 code is the string `NA`, which pandas reads as missing by default; every script therefore
reads CSV files with `keep_default_na=False, na_values=[""]`. (5) The World Bank API no longer serves `PA.NUS.PPPC.RF`; the GDP
price-level ratio is computed as `NY.GDP.PCAP.CD / NY.GDP.PCAP.PP.CD` in the year of the GNI data (`plr_gdp`).

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
  tabularx, multirow, natbib, tikz, enumitem, hyperref, xurl); `xelatex` + `bibtex` with `xetexko` (Korean), using the system
  fonts Liberation Serif/Sans/Mono and Noto Serif/Sans CJK KR. The English bibliography style `paper_en/apalike-doi.bst` is
  shipped. `build_papers.sh` fixes `SOURCE_DATE_EPOCH` so that rebuilds are byte-identical.
- Randomness: the bootstrap in `20_analysis.py` (2,000 draws, seed 20260927) and the currency-block resampling in
  `checks/price_reliability.py` (19,999 draws, seed 20260930).
- Runtime: downloads ≈ 10–20 min (App Store scrape: 654 requests); analysis ≈ 20 s; manuscripts ≈ 1 min.

## Package contents

Included: all programs; every raw extract that `run_all.sh` reads; the derived Anthropic and ITU country files; processed data;
results, tables and figures; LaTeX sources, `.bbl` files and compiled PDFs of the English manuscript (identified and anonymised
copies, separate title page) and of the Korean edition; the verification record. The submission files
(`submission/`, generated by `code/53_flatten_submission.py`) are distributed separately and are not part of the deposited package.
Not included (re-downloadable at pinned versions with `code/00_download_sources.sh`): the Anthropic release CSVs (≈450 MB), the
ITU workbook, and Microsoft's report PDFs and repository history.

| Folder | Contents |
|---|---|
| `code/`, `run_all.sh`, `run_revision.sh`, `build_papers.sh`, `check_release.sh` | Pipeline (see *Description of programs*) |
| `data/raw/`, `data/processed/` | Frozen source extracts (including `data/raw/openai/chatgpt_go_rollout.csv`, the dated rollout record with sources); analysis panel and price files |
| `output/` | `results.json` (865 scalars), `tables/*.csv`, `figures/*.pdf, *.png` |
| `paper_en/` | English manuscript: `main.tex`, `titlepage.tex`, `references.bib`, `apalike-doi.bst`, `tables/`, `figures/`, `main.pdf`, `main_anon.pdf`, `titlepage.pdf`, build record |
| `paper_ko/` | Korean edition of the version 2.0 manuscript (translation; same tables, figures, references and numbers): `main.tex`, `references.bib`, `apalike-doi.bst`, `tables/`, `figures/`, `main.pdf`, build record |
| `extensions/` | Version 2.0 and 2.1 analyses: `audit_extensions.py` (clustered inference, sensitivities, headline re-checks), `figure_price_ratio.py`, `build_revision_tables.py`, `go_rollout_analysis.py` (Section 5.5; design fixed in the script before the outcomes were computed, not externally registered), `policy_counterfactuals.py` (Section 5.6), `figure_rollout.py`, and the Korean counterparts `figure_price_ratio_ko.py` and `build_revision_tables_ko.py`; outputs in `audit_output/`; `baseline_results_v1.8.json` (frozen baseline); `upstream_validation/` (provider-file re-download checks); `pricing_sources/` (tariff-change capture record); `AUDIT_REPORT.md` (audit-stage record) |
| `checks/` | Plan-matching and currency-sample checks (`price_reliability.py`), the Go/Plus table (`build_matched_menu_table.py`), numerical verification of Appendix A (`verify_tier_model.py`), the access-conditions field dictionary and protocol of Appendix F |
| `verification/` | `README.md` (clean-room replication record), `prose_number_audit.py` (367 checks of the numbers printed in the prose), `identifying_strings.txt` (strings that must not appear in the anonymised copies) and `en_ko_number_check.py` (the Korean edition prints the same numbers as the English text) |
| `submission/` (not deposited) | Generated by `code/53_flatten_submission.py`: anonymised and identified PDFs, title page, self-contained LaTeX sources and figure files; the hand-written highlights, cover letter, declarations and checklist travel with the separate submission archive |
| `research/refs_verified.csv` | Crossref/arXiv check of bibliographic metadata |
| `README_v1_8.md` | README of the working-paper package (version history 1.1–1.8) |

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
| `code/03_anthropic_country.py` | Country-level Anthropic panel; harmonised AUI | `data/raw/anthropic/anthropic_country_*.csv` |
| `code/05_itu_price_baskets.py` | Tidy ITU price baskets | `data/raw/itu/itu_affordability_latest.csv` |
| `code/06_verify_references.py` | Crossref/arXiv check of bibliographic metadata | `research/refs_verified.csv` |
| `code/09_appstore_prices.py` | Monthly local prices, USD conversion, storefront status | `data/processed/appstore_prices_*.csv` |
| `code/10_build_dataset.py` | Merge all sources | `data/processed/country_panel.csv` |
| `code/11_data_dictionary.py` | Variable descriptions | `data/processed/data_dictionary.csv` |
| `code/20_analysis.py` | Baseline estimates | `output/results.json`, `output/tables/*.csv` |
| `code/30_figures.py` | Figures 1, 3, 4, 5 and C.1 (English and Korean labels) | `output/figures/*.pdf, *.png` |
| `code/40_tables_tex.py` | Baseline LaTeX table bodies | `paper_en/tables/`, `paper_ko/tables/` |
| `extensions/audit_extensions.py` | Independent headline re-checks; currency-clustered price slopes; within-storefront ratios; gradient-gap robustness; benchmark, vintage and broadband-price sensitivities; \$500 scenario | `extensions/audit_output/*.csv, audit_results.json` |
| `extensions/figure_price_ratio.py` | Figure 2 | `paper_en/figures/fig_price_ratio_en.pdf`, `output/figures/fig_price_ratio_en.png` |
| `extensions/build_revision_tables.py` | Bodies of Tables 5, 7, 8, 9, 12 and E.1 (`--check` verifies without writing) | `paper_en/tables/tab_{burden_compact,quintile,thresholds,price_revision,gap_revision,500_scenario}.tex` |
| `extensions/go_rollout_analysis.py` | Section 5.5: case comparison around the ChatGPT Go rollouts (specification recorded in `audit_output/go_rollout_spec.json`; post-hoc robustness labelled) | `audit_output/go_rollout_*.csv`, `audit_results_rollout.json`, `paper_en/tables/tab_rollout.tex` |
| `extensions/policy_counterfactuals.py` | Section 5.6: burden of the \$20 tier under four price schedules and the subsidy to the 2% benchmark | `audit_output/policy_counterfactuals*.csv`, `audit_results_policy.json`, `paper_en/tables/tab_policy.tex` |
| `extensions/figure_rollout.py` | Figure 6 (English and Korean) | `paper_*/figures/fig_rollout_*.pdf`, `output/figures/fig_rollout_*.png` |
| `extensions/build_revision_tables_ko.py` | Korean bodies of the version 2.0/2.1 tables: the English bodies with translated row labels only (`--check` verifies) | `paper_ko/tables/` |
| `extensions/figure_price_ratio_ko.py` | Figure 2 with Korean labels | `paper_ko/figures/fig_price_ratio_ko.pdf`, `output/figures/fig_price_ratio_ko.png` |
| `checks/price_reliability.py` | Plan-candidate audit; currency-sample, leave-one-currency-out and block-resampling checks of the Go/Plus ratio; NumPy re-implementation of HC3/CR1 | `checks/results/*.csv, price_reliability_summary.json` |
| `checks/build_matched_menu_table.py` | Body of Table 6 (`--check` verifies) | `paper_en/tables/tab_matched_menu_sensitivity.tex` |
| `checks/verify_tier_model.py` | Numerical check of the thresholds and gradients of Appendix A | `checks/tier_model_verification.json` |
| `verification/prose_number_audit.py` | Compares every number in the prose of `paper_en/main.tex` with the pipeline outputs, 367 checks (exit 1 on any mismatch) | console report |
| `verification/en_ko_number_check.py` | Compares, part by part, the numbers written in the Korean and English manuscripts; differences that come from the language alone are listed with reasons (exit 1 on any other difference) | console report |
| `run_all.sh` | Steps 09–40, figures, then `run_revision.sh --analysis-only` | all of the above |
| `run_revision.sh` | The version 2.0 analyses (and, without `--analysis-only`, the manuscripts and submission files) | as listed |
| `build_papers.sh` | Compile `paper_en` (`main.pdf`, anonymised `main_anon.pdf`, `titlepage.pdf`) and `paper_ko`; check for identifying strings in the anonymised copy; record the sources of each PDF | `paper_*/main.pdf`, `paper_*/main.pdf.sources.sha256` |
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
bash run_all.sh                            # processed data, results.json, figures, table bodies, version 2.0 analyses, prose audit
bash build_papers.sh                       # paper_en (pdflatex: main.pdf, main_anon.pdf, titlepage.pdf) and paper_ko (xelatex)
python code/53_flatten_submission.py       # optional: self-contained sources and the submission folder (not part of the deposit)
bash check_release.sh                      # fails if a PDF is older than its sources, the anonymised copy identifies the author, or a file named here is missing
```

`build_papers.sh` stops if references are unresolved, a line runs into the margin by more than 5pt, or an identifying string
appears in the anonymised copy. The anonymised copy is built from the same `main.tex` with the `\ifanon` switch
(`pdflatex -jobname=main_anon "\newif\ifanon\anontrue\input{main.tex}"`).

## List of tables and figures (English manuscript, version 2.1)

| Exhibit | Program | Output |
|---|---|---|
| Table 1 (price ladder), Table 2 (data sources) | manual, sources in notes | `paper_en/main.tex` |
| Table 7 (burdens by group) | `20_analysis.py` → `build_revision_tables.py` | `output/tables/A1_burden_by_group.csv`, `tables/tab_burden_compact.tex` |
| Table 8 (quintiles, broadband) | same, with `audit_extensions.py` (dollar price ratio) | `A2_burden_by_quintile.csv`, `audit_output/broadband_price_comparison.csv`, `tab_quintile.tex` |
| Table 9 (benchmark sensitivity) | `audit_extensions.py` → `build_revision_tables.py` | `audit_output/burden_threshold_sensitivity.csv`, `tab_thresholds.tex` |
| Table 3 (local prices) | `20_analysis.py` → `40_tables_tex.py` | `B1_localization.csv`, `tab_local.tex` |
| Table 4 (storefronts) | same | `results.json`, `tab_store.tex` |
| Table 5 (clustered price slopes) | `audit_extensions.py` → `build_revision_tables.py` | `audit_output/local_price_robustness.csv`, `within_storefront_price_ratios.csv`, `tab_price_revision.tex` |
| Table 6 (Go/Plus by currency sample) | `price_reliability.py` → `build_matched_menu_table.py` | `checks/results/matched_menu_currency_sensitivity.csv`, `tab_matched_menu_sensitivity.tex` |
| Table 10 (diffusion gradients) | `20_analysis.py` → `40_tables_tex.py` | `C2_conditional_gradients.csv`, `tab_diffusion.tex` |
| Table 11 (two margins) | same | `D1_two_margins_sample.csv`, `tab_twomargins.tex` |
| Table 12 (gradient-gap sensitivity) | `audit_extensions.py` → `build_revision_tables.py` | `audit_output/cross_provider_gradient_robustness.csv`, `tab_gap_revision.tex` |
| Table 13 (rollout comparison) | `go_rollout_analysis.py` | `audit_output/go_rollout_summary.csv`, `go_rollout_robustness.csv`, `tab_rollout.tex` |
| Table 14 (policy counterfactuals) | `policy_counterfactuals.py` | `audit_output/policy_counterfactuals_groups.csv`, `tab_policy.tex` |
| Table B.1 (Anthropic releases) | manual, from `data/raw/anthropic/DATA_DICTIONARY.md` | `paper_en/main.tex` |
| Table C.1 (connectivity decomposition) | `20_analysis.py` → `40_tables_tex.py` | `C3_connectivity_decomposition.csv`, `tab_decomp.tex` |
| Table D.1 (controls), Table D.2 (AUI over time) | same | `tab_controls.tex`, `tab_aui_time.tex` |
| Table E.1 (\$500 scenario) | `audit_extensions.py` → `build_revision_tables.py` | `audit_output/pro500_reference_scenario.csv`, `tab_500_scenario.tex` |
| Figures 1, 3, 4, 5 and C.1 | `30_figures.py` | `output/figures/fig_{prices,burden,dynamics,two_margins,decomp}_en.pdf` |
| Figure 2 | `extensions/figure_price_ratio.py` | `paper_en/figures/fig_price_ratio_en.pdf` |
| Figure 6 | `extensions/figure_rollout.py` | `paper_en/figures/fig_rollout_en.pdf` |

The Korean edition uses the same exhibits: `40_tables_tex.py` and `30_figures.py` write its baseline table bodies and Figures 1, 3,
4, 5 and C.1 with Korean labels; `extensions/build_revision_tables_ko.py` copies the version 2.0/2.1 table bodies from `paper_en/tables/`
with translated row labels, `extensions/figure_price_ratio_ko.py` draws Figure 2 and `extensions/figure_rollout.py` Figure 6.

## References

See the manuscript's reference list; bibliographic metadata were verified against Crossref and arXiv (`research/refs_verified.csv`).

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
- The translation was read against the English text paragraph by paragraph by a second reviewer; one ambiguous sentence (usage
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
