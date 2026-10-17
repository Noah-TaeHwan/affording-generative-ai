"""
09b_wave2_items.py   (no network)
Clean the second App Store wave (16 October 2026; scraped by 02b_scrape_wave2.py) into item-level monthly prices, USD
conversions, income slopes and a wave-1 stability check; flag annual prices recorded as monthly (the guard); drop items that
are listed twice.

Inputs   data/raw/appstore_wave2/core/appstore_iap_raw_wave2.jsonl            34 apps x 218 storefront codes
         data/raw/appstore_wave2/default_panel/appstore_iap_raw_wave2_default.jsonl   30 small-developer apps x 167 storefronts
         data/raw/appstore_wave2/fx/er_api_usd_20261016.json, fawaz_usd_20261016.json  USD exchange rates (two sources)
         data/raw/appstore_wave2/apps_v3.json                                  app ids and classes
         data/processed/country_panel.csv, data/processed/appstore_prices_long.csv   (wave 1, 27 Sep 2026)
         data/raw/appstore/appstore_iap_raw.jsonl                             (wave 1; only its fetch dates are read here)
Outputs  data/processed/wave2_items_long.csv           storefront x app x item: modal monthly price, USD at two FX sources,
                                                        ratio to the US price, GNI, income group, the guard's reference price
                                                        (guard_ref) and flag (flag_annual); flagged rows are kept in the file
         data/processed/wave2_default_items_long.csv   the same for the default-panel apps
         data/processed/wave2_plan_rows.csv            plan x storefront rows (AI plans and benchmark items), without the
                                                        plan x storefront cells whose selected item is flagged by the guard
         data/processed/wave2_item_slopes.csv          HC1 income slope of every item listed in >= 60 storefronts, after the
                                                        guard and the de-duplication
         data/processed/wave2_stability.csv            wave-1 vs wave-2 local price, plan x storefront
         output/tables/W1_wave2_plans.csv              (plan descriptors and unconditional slopes; 12_default_panel.py adds
                                                        the matched-sample and default-schedule columns)
         output/tables/W2_benchmarks.csv, W3_stability.csv, W5_item_classes.csv
         output/tables/W5b_applevel.csv                app-level incidence of localisation (one row per app)
         output/tables/W6_annual_guard.csv             items with flagged cells: slope before and after the guard
         output/tables/W6b_annual_guard_cells.csv      every flagged cell
         output/tables/W7_dedup.csv                    items dropped as duplicates and the item kept instead
         output/results_wave2.json                     scalars quoted in the text (12_default_panel.py adds its own)
         data/processed/wave2_data_dictionary.csv      (12_default_panel.py adds its files)

Definitions (those of the stdlib scripts that produced the first pass of the wave-2 results, analyze_v3.py and analyze_default.py,
which are not part of this package; the order of rows follows the raw file, which matters only for ties):
  * Page record per (storefront, app) = the last line with HTTP status 200, 404 or 410.  Status: 404 -> app not offered;
    200 and final URL in the same storefront -> local storefront; 200 and redirected -> no local storefront (Apple sends the
    visitor to the US storefront, whose prices are not local); anything else -> error.
  * Item = (storefront, app, in-app purchase name).  A name can be listed several times (monthly and annual variants, or
    several price points): monthly price = mode of the listed prices below five times the minimum, ties to the higher price.
  * Apple's product page lists at most ten in-app purchases (wave2_list_max_items): of the non-empty lists, those with exactly
    ten entries are lists that may have lost entries.  A missing item on such a list is censored, not necessarily unavailable,
    and a plan's monthly variant can be missing while its annual variant is listed (the guard below).
  * USD price = local price / currency units per USD (open.er-api.com, 16 Oct 2026; fawazahmed0 currency-api, 15 Oct 2026, as
    the cross-check); ratio to US = USD price / US price of the same app and item name.
  * type: `consumable` if the name matches the credit/coin/pack pattern CONS, else `subscription`.
  * Guard (annual-as-monthly).  A cell (storefront other than the US, app, item) is flagged (flag_annual) if its price is more
    than three times the price that Apple's default schedule gives for the item's US price, price_local > 3 x guard_ref with
    guard_ref = storefront multiplier (12_default_panel.py's schedule, recomputed here from the default-panel items through
    wave2_common.schedule) x US price; in a storefront without a multiplier, if the item has a single listed price
    (n_variants = 1) and a ratio to the US price above 3.  Flagged cells stay in wave2_items_long.csv but are excluded from the
    item slopes, the plan rows and everything computed from them; the stability check (wave 1 vs wave 2) and the default panel
    are not affected.
  * Item slope = HC1 OLS slope of ln(ratio to US) on ln(GNI per capita, Atlas) over the storefronts other than the US, with a
    ratio in (0.05, 20) and without a flagged cell, for items observed in >= 60 storefronts.  Slope 0 = the US dollar price is
    the same everywhere; a positive slope = richer countries pay more.
  * De-duplication of the slope sample.  The firm of an app is google (youtube, youtubemusic, gemini, googleone), xcorp (x,
    grok) or the app itself; the normalised name is the lower-case name without parentheses, punctuation and extra spaces.
    Among items with the same (firm, normalised name) the one with the largest N is kept (ties: the app whose product it is,
    youtube for Premium items and youtubemusic for Music items, then alphabetical app and name).  Within an app, an item whose
    storefront -> local price mapping is identical to that of a kept item is dropped.  W7_dedup.csv lists the dropped items.
  * LMIC in this file = Low income plus Lower-middle income (World Bank FY2027); `median_ratio_lmic` is the median ratio to the
    US price in those storefronts.  (country_panel.csv spells the group "Lower-middle income"; a test against the string
    "Lower middle income" matches nothing and would restrict the median to the low-income storefronts alone.)
  * App-level incidence: an app localises if any of its subscription items in the slope sample has a slope above 0.10; AI apps
    are those of class ai and ai_core, non-AI apps those of class nonai; two-sided Fisher exact test of the 2 x 2 table.
  * Plan rows: for each plan, the item whose name matches the plan pattern; if a storefront lists several, the one with the most
    price variants, then the lower price; a storefront whose selected item is flagged by the guard is dropped for that plan.
    Plans of analyze_v3.py plus benchmark items (YouTube Music, YouTube Premium Lite, X Premium, SuperGrok Heavy, Character.AI,
    Microsoft 365 Family) and ChatGPT Pro 500.
  * Stability: wave-1 plan x storefront local price against the wave-2 price of the same plan (chatgpt_pro5x and
    chatgpt_pro20x -> "ChatGPT Pro 100", "ChatGPT Pro 200"); identical if |w1 - w2| < 0.5% of the larger.
"""
import collections, datetime, json, pathlib, re
import numpy as np
import pandas as pd
from scipy.stats import fisher_exact
from wave2_common import LMIC, NAN, SHORT, MAIN, ols_hc1, panel_points, schedule

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW2 = ROOT / "data" / "raw" / "appstore_wave2"
PROC, TAB = ROOT / "data" / "processed", ROOT / "output" / "tables"
PROC.mkdir(parents=True, exist_ok=True)
TAB.mkdir(parents=True, exist_ok=True)
R = {}                                                                    # results_wave2.json

APPS = json.load(open(RAW2 / "apps_v3.json"))
RATES = json.load(open(RAW2 / "fx" / "er_api_usd_20261016.json"))["rates"]          # units of currency per 1 USD
RATES2 = {k.upper(): v for k, v in json.load(open(RAW2 / "fx" / "fawaz_usd_20261016.json"))["usd"].items()}
panel = pd.read_csv(ROOT / "data" / "processed" / "country_panel.csv", keep_default_na=False, na_values=[""])[["iso2", "gni_atlas", "income_group"]].copy()
panel["sf"] = panel.iso2.str.lower()
GNI = dict(zip(panel.sf, panel.gni_atlas))
GRP = dict(zip(panel.sf, panel.income_group))


# ------------------------------------------------------------------------------------------------ price parsing
def parse_price(s):
    """Return a float from an App Store price string in any storefront format (09_appstore_prices.py version, plus the narrow
    no-break space and a None for strings without a number)."""
    if s is None:
        return None
    t = s.replace("\xa0", " ").replace(" ", " ").strip()
    mult = 1.0
    if re.search(r"ribu", t, re.I):
        mult = 1e3
    elif re.search(r"\bjt\b|juta", t, re.I):
        mult = 1e6
    m = re.search(r"\d[\d.,'\s]*", t)
    if not m:
        return None
    num = m.group(0).strip().replace("'", "").replace(" ", "")
    if mult != 1.0:
        return float(num.replace(".", "").replace(",", ".")) * mult
    if "," in num and "." in num:
        dec = "," if num.rfind(",") > num.rfind(".") else "."
        thou = "." if dec == "," else ","
        num = num.replace(thou, "").replace(dec, ".")
    elif "," in num or "." in num:
        sep = "," if "," in num else "."
        parts = num.split(sep)
        if len(parts) == 2 and len(parts[1]) in (1, 2):
            num = parts[0] + "." + parts[1]
        else:
            num = "".join(parts)
    try:
        return float(num) * mult
    except ValueError:
        return None


def monthly(prices):
    """Pick the monthly price among listed variants: drop the annual cluster (>=5x the minimum), then take the mode."""
    p = sorted(prices)
    low = [x for x in p if x < 5 * p[0]]
    cnt = collections.Counter(low)
    top = max(cnt.values())
    return max(v for v, c in cnt.items() if c == top), len(p), len(low), len(cnt)


CONS = re.compile(r"credit|gem|star|boost|super ?like|coin|token|sticker|super chat|top.?up|movies|shows|rental|"
                  r"one week|1 week|single|pack|bundle of|spotlight|first impression|read receipt|super swipe|"
                  r"crédit|crédito|kredit|クレジット|크레딧|額度", re.I)


# ------------------------------------------------------------------------------------------------ page records
def last_records(path):
    """Last line with status 200/404/410 per (storefront, app); a pair that never succeeded keeps its first line.
    Returns (dict in order of first appearance, number of lines)."""
    best, n = {}, 0
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        n += 1
        k = (r["storefront"], r["app"])
        if r.get("http_status") in (200, 404, 410) or k not in best:
            best[k] = r
    return best, n


def fetch_date(*paths):
    """UTC date (YYYY-MM-DD) on which the records of the given JSONL files were fetched (field fetched_utc); all records of a
    wave were fetched on one date, which is checked."""
    dates = set()
    for path in paths:
        for line in open(path, encoding="utf-8"):
            dates.add(json.loads(line)["fetched_utc"][:10])
    assert len(dates) == 1, f"records fetched on several dates: {sorted(dates)}"
    return dates.pop()


def page_status(r, sf):
    st = r.get("http_status")
    fs = re.search(r"apps\.apple\.com/([a-z]{2})/", r.get("final_url") or "")
    fs = fs.group(1) if fs else None
    return ("app_not_offered" if st == 404 else "local" if (st == 200 and fs == sf) else
            "no_local_storefront" if st == 200 else "error")


def item_rows(best):
    """-> (Counter of (app, status), rows): one row per (storefront, app, item name), in the order of the raw file."""
    avail, names, cur_of = collections.Counter(), {}, {}
    for (sf, app), r in best.items():
        status = page_status(r, sf)
        avail[(app, status)] += 1
        if status != "local" or not r.get("iap"):
            continue
        cur_of[(sf, app)] = r.get("currency")
        for nm, ps in r["iap"]:
            v = parse_price(ps)
            if v and v > 0:
                names.setdefault((sf, app, nm.strip()), []).append((v, ps))
    rows = []
    for (sf, app, nm), vs in names.items():
        m, n_all, n_low, n_dist = monthly([v for v, _ in vs])
        cur = cur_of[(sf, app)]
        rate, rate2 = RATES.get(cur), RATES2.get(cur)
        rows.append(dict(storefront=sf, app=app, name=nm, currency=cur, price_local=m,
                         price_usd=(m / rate if rate else NAN), price_usd_alt_fx=(m / rate2 if rate2 else NAN),
                         n_variants=n_all, n_distinct_monthly=n_dist, raw_strings=" | ".join(sorted({s for _, s in vs}))))
    return avail, rows


def finish(rows, classes):
    d = pd.DataFrame(rows)
    d.insert(2, "app_class", d.app.map(classes))
    d.insert(4, "type", np.where(d.name.str.contains(CONS), "consumable", "subscription"))
    us = d[d.storefront == "us"].drop_duplicates(["app", "name"]).set_index(["app", "name"]).price_local   # US prices are in USD
    d["us_price"] = [us.get(k, NAN) for k in zip(d.app, d.name)]
    d["ratio_us"] = d.price_usd / d.us_price
    d["ratio_us_alt_fx"] = d.price_usd_alt_fx / d.us_price
    d["gni"] = d.storefront.map(GNI)
    d["income_group"] = d.storefront.map(GRP)
    return d[["storefront", "app", "app_class", "name", "type", "currency", "price_local", "price_usd", "price_usd_alt_fx",
              "n_variants", "n_distinct_monthly", "us_price", "ratio_us", "ratio_us_alt_fx", "gni", "income_group", "raw_strings"]]


# ------------------------------------------------------------------------------------------------ plans and benchmark items
PLANS = {   # plan -> (app, regular expression for the item name, label)
    "chatgpt_go": ("chatgpt", r"^ChatGPT Go$", "ChatGPT Go"), "chatgpt_plus": ("chatgpt", r"^ChatGPT Plus$", "ChatGPT Plus"),
    "chatgpt_pro100": ("chatgpt", r"^ChatGPT Pro 100$", "ChatGPT Pro 100"),
    "chatgpt_pro200": ("chatgpt", r"^ChatGPT Pro 200$", "ChatGPT Pro 200"),
    "chatgpt_pro500": ("chatgpt", r"^ChatGPT Pro 500$", "ChatGPT Pro 500"),
    "claude_pro": ("claude", r"^Claude Pro", "Claude Pro"), "claude_max5x": ("claude", r"Max 5x", r"Claude Max 5$\times$"),
    "claude_max20x": ("claude", r"Max 20x", r"Claude Max 20$\times$"),
    "gemini_plus": ("gemini", r"AI Plus \(400", "Google AI Plus"), "gemini_pro": ("gemini", r"AI Pro", "Google AI Pro"),
    "gemini_ultra": ("gemini", r"AI Ultra", "Google AI Ultra"),
    "perplexity_pro": ("perplexity", r"^Perplexity Pro$", "Perplexity Pro"),
    "supergrok": ("grok", r"^SuperGrok$", "SuperGrok"), "supergrok_lite": ("grok", r"^SuperGrok Lite$", "SuperGrok Lite"),
    "supergrok_heavy": ("grok", r"^SuperGrok Heavy$", "SuperGrok Heavy"),
    "m365_personal": ("copilot_m365", r"^Microsoft 365 Personal$", "Microsoft 365 Personal"),
    "m365_premium": ("copilot_m365", r"^Microsoft 365 Premium", "Microsoft 365 Premium"),
    "googleone_100gb": ("googleone", r"^100 GB$", "Google One 100 GB (Google One app)"),
    "gemini_100gb": ("gemini", r"^100 GB$", "Google One 100 GB"),            # the storage plan listed in the Gemini app (133 storefronts)
    "googleone_aiplus2tb": ("googleone", r"Google AI Plus \(2 TB\)", "Google AI Plus (2 TB)"),
    "youtube_premium": ("youtube", r"^YouTube Premium$", "YouTube Premium"),
    "youtubemusic_music": ("youtubemusic", r"^YouTube Music$", "YouTube Music"),
    "telegram_premium": ("telegram", r"^Telegram Premium$", "Telegram Premium"),
    "duolingo_super": ("duolingo", r"^Super Duolingo$", "Super Duolingo"), "discord_nitro": ("discord", r"^Nitro$", "Discord Nitro"),
    "snapchat_plus": ("snapchat", r"^Snapchat\+", "Snapchat+"),
    "x_premium": ("x", r"^X Premium \(Monthly\)$", "X Premium"),
    "x_premium_basic": ("x", r"^X Premium Basic \(Monthly\)$", "X Premium Basic"),
    "x_premium_plus": ("x", r"^X Premium Plus \(Monthly\)$", "X Premium Plus"),
    "characterai_lite": ("characterai", r"^Character\.AI Lite$", "Character.AI Lite"),
    "characterai_plus": ("characterai", r"^Character\.AI\+$", "Character.AI+"),
    # added for the within-firm regressions of 13_relative_prices.py (appended so that the order of the other rows is unchanged)
    "youtube_premium_lite": ("youtube", r"^Premium Lite$", "YouTube Premium Lite"),
    "m365_family": ("copilot_m365", r"^Microsoft 365 Family$", "Microsoft 365 Family"),
    # added so that every named monthly plan of the five firms of the within-firm comparisons has a plan row (Table E.9 lists them)
    "supergrok_plus": ("grok", r"^SuperGrok Plus$", "SuperGrok Plus"),
    "m365_basic": ("copilot_m365", r"^Microsoft 365 Basic$", "Microsoft 365 Basic"),
    "x_creator": ("x", r"^@elonmusk Subscription$", "X creator subscription"),
    "youtube_premium_family": ("youtube", r"^Youtube Premium Family$", "YouTube Premium Family"),
    "youtubemusic_family": ("youtubemusic", r"^YouTube Music Family$", "YouTube Music Family"),
}   # analyze_v3.py also lists "spotify" with a pattern that matches nothing; it is omitted here

BENCH = [   # firm, product, plan key, app, item name (exact), group of Table 4 (frontier, capped, smallai, noai) or, for the items
            # that the rule of Table 4 excludes, "storage", "capped_one" (the Google One app's second listing of Google AI Plus), "family"
            # or "creator": every monthly subscription item of the five firms
            # listed in at least 60 storefronts, except annual variants and X's post-promotion product (Table E.9 and Figure E.1)
    ("Google", "YouTube Premium", "youtube_premium", "youtube", "YouTube Premium", "noai"),
    ("Google", "YouTube Premium Lite", "youtube_premium_lite", "youtube", "Premium Lite", "noai"),
    ("Google", "YouTube Music", "youtubemusic_music", "youtubemusic", "YouTube Music", "noai"),
    ("Google", "YouTube Premium Family", "youtube_premium_family", "youtube", "Youtube Premium Family", "family"),
    ("Google", "YouTube Music Family", "youtubemusic_family", "youtubemusic", "YouTube Music Family", "family"),
    ("Google", "Google One 100 GB", "gemini_100gb", "gemini", "100 GB", "storage"),
    ("Google", "Google AI Plus 2 TB (Google One app)", "googleone_aiplus2tb", "googleone", "Google AI Plus (2 TB)", "capped_one"),
    ("Google", "Google AI Plus", "gemini_plus", "gemini", "Google AI Plus (400 GB)", "capped"),
    ("Google", "Google AI Pro", "gemini_pro", "gemini", "Google AI Pro (5 TB)", "frontier"),
    ("Google", "Google AI Ultra", "gemini_ultra", "gemini", "Google AI Ultra (30 TB)", "frontier"),
    ("X Corp", "X creator subscription", "x_creator", "x", "@elonmusk Subscription", "creator"),
    ("X Corp", "X Premium Basic", "x_premium_basic", "x", "X Premium Basic (Monthly)", "noai"),
    ("X Corp", "X Premium", "x_premium", "x", "X Premium (Monthly)", "smallai"),
    ("X Corp", "X Premium Plus", "x_premium_plus", "x", "X Premium Plus (Monthly)", "frontier"),
    ("X Corp", "SuperGrok Lite", "supergrok_lite", "grok", "SuperGrok Lite", "capped"),
    ("X Corp", "SuperGrok", "supergrok", "grok", "SuperGrok", "frontier"),
    ("X Corp", "SuperGrok Plus", "supergrok_plus", "grok", "SuperGrok Plus", "frontier"),
    ("X Corp", "SuperGrok Heavy", "supergrok_heavy", "grok", "SuperGrok Heavy", "frontier"),
    ("Microsoft", "Microsoft 365 Basic", "m365_basic", "copilot_m365", "Microsoft 365 Basic", "storage"),
    ("Microsoft", "Microsoft 365 Personal", "m365_personal", "copilot_m365", "Microsoft 365 Personal", "smallai"),
    ("Microsoft", "Microsoft 365 Family", "m365_family", "copilot_m365", "Microsoft 365 Family", "family"),
    ("Microsoft", "Microsoft 365 Premium", "m365_premium", "copilot_m365", "Microsoft 365 Premium Monthly", "frontier"),
    ("Character.AI", "Character.AI Lite", "characterai_lite", "characterai", "Character.AI Lite", "capped"),
    ("Character.AI", "Character.AI+", "characterai_plus", "characterai", "Character.AI+", "frontier"),
    ("OpenAI", "ChatGPT Go", "chatgpt_go", "chatgpt", "ChatGPT Go", "capped"),
    ("OpenAI", "ChatGPT Plus", "chatgpt_plus", "chatgpt", "ChatGPT Plus", "frontier"),
    ("OpenAI", "ChatGPT Pro 100", "chatgpt_pro100", "chatgpt", "ChatGPT Pro 100", "frontier"),
    ("OpenAI", "ChatGPT Pro 200", "chatgpt_pro200", "chatgpt", "ChatGPT Pro 200", "frontier"),
    ("OpenAI", "ChatGPT Pro 500", "chatgpt_pro500", "chatgpt", "ChatGPT Pro 500", "frontier"),
]

FIRM = {"youtube": "google", "youtubemusic": "google", "gemini": "google", "googleone": "google", "x": "xcorp", "grok": "xcorp"}
GUARD_K = 3                       # a price above GUARD_K times the default-schedule price of the item's US price is flagged


def item_key(app, name):
    """Key of an item in results_wave2.json: the BENCH key, else the PLANS key, else app_ + the words of the name."""
    for _firm, _product, key, a, nm, _grp in BENCH:
        if (a, nm) == (app, name):
            return key
    for key, (a, pat, _label) in PLANS.items():
        if a == app and re.search(pat, name, re.I):
            return key
    words = re.findall(r"[a-z0-9]+", name.lower())
    if words and words[0] == app:
        words = words[1:]
    return "_".join([app] + words)


# ================================================================================================ core run
best, n_lines = last_records(RAW2 / "core" / "appstore_iap_raw_wave2.jsonl")
avail, rows = item_rows(best)
items = finish(rows, {a: v["class"] for a, v in APPS.items()})
status = collections.Counter()
for (app, s), c in avail.items():
    status[s] += c
R["wave2_records"] = n_lines
R["wave2_requests"] = len(best)
R["wave2_pages_200"] = status["local"] + status["no_local_storefront"]
R["wave2_local_pages"] = status["local"]
R["wave2_no_local_pages"] = status["no_local_storefront"]
R["wave2_app_not_offered"] = status["app_not_offered"]
R["wave2_errors"] = status["error"]
R["wave2_items"] = len(items)
R["wave2_storefronts_local"] = int(items.storefront.nunique())
R["wave2_apps"] = len({a for _, a in best})
R["wave2_parser_html_v2"] = int(sum(1 for r in best.values() if r.get("parser") == "html_v2"))
R["wave2_parser_json_v1"] = int(sum(1 for r in best.values() if r.get("parser") == "json_v1"))
R["wave2_pages_no_iap_list"] = int(sum(1 for r in best.values() if r.get("http_status") == 200 and not r.get("iap")))

# Apple's list of in-app purchases on a product page is capped: lengths of the non-empty lists of the local pages
lens = {k: len(r["iap"]) for k, r in best.items() if page_status(r, k[0]) == "local" and r.get("iap")}
R["wave2_list_max_items"] = int(max(lens.values()))
R["wave2_lists_nonempty"] = len(lens)
R["wave2_lists_with_10"] = int(sum(1 for n in lens.values() if n == 10))
gem = [k for k in lens if k[1] == "gemini" and not any("Ultra" in nm for nm, _ in best[k]["iap"])]
R["wave2_gemini_lists_without_ultra"] = len(gem)
R["wave2_gemini_lists_without_ultra_full"] = int(sum(1 for k in gem if lens[k] == 10))

# ================================================================================================ default panel
# (built here, before the item slopes, because the guard needs the storefront multipliers of the panel's schedule)
APPS_D = json.load(open(RAW2 / "apps_default_panel.json"))
bestd, nd_lines = last_records(RAW2 / "default_panel" / "appstore_iap_raw_wave2_default.jsonl")
availd, rowsd = item_rows(bestd)
itd = finish(rowsd, {a: v["class"] for a, v in APPS_D.items()})
itd = itd.drop(columns=["ratio_us", "ratio_us_alt_fx", "price_usd_alt_fx"])
itd.to_csv(PROC / "wave2_default_items_long.csv", index=False)
statd = collections.Counter()
for (app, s), c in availd.items():
    statd[s] += c
RD = {}                                                                   # merged into R below, where these keys used to be
RD["default_records"] = nd_lines
RD["default_requests"] = len(bestd)
RD["default_pages"] = statd["local"] + statd["no_local_storefront"]
RD["default_not_offered"] = statd["app_not_offered"]
RD["default_errors"] = statd["error"]
RD["default_items"] = len(itd)
RD["default_apps"] = int(itd.app.nunique())
RD["default_storefronts"] = int(itd.storefront.nunique())
RD["default_panel_apps_without_priced_subscription"] = len(
    set(APPS_D) - set(itd[(itd.type == "subscription") & itd.us_price.notna()].app))

# ------------------------------------------------------------------------------------ annual-as-monthly guard
_ladder, _mult = schedule(panel_points(itd), MAIN)                        # the schedule of 12_default_panel.py (same function)
MULT = {sf: v[0] for sf, v in _mult.items()}                              # storefront multiplier: local currency per US$ of base price
has_m = items.storefront.isin(MULT)
items["guard_ref"] = items.storefront.map(MULT) * items.us_price          # default-schedule price of the item's US price
items["flag_annual"] = ((items.storefront != "us") & items.us_price.notna() & items.ratio_us.notna() &
                        ((has_m & (items.price_local > GUARD_K * items.guard_ref)) |
                         (~has_m & (items.n_variants == 1) & (items.ratio_us > GUARD_K))))
items = items[[c for c in items.columns if c != "raw_strings"] + ["raw_strings"]]
items.to_csv(PROC / "wave2_items_long.csv", index=False)

cells = items[(items.storefront != "us") & items.us_price.notna() & items.ratio_us.notna() & items.gni.notna()]
R["guard_threshold_multiple"] = GUARD_K
R["guard_cells_considered"] = len(cells)
R["guard_flagged_cells"] = int(cells.flag_annual.sum())
R["guard_flagged_multiplier_rule"] = int((cells.flag_annual & cells.storefront.isin(MULT)).sum())
R["guard_flagged_no_multiplier_rule"] = int((cells.flag_annual & ~cells.storefront.isin(MULT)).sum())
R["guard_flagged_cells_all"] = int(items.flag_annual.sum())               # also the cells of storefronts without income data
R["guard_flagged_share"] = R["guard_flagged_cells"] / R["guard_cells_considered"]
R["guard_flagged_items"] = int(cells[cells.flag_annual].groupby(["app", "name"]).ngroups)


# ---------------------------------------------------------------------------------------- item-level income slopes
def trimmed(g):
    """The cells of one item that enter its slope: ratio to the US price in (0.05, 20)."""
    return g[(g.ratio_us > 0.05) & (g.ratio_us < 20)]


def item_slopes(c):
    """HC1 slope table of the items listed in >= 60 storefronts in the cells c (non-US, with US price, ratio and income)."""
    sl = []
    for (app, nm), g in c.groupby(["app", "name"], sort=False):
        g = trimmed(g)
        if len(g) < 60:
            continue
        b, se, n = ols_hc1(np.log(g.gni), np.log(g.ratio_us))
        b2, se2, _ = ols_hc1(np.log(g.gni), np.log(g.ratio_us_alt_fx))
        low = g[g.income_group.isin(LMIC)].ratio_us
        sl.append(dict(app=app, app_class=APPS[app]["class"], name=nm, type=g.type.iloc[0],
                       us_price=float(g.us_price.iloc[0]), n=n, slope=b, se=se, slope_alt_fx=b2, se_alt_fx=se2,
                       median_ratio=float(g.ratio_us.median()), n_lmic=int(len(low)),
                       median_ratio_lmic=(float(low.median()) if len(low) else NAN)))
    return pd.DataFrame(sl).sort_values(["app_class", "app", "n", "name"], ascending=[True, True, False, True], kind="stable")


slopes_pre = item_slopes(cells)                                           # before the guard (the sample of the first pass)
slopes_g = item_slopes(cells[~cells.flag_annual])                         # after the guard
R["wave2_item_slopes_n_preguard"] = len(slopes_pre)
R["wave2_item_slopes_n"] = len(slopes_g)                                  # after the guard, before the de-duplication


# ------------------------------------------------------------------------------------------ de-duplication of items
def norm_name(s):
    """Lower case; parentheses, punctuation and extra spaces removed."""
    return " ".join(re.sub(r"[^\w\s]", "", s.lower()).split())


def own_app(firm, norm):
    """The app whose product an item is (the tie-break of the de-duplication): youtube for Premium, youtubemusic for Music."""
    words = norm.split()
    if firm != "google":
        return None
    return "youtubemusic" if "music" in words else "youtube" if "premium" in words else None


def dedup(sl, vec):
    """-> (slope table without the duplicate items, list of (kept row, dropped row, reason))."""
    s = sl.copy()
    s["firm"] = [FIRM.get(a, a) for a in s.app]
    s["norm"] = [norm_name(n) for n in s.name]
    s["own"] = [0 if own_app(f, m) == a else 1 for f, m, a in zip(s.firm, s.norm, s.app)]
    s = s.sort_values(["firm", "norm", "n", "own", "app", "name"], ascending=[True, True, False, True, True, True], kind="stable")
    first, kept, dropped = {}, [], []
    for r in s.itertuples(index=False):
        k = (r.firm, r.norm)
        if k in first:
            dropped.append((first[k], r, "same firm and normalised name; smaller N"))
        else:
            first[k] = r
            kept.append(r)
    seen, final = {}, []
    for r in sorted(kept, key=lambda r: (-r.n, r.own, r.app, r.name)):
        sig = (r.app, vec[(r.app, r.name)])
        if sig in seen:
            dropped.append((seen[sig], r, "identical price vector within the app"))
        else:
            seen[sig] = r
            final.append(r)
    keep = {(r.app, r.name) for r in final}
    return sl[[(a, n) in keep for a, n in zip(sl.app, sl.name)]], dropped


VEC = {k: tuple(sorted(zip(g.storefront, g.price_local))) for k, g in items.groupby(["app", "name"], sort=False)}
slopes, dropped = dedup(slopes_g, VEC)
slopes.to_csv(PROC / "wave2_item_slopes.csv", index=False)
pd.DataFrame([dict(kept_app=k.app, kept_item=k.name, kept_n=int(k.n), kept_slope=float(k.slope), dropped_app=d.app,
                   dropped_item=d.name, dropped_n=int(d.n), dropped_slope=float(d.slope), reason=why)
              for k, d, why in sorted(dropped, key=lambda t: (t[1].app, t[1].name))]).to_csv(TAB / "W7_dedup.csv", index=False)
R["wave2_dedup_dropped_n"] = len(dropped)
R["wave2_item_slopes_n_after"] = len(slopes)                              # after the guard and the de-duplication

# ------------------------------------------------------------------------------------------ the guard: items and cells
pre_i, fin_i = slopes_pre.set_index(["app", "name"]), slopes.set_index(["app", "name"])
w6, GK = [], {}
for (app, nm), g in cells.groupby(["app", "name"], sort=False):
    if (app, nm) not in pre_i.index:
        continue
    g = trimmed(g)
    nf = int(g.flag_annual.sum())
    if nf == 0:
        continue
    kept_c = g[~g.flag_annual]
    b0, s0, n0 = ols_hc1(np.log(g.gni), np.log(g.ratio_us))
    b1, s1, n1 = ols_hc1(np.log(kept_c.gni), np.log(kept_c.ratio_us)) if len(kept_c) >= 30 else (NAN, NAN, len(kept_c))
    w6.append(dict(item=nm, app=app, item_key=item_key(app, nm), app_class=APPS[app]["class"], n=n0, n_flagged=nf,
                   slope_before=b0, se_before=s0, slope_after=b1, se_after=s1, n_after=n1,
                   in_slope_sample=bool((app, nm) in fin_i.index)))
w6 = pd.DataFrame(w6).sort_values(["n_flagged", "app", "item"], ascending=[False, True, True], kind="stable")
assert w6.item_key.is_unique
w6.to_csv(TAB / "W6_annual_guard.csv", index=False)
for r in w6[w6.n_flagged >= 5].itertuples():
    for k, v in [("n", int(r.n)), ("n_flagged", int(r.n_flagged)), ("slope_before", r.slope_before), ("se_before", r.se_before),
                 ("slope_after", r.slope_after), ("se_after", r.se_after), ("n_after", int(r.n_after))]:
        R[f"guard_{r.item_key}_{k}"] = v
fl = items[items.flag_annual].copy()
fl["rule"] = np.where(fl.storefront.isin(MULT), "price above 3 x default-schedule price", "single price above 3 x US price")
fl["in_regressions"] = fl.gni.notna()
fl[["storefront", "app", "name", "type", "currency", "price_local", "n_variants", "us_price", "guard_ref", "ratio_us", "gni",
    "income_group", "rule", "in_regressions"]].sort_values(["app", "name", "storefront"]).to_csv(TAB / "W6b_annual_guard_cells.csv", index=False)

# ------------------------------------------------------------------------------------------ class-level distributions
GROUPS = [("nonai", ["nonai"]), ("ai_feature", ["ai_feature"]), ("ai_all", ["ai", "ai_core"]), ("ai_core", ["ai_core"]),
          ("ai", ["ai"]), ("ai_bundle", ["ai_bundle"])]
cls_rows = []
for name, members in GROUPS:
    for typ in ["subscription", "consumable"]:
        s = slopes[slopes.app_class.isin(members) & (slopes.type == typ)].slope
        if not len(s):
            continue
        cls_rows.append(dict(item_class=name, members="+".join(members), type=typ, n=int(len(s)), median=float(s.median()),
                             p25=float(np.percentile(s, 25)), p75=float(np.percentile(s, 75)), share_gt_010=float((s > 0.10).mean())))
        for k, v in [("n", int(len(s))), ("median", float(s.median())), ("p25", float(np.percentile(s, 25))),
                     ("p75", float(np.percentile(s, 75))), ("share_gt010", float((s > 0.10).mean()))]:
            R[f"slopes_{name}_{typ}_{k}"] = v
pd.DataFrame(cls_rows).to_csv(TAB / "W5_item_classes.csv", index=False)

# app-level incidence: an app localises if any of its subscription items in the slope sample has a slope above 0.10
def app_incidence(sl):
    """-> (one row per app, [AI apps, AI apps that localise, non-AI apps, non-AI apps that localise], Fisher exact p, two-sided)."""
    sub = sl[sl.type == "subscription"]
    t = pd.DataFrame([dict(app=a, app_class=g.app_class.iloc[0], n_subscription_items=int(len(g)), max_slope=float(g.slope.max()),
                           localises=bool((g.slope > 0.10).any())) for a, g in sub.groupby("app", sort=True)])
    ai, non = t[t.app_class.isin(["ai", "ai_core"])], t[t.app_class == "nonai"]
    c = [int(len(ai)), int(ai.localises.sum()), int(len(non)), int(non.localises.sum())]
    return t, c, float(fisher_exact([[c[1], c[0] - c[1]], [c[3], c[2] - c[3]]])[1])


ap, c, p = app_incidence(slopes)
ap.to_csv(TAB / "W5b_applevel.csv", index=False)
R.update(applevel_ai_apps=c[0], applevel_ai_localise=c[1], applevel_nonai_apps=c[2], applevel_nonai_localise=c[3], applevel_fisher_p=p)
_, c, p = app_incidence(slopes_pre)                                       # the sample of the first pass (before the guard and the de-duplication)
R.update(applevel_preguard_ai_apps=c[0], applevel_preguard_ai_localise=c[1], applevel_preguard_nonai_apps=c[2],
         applevel_preguard_nonai_localise=c[3], applevel_preguard_fisher_p=p)

# ------------------------------------------------------------------------------------------------ plan rows
pr = []
irows = items.to_dict("records")
for plan, (app, pat, label) in PLANS.items():
    rx = re.compile(pat, re.I)
    by_sf = collections.defaultdict(list)
    for i in irows:
        if i["app"] == app and rx.search(i["name"]):
            by_sf[i["storefront"]].append(i)
    for sf in sorted(by_sf):
        i = max(by_sf[sf], key=lambda r: (r["n_variants"], -r["price_local"]))     # most-listed variant, then the lower price
        pr.append(dict(plan=plan, storefront=sf, app=app, name=i["name"], currency=i["currency"], price_local=i["price_local"],
                       price_usd=i["price_usd"], price_usd_alt_fx=i["price_usd_alt_fx"], n_variants=i["n_variants"],
                       us_price=i["us_price"], ratio_us=i["ratio_us"], ratio_us_alt_fx=i["ratio_us_alt_fx"],
                       gni=i["gni"], income_group=i["income_group"], flag_annual=bool(i["flag_annual"])))
plan_rows_all = pd.DataFrame(pr)                                          # before the guard (the stability check uses these)
plan_rows = plan_rows_all[~plan_rows_all.flag_annual].drop(columns="flag_annual").reset_index(drop=True)
plan_rows.to_csv(PROC / "wave2_plan_rows.csv", index=False)
R["wave2_plan_rows_preguard"] = len(plan_rows_all)
R["wave2_plan_rows"] = len(plan_rows)
R["guard_plan_rows_dropped"] = int(plan_rows_all.flag_annual.sum())
for plan, k in plan_rows_all.groupby("plan").flag_annual.sum().items():
    if k:
        R[f"guard_plan_{plan}_dropped"] = int(k)

# W1: plan descriptors and unconditional (all storefronts with a price) USD slopes
w1 = []
for plan, (app, pat, label) in PLANS.items():
    s = plan_rows[(plan_rows.plan == plan) & (plan_rows.storefront != "us")]
    s = s[s.ratio_us.notna() & s.gni.notna()]
    us = plan_rows[(plan_rows.plan == plan) & (plan_rows.storefront == "us")]
    b, se, n = ols_hc1(np.log(s.gni), np.log(s.ratio_us)) if len(s) >= 3 else (NAN, NAN, len(s))
    low = s[s.income_group.isin(LMIC)].ratio_us
    w1.append(dict(plan=plan, label=label, app=app, item_pattern=pat, us_price=(float(us.price_local.iloc[0]) if len(us) else NAN),
                   n_all=n, usd_slope_all=b, usd_se_all=se, median_ratio=float(s.ratio_us.median()) if len(s) else NAN,
                   median_ratio_lmic=float(low.median()) if len(low) else NAN))
pd.DataFrame(w1).to_csv(TAB / "W1_wave2_plans.csv", index=False)

# ------------------------------------------------------------------------------------------ benchmark items (W2)
sl_i = slopes_g.set_index(["app", "name"])                                # after the guard (a benchmark item is never a duplicate)
bm = []
for firm, product, key, app, nm, grp in BENCH:
    r = sl_i.loc[(app, nm)]
    bm.append(dict(firm=firm, product=product, key=key, app=app, item_name=nm, app_class=r.app_class, group=grp,
                   us_price=float(r.us_price), n=int(r.n), slope=float(r.slope), se=float(r.se),
                   slope_alt_fx=float(r.slope_alt_fx), median_ratio=float(r.median_ratio),
                   median_ratio_lmic=float(r.median_ratio_lmic)))
    for k, col in [("slope", "slope"), ("se", "se"), ("n", "n"), ("med_lmic_ratio", "median_ratio_lmic"), ("us_price", "us_price"),
                   ("slope_altfx", "slope_alt_fx")]:
        v = bm[-1][col]
        R[f"item_{key}_{k}"] = v
pd.DataFrame(bm).to_csv(TAB / "W2_benchmarks.csv", index=False)

# ------------------------------------------------------------------------ Plus/Go ratio within storefronts
pg = items[(items.app == "chatgpt") & items.name.isin(["ChatGPT Plus", "ChatGPT Go"]) & ~items.flag_annual].pivot_table(
    index="storefront", columns="name", values="price_local", aggfunc="first").dropna()
pg["ratio"] = pg["ChatGPT Plus"] / pg["ChatGPT Go"]
pg["grp"] = pg.index.map(GRP)
R["plusgo_ratio_us"] = float(pg.loc["us", "ratio"])
for g, v in pg.groupby("grp").ratio.median().items():
    R[f"plusgo_ratio_{SHORT[g]}"] = float(v)
R["plusgo_ratio_n"] = int(len(pg))

# ------------------------------------------------------------------------------ stability against wave 1 (27 Sep 2026)
w1p = pd.read_csv(ROOT / "data" / "processed" / "appstore_prices_long.csv", keep_default_na=False, na_values=[""])
MAP = {"chatgpt_pro5x": "chatgpt_pro100", "chatgpt_pro20x": "chatgpt_pro200"}
W1_LABEL = {"chatgpt_go": "ChatGPT Go", "chatgpt_plus": "ChatGPT Plus", "chatgpt_pro5x": r"ChatGPT Pro 100 (was 5$\times$)",
            "chatgpt_pro20x": r"ChatGPT Pro 200 (was 20$\times$)", "claude_pro": "Claude Pro", "claude_max5x": r"Claude Max 5$\times$",
            "claude_max20x": r"Claude Max 20$\times$", "gemini_plus": "Google AI Plus", "gemini_pro": "Google AI Pro",
            "gemini_ultra": "Google AI Ultra"}
p2 = plan_rows_all.set_index(["plan", "storefront"]).price_local          # the guard does not touch the stability check
st = []
for r in w1p.itertuples():
    if r.plan not in W1_LABEL:                       # gemini_plus_other: other Google AI Plus tiers, no wave-2 counterpart
        continue
    k = (MAP.get(r.plan, r.plan), r.storefront)
    if k not in p2.index:
        continue
    a, b = float(r.price_local), float(p2[k])
    st.append(dict(plan=r.plan, plan_wave2=k[0], storefront=r.storefront, price_local_w1=a, price_local_w2=b,
                   identical=bool(abs(a - b) < 0.005 * max(a, b))))
stab = pd.DataFrame(st)
stab.to_csv(PROC / "wave2_stability.csv", index=False)
w3 = []
for plan, label in W1_LABEL.items():
    s = stab[stab.plan == plan]
    w3.append(dict(plan=plan, label=label, compared=int(len(s)), identical=int(s.identical.sum()),
                   share_identical=float(s.identical.mean())))
    R[f"stab_{plan}_compared"], R[f"stab_{plan}_identical"] = int(len(s)), int(s.identical.sum())
    R[f"stab_{plan}_share"] = float(s.identical.mean())
w3.append(dict(plan="all", label="All", compared=int(len(stab)), identical=int(stab.identical.sum()),
               share_identical=float(stab.identical.mean())))
pd.DataFrame(w3).to_csv(TAB / "W3_stability.csv", index=False)
R["stab_all_compared"], R["stab_all_identical"], R["stab_all_share"] = int(len(stab)), int(stab.identical.sum()), float(stab.identical.mean())

R.update(RD)                                                              # the default-panel scalars

# fetch dates of the two waves, from the records themselves
R["wave1_fetch_date_utc"] = fetch_date(ROOT / "data" / "raw" / "appstore" / "appstore_iap_raw.jsonl")
R["wave2_fetch_date_utc"] = fetch_date(RAW2 / "core" / "appstore_iap_raw_wave2.jsonl",
                                        RAW2 / "default_panel" / "appstore_iap_raw_wave2_default.jsonl")
R["days_between_waves"] = (datetime.date.fromisoformat(R["wave2_fetch_date_utc"]) -
                           datetime.date.fromisoformat(R["wave1_fetch_date_utc"])).days

json.dump({k: (round(v, 6) if isinstance(v, float) else v) for k, v in R.items()},
          open(ROOT / "output" / "results_wave2.json", "w"), indent=1)


# ================================================================================================ data dictionary
def dictionary(file, frame, desc, source):
    """Rows of the data dictionary; `source` maps a variable to its source (default: derived)."""
    return [dict(file=file, variable=c, description=desc[c], source=source.get(c, "derived"), non_missing=int(frame[c].notna().sum()))
            for c in frame.columns]


APP = "Apple App Store product pages, 16 Oct 2026 (02b_scrape_wave2.py)"
SRC_A = {c: APP for c in ["storefront", "name", "currency", "price_local", "n_variants", "n_distinct_monthly", "raw_strings", "plan",
                          "app", "us_price"]}
SRC_A.update(app_class="apps_v3.json, apps_default_panel.json", price_usd="derived; open.er-api.com, 16 Oct 2026",
             price_usd_alt_fx="derived; fawazahmed0 currency-api, 15 Oct 2026", gni="World Bank WDI via country_panel.csv",
             income_group="World Bank FY2027 via country_panel.csv",
             guard_ref="derived; default-panel schedule (wave2_common.schedule) x US price")
D_ITEM = {
    "storefront": "App Store storefront code (lower-case ISO 3166 alpha-2; tw = Taiwan)",
    "app": "App key (apps_v3.json / apps_default_panel.json)",
    "app_class": "ai_core (ChatGPT, Claude, Gemini), ai, ai_bundle (Microsoft 365 with Copilot), ai_feature (AI features inside a general subscription), nonai; default_panel for the small-developer apps",
    "name": "In-app purchase name as listed on the storefront page",
    "type": "subscription, or consumable if the name matches the credit/coin/pack pattern (CONS in 09b_wave2_items.py)",
    "currency": "Storefront currency (schema.org priceCurrency)",
    "price_local": "Modal monthly price in local currency (mode of the listed prices below 5x the minimum; ties to the higher price)",
    "price_usd": "price_local / units per US$ (open.er-api.com, 16 Oct 2026)",
    "price_usd_alt_fx": "price_local / units per US$ (fawazahmed0 currency-api, 15 Oct 2026)",
    "n_variants": "Number of prices listed for this name on the page",
    "n_distinct_monthly": "Number of distinct prices below 5x the minimum",
    "us_price": "Price of the same app and item name in the US storefront (US$)",
    "ratio_us": "price_usd / us_price",
    "ratio_us_alt_fx": "price_usd_alt_fx / us_price",
    "gni": "GNI per capita, Atlas method, current US$ (country_panel.csv)",
    "income_group": "World Bank income group FY2027 (country_panel.csv)",
    "guard_ref": "Default-schedule price of the item's US price in this storefront: storefront multiplier of the small-developer panel x us_price (empty without a multiplier or a US price)",
    "flag_annual": "True if the cell is flagged by the annual-as-monthly guard: price_local > 3 x guard_ref, or (storefront without a multiplier) n_variants = 1 and ratio_us > 3; storefronts other than the US only; flagged cells are excluded from the item slopes and plan rows",
    "raw_strings": "Price strings as displayed (distinct, sorted)",
}
D_PLAN = {
    "plan": "Plan key (PLANS in 09b_wave2_items.py)", "storefront": D_ITEM["storefront"], "app": D_ITEM["app"],
    "name": "Name of the item chosen for the plan (most price variants, then the lower price)",
    "currency": D_ITEM["currency"], "price_local": D_ITEM["price_local"], "price_usd": D_ITEM["price_usd"],
    "price_usd_alt_fx": D_ITEM["price_usd_alt_fx"], "n_variants": D_ITEM["n_variants"], "us_price": D_ITEM["us_price"],
    "ratio_us": D_ITEM["ratio_us"], "ratio_us_alt_fx": D_ITEM["ratio_us_alt_fx"], "gni": D_ITEM["gni"],
    "income_group": D_ITEM["income_group"],
}
D_SLOPE = {
    "app": D_ITEM["app"], "app_class": D_ITEM["app_class"], "name": D_ITEM["name"], "type": D_ITEM["type"],
    "us_price": D_ITEM["us_price"], "n": "Storefronts (other than the US) with a ratio in (0.05, 20), income data and no flagged cell",
    "slope": "HC1 OLS slope of ln(ratio_us) on ln(gni): 0 = same US$ price everywhere", "se": "HC1 standard error of slope",
    "slope_alt_fx": "Same slope with the fawazahmed0 exchange rates", "se_alt_fx": "HC1 standard error of slope_alt_fx",
    "median_ratio": "Median ratio to the US price over the n storefronts",
    "n_lmic": "Number of those storefronts in low- and lower-middle-income economies",
    "median_ratio_lmic": "Median ratio to the US price in low- and lower-middle-income storefronts",
}
D_STAB = {
    "plan": "Wave-1 plan key (appstore_prices_long.csv)", "plan_wave2": "Wave-2 plan key (chatgpt_pro5x -> chatgpt_pro100, chatgpt_pro20x -> chatgpt_pro200)",
    "storefront": D_ITEM["storefront"], "price_local_w1": "Local monthly price, 27 Sep 2026",
    "price_local_w2": "Local monthly price, 16 Oct 2026",
    "identical": "True if |w1 - w2| < 0.5% of the larger of the two",
}
dic = (dictionary("wave2_items_long.csv", items, D_ITEM, SRC_A) +
       dictionary("wave2_default_items_long.csv", itd, D_ITEM, SRC_A) +
       dictionary("wave2_plan_rows.csv", plan_rows, D_PLAN, SRC_A) +
       dictionary("wave2_item_slopes.csv", slopes, D_SLOPE, SRC_A) +
       dictionary("wave2_stability.csv", stab, D_STAB, {c: "Apple App Store, 27 Sep 2026 and 16 Oct 2026" for c in
                                                                ["plan", "storefront", "price_local_w1", "price_local_w2"]}))
pd.DataFrame(dic).to_csv(PROC / "wave2_data_dictionary.csv", index=False)

print("wave 2 core:", R["wave2_requests"], "requests,", R["wave2_pages_200"], "pages,", R["wave2_local_pages"], "local,",
      R["wave2_app_not_offered"], "not offered;", R["wave2_items"], "items in", R["wave2_storefronts_local"], "storefronts;",
      R["wave2_item_slopes_n"], "item slopes after the guard,", R["wave2_item_slopes_n_after"], "after the de-duplication")
print("guard:", R["guard_flagged_cells"], "of", R["guard_cells_considered"], "cells flagged in", R["guard_flagged_items"], "items;",
      R["guard_plan_rows_dropped"], "plan rows dropped; dedup dropped", R["wave2_dedup_dropped_n"], "items")
print("app level:", R["applevel_ai_localise"], "of", R["applevel_ai_apps"], "AI apps,", R["applevel_nonai_localise"], "of",
      R["applevel_nonai_apps"], "non-AI apps localise (Fisher p =", round(R["applevel_fisher_p"], 3), ")")
print("default panel:", R["default_pages"], "pages,", R["default_apps"], "apps,", R["default_storefronts"], "storefronts,",
      R["default_items"], "items")
print("stability:", R["stab_all_identical"], "of", R["stab_all_compared"], "identical")
