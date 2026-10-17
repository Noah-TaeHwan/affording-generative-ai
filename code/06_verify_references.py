"""
06_verify_references.py
Verify bibliographic metadata of candidate references against Crossref (DOIs) and arXiv (preprints).
Writes research/refs_verified.csv (one row per reference, with the metadata actually registered) and
research/refs_crossref.bib (BibTeX served by Crossref content negotiation, keys rewritten).
"""
import csv, json, re, time, pathlib, sys, urllib.parse
import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "research"
S = requests.Session()
S.headers.update({"User-Agent": "affording-genai-replication/1.0 (mailto:noah.taehwan@gmail.com)"})

# key, DOI (or None), fallback query
CANDS = [
    ("brynjolfsson2025generative", "10.1093/qje/qjae044", None),
    ("noy2023experimental", "10.1126/science.adh2586", None),
    ("dellacqua2023navigating", "10.2139/ssrn.4573321", None),
    ("eloundou2024gpts", "10.1126/science.adj0998", None),
    ("humlum2025unequal", "10.1073/pnas.2414972121", None),
    ("humlum2025large", "10.3386/w33777", None),
    ("bick2024rapid", "10.3386/w32966", None),
    ("chatterji2025how", "10.3386/w34255", None),
    ("acemoglu2025simple", "10.1093/epolic/eiae042", None),
    ("hulten1978growth", "10.2307/2297252", None),
    ("comin2010exploration", "10.1257/aer.100.5.2031", None),
    ("comin2018technology", "10.1257/mac.20150175", None),
    ("comin2004cross", "10.1016/j.jmoneco.2003.07.003", None),
    ("griliches1957hybrid", "10.2307/1905380", None),
    ("cavallo2014currency", "10.1093/qje/qju008", None),
    ("hjort2019arrival", "10.1257/aer.20161385", None),
    ("aguirre2010monopoly", "10.1257/aer.100.4.1601", None),
    ("acemoglu2019automation", "10.1257/jep.33.2.3", None),
    ("autor2024applying", "10.3386/w32140", None),
    ("korinek2021artificial", "10.3386/w28453", None),
    ("cazzaniga2024genai", "10.5089/9798400262548.006", None),
    ("pizzinelli2023labor", "10.5089/9798400254802.001", None),
    ("gmyrek2023generative", "10.54394/FHEM8239", None),
    ("gmyrek2025generative", "10.54394/HETP0387", None),
    ("felten2021occupational", "10.1002/smj.3286", None),
    ("filippucci2024impact", "10.1787/8d900037-en", None),
    ("korinek2024scenarios", "10.3386/w32255", None),
    ("liu2024who", "10.1596/1813-9450-10870", None),
    ("liu2025who", "10.1596/1813-9450-11231", None),
    ("desimone2025chalkboards", "10.1596/1813-9450-11125", None),
    ("kanazawa2022ai", "10.3386/w30612", None),
    ("balassa1964purchasing", "10.1086/258965", None),
    ("samuelson1964theoretical", "10.2307/1928178", None),
    ("deaton2010understanding", "10.1257/mac.2.4.1", None),
    ("goldfarb2019digital", "10.1257/jel.20171452", None),
    ("bjorkegren2019adoption", "10.1093/restud/rdy024", None),
    ("aker2010mobile", "10.1257/jep.24.3.207", None),
    ("dupas2014short", "10.3982/ECTA9508", None),
    ("cohen2010free", "10.1162/qjec.2010.125.1.1", None),
    ("suri2011selection", "10.3982/ECTA7749", None),
    ("foster2010microeconomics", "10.1146/annurev.economics.102308.124433", None),
    ("hall2003adoption", "10.3386/w9730", None),
    ("caselli2001cross", "10.1257/aer.91.2.328", None),
    ("chinn2007determinants", "10.1093/oep/gpl024", None),
    ("mussa1978monopoly", "10.1016/0022-0531(78)90085-6", None),
    ("brynjolfsson2019using", "10.1073/pnas.1815663116", None),
    ("goolsbee2006valuing", "10.1257/000282806777212521", None),
    ("korinek2023generative", "10.1257/jel.20231736", None),
    ("bresnahan1995general", "10.1016/0304-4076(94)01598-T", None),
    ("varian1985price", None, "Price Discrimination and Social Welfare Varian 1985 American Economic Review"),
    ("goldberg1997goods", None, "Goods Prices and Exchange Rates: What Have We Learned? Goldberg Knetter 1997"),
    ("otis2024uneven", None, "The Uneven Impact of Generative AI on Entrepreneurial Performance Otis Clarke Delecourt Holtz Koning"),
    ("cui2025effects", None, "The Effects of Generative AI on High-Skilled Work: Evidence from Three Field Experiments with Software Developers"),
    ("hartley2025labor", None, "The Labor Market Effects of Generative Artificial Intelligence Hartley Jolevski Melo Moore"),
    ("choi2024lawyering", None, "Lawyering in the Age of Artificial Intelligence Choi Monahan Schwarcz"),
    ("nagle2025latent", None, "The Latent Role of Open Models in the AI Economy Nagle Yue"),
    ("aghion2024ai", None, "AI and Growth: Where Do We Stand? Aghion Bunel"),
    ("klapper2025findex", None, "The Global Findex Database 2025 Connectivity and Financial Inclusion in the Digital Economy"),
    ("wdr2026", None, "World Development Report 2026 artificial intelligence World Bank"),
    ("hdr2025", None, "Human Development Report 2025 A matter of choice people and possibilities in the age of AI"),
    ("unctad2025tir", None, "Technology and Innovation Report 2025 Inclusive Artificial Intelligence for Development UNCTAD"),
    ("jack2014risk", "10.1257/aer.104.1.183", None),
    ("ashraf2010higher", "10.1257/aer.100.5.2383", None),
    ("lehdonvirta2024compute", None, "Compute North vs. Compute South: The Uneven Possibilities of Compute-based AI Governance Around the Globe"),
    ("maslej2025aiindex", None, "Artificial Intelligence Index Report 2025 Maslej"),
    ("peng2023impact", None, "The Impact of AI on Developer Productivity: Evidence from GitHub Copilot"),
    # version 3.0 additions (October 2026)
    ("dellavigna2019uniform", "10.1093/qje/qjz019", None),
    ("simonovska2015income", "10.1093/restud/rdv015", None),
    ("krugman1986pricing", "10.3386/w1926", None),
    ("atkeson2008pricing", "10.1257/aer.98.5.1998", None),
    ("deneckere1996damaged", "10.1111/j.1430-9134.1996.00149.x", None),
    ("bhargava2001information", "10.1080/07421222.2001.11045681", None),
    ("bhargava2008versioning", "10.1287/mnsc.1070.0773", None),
    ("sundararajan2004nonlinear", "10.1287/mnsc.1040.0291", None),
    ("shiller2011music", "10.1111/j.1467-6451.2011.00470.x", None),
    ("waldfogel2020spotify", "10.1007/s11151-020-09748-0", None),
    ("danzon2000crossnational", "10.1016/S0167-6296(99)00039-9", None),
    ("wang2017advalorem", "10.1111/1756-2171.12183", None),
    ("callaway2021did", "10.1016/j.jeconom.2020.12.001", None),
    ("cui2024effects", "10.2139/ssrn.4945566", None),
    ("kanzamanova2026digital", "10.3390/systems14080889", None),
    ("andre2025markets", "10.1787/9302bf46-en", None),
    ("otis2025uneven", "10.31219/osf.io/hdjpk_v2", None),
    ("varian1985price", None, "Price discrimination and social welfare Varian American Economic Review 1985"),
    ("goldberg1997goods", None, "Goods prices and exchange rates: what have we learned? Goldberg Knetter Journal of Economic Literature 1997"),
    # version 3.1 additions (October 2026): literature audit (lit/add_refs.bib), mathematical audit (math/new_refs.bib) and
    # references verified by the author on Crossref
    ("enache2023demand", "10.1016/j.ijindorg.2023.102945", None),
    ("colbjornsen2022what", "10.1080/16522354.2021.1949568", None),
    ("cabolis2007textbook", "10.1016/j.econlet.2006.09.019", None),
    ("chellappa2018cost", "10.1287/mnsc.2016.2698", None),
    ("jones2011information", "10.1287/mnsc.1100.1262", None),
    ("essegaier2002pricing", "10.1287/mksc.21.2.139.149", None),
    ("johnson2003multiproduct", "10.1257/000282803322157070", None),
    ("demirer2025emerging", "10.3386/w34608", None),
    ("demirer2026emerging", "10.1257/jep.20261506", None),
    ("korinek2025concentrating", "10.1093/epolic/eiae057", None),
    ("gans2026market", "10.1146/annurev-economics-051624-061832", None),
    ("sampford1953some", "10.1214/aoms/1177729093", None),
    ("bagnoli2005logconcave", "10.1007/s00199-004-0514-4", None),
    ("weyl2013passthrough", "10.1086/670401", None),
    ("goldberg2001evolution", "10.1111/1467-937X.00191", None),
    ("gopinath2011international", "10.1257/aer.101.6.2450", None),
    ("malueg1994parallel", "10.1016/0022-1996(94)90044-2", None),
    ("valletti2006differential", "10.1016/j.jinteco.2005.07.010", None),
    ("levy1997magnitude", "10.1162/003355397555352", None),
    ("zbaracki2004managerial", "10.1162/003465304323031085", None),
    ("anderson2010price", "10.1162/qjec.2010.125.2.729", None),
]

ARXIV = {
    "misra2025measuring": "2511.02781",
    "handa2025which": "2503.04761",
    "daepp2026how": "2605.30685",
    "aubakirova2026state": "2601.10088",
    "peng2023impact_arxiv": "2302.06590",
    "merali2024scaling": "2409.02391",
    "maslej2025aiindex_arxiv": "2504.07139",
    "sathish2024llempower": "2404.09356",
    "bergemann2025menu": "2502.07736",
}


def cr_doi(doi):
    r = S.get("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/()"), timeout=40)
    if r.status_code != 200:
        return None
    return r.json()["message"]


def cr_search(q):
    r = S.get("https://api.crossref.org/works", params={"query.bibliographic": q, "rows": 3}, timeout=40)
    if r.status_code != 200:
        return []
    return r.json()["message"]["items"]


def bib(doi):
    r = S.get("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/()") + "/transform/application/x-bibtex",
              timeout=40)
    return r.text if r.status_code == 200 else None


def summarize(m):
    au = "; ".join(f"{a.get('family','')}, {a.get('given','')}" for a in m.get("author", [])) or \
         "; ".join(e.get("name", "") for e in m.get("editor", []))
    yr = (m.get("published-print") or m.get("published-online") or m.get("issued") or {}).get("date-parts", [[None]])[0][0]
    return {
        "doi": m.get("DOI"), "type": m.get("type"), "title": (m.get("title") or [""])[0],
        "authors": au, "year": yr, "container": (m.get("container-title") or [""])[0],
        "volume": m.get("volume"), "issue": m.get("issue"), "page": m.get("page"),
        "publisher": m.get("publisher"),
    }


def arxiv(aid):
    """Metadata of an arXiv preprint: the export API (HTTPS), or, when it is rate-limited or unreachable, the Highwire
    meta tags of the abstract page."""
    title, auths, year = None, [], None
    try:
        r = S.get("https://export.arxiv.org/api/query", params={"id_list": aid}, timeout=40)
        t = r.text if r.status_code == 200 else ""
    except requests.RequestException:
        t = ""
    m = re.search(r"<entry>.*?<title>(.*?)</title>", t, re.S)
    if m:
        title = re.sub(r"\s+", " ", m.group(1)).strip()
        auths = re.findall(r"<author>\s*<name>(.*?)</name>", t)
        pub = re.search(r"<published>(\d{4})-(\d\d)-(\d\d)", t)
        year = pub.group(1) if pub else None
    if not title:
        time.sleep(3)
        r = S.get(f"https://arxiv.org/abs/{aid}", timeout=40)
        t = r.text if r.status_code == 200 else ""
        m = re.search(r'<meta name="citation_title" content="(.*?)"', t)
        title = re.sub(r"\s+", " ", m.group(1)).strip() if m else None
        auths = re.findall(r'<meta name="citation_author" content="(.*?)"', t)
        pub = re.search(r'<meta name="citation_date" content="(\d{4})', t)
        year = pub.group(1) if pub else None
    return {"doi": f"10.48550/arXiv.{aid}", "type": "preprint-arXiv", "title": title, "authors": "; ".join(auths), "year": year,
            "container": f"arXiv:{aid}", "volume": None, "issue": None, "page": None, "publisher": "arXiv"}


def main():
    rows, bibs = [], []
    for key, doi, q in CANDS:
        try:
            if doi:
                m = cr_doi(doi)
                if m is None:
                    rows.append({"key": key, "status": "DOI_NOT_FOUND", "doi": doi}); continue
                d = summarize(m); d.update(key=key, status="OK_DOI")
                rows.append(d)
                b = bib(doi)
                if b:
                    bibs.append(re.sub(r"^@(\w+)\{[^,]*,", lambda mm: "@" + mm.group(1) + "{" + key + ",", b.strip(), count=1))
            else:
                items = cr_search(q)
                for rank, m in enumerate(items[:3]):
                    d = summarize(m); d.update(key=key, status=f"SEARCH_HIT_{rank+1}", query=q)
                    rows.append(d)
            time.sleep(0.3)
        except Exception as e:  # noqa
            rows.append({"key": key, "status": "ERROR " + str(e)[:100]})
    for key, aid in ARXIV.items():
        try:
            d = arxiv(aid); d.update(key=key, status="OK_ARXIV"); rows.append(d)
        except Exception as e:  # noqa
            rows.append({"key": key, "status": "ERROR " + str(e)[:100]})
        time.sleep(3)
    cols = ["key", "status", "doi", "type", "title", "authors", "year", "container", "volume", "issue", "page",
            "publisher", "query"]
    with open(OUT / "refs_verified.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    (OUT / "refs_crossref.bib").write_text("\n\n".join(bibs) + "\n")
    print("rows", len(rows), "bib entries", len(bibs))


if __name__ == "__main__":
    main()
