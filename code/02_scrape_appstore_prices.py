"""
02_scrape_appstore_prices.py
Local, consumer-facing checkout prices for generative-AI subscriptions, collected through a single
uniform payment channel: the Apple App Store product page of each app in each national storefront.

For every (storefront, app) pair we record: HTTP status, final URL, storefront currency (schema.org
`priceCurrency` of the app offer), and the "In-App Purchases" list (item name, displayed price string).
Apple storefront prices are tax-inclusive in almost all storefronts; U.S. and Canadian prices exclude
sales tax. Only the extracted JSON is stored (not full HTML) to keep the package small.

Output: data/raw/appstore/appstore_iap_raw.jsonl  (one line per storefront x app)
"""
import json, re, time, datetime, pathlib, sys, random
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "appstore"
OUT.mkdir(parents=True, exist_ok=True)
APPS = {
    "chatgpt": "6448311069",   # ChatGPT (OpenAI)
    "claude": "6473753684",    # Claude by Anthropic
    "gemini": "6477489729",    # Google Gemini
}
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/17.5 Safari/605.1.15")

# The block title is localised ("In-App Purchases", "In-App-Käufe", "앱 내 구입", ...), so match any
# Annotation block carrying textPairs and keep its (localised) title for audit.
IAP_RE = re.compile(r'"\$kind":"Annotation","title":"([^"]*)","summary":"[^"]*","items":\[\{"\$kind":"AnnotationItem",'
                    r'"textPairs":(\[\[.*?\]\])\}')
CUR_RE = re.compile(r'"priceCurrency":"([A-Z]{3})"')
NAME_RE = re.compile(r'"@type":"SoftwareApplication","name":"([^"]+)"')


def storefronts():
    cm = pd.read_csv(ROOT / "data" / "raw" / "wb" / "country_metadata.csv", keep_default_na=False)
    cc = sorted({c.lower() for c, r in zip(cm.iso2, cm.region_id) if r != "NA" and len(c) == 2})
    for extra in ["tw", "hk", "mo", "xk"]:
        if extra not in cc:
            cc.append(extra)
    return cc


def fetch(cc, app, appid, tries=4):
    url = f"https://apps.apple.com/{cc}/app/id{appid}"
    rec = {"storefront": cc, "app": app, "app_id": appid, "request_url": url,
           "fetched_utc": datetime.datetime.utcnow().isoformat() + "Z"}
    for k in range(tries):
        try:
            r = requests.get(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"},
                             timeout=45, allow_redirects=True)
            rec["http_status"] = r.status_code
            rec["final_url"] = r.url
            if r.status_code == 200:
                h = r.content.decode("utf-8", errors="replace")   # pages are UTF-8; avoid requests' latin-1 guess
                m = IAP_RE.search(h)
                rec["iap_title"] = m.group(1) if m else None
                rec["iap"] = json.loads(m.group(2)) if m else None
                c = CUR_RE.search(h)
                rec["currency"] = c.group(1) if c else None
                n = NAME_RE.search(h)
                rec["app_name"] = n.group(1) if n else None
                rec["bytes"] = len(h)
                return rec
            if r.status_code in (404, 410):
                return rec
        except Exception as e:  # noqa
            rec["error"] = str(e)[:200]
        time.sleep(2 ** k + random.random())
    return rec


def main():
    ccs = storefronts()
    jobs = [(cc, app, appid) for cc in ccs for app, appid in APPS.items()]
    print(f"{len(ccs)} storefronts x {len(APPS)} apps = {len(jobs)} requests", flush=True)
    out = OUT / "appstore_iap_raw.jsonl"
    done = set()
    if out.exists():
        for line in out.read_text().splitlines():
            d = json.loads(line)
            if d.get("http_status") in (200, 404, 410):
                done.add((d["storefront"], d["app"]))
    jobs = [j for j in jobs if (j[0], j[1]) not in done]
    print("remaining:", len(jobs), flush=True)
    n = 0
    with ThreadPoolExecutor(max_workers=6) as ex, out.open("a") as f:
        futs = [ex.submit(fetch, *j) for j in jobs]
        for fu in as_completed(futs):
            rec = fu.result()
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            n += 1
            if n % 50 == 0:
                print(f"{n}/{len(jobs)}", flush=True)
    print("done", flush=True)


if __name__ == "__main__":
    main()
