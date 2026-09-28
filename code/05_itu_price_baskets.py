"""
05_itu_price_baskets.py
Tidy the ITU ICT Price Baskets workbook (Dec 2025 release, 2008-2025), downloaded 2026-09-27 from
https://www.itu.int/en/ITU-D/Statistics/Documents/ICT_Prices/ITU_ICTPriceBaskets_2008-2025.xlsx

Outputs (data/raw/itu/):
  itu_price_baskets_long.csv   all economies x basket codes x years with a value; status = official | experimental
                               (from the workbook's BasketHistory sheet: 'x' = data available, 'exp' = experimental)
  itu_affordability_latest.csv one row per economy: data-only mobile broadband 2 GB and fixed-broadband 5 GB
                               price as % of monthly GNI p.c. (2024 and 2025), plus the official 2025 data-only 5 GB basket,
                               and "latest available year" columns.
"""
import pathlib
import openpyxl
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
D = ROOT / "data" / "raw" / "itu"
XL = D / "ITU_ICTPriceBaskets_2008-2025.xlsx"

# ---- status map from BasketHistory ------------------------------------------------------------
ws = openpyxl.load_workbook(XL, read_only=True, data_only=True)["BasketHistory"]
rows = [r for r in ws.iter_rows(values_only=True)]
hdr = next(r for r in rows if r[1] == "Basket name (generic)")
years = [y for y in hdr[4:] if isinstance(y, int)]
status = {}
for r in rows:
    code = r[3]
    if isinstance(code, str) and code.endswith("*"):
        prefix = code.rstrip("*")
        for y, flag in zip(years, r[4:4 + len(years)]):
            if flag in ("x", "exp"):
                status[(prefix, y)] = "official" if flag == "x" else "experimental"

# ---- data --------------------------------------------------------------------------------------
d = pd.read_excel(XL, sheet_name="economies_2008-2025", keep_default_na=False, na_values=["NA", "n.a.", ""])
ycols = [c for c in d.columns if isinstance(c, int)]
long = d.melt(id_vars=["IsoCode", "Economy", "Code", "Basket name", "Unit", "ITURegion", "LDC", "LLDC", "SIDS", "Income_2025"],
              value_vars=ycols, var_name="year", value_name="value")
long["value"] = pd.to_numeric(long["value"], errors="coerce")
long = long.dropna(subset=["value"])


def prefix_of(code):
    for suf in ("_GNI", "_PPP", "$"):
        if code.endswith(suf):
            return code[: -len(suf)]
    return code


long["status"] = [status.get((prefix_of(c), y), "year outside BasketHistory range") for c, y in zip(long.Code, long.year)]
long["unit_label"] = long.Unit.map({"GNIpc": "% of monthly GNI per capita", "USD": "USD per month",
                                    "PPP": "PPP$ per month"})
long = long.rename(columns={"IsoCode": "iso3", "Economy": "economy", "Code": "code", "Basket name": "basket_name",
                            "Unit": "unit", "ITURegion": "itu_region", "Income_2025": "wb_income_2025"})
long = long[["iso3", "economy", "code", "basket_name", "unit", "unit_label", "year", "value", "status", "itu_region",
             "wb_income_2025", "LDC", "LLDC", "SIDS"]].sort_values(["iso3", "code", "year"])
long.to_csv(D / "itu_price_baskets_long.csv", index=False)

# ---- wide affordability file -------------------------------------------------------------------
W = {("i271mb_2GB_GNI", 2024): "mbb_2gb_pct_gni_2024", ("i271mb_2GB_GNI", 2025): "mbb_2gb_pct_gni_2025_exp",
     ("i271mb_5GB_GNI", 2025): "mbb_5gb_pct_gni_2025", ("i154_FBB5_GNI", 2024): "fbb_5gb_pct_gni_2024",
     ("i154_FBB5_GNI", 2025): "fbb_5gb_pct_gni_2025",
     ("i271mb_2GB$", 2024): "mbb_2gb_usd_2024", ("i271mb_2GB$", 2025): "mbb_2gb_usd_2025_exp",
     ("i271mb_5GB$", 2025): "mbb_5gb_usd_2025", ("i154_FBB5$", 2024): "fbb_5gb_usd_2024", ("i154_FBB5$", 2025): "fbb_5gb_usd_2025",
     ("i271mb_2GB_PPP", 2024): "mbb_2gb_ppp_2024", ("i154_FBB5_PPP", 2024): "fbb_5gb_ppp_2024",
     ("i271mb_5GB_PPP", 2025): "mbb_5gb_ppp_2025", ("i154_FBB5_PPP", 2025): "fbb_5gb_ppp_2025"}
sel = long[[(c, y) in W for c, y in zip(long.code, long.year)]].copy()
sel["col"] = [W[(c, y)] for c, y in zip(sel.code, sel.year)]
wide = sel.pivot_table(index="iso3", columns="col", values="value").reset_index()
meta = d[["IsoCode", "Economy", "ITURegion", "Income_2025", "LDC", "LLDC", "SIDS"]].drop_duplicates("IsoCode") \
    .rename(columns={"IsoCode": "iso3", "Economy": "economy", "ITURegion": "itu_region", "Income_2025": "wb_income_2025"})
wide = meta.merge(wide, on="iso3", how="left")


def latest(row, code):
    """Latest OFFICIAL-basket value: 2 GB mobile official through 2024; fixed 5 GB official 2018-2025."""
    s = long[(long.iso3 == row.iso3) & (long.code == code) & (long.status == "official")]
    if s.empty:
        return pd.Series([None, None])
    r = s.sort_values("year").iloc[-1]
    return pd.Series([r.value, int(r.year)])


wide[["mbb_2gb_pct_gni_latest_official", "mbb_2gb_latest_year"]] = wide.apply(latest, axis=1, code="i271mb_2GB_GNI")
wide[["fbb_5gb_pct_gni_latest_official", "fbb_5gb_latest_year"]] = wide.apply(latest, axis=1, code="i154_FBB5_GNI")
order = ["iso3", "economy", "itu_region", "wb_income_2025", "LDC", "LLDC", "SIDS",
         "mbb_2gb_pct_gni_2024", "mbb_2gb_pct_gni_2025_exp", "mbb_5gb_pct_gni_2025", "fbb_5gb_pct_gni_2024",
         "fbb_5gb_pct_gni_2025", "mbb_2gb_pct_gni_latest_official", "mbb_2gb_latest_year",
         "fbb_5gb_pct_gni_latest_official", "fbb_5gb_latest_year"]
wide = wide[order + [c for c in wide.columns if c not in order]]
wide.to_csv(D / "itu_affordability_latest.csv", index=False)

print("long rows:", len(long), " economies:", long.iso3.nunique())
for c in ["mbb_2gb_pct_gni_2024", "mbb_2gb_pct_gni_2025_exp", "mbb_5gb_pct_gni_2025", "fbb_5gb_pct_gni_2024", "fbb_5gb_pct_gni_2025"]:
    print(f"{c:28s} n={wide[c].notna().sum():3d} median={wide[c].median():.2f}")
print(wide.groupby("wb_income_2025")[["mbb_2gb_pct_gni_2024", "fbb_5gb_pct_gni_2024", "mbb_5gb_pct_gni_2025",
                                      "fbb_5gb_pct_gni_2025"]].median().round(2).to_string())
