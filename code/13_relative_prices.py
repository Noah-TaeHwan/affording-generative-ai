"""
13_relative_prices.py   (no network; run after 12_default_panel.py)
Relative prices within a vendor and a storefront: the income gradient of the price of one plan against another plan of the same
vendor (or against a frontier numeraire) that does not use Apple's default schedule.

Idea.  Within a storefront every plan of one vendor goes through the same conversion, tax and rounding.  The price of plan A
relative to plan B in storefront c, normalised by the same ratio in the US, therefore needs no estimate of the default:
  r_ic = ln(price in US$ of plan i in c / US price of i),   d_c = r_A,c - r_B,c = ln(p_A,c / p_B,c) - ln(P_A,US / P_B,US)
(the exchange rate and the storefront's tax cancel in d_c).  A plan that is priced like the US dollar price everywhere has
d_c = 0 against another such plan; a capped entry tier that is localised has a positive slope of d_c on ln(GNI per capita).
Sample: the plan rows of 09b_wave2_items.py (after the annual-as-monthly guard), storefronts other than the US with GNI per
capita (Atlas) and a ratio to the US price.  LMIC = low plus lower-middle income (World Bank FY2027).

Inputs   data/processed/wave2_plan_rows.csv (09b_wave2_items.py), wave2_plan_vs_default.csv (12_default_panel.py)
         output/tables/W1_wave2_plans.csv (12_default_panel.py: plan labels and deviation slopes)
Outputs  output/tables/W8_relative_pairs.csv         (a) 12 within-vendor pairs
         output/tables/W9_relative_stacked.csv        (b) stacked regression with firm x storefront and item fixed effects
         output/tables/W10_cross_vendor.csv           (c) every plan against ChatGPT Plus and against the median frontier plan
         output/tables/W12_increment.csv              (d) increment of a plan over the next lower plan against the default increment
         data/processed/wave2_relative_long.csv       pair x storefront relative prices behind W8
         output/results_wave2.json                    rel_*, stacked_*, relplus_*, relfront_*, incr_*, incrusd_* are added
         data/processed/wave2_data_dictionary.csv     the description of wave2_relative_long.csv is added

Definitions.
  (a) Pairs (A vs B), the 21 pairs and their order are fixed in PAIRS.  Per pair: N = storefronts with both plans, GNI and a ratio
      to the US price; slope = OLS slope of d_c on ln(GNI); HC1 standard error; CR1 standard error clustered by storefront
      currency (CGM small-sample factor G / (G - 1) (N - 1) / (N - 2); all US$-priced storefronts form one cluster); randomisation-
      inference p-value = share of 2,000 random permutations of the ln(GNI) vector across the storefronts (numpy default_rng,
      seed 20261016, the pairs in the order of PAIRS) with |slope| >= |observed slope|; median of exp(d_c) = A's price relative
      to B's, in LMIC storefronts; share of storefronts with d_c < ln 0.9; share with |d_c| < 0.005 (mass at a relative price of 1).
  (b) Stacked regression over the 20 items of the five vendors with several tiers (STACK):
        r_ic = theta_(f(i),c) + mu_i + sum_g gamma_g 1[i in g] ln y_c + e_ic,
      theta = vendor x storefront fixed effects, mu = item fixed effects (one item per vendor dropped, which the vendor x storefront
      effects absorb), groups g = capped AI tier, no AI allowance, small AI allowance; the omitted group is the frontier tiers.
      OLS with dummies (statsmodels); standard errors clustered two-way by storefront and item (cov_type='cluster' with a
      two-column groups array: the CGM combination of the storefront, the item and the storefront x item covariance matrices, each
      with statsmodels' default small-sample factor G / (G - 1) (N - 1) / (N - K), K counting every dummy).  The same regression
      on US$-priced storefronts and on local-currency storefronts only.  Randomisation inference: all relabellings that permute
      the group labels among the items of each vendor and keep the number of items per group and vendor (129,600 here; if there
      were more than 200,000, 20,000 random relabellings, seed 20261016) are enumerated; the p-value of gamma_g is the share of
      relabellings whose |gamma_g| is at least the observed one.  The coefficients of all relabellings are computed by the
      Frisch-Waugh-Lovell theorem (the fixed effects are partialled out once; each relabelling is a 3 x 3 solve).
  (c) Cross-vendor numeraires: for each plan the HC1 slope of ln(p_plan,c / p_num,c) - ln(P_plan,US / P_num,US) on ln(GNI) with
      the numeraire (i) ChatGPT Plus or (ii) the median local price of the three US$19.99 frontier plans (ChatGPT Plus, Google
      AI Pro, Microsoft 365 Premium; at least two present; US numeraire 19.99); LMIC median = 100 (e^m - 1), m the median of the
      log relative price in LMIC storefronts; the deviation slope of 12_default_panel.py is shown for comparison.
  (d) Increment test for five (high plan, low plan) pairs.  Relative to the default increment: the slope on ln(GNI) of
      ln[(p_H,c - p_L,c) / (D_H,c - D_L,c)], D = the default reference of wave2_plan_vs_default.csv, in storefronts with p_H > p_L
      and D_H > D_L; median ratio by World Bank income group (High, Upper-middle, Lower-middle, Low income).  In US$: the slope of
      ln[(p_H,c - p_L,c)_US$ / (P_H,US - P_L,US)] on ln(GNI), with p_H > p_L.
"""
import os
for _v in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ[_v] = "1"                                   # fixed order of summation: the output is byte-identical between runs
import itertools, json, math, pathlib
import numpy as np
import pandas as pd
import statsmodels.api as sm
from wave2_common import LMIC, NAN, ols_hc1, ols_cr1

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROC, TAB = ROOT / "data" / "processed", ROOT / "output" / "tables"
SEED, N_PERM = 20261016, 2000
MAX_EXACT, N_SAMPLE = 500_000, 20_000                      # exact enumeration up to this many relabellings, else a random sample
RI_CHUNK = 50_000                                           # relabellings per batch of the vectorised enumeration (memory)
R = {}
rng = np.random.default_rng(SEED)

PLAN_ROWS = pd.read_csv(PROC / "wave2_plan_rows.csv", keep_default_na=False, na_values=[""])
PVD = pd.read_csv(PROC / "wave2_plan_vs_default.csv", keep_default_na=False, na_values=[""])
W1 = pd.read_csv(TAB / "W1_wave2_plans.csv", keep_default_na=False, na_values=[""]).set_index("plan")
LABEL = W1.label.to_dict()
assert not PLAN_ROWS.duplicated(["plan", "storefront"]).any()

# the sample: storefronts other than the US with income and a ratio to the US price
S = PLAN_ROWS[(PLAN_ROWS.storefront != "us") & PLAN_ROWS.gni.notna() & PLAN_ROWS.ratio_us.notna()].sort_values(["plan", "storefront"])
S = S.assign(lr=np.log(S.ratio_us), lny=np.log(S.gni))
LR = S.pivot(index="storefront", columns="plan", values="lr")             # r_ic
META = S.drop_duplicates("storefront").set_index("storefront")[["currency", "income_group", "gni"]].sort_index()
assert (S.groupby("storefront")[["currency", "income_group", "gni"]].nunique() <= 1).all().all()


def finite(x):
    return x == x and x not in (float("inf"), float("-inf"))


def put(prefix, values):
    """Add `prefix_<key>` to the results for every value that is not missing."""
    for k, v in values.items():
        if v is not None and finite(float(v)):
            R[f"{prefix}_{k}"] = int(v) if isinstance(v, (int, np.integer)) else float(v)


# ================================================================================================ (a) pairs
PAIRS = [   # key, firm, label, plan A, plan B.  Rule: every plan of Table 4 (and Anthropic's plans) is plan A, measured relative
            # to its firm's standard frontier tier as plan B (ChatGPT Plus, Google AI Pro, Claude Pro, SuperGrok at $30 for X Corp/xAI,
            # Microsoft 365 Premium, Character.AI+ at $9.99), whether A is a lower or a higher tier; plus two X Corp pairs that hold
            # the app fixed (X Premium vs X Premium Plus) or compare the two entry products (X Premium Basic vs SuperGrok Lite)
    ("go_plus", "OpenAI", "ChatGPT Go vs Plus", "chatgpt_go", "chatgpt_plus"),
    ("pro100_plus", "OpenAI", "ChatGPT Pro 100 vs Plus", "chatgpt_pro100", "chatgpt_plus"),
    ("pro200_plus", "OpenAI", "ChatGPT Pro 200 vs Plus", "chatgpt_pro200", "chatgpt_plus"),
    ("pro500_plus", "OpenAI", "ChatGPT Pro 500 vs Plus", "chatgpt_pro500", "chatgpt_plus"),
    ("ytprem_aipro", "Google", "YouTube Premium vs Google AI Pro", "youtube_premium", "gemini_pro"),
    ("ytlite_aipro", "Google", "YouTube Premium Lite vs Google AI Pro", "youtube_premium_lite", "gemini_pro"),
    ("ytmusic_aipro", "Google", "YouTube Music vs Google AI Pro", "youtubemusic_music", "gemini_pro"),
    ("aiplus_aipro", "Google", "Google AI Plus vs AI Pro", "gemini_plus", "gemini_pro"),
    ("ultra_aipro", "Google", "Google AI Ultra vs AI Pro", "gemini_ultra", "gemini_pro"),
    ("xbasic_supergrok", "X Corp/xAI", "X Premium Basic vs SuperGrok", "x_premium_basic", "supergrok"),
    ("xprem_supergrok", "X Corp/xAI", "X Premium vs SuperGrok", "x_premium", "supergrok"),
    ("sglite_supergrok", "X Corp/xAI", "SuperGrok Lite vs SuperGrok", "supergrok_lite", "supergrok"),
    ("xplus_supergrok", "X Corp/xAI", "X Premium Plus vs SuperGrok", "x_premium_plus", "supergrok"),
    ("sgplus_supergrok", "X Corp/xAI", "SuperGrok Plus vs SuperGrok", "supergrok_plus", "supergrok"),
    ("heavy_supergrok", "X Corp/xAI", "SuperGrok Heavy vs SuperGrok", "supergrok_heavy", "supergrok"),
    ("xprem_xplus", "X Corp/xAI", "X Premium vs X Premium Plus", "x_premium", "x_premium_plus"),
    ("xbasic_sglite", "X Corp/xAI", "X Premium Basic vs SuperGrok Lite", "x_premium_basic", "supergrok_lite"),
    ("m365pers_prem", "Microsoft", "Microsoft 365 Personal vs Premium", "m365_personal", "m365_premium"),
    ("cai_lite_plus", "Character.AI", "Character.AI Lite vs Character.AI+", "characterai_lite", "characterai_plus"),
    ("max5_claudepro", "Anthropic", "Claude Max 5$\\times$ vs Pro", "claude_max5x", "claude_pro"),
    ("max20_claudepro", "Anthropic", "Claude Max 20$\\times$ vs Pro", "claude_max20x", "claude_pro"),
]


STACK = [   # plan, firm, group (capped AI tier, no AI allowance, small AI allowance; frontier = omitted group).  Rule: every named
            # monthly consumer plan of the five firms with a U.S. price of $4 or more and listed in at least 60 storefronts, except
            # annual and family variants, storage plans (Google One, Microsoft 365 Basic) and X's creator and post-promotion products
    ("chatgpt_go", "OpenAI", "capped"), ("chatgpt_plus", "OpenAI", "frontier"), ("chatgpt_pro100", "OpenAI", "frontier"),
    ("chatgpt_pro200", "OpenAI", "frontier"), ("chatgpt_pro500", "OpenAI", "frontier"),
    ("gemini_plus", "Google", "capped"), ("youtube_premium", "Google", "noai"), ("youtube_premium_lite", "Google", "noai"),
    ("youtubemusic_music", "Google", "noai"), ("gemini_pro", "Google", "frontier"), ("gemini_ultra", "Google", "frontier"),
    ("supergrok_lite", "X Corp/xAI", "capped"), ("x_premium_basic", "X Corp/xAI", "noai"), ("x_premium", "X Corp/xAI", "smallai"),
    ("x_premium_plus", "X Corp/xAI", "frontier"), ("supergrok", "X Corp/xAI", "frontier"), ("supergrok_plus", "X Corp/xAI", "frontier"),
    ("supergrok_heavy", "X Corp/xAI", "frontier"),
    ("m365_personal", "Microsoft", "smallai"), ("m365_premium", "Microsoft", "frontier"),
    ("characterai_lite", "Character.AI", "capped"), ("characterai_plus", "Character.AI", "frontier"),
]
GROUPS = ["capped", "noai", "smallai"]
GROUP_LABEL = {"capped": "Capped AI tier", "noai": "No AI allowance", "smallai": "Small AI allowance"}
FIRMS = list(dict.fromkeys(f for _, f, _ in STACK))
FIRM, GRP = {p: f for p, f, _ in STACK}, {p: g for p, _, g in STACK}
GRP_ALL = dict(GRP)                                        # plans outside the stack (Anthropic's) are frontier tiers or named below
GRP_ALL.update({"claude_pro": "frontier", "claude_max5x": "frontier", "claude_max20x": "frontier"})


def ri_p(x, y, b):
    """Two-sided randomisation p-value of the slope of y on x: share of N_PERM random permutations of x with |slope| >= |b|."""
    xc, yc = x - x.mean(), y - y.mean()
    perm = rng.permuted(np.tile(np.arange(len(x)), (N_PERM, 1)), axis=1)
    bp = (xc[perm] * yc).sum(axis=1) / (xc ** 2).sum()
    return float((np.abs(bp) >= abs(b) * (1 - 1e-12)).mean())


w8, long = [], []
for key, firm, lab, a, b in PAIRS:
    d = (LR[a] - LR[b]).dropna()
    m = META.loc[d.index]
    x = np.log(m.gni.values)
    slope, hc1, cr1, n, g = ols_cr1(x, d.values, m.currency.values)
    lm = d[m.income_group.isin(LMIC).values]
    row = dict(pair=key, firm=firm, label=lab, plan_a=a, plan_b=b, group_a=GRP_ALL.get(a, "frontier"), group_b=GRP_ALL.get(b, "frontier"),
               n=n, n_currencies=g, slope=slope, se_hc1=hc1, se_cr1=cr1,
               ri_p=ri_p(x, d.values, slope), lmic_n=int(len(lm)), lmic_med=float(np.median(np.exp(lm))),
               share_below09=float((d < math.log(0.9)).mean()), mass_at1=float((d.abs() < 0.005).mean()))
    w8.append(row)
    put(f"rel_{key}", {k: row[k] for k in ("n", "n_currencies", "slope", "se_hc1", "se_cr1", "ri_p", "lmic_n", "lmic_med",
                                           "share_below09", "mass_at1")})
    long.append(pd.DataFrame(dict(pair=key, firm=firm, storefront=d.index, currency=m.currency.values, income_group=m.income_group.values,
                                  gni=m.gni.values, plan_a=a, plan_b=b, ratio_us_a=np.exp(LR.loc[d.index, a]).values,
                                  ratio_us_b=np.exp(LR.loc[d.index, b]).values, ln_rel=d.values)))
w8 = pd.DataFrame(w8)
# the pairs of two frontier tiers of the same firm (the bound quoted in the text: the slope of the higher tier relative to the standard tier)
ff = w8[(w8.group_a == "frontier") & (w8.group_b == "frontier")]
put("rel_frontierpairs", dict(n_pairs=int(len(ff)), slope_min=float(ff.slope.min()), slope_max=float(ff.slope.max()),
                              abs_slope_max=float(ff.slope.abs().max()), n_negative=int((ff.slope < 0).sum()),
                              se_cr1_max=float(ff.se_cr1.max())))
w8.round(10).to_csv(TAB / "W8_relative_pairs.csv", index=False)
R["rel_ri_permutations"], R["rel_ri_seed"] = N_PERM, SEED
long = pd.concat(long, ignore_index=True)
long.round(10).to_csv(PROC / "wave2_relative_long.csv", index=False)

# ================================================================================================ (b) stacked regression
ITEMS = [p for p, _, _ in STACK]

D = S[S.plan.isin(ITEMS)].copy()
D["firm"], D["grp"] = D.plan.map(FIRM), D.plan.map(GRP)


def design(d):
    """Regressors (the three group x ln y columns) and fixed effects (item dummies, one per vendor dropped; vendor x storefront cells)."""
    items = [p for p in ITEMS if (d.plan == p).any()]
    drop = {f: next(p for p in items if FIRM[p] == f) for f in FIRMS if any(FIRM[p] == f for p in items)}
    g = np.column_stack([((d.grp == k) * d.lny).values for k in GROUPS])
    fe = [(d.plan == p).astype(float).values for p in items if p not in drop.values()]
    cell = (d.firm + "|" + d.storefront).values
    cells = sorted(set(cell))
    fe += [(cell == c).astype(float) for c in cells]
    return g, np.column_stack(fe), items


def stacked_fit(d):
    """Group coefficients and their two-way (storefront, item) cluster-robust covariance matrix; sizes of the sample."""
    g, fe, items = design(d)
    X = np.column_stack([g, fe])
    assert np.linalg.matrix_rank(X) == X.shape[1], "rank-deficient design"
    groups = np.column_stack([pd.factorize(d.storefront)[0], pd.factorize(d.plan)[0]])
    res = sm.OLS(d.lr.values, X).fit(cov_type="cluster", cov_kwds={"groups": groups})
    v = np.diag(res.cov_params())[:3]
    assert (v > 0).all(), "two-way cluster covariance not positive"
    return dict(gamma=res.params[:3], se=np.sqrt(v), n_obs=len(d), n_items=len(items), n_storefronts=int(d.storefront.nunique()))


fits = {"": stacked_fit(D), "usd": stacked_fit(D[D.currency == "USD"]), "lcu": stacked_fit(D[D.currency != "USD"])}
main = fits[""]

# exact randomisation inference (Frisch-Waugh-Lovell): partial the fixed effects out of the 20 item x ln y columns and of y once
g_, fe_, _ = design(D)
Z = np.column_stack([((D.plan == p) * D.lny).values for p in ITEMS])                  # N x 20
rhs = np.column_stack([Z, D.lr.values])
res_ = rhs - fe_ @ np.linalg.lstsq(fe_, rhs, rcond=None)[0]
A_, h_ = res_[:, :-1].T @ res_[:, :-1], res_[:, :-1].T @ res_[:, -1]                    # Z'MZ (20 x 20), Z'My (20)
CODE = {"capped": 0, "noai": 1, "smallai": 2, "frontier": 3}
lab0 = np.array([CODE[GRP[p]] for p in ITEMS])
members = {f: [i for i, p in enumerate(ITEMS) if FIRM[p] == f] for f in FIRMS}
arrangements = {f: np.array(sorted(set(itertools.permutations(lab0[members[f]])))) for f in FIRMS}   # distinct relabellings per vendor
sizes = [len(arrangements[f]) for f in FIRMS]
n_relabel = int(np.prod(sizes))
if n_relabel <= MAX_EXACT:
    pick = np.indices(sizes).reshape(len(FIRMS), -1)                                      # all combinations
else:
    pick = np.array(np.unravel_index(np.sort(rng.choice(n_relabel, N_SAMPLE, replace=False)), sizes))
labels = np.empty((pick.shape[1], len(ITEMS)), dtype=np.int8)
for k, f in enumerate(FIRMS):
    labels[:, members[f]] = arrangements[f][pick[k]]
ind0 = np.stack([lab0 == k for k in range(3)], axis=1).astype(float)                   # the observed assignment
obs = np.linalg.solve(ind0.T @ A_ @ ind0, ind0.T @ h_)
assert np.allclose(obs, main["gamma"], rtol=0, atol=1e-9), "Frisch-Waugh-Lovell coefficients differ from OLS"
n_ge = np.zeros(3, dtype=int)
for start in range(0, labels.shape[0], RI_CHUNK):                                       # in batches: relabellings x items x 3 groups
    ind = np.stack([labels[start:start + RI_CHUNK] == k for k in range(3)], axis=2).astype(float)
    G_ = np.matmul(ind.transpose(0, 2, 1), np.matmul(A_, ind))
    v_ = np.einsum("rig,i->rg", ind, h_)
    gam = np.linalg.solve(G_, v_[..., None])[..., 0]
    n_ge += (np.abs(gam) >= np.abs(obs) * (1 - 1e-9)).sum(axis=0)
ri = n_ge / pick.shape[1]
R["stacked_ri_permutations"], R["stacked_ri_exact"] = int(pick.shape[1]), bool(n_relabel <= MAX_EXACT)

w9 = []
for k, grp in enumerate(GROUPS):
    items = [LABEL[p] for p in ITEMS if GRP[p] == grp]
    w9.append(dict(group=grp, label=GROUP_LABEL[grp], items=", ".join(items), n_items=len(items),
                   gamma=main["gamma"][k], se=main["se"][k], ri_p=ri[k], ri_n_ge=int(n_ge[k]),
                   gamma_usd=fits["usd"]["gamma"][k], se_usd=fits["usd"]["se"][k],
                   gamma_lcu=fits["lcu"]["gamma"][k], se_lcu=fits["lcu"]["se"][k],
                   n_obs=main["n_obs"], n_storefronts=main["n_storefronts"],
                   n_obs_usd=fits["usd"]["n_obs"], n_storefronts_usd=fits["usd"]["n_storefronts"],
                   n_obs_lcu=fits["lcu"]["n_obs"], n_storefronts_lcu=fits["lcu"]["n_storefronts"], n_permutations=int(pick.shape[1])))
    put(f"stacked_{grp}", dict(gamma=main["gamma"][k], se=main["se"][k], ri_p=ri[k], ri_n_ge=int(n_ge[k]),
                               gamma_usd=fits["usd"]["gamma"][k], se_usd=fits["usd"]["se"][k],
                               gamma_lcu=fits["lcu"]["gamma"][k], se_lcu=fits["lcu"]["se"][k]))
pd.DataFrame(w9).round(10).to_csv(TAB / "W9_relative_stacked.csv", index=False)
put("stacked", dict(n_obs=main["n_obs"], n_items=main["n_items"], n_storefronts=main["n_storefronts"],
                    n_obs_usd=fits["usd"]["n_obs"], n_storefronts_usd=fits["usd"]["n_storefronts"],
                    n_obs_lcu=fits["lcu"]["n_obs"], n_storefronts_lcu=fits["lcu"]["n_storefronts"]))

# ================================================================================================ (c) cross-vendor numeraires
CV_PLANS = [   # firm, plan (the order of the table): the plans of Table 4, Anthropic's plans, the same firms' storage and creator
               # products, Perplexity Pro and three other apps
    ("OpenAI", "chatgpt_go"), ("OpenAI", "chatgpt_plus"), ("OpenAI", "chatgpt_pro100"), ("OpenAI", "chatgpt_pro200"),
    ("OpenAI", "chatgpt_pro500"),
    ("Anthropic", "claude_pro"), ("Anthropic", "claude_max5x"), ("Anthropic", "claude_max20x"),
    ("Google", "gemini_plus"), ("Google", "gemini_pro"), ("Google", "gemini_ultra"), ("Google", "gemini_100gb"), ("Google", "googleone_aiplus2tb"),
    ("Google", "youtube_premium"), ("Google", "youtube_premium_lite"), ("Google", "youtubemusic_music"),
    ("Google", "youtube_premium_family"), ("Google", "youtubemusic_family"),
    ("X Corp/xAI", "x_creator"), ("X Corp/xAI", "x_premium_basic"), ("X Corp/xAI", "x_premium"), ("X Corp/xAI", "x_premium_plus"),
    ("X Corp/xAI", "supergrok_lite"), ("X Corp/xAI", "supergrok"), ("X Corp/xAI", "supergrok_plus"), ("X Corp/xAI", "supergrok_heavy"),
    ("Microsoft", "m365_basic"), ("Microsoft", "m365_personal"), ("Microsoft", "m365_family"), ("Microsoft", "m365_premium"),
    ("Character.AI", "characterai_lite"), ("Character.AI", "characterai_plus"),
    ("Perplexity", "perplexity_pro"),
    ("Other apps", "duolingo_super"), ("Other apps", "telegram_premium"), ("Other apps", "snapchat_plus"),
]
FRONTIER, FRONTIER_US = ["chatgpt_plus", "gemini_pro", "m365_premium"], 19.99
PRICE = S.pivot(index="storefront", columns="plan", values="price_local")
US_PRICE = S.groupby("plan").us_price.first()
front = PRICE[FRONTIER]
front_med = front.median(axis=1).where(front.notna().sum(axis=1) >= 2)                 # median of the available plans, at least two


def vs_numeraire(plan, num, num_us):
    """(slope, HC1 s.e., n, LMIC median in percent) of ln(p_plan / p_num) - ln(P_plan,US / P_num,US) on ln(GNI)."""
    y = (np.log(PRICE[plan] / num) - math.log(US_PRICE[plan] / num_us)).dropna()
    m = META.loc[y.index]
    b, se, n = ols_hc1(np.log(m.gni.values), y.values)
    lm = y[m.income_group.isin(LMIC).values]
    return b, se, n, (100 * (math.exp(float(lm.median())) - 1) if len(lm) else NAN)


w10 = []
for firm, plan in CV_PLANS:
    if plan == "chatgpt_plus":
        bp = (NAN, NAN, 0, NAN)                                                       # a plan against itself
    else:
        bp = vs_numeraire(plan, PRICE["chatgpt_plus"], US_PRICE["chatgpt_plus"])
    bf = vs_numeraire(plan, front_med, FRONTIER_US)
    row = dict(firm=firm, plan=plan, label=LABEL[plan], us_price=float(US_PRICE[plan]),
               n_plus=bp[2], slope_plus=bp[0], se_plus=bp[1], lmic_pct_plus=bp[3],
               n_front=bf[2], slope_front=bf[0], se_front=bf[1], lmic_pct_front=bf[3],
               dev_slope=float(W1.dev_slope[plan]), dev_se=float(W1.dev_se[plan]))
    w10.append(row)
    put(f"relplus_{plan}", dict(slope=bp[0], se=bp[1], n=(bp[2] or None), lmic_pct=bp[3]))
    put(f"relfront_{plan}", dict(slope=bf[0], se=bf[1], n=bf[2], lmic_pct=bf[3]))
pd.DataFrame(w10).round(10).to_csv(TAB / "W10_cross_vendor.csv", index=False)

# ================================================================================================ (d) increment test
INCR = [   # key, label, high plan, low plan
    ("plus_go", "ChatGPT Plus $-$ Go", "chatgpt_plus", "chatgpt_go"),
    ("caiplus_lite", "Character.AI+ $-$ Lite", "characterai_plus", "characterai_lite"),
    ("aipro_aiplus", "Google AI Pro $-$ AI Plus", "gemini_pro", "gemini_plus"),
    ("pro200_plus", "ChatGPT Pro 200 $-$ Plus", "chatgpt_pro200", "chatgpt_plus"),
    ("m365prem_pers", "Microsoft 365 Premium $-$ Personal", "m365_premium", "m365_personal"),
]
GROUP_ORDER = [("High income", "hic"), ("Upper-middle income", "umic"), ("Lower-middle income", "lmic"), ("Low income", "lic")]
w12 = []
for key, lab, hi, lo in INCR:
    a, b = PVD[PVD.plan == hi].set_index("storefront"), PVD[PVD.plan == lo].set_index("storefront")
    sf = sorted(set(a.index) & set(b.index))
    a, b = a.loc[sf], b.loc[sf]
    ok = a.gni.gt(0) & ((a.price_local > b.price_local) & (a.default_ref > b.default_ref))
    inc = (a.price_local - b.price_local)[ok] / (a.default_ref - b.default_ref)[ok]        # increment relative to the default increment
    s1, se1, n1 = ols_hc1(np.log(a.gni[ok].values), np.log(inc.values))
    ok2 = a.gni.gt(0) & (a.price_usd > b.price_usd)
    inc2 = (a.price_usd - b.price_usd)[ok2] / (a.us_price - b.us_price)[ok2]               # US$ increment relative to the US increment
    s2, se2, n2 = ols_hc1(np.log(a.gni[ok2].values), np.log(inc2.values))
    med = {short: float(inc[a.income_group[ok] == g].median()) for g, short in GROUP_ORDER}
    w12.append(dict(pair=key, label=lab, high=hi, low=lo, n=n1, slope=s1, se=se1, med_hic=med["hic"], med_umic=med["umic"],
                    med_lmic=med["lmic"], med_lic=med["lic"], n_usd=n2, slope_usd=s2, se_usd=se2))
    put(f"incr_{key}", dict(slope=s1, se=se1, n=n1, med_hic=med["hic"], med_umic=med["umic"], med_lmic=med["lmic"], med_lic=med["lic"]))
    put(f"incrusd_{key}", dict(slope=s2, se=se2, n=n2))
pd.DataFrame(w12).round(10).to_csv(TAB / "W12_increment.csv", index=False)

# ================================================================================================ results and data dictionary
res = json.load(open(ROOT / "output" / "results_wave2.json"))
res.update({k: (round(v, 6) if isinstance(v, float) else v) for k, v in R.items()})
json.dump(res, open(ROOT / "output" / "results_wave2.json", "w"), indent=1)


def rows(file, frame, desc, source):
    return [dict(file=file, variable=c, description=desc[c], source=source.get(c, "derived"), non_missing=int(frame[c].notna().sum()))
            for c in frame.columns]


D_REL = {"pair": "Pair key (PAIRS in 13_relative_prices.py)", "firm": "Vendor of the two plans", "storefront": "App Store storefront code",
         "currency": "Storefront currency", "income_group": "World Bank income group FY2027", "gni": "GNI per capita, Atlas method, US$",
         "plan_a": "Plan key of plan A", "plan_b": "Plan key of plan B (the comparison plan)",
         "ratio_us_a": "Price in US$ of plan A in this storefront / its US price", "ratio_us_b": "The same for plan B",
         "ln_rel": "ln(ratio_us_a / ratio_us_b): price of A relative to B in this storefront, normalised by the same ratio in the US"}
SRC_R = {c: "derived; wave2_plan_rows.csv (Apple App Store, 16 Oct 2026)" for c in ["ratio_us_a", "ratio_us_b", "ln_rel", "plan_a", "plan_b", "pair", "firm"]}
SRC_R.update(storefront="Apple App Store, 16 Oct 2026", currency="Apple App Store, 16 Oct 2026", gni="World Bank WDI via country_panel.csv",
             income_group="World Bank FY2027 via country_panel.csv")
dpath = PROC / "wave2_data_dictionary.csv"
old = pd.read_csv(dpath, keep_default_na=False, na_values=[""])
new = pd.DataFrame(rows("wave2_relative_long.csv", long, D_REL, SRC_R))
pd.concat([old[old.file != "wave2_relative_long.csv"], new], ignore_index=True).to_csv(dpath, index=False)

print("pairs (slope, HC1, CR1, RI p):", "; ".join(f"{r['pair']} {r['slope']:.3f} ({r['se_hc1']:.3f}) [{r['se_cr1']:.3f}] p={r['ri_p']:.4f}" for r in w8.to_dict("records")))
print(f"stacked: N = {main['n_obs']}, {main['n_items']} items, {main['n_storefronts']} storefronts, {pick.shape[1]} relabellings; "
      + "; ".join(f"{g} {main['gamma'][k]:.3f} ({main['se'][k]:.3f}) RI p = {ri[k]:.4f}" for k, g in enumerate(GROUPS)))
print("cross-vendor (vs Plus / vs frontier median):", "; ".join(f"{r['plan']} {r['slope_plus']:.3f} / {r['slope_front']:.3f}" for r in w10))
print("increments:", "; ".join(f"{r['pair']} {r['slope']:.3f} ({r['se']:.3f}) N = {r['n']}, US$ {r['slope_usd']:.3f} ({r['se_usd']:.3f}) N = {r['n_usd']}" for r in w12))
