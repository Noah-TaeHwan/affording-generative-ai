# Verification record — package version 1.8

Checks run on 28 September 2026 on macOS (Apple silicon) against a fresh copy of this package. They separate
**bundled-input replication** (rerunning `run_all.sh` on the shipped extracts) from **upstream-source
reconstruction** (rebuilding the derived Anthropic and ITU files from the original provider files).

## 1. Bundled-input replication: clean rerun of `run_all.sh`

Procedure:

1. Delete all 72 generated files: `data/processed/*.csv` (4), `output/results.json`, `output/tables/*.csv` (9),
   `output/figures/*` (24), `paper_en/figures/*.pdf` and `paper_ko/figures/*.pdf` (12), and
   `paper_en/tables/*.tex` and `paper_ko/tables/*.tex` (22).
2. Run `bash run_all.sh`.
3. Compare every regenerated file with the shipped one.

Environment: Python 3.11.14 with numpy 2.4.6, pandas 3.0.3, scipy 1.17.1, statsmodels 0.14.6, matplotlib 3.10.9 and
openpyxl 3.1.5. This deliberately differs from the pins in `requirements.txt` (numpy 2.4.4, pandas 3.0.2,
statsmodels 0.15.0) to test robustness to minor library versions.

Result: exit status 0 in about 30 seconds; all 72 files regenerated.

| Output | Files | Result |
|---|---|---|
| `output/results.json` | 1 | Identical file: 865 keys, all values equal as stored (6 decimals) |
| LaTeX table bodies `paper_*/tables/*.tex` | 22 | Byte-identical |
| CSV files (processed data and output tables) | 13 | 7 byte-identical; in the other 6 the same rows, columns and missing cells, with numbers differing only in the last floating-point digit (largest relative difference 9.8e-13 across 59,536 cells) |
| Figures `*.pdf`, `*.png` | 36 | Not byte-identical: font rendering and bounding boxes differ by a few pixels across library versions and installed fonts; the plotted data come from the identical CSV and JSON inputs |

Every number printed in the manuscripts is in, or computed directly from, `results.json`, the table bodies, the
output tables or the processed data (Appendix B). All of these match, so the rerun reproduces the printed numbers.

Independently of the Python code, 19 headline values (the median \$20 burdens by income group, the 60.112%
working-age population share, and the slopes, HC3 standard errors and sample sizes of the main regressions, including
the 0.371/0.711 two-margin elasticities and the −0.026 (0.011) convergence slope) were recomputed with separate code
from `data/processed/country_panel.csv`. All 19 match `results.json` to its 6-decimal precision.

Troubleshooting: on macOS, compiled Python extensions downloaded by a sandboxed process that marks files as
quarantined can be refused at import ("library load disallowed by system policy"). Installing the requirements from
an ordinary terminal avoids this; it is an environment issue, not a package issue.

## 2. Upstream-source reconstruction

| Derived file | Source | Check | Result |
|---|---|---|---|
| `data/raw/anthropic/anthropic_country_latest.csv` and `_wide.csv` | Anthropic EconomicIndex, commit 2ea58ff75e4247d26810c37f10c179edc2466cac, release 2026-06-26 | Rebuilt independently with the Python standard library and compared row by row | 16,236 long rows and 235 wide rows match; no differences |
| ITU price-basket country files | ITU ICT Price Baskets workbook, December 2025 | Workbook cells read independently and compared with the shipped long and wide files | 41,853 long rows and 221 economies match; no differences |

## 3. Manuscripts

`bash build_papers.sh` with TeX Live 2026 (pdfTeX 1.40.29 for English, XeTeX 0.999998 for Korean) builds the English
manuscript (29 pages) and the Korean manuscript (30 pages) with no unresolved references and no line running into
the margin by more than 5pt. `bash check_release.sh` then confirms that both PDFs were built from the shipped sources.
