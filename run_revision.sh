#!/usr/bin/env bash
# Additional analyses of version 2.0 (robustness, sensitivity and verification outputs), then the manuscripts.
# run_all.sh calls this script after the baseline pipeline; it can also be run on its own once output/results.json
# and data/processed/ exist. Reads frozen local inputs only; no network requests.
set -euo pipefail
cd "$(dirname "$0")"

if [[ $# -gt 1 ]] || [[ $# -eq 1 && "$1" != "--analysis-only" ]]; then
  echo "Usage: bash run_revision.sh [--analysis-only]" >&2
  exit 2
fi
REVISION_PYTHON="${REVISION_PYTHON:-python3}"
# The Korean edition (paper_ko/main.tex) and the title page (paper_en/titlepage.tex) are not part of the anonymised copy
# of the package: the steps that only serve them are skipped there.
HAVE_KO=0
if [[ -f paper_ko/main.tex ]]; then HAVE_KO=1; fi
"$REVISION_PYTHON" extensions/audit_extensions.py          # headline re-checks, clustered SEs, sensitivities
"$REVISION_PYTHON" extensions/figure_price_ratio.py        # Figure 2 (Go/Plus ratio within storefronts)
"$REVISION_PYTHON" extensions/build_revision_tables.py     # bodies of tab_burden_compact, tab_quintile, tab_thresholds, tab_price_revision, tab_gap_revision, tab_500_scenario
"$REVISION_PYTHON" extensions/build_revision_tables.py --check
"$REVISION_PYTHON" checks/price_reliability.py    # plan-matching and currency-sample checks
"$REVISION_PYTHON" checks/build_matched_menu_table.py   # body of tab_matched_menu_sensitivity
"$REVISION_PYTHON" checks/build_matched_menu_table.py --check
"$REVISION_PYTHON" extensions/go_rollout_analysis.py       # Section 5.5: ChatGPT Go rollout comparison (design fixed before outcomes), Table 13 body
"$REVISION_PYTHON" extensions/policy_counterfactuals.py     # Section 5.6: price schedules and subsidy counterfactuals, Table 14 body
if [[ $HAVE_KO -eq 1 ]]; then
  "$REVISION_PYTHON" extensions/figure_rollout.py             # Figure 6 (English and Korean)
  "$REVISION_PYTHON" extensions/build_revision_tables_ko.py  # Korean bodies of the version 2.0/2.1 tables (row labels only)
  "$REVISION_PYTHON" extensions/build_revision_tables_ko.py --check
  "$REVISION_PYTHON" extensions/figure_price_ratio_ko.py     # Figure 2 with Korean labels
else
  "$REVISION_PYTHON" extensions/figure_rollout.py en         # Figure 6 (English only: no Korean edition in this package)
fi
"$REVISION_PYTHON" checks/verify_tier_model.py    # numerical check of the Appendix A propositions
"$REVISION_PYTHON" verification/prose_number_audit.py          # every number in the prose against the outputs
if [[ $HAVE_KO -eq 1 ]]; then
  "$REVISION_PYTHON" verification/en_ko_number_check.py          # the Korean edition prints the same numbers as the English text
fi

if [[ "${1:-}" == "--analysis-only" ]]; then
  if [[ $HAVE_KO -eq 1 ]]; then
    echo "Version 2.1 analyses, table bodies and Figures 2 and 6 regenerated; prose-number audit and English-Korean number check passed."
  else
    echo "Version 2.1 analyses, table bodies and Figures 2 and 6 regenerated; prose-number audit passed."
  fi
  exit 0
fi

command -v pdflatex >/dev/null || { echo "pdflatex is required; use --analysis-only to skip PDF compilation." >&2; exit 1; }
bash build_papers.sh
if [[ -f paper_en/titlepage.tex ]]; then
  "$REVISION_PYTHON" code/53_flatten_submission.py
  "$REVISION_PYTHON" code/54_anonymised_package.py           # anonymised copy of this package for the reviewers
  echo "Manuscripts built (paper_en/main.pdf, main_anon.pdf, titlepage.pdf; paper_ko/main.pdf), submission sources flattened and anonymised package written."
else
  echo "Manuscript built (paper_en/main.pdf, identical to main_anon.pdf in this anonymised package); the submission files are assembled from the public package."
fi
