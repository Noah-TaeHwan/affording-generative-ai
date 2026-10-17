# `data/raw/appstore_wave2/` — second App Store price wave, 16 October 2026

Raw extracts of the Apple App Store product pages (`https://apps.apple.com/<cc>/app/id<app id>`), collected on 16 October 2026
with `code/02b_scrape_wave2.py`; wave 1 (27 September 2026, ChatGPT, Claude and Gemini only) is in `data/raw/appstore/`. The files
here are read by `code/09b_wave2_items.py` (item prices, slopes, stability) and, through its output, by `code/12_default_panel.py`.
Nothing in this folder is changed by the pipeline.

## Files

| File | Contents | Records |
|---|---|---|
| `core/appstore_iap_raw_wave2.jsonl` | One line per request attempt, 34 apps × 218 storefront codes. Fields: `storefront`, `app`, `app_id`, `request_url`, `fetched_utc`, `http_status`, `final_url`, `iap_title`, `iap` (list of `[item name, displayed price]`), `parser`, `currency`, `app_name`, `bytes`, `sha256` (and `error` where a request failed) | 7,816 lines = 7,412 (storefront, app) pairs + 404 lines of retried HTTP 429 answers |
| `default_panel/appstore_iap_raw_wave2_default.jsonl` | The same fields for the 30 small-developer "default panel" apps × the 167 storefronts of `local_storefronts.json` | 5,310 lines = 5,010 pairs + 300 retried HTTP 429 lines |
| `fx/er_api_usd_20261016.json` | open.er-api.com USD rates (units per US$), `time_last_update_utc` 16 Oct 2026 00:02:31 UTC, 166 currencies | |
| `fx/fawaz_usd_20261016.json` | fawazahmed0 currency-api USD rates, `date` field 2026-10-15 (the file is named for the collection date, 16 Oct; the rates are those of the date field), 340 codes | |
| `apps_v3.json` | The 34 apps of the core run: App Store id and class (`ai_core` 3: ChatGPT, Claude, Gemini; `ai` 5: Perplexity, Grok, Mistral, Poe, Character.AI; `ai_bundle` 1: Microsoft 365 with Copilot; `ai_feature` 4: Canva, CapCut, Notion, Grammarly; `nonai` 21) | 34 |
| `apps_default_panel.json` | The 30 small-developer apps of the default panel (id, name) | 30 |
| `indie_candidates.json` | The 85 candidate small-developer apps from which the panel was assembled: id, name, seller, search term and the US in-app purchase list at the time | 85 |
| `local_storefronts.json` | The 167 storefront codes in which the ChatGPT page is served from the storefront itself (not redirected to the US); the default panel was requested in these only | 167 |
| `../_log_appstore_wave2.txt`, `../_log_appstore_wave2_default.txt` | Progress logs of the scraper (three invocations for the core run, two for the default panel; clock times are Korea Standard Time, UTC+9) | |

SHA-256 of the files as deposited:

| File | SHA-256 |
|---|---|
| `core/appstore_iap_raw_wave2.jsonl` | `ea48638bf511b03f777e500a21fc445261fd253de5fa651cf3bc15eb01df011f` |
| `default_panel/appstore_iap_raw_wave2_default.jsonl` | `2122343e87c37c7a55ccb65d49959b1c72f49bd390183a2b300921ff9079a01b` |
| `fx/er_api_usd_20261016.json` | `9fe5585677fbd4c15e66ebfee382a19e7ea8827834184dfd316024fdde600b58` |
| `fx/fawaz_usd_20261016.json` | `51704139cb2e4f1af3873abc882adf823c6b33cd6979c30f6ad3a06999d5e9a0` |
| `apps_v3.json` | `55cbd8e87728c5476062cd51f701121075883e1ca44bd177fc6dce0fcb8a41fb` |
| `apps_default_panel.json` | `9540b847c8da6179e39a0e5cdea3041307f90dfa11e13b4be4143f1702c957df` |
| `indie_candidates.json` | `7dd137fc55d9daedba2e12e026071f4ef93e71846d119b0a21f013a929257075` |
| `local_storefronts.json` | `6d2ea7b01657ce1cfd3cf70c31818aec3a3910fb06de8a929d5e28e371cc55dd` |

## Collection

* Core run, 16 Oct 2026 05:01–05:53 UTC: 7,412 pairs; HTTP 200 for 7,218, 404 (app not offered in the
  storefront) for 194. Of the 7,218 pages, 5,688 are served from the storefront itself (local prices) and 1,530 are redirected to
  the US storefront (no local storefront; the prices on them are the US prices and are not used); 173 storefronts have local pages
  (170 for at least one of ChatGPT, Claude and Gemini: ChatGPT 167, Claude 164, Gemini 169; `tw` has no World Bank record and no GNI).
  122 pages carry no in-app purchase list.
* Default panel, 16 Oct 2026 05:57–06:36 UTC: 5,010 pairs; HTTP 200 for 5,007, 404 for 1; the pairs (`mz`, `indie_6448909309`) and
  (`us`, `indie_839285684`) stayed at HTTP 429 after four attempts and have no record. The US storefront is therefore missing for
  one panel app, whose items cannot be placed on a US price point.
* Requests were made with three parallel workers, a random 0.2–0.8 s pause and exponential back-off on HTTP 429 (four attempts),
  in an order shuffled with a fixed seed; every attempt is a line of the JSONL file. A pair can have several lines (HTTP 429 first,
  then the answer); the analysis keeps the last line with HTTP status 200, 404 or 410.
* Prices are those the storefront displays to a visitor without an account: tax-inclusive in almost all storefronts, excluding sales
  tax in the US and Canada, as in wave 1.

## Page format change, 27 September to 16 October 2026

On 27 September (wave 1) the In-App Purchases list was embedded in the page source as JSON (`"$kind":"Annotation" … "textPairs"`).
By 16 October Apple serves the list as HTML (`<dt>In-App Purchases</dt><dd> … <div class="text-pair"><span>name</span> <span>price</span>`).
`02b_scrape_wave2.py` reads the JSON form first and the HTML form second and records which it used in `parser` (`html_v2` for all
12,103 pages of this wave that carry a list, `html_v2_none` for the 122 pages without one; the `json_v1` branch is not exercised). The prices
of the 1,586 wave-1 plan × storefront cells that exist in both waves are identical across the format change
(`output/tables/W3_stability.csv`, `paper_en/tables/tab_stability.tex`), so the change of format did not alter what the
parser recovers.

## Plan names

The ChatGPT tiers that wave 1 labelled `Pro 5x` and `Pro 20x` are listed on 16 October as `ChatGPT Pro 100` and `ChatGPT Pro 200` at
the same prices (US$100 and US$200); a new `ChatGPT Pro 500` (US$500) is also listed. `code/09b_wave2_items.py` maps
`chatgpt_pro5x` → `chatgpt_pro100` and `chatgpt_pro20x` → `chatgpt_pro200` for the stability comparison. The Claude and Gemini
item names are unchanged (`Claude Max 5x/20x - Monthly`, `Google AI Plus (400 GB)`, `Google AI Pro (5 TB)`, `Google AI Ultra (30 TB)`).

## Page archive (deposited as a separate file)

The scraper keeps, for each page, the gzipped full HTML of the three core apps (`html/<app>_<storefront>.html.gz`) and, for all
apps, the gzipped In-App Purchases block and JSON-LD (`snip/<app>_<storefront>.html.gz`). The archive of the run of 16 October 2026
is deposited alongside this package in the Zenodo record of version 3.1 as `appstore_wave2_page_archive_2026-10-16.zip` (109 MB):
12,860 gzipped files for the 12,225 pages with HTTP 200, the in-app purchase block and JSON-LD of all 7,218 pages of the 34 apps
(`snip/`) and of all 5,007 pages of the 30-app panel (`snip_default_panel/`), the 635 full pages of ChatGPT, Claude and Gemini
(`html/`), a README and SHA256SUMS. The SHA-256 of all 635 decompressed full pages equals the `sha256` field of the matching JSONL
line. It is not part of this package. The link between a parsed record and its page is the
`sha256` field of the JSONL line: the SHA-256 of the full page bytes as received (present for all 7,218 + 5,007 pages with HTTP 200).
A checker with the archive can re-parse a page with `parse_iap_html` from `02b_scrape_wave2.py` and compare the result with the `iap`
field of the line carrying that hash.

## Rebuilding

`python code/09b_wave2_items.py && python code/12_default_panel.py` rebuild every processed file from these extracts (no network).
`python code/02b_scrape_wave2.py core|default|both` re-scrapes (prices will differ; see the docstring of the script).
