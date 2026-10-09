"""Figure 6 (version 2.1): adoption around the first rollouts of ChatGPT Go. English and Korean labels.

Panel (a): Microsoft AI User Share, indexed to H1 2025 = 100, for India, Indonesia, the median of the sixteen Asian
economies with country-specific estimates (Cohort 2), and the median of all other country-specific economies.
Panel (b): Anthropic AI Usage Index, indexed to August 2025 = 100, same groups (published economies).
Vertical markers: India launch (19 Aug 2025), Cohort 2 (8 Oct 2025), worldwide (16 Jan 2026).
Reads extensions/audit_output/go_rollout_economy_detail.csv and the panel; writes
paper_en/figures/fig_rollout_en.pdf, paper_ko/figures/fig_rollout_ko.pdf and PNG previews in output/figures.
Usage: python extensions/figure_rollout.py [en|ko|both]
"""
from pathlib import Path
import logging
import sys
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
logging.getLogger("fontTools").setLevel(logging.ERROR)
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "extensions" / "audit_output"
spec = json.load(open(OUT / "go_rollout_spec.json"))
C1, C2 = spec["cohorts"]["C1"], spec["cohorts"]["C2"]
d = pd.read_csv(ROOT / "data/processed/country_panel.csv", keep_default_na=False, na_values=[""]).copy()
d["cohort"] = np.where(d.iso3.isin(C1), "C1", np.where(d.iso3.isin(C2), "C2", "other"))
cs = d[d.ms_country_specific.astype(str).str.lower().isin(["true", "1", "1.0"])]

INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
COL = {"India": "#eb6834", "Indonesia": "#c9a227", "C2": "#1c5cab", "other": "#898781"}
MS_COLS = ["ms_h1_2025", "ms_h2_2025", "ms_q1_2026", "ms_q2_2026"]
AUI_COLS = ["aui_aug25", "aui_nov25", "aui_feb26", "aui_apr26", "aui_may26"]
LAB = {
    "en": {"ta": "(a) Any generative-AI use (Microsoft AI User Share)", "tb": "(b) Per-capita Claude activity (Anthropic AUI)",
           "ya": "Index, H1 2025 = 100", "yb": "Index, August 2025 = 100",
           "ms_x": ["H1 2025", "H2 2025", "Q1 2026", "Q2 2026"], "aui_x": ["Aug 25", "Nov 25", "Feb 26", "Apr 26", "May 26"],
           "India": "India (Go from Aug 2025; free from Nov 2025)", "Indonesia": "Indonesia (Go from Sep 2025)",
           "C2": "Sixteen Asian economies, median (Go from 8 Oct 2025)", "other": "All other economies, median",
           "ev_ms": ["", "Go: India, Indonesia,\nAsian sixteen, 71 more", "Go worldwide\n(16 Jan)", ""],
           "ev_aui": ["", "", "", "", ""],
           "font": ["Liberation Sans", "DejaVu Sans"]},
    "ko": {"ta": "(a) 생성형 AI 이용 여부 (마이크로소프트 AI User Share)", "tb": "(b) 1인당 Claude 이용량 (Anthropic AUI)",
           "ya": "지수, 2025년 상반기 = 100", "yb": "지수, 2025년 8월 = 100",
           "ms_x": ["2025 상반기", "2025 하반기", "2026 1분기", "2026 2분기"], "aui_x": ["25년 8월", "25년 11월", "26년 2월", "26년 4월", "26년 5월"],
           "India": "인도 (2025년 8월 Go 출시; 11월부터 무료)", "Indonesia": "인도네시아 (2025년 9월 Go 출시)",
           "C2": "아시아 16개국 중위값 (2025년 10월 8일 Go 출시)", "other": "그 밖의 경제권 중위값",
           "ev_ms": ["", "Go: 인도, 인도네시아,\n아시아 16개국, 71개국", "Go 전 세계\n(1월 16일)", ""],
           "ev_aui": ["", "", "", "", ""],
           "font": ["NanumGothic", "Noto Sans CJK KR", "DejaVu Sans"]},
}


def series(frame, cols, iso=None, cohort=None):
    if iso:
        v = frame.loc[frame.iso3 == iso, cols].iloc[0].astype(float).values
    else:
        g = frame[frame.cohort == cohort][cols].dropna()
        v = g.median().values
    return v / v[0] * 100


def draw(lang):
    L = LAB[lang]
    have = {f.name for f in font_manager.fontManager.ttflist}
    fonts = [f for f in L["font"] if f in have] or ["DejaVu Sans"]
    plt.rcParams.update({"font.family": fonts, "font.size": 8.5, "axes.edgecolor": AXIS, "axes.linewidth": 0.6,
                         "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelcolor": INK2,
                         "ytick.labelcolor": INK2, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5,
                         "axes.axisbelow": True, "axes.spines.top": False, "axes.spines.right": False,
                         "legend.frameon": False, "axes.titlesize": 9.5, "axes.titleweight": "bold", "axes.titlecolor": INK,
                         "axes.titlelocation": "left", "legend.fontsize": 7.8, "pdf.fonttype": 42, "axes.unicode_minus": False})
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.3))
    for ax, cols, xl, title, ylab, frame, events in [
            (axes[0], MS_COLS, L["ms_x"], L["ta"], L["ya"], cs, L["ev_ms"]),
            (axes[1], AUI_COLS, L["aui_x"], L["tb"], L["yb"], d[d[AUI_COLS].notna().all(axis=1)], L["ev_aui"])]:
        x = np.arange(len(cols))
        for key, kw in [("other", dict(cohort="other")), ("C2", dict(cohort="C2")), ("Indonesia", dict(iso="IDN")), ("India", dict(iso="IND"))]:
            y = series(frame, cols, **kw)
            ax.plot(x, y, marker="o", ms=4, lw=1.8 if key in ("India", "C2") else 1.4, color=COL[key], label=L[key],
                    markeredgecolor="white", markeredgewidth=0.6, ls="-" if key != "other" else "--")
        ax.set_xticks(x); ax.set_xticklabels(xl)
        ax.set_title(title); ax.set_ylabel(ylab)
        ax.grid(axis="x", visible=False)
        for i, txt in enumerate(events):
            if txt:
                ax.annotate(txt, xy=(i, ax.get_ylim()[0]), xytext=(0, 4), textcoords="offset points", fontsize=6.6,
                            color=INK2, ha="center", va="bottom")
    axes[1].set_ylim(50, max(axes[1].get_ylim()[1], 160))
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h[::-1], l[::-1], loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.06), columnspacing=1.4, handletextpad=0.5)
    fig.subplots_adjust(left=0.075, right=0.99, top=0.9, bottom=0.26, wspace=0.28)
    dest = ROOT / f"paper_{lang}/figures/fig_rollout_{lang}.pdf"
    fig.savefig(dest, bbox_inches="tight", metadata={"CreationDate": None})
    fig.savefig(ROOT / f"output/figures/fig_rollout_{lang}.png", dpi=240, bbox_inches="tight")
    plt.close(fig)
    print("wrote", dest)


which = sys.argv[1] if len(sys.argv) > 1 else "both"
for lang in (["en", "ko"] if which == "both" else [which]):
    draw(lang)
