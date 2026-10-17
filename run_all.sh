#!/usr/bin/env bash
# Rebuild everything from the shipped raw extracts: processed data, results.json, figures and LaTeX table bodies
# (baseline pipeline, unchanged since version 1.8), the second price wave (09b, 12-16, 31_wave2), then the additional analyses of
# versions 2.0-3.1 (run_revision.sh, which also writes the wave-2 table bodies with code/41_tables_wave2.py and 42_tables_relative.py),
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
# second price wave (16 Oct 2026; scraped by code/02b_scrape_wave2.py, not run here): item prices and slopes with the
# annual-as-monthly guard, Apple's default schedule, the default-free relative prices (13_relative_prices.py, which reads the
# outputs of 12), the validation of the default schedule (14_default_validation.py), the vintage test of the deviations
# (15_vintage_test.py; reads the exchange-rate snapshots of data/raw/fx_hist/), the cross-channel check against the Microsoft web
# store and Google Play (16_cross_channel.py; reads data/raw/web/ and the 15 Oct 2026 rates; 14-16 read only the outputs of 12 and raw
# files) and the figures (31_figures_wave2.py writes its PDFs straight to paper_en/figures/, like
# extensions/figure_rollout.py, so the cp line below does not need to carry them). The wave-2 table bodies (code/41_tables_wave2.py
# and code/42_tables_relative.py) are written by run_revision.sh, because Table 7 also needs extensions/policy_counterfactuals.py.
python code/09b_wave2_items.py
python code/12_default_panel.py
python code/13_relative_prices.py
python code/14_default_validation.py
python code/15_vintage_test.py
python code/16_cross_channel.py
python code/31_figures_wave2.py
cp output/figures/*_en.pdf paper_en/figures/
# the Korean edition is not part of the anonymised copy of the package (40_tables_tex.py still writes Korean table bodies)
if [[ -f paper_ko/main.tex ]]; then
  cp output/figures/*_ko.pdf paper_ko/figures/
fi
bash run_revision.sh --analysis-only
echo "done: see output/, extensions/audit_output/, checks/results/ and paper_*/tables"
