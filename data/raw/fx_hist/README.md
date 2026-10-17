# `data/raw/fx_hist/` — US-dollar exchange rates on six dates (vintage test)

Six daily snapshots of the fawazahmed0 currency-api, one file per date: `usd_2024-03-06.json`, `usd_2024-10-15.json`,
`usd_2025-04-15.json`, `usd_2025-10-15.json`, `usd_2026-04-15.json` and `usd_2026-10-15.json`. Each file has two fields: `date`
(the snapshot date, equal to the date in the file name) and `usd`, a dictionary from the lower-case currency code to the number of
currency units per US$ (so `usd["eur"]` = 0.89 means US$1 = EUR 0.89; `usd["usd"]` = 1).

Source: fawazahmed0 currency-api snapshots, dates as named; collected by the author's agent on 16 Oct 2026. The URL pattern the
collector reports is `https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@<date>/v1/currencies/usd.json`. The pipeline makes no
network request and no script in this package downloads these files; they are frozen inputs, like the rest of `data/raw/`.

| File | Codes | SHA-256 |
|---|---|---|
| `usd_2024-03-06.json` | 701 | `106b9ad9dab6a8da37b60d8d546ca127f4dfde75df399012da4e99e02eddfe79` |
| `usd_2024-10-15.json` | 341 | `9d9969dc6ad00b4c2d245f404713a1a74c2acb170baaf8e27683876124c8cbff` |
| `usd_2025-04-15.json` | 338 | `12f751940c34b329cce7962b20351d7a7d2c1b5b92fde1b8c05ff847d2ff605c` |
| `usd_2025-10-15.json` | 341 | `95509b6783d1e427a16b8df821c1be49178cfde209167f78d019982d6247a1b3` |
| `usd_2026-04-15.json` | 300 | `e8cc1e559dfccb0058daf62830a87a81b7a626268e2aedd40895dc47bf0b4dda` |
| `usd_2026-10-15.json` | 340 | `51704139cb2e4f1af3873abc882adf823c6b33cd6979c30f6ad3a06999d5e9a0` |

`usd_2026-10-15.json` is byte-identical to `data/raw/appstore_wave2/fx/fawaz_usd_20261016.json` (the second source of exchange rates
of the second price wave, whose `date` field is also 2026-10-15). The files also list crypto-assets and other non-currency codes,
and in different numbers (the 2024-03-06 file has the most), which is why they differ in size; only the codes of the App Store and
Google Play storefront currencies are used.

## Use

* `code/15_vintage_test.py` (vintage test of the deviations from the revealed Apple default schedule): the FX movement of a currency is
  the range of ln(units per US$) over the six dates (0 for the US dollar). A storefront whose currency is missing from any of the six
  files has no movement and drops out of the test (none does: all 43 storefront currencies are present on all six dates). The script
  stops if the `date` field of a file differs from its name.
* `code/16_cross_channel.py`: `usd_2026-10-15.json` converts the Google Play prices of 16 Oct 2026 to US dollars at the rates of
  15 Oct 2026, the same rates as `price_usd_alt_fx` of the second price wave.

Rates are the daily reference rates published by the API, not transaction rates. Nothing in this folder is changed by the pipeline.
