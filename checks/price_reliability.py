"""Independent price-audit checks and matched-menu sensitivity.

This file never writes to the supplied manuscript, data, or shared scripts.
OLS, HC3, and currency-clustered CR1 covariance are computed directly with
NumPy, then compared with statsmodels as an implementation cross-check.
Provider/SKU uncertainty is not included in these standard errors.
"""
from pathlib import Path
import hashlib
import json
import sys
import collections
import re

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

HERE = Path(__file__).resolve().parent
SRC = HERE.parent
OUT = HERE / "results"
OUT.mkdir(exist_ok=True)
rd = lambda p: pd.read_csv(p, keep_default_na=False, na_values=[""])
d = rd(SRC / "data/processed/country_panel.csv")
p = rd(SRC / "data/processed/appstore_prices_long.csv")
cm = d[["iso3", "iso2", "gni_atlas", "gni_atlas_year", "income_group", "region"]].copy()
cm["storefront"] = cm.iso2.str.lower()
lp = p.merge(cm, on="storefront", how="inner").dropna(subset=["price_usd", "gni_atlas"])
lp = lp[(lp.gni_atlas > 0) & (lp.price_usd > 0)].copy()
lp["ln_gni"] = np.log(lp.gni_atlas)
lp["ln_p"] = np.log(lp.price_usd)


def direct_ols(x, y, groups=None):
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    X = np.column_stack([np.ones(len(x)), x])
    inv = np.linalg.inv(X.T @ X)
    beta = inv @ X.T @ y
    resid = y - X @ beta
    h = np.einsum("ij,jk,ik->i", X, inv, X)
    hc3_cov = inv @ (X.T @ (X * (resid / (1-h))[:, None] ** 2)) @ inv
    se_hc3 = np.sqrt(hc3_cov[1, 1])
    n = len(x)
    ans = dict(n=n, slope=float(beta[1]), se_HC3=float(se_hc3),
               hc3_ci_low=float(beta[1]-stats.norm.ppf(.975)*se_hc3),
               hc3_ci_high=float(beta[1]+stats.norm.ppf(.975)*se_hc3))
    if groups is not None:
        gcode, gnames = pd.factorize(np.asarray(groups))
        G = len(gnames)
        ans["currency_clusters"] = G
        if G > 1:
            score = np.zeros((G, 2))
            np.add.at(score, gcode, X * resid[:, None])
            cov = inv @ (score.T @ score) @ inv * G/(G-1) * (n-1)/(n-2)
            se = np.sqrt(cov[1, 1])
            cv = stats.t.ppf(.975, G-1)
            ans.update(se_currency_CR1=float(se), cluster_ci_low=float(beta[1]-cv*se),
                       cluster_ci_high=float(beta[1]+cv*se),
                       cluster_t_p=float(2*stats.t.sf(abs(beta[1]/se), G-1)))
    return ans


checks = []
baseline = json.loads((SRC / "extensions/baseline_results_v1.8.json").read_text())
for group, short in [("High income", "HIC"), ("Upper-middle income", "UMIC"),
                     ("Lower-middle income", "LMIC"), ("Low income", "LIC")]:
    key = f"aab_p20_{short}"
    v = float((24000/d.loc[d.income_group == group, "gni_atlas"]).median())
    checks.append(dict(key=key, computed=v, reported=baseline[key], pass_6dp=round(v, 6)==baseline[key]))
g = d[d.gni_atlas.notna()]
v = float(g.loc[24000/g.gni_atlas > 2, "pop1564"].sum()/g.pop1564.sum())
key = "share_wapop_aab20_gt2"
checks.append(dict(key=key, computed=v, reported=baseline[key], pass_6dp=round(v, 6)==baseline[key]))
ms = d[(d.ms_country_specific == 1) & d.gni_atlas.notna()].copy()
ms["ln_ms"] = np.log(ms.ms_q2_2026/100)
both = ms[ms.aui_may26.notna() & (ms.aui_may26 > 0)].copy()
both["ln_aui"] = np.log(both.aui_may26)
for prefix, a, y in [("ms_log_cs", ms, "ln_ms"), ("tm_ms", both, "ln_ms"), ("tm_aui", both, "ln_aui")]:
    fit = direct_ols(a.ln_gni, a[y])
    for k, suffix in [("slope", "b"), ("se_HC3", "se"), ("n", "n")]:
        key = f"{prefix}_{suffix}"
        checks.append(dict(key=key, computed=fit[k], reported=baseline[key], pass_6dp=round(fit[k], 6)==baseline[key]))
pd.DataFrame(checks).to_csv(OUT / "independent_headline_checks.csv", index=False)
assert all(z["pass_6dp"] for z in checks)

# The long extract has one row per storefront/plan; no arbitrary first-row choice.
assert not lp.duplicated(["iso3", "plan"]).any()
wide = lp.pivot(index="iso3", columns="plan", values="price_local")
wide = wide.join(lp.groupby("iso3").currency.first()).join(d.set_index("iso3")[["ln_gni", "income_group", "gni_atlas_year", "region"]])
currency_per_store = lp.groupby("iso3").currency.nunique()
assert (currency_per_store == 1).all()

ratio_frames = {}
for label, num, den in [("ChatGPT Go / Plus", "chatgpt_go", "chatgpt_plus"),
                         ("Google Plus / Pro", "gemini_plus", "gemini_pro")]:
    a = wide.dropna(subset=[num, den, "ln_gni"]).copy()
    a["log_ratio"] = np.log(a[num]/a[den])
    ratio_frames[label] = a

rows = []
a = ratio_frames["ChatGPT Go / Plus"]
for label, sub in [("All matched storefronts", a),
                    ("2025 GNI only", a[a.gni_atlas_year == 2025]),
                    ("USD only", a[a.currency == "USD"]),
                    ("EUR only", a[a.currency == "EUR"]),
                    ("Exclude USD", a[a.currency != "USD"]),
                    ("Exclude USD and EUR", a[~a.currency.isin(["USD", "EUR"])])]:
    fit = direct_ols(sub.ln_gni, sub.log_ratio, sub.currency)
    check = smf.ols("log_ratio ~ ln_gni", sub).fit(cov_type="HC3")
    assert abs(fit["slope"]-check.params.ln_gni) < 1e-12
    assert abs(fit["se_HC3"]-check.bse.ln_gni) < 1e-12
    if fit["currency_clusters"] > 1:
        check = smf.ols("log_ratio ~ ln_gni", sub).fit(cov_type="cluster", cov_kwds={"groups":sub.currency}, use_t=True)
        assert abs(fit["se_currency_CR1"]-check.bse.ln_gni) < 1e-12
    fit.update(specification=label, low_income_n=int((sub.income_group == "Low income").sum()))
    rows.append(fit)
pd.DataFrame(rows).to_csv(OUT / "matched_menu_currency_sensitivity.csv", index=False)

# Equivalent contrast: separate Go and Plus regressions must use this same sample.
go = lp[lp.plan == "chatgpt_go"].set_index("iso3").loc[a.index]
plus = lp[lp.plan == "chatgpt_plus"].set_index("iso3").loc[a.index]
contrast = direct_ols(a.ln_gni, np.log(go.price_usd/plus.price_usd), a.currency)
go_fit = direct_ols(go.ln_gni, go.ln_p)
plus_fit = direct_ols(plus.ln_gni, plus.ln_p)
assert abs(contrast["slope"]-(go_fit["slope"]-plus_fit["slope"])) < 1e-12
# Cancellation of exchange-rate conversion is checked numerically, not assumed.
assert np.max(np.abs(np.log(go.price_usd/plus.price_usd)-a.log_ratio)) < 1e-12

loo = []
for currency in sorted(a.currency.unique()):
    sub = a[a.currency != currency]
    fit = direct_ols(sub.ln_gni, sub.log_ratio)
    loo.append(dict(excluded_currency=currency, **fit))
pd.DataFrame(loo).to_csv(OUT / "leave_one_currency_out.csv", index=False)

# This estimate has 39 nominal currencies, but 37 singleton currencies provide
# no within-currency slope information. Only USD and EUR identify the slope.
counts = a.currency.value_counts()
identifying = a[a.currency.map(counts) > 1].copy()
identifying["within_x"] = identifying.ln_gni-identifying.groupby("currency").ln_gni.transform("mean")
identifying["within_y"] = identifying.log_ratio-identifying.groupby("currency").log_ratio.transform("mean")
fe_beta = float((identifying.within_x*identifying.within_y).sum()/(identifying.within_x**2).sum())
fe_ref = smf.ols("log_ratio ~ ln_gni + C(currency)", a).fit()
assert abs(fe_beta-fe_ref.params.ln_gni) < 1e-12

# Nonparametric currency-block resampling is a dependence diagnostic. Its
# percentile band is labelled a resampling range because dominated clusters
# weaken conventional cluster-asymptotic confidence-interval interpretation.
# Aggregation retains every country at equal weight within selected blocks.
agg = a.assign(xy=a.ln_gni*a.log_ratio, x2=a.ln_gni**2).groupby("currency").agg(
    n=("ln_gni","size"), sx=("ln_gni","sum"), sy=("log_ratio","sum"),
    sxy=("xy","sum"), sx2=("x2","sum"))
rng = np.random.default_rng(20260930)
B = 19999
weights = rng.multinomial(len(agg), np.repeat(1/len(agg), len(agg)), size=B)
tots = weights @ agg.to_numpy(float)
nb, sx, sy, sxy, sx2 = tots.T
boots = (sxy-sx*sy/nb)/(sx2-sx*sx/nb)
assert np.isfinite(boots).all()
np.savetxt(OUT / "currency_block_resample_slopes.csv", boots, delimiter=",", header="slope", comments="")

# Mapping sensitivity. A unique surviving candidate is not authenticated SKU
# metadata. The monthly filtering heuristic is unchanged, only its sensitivity
# and product-name ambiguity are audited here.
mapping_rows = []
for plan in ["chatgpt_go", "chatgpt_plus", "claude_pro", "gemini_plus", "gemini_pro"]:
    sub = lp[lp.plan == plan]
    for spec, sample, col in [("Published modal candidate", sub, "price_usd"),
                              ("Minimum surviving candidate", sub, "price_usd_min_candidate"),
                              ("Exclude multiple surviving price candidates", sub[sub.n_distinct_monthly == 1], "price_usd")]:
        fit = direct_ols(sample.ln_gni, np.log(sample[col]), sample.currency)
        mapping_rows.append(dict(plan=plan, specification=spec, excluded_n=len(sub)-len(sample), **fit))
pd.DataFrame(mapping_rows).to_csv(OUT / "monthly_candidate_sensitivity.csv", index=False)

# Name-level scope and annual-filter stability for ChatGPT.
raw = [json.loads(z) for z in (SRC/"data/raw/appstore/appstore_iap_raw.jsonl").read_text().splitlines()]
raw_index = {(z["storefront"], z["app"]):z for z in raw}

def parse_local_price(s):
    """Numeric formatting only; it supplies no billing-period metadata."""
    t=s.replace("\xa0"," ").strip()
    m=re.search(r"\d[\d.,'\s]*",t)
    if not m:
        raise ValueError(s)
    num=m.group().strip().replace("'","").replace(" ","")
    if re.search(r"ribu",t,re.I):
        return float(num.replace(".","").replace(",","."))*1000
    if re.search(r"\bjt\b|juta",t,re.I):
        return float(num.replace(".","").replace(",","."))*1000000
    if "," in num and "." in num:
        dec="," if num.rfind(",")>num.rfind(".") else "."
        num=num.replace("." if dec=="," else ",","").replace(dec,".")
    elif "," in num or "." in num:
        sep="," if "," in num else "."
        pieces=num.split(sep)
        num=".".join(pieces) if len(pieces)==2 and len(pieces[1]) in [1,2] else "".join(pieces)
    return float(num)

parse_records = []
cutoff_checks=[]
for plan in ["chatgpt_go", "chatgpt_plus"]:
    for _, z in lp[lp.plan == plan].iterrows():
        r = raw_index[z.storefront, "chatgpt"]
        names = [(nm,pr) for nm,pr in r.get("iap",[]) if nm.lower() == ("chatgpt go" if plan=="chatgpt_go" else "chatgpt plus")]
        values=[parse_local_price(pr) for _,pr in names]
        for cutoff in [3,5,8]:
            low=[v for v in values if v < cutoff*min(values)]
            counts=collections.Counter(low)
            mode=max(v for v,n in counts.items() if n==max(counts.values()))
            cutoff_checks.append(dict(iso3=z.iso3, plan=plan, annual_filter_cutoff=cutoff,
                                     selected_price_local=mode,published_price_local=z.price_local,
                                     exact_match=bool(abs(mode-z.price_local)<1e-9)))
        parse_records.append(dict(iso3=z.iso3, plan=plan, n_named_entries=len(names),
                                  n_surviving_candidates=int(z.n_distinct_monthly),
                                  explicit_period_label=any("monthly" in nm.lower() for nm,_ in names)))
pd.DataFrame(parse_records).to_csv(OUT / "chatgpt_name_matching_scope.csv", index=False)
pd.DataFrame(cutoff_checks).to_csv(OUT / "chatgpt_annual_filter_sensitivity.csv", index=False)
assert all(z["exact_match"] for z in cutoff_checks)

gpro = ratio_frames["Google Plus / Pro"].copy()
ambiguous_iso = set(lp.loc[(lp.plan == "gemini_pro") & (lp.n_distinct_monthly > 1), "iso3"])
ratio_mapping = []
for spec, sub in [("Published mapping", gpro), ("Exclude ambiguous Pro cells", gpro[~gpro.index.isin(ambiguous_iso)])]:
    fit = direct_ols(sub.ln_gni, sub.log_ratio, sub.currency)
    ratio_mapping.append(dict(specification=spec, **fit))
pd.DataFrame(ratio_mapping).to_csv(OUT / "google_ratio_mapping_sensitivity.csv", index=False)

summary = dict(
    environment=dict(python=sys.version, numpy=np.__version__, pandas=pd.__version__),
    frozen_input_hashes={str(f.relative_to(SRC)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [SRC/"data/processed/country_panel.csv",SRC/"data/processed/appstore_prices_long.csv",SRC/"data/raw/appstore/appstore_iap_raw.jsonl"]},
    independently_recomputed_headline_checks=len(checks), all_headline_checks_pass=True,
    all_direct_HC3_and_CR1_checks_match_statsmodels=True,
    matched_ratio_contrast=dict(go_slope=go_fit["slope"], plus_slope=plus_fit["slope"], **contrast),
    leave_one_currency_out=dict(min=min(z["slope"] for z in loo), max=max(z["slope"] for z in loo)),
    currency_fixed_effect=dict(slope=fe_beta, identifying_currency_count=int(identifying.currency.nunique()), identifying_country_n=len(identifying), inference="Not reported: only USD and EUR contribute within-currency slope identification; singleton currencies do not supply independent within-currency contrasts."),
    currency_block_resampling=dict(draws=B, seed=20260930, percentile_2_5=float(np.quantile(boots,.025)), percentile_97_5=float(np.quantile(boots,.975)), median=float(np.median(boots)), positive_fraction=float((boots>0).mean()), min_resampled_country_n=float(nb.min()), max_resampled_country_n=float(nb.max()), interpretation="Percentile resampling range as a dependence diagnostic, not a calibrated confidence interval with 39 balanced informative clusters."),
    candidate_audit=dict(go_cells=len(lp[lp.plan=="chatgpt_go"]), plus_cells=len(lp[lp.plan=="chatgpt_plus"]), all_go_plus_have_single_surviving_candidate=bool((lp[lp.plan.isin(["chatgpt_go","chatgpt_plus"])].n_distinct_monthly==1).all()), annual_filter_cutoff_3_5_8_all_identical=all(z["exact_match"] for z in cutoff_checks), explicit_monthly_labels_in_chatgpt_go_plus=sum(z["explicit_period_label"] for z in parse_records), ambiguous_google_pro_iso3=sorted(ambiguous_iso), limitation="Single surviving candidate does not authenticate billing period; historical HTML and SKU metadata are absent."),
)
(OUT / "price_reliability_summary.json").write_text(json.dumps(summary, indent=2)+"\n")

# The publication table uses HC3 SE and normal-HC3 intervals in every row.
keep = ["All matched storefronts","USD only","Exclude USD","Exclude USD and EUR"]
tab=[]
for z in rows:
    if z["specification"] not in keep:
        continue
    tab.append(" & ".join([z["specification"], f"{z['slope']:.3f}",
                          f"{z['se_HC3']:.3f}",
                          f"[{z['hc3_ci_low']:.3f}, {z['hc3_ci_high']:.3f}]",
                          str(z["n"])]) + r" \\")
(OUT / "tab_matched_menu_sensitivity.tex").write_text("\n".join(tab)+"\n")
print(pd.DataFrame(rows).to_string(index=False))
print("\nMONTHLY CANDIDATE MAPPING\n",pd.DataFrame(mapping_rows).to_string(index=False))
print("\nSUMMARY\n",json.dumps(summary,indent=2))
