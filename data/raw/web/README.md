# `data/raw/web/` — cross-channel prices: Microsoft 365 web store and Google Play in-app price ranges

Two frozen extracts of public web pages, collected on **16 October 2026** and read by `code/16_cross_channel.py`, which compares them
with the App Store prices of the second price wave (`data/raw/appstore_wave2/`, same day). Microsoft fetches ran 13:36-13:44 UTC
; Google Play fetches ran 13:46-13:56 UTC. All requests came from one residential IP address, used the Python standard library (`urllib`) only, and were read-only GETs (no logins, forms, purchases or posting). The
collection scripts are not part of this package.

| File | Rows | Content | SHA-256 |
|---|---|---|---|
| `ms365_web_prices.csv` | 376 | Microsoft 365 Personal, Family and Premium, monthly and annual, from 63 locale paths in 57 countries | `6a565663d240d7f33af0959eda66b1ce2a705d157fda2646b539a4dc87fd6105` |
| `play_iap_ranges.csv` | 360 | 12 apps x 30 countries: the "in-app purchases" price range (lowest and highest item) shown on the Google Play web page of the app | `28f23daeaecaccbda7410c79f47c486f63048e335955e6d0a5d4760b0d6daac6` |

**Raw pages.** Every fetched body was archived gzipped as received (`web/raw/`, 487 files: 107 Microsoft 365 locale pages, 362
Google Play pages, 17 Microsoft probe pages and 1 locale selector); each CSV row carries the archive path (`archive_path`) and the
SHA-256 of the raw body (`sha256`). The archive is deposited alongside this package in the Zenodo record of version 3.1 as
`cross_channel_page_archive_2026-10-16.zip` (487 files, a README and SHA256SUMS; 77 MB); the `sha256` of the pages behind all 63
Microsoft locales and all 360 Google Play rows equals the hash of the archived raw body. The archive is not part of this package;
the archive paths in the CSVs therefore point to files that are not in this folder. A checker with the archive can re-parse
a page and compare the result with the row that carries its hash.

## Columns of `ms365_web_prices.csv`

| Column | Meaning |
|---|---|
| `locale` | Locale path of the page (`https://www.microsoft.com/<locale>/microsoft-365/buy/compare-all-microsoft-365-products`), e.g. `en-us`, `de-ch` |
| `iso2` | Country of the locale (upper-case ISO 3166 alpha-2). Several countries appear under two locales with identical prices (CA, CH, BE, SA, AE, HK) |
| `currency` | Currency code of the price: the locale's currency, with the overrides recorded in `note` |
| `product` | `Microsoft 365 Personal`, `Microsoft 365 Family` or `Microsoft 365 Premium` |
| `period` | `monthly` or `annual` (billing period of the offer; the period word on the page matches the analytics attribute `data-bi-rpid` in every row) |
| `price` | Price in `currency`, parsed with a locale-aware number parser (two different separators: the last is the decimal mark; a repeated separator is digit grouping; a single separator followed by three digits is grouping, flagged in `note`) |
| `raw_string`, `price_token` | The text of the buy button and the price as shown on the page (with symbol) |
| `product_name_on_page`, `product_id` | Product name (`data-bi-prdname`) and product id (`data-bi-pid`) of the buy button; Personal `cfq7ttc0k5bf` (ja-jp `cfq7ttc0k5bc`), Family `cfq7ttc0k5dm`, Premium `cfq7ttc11z3q` |
| `n_occurrences_on_page`, `n_distinct_values_on_page` | Number of buy buttons for this product and period on the page, and number of distinct prices among them (1 in every row) |
| `tax_statement_on_page` | Whether the page states that prices include tax: `none found` in every row (tax treatment is unknown) |
| `header_text_crosscheck` | Independent check of the mapping: the card header text ("product monthly annual") against the buy-button mapping; `3 ok/0 annual-first` etc. (53 of 63 locales matched, none contradicted; in 10 locales the header parser found no match because of space-grouped numbers or suffix currency formats, and those rely on the other checks) |
| `note` | Parsing or currency remark: `single 3-digit group read as thousands separator` (KRW, JPY, CLP, COP, IDR, VND-style formats; all correct), `page uses 3 decimals e.g. 52,999.000` (es-cr), `page shows 'USD$' (Gulf storefront priced in USD)` (ar-ae, en-ae), `page shows EUR (Bulgaria euro adoption)` (bg-bg), `page shows '$' symbol; RSD inferred from magnitude ... UNVERIFIED currency label` (sr-latn-rs) |
| `url`, `final_url` | Requested URL and URL after redirects |
| `fetch_utc`, `fetch_kst` | Time of the request (UTC, and the local time of the collection, UTC+9) |
| `archive_path`, `sha256` | Gzipped raw page in the archive, and SHA-256 of the raw body |

Mapping checks: the en-us page reproduces the expected US ladder exactly (Personal $9.99 a month and $99.99 a year, Family $12.99 and
$129.99, Premium $19.99 and $199.99); the annual price is 8 to 11 times the monthly price in all 188 product-locale pairs. Coverage: prices
were found in 63 locales. zh-cn lists Personal and Family only (no Premium). ru-ru and en-lb returned HTTP 200 without prices; 42
locale paths returned HTTP 404 for the compare page (among them the requested low-income anchors Nigeria, Kenya, Pakistan, Egypt and
Bangladesh, where the Microsoft Store web apparently does not sell the consumer plans), so the lower-income coverage is thin (India is
the only low or lower-middle-income country with both Personal and Premium). The strike-through original-price containers were empty on
every page (no promotional prices detected; absence is unverified outside en-us). All pages were fetched from one IP address; prices
nonetheless follow the locale path and match each locale's currency, but this was not tested from a second IP.

## Columns of `play_iap_ranges.csv`

| Column | Meaning |
|---|---|
| `app`, `package` | App name and Google Play package id: ChatGPT `com.openai.chatgpt`, Claude `com.anthropic.claude`, Gemini `com.google.android.apps.bard`, Perplexity `ai.perplexity.app.android`, Grok `ai.x.grok`, YouTube `com.google.android.youtube`, X `com.twitter.android`, Snapchat `com.snapchat.android`, Duolingo `com.duolingo`, Spotify `com.spotify.music`, Telegram `org.telegram.messenger`, Microsoft Copilot `com.microsoft.office.officehubrow` |
| `country` | Country code passed as `gl=` in `https://play.google.com/store/apps/details?id=<package>&hl=en&gl=<country>` (30 countries); `gl=`, not the IP address, drives the price shown |
| `status` | HTTP status (200 in all 360 requests; no 429 or block) |
| `app_title` | Title of the app page |
| `currency_jsonld` | Currency of the page, from the JSON-LD `offers.priceCurrency`; equals the currency of the `gl=` country in all 30 countries |
| `has_iap_badge`, `iap_range_shown` | Whether the page shows an in-app purchases badge and a price range (330 rows True; Gemini shows none in any of the 30 countries because its subscriptions are sold through Google One) |
| `min`, `max` | Lowest and highest in-app item price in `currency_jsonld`, taken only from the `AF_initDataCallback` block `ds:5` (the main app details; the similar-apps block `ds:8` is ignored) |
| `raw_string`, `range_suffix` | The range string as shown, and its wording: `per item` (297 rows) or `if billed through Play` (33 rows: GB, DE and PL, the user-choice-billing jurisdictions) |
| `n_ranges_in_ds5` | Number of range strings in `ds:5` (0 or 1) |
| `parse_flag` | `assumed_thousands_sep` where a single separator followed by three digits was read as a thousands separator (zero-decimal-style currencies JPY, KRW, IDR, VND, COP, CLP; checked visually) |
| `url`, `final_url`, `fetch_utc`, `fetch_kst`, `archive_path`, `sha256` | As above |

Caveats: the range covers **all** in-app items (consumables, add-ons, annual plans, other tiers), not a specific plan, and Google Play's
web page does not map the minimum and maximum to tiers; the US minimum of ChatGPT ($8.00) is the Go price and that of Claude ($20.00)
is Pro, but the maxima ($500, $700) are not plan prices. `com.microsoft.copilot` returned HTTP 404 in the US, India and the UK; the
Play search for "Microsoft Copilot" lists `com.microsoft.office.officehubrow` first (the former Microsoft 365 hub app, now titled
"Microsoft Copilot"), so its range may mix Microsoft 365 and Copilot Pro items and is not a clean consumer-Copilot listing. Google
web prices (YouTube Premium, Google One) are localised by IP address and were not collected. No exchange-rate conversion was done in the
extract; `code/16_cross_channel.py` converts at the rates of `data/raw/fx_hist/usd_2026-10-15.json`.

## Use

`code/16_cross_channel.py` reads the two CSVs (monthly rows of the Microsoft file; the `min` of ChatGPT and Claude of the Play file)
and writes `output/tables/W15_cross_channel.csv`, `W15b_play_countries.csv`, the `xch_*` scalars of `output/results_wave2.json` and,
through `code/41_tables_wave2.py`, `paper_en/tables/tab_cross_channel.tex` and `tab_play_countries.tex`. Nothing in this folder is
changed by the pipeline.
