"""
30_figures.py -- paper figures (English and Korean labels), vector PDF + PNG.
Visual rules: ordinal blue ramp for the (ordered) World Bank income groups with redundant marker shapes;
two-series comparisons use categorical slots 1-2; hairline solid grids; 2px lines; ringed markers.
"""
import json, pathlib, sys
import numpy as np
import pandas as pd
import logging
logging.getLogger("fontTools").setLevel(logging.ERROR)  # quiet font-subsetting notices
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe
import statsmodels.formula.api as smf

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROC, FIG = ROOT / "data" / "processed", ROOT / "output" / "figures"
FIG.mkdir(parents=True, exist_ok=True)
R = json.load(open(ROOT / "output" / "results.json"))

INK, INK2, MUTED, GRID, AXIS, SURF = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#ffffff"
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"
GROUPS = ["HIC", "UMIC", "LMIC", "LIC"]
GCOL = {"HIC": "#0d366b", "UMIC": "#1c5cab", "LMIC": "#3987e5", "LIC": "#86b6ef"}
GMRK = {"HIC": "o", "UMIC": "D", "LMIC": "s", "LIC": "^"}
plt.rcParams.update({
    "font.family": "Liberation Sans", "font.size": 8.5, "axes.edgecolor": AXIS, "axes.linewidth": 0.6,
    "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelcolor": INK2,
    "ytick.labelcolor": INK2, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5, "grid.linestyle": "-",
    "axes.axisbelow": True, "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF, "axes.titlesize": 9.5,
    "axes.titleweight": "bold", "axes.titlecolor": INK, "axes.titlelocation": "left", "legend.fontsize": 8,
    "pdf.fonttype": 42,
})

L = {
    "en": {
        "grp": {"HIC": "High income", "UMIC": "Upper-middle income", "LMIC": "Lower-middle income",
                "LIC": "Low income"},
        "gni": "GNI per capita, Atlas method, 2025 (current US$, log scale)",
        "f1_ta": "(a) $20 tier: local App Store price", "f1_tb": "(b) Entry tier: local App Store price",
        "f1_y": "Monthly price (US$, log scale)",
        "us_ref": "US list price", "ppp_ref": "PPP-indexed price (slope {b:.2f})",
        "fit": "Fitted slope {b:.2f}", "plus": "ChatGPT Plus", "claude": "Claude Pro", "gpro": "Google AI Pro",
        "go": "ChatGPT Go", "gplus": "Google AI Plus",
        "f2_x": "Annual cost of a $20/month plan as % of mean income (log scale)",
        "q1": "Poorest 20%", "avg": "Average (GNI per capita)", "q5": "Richest 20%",
        "bench": "2% affordability benchmark", "f2_note": "Median across economies; quintile incomes from survey shares",
        "f3_y": "Log deviation from cross-country mean", "ms": "Any generative-AI use (Microsoft AI User Share), slope {b:.2f}",
        "aui": "Per-capita Claude usage (Anthropic AUI), slope {b:.2f}",
        "f4_ta": "(a) Median AI user share by income group",
        "f4_tb": "(b) Gain, H1 2025 to Q2 2026", "f4_y": "Share of population aged 15-64 (%)",
        "f4_yb": "Change (percentage points)",
        "periods": ["H1 2025", "H2 2025", "Q1 2026", "Q2 2026"],
        "f5_x": "Log gap in AI user share relative to the high-income group (difference in mean logs)",
        "connect": "Connectivity (internet use)", "cond": "AI-use-to-internet-use ratio",
        "f6_x": "Illustrative gain in aggregate output (% of GDP)", "cur": "Current adoption",
        "hic_ad": "If adoption matched high-income level", "rng": "Task-level gain 10-30% (dot: 20%)",
        "n_note": "n = {n}",
    },
    "ko": {
        "grp": {"HIC": "고소득국", "UMIC": "상위중소득국", "LMIC": "하위중소득국", "LIC": "저소득국"},
        "gni": "1인당 GNI, Atlas 방식, 2025년 (현재 달러, 로그 척도)",
        "f1_ta": "(a) 20달러 요금제: 현지 앱스토어 가격", "f1_tb": "(b) 입문 요금제: 현지 앱스토어 가격",
        "f1_y": "월 가격 (달러, 로그 척도)",
        "us_ref": "미국 표시가격", "ppp_ref": "PPP 연동 가격 (기울기 {b:.2f})",
        "fit": "추정 기울기 {b:.2f}", "plus": "ChatGPT Plus", "claude": "Claude Pro", "gpro": "Google AI Pro",
        "go": "ChatGPT Go", "gplus": "Google AI Plus",
        "f2_x": "월 20달러 요금제의 연간 비용 / 평균소득 (%, 로그 척도)",
        "q1": "하위 20%", "avg": "평균 (1인당 GNI)", "q5": "상위 20%",
        "bench": "2% 적정부담 기준", "f2_note": "국가 중위값, 분위 소득은 가계조사 소득점유율로 근사",
        "f3_y": "국가 간 평균 대비 로그 편차", "ms": "생성형 AI 이용 여부 (Microsoft AI User Share), 기울기 {b:.2f}",
        "aui": "1인당 Claude 이용량 (Anthropic AUI), 기울기 {b:.2f}",
        "f4_ta": "(a) 소득집단별 AI 이용자 비중 중위값",
        "f4_tb": "(b) 증가폭, 2025년 상반기→2026년 2분기", "f4_y": "15-64세 인구 대비 비중 (%)",
        "f4_yb": "변화 (%포인트)",
        "periods": ["2025 상반기", "2025 하반기", "2026 1분기", "2026 2분기"],
        "f5_x": "고소득국 대비 AI 이용 비중의 로그 격차(집단별 로그 평균의 차이)",
        "connect": "연결성 (인터넷 이용)", "cond": "AI 이용자/인터넷 이용자 비율",
        "f6_x": "총산출 증가 시나리오 (GDP 대비 %)", "cur": "현재 채택률",
        "hic_ad": "고소득국 채택률 적용 시", "rng": "과업 단위 생산성 10-30% (점: 20%)",
        "n_note": "n = {n}",
    },
}

df = pd.read_csv(PROC / "country_panel.csv", keep_default_na=False, na_values=[""]).copy()  # keep ISO2 "NA" = Namibia; .copy() consolidates
SH = {"High income": "HIC", "Upper-middle income": "UMIC", "Lower-middle income": "LMIC", "Low income": "LIC"}
df["grp"] = df.income_group.map(SH)
lp = pd.read_csv(PROC / "appstore_prices_long.csv", keep_default_na=False, na_values=[""])
df["storefront"] = df.iso2.str.lower()
lp = lp.merge(df[["storefront", "iso3", "gni_atlas", "grp"]], on="storefront").dropna(subset=["gni_atlas"])


# TrueType fonts embed cleanly in PDF (Type 42); DejaVu Sans is the fallback for any missing glyph.
# Korean labels need NanumGothic (Debian/Ubuntu package fonts-nanum).
FONT = {"en": ["Liberation Sans", "Arial", "Helvetica", "DejaVu Sans"],
        "ko": ["NanumGothic", "AppleGothic", "Malgun Gothic", "Noto Sans CJK KR", "DejaVu Sans"]}
from matplotlib import font_manager
_HAVE = {f.name for f in font_manager.fontManager.ttflist}


def fonts(lang):
    """First available families from FONT[lang] (the figures in the paper use the first entry)."""
    return [f for f in FONT[lang] if f in _HAVE] or ["DejaVu Sans"]


def save(fig, name):
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight", metadata={"CreationDate": None})
    fig.savefig(FIG / f"{name}.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def logx_money(ax):
    ax.set_xscale("log")
    ax.set_xticks([500, 1000, 2000, 5000, 10000, 20000, 50000, 100000])
    ax.set_xticklabels(["500", "1k", "2k", "5k", "10k", "20k", "50k", "100k"])
    ax.minorticks_off()


def group_legend(lang, ax, loc="lower right"):
    h = [Line2D([], [], marker=GMRK[g], color="none", markerfacecolor=GCOL[g], markeredgecolor=SURF,
                markersize=6.5, label=L[lang]["grp"][g]) for g in GROUPS]
    return h


# ------------------------------------------------------------------------------------------ Figure: localisation
def fig_prices(lang):
    t = L[lang]
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.1), sharey=True)
    xs = np.array([400, 150000])
    for ax, plans, title, us in [(axes[0], [("chatgpt_plus", "plus")], t["f1_ta"], 19.99),
                                 (axes[1], [("chatgpt_go", "go")], t["f1_tb"], 8.00)]:
        for plan, key in plans:
            s = lp[lp.plan == plan]
            for g in GROUPS[::-1]:
                ss = s[s.grp == g]
                ax.scatter(ss.gni_atlas, ss.price_usd, s=26, marker=GMRK[g], color=GCOL[g], edgecolor=SURF,
                           linewidth=0.7, zorder=3)
            b = R[f"loc_{plan}_b"]
            fit = smf.ols("np.log(price_usd) ~ np.log(gni_atlas)", s).fit()
            ax.plot(xs, np.exp(fit.params.iloc[0]) * xs ** fit.params.iloc[1], color=INK, lw=1.4, zorder=4)
            pos = (0.97, 0.05, "right", "bottom") if plan == "chatgpt_plus" else (0.03, 0.95, "left", "top")
            ax.text(pos[0], pos[1], t["fit"].format(b=b) + f" (SE {R[f'loc_{plan}_se']:.3f})", transform=ax.transAxes,
                    ha=pos[2], va=pos[3], color=INK, fontsize=8)
        ax.axhline(us, color=MUTED, lw=1.0, zorder=2)
        # PPP-indexed benchmark anchored at the US: p_c = p_US * (GNI_c/GNI_US)^b_ppp
        bp = R["plr_b"]; gus = float(df.loc[df.iso3 == "USA", "gni_atlas"].iloc[0])
        ax.plot(xs, us * (xs / gus) ** bp, color=S2, lw=1.4, zorder=2)
        ax.text(420, us * 0.955, t["us_ref"], color=INK2, fontsize=7.5, va="top", zorder=5,
                path_effects=[pe.withStroke(linewidth=2.5, foreground=SURF)])  # halo keeps the label legible over markers
        ax.text(560, us * (560 / gus) ** bp * 0.93, t["ppp_ref"].format(b=bp), color=INK2, fontsize=7.5, va="top")
        logx_money(ax); ax.set_yscale("log"); ax.set_title(title)
        ax.set_xlim(380, 160000)
    axes[0].set_yticks([2, 3, 5, 8, 10, 20, 30]); axes[0].set_yticklabels(["2", "3", "5", "8", "10", "20", "30"])
    axes[0].set_ylim(1.8, 36); axes[0].set_ylabel(t["f1_y"])
    fig.supxlabel(t["gni"], fontsize=8.5, color=INK2, y=0.0)
    fig.legend(handles=group_legend(lang, axes[0]), loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.08))
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    save(fig, f"fig_prices_{lang}")


# ------------------------------------------------------------------------------------------ Figure: burden by quintile
def fig_burden(lang):
    t = L[lang]
    fig, ax = plt.subplots(figsize=(6.2, 2.5))
    ys = np.arange(len(GROUPS))[::-1]
    for y, g in zip(ys, GROUPS):
        q1, av, q5 = R[f"aab20_q1_{g}"], R[f"aab_p20_{g}"], R[f"aab20_q5_{g}"]
        ax.plot([q5, q1], [y, y], color=GRID, lw=5, solid_capstyle="round", zorder=1)
        ax.scatter([q5], [y], s=46, marker="o", color=SURF, edgecolor=S1, linewidth=1.6, zorder=3)
        ax.scatter([av], [y], s=46, marker="D", color=INK2, edgecolor=SURF, linewidth=0.8, zorder=3)
        ax.scatter([q1], [y], s=46, marker="o", color=S1, edgecolor=SURF, linewidth=0.8, zorder=3)
        for v, dy in [(q1, 0.25), (q5, 0.25)]:
            ax.text(v, y + dy, f"{v:.1f}%" if v < 10 else f"{v:.0f}%", ha="center", va="bottom", fontsize=7.5,
                    color=INK2)
    ax.axvline(2, color=S2, lw=1.2, zorder=1.5)
    ax.text(2.1, ys[0] + 0.55, t["bench"], color=INK2, fontsize=7.5, va="bottom")
    ax.set_yticks(ys); ax.set_yticklabels([t["grp"][g] for g in GROUPS]); ax.tick_params(axis="y", length=0)
    ax.set_xscale("log"); ax.set_xlim(0.2, 120)
    ax.set_xticks([0.25, 0.5, 1, 2, 5, 10, 20, 50, 100]); ax.set_xticklabels(["0.25", "0.5", "1", "2", "5", "10", "20", "50", "100"])
    ax.minorticks_off(); ax.set_ylim(-0.6, len(GROUPS) - 0.1); ax.grid(axis="y", visible=False)
    ax.set_xlabel(t["f2_x"])
    h = [Line2D([], [], marker="o", color="none", markerfacecolor=S1, markeredgecolor=SURF, markersize=6.5, label=t["q1"]),
         Line2D([], [], marker="D", color="none", markerfacecolor=INK2, markeredgecolor=SURF, markersize=6, label=t["avg"]),
         Line2D([], [], marker="o", color="none", markerfacecolor=SURF, markeredgecolor=S1, markeredgewidth=1.4,
                markersize=6.5, label=t["q5"])]
    ax.legend(handles=h, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.45))
    save(fig, f"fig_burden_{lang}")


# ------------------------------------------------------------------------------------------ Figure: two margins
def fig_two_margins(lang):
    t = L[lang]
    b = pd.read_csv(ROOT / "output" / "tables" / "D1_two_margins_sample.csv")
    b["ln_ms"] = np.log(b.ms_q2_2026 / 100); b["ln_aui"] = np.log(b.aui_may26)
    b["y_ms"] = b.ln_ms - b.ln_ms.mean(); b["y_aui"] = b.ln_aui - b.ln_aui.mean()
    fig, ax = plt.subplots(figsize=(6.2, 3.3))
    xs = np.linspace(b.gni_atlas.min() * 0.9, b.gni_atlas.max() * 1.1, 50)
    for y, col, lab, key in [("y_ms", S1, t["ms"], "tm_ms_b"), ("y_aui", S2, t["aui"], "tm_aui_b")]:
        ax.scatter(b.gni_atlas, b[y], s=20, color=col, edgecolor=SURF, linewidth=0.6, alpha=0.9, zorder=3)
        fit = np.polyfit(np.log(b.gni_atlas), b[y], 1)
        ax.plot(xs, fit[1] + fit[0] * np.log(xs), color=col, lw=2, zorder=4, label=lab.format(b=R[key]))
    logx_money(ax); ax.set_xlim(900, 140000)
    ax.set_ylabel(t["f3_y"]); ax.set_xlabel(t["gni"])
    ax.axhline(0, color=AXIS, lw=0.6)
    ax.legend(loc="upper left")
    ax.text(0.99, 0.02, t["n_note"].format(n=R["n_two_margins"]), transform=ax.transAxes, ha="right", va="bottom",
            color=MUTED, fontsize=7.5)
    save(fig, f"fig_two_margins_{lang}")


# ------------------------------------------------------------------------------------------ Figure: dynamics
def fig_dynamics(lang):
    t = L[lang]
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.9), gridspec_kw={"width_ratios": [1, 1.15]})
    ax = axes[0]
    per = ["ms_h1_2025", "ms_h2_2025", "ms_q1_2026", "ms_q2_2026"]
    x = np.arange(4)
    for g in GROUPS:
        y = [R[f"{p}_median_cs_{g}"] for p in per]
        ax.plot(x, y, color=GCOL[g], lw=2, marker=GMRK[g], markersize=5, markeredgecolor=SURF, zorder=3)
        ax.text(3.12, y[-1], f"{y[-1]:.1f}", va="center", fontsize=7.5, color=INK2)
    ax.set_xticks(x); ax.set_xticklabels(t["periods"], fontsize=7.5); ax.set_xlim(-0.2, 3.55)
    ax.set_ylim(0, 36); ax.set_ylabel(t["f4_y"]); ax.set_title(t["f4_ta"], fontsize=8.8)
    ax.grid(axis="x", visible=False)
    ax2 = axes[1]
    m = df[(df.ms_region_imputed == 0) & df.ms_q2_2026.notna() & df.gni_atlas.notna()].copy()
    m["gain"] = m.ms_q2_2026 - m.ms_h1_2025
    for g in GROUPS[::-1]:
        s = m[m.grp == g]
        ax2.scatter(s.gni_atlas, s.gain, s=24, marker=GMRK[g], color=GCOL[g], edgecolor=SURF, linewidth=0.7, zorder=3)
    xs = np.linspace(m.gni_atlas.min() * 0.9, m.gni_atlas.max() * 1.1, 50)
    ax2.plot(xs, np.polyval(np.polyfit(np.log(m.gni_atlas), m.gain, 1), np.log(xs)), color=INK, lw=1.4)
    ax2.text(0.03, 0.95, t["fit"].format(b=R["conv_pp_b"]) + " pp / log", transform=ax2.transAxes, va="top",
             fontsize=7.5, color=INK)
    logx_money(ax2); ax2.set_xlim(500, 140000); ax2.set_ylabel(t["f4_yb"]); ax2.set_title(t["f4_tb"], fontsize=8.8)
    ax2.set_xlabel(t["gni"], fontsize=7.5)
    fig.legend(handles=group_legend(lang, ax), loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.1))
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    save(fig, f"fig_dynamics_{lang}")


# ------------------------------------------------------------------------------------------ Figure: decomposition
def fig_decomp(lang):
    t = L[lang]
    tab = pd.read_csv(ROOT / "output" / "tables" / "C3_connectivity_decomposition.csv")
    tab = tab[tab.group != "HIC"].set_index("group").loc[["UMIC", "LMIC", "LIC"]]
    fig, ax = plt.subplots(figsize=(6.2, 1.9))
    ys = np.arange(3)[::-1]
    for y, (g, r) in zip(ys, tab.iterrows()):
        c, a = r.loggap_connect, r.loggap_conditional
        ax.barh(y, c, height=0.42, color=S1, edgecolor=SURF, linewidth=1.5)
        ax.barh(y, a, left=c, height=0.42, color=S2, edgecolor=SURF, linewidth=1.5)
        ax.text(c + a - 0.03, y, f"{r.loggap_total:.2f}", ha="right", va="center", fontsize=7.5, color=INK2)
        ax.text(0.02, y, t["n_note"].format(n=int(r.n)), ha="left", va="center", fontsize=7, color=MUTED)
    ax.set_yticks(ys); ax.set_yticklabels([t["grp"][g] for g in tab.index]); ax.tick_params(axis="y", length=0)
    ax.axvline(0, color=AXIS, lw=0.8); ax.set_xlim(-1.55, 0.25); ax.grid(axis="y", visible=False)
    ax.set_xlabel(t["f5_x"])
    h = [plt.Rectangle((0, 0), 1, 1, color=S1, label=t["connect"]), plt.Rectangle((0, 0), 1, 1, color=S2, label=t["cond"])]
    ax.legend(handles=h, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.62))
    save(fig, f"fig_decomp_{lang}")


# ------------------------------------------------------------------------------------------ Figure: scenarios
def fig_scen(lang):
    t = L[lang]
    tab = pd.read_csv(ROOT / "output" / "tables" / "E1_scenarios.csv")
    fig, ax = plt.subplots(figsize=(6.2, 2.3))
    ys = np.arange(4)[::-1]
    for y, g in zip(ys, GROUPS):
        s = tab[tab.group == g].set_index("g_task")
        for col, off, fc, ec in [("hulten", 0.12, S1, SURF), ("hulten_if_HIC_adoption", -0.12, SURF, S1)]:
            lo, mid, hi = s.loc[0.1, col] * 100, s.loc[0.2, col] * 100, s.loc[0.3, col] * 100
            if g == "HIC" and col != "hulten":
                continue
            ax.plot([lo, hi], [y + off, y + off], color=S1 if col == "hulten" else AXIS, lw=2, zorder=2,
                    solid_capstyle="round")
            ax.scatter([mid], [y + off], s=40, color=fc, edgecolor=ec if col != "hulten" else SURF,
                       linewidth=1.4 if col != "hulten" else 0.8, zorder=3)
            ax.text(hi + 0.03, y + off, f"{mid:.2f}", va="center", fontsize=7.2, color=INK2)
    ax.set_yticks(ys); ax.set_yticklabels([t["grp"][g] for g in GROUPS]); ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 2.0); ax.grid(axis="y", visible=False); ax.set_xlabel(t["f6_x"])
    h = [Line2D([], [], marker="o", color=S1, lw=2, markerfacecolor=S1, markeredgecolor=SURF, markersize=6, label=t["cur"]),
         Line2D([], [], marker="o", color=AXIS, lw=2, markerfacecolor=SURF, markeredgecolor=S1, markeredgewidth=1.4,
                markersize=6, label=t["hic_ad"])]
    ax.legend(handles=h, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.5))
    save(fig, f"fig_scen_{lang}")


if __name__ == "__main__":
    for lang in ["en", "ko"]:
        plt.rcParams["font.family"] = fonts(lang)
        fig_prices(lang); fig_burden(lang); fig_two_margins(lang); fig_dynamics(lang); fig_decomp(lang); fig_scen(lang)
    print("figures written:", sorted(p.name for p in FIG.glob("*.png")))
