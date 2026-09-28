"""
01_download_wb.py
Download World Bank data used in the paper:
  * Country metadata (ISO codes, region, CURRENT income classification = FY2027, published 1 July 2026)
  * World Development Indicators (source 2)
  * Global Findex 2025 indicators (source 28)
Raw API responses are saved as JSON; a tidy long CSV is written to data/raw/wb/.
Run date is recorded in data/raw/wb/_download_log.json.
"""
import json, time, datetime, pathlib, sys
import requests
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "wb"
OUT.mkdir(parents=True, exist_ok=True)
S = requests.Session()
S.headers.update({"User-Agent": "research-replication/1.0"})

WDI = {
    "NY.GNP.PCAP.CD": "GNI per capita, Atlas method (current US$)",
    "NY.GNP.PCAP.PP.CD": "GNI per capita, PPP (current international $)",
    "NY.GDP.PCAP.CD": "GDP per capita (current US$)",
    "NY.GDP.PCAP.PP.CD": "GDP per capita, PPP (current international $)",
    "NE.CON.PRVT.CD": "Households and NPISHs final consumption expenditure (current US$)",
    # PA.NUS.PPPC.RF is no longer served by the API ("Invalid value", Sep 2026); 10_build_dataset.py computes the same
    # GDP price-level ratio as NY.GDP.PCAP.CD / NY.GDP.PCAP.PP.CD.
    "PA.NUS.PPPC.RF": "Price level ratio of PPP conversion factor (GDP) to market exchange rate",
    "PA.NUS.FCRF": "Official exchange rate (LCU per US$, period average)",
    "SP.POP.TOTL": "Population, total",
    "SP.POP.1564.TO": "Population ages 15-64, total",
    "IT.NET.USER.ZS": "Individuals using the Internet (% of population)",
    "EG.ELC.ACCS.ZS": "Access to electricity (% of population)",
    "IT.NET.BBND.P2": "Fixed broadband subscriptions (per 100 people)",
    "SI.DST.FRST.10": "Income share held by lowest 10%",
    "SI.DST.FRST.20": "Income share held by lowest 20%",
    "SI.DST.02ND.20": "Income share held by second 20%",
    "SI.DST.03RD.20": "Income share held by third 20%",
    "SI.DST.04TH.20": "Income share held by fourth 20%",
    "SI.DST.05TH.20": "Income share held by highest 20%",
    "SI.DST.10TH.10": "Income share held by highest 10%",
    "SI.POV.GINI": "Gini index",
    "SE.TER.ENRR": "School enrollment, tertiary (% gross)",
    "HD.HCI.OVRL": "Human Capital Index (HCI) (scale 0-1)",
    "SP.URB.TOTL.IN.ZS": "Urban population (% of total population)",
    "SP.POP.65UP.TO.ZS": "Population ages 65 and above (% of total population)",
    "SL.EMP.WORK.ZS": "Wage and salaried workers, total (% of total employment)",
    "SL.SRV.EMPL.ZS": "Employment in services (% of total employment)",
}
FINDEX = {
    "account.t.d": "Account (% age 15+)",
    "fin10": "Owns a credit card (% age 15+)",
    "fin2.t.d": "Owns a debit card (% age 15+)",
    "fin27a": "Made a digital online merchant payment for an online purchase (% age 15+)",
    "g20.made": "Made a digital payment (% age 15+)",
    "con9a": "Main mobile phone is a smartphone (% age 15+)",
    "Internet": "Has access to the Internet (% age 15+)",
}


def get_json(url, tries=5):
    for k in range(tries):
        try:
            r = S.get(url, timeout=60)
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa
            wait = 2 ** k
            print(f"  retry {k+1} after error {e}; sleeping {wait}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"failed: {url}")


def fetch_indicator(code, source, date="2010:2025"):
    rows, page = [], 1
    while True:
        url = (f"https://api.worldbank.org/v2/country/all/indicator/{code}"
               f"?format=json&per_page=20000&date={date}&source={source}&page={page}")
        d = get_json(url)
        if not isinstance(d, list) or len(d) < 2 or d[1] is None:
            print(f"  no data for {code}: {str(d)[:200]}")
            break
        meta, data = d[0], d[1]
        for x in data:
            rows.append({
                "iso3": x.get("countryiso3code") or x["country"]["id"],
                "country_wb": x["country"]["value"],
                "indicator": code,
                "year": int(x["date"]),
                "value": x["value"],
                "source_id": source,
                "lastupdated": meta.get("lastupdated"),
            })
        if page >= int(meta.get("pages", 1)):
            break
        page += 1
    return rows


def main():
    log = {"run_utc": datetime.datetime.utcnow().isoformat() + "Z", "indicators": {}}
    # 1. country metadata (current classification)
    meta = get_json("https://api.worldbank.org/v2/country?format=json&per_page=400")
    (OUT / "country_metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    cm = pd.DataFrame([{
        "iso3": c["id"], "iso2": c["iso2Code"], "country_wb": c["name"],
        "region": c["region"]["value"], "region_id": c["region"]["id"],
        "income_group_current": c["incomeLevel"]["value"], "income_id_current": c["incomeLevel"]["id"],
        "lending": c["lendingType"]["value"], "capital": c["capitalCity"],
    } for c in meta[1]])
    cm.to_csv(OUT / "country_metadata.csv", index=False)
    print("countries:", (cm.region_id != "NA").sum(), "economies;", len(cm), "rows incl. aggregates")

    allrows = []
    for code, lab in WDI.items():
        print("WDI", code)
        rows = fetch_indicator(code, 2)
        allrows += rows
        log["indicators"][code] = {"label": lab, "source": 2, "n": len(rows),
                                   "lastupdated": rows[0]["lastupdated"] if rows else None}
    for code, lab in FINDEX.items():
        print("Findex", code)
        rows = fetch_indicator(code, 28, date="2011:2025")
        allrows += rows
        log["indicators"][code] = {"label": lab, "source": 28, "n": len(rows),
                                   "lastupdated": rows[0]["lastupdated"] if rows else None}
    df = pd.DataFrame(allrows)
    df.to_csv(OUT / "wb_indicators_long.csv", index=False)
    (OUT / "_download_log.json").write_text(json.dumps(log, indent=1))
    print("done:", len(df), "rows")


if __name__ == "__main__":
    main()
