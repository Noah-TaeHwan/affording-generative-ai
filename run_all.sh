#!/usr/bin/env bash
# Rebuild processed data, results, figures and LaTeX tables from the shipped raw extracts.
set -euo pipefail
cd "$(dirname "$0")"
python code/09_appstore_prices.py
python code/10_build_dataset.py
python code/11_data_dictionary.py
python code/20_analysis.py
python code/30_figures.py
python code/40_tables_tex.py
cp output/figures/*_en.pdf paper_en/figures/ && cp output/figures/*_ko.pdf paper_ko/figures/
echo "done: see output/ and paper_*/tables"
