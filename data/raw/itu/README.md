# ITU ICT Price Baskets — provenance and definitions

Downloaded 2026-09-27 (processing script: `code/05_itu_price_baskets.py`).

| File | Source URL | Notes |
|---|---|---|
| ITU_ICTPriceBaskets_2008-2025.xlsx | https://www.itu.int/en/ITU-D/Statistics/Documents/ICT_Prices/ITU_ICTPriceBaskets_2008-2025.xlsx | Server Last-Modified 10 Dec 2025; workbook "Release date" 2 Dec 2025; cite as "ITU ICT Price Baskets, historical data series, Dec 2025 release". Sheets: Overview, BasketHistory, economies_2008-2025 (221 economies), medians, GNI_denominator |
| ITU_ICTPriceBaskets_Allowance_2025.xlsx | …/ICT_Prices/ITU_ICTPriceBaskets_Allowance_2025.xlsx | 2025 plan-level metadata (operator, allowance, speed, technology, tax rate, notes) for the 5 current baskets |
| ITU_IPBQManual_2025.pdf | …/ICT_Prices/ITU_IPBQManual_2025.pdf | ITU ICT Price Basket Questionnaire manual (dated January 2025): basket definitions & collection rules |
| itu_price_baskets_long.csv | derived | tidy long version of `economies_2008-2025` (all codes, years with a value), with `status` from BasketHistory |
| itu_affordability_latest.csv | derived | one row per economy with the requested indicators (2024, 2025) and latest-official-year columns |

Landing page: https://www.itu.int/en/ITU-D/Statistics/Pages/ICTprices/default.aspx . The ITU DataHub
(https://datahub.itu.int, API api.datahub.itu.int) returned HTTP 403 (CloudFront block) from this environment on
2026-09-27, so the Excel release above is the machine-readable source used.

## Indicators requested

| Indicator | Code (unit = % of monthly GNI p.c.) | Official years | Economies with data |
|---|---|---|---|
| Data-only mobile-broadband basket, 2 GB | `i271mb_2GB_GNI` | official 2021–2024; **2025 = experimental** ("exp") | 2024: 206; 2025 (exp): 205 |
| Data-only mobile-broadband basket, 5 GB (replaces 2 GB from 2025) | `i271mb_5GB_GNI` | official 2025; 2022–2024 = experimental | 2025: 206 |
| Fixed-broadband basket, 5 GB | `i154_FBB5_GNI` | official 2018–2025 | 2024: 195; 2025: 195 |

Also in the file for each basket: `$` (USD/month) and `_PPP` (PPP$/month) versions; other baskets: mobile data+voice
low (70 min+20 SMS+500 MB, 2018–2024; 70 min+50 SMS+1 GB from 2025), high (140 min+70 SMS+2 GB 2021–2024; 140 min+20 SMS+5 GB
from 2025), experimental 1 GB and 10 GB data-only, and historical baskets back to 2008 (mapping in sheet BasketHistory).

**Latest available year:** 2025 (Dec 2025 release). For the 2 GB data-only basket the latest *official* year is 2024;
the 2025 value is from ITU's experimental collection. `itu_affordability_latest.csv` provides both, plus
`mbb_2gb_pct_gni_latest_official` / `fbb_5gb_pct_gni_latest_official` with the year used (2 GB: 2024 for 206 economies,
2022/2023 for one each; fixed 5 GB: 2025 for 195, earlier for 5).

## Definitions (ITU manual, Jan 2025)
* Data-only mobile-broadband basket: "the cheapest available mobile data connection from the largest operator in a
  country, using 3G or more advanced technology, that allows at least [2 GB until 2024 / 5 GB from 2025] monthly Internet
  data usage"; minimum advertised download speed 256 kbit/s; residential single-user; prepaid or postpaid, whichever is
  cheapest; reference operator = largest mobile operator by subscriptions; excludes WiFi/hotspot-only offers.
* Fixed-broadband basket (5 GB): "the monthly price of the cheapest available fixed-broadband Internet subscription plan
  offering at least 5 GB of data usage per month at a minimum advertised download speed of 256 kbit/s", from the ISP with
  the largest market share (fixed-broadband subscriptions); residential; 12-month commitment plan (or closest); regular
  (post-promotion) price.
* All prices include taxes. Monthly reference period (plans with shorter validity are multiplied to cover the month).
* % of GNI p.c. = monthly basket price / (GNI per capita / 12). Denominator: World Bank WDI GNI per capita for the previous
  (or last available) year, retrieved each October; UN DESA National Accounts where WDI unavailable; local-currency GNI
  (NY.GNP.PCAP.CN) when the price is advertised in local currency, Atlas USD (NY.GNP.PCAP.CD) when advertised in USD.
  (The Overview sheet says the GNI_denominator sheet holds values "at the time of computation (Oct 2024)", but the sheet's
  own notes mostly read "GNI data year: 2024" — likely a stale note; check before relying on the vintage.)
* PPP: WB PPP conversion factor, private consumption (PA.NUS.PRVT.PP), extrapolated with GDP PPP ratios where missing.
  USD: IMF exchange rates (UN operational rates where missing).
* Affordability target: Broadband Commission / ITU benchmark of ≤ 2% of monthly GNI p.c. for entry-level broadband.

## Quick facts from the file (own computation, medians across economies by WB income group 2025)

| WB income group | Mobile 2 GB 2024 | Fixed 5 GB 2024 | Mobile 5 GB 2025 | Fixed 5 GB 2025 |
|---|---|---|---|---|
| High income | 0.43 | 1.00 | 0.43 | 1.00 |
| Upper middle income | 1.15 | 2.60 | 1.34 | 2.61 |
| Lower middle income | 2.17 | 6.32 | 3.05 | 5.60 |
| Low income | 7.36 | 29.51 | 9.42 | 29.91 |
| All economies (median) | 1.10 (n=206) | 2.60 (n=195) | 1.38 (n=206) | 2.52 (n=195) |

(ITU's own group medians are in sheet `medians`; use those for official statements.)
