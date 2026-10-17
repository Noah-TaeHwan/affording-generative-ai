"""
42_tables_relative.py -- LaTeX table bodies (English; rows only, no header) for the annual-as-monthly guard, the default-free
relative-price analysis and the tax-absorption test of the second price wave.

    python code/42_tables_relative.py            write the bodies
    python code/42_tables_relative.py --check    recompute and compare with the files on disk without writing; exit 1 on a difference

Reads output/tables/W6_annual_guard.csv (09b_wave2_items.py), W13_tax_absorption.csv (12_default_panel.py), W8_relative_pairs.csv,
W9_relative_stacked.csv, W10_cross_vendor.csv, W12_increment.csv (13_relative_prices.py) and output/results_wave2.json (consistency
check of the shared numbers).
Writes paper_en/tables/tab_annual_guard.tex, tab_relative_pairs.tex, tab_relative_stacked.tex, tab_cross_vendor.tex,
tab_increment.tex, tab_tax_absorption.tex.

Columns (the header belongs to the caller in main.tex)
  tab_annual_guard.tex      Item | Class | N | Flagged | Slope before (s.e.) | Slope after (s.e.)     (items with >= 5 flagged cells)
  tab_relative_pairs.tex    Pair (A vs B) | N | Slope | (HC1) | [CR1] | RI p | LMIC median | Share < 0.9 (%) | Share at 1 (%)
                            firms separated by \\addlinespace; RI p = share of 2,000 permutations with |slope| at least as large
  tab_relative_stacked.tex  Group | Items | gamma (s.e.), all storefronts | gamma (s.e.), USD storefronts |
                            gamma (s.e.), local-currency storefronts | RI p       (exact randomisation inference)
  tab_cross_vendor.tex      Plan | US$ | N | Slope vs ChatGPT Plus (s.e.) | LMIC median (%) | Slope vs median frontier plan (s.e.) |
                            LMIC median (%) | Deviation slope (s.e.)      (N of both comparisons if they differ; firms separated)
  tab_increment.tex         Pair | N | Slope, relative to default increment (s.e.) | Median ratio: HIC / UMIC / LMIC / LIC | N |
                            Slope, USD relative to U.S. increment (s.e.)    (LMIC here = lower-middle income, LIC = low income)
  tab_tax_absorption.tex    Plan | N | At U.S. price | Within 3% of default | of which LMIC storefronts | at U.S. price in them

Conventions: minus signs are written $-$, a permutation p-value of zero as $<$0.0005 (none of the 2,000 permutations), the other
p-values with four decimals; percentages are plain numbers; the table notes belong to the caller.
"""
import argparse, hashlib, json, math, pathlib, re, sys
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
TAB = ROOT / "output" / "tables"
OUT = ROOT / "paper_en" / "tables"
END = r" \\"
CLASS = {"nonai": "Non-AI", "ai_core": "AI", "ai": "AI", "ai_bundle": "AI bundle", "ai_feature": "AI feature"}


def read(path):
    return pd.read_csv(path, keep_default_na=False, na_values=[""])


def num(x, d=2):
    """Fixed-point number with a LaTeX minus sign; a value that rounds to zero carries no sign."""
    s = f"{x:,.{d}f}"
    if s.startswith("-"):
        s = s[1:]
        if float(s.replace(",", "")) != 0:
            return "$-$" + s
    return s


def slope_se(b, se):
    return f"{num(b, 3)} ({se:.3f})"


def pct(x):
    """Integer percent of a share."""
    return f"{100 * x:.0f}"


def signed_pct(x):
    """Integer percent with a sign; 0 stays 0."""
    v = round(x)
    return "0" if v == 0 else ("$-$" + str(-v) if v < 0 else "$+$" + str(v))


def pval(p):
    """Permutation p-value: four decimals; zero (no permutation as extreme) as $<$0.0005."""
    return r"$<$0.0005" if p == 0 else f"{p:.4f}"


def body(rows):
    return "\n".join(" & ".join(r) + END if not isinstance(r, str) else r for r in rows)


def item_label(app, name):
    """Item as shown: the name, preceded by the app when the name does not contain it (100 GB -> Gemini 100 GB)."""
    return name if app in re.sub("[^a-z0-9]", "", name.lower()) else f"{app.title()} {name}"


def by_firm(rows, firms, make):
    """Rows made by `make(row)` for the records of `rows`, with \\addlinespace between firms."""
    out, last = [], None
    for r, f in zip(rows, firms):
        if last is not None and f != last:
            out.append(r"\addlinespace")
        out.append(make(r))
        last = f
    return out


def construct():
    t = {}
    # ------------------------------------------------------------------ annual-as-monthly guard
    w6 = read(TAB / "W6_annual_guard.csv")
    w6 = w6[w6.n_flagged >= 5]
    t["tab_annual_guard.tex"] = body([[item_label(r.app, r.item), CLASS[r.app_class], str(int(r.n)), str(int(r.n_flagged)),
                                       slope_se(r.slope_before, r.se_before), slope_se(r.slope_after, r.se_after)]
                                      for r in w6.itertuples()])
    # ------------------------------------------------------------------ the 12 within-vendor pairs
    w8 = read(TAB / "W8_relative_pairs.csv")
    t["tab_relative_pairs.tex"] = body(by_firm(
        list(w8.itertuples()), list(w8.firm),
        lambda r: [r.label, str(int(r.n)), num(r.slope, 3), f"({r.se_hc1:.3f})", f"[{r.se_cr1:.3f}]", pval(r.ri_p),
                   f"{r.lmic_med:.2f}", pct(r.share_below09), pct(r.mass_at1)]))
    # ------------------------------------------------------------------ stacked regression
    w9 = read(TAB / "W9_relative_stacked.csv")
    t["tab_relative_stacked.tex"] = body([[r.label, r.items, slope_se(r.gamma, r.se), slope_se(r.gamma_usd, r.se_usd),
                                           slope_se(r.gamma_lcu, r.se_lcu), pval(r.ri_p)] for r in w9.itertuples()])
    # ------------------------------------------------------------------ cross-vendor numeraires
    w10 = read(TAB / "W10_cross_vendor.csv")

    def cv(r):
        plus_ok = r.n_plus > 0
        n = str(int(r.n_front)) if (not plus_ok or r.n_plus == r.n_front) else f"{int(r.n_plus)}/{int(r.n_front)}"
        return [r.label, f"{r.us_price:,.2f}", n, slope_se(r.slope_plus, r.se_plus) if plus_ok else "--",
                signed_pct(r.lmic_pct_plus) if plus_ok else "--", slope_se(r.slope_front, r.se_front), signed_pct(r.lmic_pct_front),
                slope_se(r.dev_slope, r.dev_se)]
    t["tab_cross_vendor.tex"] = body(by_firm(list(w10.itertuples()), list(w10.firm), cv))
    # ------------------------------------------------------------------ increment test
    w12 = read(TAB / "W12_increment.csv")
    t["tab_increment.tex"] = body([[r.label, str(int(r.n)), slope_se(r.slope, r.se),
                                    f"{r.med_hic:.2f} / {r.med_umic:.2f} / {r.med_lmic:.2f} / {r.med_lic:.2f}",
                                    str(int(r.n_usd)), slope_se(r.slope_usd, r.se_usd)] for r in w12.itertuples()])
    # ------------------------------------------------------------------ tax absorption
    w13 = read(TAB / "W13_tax_absorption.csv")
    t["tab_tax_absorption.tex"] = body([[r.label, str(int(r.n)), str(int(r.at_us)), str(int(r.at_default)), str(int(r.n_lmic)),
                                         str(int(r.at_us_lmic))] for r in w13.itertuples()])
    return t


def consistency():
    """The shared numbers in the tables must equal the scalars in results_wave2.json (stale-input guard)."""
    R = json.load(open(ROOT / "output" / "results_wave2.json"))
    bad = []

    def chk(key, v):
        if isinstance(v, float) and v != v:
            if key in R:
                bad.append(f"{key}: json {R[key]} vs csv missing")
        elif key not in R or not math.isclose(R[key], float(v), abs_tol=1e-5, rel_tol=1e-5):
            bad.append(f"{key}: json {R.get(key)} vs csv {v}")

    for r in read(TAB / "W8_relative_pairs.csv").itertuples():
        for k, v in [("n", r.n), ("slope", r.slope), ("se_hc1", r.se_hc1), ("se_cr1", r.se_cr1), ("ri_p", r.ri_p),
                     ("lmic_med", r.lmic_med), ("share_below09", r.share_below09), ("mass_at1", r.mass_at1)]:
            chk(f"rel_{r.pair}_{k}", v)
    for r in read(TAB / "W9_relative_stacked.csv").itertuples():
        for k, v in [("gamma", r.gamma), ("se", r.se), ("ri_p", r.ri_p), ("gamma_usd", r.gamma_usd), ("se_usd", r.se_usd),
                     ("gamma_lcu", r.gamma_lcu), ("se_lcu", r.se_lcu)]:
            chk(f"stacked_{r.group}_{k}", v)
    for r in read(TAB / "W10_cross_vendor.csv").itertuples():
        for pre, cols in [("relplus", (r.slope_plus, r.se_plus, r.n_plus, r.lmic_pct_plus)),
                          ("relfront", (r.slope_front, r.se_front, r.n_front, r.lmic_pct_front))]:
            for k, v in zip(("slope", "se", "n", "lmic_pct"), cols):
                if k == "n" and v == 0:
                    continue                                    # ChatGPT Plus against itself
                chk(f"{pre}_{r.plan}_{k}", v)
    for r in read(TAB / "W12_increment.csv").itertuples():
        for k, v in [("slope", r.slope), ("se", r.se), ("n", r.n), ("med_hic", r.med_hic), ("med_umic", r.med_umic),
                     ("med_lmic", r.med_lmic), ("med_lic", r.med_lic)]:
            chk(f"incr_{r.pair}_{k}", v)
        for k, v in [("slope", r.slope_usd), ("se", r.se_usd), ("n", r.n_usd)]:
            chk(f"incrusd_{r.pair}_{k}", v)
    for r in read(TAB / "W13_tax_absorption.csv").itertuples():
        for k, v in [("n", r.n), ("at_us", r.at_us), ("at_default", r.at_default), ("n_lmic", r.n_lmic), ("at_us_lmic", r.at_us_lmic)]:
            chk(f"taxabs_{r.plan}_{k}", v)
    for r in read(TAB / "W6_annual_guard.csv").itertuples():
        if r.n_flagged >= 5:
            for k, v in [("n", r.n), ("n_flagged", r.n_flagged), ("slope_before", r.slope_before), ("slope_after", r.slope_after)]:
                chk(f"guard_{r.item_key}_{k}", v)
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="compare without writing; exit 1 on a difference")
    args = ap.parse_args()
    stale = consistency()
    for s in stale:
        print("INCONSISTENT", s, file=sys.stderr)
    tables = construct()
    OUT.mkdir(parents=True, exist_ok=True)
    ok = not stale
    for name, content in tables.items():
        path = OUT / name
        exp = content.encode("utf-8")
        same = path.exists() and path.read_bytes() == exp
        print(f"{'ok  ' if same else 'DIFF' if args.check else 'new '} {path.relative_to(ROOT)}  {hashlib.sha256(exp).hexdigest()[:12]}")
        if args.check:
            ok = ok and same
        else:
            path.write_bytes(exp)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
