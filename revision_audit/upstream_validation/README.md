# Upstream source validation

Completed on 30 September 2026, Korea time. `upstream_verification.json` is the authoritative record of file hashes, row counts and comparisons.

The four Anthropic release CSVs and three supporting population/GDP/ISO files were downloaded from Hugging Face commit `2ea58ff75e4247d26810c37f10c179edc2466cac`. The original `code/03_anthropic_country.py` was run in an isolated reconstruction directory. All four derived outputs, including the five-window country panel, were byte-identical to v1.8. The ITU historical workbook was downloaded from its documented URL, and the original `code/05_itu_price_baskets.py` regenerated both country outputs byte-identically. Its URL is not immutable; the SHA256 records the exact file received.

Separately, `verify_upstream.py` directly selects the published May AUI from the full raw CSV, compares all 120 World Bank-matched values with the analysis panel, and estimates the primary n=96 regression with independent NumPy HC3 code. Every value matches; slope 0.711136928 and HC3 SE 0.035923227.

The large original raw files are not bundled in this supplement. Their exact download locations are in the package's `code/00_download_sources.sh`; hashes are in the JSON record. To repeat the check, fetch those files into an isolated copy of the original package, run its Anthropic and ITU construction scripts, then invoke:

```bash
python verify_upstream.py \
  --package-root /path/to/frozen-package \
  --reconstruction-root /path/to/reconstructed-package \
  --raw-root /path/to/directory-containing-the-latest-csv-and-itu-workbook \
  --out-dir /path/to/new-verification-output
```

`--raw-root` contains `aei_claude_ai_2026-06-26.csv` and `ITU_ICTPriceBaskets_2008-2025.xlsx`. Earlier raw files and supporting files remain under the reconstructed package's normal `data/raw/anthropic/release_*/` directories. Do not overwrite frozen originals.

These checks validate extraction and calculation against the specified provider files. They do not validate the providers' sampling models, establish price causality, or independently reconstruct historical App Store pages, World Bank downloads, Google data or exchange-rate snapshots.
