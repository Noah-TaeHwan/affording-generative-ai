# Verification record — package version 3.1 (17 October 2026)

## Version 3.1 (17 October 2026) — revised manuscript, within-firm relative prices, schedule validation, cross-channel check

Verification passes (17 October 2026). The text and the generators were revised in two further internal verification passes,
as `README.md` (*Changes in version 3.1*, second and third verification passes) lists; the checks below were repeated on the
final files and the figures in this section are the final ones. The audit found one rounding inconsistency, corrected in the
text (Section 7.2: "0.1–1.6% of GNI" now reads 0.08–1.55%, as in Section 5.5), and one inequality that the tables contradicted
("the only slopes beyond ±0.01" among the frontier pairs: X Premium Plus relative to SuperGrok is 0.011); the frontier pairs
are now all oriented as the higher tier relative to the standard tier and the text names both directions.

- **Prose-number audit.** `verification/prose_number_audit.py` was rewritten for the version 3.1 text of `paper_en/main.tex`
  (its infrastructure is that of version 3.0; the ledger is new). It compares every numerical statement in the abstract,
  Sections 1–8, the Declarations and Appendices A–G — including the numbers typed by hand in table notes, captions and column
  headers and in the hand-written Tables 1, 2, A.1, B.1 and G.1 — with the pipeline value: `output/results.json`,
  `output/results_wave2.json` (now including the `rel_*`/`relplus_*`/`relfront_*`/`stacked_*`/`incr_*`/`incrusd_*` keys of
  `code/13_relative_prices.py`, the `taxabs_*`, `<plan>_n_exact`, `_above3`/`_above10` and robustness keys of
  `code/12_default_panel.py`, the `guard_*`/`applevel_*`/`wave2_dedup_*` keys of `code/09b_wave2_items.py`, `val_*` of
  `code/14_default_validation.py`, `vint_*` of `code/15_vintage_test.py` and `xch_*` of `code/16_cross_channel.py`), the
  `output/tables/W1`–`W15b` CSVs, the outputs of `extensions/` and `checks/` (among them `checks/results/sim_output.txt` for the
  calibrated examples of Appendix A), the READMEs of the raw extracts (`data/raw/web`, `data/raw/appstore_wave2`,
  `data/raw/fx_hist`), the constants read from the generators (`wave2_common.py`, `09b`, `12`–`16`, `41`, `42`), or a direct
  recomputation from the processed data and the raw records. Table bodies are not part of it (the generators' `--check` modes
  verify them). Run from the package root: `python3 verification/prose_number_audit.py --strict` (options `--list-pins`,
  `--list-unresolved`, `--no-coverage`); `run_revision.sh` runs it with `--strict`. Final result on the identified manuscript (version 3.1, final files):
  **1,952 checks, 0 mismatches** (1,203 printed numbers against a pipeline value, 243 number words, 129 dates, 238 conditions,
  139 numbers pinned to the text, 0 unresolved entries); coverage: 1,792 numerals in 1,168 lines (1,379 compared, 97 pinned,
  178 names and labels, 138 notation), 0 numerals, 0 number words and 0 month names unaccounted for. In the anonymised copy
  (the `\ifanon` branch only, no `extensions/zenodo_record.json`) the identified-only passages (author line with the preprint
  number and version, date line, archive versions of the data-availability paragraph) are skipped and the audit makes
  1,935 checks, 0 mismatches, with full coverage. A mutation test (15 edits to digits, months and number words across the
  manuscript) was detected in all 15 cases. During the rewrite the audit found one stale number, corrected in the text
  (Appendix A: the Character.AI+ over Lite increment slope "−0.21 (s.e. 0.05)" is −0.059 (0.012), as in Section 5.4), and
  four statements that were reworded rather than renumbered: "29 with priced subscription items" (28 apps have one; 29 have
  a priced item of any type), "t_c lies between one and about 1.27" (now the 5th–95th percentile band 0.98–1.29 and the
  extremes 0.46 and 1.57), "Google AI Plus 2 TB, slope −0.016" (the USD item slope is 0.026; −0.016 is its slope relative to
  ChatGPT Plus) and "including the 45 economies without a storefront" (31 of them have income data); three non-numerical
  statements were made exact (the income groups in which the frontier tiers' median deviation is zero, the HC3–HC1 difference
  of the standard errors, "about half or more of the storefronts").
- **Generators and their checks.** Every table body is written by code and verified by the `--check` modes of
  `code/41_tables_wave2.py`, `code/42_tables_relative.py`, `extensions/build_revision_tables.py` and
  `checks/build_matched_menu_table.py`; `checks/verify_tier_model.py` (Propositions A.1 and A.2, parsing the two quoted
  sentences of Appendix A) and `checks/sim_check.py` (Propositions A.1–A.4, Table A.1 and the increment test; output
  `checks/results/sim_output.txt`, byte-identical between runs) pass.
- **Reproduction of the independent re-analyses.** The analyses supplied with the internal audit of version 3.0 (annual-as-monthly
  guard, within-firm relative slopes, the 12-pair table, the validation of the schedule, the vintage test and the cross-channel
  comparison, all written against the version 3.0 files with the standard library) were re-implemented in the pipeline with pandas
  (`code/09b`, `13`–`16`). Every headline number is reproduced; the differences, each traced to a definition, are listed in
  `README.md` (*Changes in version 3.1*): 151 guarded cells against 149 (fallback rule for storefronts without a multiplier),
  Gemini 100 GB 0.033 against 0.062, Google AI Plus relative to AI Pro −0.012 against −0.023 and the Character.AI+ − Lite
  increment −0.059 against −0.21 (the guard, applied before these statistics), the Microsoft web medians −31.0%/−9.0% against
  −31.1%/−9.1% (rounding order), the Google Play lower-income ratios without Bangladesh, six X Corp items in the stacked
  regression, and no consumables-only schedule.
- **Clean-room rerun.** On a fresh copy of this package (Linux, x86-64, Python 3.11; `bash run_all.sh && bash run_revision.sh`,
  2 min 44 s for the final files), all 349 files of the package including the separately distributed `submission/`
  folder are byte-identical to the working copy (`SOURCE_DATE_EPOCH` 1792108800). `bash check_release.sh`: release check
  passed, including the thirteen hygiene patterns of version 3.1 (author's surname in citation form, time zone and location
  phrases including the collection time zone, review-history wording, item codes, the publisher's name).
- **Anonymised package.** `code/54_anonymised_package.py` writes 263 files (232 text files contain none of the 24 strings in
  `verification/identifying_strings.txt` or of the 13 forbidden patterns; equal to a fresh build; the Korean-edition files and
  the Zenodo file size and MD5 are left out, the collection time zone of the audit notes reads "local time" and the web-store
  extracts carry their UTC timestamps only). Test of the zip in a fresh directory: `bash run_all.sh &&
  bash build_papers.sh` exit 0; none of the shipped files changed; the regenerated outputs are byte-identical to the public
  package's except the files that the script redacts (`extensions/audit_output/audit_results.json`, whose Zenodo record number is
  `null`, and the redacted scripts and records); the compiled manuscript has the same text as `paper_en/main_anon.pdf`, empty PDF
  metadata and no identifying string. The prose-number audit of the anonymised copy makes 1,935 checks, 0 mismatches.


## Version 3.0 (16 October 2026) — revised manuscript, second price wave

Version 3.0 adds the second App Store wave of 16 October 2026 (34 apps × 218 storefront codes and the 30-app default panel;
`code/02b_scrape_wave2.py`, `09b_wave2_items.py`, `12_default_panel.py`, `41_tables_wave2.py`, `31_figures_wave2.py`), restructures
the English manuscript around the deviation of listed prices from Apple's default schedule, the within-storefront price ratio,
the within-firm contrasts and the price stability between the waves, adds the supply side of the model (Proposition A.2,
predictions P1–P5), and demotes the usage-indicator analysis to a descriptive section (the ChatGPT Go rollout comparison is
Appendix E, without causal language; the version 2.1 convergence proposition, \$500 scenario appendix and policy counterfactual
section are removed, the policy schedule table stays as Table D.7). The baseline data, `output/results.json` and every
version 2.1 table body and figure that the text still uses are unchanged. The Korean edition is not part of this version
(the version 2.1 Korean edition is in the version 2.1 record; `paper_ko/` holds only the table bodies written by
`code/40_tables_tex.py`; `build_papers.sh`, `run_revision.sh` and `check_release.sh` skip the Korean steps when
`paper_ko/main.tex` is absent). Checks on this working copy:

- **Independent reproduction of the second wave.** Before the wave-2 scripts were written into the package, the headline
  numbers supplied with the raw records were recomputed with an independent pandas implementation from the JSONL files (parsing,
  modal monthly price, HC1 slopes, revealed default schedule). All matched, with these differences, which the package follows:
  the SuperGrok Heavy slope is 0.027 (not 0.041 as first reported); the alternative-exchange-rate slopes at plan level are 0.040
  (Plus) and 0.143 (Go); the "LMIC" medians are over low- and lower-middle-income storefronts together (the first analysis used
  low-income only for some items); the tie rule of the revealed default is "unique mode with share at least one half" (111 clean
  storefronts, default slope 0.0327), the other tie rules being reported as a sensitivity (`results_wave2.json`, keys
  `default_tie_*`); Microsoft 365 Personal is 0.163 log points, 15.0%, below the default in the median poorer storefront.
- **Prose-number audit.** The version 3.0 ledger of `verification/prose_number_audit.py` made **1,184 checks, 0 mismatches**
  (739 printed numbers against a pipeline value, 161 number words, 106 dates, 102 conditions, 76 pins; a mutation test of 581
  single edits was detected in 579 cases) and found and corrected four statements ("four" for three nested thresholds;
  "114--120" for 113--120 Anthropic economies, twice; "2.5" for 2.6 months of exposure) and two that were reworded. It is
  superseded by the version 3.1 ledger described above.
- **Model.** `checks/verify_tier_model.py` was extended to the four-option menu: 280,000 argmax comparisons of the choice
  rule (0 mismatches); the Proposition A.1 gradients against central differences (maximum error 1.2e-9); Proposition A.2 on a
  grid of 18 values of s in [0.3, 2] and 109 values of the Lerner index L (finite-difference elasticity against ξ/(ξ+L) and the
  closed form (A.8), maximum differences 7e-10 and 3e-10; β strictly decreasing in L for every s; β(0) = 1; the printed values
  0.63/0.30/0.05 and 0.76/0.44/0.09 reproduced to two decimals). `checks/tier_model_verification.json` is deterministic.
- **References.** Every reference added in version 3.0 was checked against Crossref or arXiv (`code/06_verify_references.py`,
  `research/refs_verified.csv`: 76 DOI/arXiv records found; Varian 1985 and Goldberg–Knetter 1997 have no Crossref record of the
  journal version and are cited without DOI). Waldfogel's 2020 Spotify paper replaced a mis-keyed entry; Shiller–Waldfogel 2011
  is cited only for uniform pricing (it is not a cross-country study); the statements about Apple's pricing are rewritten around
  Apple's own wording ("accounting for foreign exchange rates and certain taxes").
- **Build.** English: pdflatex, no warnings, no overfull or underfull boxes, no unresolved reference, **41 pages** (identified
  and anonymised copies, same page count); the anonymised copy contains none of the 23 strings of
  `verification/identifying_strings.txt` and `submission/journal_strings.txt`; title page 1 page. `SOURCE_DATE_EPOCH=1792108800`
  (16 October 2026). Word count from the PDF text: about 11,800 words from the introduction to the declarations (tables and
  captions included), 6,400 in the appendices, abstract 249 words. Every rendered page was inspected.
- **Clean-room rerun.** Copying the package, deleting every generated file (175 of 299 files: processed data 13,
  `results.json`, `results_wave2.json` and output tables 16, figures 38, LaTeX table bodies 35, `extensions/audit_output/` 20,
  `checks/results/` and `tier_model_verification.json` 12, manuscript PDFs, `.bbl` files and build records 6, generated
  `submission/` files 35) and running `bash run_all.sh && bash run_revision.sh && bash check_release.sh` (102 seconds; Python
  3.11, pandas 3.0.2, statsmodels 0.15.0, numpy 2.4.4, scipy 1.17.1, TeX Live pdfTeX) gave exit status 0, "release check passed", and
  **all 299 files byte-identical** to the working copy. The first rerun had failed because `code/41_tables_wave2.py` (Table 7)
  reads `extensions/audit_output/policy_counterfactuals_groups.csv`, which `run_revision.sh` writes; the step was moved into
  `run_revision.sh` after `policy_counterfactuals.py`, and leftover Korean files of version 2.1 that no step regenerates were
  removed from the package.
- **Anonymised package.** `code/54_anonymised_package.py` builds the anonymised copy (230 files; Korean table bodies, title page,
  identified README, submission folder and research record excluded; eight files redacted); the scan of binary files ignores
  strings of three characters or fewer, which compressed data matches by chance. Test of the zip in a fresh directory:
  `bash run_all.sh && bash run_revision.sh` exit 0 (86 seconds; 1,174 audit checks, the identified-only checks skipped); the
  compiled manuscript has the same text as `paper_en/main_anon.pdf`, empty PDF metadata, and no identifying string or journal
  name.

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
- **Meaning.** A second reader read every paragraph, caption and table note of the two texts side by side and reported one
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
