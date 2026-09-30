#!/usr/bin/env bash
# Rebuild everything from the shipped raw extracts: processed data, results.json, figures and LaTeX table bodies
# (baseline pipeline, unchanged since version 1.8), then the additional analyses of version 2.0 (run_revision.sh),
# whose outputs supersede the baseline where they overlap (paper_en/tables/tab_quintile.tex).
# Reads frozen local inputs only; no network requests. Manuscript PDFs: bash build_papers.sh (or run_revision.sh without --analysis-only).
set -euo pipefail
cd "$(dirname "$0")"
python code/09_appstore_prices.py
python code/10_build_dataset.py
python code/11_data_dictionary.py
python code/20_analysis.py
python code/30_figures.py
python code/40_tables_tex.py
cp output/figures/*_en.pdf paper_en/figures/ && cp output/figures/*_ko.pdf paper_ko/figures/
bash run_revision.sh --analysis-only
echo "done: see output/, revision_audit/audit_output/, publication_upgrade/results/ and paper_*/tables"
