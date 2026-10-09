# Verification record — package version 2.1 (8 October 2026)

## Version 2.1 (8 October 2026) — revised manuscript

Version 2.1 adds two analyses (Section 5.5, the ChatGPT Go rollout comparison; Section 5.6, policy counterfactuals), rewrites
the front and back of the English manuscript, and synchronises the Korean edition. Data, `output/results.json` and every
version 2.0 table body and figure are unchanged. Checks on this working copy:

- **Design fixed before the outcomes.** `extensions/go_rollout_analysis.py` writes its design (cohorts, comparison group,
  windows, regression, permutation scheme with seed 20261008 and 2,000 draws) to `audit_output/go_rollout_spec.json` before any
  outcome is read. The design was not registered externally and no time-stamped record predating the results exists outside the
  author's working files, so the manuscript says so (Sections 5.5 and 6.5); the post-hoc robustness columns (region fixed effects, non-high-income comparison, percentage-point outcome) are
  labelled as such in `go_rollout_robustness.csv` and in the text. The rollout dates in `data/raw/openai/chatgpt_go_rollout.csv`
  carry their sources (OpenAI release notes and help pages, TechCrunch, TechCabal).
- **Prose-number audit.** `verification/prose_number_audit.py` now makes **367 checks, 0 mismatches**, adding the Plus-to-Go
  multiples, every number of Sections 5.5 and 5.6 and their table notes, the β* note of Appendix A and the illustrative
  convergence arithmetic of Section 6.2. During drafting it caught five wrong statements (a permutation p stated as "none of
  2,000" when one draw exceeded the contrast; \$85 for a median of \$84.4999; "1.6% of GNI" for 1.55%; "less than half of the gap"
  for a ratio of 0.51--0.53; "a fraction of a percent of GNI" for a low-income median of 1.55%); all were corrected. An
  external read then found log differences quoted as percentages ("fell 18%" for $-0.180$ log points); the text now quotes
  $e^{\Delta}-1$ (16.5%, 15.3%, 2.5%, 4.9%) and the audit checks the conversions.
- **Korean edition.** `paper_ko/main.tex` follows the version 2.1 English text section by section (39 pages, xelatex, no
  warnings, no overfull or underfull boxes). `verification/en_ko_number_check.py` compares **31 parts, 880 numbers in the
  English text; 117 listed language-only differences; no other difference**. The nine version 2.0/2.1 Korean table bodies are
  written by `build_revision_tables_ko.py` from the English bodies (row labels only; `--check` passes); Figure 6 is drawn by
  `figure_rollout.py ko` from the same data. New tables and the figure were inspected visually.
- **Build.** English: pdflatex, no warnings or overfull boxes, 38 pages (identified and anonymised copies); the anonymised copy
  contains none of the identifying strings; title page 1 page. Word count from the PDF text: about 13,600 words from the
  introduction to the references (tables and captions included), 3,100 in the appendices, abstract 246 words.
- **Clean-room rerun.** Copying the package, deleting every generated file (163 of 268 files: processed data 4, `results.json`
  and output tables 10, figures 44, LaTeX table bodies 38, `extensions/audit_output/` 20, `checks/results/`
  and `tier_model_verification.json` 12, manuscript PDFs, `.bbl` files and build records 9, generated `submission/` files 26)
  and running `bash run_all.sh && bash build_papers.sh && python code/53_flatten_submission.py && bash check_release.sh`
  (46 seconds; same environment as section 1, `SOURCE_DATE_EPOCH=1790726400`) gave exit status 0, "release check passed", and
  **all 268 files byte-identical** to the working copy, the four PDFs and the two new permutation outputs included. The rerun was
  repeated after the folder rename and the wording changes listed above, with the same result.
- **Journal formatting and anonymised package (8 October 2026, later the same day).** Appendix tables, figures and equations
  are numbered per appendix (`\counterwithin` after `\appendix`: Table B.1, C.1, D.1, D.2, E.1, Figure C.1, Eq. (A.1)--(A.7);
  main-text numbering unchanged; checked in the PDF text of both editions, no unresolved reference). The submission figure
  files are written as `Figure_1.pdf` … `Figure_6.pdf`, `Figure_C1.pdf` from the order of `\includegraphics` in `main.tex`
  (`code/53_flatten_submission.py --check-figures`). `code/54_anonymised_package.py` builds the anonymised copy of the package
  (192 files; the Korean edition, title page, citation file, identified README and Zenodo record excluded; eight files redacted);
  it and `check_release.sh` scan every text file of the zip and the text of the anonymised manuscript for the 17 strings in
  `verification/identifying_strings.txt` (0 occurrences). Test of the zip in a fresh directory: `bash run_all.sh && bash
  build_papers.sh` exit 0; none of the 192 shipped files changed; the regenerated outputs are byte-identical to the public
  package's except `extensions/audit_output/audit_results.json`, whose Zenodo record number is redacted to `null`; the compiled
  manuscript has the same text as `paper_en/main_anon.pdf`, empty PDF metadata and no identifying string. The public
  clean-room rerun was repeated after these changes (275 files including the separately distributed `submission/` folder, all byte-identical, 47 seconds). The corresponding author's full
  postal address, which the submission title page must carry, is kept in `submission/postal_address.txt` (not deposited) and
  inserted only into `submission/Title_Page.tex`/`.pdf` by `code/53_flatten_submission.py`; the same script inserts the
  journal-specific lines of the title page (journal name, issue label, article type, submission history) from
  `submission/title_page_journal.tex`, so the deposited `paper_en/titlepage.tex`/`.pdf` names no journal; `check_release.sh`
  fails if the address, a journal name or a manuscript-number prefix (`submission/journal_strings.txt`) appears in any
  deposited file or PDF.

## Korean edition (after version 2.0, 1 October 2026)

The Korean manuscript in `paper_ko/` was replaced by a translation of the version 2.0 English text. Checks on this working copy:

- **Same numbers as the English text.** `verification/en_ko_number_check.py` splits both manuscripts into the same 29 parts
  (front matter, each section and subsection, declarations, appendices) and compares the numbers written in digits in the prose,
  headings, captions, table notes and equations. The English text contains 666 such numbers. After removing month numbers
  (English writes month names) and "1인당" (per capita), 55 differences remain, each listed in the script with its reason (number
  words such as "nine plans" = "9개 요금제", "one-seventh" = "7분의 1", "richest fifth" = "최상위 20%", "quintile" = "5분위").
  No other difference. A mutation test (changing one printed number in the Korean text, e.g. 0.711 to 0.717) is flagged.
- **Same table bodies.** The seven version 2.0 table bodies of the Korean edition are written by
  `extensions/build_revision_tables_ko.py` from the English bodies, replacing only the row label and failing if any other cell
  differs; the baseline bodies come from `code/40_tables_tex.py` as before.
- **Same structure.** Labels (59, in the same order), cross-references (70), citations (98), table inputs (14) and figures (6)
  coincide with the identified English manuscript; the Korean bibliography (`.bbl`, 69 entries) is identical to the English one.
- **Meaning.** A second reviewer read every paragraph, caption and table note of the two texts side by side and reported one
  ambiguous Korean sentence (usage caps "rather than by withholding frontier models", which could be read the other way round)
  and 18 minor hedge, scope or terminology points (e.g. "suggests", "lower-income" as a relative term, "군집" for both
  clustered and collapsed); all were corrected, and no omitted or added content was found.
- **Build.** `xelatex` with no warnings, no overfull or underfull boxes and no missing glyphs (34 pages); pages inspected visually.
- **Clean-room rerun.** Deleting every generated file (as in section 1, now including the 17 Korean table bodies and 7 Korean
  figures) and running `bash run_all.sh && bash build_papers.sh && python code/53_flatten_submission.py && bash check_release.sh`
  gave exit status 0 and all 245 files of the working copy byte-identical, including the 30 files in `paper_ko/`. The three
  English PDFs are byte-identical to version 2.0.

The version 2.0 record follows. Three layers of checks, run on a fresh copy of this package on Linux (Debian, x86-64): a **clean-room rerun** of the whole
pipeline including the manuscripts, an **audit of every number printed in the prose**, and the **upstream-source
reconstruction** carried over from the audit stage. The version 1.8 record is kept at the end.

## 1. Clean-room rerun

Procedure: copy the package; delete every generated file — `data/processed/*.csv` (4), `output/results.json`,
`output/tables/*.csv` (9), `output/figures/*` (25), `paper_en/figures/*` and `paper_ko/figures/*` (13), `paper_en/tables/*.tex`
(17) and `paper_ko/tables/*.tex` (11), `extensions/audit_output/*` except the audit-stage record `rerun_comparison.json`,
`checks/results/*` and `tier_model_verification.json`, all PDFs, `.bbl` files and build records, and the generated
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
| `extensions/audit_output/*` (12), `checks/results/*` (11), `tier_model_verification.json` | 24 | Byte-identical |
| `paper_en/main.pdf`, `main_anon.pdf`, `titlepage.pdf`, `paper_ko/main.pdf`, `.bbl` files, build records | 9 | Byte-identical (fixed `SOURCE_DATE_EPOCH`); text extracted with `pdftotext` identical |
| `submission/latex_source_*/`, `submission/figures/` (the submission folder is distributed separately, not in the deposited package) | 20 | Byte-identical; each flattened `.tex` compiles standalone and its PDF text equals the corresponding `paper_en` PDF |

The anonymised copy (`main_anon.pdf`) contains none of the strings `taehwan`, `orcid`, `noah.taehwan`, `zenodo`, `paju`
(checked by `build_papers.sh` and `check_release.sh`), and its PDF metadata carry no title or author.

## 2. Prose-number audit

`verification/prose_number_audit.py` (run by `run_revision.sh`) compares every numerical statement in the abstract, main text
and Appendices B, C and E of `paper_en/main.tex` with the pipeline value: `output/results.json`, the CSV and JSON outputs of
`extensions/` and `checks/`, or a direct recomputation from the processed data and the raw App Store records
(for example the 654/500/135/19 request outcomes, the 45 redirected codes, the 1.6% exchange-rate agreement, the 98.6%
population coverage, the currency-cluster sizes 102/25/37 and the West African pooled series). A value passes if it equals the
pipeline value rounded to the printed precision. **292 checks, 0 mismatches.** Table bodies are not part of this audit because
they are written by code and verified by the clean-room rerun above.

Independently of the Python pipeline, `extensions/audit_extensions.py` recomputes 14 headline quantities (the four \$20
burden medians, the 60.112% population share, and the slopes, standard errors and sample sizes of the main regressions) and
`checks/price_reliability.py` re-implements OLS, HC3 and currency-clustered CR1 covariances in NumPy; both match
`results.json` and statsmodels to six decimals (`audit_output/independent_headline_checks.csv`,
`checks/results/price_reliability_summary.json`). `checks/verify_tier_model.py` checks the
thresholds and gradient formulas of Appendix A numerically (50,000 utility comparisons; 4,000 gradient components against finite
differences).

## 3. Upstream-source reconstruction (audit stage, 30 September 2026)

Recorded in `extensions/upstream_validation/upstream_verification.json`. The four Anthropic release CSVs and three supporting
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
