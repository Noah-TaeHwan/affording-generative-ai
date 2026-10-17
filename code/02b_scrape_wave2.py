"""
02b_scrape_wave2.py
Second wave of the App Store price collection (16 October 2026): the same uniform payment channel as wave 1
(02_scrape_appstore_prices.py) -- the Apple App Store product page of an app in a national storefront -- extended in two ways.

  core     34 apps x 218 storefront codes (7,412 requests).  The three core apps of wave 1 (ChatGPT, Claude, Gemini,
           class ai_core), five further AI apps (Perplexity, Grok, Mistral, Poe, Character.AI; class ai), Microsoft 365
           with Copilot (ai_bundle), 21 non-AI subscription apps (YouTube, YouTube Music, Google One, Duolingo, Telegram,
           Discord, Snapchat, LinkedIn, Dropbox, Headspace, Calm, Strava, Tinder, Bumble, Truecaller, Babbel, X, Lightroom,
           NordVPN, Picsart, Evernote; nonai) and four apps whose AI features are sold inside a general subscription
           (Canva, CapCut, Notion, Grammarly; ai_feature).  App ids and classes are in apps_v3.json.
  default  30 small-developer apps (apps_default_panel.json) x the 167 storefronts in which the core run found a local
           storefront (local_storefronts.json) = 5,010 requests.  These apps have no pricing team of their own and
           reveal Apple's default price schedule (see 12_default_panel.py).

Inputs (data/raw/appstore_wave2/):  apps_v3.json, apps_default_panel.json, local_storefronts.json;
                                    data/raw/wb/country_metadata.csv (storefront codes of the core run)
Outputs:  data/raw/appstore_wave2/core/appstore_iap_raw_wave2.jsonl
          data/raw/appstore_wave2/default_panel/appstore_iap_raw_wave2_default.jsonl
          (one line per request attempt; requests answered with HTTP 429 are written too and retried on the next
          invocation, so a (storefront, app) pair can have several lines -- the analysis keeps the last line with
          status 200, 404 or 410)
          page archive (deposited as a separate file, appstore_wave2_page_archive_2026-10-16.zip, 12,860 gzipped files, 109 MB,
          in the Zenodo record of version 3.1; not part of the replication package itself):
          <archive-dir>/html/<app>_<storefront>.html.gz   full page, core apps only (chatgpt, claude, gemini)
          <archive-dir>/snip/<app>_<storefront>.html.gz   In-App Purchases block + JSON-LD, all apps
          Every JSONL line of a page carries `sha256`, the SHA-256 of the full page bytes, which links the parsed record
          to the archived page.

Page format.  On 27 September 2026 (wave 1) the In-App Purchases list was embedded as JSON in the page source
(`"$kind":"Annotation" ... "textPairs":[[name, price], ...]`); by 16 October 2026 Apple serves it as HTML
(`<dt>In-App Purchases</dt><dd> ... <div class="text-pair"><span>name</span> <span>price</span>`).  `fetch` tries the JSON
format first and falls back to the HTML format; `parser` in each record says which one was used (`json_v1` / `html_v2`).

Not run by run_all.sh (network).  Re-running today gives different prices and, once Apple changes the page again, may
need a new parser.  Usage:
    python code/02b_scrape_wave2.py core    > data/raw/_log_appstore_wave2.txt          # 7,412 requests, about 1 h
    python code/02b_scrape_wave2.py default > data/raw/_log_appstore_wave2_default.txt  # 5,010 requests, about 45 min
    python code/02b_scrape_wave2.py both [--archive-dir DIR | --no-archive] [--workers 3] [--dry-run]
Re-invoke until `remaining` reaches 0 (requests answered with HTTP 429 are retried).  Request order is shuffled with
a fixed seed; three workers and a random 0.2-0.8 s pause per request keep the load on Apple's servers low.
Standard library only.
"""
import argparse, csv, datetime, gzip, hashlib, html as _html, json, pathlib, random, re, sys, time
import urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
W2 = RAW / "appstore_wave2"
RUNS = {  # run -> (app list, output file)
    "core": (W2 / "apps_v3.json", W2 / "core" / "appstore_iap_raw_wave2.jsonl"),
    "default": (W2 / "apps_default_panel.json", W2 / "default_panel" / "appstore_iap_raw_wave2_default.jsonl"),
}
CORE = {"chatgpt", "claude", "gemini"}   # apps whose full pages are archived

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/17.5 Safari/605.1.15")
# --- parsing (the stdlib scrape_lib.py of the first pass of this wave) ------------------------------------------------------------------
IAP_RE = re.compile(r'"\$kind":"Annotation","title":"([^"]*)","summary":"[^"]*","items":\[\{"\$kind":"AnnotationItem",'
                    r'"textPairs":(\[\[.*?\]\])\}')
CUR_RE = re.compile(r'"priceCurrency":"([A-Z]{3})"')
NAME_RE = re.compile(r'"@type":"SoftwareApplication","name":"([^"]+)"')
TP_RE = re.compile(r'<div class="text-pair[^"]*"><span>(.*?)</span>\s*<span>(.*?)</span>', re.S)
LD_RE = re.compile(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', re.S)


def parse_iap_html(h):
    """2026-10 page format: <dt>In-App Purchases</dt><dd><details>...<ul><li><div class="text-pair"><span>NAME</span> <span>PRICE</span>"""
    pairs = TP_RE.findall(h)
    if not pairs:
        return None, None, "html_v2_none"
    i = h.find('class="text-pair')
    k = h.rfind('<dt', 0, i)
    dt = re.sub('<[^>]+>', '', h[k:h.find('</dt>', k)]).strip() if k >= 0 else None
    return (_html.unescape(dt) if dt else None), [[_html.unescape(a).strip(), _html.unescape(b).strip()] for a, b in pairs], "html_v2"


def fetch(cc, app, appid, tries=4):
    """One request attempt (with up to `tries` retries on errors and HTTP 429).  Returns (record, page bytes or None)."""
    url = f"https://apps.apple.com/{cc}/app/id{appid}"
    rec = {"storefront": cc, "app": app, "app_id": appid, "request_url": url,
           "fetched_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    html = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
            with urllib.request.urlopen(req, timeout=45) as r:
                rec["http_status"] = r.status
                rec["final_url"] = r.geturl()
                b = r.read()
            h = b.decode("utf-8", "replace")
            html = b
            m = IAP_RE.search(h)
            if m:
                rec["iap_title"] = m.group(1)
                rec["iap"] = json.loads(m.group(2))
                rec["parser"] = "json_v1"
            else:
                rec["iap_title"], rec["iap"], rec["parser"] = parse_iap_html(h)
            c = CUR_RE.search(h)
            rec["currency"] = c.group(1) if c else None
            n = NAME_RE.search(h)
            rec["app_name"] = n.group(1) if n else None
            rec["bytes"] = len(b)
            return rec, html
        except urllib.error.HTTPError as e:
            rec["http_status"] = e.code
            rec["final_url"] = url
            if e.code in (404, 410):
                return rec, None
        except Exception as e:  # noqa
            rec["error"] = str(e)[:200]
        time.sleep(2 ** k + random.random())
    return rec, html


# --- storefront and job lists ----------------------------------------------------------------------------------
def core_storefronts():
    """All ISO2 codes of World Bank economies (as wave 1) plus Taiwan, Hong Kong, Macao and Kosovo: 218 codes."""
    cm = list(csv.DictReader(open(RAW / "wb" / "country_metadata.csv", encoding="utf-8")))
    ccs = sorted({r["iso2"].lower() for r in cm if r.get("region_id") != "NA" and len(r["iso2"]) == 2})
    for x in ["tw", "hk", "mo", "xk"]:
        if x not in ccs:
            ccs.append(x)
    return ccs


def run(which, archive, workers, dry):
    apps_file, out = RUNS[which]
    apps = json.load(open(apps_file))
    ccs = core_storefronts() if which == "core" else json.load(open(W2 / "local_storefronts.json"))
    jobs = [(cc, a, v["id"]) for cc in ccs for a, v in apps.items()]
    print(len(ccs), "storefronts x", len(apps), "apps; requests", len(jobs), flush=True)
    done = set()
    if out.exists():
        for line in out.read_text().splitlines():
            d = json.loads(line)
            if d.get("http_status") in (200, 404, 410):
                done.add((d["storefront"], d["app"]))
    jobs = [j for j in jobs if (j[0], j[1]) not in done]
    random.seed(7)
    random.shuffle(jobs)
    print("remaining", len(jobs), flush=True)
    if dry or not jobs:
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    if archive:
        (archive / "html").mkdir(parents=True, exist_ok=True)
        (archive / "snip").mkdir(parents=True, exist_ok=True)

    def work(j):
        cc, a, i = j
        time.sleep(random.uniform(0.2, 0.8))
        rec, h = fetch(cc, a, i)
        if h:
            rec["sha256"] = hashlib.sha256(h).hexdigest()
            if archive:
                s = h.decode("utf-8", "replace")
                if a in CORE:
                    (archive / "html" / f"{a}_{cc}.html.gz").write_bytes(gzip.compress(h))
                k = s.find('class="text-pair')
                dt = s.rfind('<dt', 0, k) if k >= 0 else -1
                e = s.find('</dd>', k) if k >= 0 else -1
                snip = (s[dt:e + 5] if dt >= 0 and e > 0 else "") + "\n<!--LD-->\n" + "\n".join(LD_RE.findall(s))
                (archive / "snip" / f"{a}_{cc}.html.gz").write_bytes(gzip.compress(snip.encode()))
        return rec

    n = 0
    with ThreadPoolExecutor(max_workers=workers) as ex, out.open("a") as f:
        for fu in as_completed([ex.submit(work, j) for j in jobs]):
            f.write(json.dumps(fu.result(), ensure_ascii=False) + "\n")
            f.flush()
            n += 1
            if n % 200 == 0:
                print(time.strftime("%H:%M:%S"), n, "/", len(jobs), flush=True)
    print("done", time.strftime("%H:%M:%S"), flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("which", choices=["core", "default", "both"])
    ap.add_argument("--archive-dir", type=pathlib.Path, default=W2 / "pages",
                    help="where the gzipped pages go (default data/raw/appstore_wave2/pages; not part of the deposit)")
    ap.add_argument("--no-archive", action="store_true", help="do not keep the pages (the sha256 link is then lost)")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--dry-run", action="store_true", help="count the remaining requests and stop")
    a = ap.parse_args()
    for which in (["core", "default"] if a.which == "both" else [a.which]):
        run(which, None if a.no_archive else a.archive_dir / which, a.workers, a.dry_run)


if __name__ == "__main__":
    main()
