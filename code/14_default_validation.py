"""
14_default_validation.py   (no network; run after 12_default_panel.py)
Validation of the estimated Apple default schedule.

Question.  12_default_panel.py reads Apple's default price schedule off a panel of 30 small-developer subscription apps.  Is that
schedule a property of Apple's price tiers or of the apps that happen to be in the panel, how well is it determined in the
lower-income storefronts, and how often do the frontier AI plans sit exactly on one of its price points?  Every statistic below is
recomputed from the panel items with the functions of wave2_common.py (panel_points, schedule, ols_hc1), that is, with the
definitions of 12_default_panel.py: a ladder entry (storefront, US price point) is the modal local price over the panel items at
that point if there are >= 3 such items, the mode is unique and its share is >= 1/2 (rule "none", MAIN); the multiplier of a
storefront is the median over price points >= US$2.99 with a mode of (modal local price / US price), from >= 3 points; tax factor =
multiplier / fx (fx of wave2_default_multiplier.csv); the income slope of the schedule is the HC1 OLS slope of ln(tax factor) on
ln(GNI per capita).

Inputs   data/processed/wave2_default_items_long.csv, wave2_default_multiplier.csv, wave2_default_ladder.csv,
         wave2_plan_vs_default.csv (12_default_panel.py), country_panel.csv
Outputs  output/tables/W11_default_validation.csv    one row per statistic (the keys column gives the results_wave2.json keys)
         output/tables/W11b_weak_storefronts.csv     ladder and multiplier of six lower-income and six other emerging-market storefronts
         output/results_wave2.json                   val_* scalars (the val_* keys of an earlier run that are not written again are removed)

Definitions.
  (a) Rebuild: the ladder and the multipliers recomputed from the items equal wave2_default_ladder.csv and wave2_default_multiplier.csv
      (storefronts; largest |ln(rebuilt / file)| of a multiplier; ladder entries that differ).  Both files are read without loss of
      precision, so identical computations give a difference of exactly 0.
  (b) Income slope of the schedule.  The regression sample of every variant is the set of storefronts of the main schedule (the 164
      of the multiplier file, whose fx defines the tax factor) that have a multiplier in that variant and income data; Nigeria,
      which obtains a multiplier only when an app is left out or in some halves of the panel, therefore never enters.  Main rule:
      slope, HC1 s.e. and N of the package.  Strict-majority rule: a price needs a share > 1/2 (RULES["strict"]).
  (c) Subscription-only schedule: the same construction on the items of type subscription; consumables-only: on the items of type
      consumable, reported as a slope only if at least 20 storefronts have a multiplier (none does).  Where a storefront has both,
      the median of |ln(subscription multiplier / consumable multiplier)| and the shares within 3% and 10%.
  (d) Leave one app out: the schedule and the slope recomputed without each of the 29 apps that have priced items (storefront !=
      us, US price of the same item); range of the slopes, smallest N, and the largest absolute change of a storefront's multiplier
      (|ln(multiplier without the app / multiplier with all apps)|) over apps and storefronts.
  (e) Split half: 300 random splits of the 29 apps into 14 and 15 apps (Python's random.Random(20261016).shuffle of the sorted list
      of app keys; the first 14 form half A), the schedule of each half, and on the storefronts with a multiplier in both halves
      (at least 20; every split has): the median of |ln(multiplier A / multiplier B)| and the shares within 3% and 10%.  Reported:
      the median over the splits of each of these, the median number of common storefronts, and the 5th and 95th percentile
      (the value at position int(p (n - 1)) of the sorted list, no interpolation) of the 600 half-sample slopes.
  (f) Exact coincidence: of the plan x storefront rows of wave2_plan_vs_default.csv with a deviation and an exact ladder reference
      (default_exact) for the 12 frontier plans (ChatGPT Plus, Pro 100, Pro 200; Claude Pro, Max 5x, Max 20x; Gemini Pro, Ultra;
      Perplexity Pro; SuperGrok, SuperGrok Heavy; Microsoft 365 Premium), the share listed at the modal price of the panel to the
      cent (|dev| <= 0.005).  Overall, for each plan with such rows, and in the "anomalous" storefronts where the schedule departs
      from FX parity by more than 20% (|ln(tax factor)| > ln 1.2, main schedule), which are the storefronts whose schedule embeds
      a tax or a mark-up.
  (g) Weak storefronts: for India, Brazil, Egypt, Uganda, Nigeria and Turkiye (the lower-income and large markets named in the
      review) and Indonesia, Pakistan, the Philippines, Viet Nam, Mexico and South Africa: ladder entries (>= 3 items at a price
      point), entries with a unique mode of share >= 1/2, median modal share over the entries, multiplier and spread (empty where
      the storefront has no multiplier), and the frontier plans with an exact ladder point.  Ladder summary: entries, entries with
      a mode, median modal share and the share of entries whose modal share is >= 0.75 (over all entries, with or without a mode).
"""
import os
for _v in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ[_v] = "1"                                   # fixed order of summation: the output is byte-identical between runs
import json, math, pathlib, random
import numpy as np
import pandas as pd
from wave2_common import NAN, MAIN, ols_hc1, panel_points, schedule

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROC, TAB = ROOT / "data" / "processed", ROOT / "output" / "tables"
SEED, N_SPLITS = 20261016, 300
FRONT = ["chatgpt_plus", "chatgpt_pro100", "chatgpt_pro200", "claude_pro", "claude_max5x", "claude_max20x", "gemini_pro",
         "gemini_ultra", "perplexity_pro", "supergrok", "supergrok_heavy", "m365_premium"]
WEAK = [("in", 1), ("br", 1), ("eg", 1), ("ug", 1), ("ng", 1), ("tr", 1),          # (storefront, block of W11b)
        ("id", 2), ("pk", 2), ("ph", 2), ("vn", 2), ("mx", 2), ("za", 2)]
R, ROWS = {}, []


def read(path, **kw):
    return pd.read_csv(path, keep_default_na=False, na_values=[""], **kw)


def py(v):
    """Python scalar of a numpy scalar (None and NaN stay as they are)."""
    return v.item() if isinstance(v, np.generic) else v


def put(stat, description, note="", **cells):
    """Add the W11 row `stat` and the val_* keys.  cells: column (value, se, n, numerator, denominator) -> (key suffix, number)."""
    row = dict(statistic=stat, description=description, value=NAN, se=NAN, n=NAN, numerator=NAN, denominator=NAN, note=note)
    keys = []
    for col, (suffix, x) in cells.items():
        x = py(x)
        row[col] = x
        if x is not None and x == x:
            R[f"val_{suffix}"] = x
            keys.append(f"{col}={'val_' + suffix}")
    row["keys"] = ";".join(keys)
    ROWS.append(row)


def lower_quantile(v, p):
    """Value at position int(p (n - 1)) of the sorted list (no interpolation)."""
    return sorted(v)[int(p * (len(v) - 1))]


# ================================================================================================ data and the main schedule
items = read(PROC / "wave2_default_items_long.csv")
mfile = read(PROC / "wave2_default_multiplier.csv", float_precision="round_trip").set_index("storefront")
lfile = read(PROC / "wave2_default_ladder.csv", float_precision="round_trip")
pvd = read(PROC / "wave2_plan_vs_default.csv")
panel = read(PROC / "country_panel.csv")[["iso2", "country_wb", "income_group", "gni_atlas"]].copy()
panel["sf"] = panel.iso2.str.lower()
GNI, NAME, GROUP = dict(zip(panel.sf, panel.gni_atlas)), dict(zip(panel.sf, panel.country_wb)), dict(zip(panel.sf, panel.income_group))
FX = {s: float(v) for s, v in mfile.fx.items() if v == v}

d = panel_points(items)
SLIM = d[["storefront", "us_pt", "loc_r"]]                 # the only columns that schedule() uses (a narrower frame is much faster)


def sched(mask=None, rule=MAIN):
    """schedule() of the panel items selected by the boolean Series `mask` (all items if None)."""
    return schedule(SLIM if mask is None else SLIM[mask.values], rule)


lad, mult = sched()
apps = sorted(d.app.unique())


def slope(m):
    """(slope, HC1 s.e., N) of ln(tax factor) on ln(GNI): storefronts of the main schedule (those with an fx in the multiplier file)
    that have a multiplier in `m` and income data."""
    sf = [s for s in m if s in FX and GNI.get(s, NAN) > 0]
    return ols_hc1(np.log([GNI[s] for s in sf]), np.log([m[s][0] / FX[s] for s in sf]))


# ================================================================================================ (a) rebuild
assert set(mult) == set(mfile.index), "storefronts with a multiplier differ from wave2_default_multiplier.csv"
rebuild = max(abs(math.log(mult[s][0] / mfile.multiplier[s])) for s in mult)
assert rebuild < 1e-9, f"multipliers rebuilt from the items differ from the file by {rebuild}"
lf = lfile.set_index(["storefront", "us_price"])
n_diff = len(set(lf.index) ^ set(lad))
for key, e in lad.items():
    if key in lf.index:
        r = lf.loc[key]
        same = (e["n_items"] == r.n_items and e["tie"] == r.tie and e["modal_share"] == r.modal_share and
                (e["modal_local"] is None and r.modal_local != r.modal_local or e["modal_local"] == r.modal_local))
        n_diff += not same
assert n_diff == 0, f"{n_diff} ladder entries rebuilt from the items differ from wave2_default_ladder.csv"
put("rebuild", "Multipliers rebuilt from the panel items against wave2_default_multiplier.csv: storefronts; largest |ln(rebuilt / file)|",
    value=("rebuild_max_logdiff", rebuild), n=("rebuild_n", len(mult)))
put("rebuild_ladder", "Ladder entries rebuilt from the panel items against wave2_default_ladder.csv: entries; entries that differ",
    value=("rebuild_ladder_diff", n_diff), n=("rebuild_ladder_n", len(lad)))

# ================================================================================================ (b) slope: main and strict rule
b, se, n = slope(mult)
put("slope_main", "Income slope of ln(tax factor), main rule (unique mode, share >= 1/2)", value=("slope_main", b), se=("slope_main_se", se),
    n=("slope_main_n", n))
mult_strict = sched(rule="strict")[1]
bs, ses, ns = slope(mult_strict)
put("slope_strict", "Income slope, strict majority (share > 1/2)", value=("slope_strict", bs), se=("slope_strict_se", ses),
    n=("slope_strict_n", ns))
put("multipliers_strict", "Storefronts with a multiplier under the strict-majority rule", n=("strict_multipliers", len(mult_strict)))

# ================================================================================================ (c) subscriptions and consumables
m_sub = sched(d.type == "subscription")[1]
m_con = sched(d.type == "consumable")[1]
bu, seu, nu = slope(m_sub)
put("slope_sub", "Income slope, schedule from the items of type subscription only", value=("slope_sub", bu), se=("slope_sub_se", seu),
    n=("slope_sub_n", nu))
put("multipliers_sub", "Storefronts with a multiplier from subscription items only", n=("sub_multipliers", len(m_sub)))
put("multipliers_cons", "Storefronts with a multiplier from consumable items only (the slope needs >= 20)",
    n=("cons_multipliers", len(m_con)))
if len(m_con) >= 20:
    bc, sec, nc = slope(m_con)
    put("slope_cons", "Income slope, schedule from the items of type consumable only", value=("slope_cons", bc), se=("slope_cons_se", sec),
        n=("slope_cons_n", nc))
both = [s for s in m_sub if s in m_con]
dd = np.array([math.log(m_sub[s][0] / m_con[s][0]) for s in both])
put("sub_vs_cons", "Storefronts with a multiplier from both: median |ln(subscription / consumable)|",
    value=("subcons_med_abs_logdiff", float(np.median(np.abs(dd))) if len(dd) else NAN), n=("subcons_n", len(both)))
if len(dd):
    put("sub_vs_cons_within3", "Storefronts with both: share of the multipliers within 3% of each other",
        value=("subcons_within3", float((np.abs(dd) <= 0.03).mean())))
    put("sub_vs_cons_within10", "Storefronts with both: share of the multipliers within 10% of each other",
        value=("subcons_within10", float((np.abs(dd) <= 0.10).mean())))

# ================================================================================================ (d) leave one app out
loo = []
for a in apps:
    m = sched(d.app != a)[1]
    b1, s1, n1 = slope(m)
    shifts = {s: abs(math.log(m[s][0] / mult[s][0])) for s in m if s in mult}
    worst = max(shifts, key=lambda s: (shifts[s], s))
    loo.append(dict(app=a, slope=b1, n=n1, max_shift=shifts[worst], worst_storefront=worst, shifts=shifts))
by_sf = {}
for r in loo:
    for s, v in r["shifts"].items():
        by_sf[s] = max(by_sf.get(s, 0.0), v)
top = max(loo, key=lambda r: (r["max_shift"], r["app"]))
put("loo_slope_min", f"Leave one app out ({len(apps)} refits): smallest income slope", value=("loo_slope_min", min(r["slope"] for r in loo)),
    note=f"without {min(loo, key=lambda r: r['slope'])['app']}")
put("loo_slope_max", "Leave one app out: largest income slope", value=("loo_slope_max", max(r["slope"] for r in loo)),
    note=f"without {max(loo, key=lambda r: r['slope'])['app']}")
put("loo_n_min", "Leave one app out: smallest N of the slope", value=("loo_n_min", min(r["n"] for r in loo)))
put("loo_max_shift", "Leave one app out: largest |ln(multiplier without the app / multiplier with all apps)| of a storefront",
    value=("loo_max_shift", top["max_shift"]), note=f"storefront {top['worst_storefront']}, without {top['app']}")
mx = np.array(list(by_sf.values()))
put("loo_median_storefront_max", "Leave one app out: median over storefronts of the largest change of the multiplier over the apps",
    value=("loo_median_storefront_max", float(np.median(mx))), n=("loo_storefronts", len(mx)))
put("loo_p90_storefront_max", "Leave one app out: 90th percentile over storefronts of the largest change of the multiplier over the apps",
    value=("loo_p90_storefront_max", lower_quantile(list(mx), 0.90)))
put("loo_share_within3", "Leave one app out: share of storefronts whose multiplier never changes by more than 3%",
    value=("loo_share_within3", float((mx <= 0.03).mean())), numerator=("loo_within3", int((mx <= 0.03).sum())),
    denominator=("loo_storefronts", len(mx)))
put("loo_apps", "Apps left out one at a time (apps with priced items)", n=("loo_apps", len(apps)))

# ================================================================================================ (e) split half
rnd = random.Random(SEED)
splits = []
for _ in range(N_SPLITS):
    order = apps[:]
    rnd.shuffle(order)
    half = set(order[:len(order) // 2])
    mA, mB = sched(d.app.isin(half))[1], sched(~d.app.isin(half))[1]
    com = [s for s in mA if s in mB]
    if len(com) < 20:
        continue
    diff = np.array([math.log(mA[s][0] / mB[s][0]) for s in com])
    splits.append(dict(n=len(com), med_abs=float(np.median(np.abs(diff))), within3=float((np.abs(diff) <= 0.03).mean()),
                       within10=float((np.abs(diff) <= 0.10).mean()), bA=slope(mA)[0], bB=slope(mB)[0]))
half_slopes = [r["bA"] for r in splits] + [r["bB"] for r in splits]
put("split_reps", "Split half: random splits of the apps kept (>= 20 storefronts with a multiplier in both halves)", n=("split_reps", len(splits)))
put("split_n_common_median", "Split half: median number of storefronts with a multiplier in both halves",
    value=("split_n_common_median", float(np.median([r["n"] for r in splits]))))
put("split_med_abs_logdiff", "Split half: median over splits of the median |ln(multiplier A / multiplier B)|",
    value=("split_med_abs_logdiff", float(np.median([r["med_abs"] for r in splits]))))
put("split_within3", "Split half: median over splits of the share of common storefronts within 3%",
    value=("split_within3", float(np.median([r["within3"] for r in splits]))))
put("split_within10", "Split half: median over splits of the share of common storefronts within 10%",
    value=("split_within10", float(np.median([r["within10"] for r in splits]))))
put("split_slope_p05", "Split half: 5th percentile of the 600 half-sample income slopes", value=("split_slope_p05", lower_quantile(half_slopes, 0.05)))
put("split_slope_p95", "Split half: 95th percentile of the 600 half-sample income slopes", value=("split_slope_p95", lower_quantile(half_slopes, 0.95)))

# ================================================================================================ (f) exact coincidence
ex = pvd[pvd.plan.isin(FRONT) & pvd.default_exact & pvd.dev_log.notna()].copy()
ex["at_modal"] = ex.dev_log.abs() <= 0.005
put("coinc", "Frontier plan x storefront rows with an exact ladder point: rows listed at the modal price to the cent",
    value=("coinc_share", float(ex.at_modal.mean())), numerator=("coinc_exact", int(ex.at_modal.sum())), denominator=("coinc_rows", len(ex)))
for plan in FRONT:
    g = ex[ex.plan == plan]
    if len(g):
        put(f"coinc_{plan}", f"The same for {plan}", value=(f"coinc_{plan}_share", float(g.at_modal.mean())),
            numerator=(f"coinc_{plan}_exact", int(g.at_modal.sum())), denominator=(f"coinc_{plan}_rows", len(g)))
anom = sorted(s for s, (m, k, sp) in mult.items() if s in FX and abs(math.log(m / FX[s])) > math.log(1.20))
ga = ex[ex.storefront.isin(anom)]
put("coinc_anom", "The same in the storefronts where the schedule departs from FX parity by more than 20%",
    value=("coinc_anom_share", float(ga.at_modal.mean()) if len(ga) else NAN), numerator=("coinc_anom_exact", int(ga.at_modal.sum())),
    denominator=("coinc_anom_rows", len(ga)), note=" ".join(anom))
put("coinc_anom_storefronts", "Storefronts where the schedule departs from FX parity by more than 20%", n=("coinc_anom_storefronts", len(anom)))

# ================================================================================================ (g) ladder strength and weak storefronts
L = pd.DataFrame([dict(storefront=sf, us_price=p, **e) for (sf, p), e in lad.items()])
L["has_mode"] = L.modal_local.notna()
put("ladder_entries", "Ladder entries (storefront x US price point with >= 3 panel items)", n=("ladder_entries", len(L)))
put("ladder_with_mode", "Ladder entries with a unique mode of share >= 1/2", value=("ladder_with_mode_share", float(L.has_mode.mean())),
    numerator=("ladder_with_mode", int(L.has_mode.sum())), denominator=("ladder_entries", len(L)))
put("ladder_median_modal_share", "Median modal share over all ladder entries", value=("ladder_median_modal_share", float(L.modal_share.median())))
put("ladder_share_ge075", "Share of ladder entries with a modal share >= 0.75", value=("ladder_share_ge075", float((L.modal_share >= 0.75).mean())),
    numerator=("ladder_ge075", int((L.modal_share >= 0.75).sum())), denominator=("ladder_entries", len(L)))

weak = []
for sf, block in WEAK:
    g = L[L.storefront == sf]
    hit = ex[ex.storefront == sf]
    rec = dict(storefront=sf, country=NAME[sf], income_group=GROUP[sf], block=block, points=len(g), with_mode=int(g.has_mode.sum()),
               median_modal_share=float(g.modal_share.median()), multiplier=mult[sf][0] if sf in mult else NAN,
               spread=mult[sf][2] if sf in mult else NAN, frontier_exact_points=len(hit), frontier_exact_plans=";".join(sorted(hit.plan)),
               frontier_exact="yes" if len(hit) else "no")
    weak.append(rec)
    for k in ("points", "with_mode", "median_modal_share", "multiplier", "spread", "frontier_exact_points"):
        if rec[k] == rec[k]:
            R[f"val_weak_{sf}_{k}"] = py(rec[k])
first6 = [r for r in weak if r["block"] == 1]
R["val_weak6_median_share_min"] = min(r["median_modal_share"] for r in first6)
R["val_weak6_median_share_max"] = max(r["median_modal_share"] for r in first6)
R["val_weak6_frontier_exact_points"] = sum(r["frontier_exact_points"] for r in first6)

# ================================================================================================ output
pd.DataFrame(ROWS, columns=["statistic", "description", "value", "se", "n", "numerator", "denominator", "note", "keys"]).round(10).to_csv(
    TAB / "W11_default_validation.csv", index=False)
pd.DataFrame(weak).round(10).to_csv(TAB / "W11b_weak_storefronts.csv", index=False)

res = json.load(open(ROOT / "output" / "results_wave2.json"))
for k in [k for k in res if k.startswith("val_") and k not in R]:
    del res[k]                                                             # stale keys of an earlier version
res.update({k: (round(v, 6) if isinstance(v, float) else v) for k, v in R.items()})
json.dump(res, open(ROOT / "output" / "results_wave2.json", "w"), indent=1)

print(f"rebuild: {len(mult)} multipliers, largest |ln difference| {rebuild:.1e}, {len(lad)} ladder entries, {n_diff} differ")
print(f"income slope of the schedule: main {b:.4f} ({se:.4f}) N = {n}; strict {bs:.4f} ({ses:.4f}) N = {ns}; "
      f"subscriptions only {bu:.4f} ({seu:.4f}) N = {nu}; storefronts with a consumables-only multiplier: {len(m_con)}")
print(f"leave one app out ({len(apps)}): slopes {min(r['slope'] for r in loo):.4f} to {max(r['slope'] for r in loo):.4f}, N >= "
      f"{min(r['n'] for r in loo)}, largest multiplier shift {top['max_shift']:.3f} ({top['worst_storefront']}, without {top['app']})")
print(f"split half ({len(splits)} splits): {np.median([r['n'] for r in splits]):.0f} common storefronts, median |ln diff| "
      f"{np.median([r['med_abs'] for r in splits]):.2e}, within 3% {np.median([r['within3'] for r in splits]):.3f}, within 10% "
      f"{np.median([r['within10'] for r in splits]):.3f}, half-sample slopes p05 {lower_quantile(half_slopes, .05):.4f} p95 {lower_quantile(half_slopes, .95):.4f}")
print(f"exact coincidence: {int(ex.at_modal.sum())} of {len(ex)}; "
      + "; ".join(f"{p} {int(ex[ex.plan == p].at_modal.sum())}/{(ex.plan == p).sum()}" for p in FRONT if (ex.plan == p).any())
      + f"; anomalous storefronts ({len(anom)}) {int(ga.at_modal.sum())}/{len(ga)}")
print(f"ladder: {len(L)} entries, {int(L.has_mode.sum())} with a mode, median modal share {L.modal_share.median():.3f}, share >= 0.75: "
      f"{(L.modal_share >= 0.75).mean():.3f}")
