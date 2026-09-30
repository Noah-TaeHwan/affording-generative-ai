# Verification record — package version 2.0 (30 September 2026)

Three layers of checks, run on a fresh copy of this package on Linux (Debian, x86-64): a **clean-room rerun** of the whole
pipeline including the manuscripts, an **audit of every number printed in the prose**, and the **upstream-source
reconstruction** carried over from the audit stage. The version 1.8 record is kept at the end.

## 1. Clean-room rerun

Procedure: copy the package; delete every generated file — `data/processed/*.csv` (4), `output/results.json`,
`output/tables/*.csv` (9), `output/figures/*` (25), `paper_en/figures/*` and `paper_ko/figures/*` (13), `paper_en/tables/*.tex`
(17) and `paper_ko/tables/*.tex` (11), `revision_audit/audit_output/*` except the audit-stage record `rerun_comparison.json`,
`publication_upgrade/results/*` and `tier_model_verification.json`, all PDFs, `.bbl` files and build records, and the generated
part of `submission/` — then run

```bash
bash run_all.sh && bash build_papers.sh && python code/53_flatten_submission.py && bash check_release.sh
```

Environment: Python 3.11.15 with numpy 2.4.4, pandas 3.0.2, scipy 1.17.1, statsmodels 0.15.0, matplotlib 3.10.9; TeX Live 2023
(pdfTeX 1.40.25, XeTeX 0.999995) with Liberation and Noto CJK fonts; `SOURCE_DATE_EPOCH=1790726400`.

Result: exit status 0 for the pipeline, the build and the flattening (36 seconds in total); `check_release.sh` then reported
only the hand-written submission files that the procedure had deleted (highlights, cover letter, declarations, checklist), as it should;
without a `submission/` folder at all (the deposited package) it passes.
Every one of the **133 regenerated files is byte-identical** to the shipped file:

| Output | Files | Result |
|---|---|---|
| `data/processed/*.csv` | 4 | Byte-identical |
| `output/results.json` (865 scalars), `output/tables/*.csv` | 10 | Byte-identical |
| `output/figures/*.pdf, *.png`, `paper_*/figures/*.pdf` | 38 | Byte-identical (timestamps are suppressed in the PDF metadata) |
| LaTeX table bodies `paper_en/tables/*.tex`, `paper_ko/tables/*.tex` | 28 | Byte-identical; the `--check` modes of `build_revision_tables.py` and `build_matched_menu_table.py` also passed |
| `revision_audit/audit_output/*` (12), `publication_upgrade/results/*` (11), `tier_model_verification.json` | 24 | Byte-identical |
| `paper_en/main.pdf`, `main_anon.pdf`, `titlepage.pdf`, `paper_ko/main.pdf`, `.bbl` files, build records | 9 | Byte-identical (fixed `SOURCE_DATE_EPOCH`); text extracted with `pdftotext` identical |
| `submission/latex_source_*/`, `submission/figures/` (the submission folder is distributed separately, not in the deposited package) | 20 | Byte-identical; each flattened `.tex` compiles standalone and its PDF text equals the corresponding `paper_en` PDF |

The anonymised copy (`main_anon.pdf`) contains none of the strings `taehwan`, `orcid`, `noah.taehwan`, `zenodo`, `paju`
(checked by `build_papers.sh` and `check_release.sh`), and its PDF metadata carry no title or author.

## 2. Prose-number audit

`verification/prose_number_audit.py` (run by `run_revision.sh`) compares every numerical statement in the abstract, main text
and Appendices B, C and E of `paper_en/main.tex` with the pipeline value: `output/results.json`, the CSV and JSON outputs of
`revision_audit/` and `publication_upgrade/`, or a direct recomputation from the processed data and the raw App Store records
(for example the 654/500/135/19 request outcomes, the 45 redirected codes, the 1.6% exchange-rate agreement, the 98.6%
population coverage, the currency-cluster sizes 102/25/37 and the West African pooled series). A value passes if it equals the
pipeline value rounded to the printed precision. **292 checks, 0 mismatches.** Table bodies are not part of this audit because
they are written by code and verified by the clean-room rerun above.

Independently of the Python pipeline, `revision_audit/audit_extensions.py` recomputes 14 headline quantities (the four \$20
burden medians, the 60.112% population share, and the slopes, standard errors and sample sizes of the main regressions) and
`publication_upgrade/price_reliability.py` re-implements OLS, HC3 and currency-clustered CR1 covariances in NumPy; both match
`results.json` and statsmodels to six decimals (`audit_output/independent_headline_checks.csv`,
`publication_upgrade/results/price_reliability_summary.json`). `publication_upgrade/verify_tier_model.py` checks the
thresholds and gradient formulas of Appendix A numerically (50,000 utility comparisons; 4,000 gradient components against finite
differences).

## 3. Upstream-source reconstruction (audit stage, 30 September 2026)

Recorded in `revision_audit/upstream_validation/upstream_verification.json`. The four Anthropic release CSVs and three supporting
files were re-downloaded from Hugging Face commit `2ea58ff75e4247d26810c37f10c179edc2466cac` and the ITU workbook from its
documented URL; running the package's `03_anthropic_country.py` and `05_itu_price_baskets.py` on them regenerated all six derived
files byte-identically (16,236 / 235 / 6,920 / 5 / 41,853 / 221 rows). A direct extraction of the May 2026 AUI from the raw CSV
matched all 120 World Bank-matched values and reproduced the n = 96 regression (slope 0.711136928, HC3 s.e. 0.035923227).
Microsoft's Q2 2026 CSV at commit `507c31611c2af77abf44de43036f3ea1d599c248` was re-downloaded and was byte-identical.

Not reconstructed from upstream: the App Store pages (the archive stores parsed listing records, not HTML), the World Bank API
pulls (the API serves later vintages), the Google ATLAS file and the exchange-rate snapshots; these are frozen extracts whose
processing is covered by layer 1.

## Version 1.8 record (28 September 2026)

Checks run on macOS (Apple silicon) against a fresh copy of package version 1.8, with Python 3.11.14, numpy 2.4.6, pandas 3.0.3,
scipy 1.17.1, statsmodels 0.14.6, matplotlib 3.10.9 and openpyxl 3.1.5 — deliberately different from the pins in
`requirements.txt` to test robustness to minor library versions. `run_all.sh` regenerated all 72 generated files of that version:
`results.json` identical (865 keys), 22 table bodies byte-identical, 7 of 13 CSV files byte-identical and the other 6 equal up to
the last floating-point digit (largest relative difference 9.8e-13 across 59,536 cells), figures equal in content but not in bytes
(font rendering). 19 headline values were recomputed with separate code from `data/processed/country_panel.csv` and matched
`results.json` to six decimals. `build_papers.sh` with TeX Live 2026 built both manuscripts with no unresolved references and no
line running into the margin by more than 5pt.

Troubleshooting: on macOS, compiled Python extensions downloaded by a sandboxed process that marks files as quarantined can be
refused at import ("library load disallowed by system policy"). Installing the requirements from an ordinary terminal avoids
this; it is an environment issue, not a package issue.
