#!/usr/bin/env bash
# 00_download_sources.sh -- fetch third-party source files at the exact versions used in the paper.
# World Bank data and App Store prices are retrieved by 01_download_wb.py and 02_scrape_appstore_prices.py.
# The App Store scrape and exchange rates are date-specific (27 Sep 2026); the snapshots used in the paper are
# shipped in data/raw/appstore and data/raw/fx and should NOT be overwritten if you want to reproduce the paper.
set -euo pipefail
cd "$(dirname "$0")/.."
RAW=data/raw

# Microsoft AI Economy Institute, AI Diffusion dataset (commit 507c316, 20 Sep 2026; MIT licence)
mkdir -p $RAW/ms_repo/data
curl -fsSL -o $RAW/ms_repo/data/AI_Diffusion_Q22026_Update.csv \
  https://raw.githubusercontent.com/microsoft/ai-diffusion-report/507c31611c2af77abf44de43036f3ea1d599c248/data/AI_Diffusion_Q22026_Update.csv

# Anthropic Economic Index (HuggingFace, commit 2ea58ff..., data CC-BY, code MIT) -- about 450 MB in total
HF=https://huggingface.co/datasets/Anthropic/EconomicIndex/resolve/2ea58ff75e4247d26810c37f10c179edc2466cac
A=$RAW/anthropic
mkdir -p $A/release_2025_09_15 $A/release_2026_01_15 $A/release_2026_03_24 $A/release_2026_06_26
curl -fsSL -o $A/release_2025_09_15/aei_enriched_claude_ai_2025-08-04_to_2025-08-11.csv $HF/release_2025_09_15/data/output/aei_enriched_claude_ai_2025-08-04_to_2025-08-11.csv
for f in working_age_pop_2024_country.csv gdp_2024_country.csv iso_country_codes.csv; do
  curl -fsSL -o $A/release_2025_09_15/$f $HF/release_2025_09_15/data/intermediate/$f
done
curl -fsSL -o $A/release_2026_01_15/aei_raw_claude_ai_2025-11-13_to_2025-11-20.csv $HF/release_2026_01_15/data/intermediate/aei_raw_claude_ai_2025-11-13_to_2025-11-20.csv
curl -fsSL -o $A/release_2026_03_24/aei_raw_claude_ai_2026-02-05_to_2026-02-12.csv $HF/release_2026_03_24/data/aei_raw_claude_ai_2026-02-05_to_2026-02-12.csv
curl -fsSL -o $A/release_2026_06_26/aei_claude_ai_2026-06-26.csv $HF/release_2026_06_26/data/aei_claude_ai_2026-06-26.csv

# Google AI & Economy ATLAS v1.0 public data (April 2026 sample)
mkdir -p $RAW/google_atlas
curl -fsSL -o $RAW/google_atlas/atlas_v1_public_data.zip https://ai.google/economy/atlas/embed-report-2026/data/atlas_v1_public_data.zip
(cd $RAW/google_atlas && unzip -o -q atlas_v1_public_data.zip)

# ITU ICT Price Baskets, historical series 2008-2025 (December 2025 release)
mkdir -p $RAW/itu
curl -fsSL -o $RAW/itu/ITU_ICTPriceBaskets_2008-2025.xlsx https://www.itu.int/en/ITU-D/Statistics/Documents/ICT_Prices/ITU_ICTPriceBaskets_2008-2025.xlsx
echo "sources downloaded"
