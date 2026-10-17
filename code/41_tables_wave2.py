"""
41_tables_wave2.py -- LaTeX table bodies (English; rows only, no header) for the second price wave (16 October 2026).

    python code/41_tables_wave2.py            write the bodies
    python code/41_tables_wave2.py --check    recompute and compare with the files on disk without writing; exit 1 on a difference

Reads output/tables/W1_wave2_plans.csv, W2_benchmarks.csv, W3_stability.csv, W5_item_classes.csv (09b_wave2_items.py,
12_default_panel.py), W11_default_validation.csv, W11b_weak_storefronts.csv (14_default_validation.py), W14_vintage.csv
(15_vintage_test.py), W15_cross_channel.csv, W15b_play_countries.csv (16_cross_channel.py), A1_burden_by_group.csv,
A2_burden_by_quintile.csv (20_analysis.py), extensions/audit_output/policy_counterfactuals_groups.csv (policy_counterfactuals.py;
shipped, identical on every run), data/processed/appstore_prices_long.csv (wave 1) and country_panel.csv, output/results.json
(tax-inclusive local burden of ChatGPT Plus in tab_afford) and output/results_wave2.json (deviation slopes of tab_benchmarks;
consistency check of the shared numbers).
Writes paper_en/tables/tab_wave2_plans.tex, tab_benchmarks.tex, tab_classes.tex, tab_stability.tex, tab_afford.tex,
tab_default_validation.tex, tab_weak_storefronts.tex, tab_vintage.tex, tab_cross_channel.tex and tab_play_countries.tex.

Columns (the header and the notes belong to the caller in main.tex).
  tab_wave2_plans        plan | U.S. price | N | USD slope (s.e.) | deviation slope (s.e.) | within 3% | below 10% | median LMIC deviation
                         (%) | exact reference (%) (share of the plan's storefronts whose reference is an exact ladder point,
                         n_exact / n); 17 plans, a thin space between the vendors
  tab_benchmarks         firm | product | group | U.S. price | N | slope (s.e.) | deviation slope (s.e.) (results_wave2.json <plan>_dev_slope,
                         <plan>_dev_se, of the plan's storefronts with a default reference, so on a smaller sample than N; "--" if
                         the plan has none) | median ratio in LMIC
  tab_afford             income group | N | $20, % of GNI p.c. | tax-inclusive local ChatGPT Plus, % of GNI p.c. (results.json
                         laab_chatgpt_plus_*) | $20 PPP | $20 consumption | poorest 20% | richest 20% | entry-tier local price | above
                         the 2% benchmark (%) | subsidy rate (%)
  tab_default_validation check | result (two columns of text)
  tab_weak_storefronts   storefront | ladder points | with a unique mode | median modal share | multiplier spread | frontier plan on an exact
                         ladder point (yes/no)
  tab_vintage            sample | N | slope on ln GNI (s.e.) | with FX-movement control (s.e.) | coefficient on FX movement (s.e.) | |dev| on
                         FX movement (s.e.) | median dev. | share within 3% (%): US$ / stable / moved ("--" for a class of fewer than
                         MIN_CLASS rows)
  tab_cross_channel      check | result (two columns of text)
  tab_play_countries     country | income group | currency | Google Play lowest item | US$ | App Store | log difference; ChatGPT (App Store
                         price of ChatGPT Go), then Claude (Claude Pro), richest country first

Conventions: minus signs are written $-$; the table notes (LMIC = low and lower-middle income; deviation = ln of local price over the
Apple default schedule; slopes with HC1 standard errors) belong to the caller in main.tex.
"""
import argparse, hashlib, json, math, pathlib, sys
import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
TAB, PROC = ROOT / "output" / "tables", ROOT / "data" / "processed"
OUT = ROOT / "paper_en" / "tables"
END = r" \\"
GROUPS = ["High income", "Upper-middle income", "Lower-middle income", "Low income"]
SHORT = {"High income": "HIC", "Upper-middle income": "UMIC", "Lower-middle income": "LMIC", "Low income": "LIC"}
# tab_wave2_plans: the AI plans by vendor, then the two Microsoft plans (W1 keys); a thin space follows each inner list
PLANS = [["chatgpt_go", "chatgpt_plus", "chatgpt_pro100", "chatgpt_pro200", "chatgpt_pro500"],
         ["claude_pro", "claude_max5x", "claude_max20x"],
         ["gemini_plus", "gemini_pro", "gemini_ultra"],
         ["perplexity_pro"],
         ["supergrok_lite", "supergrok", "supergrok_heavy"],
         ["m365_personal", "m365_premium"]]
# tab_benchmarks: the product groups of the stacked regression (13_relative_prices.py) and the items outside it (storage plans,
# the Google One app's listing of Google AI Plus, family variants, X's creator subscription)
BENCH_GROUP = {"frontier": "Frontier AI", "capped": "Capped AI", "smallai": "Small AI allowance", "noai": "No AI allowance",
               "family": "Family variant", "creator": "Creator product", "capped_one": "Capped AI (duplicate)",
               "storage": "Storage (no AI)"}
# tab_vintage: the ten frontier plans (15_vintage_test.py)
FRONT = ["chatgpt_plus", "chatgpt_pro200", "claude_pro", "claude_max20x", "gemini_pro", "gemini_ultra", "perplexity_pro", "supergrok",
         "supergrok_heavy", "m365_premium"]
MIN_CLASS = 10                                              # tab_vintage: a share is shown only for a class of at least this many rows
NO_DECIMALS = {"JPY", "KRW", "IDR", "VND", "COP", "CLP"}    # currencies whose store prices are whole numbers (tab_play_countries)
PLAY_APPS = ["ChatGPT", "Claude"]


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


def slope_se(b, se, d=3):
    return f"{num(b, d)} ({se:.{d}f})"


def pct(x):
    """Integer percent of a share."""
    return f"{100 * x:.0f}"


def pct1(x):
    """Percent of a share with one decimal."""
    return f"{100 * x:.1f}"


def signed_pct(x):
    """Integer percent with a sign; 0 stays 0."""
    v = round(x)
    return "0" if v == 0 else ("$-$" + str(-v) if v < 0 else "$+$" + str(v))


def zero(x):
    """0 for an exact zero, else scientific notation."""
    return "0" if x == 0 else f"{x:.1e}"


def body(rows):
    return "\n".join(" & ".join(r) + END if not isinstance(r, str) else r for r in rows)


# ---------------------------------------------------------------------------------------------------------------------------------
# tab_default_validation / tab_weak_storefronts (14_default_validation.py)
# ---------------------------------------------------------------------------------------------------------------------------------
def default_validation():
    v = read(TAB / "W11_default_validation.csv").set_index("statistic")
    w1 = read(TAB / "W1_wave2_plans.csv").set_index("plan")
    f = lambda s, c="value": float(v.loc[s, c])
    i = lambda s, c="n": int(v.loc[s, c])
    frac = lambda s: f"{i(s, 'numerator'):,} of {i(s, 'denominator'):,} ({pct1(f(s))}\\%)"
    slope4 = lambda s: f"{slope_se(f(s), f(s, 'se'), 4)}; $N = {i(s)}$"
    assert "slope_cons" not in v.index, "a consumables-only slope exists: add a row to tab_default_validation"
    plans3 = ["coinc_chatgpt_plus", "coinc_gemini_pro", "coinc_m365_premium"]
    rows = [
        ["Multipliers and ladder rebuilt from the panel items",
         f"{i('rebuild')} multipliers, largest $|\\Delta\\ln|$ {zero(f('rebuild'))}; {i('rebuild_ladder'):,} ladder entries, "
         f"{int(f('rebuild_ladder'))} differ"],
        ["Income slope of the schedule, main rule (modal share $\\ge$ 1/2)", slope4("slope_main")],
        ["Strict majority rule (modal share $>$ 1/2)", slope4("slope_strict")],
        ["Items of type subscription only", slope4("slope_sub")],
        ["Items of type consumable only",
         f"{i('multipliers_cons')} storefronts with a multiplier (20 needed for a slope)"],
        ["Leave one app out (29 refits): income slope",
         f"{num(f('loo_slope_min'), 4)} to {num(f('loo_slope_max'), 4)}; $N \\ge {int(f('loo_n_min'))}$"],
        ["Leave one app out: largest change of a storefront's multiplier over the refits, $|\\Delta\\ln|$",
         f"median over storefronts {num(f('loo_median_storefront_max'), 3)}; 90th percentile {num(f('loo_p90_storefront_max'), 3)}; "
         f"maximum {num(f('loo_max_shift'), 3)}"],
        [f"Split half ({i('split_reps')} random splits of the apps): multipliers of the two halves",
         f"median $|\\Delta\\ln|$ {f('split_med_abs_logdiff'):.5f}; {pct1(f('split_within3'))}\\% within 3\\%; "
         f"{pct1(f('split_within10'))}\\% within 10\\%; {int(f('split_n_common_median'))} storefronts in common (median)"],
        ["Split half: income slope of the half samples",
         f"{num(f('split_slope_p05'), 3)} to {num(f('split_slope_p95'), 3)} (5th to 95th percentile)"],
        ["Frontier plans on an exact ladder point: listed at the panel's modal price", frac("coinc")],
        ["\\quad " + "; ".join(w1.loc[s[len("coinc_"):], "label"] for s in plans3),
         "; ".join(f"{i(s, 'numerator')} of {i(s, 'denominator')}" for s in plans3)],
        [f"\\quad in the {i('coinc_anom_storefronts')} storefronts where the schedule departs from FX parity by more than 20\\%",
         frac("coinc_anom")],
        ["Ladder entries with a unique mode (modal share $\\ge$ 1/2)",
         f"{i('ladder_with_mode', 'numerator'):,} of {i('ladder_entries'):,} ({pct1(f('ladder_with_mode'))}\\%); median modal share "
         f"{f('ladder_median_modal_share'):.3f}; {pct1(f('ladder_share_ge075'))}\\% of entries have a share $\\ge$ 0.75"],
    ]
    return body(rows)


def weak_storefronts():
    w = read(TAB / "W11b_weak_storefronts.csv")
    rows, block = [], None
    for r in w.itertuples():
        if block is not None and r.block != block:
            rows.append(r"\addlinespace")
        block = r.block
        rows.append([r.country, str(int(r.points)), str(int(r.with_mode)), f"{r.median_modal_share:.2f}",
                     "--" if pd.isna(r.spread) else f"{r.spread:.2f}", r.frontier_exact])
    return body(rows)


# ---------------------------------------------------------------------------------------------------------------------------------
# tab_vintage (15_vintage_test.py)
# ---------------------------------------------------------------------------------------------------------------------------------
def vintage():
    w = read(TAB / "W14_vintage.csv").set_index("group")
    w1 = read(TAB / "W1_wave2_plans.csv").set_index("plan")
    rows = []
    for g in ["frontier", "go"] + FRONT:
        r = w.loc[g]
        label = "Frontier plans, pooled" if g == "frontier" else w1.loc["chatgpt_go" if g == "go" else g, "label"]
        shares = [(r.within3_usd, r.n_usd), (r.within3_stable, r.n_stable), (r.within3_moved, r.n_moved)]
        rows.append([label, f"{int(r.n):,}", slope_se(r.slope, r.se, 4), slope_se(r.slope_ctrl, r.se_ctrl, 4),
                     slope_se(r.coef_fx, r.se_fx), slope_se(r.absdev_fx, r.absdev_fx_se), num(r.median_dev, 3),
                     " / ".join(pct(s) if n >= MIN_CLASS else "--" for s, n in shares)])
        if g == "go":
            rows.append(r"\addlinespace")
    return body(rows)


# ---------------------------------------------------------------------------------------------------------------------------------
# tab_cross_channel / tab_play_countries (16_cross_channel.py)
# ---------------------------------------------------------------------------------------------------------------------------------
def cross_channel(panel):
    w = read(TAB / "W15_cross_channel.csv").set_index("statistic")
    b = read(TAB / "W15b_play_countries.csv")
    f = lambda s, c="value": float(w.loc[s, c])
    i = lambda s, c="n": int(w.loc[s, c])
    name = dict(zip(panel.iso2.str.lower(), panel.country_wb))
    lmic = ", ".join(name[c] for c in w.loc["ms_lmic", "note"].split())
    us = {a: float(b[(b.app == a) & (b.country == "us")].play_min.iloc[0]) for a in PLAY_APPS}

    def web(key, product):
        s = f"ms_web_vs_app_{key}"
        return [f"Web store against App Store, {product}, same currency",
                f"{i(s + '_median')} comparisons; median log difference {num(f(s + '_median'), 3)}; "
                f"{pct(f(s + '_within5'))}\\% within 5\\%; identical to the cent in {int(w.loc[s + '_exact', 'numerator'])}, "
                f"within 0.5\\% in {int(w.loc[s + '_within05', 'numerator'])}; widest gap {num(f(s + '_maxgap'), 1)}\\% "
                f"({name[w.loc[s + '_maxgap', 'note']]})"]

    def play(key, app, plan):
        s = f"play_{key}"
        return [f"Google Play lowest in-app item against the App Store price of {plan} (US minimum \\${us[app]:.2f})",
                f"{i(s + '_median')} of {i(s + '_n')} countries comparable; median log difference {num(f(s + '_median'), 3)}; "
                f"{pct(f(s + '_within5'))}\\% within 5\\%"]

    rows = [
        ["Microsoft 365 web store: income slope of the Personal / Premium price ratio relative to the U.S.",
         f"{slope_se(f('ms_slope'), f('ms_slope', 'se'))}; $N = {i('ms_slope')}$"],
        ["\\quad median of the same ratio, low and lower-middle income countries",
         f"{num(f('ms_lmic'), 0)}\\% ($N = {i('ms_lmic')}$: {lmic})"],
        ["\\quad median of the same ratio, high-income countries", f"{num(f('ms_hic'), 0)}\\% ($N = {i('ms_hic')}$)"],
        web("premium", "Microsoft 365 Premium"),
        web("personal", "Microsoft 365 Personal"),
        play("chatgpt", "ChatGPT", "ChatGPT Go"),
        play("claude", "Claude", "Claude Pro"),
        ["ChatGPT on Google Play: lowest in-app item in low and lower-middle income countries, US\\$ price relative to the U.S. (median)",
         f"{f('play_chatgpt_lmic_ratio'):.2f} ($N = {i('play_chatgpt_lmic_ratio')}$)"],
        ["Claude on Google Play: the same",
         f"{f('play_claude_lmic_ratio'):.2f} ($N = {i('play_claude_lmic_ratio')}$)"],
        ["Gemini on Google Play",
         f"no in-app price range shown in any of the {i('play_gemini', 'denominator')} countries"],
    ]
    return body(rows), play_countries(b)


def play_countries(b):
    def price(x, cur):
        return f"{x:,.0f}" if cur in NO_DECIMALS else f"{x:,.2f}"

    rows = []
    for app in PLAY_APPS:
        if rows:
            rows.append(r"\addlinespace")
        for r in b[b.app == app].itertuples():
            if not r.app_store_storefront:
                store = "no store"
            elif r.app_store_currency == r.currency:
                store = price(r.app_store_price, r.currency)
            else:
                store = f"US\\${r.app_store_price:,.2f}" if r.app_store_currency == "USD" else \
                    f"{price(r.app_store_price, r.app_store_currency)} {r.app_store_currency}"
            rows.append([r.country_name, r.income_group, r.currency, price(r.play_min, r.currency), f"{r.usd_at_fx:,.2f}", store,
                         num(r.log_diff, 3) if r.compared else "--"])
    return body(rows)


def construct():
    t = {}
    w1 = read(TAB / "W1_wave2_plans.csv").set_index("plan")
    R1 = json.load(open(ROOT / "output" / "results.json"))
    R2 = json.load(open(ROOT / "output" / "results_wave2.json"))
    # ------------------------------------------------------------------ plans against the Apple default schedule
    rows = []
    for k, plans in enumerate(PLANS):
        if k:
            rows.append(r"\addlinespace")
        for p in plans:
            r = w1.loc[p]
            rows.append([r.label, f"{r.us_price:,.2f}", str(int(r.n)), slope_se(r.usd_slope, r.usd_se),
                         slope_se(r.dev_slope, r.dev_se), pct(r.within3), pct(r.below10), signed_pct(r.med_lmic_pct),
                         pct(r.n_exact / r.n)])
    t["tab_wave2_plans.tex"] = body(rows)
    # ------------------------------------------------------------------ within-firm benchmarks
    w2 = read(TAB / "W2_benchmarks.csv")
    rows, firm = [], None
    for r in w2.itertuples():
        if firm is not None and r.firm != firm:
            rows.append(r"\addlinespace")
        if f"{r.key}_dev_slope" in R2:
            dev = slope_se(R2[f"{r.key}_dev_slope"], R2[f"{r.key}_dev_se"])
        else:
            dev = "--"
            print(f"WARNING: no deviation slope for {r.key} in results_wave2.json", file=sys.stderr)
        rows.append([r.firm if r.firm != firm else "", r.product, BENCH_GROUP[r.group], f"{r.us_price:,.2f}", str(int(r.n)),
                     slope_se(r.slope, r.se), dev, f"{r.median_ratio_lmic:.2f}"])
        firm = r.firm
    t["tab_benchmarks.tex"] = body(rows)
    # ------------------------------------------------------------------ slopes by class of app
    w5 = read(TAB / "W5_item_classes.csv").set_index(["item_class", "type"])
    rows = []
    for label, key in [("Non-AI subscriptions", ("nonai", "subscription")),
                       ("AI-feature apps' subscriptions", ("ai_feature", "subscription")),
                       ("AI subscriptions", ("ai_all", "subscription")),
                       ("AI consumables (credits)", ("ai_all", "consumable"))]:
        r = w5.loc[key]
        rows.append([label, str(int(r.n)), num(r["median"], 3), f"{num(r.p25, 3)}--{num(r.p75, 3)}", pct(r.share_gt_010)])
    t["tab_classes.tex"] = body(rows)
    # ------------------------------------------------------------------ stability of wave-1 prices
    w3 = read(TAB / "W3_stability.csv")
    rows = []
    for r in w3.itertuples():
        share = "100" if r.identical == r.compared else f"{100 * r.share_identical:.1f}"
        rows.append([r.label, str(int(r.compared)), str(int(r.identical)), share])
    t["tab_stability.tex"] = body(rows)
    # ------------------------------------------------------------------ consolidated affordability
    A1, A2 = read(TAB / "A1_burden_by_group.csv").set_index("group"), read(TAB / "A2_burden_by_quintile.csv").set_index("group")
    pol = read(ROOT / "extensions" / "audit_output" / "policy_counterfactuals_groups.csv").set_index("group")
    panel = read(PROC / "country_panel.csv")
    panel["storefront"] = panel.iso2.str.lower()
    go = read(PROC / "appstore_prices_long.csv")
    go = go[go.plan == "chatgpt_go"][["storefront", "price_usd"]].merge(panel[["storefront", "gni_atlas", "income_group"]], on="storefront")
    go = go[go.gni_atlas.gt(0)]
    go["burden"] = 1200 * go.price_usd / go.gni_atlas
    rows = []
    for g in GROUPS:
        a, q = A1.loc[SHORT[g]], A2.loc[SHORT[g]]
        rows.append([g, str(int(a.n)), f"{a.aab_p20:.2f}", f"{R1['laab_chatgpt_plus_' + SHORT[g]]:.2f}", f"{a.aabppp_p20:.2f}",
                     f"{a.aabhh_p20:.2f}", f"{q.aab20_q1:.2f}", f"{q.aab20_q5:.2f}", f"{go[go.income_group == g].burden.median():.2f}",
                     pct(pol.loc[g, "above_uniform"] / 100), pct(pol.loc[g, "sub_rate"] / 100)])
    t["tab_afford.tex"] = body(rows)
    # ------------------------------------------------------------------ validation of the default schedule, vintage test, cross-channel check
    t["tab_default_validation.tex"] = default_validation()
    t["tab_weak_storefronts.tex"] = weak_storefronts()
    t["tab_vintage.tex"] = vintage()
    t["tab_cross_channel.tex"], t["tab_play_countries.tex"] = cross_channel(panel)
    return t


def consistency():
    """The shared numbers in the tables must equal the scalars in results_wave2.json (stale-input guard)."""
    R = json.load(open(ROOT / "output" / "results_wave2.json"))
    bad = []

    def same(key, value, source, required=False):
        if key not in R:
            if required:
                bad.append(f"{key}: missing in results_wave2.json ({source})")
        elif not math.isclose(R[key], float(value), abs_tol=1e-5, rel_tol=1e-5):
            bad.append(f"{key}: json {R[key]} vs {source} {value}")

    w1 = read(TAB / "W1_wave2_plans.csv").set_index("plan")
    for p, r in w1.iterrows():
        for k, col in [("n", "n"), ("usd_slope", "usd_slope"), ("dev_slope", "dev_slope"), ("within3", "within3"),
                       ("below10", "below10"), ("med_lmic_pct", "med_lmic_pct"), ("n_exact", "n_exact")]:
            same(f"{p}_{k}", r[col], "W1")
    w2 = read(TAB / "W2_benchmarks.csv")
    for r in w2.itertuples():
        for k, v in [("slope", r.slope), ("n", r.n), ("med_lmic_ratio", r.median_ratio_lmic)]:
            same(f"item_{r.key}_{k}", v, "W2")
    # W11 and W15 name the results_wave2.json key of each of their cells in the column `keys` ("value=val_slope_main;n=val_slope_main_n")
    for name in ("W11_default_validation.csv", "W15_cross_channel.csv"):
        for r in read(TAB / name).to_dict("records"):
            for pair in (r["keys"].split(";") if isinstance(r["keys"], str) else []):
                col, key = pair.split("=")
                same(key, r[col], name, required=True)
    for r in read(TAB / "W11b_weak_storefronts.csv").to_dict("records"):
        for col in ("points", "with_mode", "median_modal_share", "multiplier", "spread", "frontier_exact_points"):
            if r[col] == r[col]:
                same(f"val_weak_{r['storefront']}_{col}", r[col], "W11b", required=True)
    for r in read(TAB / "W14_vintage.csv").to_dict("records"):
        for col, v in r.items():
            if col not in ("group", "plans") and v == v:
                same(f"vint_{r['group']}_{col}", v, "W14", required=True)
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
