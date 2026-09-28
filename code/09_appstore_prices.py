"""
09_appstore_prices.py
Clean the App Store scrape (02_scrape_appstore_prices.py) into monthly local prices by storefront and plan,
convert to US dollars at market exchange rates on the scrape date, and flag storefront availability.

Output: data/processed/appstore_prices_long.csv, data/processed/appstore_prices_wide.csv
"""
import json, re, glob, pathlib, collections
import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW, PROC = ROOT / "data" / "raw", ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)

recs = [json.loads(l) for l in open(RAW / "appstore" / "appstore_iap_raw.jsonl")]
er = json.load(open(sorted(glob.glob(str(RAW / "fx" / "er_api_usd_*.json")))[-1]))
fw = json.load(open(sorted(glob.glob(str(RAW / "fx" / "fawaz_usd_*.json")))[-1]))
RATES = er["rates"]                                   # units of currency per 1 USD
RATES2 = {k.upper(): v for k, v in fw["usd"].items()}


def parse_price(s):
    """Return a float from an App Store price string in any storefront format."""
    if s is None:
        return np.nan
    t = s.replace("\xa0", " ").strip()
    mult = 1.0
    if re.search(r"ribu", t, re.I):
        mult = 1e3
    elif re.search(r"\bjt\b|juta", t, re.I):
        mult = 1e6
    m = re.search(r"\d[\d.,'\s]*", t)
    if not m:
        return np.nan
    num = m.group(0).strip().replace("'", "").replace(" ", "")
    if mult != 1.0:                                          # Indonesian abbreviations: "Rp 1,889juta" = 1.889 million
        return float(num.replace(".", "").replace(",", ".")) * mult
    if "," in num and "." in num:
        dec = "," if num.rfind(",") > num.rfind(".") else "."
        thou = "." if dec == "," else ","
        num = num.replace(thou, "").replace(dec, ".")
    elif "," in num or "." in num:
        sep = "," if "," in num else "."
        parts = num.split(sep)
        if len(parts) == 2 and len(parts[1]) in (1, 2):      # decimal separator (e.g. 19,99 or 19.99)
            num = parts[0] + "." + parts[1]
        else:                                                # thousands separator (e.g. 1,999 or 309.000)
            num = "".join(parts)
    return float(num) * mult


def plan_of(app, name):
    n = name.lower()
    if app == "chatgpt":
        if "credit" in n:
            return None
        if "pro 20x" in n: return "chatgpt_pro20x"
        if "pro 5x" in n: return "chatgpt_pro5x"
        if re.search(r"\bgo\b", n): return "chatgpt_go"
        if "plus" in n: return "chatgpt_plus"
    if app == "claude":
        if "credit" in n or "annual" in n or "jährlich" in n:
            return None
        if "max 20x" in n: return "claude_max20x"
        if "max 5x" in n: return "claude_max5x"
        if "pro" in n: return "claude_pro"
    if app == "gemini":
        if "ultra" in n: return "gemini_ultra"
        if "ai pro" in n: return "gemini_pro"
        if "ai plus" in n: return "gemini_plus" if "400" in n else "gemini_plus_other"
    return None


def monthly(prices):
    """Pick the monthly price among listed variants: drop the annual cluster (>=5x the minimum), then take the mode."""
    p = sorted(prices)
    low = [x for x in p if x < 5 * p[0]]
    cnt = collections.Counter(low)
    top = max(cnt.values())
    return max(v for v, c in cnt.items() if c == top), len(p), len(low), min(low), len(cnt)


rows, avail = [], []
for r in recs:
    sf, app = r["storefront"], r["app"]
    st = r.get("http_status")
    final_sf = re.search(r"apps\.apple\.com/([a-z]{2})/", r.get("final_url") or "")
    final_sf = final_sf.group(1) if final_sf else None
    if st == 404:
        status = "app_not_offered"
    elif st == 200 and final_sf == sf:
        status = "local_storefront"
    elif st == 200:
        status = "no_local_storefront"          # Apple redirects to the US storefront
    else:
        status = "error"
    avail.append({"storefront": sf, "app": app, "status": status, "currency": r.get("currency")
                  if status == "local_storefront" else None, "iap_title": r.get("iap_title")})
    if status != "local_storefront" or not r.get("iap"):
        continue
    byplan = collections.defaultdict(list)
    for name, ps in r["iap"]:
        pl = plan_of(app, name)
        if pl:
            byplan[pl].append((parse_price(ps), ps, name))
    for pl, items in byplan.items():
        vals = [v for v, _, _ in items if np.isfinite(v)]
        if not vals:
            continue
        m, n_all, n_low, m_min, n_dist = monthly(vals)
        cur = r.get("currency")
        rate, rate2 = RATES.get(cur), RATES2.get(cur)
        rows.append({"storefront": sf, "app": app, "plan": pl, "currency": cur, "price_local": m,
                     "price_usd": m / rate if rate else np.nan,
                     "price_usd_alt_fx": m / rate2 if rate2 else np.nan,
                     "n_variants": n_all, "n_monthly_candidates": n_low, "n_distinct_monthly": n_dist,
                     "price_local_min_candidate": m_min,
                     "price_usd_min_candidate": m_min / rate if rate else np.nan,
                     "raw_strings": " | ".join(sorted({s for _, s, _ in items})),
                     "fetched_utc": r.get("fetched_utc")})

long = pd.DataFrame(rows)
av = pd.DataFrame(avail)
long["fx_source"] = f"open.er-api.com {er['time_last_update_utc']}"
long["fx_check_ratio"] = long.price_usd / long.price_usd_alt_fx
us = long[long.storefront == "us"].set_index("plan")["price_usd"]
long["rel_to_us"] = long.price_usd / long.plan.map(us)
# Where only an annual variant appears among the listed in-app purchases the monthly price is not observed:
bad = long.rel_to_us >= 5
print("dropped (only annual variant listed):", long.loc[bad, ["storefront", "plan", "raw_strings"]].values.tolist())
long = long[~bad].copy()
long.to_csv(PROC / "appstore_prices_long.csv", index=False)

wide = long.pivot_table(index="storefront", columns="plan", values="price_usd", aggfunc="first")
wide.columns = [f"p_{c}" for c in wide.columns]
cur = long.groupby("storefront")["currency"].first().rename("store_currency")
st = av.pivot_table(index="storefront", columns="app", values="status", aggfunc="first")
st.columns = [f"store_{c}" for c in st.columns]
wide = wide.join(cur, how="outer").join(st, how="outer")
cm = pd.read_csv(RAW / "wb" / "country_metadata.csv", keep_default_na=False)
cm["storefront"] = cm.iso2.str.lower()
wide = wide.reset_index().merge(cm[["storefront", "iso3"]], on="storefront", how="left")
wide = wide[wide.iso3.notna() & (wide.iso3 != "")]
wide.to_csv(PROC / "appstore_prices_wide.csv", index=False)

print("local price rows:", len(long), "| storefronts with any price:", long.storefront.nunique())
print("FX check (median, min, max of er-api/fawaz):", long.fx_check_ratio.median().round(4),
      long.fx_check_ratio.min().round(3), long.fx_check_ratio.max().round(3))
print(av.groupby(["app", "status"]).size().unstack(fill_value=0))
print(long.groupby("plan").agg(n=("price_usd", "size"), us=("price_usd", lambda s: s[long.loc[s.index, 'storefront'] == 'us'].mean()),
                               med=("price_usd", "median"), p10=("price_usd", lambda s: s.quantile(.1)),
                               p90=("price_usd", lambda s: s.quantile(.9))).round(2))
