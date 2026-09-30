# Replication package — *Affording Generative AI: Uniform Prices, Unequal Burdens, and the Two Margins of AI Diffusion*

TaeHwan Oh (independent researcher; ORCID https://orcid.org/0009-0004-4111-4802) · package version 1.8 · 28 September 2026 ·
DOI https://doi.org/10.5281/zenodo.23006366

This package reproduces every table, figure and in-text number of the English and Korean manuscripts. It follows the
structure of the Social Science Data Editors' README template (https://social-science-data-editors.github.io/template_README/).

## How to cite

Please cite the package and the paper:

- Oh, TaeHwan (2026). *Replication package for "Affording Generative AI: Uniform Prices, Unequal Burdens, and the Two
  Margins of AI Diffusion"*, version 1.8 [data and code]. Zenodo. https://doi.org/10.5281/zenodo.23006366
- Oh, TaeHwan (2026). *Affording Generative AI: Uniform Prices, Unequal Burdens, and the Two Margins of AI Diffusion.*
  Working paper, September 2026.

## Overview

The code (i) downloads World Bank indicators and third-party usage datasets, (ii) scrapes local App Store prices of
ChatGPT, Claude and Gemini in every storefront, (iii) builds a country-level panel (`data/processed/country_panel.csv`),
(iv) runs the analysis (`output/results.json`, `output/tables/*.csv`), (v) draws the figures and (vi) writes LaTeX table
bodies for both manuscripts. From the shipped raw extracts, steps (iii)–(vi) run in about 15 seconds.

## Data availability and provenance statements

All data are publicly available. The author has legitimate access to all data used in this manuscript and the
package includes the inputs used by `run_all.sh`, including derived Anthropic and ITU country files. The large
Anthropic release files (approximately 450 MB) and the ITU workbook are not bundled. `code/00_download_sources.sh`
retrieves the Anthropic files at the pinned commit and the ITU workbook from the dated provider URL so that the
country-level extractions can also be rebuilt. A dated provider URL is not an immutable version guarantee.

| Source | Provider / URL | Version used | Licence | Files in package |
|---|---|---|---|---|
| World Development Indicators; Global Findex 2025; country classification FY2027 | World Bank API `api.worldbank.org/v2` | extracted 27 Sep 2026 (WDI last updated 13 Jul 2026) | CC BY 4.0 | `data/raw/wb/` |
| AI Diffusion dataset (AI User Share H1 2025–Q2 2026) and reports | Microsoft AI Economy Institute, `github.com/microsoft/ai-diffusion-report` | commit 507c316 (20 Sep 2026) | MIT | `data/raw/ms_repo/data/AI_Diffusion_Q22026_Update.csv` |
| Technical paper (region-imputed flags) | Misra et al. (2025), arXiv:2511.02781 | v1 | arXiv | cited; flags reproduced in code |
| Anthropic Economic Index, country level | `huggingface.co/datasets/Anthropic/EconomicIndex` | commit 2ea58ff (26 Jun 2026) | data CC-BY, code MIT | derived: `data/raw/anthropic/anthropic_country_*.csv`; raw via script |
| Google AI & Economy ATLAS v1.0 | `ai.google/economy/atlas` | April 2026 sample, published 23 Jul 2026 | see provider | `data/raw/google_atlas/` |
| ITU ICT Price Baskets 2008–2025 | ITU, `itu.int/en/ITU-D/Statistics/Pages/ICTprices` | December 2025 release | ITU terms (attribution) | derived CSVs; workbook via script |
| App Store in-app purchase prices | Apple App Store product pages (`apps.apple.com/<cc>/app/id<app>`) | scraped 27 Sep 2026 (UTC) | public web pages; factual data | `data/raw/appstore/appstore_iap_raw.jsonl` |
| Exchange rates | open.er-api.com (ExchangeRate-API, attribution required); cross-check: fawazahmed0 currency-api | 27 Sep 2026 | provider terms | `data/raw/fx/` |

Notes. (1) The App Store scrape and exchange rates are point-in-time snapshots; re-running `02_scrape_appstore_prices.py`
today will give different prices. (2) Microsoft pools 36 economies into regional aggregates; `10_build_dataset.py`
flags them (`ms_region_imputed`). (3) Anthropic's August-2025 published AUI includes un-geolocated traffic in the
denominator; `03_anthropic_country.py` builds a harmonised index (`aui_geo_baseline`). (4) Namibia's ISO2 code is the
string `NA`, which pandas reads as missing by default; every script therefore reads CSV files with
`keep_default_na=False, na_values=[""]` (version 1.1 fixes two scripts that did not, which had dropped Namibia's nine prices).
(5) The World Bank API no longer serves `PA.NUS.PPPC.RF`; the GDP price-level ratio is computed as
`NY.GDP.PCAP.CD / NY.GDP.PCAP.PP.CD` in the year of the GNI data (`plr_gdp`).

## Computational requirements

- Tested with Python 3.11.15, pandas 3.0.2, numpy 2.4.4, statsmodels 0.15.0, scipy 1.17.1, matplotlib 3.10.9,
  requests 2.33.1, openpyxl 3.1.5 (and python-docx 1.2.0 + pandoc 3.1.3 for the optional Word version).
  Install with `pip install -r requirements.txt`.
- Fonts for figures: Liberation Sans (English labels) and NanumGothic (Korean labels; Debian/Ubuntu package `fonts-nanum`),
  both TrueType so that they embed cleanly in PDF. Where they are missing, `30_figures.py` falls back to Arial/AppleGothic
  or DejaVu Sans; the figures then look slightly different and are not byte-identical to the shipped files.
- Platforms: on other operating systems the CSV outputs can differ in the last printed digit (floating-point formatting);
  `output/results.json` and the LaTeX tables, which are rounded, are unaffected.
- LaTeX (TeX Live 2023): `pdflatex` + `bibtex` (English); `xelatex` + `bibtex` with the `ko.TeX`/`xetexko` package
  (Korean), using the system fonts Liberation Serif/Sans/Mono and Noto Serif/Sans CJK KR. Both manuscripts compile on
  Overleaf, where these fonts are installed (upload the folder; set the compiler to XeLaTeX for Korean). On a computer
  without them, install the fonts or change the font names in the preamble of `paper_ko/main.tex`.
- Randomness: the only stochastic step is the bootstrap in `20_analysis.py` (2,000 draws, seed 20260927).
- Runtime: downloads ≈ 10–20 min (App Store scrape: 654 requests); analysis ≈ 15 s. Disk: ≈ 500 MB with raw Anthropic files.

## Package contents

Included: all programs; every raw extract that `run_all.sh` reads; the derived Anthropic and ITU country files; processed
data; results, tables and figures; LaTeX sources, `.bbl` files and compiled PDFs of both manuscripts; the reference check.
Not included (re-downloadable at pinned versions with `code/00_download_sources.sh`): the Anthropic release CSVs (≈450 MB),
the ITU workbook, and Microsoft's report PDFs and repository history.

## Licence

The code (`code/`, `run_all.sh`, `build_papers.sh`, `check_release.sh`) is released under the MIT License. Data compiled by the author—the App Store price
extraction and the author's contributions to the processed files—are released under Creative Commons Attribution 4.0
International (CC BY 4.0). Values taken from third-party sources remain subject to the providers' licences listed above;
Microsoft's MIT licence is in `data/raw/ms_repo/LICENSE.md`. The English and Korean manuscripts (PDF and LaTeX prose)
are copyright 2026 TaeHwan Oh, all rights reserved; they are not covered by the MIT or CC BY grants. Generated tables
and figures retain the terms applicable to their underlying code and data. See `LICENSE.txt`.

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
| `code/20_analysis.py` | All estimates | `output/results.json`, `output/tables/*.csv` |
| `code/30_figures.py` | Figures (English and Korean labels) | `output/figures/*.pdf, *.png` |
| `code/40_tables_tex.py` | LaTeX table bodies | `paper_en/tables/`, `paper_ko/tables/` |
| `build_papers.sh` | Compile both manuscripts; record the sources of each PDF | `paper_*/main.pdf`, `paper_*/main.pdf.sources.sha256` |
| `check_release.sh` | Pre-release check: PDFs current, files named here present | exit status |
| `code/50_make_docx.py` | Optional Word version of a compiled manuscript (`python code/50_make_docx.py ko`); needs pandoc and python-docx | `output/Affording_Generative_AI_KO.docx` |

## Instructions to replicators

```bash
pip install -r requirements.txt
bash code/00_download_sources.sh          # optional: only needed to rebuild Anthropic/ITU derived files
python code/03_anthropic_country.py        # optional (requires the raw Anthropic files)
python code/05_itu_price_baskets.py        # optional (requires the ITU workbook)
# python code/01_download_wb.py            # re-downloads World Bank data (will reflect later WDI updates)
# python code/02_scrape_appstore_prices.py # re-scrapes prices (will differ from the 27 Sep 2026 snapshot)
python code/09_appstore_prices.py
python code/10_build_dataset.py
python code/11_data_dictionary.py
python code/20_analysis.py
python code/30_figures.py
python code/40_tables_tex.py
bash build_papers.sh                      # compiles paper_en (pdflatex) and paper_ko (xelatex), with bibtex
bash check_release.sh                     # fails if a PDF is older than its sources or a README file is missing
```
Or run `bash run_all.sh` for the analysis steps from the shipped extracts, then `bash build_papers.sh`.
`build_papers.sh` stops if references are unresolved or a line runs into the margin by more than 5pt, and writes
`paper_*/main.pdf.sources.sha256`, the hashes of the sources each PDF was built from.

## List of tables and figures

| Exhibit (English numbering) | Program | Output |
|---|---|---|
| Table 1 (price ladder), Table 2 (data) | manual, sources in notes | `paper_*/main.tex` |
| Table 3 (burdens) | `20_analysis.py` → `40_tables_tex.py` | `output/tables/A1_burden_by_group.csv`, `tables/tab_burden.tex` |
| Table 4 (quintiles, broadband) | same | `A2_burden_by_quintile.csv`, `tab_quintile.tex` |
| Table 5 (local prices) | same | `B1_localization.csv`, `tab_local.tex` |
| Table 6 (storefronts) | same | `results.json`, `tab_store.tex` |
| Table 7 (diffusion gradients) | same | `C2_conditional_gradients.csv`, `tab_diffusion.tex` |
| Table 8 (decomposition) | same | `C3_connectivity_decomposition.csv`, `tab_decomp.tex` |
| Table 9 (two margins) | same | `D1_two_margins_sample.csv`, `tab_twomargins.tex` |
| Table 10 (scenarios) | same | `E1_scenarios.csv`, `tab_scen.tex` |
| Tables 11–13 (appendix) | same | `T1_case_countries.csv`, `tab_case.tex`, `tab_controls.tex`, `tab_aui_time.tex` |
| Figures 1–6 | `30_figures.py` | `output/figures/fig_{burden,prices,decomp,dynamics,two_margins,scen}_{en,ko}.pdf` |

## References

See the manuscripts' reference lists; bibliographic metadata were verified against Crossref and arXiv (`research/refs_verified.csv`).

## Changes in version 1.1 (28 September 2026)

Responding to an independent cross-review:
- `20_analysis.py`, `30_figures.py` and `11_data_dictionary.py` now read `country_panel.csv` with `keep_default_na=False`,
  so Namibia (ISO2 `NA`) is no longer dropped from the price analysis (1,634 → 1,643 price observations; localisation
  elasticities change by at most 0.00021; the share of lower-middle-income economies whose cheapest local tier meets
  the 2% benchmark is 38% rather than 36%).
- `10_build_dataset.py` adds the GDP price-level ratio (`plr_gdp`) to compare with the Atlas/PPP proxy;
  `09_appstore_prices.py` records the lowest listed monthly price (`price_usd_min_candidate`) and `20_analysis.py` reports
  the sensitivity for the three cells that list two monthly prices.
- `30_figures.py`: the decomposition figure is labelled as a difference in group means of logs (not medians); fonts fall
  back to installed families without warnings.

## Changes in version 1.2 (28 September 2026)

Responding to the second round of the cross-review:
- `10_build_dataset.py` takes the GDP price-level ratio in the year of the GNI data (four economies—Kuwait, Macao SAR,
  Oman and Sint Maarten—previously used a GDP ratio one year later); the comparison in the manuscripts' footnote is now
  a median difference of 3.1% (90th percentile 8.3%) and an income elasticity of 0.224 for the GDP ratio.
- The manuscripts describe App Store prices as listed prices rather than checkout prices, and two sentences on the
  extensive margin state the observation (no decline in adoption with the burden) without implying a tested price effect.
- A stale "Hulten-consistent" comment in `20_analysis.py` was corrected. Results are otherwise unchanged.

## Changes in version 1.3 (28 September 2026)

- Licence chosen (MIT for code, CC BY 4.0 for the author's data; `LICENSE.txt` added).
- The manuscripts' declarations on AI use and competing interests completed; two appendix sentences on App Store
  listings clarified. No results changed.

## Changes in version 1.4 (28 September 2026)

- The prose of both manuscripts was edited for readability (fewer dashes and semicolons, plainer wording in English;
  less translation-style phrasing in Korean). An automated comparison confirms that every number, citation,
  cross-reference and equation, the body of every table and the Declarations section are unchanged (a few table notes
  and captions were reworded); no code, data or results changed.

## Changes in version 1.5 (28 September 2026, final)

Responding to the cross-review of version 1.4: three sentences whose wording had become broader than the evidence were
narrowed—the AI access paradox is now stated for the task-level gains illustrated (Proposition 2 allows convergence if
gains for low-income economies were more than about eleven times larger), vendors are said to barely localise
frontier-tier prices, and the conclusion refers to who can access or afford frontier models. No numbers changed.

## Changes in version 1.6 (28 September 2026)

- The author's ORCID iD (https://orcid.org/0009-0004-4111-4802) was added to the title footnote of both manuscripts and
  to this README. No code, data, results, tables, figures or other manuscript text changed.

## Changes in version 1.7 (28 September 2026)

- Section 5.3 of both manuscripts now reports the convergence regression as −0.026 (s.e. 0.011), as in
  `output/results.json` (`conv_log_b` = −0.026465, `conv_log_se` = 0.011462). Version 1.6 printed −0.027 (0.012),
  a double-rounding error; the conclusion is unchanged.
- Appendix B no longer states that every number in the text is written to `output/results.json`. It now says that every
  number can be reproduced from the package: most are in `results.json`, and the rest are simple calculations from those
  values or are read from the output tables, the processed data or the scripts.
- The Zenodo DOI of this package (https://doi.org/10.5281/zenodo.23006366) was added to the title footnote and
  the data-availability statement of both manuscripts, and to this README (header and "How to cite").
- A page break before Appendix D keeps Table 11 ahead of it; the English PDF now has 29 pages. No code, data or results
  changed.


## Changes in version 1.8 (28 September 2026)

No estimate, table or figure changed; `output/results.json` is identical to version 1.7.

- Denominator. The abstracts and introductions describe the 60% share as the working-age population of the 201
  economies covered (98.6% of the world's), not the whole world. The estimate (60.112%) is unchanged.
- Interpretation narrowed to what the data measure:
  - The Anthropic AI Usage Index pools the free and paid accounts of one vendor. The abstract, introduction,
    Section 5.4, discussion and conclusion now call it per-capita Claude use that proxies the frontier margin
    imperfectly, and Section 3.2 no longer states as fact that it weights paid users heavily.
  - The rise in its income gradient between August 2025 and February 2026 is described as a change in measured
    Claude use, because the releases added Max accounts and, from April 2026, Cowork sessions and monthly windows.
  - "Adoption among internet users" is defined as the ratio of AI users to internet users, an accounting construct,
    and the price argument in Section 5.3 is stated as holding other things equal.
- The data-availability statement says the package is deposited at Zenodo, and the DOI no longer runs into the
  margin (the English version 1.7 PDF overran by 75pt). The English abstract has 249 words.
- Appendix B distinguishes bundled inputs and derived country files from the unbundled Anthropic release files and
  ITU workbook.
- The manuscript copyright scope is explicit: all rights reserved for manuscript PDFs and LaTeX prose, MIT for code,
  CC BY 4.0 for the author's data contributions, with third-party provider terms preserved.
- `build_papers.sh` (with fixed timestamps, so rebuilds are byte-identical) and `check_release.sh` were added. A first build of this version still carried the version 1.7
  PDFs because the LaTeX sources had been edited but not recompiled; the build record and check now catch that.
- `verification/README.md` documents a clean rerun of `run_all.sh` and independent checks of the derived Anthropic
  and ITU files.
