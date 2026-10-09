"""Policy counterfactuals for the $20 tier (Section 5.6 and Table 14 of version 2.1).

For each of the 201 economies with GNI per capita, the annual cost of the standard $20 tier as a share of GNI per
capita (the burden, 1200 p / y) is computed under four price schedules anchored at the U.S. price and income:
  uniform            p = 20
  entry-tier slope   p = 20 (y / y_US)^0.143, the localisation observed for ChatGPT Go applied to the $20 tier
  price-level index  p = 20 PLR, with PLR the Atlas-to-PPP income ratio (Remark 1 of the paper)
  proportional       p = 20 (y / y_US), a constant burden equal to the U.S. burden
and, under uniform pricing, the subsidy that would bring the burden to the 2% broadband benchmark:
  subsidy rate       max(0, 1 - y / 12,000)
  annual subsidy     max(0, 240 - 0.02 y) dollars per subscriber
  fiscal cost        that subsidy for one tenth of the working-age population, as a share of GNI:
                     0.1 (pop_15-64 / pop) max(0, 240 - 0.02 y) / y
Group medians of the economy-level values are reported (ratios are computed before taking medians), with the share
of economies whose burden exceeds 2% under each schedule. The entry-tier slope is read from audit_output/
local_price_robustness.csv (ChatGPT Go, full sample) so that the table follows the estimate.

Outputs: audit_output/policy_counterfactuals.csv, paper_en/tables/tab_policy.tex, and scalars in
audit_output/audit_results_policy.json.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "extensions" / "audit_output"
GROUPS = ["High income", "Upper-middle income", "Lower-middle income", "Low income"]

d = pd.read_csv(ROOT / "data/processed/country_panel.csv", keep_default_na=False, na_values=[""])
d = d[d.gni_atlas.gt(0)].copy()
res = json.load(open(ROOT / "output/results.json"))
beta_go = float(res["loc_chatgpt_go_b"]) if "loc_chatgpt_go_b" in res else None
if beta_go is None:
    lp = pd.read_csv(OUT / "local_price_robustness.csv")
    beta_go = float(lp.loc[(lp.plan.str.contains("Go")) & (lp.sample.str.contains("ull")), "slope"].iloc[0])
y_us = float(d.loc[d.iso3 == "USA", "gni_atlas"].iloc[0])
P = 20.0
d["b_uniform"] = 1200 * P / d.gni_atlas
d["b_entry"] = 1200 * P * (d.gni_atlas / y_us) ** beta_go / d.gni_atlas
d["b_plr"] = 1200 * P / d.gni_ppp                          # = 1200 p PLR / y with PLR = y / y_PPP (Remark 1)
d["b_prop"] = 1200 * P * (d.gni_atlas / y_us) / d.gni_atlas
d["sub_rate"] = np.maximum(0, 1 - d.gni_atlas / (600 * P))
d["sub_usd"] = np.maximum(0, 12 * P - 0.02 * d.gni_atlas)
d["sub_cost_gni"] = 0.1 * (d.pop1564 / d["pop"]) * d.sub_usd / d.gni_atlas * 100
d.to_csv(OUT / "policy_counterfactuals.csv", index=False,
         columns=["iso3", "country_wb", "income_group", "gni_atlas", "gni_ppp", "b_uniform", "b_entry", "b_plr", "b_prop",
                  "sub_rate", "sub_usd", "sub_cost_gni"])

rows, scal = [], {"beta_go": beta_go, "y_us": y_us}
for g in GROUPS:
    s = d[d.income_group == g]
    plr = s[s.b_plr.notna()]
    r = {"group": g, "n": len(s), "uniform": s.b_uniform.median(), "entry": s.b_entry.median(),
         "plr": plr.b_plr.median(), "prop": s.b_prop.median(),
         "above_uniform": (s.b_uniform > 2).mean() * 100, "above_entry": (s.b_entry > 2).mean() * 100,
         "above_plr": (plr.b_plr > 2).mean() * 100,
         "sub_rate": s.sub_rate.median() * 100, "sub_usd": s.sub_usd.median(), "sub_cost": s.sub_cost_gni.median()}
    rows.append(r)
    key = {"High income": "HIC", "Upper-middle income": "UMIC", "Lower-middle income": "LMIC", "Low income": "LIC"}[g]
    for k, v in r.items():
        if k not in ("group",):
            scal[f"{k}_{key}"] = float(v)
tab = pd.DataFrame(rows)
tab.to_csv(OUT / "policy_counterfactuals_groups.csv", index=False)
lines = []
for r in rows:
    lines.append(" & ".join([r["group"], str(r["n"]), f"{r['uniform']:.2f}", f"{r['entry']:.2f}", f"{r['plr']:.2f}",
                             f"{r['prop']:.2f}", f"{r['sub_rate']:.0f}", f"{r['sub_usd']:.0f}", f"{r['sub_cost']:.2f}"]) + r" \\")
(ROOT / "paper_en/tables/tab_policy.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
# whole-sample scalars
scal["share_econ_above2_uniform"] = float((d.b_uniform > 2).mean() * 100)
scal["share_econ_above2_entry"] = float((d.b_entry > 2).mean() * 100)
scal["share_econ_above2_plr"] = float((d.b_plr > 2).mean() * 100)
scal["n_econ_need_subsidy"] = int((d.sub_rate > 0).sum())
scal["n_econ"] = int(len(d))
# population-weighted share of the covered working-age population living where the burden exceeds 2%
w = d[d.pop1564.notna()]
for k in ["b_uniform", "b_entry", "b_plr"]:
    scal[f"pop_share_above2_{k}"] = float(w.loc[w[k] > 2, "pop1564"].sum() / w.pop1564.sum() * 100)
json.dump(scal, open(OUT / "audit_results_policy.json", "w"), indent=2)
print(tab.round(2).to_string(index=False))
print({k: round(v, 3) if isinstance(v, float) else v for k, v in scal.items() if not k[-4:] in ("_HIC", "UMIC", "LMIC", "_LIC")})
