"""Localised entry tiers and adoption: the first rollouts of ChatGPT Go (Section 5.4 of version 2.1).

Design written before any result was examined (8 October 2026; not registered externally). The specification is recorded here and in
audit_output/go_rollout_spec.json; the outputs are audit_output/go_rollout_*.csv and audit_results_rollout.json.

Question. Does the arrival of a cheap, localised entry tier change the share of adults using any generative-AI
product (the extensive margin) or the per-capita activity on a competing product (Claude)? The model of
Appendix A predicts no change on the extensive margin when a free tier already exists, and a cross-provider
response only through substitution.

Treatment and timing (data/raw/openai/chatgpt_go_rollout.csv). ChatGPT Go reached India on 19 August 2025 (and
became free for twelve months to eligible Indian users on 4 November 2025), Indonesia on 22 September 2025, sixteen
further Asian economies on 8 October 2025, 71 undocumented economies on 14 October 2025, Brazil and eight European
economies on 28-30 October 2025, further undocumented economies before 16 January 2026, and the rest of the world
(including the United States) on 16 January 2026. Only the first two cohorts (C1: India, Indonesia; C2: the
Asian sixteen) and the late cohorts are documented at the country level.

Outcomes. (i) Microsoft AI User Share, country-specific estimates: H1 2025 (before any rollout), H2 2025 (C1 exposed
for 3.3-4.5 months, C2 for 2.8 months, C3-C4 for about 2-2.5 months, later cohorts for 0-2 months), Q1 2026 and
Q2 2026 (everyone exposed). (ii) Anthropic AI Usage Index: 4-11 August 2025 (before India's launch), 13-20 November
2025 (C1-C4 exposed), 5-12 February 2026, April and May 2026 (everyone exposed).

Design. Because the comparison group is partly exposed from mid-October 2025, the H2 2025 contrast is one of
exposure length (C1 and C2 versus the rest), not of treatment versus no treatment. The analysis is therefore a
case comparison with permutation inference, not an event study:
  1. For each outcome window, compute the change in the log outcome for every economy.
  2. Regress that change on log GNI per capita and the initial log level in the comparison economies (all
     country-specific economies not in C1 or C2), and compute the residual change for every economy using those
     coefficients.
  3. Report the residual of India, of Indonesia and of the C2 mean, and its rank among the residuals of all
     economies (a placebo-in-space permutation p-value: the share of economies with an absolute residual at
     least as large). Also report the C2 contrast with an HC3 standard error from the pooled regression with a
     C2 indicator.
  4. Prediction under the model: no systematic positive residual for any-use in H2 2025 or Q1 2026; for Claude
     activity a zero or negative residual (substitution) in November 2025.
  5. Do the same for India alone in the windows after its free offer (H2 2025 -> Q1 2026; Nov 2025 -> Feb 2026).
No outcome was examined before this specification was written. Nothing in this script is a causal estimate: the
rollout order was chosen by the vendor, and only four (Microsoft) or five (Anthropic) windows are observed.

Run: python extensions/go_rollout_analysis.py
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "extensions" / "audit_output"
OUT.mkdir(exist_ok=True)

SPEC = {
    "written": "2026-10-08",
    "cohorts": {"C1": ["IND", "IDN"],
                "C2": ["AFG", "BGD", "BTN", "BRN", "KHM", "LAO", "MYS", "MDV", "MMR", "NPL", "PAK", "PHL", "LKA", "THA",
                       "TLS", "VNM"]},
    "exposure_months_h2_2025": {"IND": 4.4, "IDN": 3.3, "C2": 2.8, "C3_C4": 2.3, "later": "0-2", "C6": 0},
    "windows": {
        "ms": [("ms_h1_2025", "ms_h2_2025", "H1 2025 to H2 2025"), ("ms_h2_2025", "ms_q1_2026", "H2 2025 to Q1 2026"),
               ("ms_q1_2026", "ms_q2_2026", "Q1 2026 to Q2 2026")],
        "aui": [("aui_aug25", "aui_nov25", "Aug 2025 to Nov 2025"), ("aui_nov25", "aui_feb26", "Nov 2025 to Feb 2026"),
                ("aui_feb26", "aui_may26", "Feb 2026 to May 2026")]},
    "comparison": "country-specific economies (Microsoft) or published economies (Anthropic) not in C1 or C2",
    "adjustment": "OLS of the log change on log GNI per capita and the initial log level, fitted on the comparison group",
    "inference": "rank of the absolute residual among all economies (permutation p-value); HC3 for the C2 indicator",
}
(OUT / "go_rollout_spec.json").write_text(json.dumps(SPEC, indent=2))

d = pd.read_csv(ROOT / "data/processed/country_panel.csv", keep_default_na=False, na_values=[""])
d = d[d.gni_atlas.notna()].copy()
d["ln_gni"] = np.log(d.gni_atlas)
C1, C2 = SPEC["cohorts"]["C1"], SPEC["cohorts"]["C2"]
d["cohort"] = np.where(d.iso3.isin(C1), "C1", np.where(d.iso3.isin(C2), "C2", "other"))

rows, summary = [], {}


def analyse(pre, post, label, source):
    s = d[d[pre].notna() & d[post].notna() & (d[pre] > 0) & (d[post] > 0)].copy()
    if source == "ms":
        s = s[s.ms_country_specific.astype(str).str.lower().isin(["true", "1", "1.0"])]
    s["dlog"] = np.log(s[post]) - np.log(s[pre])
    s["lpre"] = np.log(s[pre])
    comp = s[s.cohort == "other"]
    X = sm.add_constant(comp[["ln_gni", "lpre"]])
    fit = sm.OLS(comp.dlog, X).fit(cov_type="HC3")
    s["resid"] = s.dlog - fit.predict(sm.add_constant(s[["ln_gni", "lpre"]]))
    # permutation p-value: share of all economies with |resid| >= the economy's |resid|
    absr = s.resid.abs().values
    def perm_p(r):
        return float((absr >= abs(r)).mean())
    out = {"source": source, "window": label, "n_comparison": int(len(comp)), "n_all": int(len(s)),
           "sd_resid_comparison": float(comp.assign(resid=s.loc[comp.index, "resid"]).resid.std(ddof=1))}
    for iso in C1:
        if iso in set(s.iso3):
            r = float(s.loc[s.iso3 == iso, "resid"].iloc[0])
            out[f"{iso}_dlog"] = float(s.loc[s.iso3 == iso, "dlog"].iloc[0])
            out[f"{iso}_resid"] = r
            out[f"{iso}_perm_p"] = perm_p(r)
            out[f"{iso}_pre"] = float(s.loc[s.iso3 == iso, pre].iloc[0])
            out[f"{iso}_post"] = float(s.loc[s.iso3 == iso, post].iloc[0])
    c2 = s[s.cohort == "C2"]
    out["C2_n"] = int(len(c2))
    if len(c2):
        out["C2_mean_resid"] = float(c2.resid.mean())
        # pooled regression with a C2 indicator (C1 excluded), HC3
        p = s[s.cohort != "C1"].copy()
        p["c2"] = (p.cohort == "C2").astype(float)
        fit2 = sm.OLS(p.dlog, sm.add_constant(p[["ln_gni", "lpre", "c2"]])).fit(cov_type="HC3")
        out["C2_coef"] = float(fit2.params["c2"]); out["C2_se"] = float(fit2.bse["c2"]); out["C2_p"] = float(fit2.pvalues["c2"])
        # permutation: mean residual of 1000 random groups of the same size drawn from the comparison economies
        rng = np.random.default_rng(20261008)
        compres = s.loc[s.cohort == "other", "resid"].values
        draws = np.array([rng.choice(compres, len(c2), replace=False).mean() for _ in range(2000)])
        out["C2_perm_p"] = float((np.abs(draws) >= abs(c2.resid.mean())).mean())
    out["comparison_mean_dlog"] = float(comp.dlog.mean())
    rows.append(out)
    return s[["iso3", "country_wb", "income_group", "cohort", pre, post, "dlog", "resid"]].assign(window=label, source=source)


detail = []
for pre, post, label in SPEC["windows"]["ms"]:
    detail.append(analyse(pre, post, label, "ms"))
for pre, post, label in SPEC["windows"]["aui"]:
    detail.append(analyse(pre, post, label, "aui"))
pd.concat(detail).to_csv(OUT / "go_rollout_economy_detail.csv", index=False)
res = pd.DataFrame(rows)
res.to_csv(OUT / "go_rollout_summary.csv", index=False)

# levels for the case table: India, Indonesia, C2 median, lower-middle-income median (country-specific), all country-specific median
lv = {}
cs = d[d.ms_country_specific.astype(str).str.lower().isin(["true", "1", "1.0"])]
for k, name in [("ms_h1_2025", "H1 2025"), ("ms_h2_2025", "H2 2025"), ("ms_q1_2026", "Q1 2026"), ("ms_q2_2026", "Q2 2026")]:
    lv[name] = {"India": float(d.loc[d.iso3 == "IND", k].iloc[0]), "Indonesia": float(d.loc[d.iso3 == "IDN", k].iloc[0]),
                "C2 median": float(cs.loc[cs.cohort == "C2", k].median()),
                "LMIC median (country-specific, excl. C1-C2)": float(cs[(cs.cohort == "other") & (cs.income_group == "Lower-middle income")][k].median()),
                "All country-specific median (excl. C1-C2)": float(cs[cs.cohort == "other"][k].median())}
for k, name in [("aui_aug25", "AUI Aug 2025"), ("aui_nov25", "AUI Nov 2025"), ("aui_feb26", "AUI Feb 2026"), ("aui_apr26", "AUI Apr 2026"), ("aui_may26", "AUI May 2026")]:
    a = d[d[k].notna()]
    lv[name] = {"India": float(d.loc[d.iso3 == "IND", k].iloc[0]) if d.loc[d.iso3 == "IND", k].notna().iloc[0] else None,
                "Indonesia": float(d.loc[d.iso3 == "IDN", k].iloc[0]) if d.loc[d.iso3 == "IDN", k].notna().iloc[0] else None,
                "C2 median": float(a.loc[a.cohort == "C2", k].median()),
                "LMIC median (excl. C1-C2)": float(a[(a.cohort == "other") & (a.income_group == "Lower-middle income")][k].median()),
                "All published median (excl. C1-C2)": float(a[a.cohort == "other"][k].median())}
json.dump({"spec": SPEC, "levels": lv, "windows": rows}, open(OUT / "audit_results_rollout.json", "w"), indent=2)
pd.set_option("display.width", 200)
print(res.round(3).to_string())
print(json.dumps(lv, indent=1))


# ---------------------------------------------------------------------------------------------------------------
# Robustness checks specified AFTER the main results were seen (8 October 2026), reported as such in the paper:
# (a) region fixed effects in the adjustment regression; (b) comparison group restricted to non-high-income
# economies; (c) C2 contrast in percentage points instead of logs. Same windows and inference.
rob = []
for pre, post, label in SPEC["windows"]["ms"] + SPEC["windows"]["aui"]:
    source = "ms" if pre.startswith("ms") else "aui"
    s = d[d[pre].notna() & d[post].notna() & (d[pre] > 0) & (d[post] > 0)].copy()
    if source == "ms":
        s = s[s.ms_country_specific.astype(str).str.lower().isin(["true", "1", "1.0"])]
    s["dlog"] = np.log(s[post]) - np.log(s[pre]); s["lpre"] = np.log(s[pre]); s["dpp"] = s[post] - s[pre]
    for variant in ["region_fe", "non_high_income", "pp"]:
        p = s[s.cohort != "C1"].copy()
        if variant == "non_high_income":
            p = p[p.income_group != "High income"]
        p["c2"] = (p.cohort == "C2").astype(float)
        X = p[["ln_gni", "lpre", "c2"]].copy()
        y = p.dlog
        if variant == "region_fe":
            X = pd.concat([X, pd.get_dummies(p.region, prefix="r", drop_first=True).astype(float)], axis=1)
        if variant == "pp":
            X = p[["ln_gni", "c2"]].copy(); X["pre"] = p[pre]; y = p.dpp
        fit = sm.OLS(y, sm.add_constant(X)).fit(cov_type="HC3")
        rob.append({"source": source, "window": label, "variant": variant, "n": int(fit.nobs),
                    "C2_coef": float(fit.params["c2"]), "C2_se": float(fit.bse["c2"]), "C2_p": float(fit.pvalues["c2"])})
        # India's residual under the same variant
        q = s.copy()
        Xq = q[["ln_gni", "lpre"]].copy(); yq = q.dlog
        comp_mask = (q.cohort == "other") & ((q.income_group != "High income") if variant == "non_high_income" else True)
        if variant == "region_fe":
            Xq = pd.concat([Xq, pd.get_dummies(q.region, prefix="r", drop_first=True).astype(float)], axis=1)
        if variant == "pp":
            Xq = q[["ln_gni"]].copy(); Xq["pre"] = q[pre]; yq = q.dpp
        f2 = sm.OLS(yq[comp_mask], sm.add_constant(Xq[comp_mask])).fit()
        q["resid"] = yq - f2.predict(sm.add_constant(Xq))
        r_ind = float(q.loc[q.iso3 == "IND", "resid"].iloc[0])
        rob[-1]["IND_resid"] = r_ind
        rob[-1]["IND_perm_p"] = float((q.resid.abs().values >= abs(r_ind)).mean())
pd.DataFrame(rob).to_csv(OUT / "go_rollout_robustness.csv", index=False)
print(pd.DataFrame(rob).round(3).to_string())


# ---------------------------------------------------------------------------------------------------------------
# Table body (paper_en/tables/tab_rollout.tex) and Figure 4 (paper_en/figures/fig_rollout_en.pdf; Korean version
# written by figure_rollout_ko.py from the same CSVs).
robdf = pd.DataFrame(rob)
lines = []
for r in rows:
    fe = robdf[(robdf.window == r["window"]) & (robdf.variant == "region_fe")].iloc[0]
    src = "Any use" if r["source"] == "ms" else "Claude activity"
    win = r["window"].replace(" to ", "--")
    lines.append(" & ".join([
        f"{src}, {win}", str(r["n_comparison"]), f"{r['comparison_mean_dlog']:.3f}",
        f"{r['IND_dlog']:.3f}", f"{r['IND_resid']:.3f} ({r['IND_perm_p']:.2f})",
        f"{r['C2_coef']:.3f} ({r['C2_se']:.3f}) [{r['C2_perm_p']:.2f}]",
        f"{fe['C2_coef']:.3f} ({fe['C2_se']:.3f})"]) + r" \\")
(ROOT / "paper_en/tables/tab_rollout.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
# signs of the C2 residuals in each window (reported in the text)
signs = {}
det = pd.concat(detail)
for (src, win), g in det[det.cohort == "C2"].groupby(["source", "window"]):
    signs[f"{src}|{win}"] = {"positive": int((g.resid > 0).sum()), "n": int(len(g))}
json.dump({"spec": SPEC, "levels": lv, "windows": rows, "robustness": rob, "c2_signs": signs},
          open(OUT / "audit_results_rollout.json", "w"), indent=2)
print(signs)
