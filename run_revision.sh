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
"$REVISION_PYTHON" revision_audit/audit_extensions.py          # headline re-checks, clustered SEs, sensitivities
"$REVISION_PYTHON" revision_audit/figure_price_ratio.py        # Figure 3 (Go/Plus ratio within storefronts)
"$REVISION_PYTHON" revision_audit/build_revision_tables.py     # bodies of tab_burden_compact, tab_quintile, tab_thresholds, tab_price_revision, tab_gap_revision, tab_500_scenario
"$REVISION_PYTHON" revision_audit/build_revision_tables.py --check
"$REVISION_PYTHON" publication_upgrade/price_reliability.py    # plan-matching and currency-sample checks
"$REVISION_PYTHON" publication_upgrade/build_matched_menu_table.py   # body of tab_matched_menu_sensitivity
"$REVISION_PYTHON" publication_upgrade/build_matched_menu_table.py --check
"$REVISION_PYTHON" revision_audit/build_revision_tables_ko.py  # Korean bodies of the seven tables above (row labels only)
"$REVISION_PYTHON" revision_audit/build_revision_tables_ko.py --check
"$REVISION_PYTHON" revision_audit/figure_price_ratio_ko.py     # Figure 3 with Korean labels
"$REVISION_PYTHON" publication_upgrade/verify_tier_model.py    # numerical check of the Appendix A propositions
"$REVISION_PYTHON" verification/prose_number_audit.py          # every number in the prose against the outputs
"$REVISION_PYTHON" verification/en_ko_number_check.py          # the Korean edition prints the same numbers as the English text

if [[ "${1:-}" == "--analysis-only" ]]; then
  echo "Version 2.0 analyses, table bodies and Figure 3 regenerated; prose-number audit and English-Korean number check passed."
  exit 0
fi

command -v pdflatex >/dev/null || { echo "pdflatex is required; use --analysis-only to skip PDF compilation." >&2; exit 1; }
bash build_papers.sh
"$REVISION_PYTHON" code/53_flatten_submission.py
echo "Manuscripts built (paper_en/main.pdf, main_anon.pdf, titlepage.pdf; paper_ko/main.pdf) and submission sources flattened."
