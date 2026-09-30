"""
40_tables_tex.py -- LaTeX table bodies (English / Korean) generated from output/tables and output/results.json,
so that every number in the manuscripts is produced by code. Writes paper_en/tables/*.tex, paper_ko/tables/*.tex.
"""
import json, pathlib
import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
TAB = ROOT / "output" / "tables"
R = json.load(open(ROOT / "output" / "results.json"))
G = ["HIC", "UMIC", "LMIC", "LIC"]
LAB = {"en": {"HIC": "High income", "UMIC": "Upper-middle income", "LMIC": "Lower-middle income", "LIC": "Low income"},
       "ko": {"HIC": "고소득국", "UMIC": "상위중소득국", "LMIC": "하위중소득국", "LIC": "저소득국"}}


def f(x, d=2):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "--"
    return f"{x:,.{d}f}"


def pct(x, d=0):
    return f"{100 * x:.{d}f}"


def write(lang, name, body):
    p = ROOT / f"paper_{lang}" / "tables"
    p.mkdir(parents=True, exist_ok=True)
    (p / f"{name}.tex").write_text(body)


def se(x):
    return f"({x:.3f})"


for lang in ["en", "ko"]:
    L = LAB[lang]
    # ---------------------------------------------------------------- Table: burden by income group
    A = pd.read_csv(TAB / "A1_burden_by_group.csv").set_index("group")
    rows = []
    for g in G:
        r = A.loc[g]
        rows.append(f"{L[g]} & {int(r.n)} & {f(r.median_gni, 0)} & {f(r.aab_p8)} & \\textbf{{{f(r.aab_p20)}}} & "
                    f"{f(r.aab_p60)} & {f(r.aab_p100)} & {f(r.aab_p200)} & {f(r.aab_p300)} & "
                    f"{pct(R[f'share_meets2pct_p20_{g}'])} & {f(r.aabhh_p20)} & {f(r.aabppp_p20)} \\\\")
    write(lang, "tab_burden", "\n".join(rows))
    # ---------------------------------------------------------------- Table: quintile burdens
    Q = pd.read_csv(TAB / "A2_burden_by_quintile.csv").set_index("group")
    rows = [f"{L[g]} & {int(Q.loc[g].n)} & {f(Q.loc[g].aab20_q1, 1)} & {f(Q.loc[g].aab20_q3, 1)} & "
            f"{f(Q.loc[g].aab20_q5, 1)} & {f(R[f'mbb_{g}'], 2)} & {f(R[f'ai_over_mbb_{g}'], 1)} \\\\" for g in G]
    write(lang, "tab_quintile", "\n".join(rows))
    # ---------------------------------------------------------------- Table: local prices
    B = pd.read_csv(TAB / "B1_localization.csv").set_index("plan")
    names = {"chatgpt_go": "ChatGPT Go", "gemini_plus": "Google AI Plus", "chatgpt_plus": "ChatGPT Plus",
             "claude_pro": "Claude Pro", "gemini_pro": "Google AI Pro", "chatgpt_pro5x": "ChatGPT Pro 5x",
             "claude_max5x": "Claude Max 5x", "chatgpt_pro20x": "ChatGPT Pro 20x", "gemini_ultra": "Google AI Ultra"}
    rows = []
    for plan in ["chatgpt_go", "gemini_plus", "chatgpt_plus", "claude_pro", "gemini_pro", "chatgpt_pro5x",
                 "claude_max5x", "chatgpt_pro20x", "gemini_ultra"]:
        r = B.loc[plan]
        rows.append(f"{names[plan]} & {f(r.us_price)} & {f(r.median_HIC)} & {f(r.median_UMIC)} & {f(r.median_LMIC)} & "
                    f"{f(r.median_LIC)} & {r.beta_ln_gni:.3f} & {se(r.se)} & {int(r.n)} \\\\")
        if plan in ("gemini_plus", "gemini_pro", "claude_max5x"):
            rows.append("\\addlinespace")
    write(lang, "tab_local", "\n".join(rows))
    rows = []
    for g in G:
        rows.append(f"{L[g]} & {R[f'n_store_{g}']} & {pct(R[f'store_local_chatgpt_{g}'])} & {pct(R[f'store_none_{g}'])} & "
                    f"{pct(R[f'store_notoffered_{g}'])} & {pct(R[f'store_usd_{g}'])} & {f(R[f'cheapest_price_{g}'])} & "
                    f"{f(R[f'laab_cheapest_{g}'])} & {f(R[f'laab_chatgpt_plus_{g}'])} \\\\")
    write(lang, "tab_store", "\n".join(rows))
    # ---------------------------------------------------------------- Table: diffusion gradients
    cols = [("ms_lev_cs", "lev"), ("ms_log_cs", "log"), ("ms_log_all", "log"), ("ms_log_collapsed", "log"),
            ("ms_c1", "log"), ("ms_c4", "log"), ("ms_c5", "log")]
    b = " & ".join(f"{R[c + '_b']:.3f}" for c, _ in cols)
    s = " & ".join(se(R[c + "_se"]) for c, _ in cols)
    n = " & ".join(str(R[c + "_n"]) for c, _ in cols)
    r2 = " & ".join(f"{R[c + '_r2']:.2f}" for c, _ in cols)
    lab = {"en": ["ln GNI per capita", "", "Controls", "Region fixed effects", "Sample", "Observations", "$R^2$"],
           "ko": ["ln 1인당 GNI", "", "통제변수", "지역 고정효과", "표본", "관측치", "$R^2$"]}[lang]
    yes, no = ("Yes", "No") if lang == "en" else ("예", "아니오")
    smp = {"en": ["CS", "CS", "All", "Coll.", "CS$^\\dagger$", "CS$^\\dagger$", "CS$^\\dagger$"],
           "ko": ["국가별", "국가별", "전체", "합침", "국가별$^\\dagger$", "국가별$^\\dagger$", "국가별$^\\dagger$"]}[lang]
    body = (f"{lab[0]} & {b} \\\\\n & {s} \\\\\n\\addlinespace\n"
            f"{lab[2]} & {no} & {no} & {no} & {no} & {no} & {yes} & {yes} \\\\\n"
            f"{lab[3]} & {no} & {no} & {no} & {no} & {no} & {no} & {yes} \\\\\n"
            f"{lab[4]} & {' & '.join(smp)} \\\\\n{lab[5]} & {n} \\\\\n{lab[6]} & {r2} \\\\")
    write(lang, "tab_diffusion", body)
    # ---------------------------------------------------------------- Table: two margins
    specs = [("tm_ms", "tm_aui", {"en": "Baseline: country-specific MS, Q2 2026 vs AUI, May 2026",
                                   "ko": "기준: 국가별 MS 2026년 2분기 vs AUI 2026년 5월"}),
             ("tm_logit_ms", "tm_aui", {"en": "MS in log-odds (ceiling check)", "ko": "MS 로그오즈 변환 (상한 효과 점검)"}),
             ("tm_ms_nonhic", "tm_aui_nonhic", {"en": "Excluding high-income economies", "ko": "고소득국 제외"}),
             ("tm_ms_ctl", "tm_aui_ctl", {"en": "Conditional on internet use, tertiary enrolment, urbanisation",
                                          "ko": "인터넷 이용·고등교육 등록률·도시화 통제"}),
             ("tm_ms_2025", "tm_aui_2025", {"en": "Earlier windows: MS H2 2025 vs AUI Aug 2025",
                                            "ko": "이전 시점: MS 2025년 하반기 vs AUI 2025년 8월"}),
             ("tm_ms_allms", "tm_aui_allms", {"en": "Including region-imputed MS values",
                                              "ko": "지역 대체값 포함"})]
    rows = []
    for a, bb, lab_ in specs:
        rows.append(f"{lab_[lang]} & {R[a + '_b']:.3f} {se(R[a + '_se'])} & {R[bb + '_b']:.3f} {se(R[bb + '_se'])} & "
                    f"{R[a + '_n']} \\\\")
    rows.append("\\addlinespace")
    dlab = {"en": "Difference in baseline elasticities (AUI $-$ MS)", "ko": "기준 탄력성 차이 (AUI $-$ MS)"}[lang]
    bt = "bootstrap 95\\% CI" if lang == "en" else "부트스트랩 95\\% 구간"
    rows.append(f"{dlab} & \\multicolumn{{2}}{{c}}{{{R['tm_diff_b']:.3f} {se(R['tm_diff_se'])}; "
                f"{bt} [{R['tm_diff_boot_lo']:.2f}, {R['tm_diff_boot_hi']:.2f}]}} & {R['tm_ms_n']} \\\\")
    write(lang, "tab_twomargins", "\n".join(rows))
    # AUI over time
    wl = {"en": {"aug25": "Aug 2025", "nov25": "Nov 2025", "feb26": "Feb 2026", "apr26": "Apr 2026", "may26": "May 2026"},
          "ko": {"aug25": "2025년 8월", "nov25": "2025년 11월", "feb26": "2026년 2월", "apr26": "2026년 4월", "may26": "2026년 5월"}}[lang]
    rows = [f"{wl[w]} & {R[f'aui_{w}_b']:.3f} & {se(R[f'aui_{w}_se'])} & {R[f'aui_{w}_n']} & {R[f'aui_{w}_r2']:.2f} & "
            f"{R[f'aui_common_{w}_b']:.3f} & {se(R[f'aui_common_{w}_se'])} \\\\"
            for w in ["aug25", "nov25", "feb26", "apr26", "may26"]]
    write(lang, "tab_aui_time", "\n".join(rows))
    # ---------------------------------------------------------------- Table: decomposition
    C = pd.read_csv(TAB / "C3_connectivity_decomposition.csv").set_index("group")
    rows = []
    for g in G:
        r = C.loc[g]
        sh = "--" if g == "HIC" else f"{100 * r.share_connect:.0f}"
        rows.append(f"{L[g]} & {int(r.n)} & {f(r.mean_ms, 1)} & {f(r.mean_internet, 1)} & {f(100 * r.mean_ai_among_online, 1)} & "
                    f"{f(r.loggap_total)} & {f(r.loggap_connect)} & {f(r.loggap_conditional)} & {sh} \\\\")
    write(lang, "tab_decomp", "\n".join(rows))
    # ---------------------------------------------------------------- Table: scenarios
    E = pd.read_csv(TAB / "E1_scenarios.csv")
    rows = []
    for g in G:
        s = E[E.group == g].set_index("g_task")
        rows.append(f"{L[g]} & {100 * s.loc[0.1].E_exposed:.0f} & {100 * s.loc[0.1].a_adoption:.1f} & "
                    f"{100 * s.loc[0.2].naive_a_g:.2f} & {100 * s.loc[0.1].hulten:.2f} & \\textbf{{{100 * s.loc[0.2].hulten:.2f}}} & "
                    f"{100 * s.loc[0.3].hulten:.2f} & {100 * s.loc[0.2].hulten_if_HIC_adoption:.2f} \\\\")
    write(lang, "tab_scen", "\n".join(rows))
    # ---------------------------------------------------------------- Appendix: case countries
    T = pd.read_csv(TAB / "T1_case_countries.csv")
    kon = {"USA": "미국", "KOR": "한국", "AUS": "호주", "SGP": "싱가포르", "DEU": "독일", "CHL": "칠레", "CHN": "중국",
           "BRA": "브라질", "MEX": "멕시코", "THA": "태국", "ZAF": "남아프리카공화국", "COL": "콜롬비아", "IND": "인도",
           "KEN": "케냐", "NGA": "나이지리아", "BGD": "방글라데시", "GHA": "가나", "MAR": "모로코", "UGA": "우간다",
           "RWA": "르완다", "MWI": "말라위", "MOZ": "모잠비크", "MDG": "마다가스카르", "NER": "니제르"}
    ens = {"Korea, Rep.": "Korea, Rep."}
    st = {"en": {"local_storefront": "", "no_local_storefront": "no store", "app_not_offered": "not offered"},
          "ko": {"local_storefront": "", "no_local_storefront": "스토어 없음", "app_not_offered": "미제공"}}[lang]
    rows = []
    prev = None
    for _, r in T.iterrows():
        if prev is not None and r.grp != prev:
            rows.append("\\addlinespace")
        prev = r.grp
        name = kon[r.iso3] if lang == "ko" else r.country_wb
        ms = f"{r.ms_q2_2026:.1f}" + ("$^{\\ddagger}$" if r.ms_region_imputed == 1 else "")
        cur = r.store_currency if isinstance(r.store_currency, str) else st[r.store_status]
        rows.append(f"{name} & {r.grp} & {f(r.gni_atlas, 0)} & {f(r.aab20)} & {f(r.chatgpt_plus)} & {f(r.laab_plus)} & "
                    f"{f(r.chatgpt_go)} & {cur} & {ms} & {f(r.aui_may26)} \\\\")
    write(lang, "tab_case", "\n".join(rows))
    # ---------------------------------------------------------------- Appendix: controls
    C2 = pd.read_csv(TAB / "C2_conditional_gradients.csv").set_index("spec")
    names_c = {"en": {"internet_pct": "Internet users (\\%)", "tertiary_enrol": "Tertiary enrolment (\\% gross)",
                      "urban_pct": "Urban population (\\%)", "age65_pct": "Population 65+ (\\%)",
                      "fx_online_merchant_pay": "Paid online merchant digitally (\\%)"},
               "ko": {"internet_pct": "인터넷 이용자 (\\%)", "tertiary_enrol": "고등교육 총등록률 (\\%)",
                      "urban_pct": "도시인구 비중 (\\%)", "age65_pct": "65세 이상 인구 (\\%)",
                      "fx_online_merchant_pay": "온라인 디지털 결제 경험 (\\%)"}}[lang]
    rows = []
    for v in ["ln_gni", "internet_pct", "tertiary_enrol", "urban_pct", "age65_pct", "fx_online_merchant_pay"]:
        nm = lab[0] if v == "ln_gni" else names_c[v]
        vals = " & ".join(f"{C2.loc[k, v]:.4f}" if (v in C2.columns and pd.notna(C2.loc[k, v])) else "" for k in
                          ["c1", "c2", "c3", "c4", "c5"])
        ses = " & ".join(se(C2.loc[k, v + "_se"]) if (v + "_se" in C2.columns and pd.notna(C2.loc[k, v + "_se"])) else ""
                         for k in ["c1", "c2", "c3", "c4", "c5"])
        rows.append(f"{nm} & {vals} \\\\\n & {ses} \\\\")
    rows.append("\\addlinespace")
    rows.append(f"{lab[3]} & {no} & {no} & {no} & {no} & {yes} \\\\")
    rows.append(f"{lab[5]} & " + " & ".join(str(int(C2.loc[k, 'n'])) for k in ["c1", "c2", "c3", "c4", "c5"]) + " \\\\")
    rows.append(f"$R^2$ & " + " & ".join(f"{C2.loc[k, 'r2']:.2f}" for k in ["c1", "c2", "c3", "c4", "c5"]) + " \\\\")
    write(lang, "tab_controls", "\n".join(rows))
print("tables written")
