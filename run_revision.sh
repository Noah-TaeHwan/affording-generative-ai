#!/usr/bin/env bash
# Additional analyses of version 3.1 (robustness, sensitivity and verification outputs), then the manuscripts.
# run_all.sh calls this script after the baseline pipeline; it can also be run on its own once output/results.json
# and data/processed/ exist. Reads frozen local inputs only; no network requests.
set -euo pipefail
cd "$(dirname "$0")"

if [[ $# -gt 1 ]] || [[ $# -eq 1 && "$1" != "--analysis-only" ]]; then
  echo "Usage: bash run_revision.sh [--analysis-only]" >&2
  exit 2
fi
REVISION_PYTHON="${REVISION_PYTHON:-python3}"
# The Korean edition (paper_ko/main.tex) is absent by design in version 3.0 and version 3.1: HAVE_KO is then 0 and the steps that only
# serve it are skipped. The title page (paper_en/titlepage.tex) is not part of the anonymised copy of the package either.
HAVE_KO=0
if [[ -f paper_ko/main.tex ]]; then HAVE_KO=1; fi
"$REVISION_PYTHON" extensions/audit_extensions.py          # headline re-checks, clustered SEs, sensitivities
"$REVISION_PYTHON" extensions/figure_price_ratio.py        # Figure 3 (Go/Plus ratio within storefronts)
"$REVISION_PYTHON" extensions/build_revision_tables.py     # bodies of Tables D.2, D.5, D.6 and D.8 (tab_price_revision, tab_quintile, tab_thresholds, tab_gap_revision); tab_burden_compact and tab_500_scenario are still written but no longer used in the text
"$REVISION_PYTHON" extensions/build_revision_tables.py --check
"$REVISION_PYTHON" checks/price_reliability.py    # plan-matching and currency-sample checks
"$REVISION_PYTHON" checks/build_matched_menu_table.py   # body of tab_matched_menu_sensitivity (Table D.3)
"$REVISION_PYTHON" checks/build_matched_menu_table.py --check
"$REVISION_PYTHON" extensions/go_rollout_analysis.py       # Appendix E, Table E.1 body: ChatGPT Go rollout, a descriptive comparison; specification fixed in the script before the outcomes were computed, not externally registered
"$REVISION_PYTHON" extensions/policy_counterfactuals.py     # Appendix D: price schedules and subsidy counterfactuals, Table D.7 body
"$REVISION_PYTHON" code/41_tables_wave2.py                 # wave 2: bodies of Tables 3-7 (Table 7 uses the policy counterfactuals) and of the validation, vintage and cross-channel tables (reads W11, W11b, W14, W15, W15b of 14-16)
"$REVISION_PYTHON" code/41_tables_wave2.py --check
"$REVISION_PYTHON" code/42_tables_relative.py              # wave 2: bodies of the annual-as-monthly guard, relative-price, increment and tax-absorption tables (reads W6, W8-W10, W12, W13)
"$REVISION_PYTHON" code/42_tables_relative.py --check
if [[ $HAVE_KO -eq 1 ]]; then
  "$REVISION_PYTHON" extensions/figure_rollout.py             # Figure E.1 (English and Korean)
  "$REVISION_PYTHON" extensions/build_revision_tables_ko.py  # Korean bodies of the revision tables (row labels only)
  "$REVISION_PYTHON" extensions/build_revision_tables_ko.py --check
  "$REVISION_PYTHON" extensions/figure_price_ratio_ko.py     # Figure 3 with Korean labels
else
  "$REVISION_PYTHON" extensions/figure_rollout.py en         # Figure E.1 (English only: no Korean edition in this package)
fi
"$REVISION_PYTHON" checks/verify_tier_model.py    # numerical check of Propositions A.1 and A.2 of Appendix A (four-option model); writes checks/tier_model_verification.json
"$REVISION_PYTHON" checks/sim_check.py > /dev/null   # standard-library checks of Propositions A.1-A.4 and of the increment test (Appendix A); writes checks/results/sim_output.txt
"$REVISION_PYTHON" verification/prose_number_audit.py --strict         # every number in the prose against the outputs
if [[ $HAVE_KO -eq 1 ]]; then
  "$REVISION_PYTHON" verification/en_ko_number_check.py          # the Korean edition prints the same numbers as the English text
fi

if [[ "${1:-}" == "--analysis-only" ]]; then
  if [[ $HAVE_KO -eq 1 ]]; then
    echo "Version 3.1 analyses, table bodies and figures regenerated; prose-number audit (no mismatches; unresolved entries, if any, are listed above) and English-Korean number check passed."
  else
    echo "Version 3.1 analyses, table bodies and figures regenerated; prose-number audit finished without mismatches (unresolved entries, if any, are listed above)."
  fi
  exit 0
fi

command -v pdflatex >/dev/null || { echo "pdflatex is required; use --analysis-only to skip PDF compilation." >&2; exit 1; }
bash build_papers.sh
if [[ -f paper_en/titlepage.tex ]]; then
  "$REVISION_PYTHON" code/53_flatten_submission.py
  "$REVISION_PYTHON" code/54_anonymised_package.py           # anonymised copy of this package for review
  echo "Manuscripts built (paper_en/main.pdf, main_anon.pdf, titlepage.pdf; paper_ko/main.pdf only when the Korean edition is present), submission sources flattened and anonymised package written."
else
  echo "Manuscript built (paper_en/main.pdf, identical to main_anon.pdf in this anonymised package); the submission files are assembled from the public package."
fi
