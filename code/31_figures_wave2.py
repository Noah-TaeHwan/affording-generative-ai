"""
31_figures_wave2.py -- figures of the second price wave (16 October 2026), English labels.

  fig_default_dev_en.pdf   Deviation of four plans from Apple's default price schedule (100 x log points) against GNI per
                           capita: ChatGPT Go, ChatGPT Plus, Google AI Pro, YouTube Premium.  Points by income group,
                           zero line = on the schedule, fitted line and HC1 slope of the deviation on ln(GNI).
  fig_benchmarks_en.pdf    Income slopes of the US-dollar price (+-1.96 s.e.) of the within-firm items of tab_benchmarks (19 items,
                           including Google AI Plus, SuperGrok Lite, YouTube Premium Lite and Microsoft 365 Family);
                           dashed line = slope of Apple's default schedule, dotted line = 0.10.
  fig_relative_en.pdf      Income slopes of the relative price of the 12 within-vendor pairs of tab_relative_pairs (plan A against plan B
                           of the same vendor in the same storefront, normalised by the US ratio), with +-1.96 currency-clustered
                           (CR1) standard errors, grouped by vendor; vertical line at 0 = the two plans are priced alike everywhere.

Reads data/processed/wave2_plan_vs_default.csv, output/tables/W2_benchmarks.csv, W4_default_schedule.csv, W8_relative_pairs.csv,
output/results_wave2.json (12_default_panel.py, 13_relative_prices.py), data/processed/wave2_plan_rows.csv and
data/raw/appstore_wave2/apps_v3.json (classes).  Style as 30_figures.py (Liberation Sans, hairline grids, ringed markers).
Like extensions/figure_rollout.py it writes the PDFs directly to paper_en/figures/ (so the `cp output/figures/*_en.pdf` line of
run_all.sh does not need to carry them) and PNG previews to output/figures/.
"""
import json, logging, pathlib
import numpy as np
import pandas as pd
logging.getLogger("fontTools").setLevel(logging.ERROR)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROC, TAB = ROOT / "data" / "processed", ROOT / "output" / "tables"
PDF, PNG = ROOT / "paper_en" / "figures", ROOT / "output" / "figures"
PDF.mkdir(parents=True, exist_ok=True)
PNG.mkdir(parents=True, exist_ok=True)
R = json.load(open(ROOT / "output" / "results_wave2.json"))

INK, INK2, MUTED, GRID, AXIS, SURF = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#ffffff"
S1, S2 = "#2a78d6", "#eb6834"
GROUPS = ["High income", "Upper-middle income", "Lower-middle income", "Low income"]
GCOL = {"High income": "#0d366b", "Upper-middle income": "#1c5cab", "Lower-middle income": "#3987e5", "Low income": "#86b6ef"}
GMRK = {"High income": "o", "Upper-middle income": "D", "Lower-middle income": "s", "Low income": "^"}
have = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams.update({
    "font.family": "Liberation Sans" if "Liberation Sans" in have else "DejaVu Sans", "font.size": 8.5,
    "axes.edgecolor": AXIS, "axes.linewidth": 0.6, "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED,
    "xtick.labelcolor": INK2, "ytick.labelcolor": INK2, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5,
    "grid.linestyle": "-", "axes.axisbelow": True, "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF, "axes.titlesize": 9.5,
    "axes.titleweight": "bold", "axes.titlecolor": INK, "axes.titlelocation": "left", "legend.fontsize": 8,
    "pdf.fonttype": 42, "axes.unicode_minus": False,
})


def save(fig, name):
    fig.savefig(PDF / f"{name}.pdf", bbox_inches="tight", metadata={"CreationDate": None})
    fig.savefig(PNG / f"{name}.png", dpi=220, bbox_inches="tight")
    plt.close(fig)
    print("wrote", PDF / f"{name}.pdf")


# ------------------------------------------------------------------------------------------ deviation from the schedule
def fig_default_dev():
    pv = pd.read_csv(PROC / "wave2_plan_vs_default.csv", keep_default_na=False, na_values=[""])
    w4 = pd.read_csv(TAB / "W4_default_schedule.csv", keep_default_na=False, na_values=[""]).set_index("plan")
    panels = [("chatgpt_go", "(a) ChatGPT Go"), ("chatgpt_plus", "(b) ChatGPT Plus"), ("gemini_pro", "(c) Google AI Pro"),
              ("youtube_premium", "(d) YouTube Premium (benchmark)")]
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.5), sharex=True, sharey=True)
    for ax, (plan, title) in zip(axes.ravel(), panels):
        s = pv[(pv.plan == plan) & pv.dev_log.notna() & pv.gni.notna()]
        for g in GROUPS[::-1]:
            z = s[s.income_group == g]
            ax.scatter(z.gni, 100 * z.dev_log, s=22, marker=GMRK[g], color=GCOL[g], edgecolor=SURF, linewidth=0.6, zorder=3)
        lx = np.log(s.gni)
        b, a = np.polyfit(lx, 100 * s.dev_log, 1)                        # intercept a, slope b in 100 x log points per log point
        xs = np.geomspace(s.gni.min(), s.gni.max(), 100)
        ax.plot(xs, a + b * np.log(xs), color=INK, lw=1.4, zorder=4)
        ax.axhline(0, color=MUTED, lw=1.0, zorder=2)
        r = w4.loc[plan]
        ax.text(0.97, 0.05, f"Slope {r.dev_slope:.3f} (s.e. {r.dev_se:.3f})\nN = {int(r.n)}", transform=ax.transAxes, ha="right",
                va="bottom", color=INK, fontsize=8, linespacing=1.4)
        ax.set_xscale("log")
        ax.set_xticks([500, 1000, 2000, 5000, 10000, 20000, 50000, 100000])
        ax.set_xticklabels(["500", "1k", "2k", "5k", "10k", "20k", "50k", "100k"])
        ax.minorticks_off()
        ax.set_xlim(380, 170000)
        ax.set_title(title)
    axes[0, 0].set_ylim(-250, 85)
    axes[0, 0].set_yticks([-240, -180, -120, -60, 0, 60])
    axes[0, 0].text(0.02, 0.775, "Default schedule", transform=axes[0, 0].transAxes, ha="left", va="bottom", color=INK2, fontsize=7.2)
    for ax in axes[:, 0]:
        ax.set_ylabel("100 × log(local price / schedule price)")
    fig.supxlabel("GNI per capita, Atlas method, 2025 (current US$, log scale)", fontsize=8.5, color=INK2, y=0.05)
    h = [Line2D([], [], marker=GMRK[g], color="none", markerfacecolor=GCOL[g], markeredgecolor=SURF, markersize=6.5, label=g) for g in GROUPS]
    fig.legend(handles=h, loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.005))
    fig.tight_layout(rect=(0, 0.075, 1, 1))
    save(fig, "fig_default_dev_en")


# ------------------------------------------------------------------------------------------ benchmark slopes
def fig_benchmarks():
    w2 = pd.read_csv(TAB / "W2_benchmarks.csv", keep_default_na=False, na_values=[""])
    fig, ax = plt.subplots(figsize=(7.2, 5.9 + 0.24 * max(0, len(w2) - 19)))
    y, ticks, labels, heads = 0.0, [], [], []
    firm = None
    for r in w2.itertuples():
        if r.firm != firm:
            y += 0.55 if firm is not None else 0.0
            heads.append((y, r.firm))
            y += 0.85
            firm = r.firm
        col, face, mk = GROUP_STYLE[r.group]
        ax.plot([r.slope - 1.96 * r.se, r.slope + 1.96 * r.se], [y, y], color=col, lw=1.6, solid_capstyle="butt", zorder=3)
        ax.scatter([r.slope], [y], s=44, marker=mk, facecolor=face, edgecolor=col, linewidth=1.6, zorder=4)
        ticks.append(y)
        labels.append(f"{r.product}  (US${r.us_price:,.2f})")
        y += 1.0
    ax.set_ylim(y - 0.3, -0.7)
    ax.set_yticks(ticks)
    ax.set_yticklabels(labels, fontsize=8)
    ax.tick_params(axis="y", length=0)
    for yy, name in heads:
        ax.text(-0.012, yy, name, transform=ax.get_yaxis_transform(), ha="right", va="center", color=INK, fontsize=8.5, fontweight="bold",
                clip_on=False)
    ax.grid(axis="y", visible=False)
    ds = R["default_slope"]
    ax.axvline(ds, color=INK2, lw=1.2, ls="--", zorder=2)
    ax.axvline(0.10, color=INK2, lw=1.2, ls=":", zorder=2)
    ax.axvline(0, color=AXIS, lw=0.8, zorder=1)
    top = ax.get_ylim()[1]
    ax.text(ds - 0.006, top + 0.15, f"Apple default\nschedule {ds:.3f}", ha="right", va="bottom", color=INK2, fontsize=7.6, linespacing=1.3)
    ax.text(0.10 + 0.006, top + 0.15, "0.10", ha="left", va="bottom", color=INK2, fontsize=7.6)
    ax.set_xlim(-0.1, 0.5)
    ax.set_xlabel("Income slope of the US-dollar price relative to the US price\n(HC1 regression of ln ratio on ln GNI per capita; bars ±1.96 s.e.)")
    h = [Line2D([], [], marker=mk, color=col, markerfacecolor=face, markeredgewidth=1.6, markersize=6.5, lw=1.6, label=GROUP_NAME[g][0].upper() + GROUP_NAME[g][1:])
         for g, (col, face, mk) in GROUP_STYLE.items() if (w2.group == g).any()]
    fig.legend(handles=h, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.01), columnspacing=1.3, handletextpad=0.5)
    fig.subplots_adjust(left=0.30, right=0.985, top=0.91 + 0.03 * (fig.get_figheight() > 6), bottom=0.17 * 5.9 / fig.get_figheight())
    save(fig, "fig_benchmarks_en")


# ------------------------------------------------------------------------------------------ relative prices within vendors
# product groups of the stacked regression (13_relative_prices.py) and of Table E.9; one style per group in Figures 1 and E.1
GROUP_NAME = {"frontier": "frontier AI tier", "capped": "capped AI tier", "smallai": "small AI allowance", "noai": "no AI allowance",
              "storage": "storage plan (no AI)", "capped_one": "capped AI tier (Google One app)", "family": "family variant",
              "creator": "creator subscription"}
GROUP_STYLE = {"frontier": (S1, S1, "o"), "capped": (S1, SURF, "o"), "smallai": (S2, SURF, "s"), "noai": (S2, S2, "s"),
               "storage": (INK2, SURF, "D"), "capped_one": (S1, SURF, "D"), "family": (S2, SURF, "^"), "creator": (INK2, SURF, "v")}


def fig_relative():
    w8 = pd.read_csv(TAB / "W8_relative_pairs.csv", keep_default_na=False, na_values=[""])
    fig, ax = plt.subplots(figsize=(7.2, 4.9 + 0.22 * max(0, len(w8) - 12)))
    y, ticks, labels, heads = 0.0, [], [], []
    firm = None
    for r in w8.itertuples():
        if r.firm != firm:
            y += 0.55 if firm is not None else 0.0
            heads.append((y, r.firm))
            y += 0.85
            firm = r.firm
        col, face, mk = GROUP_STYLE[r.group_a]
        ax.plot([r.slope - 1.96 * r.se_cr1, r.slope + 1.96 * r.se_cr1], [y, y], color=col, lw=1.6, solid_capstyle="butt", zorder=3)
        ax.scatter([r.slope], [y], s=44, marker=mk, facecolor=face, edgecolor=col, linewidth=1.6, zorder=4)
        ax.text(1.005, y, f"{r.slope:.3f}  (N = {int(r.n)})".replace("-", "−"), transform=ax.get_yaxis_transform(), ha="left", va="center",
                color=INK2, fontsize=7.6, clip_on=False)
        ticks.append(y)
        labels.append(r.label.replace("$\\times$", "×"))
        y += 1.0
    ax.set_ylim(y - 0.3, -0.7)
    ax.set_yticks(ticks)
    ax.set_yticklabels(labels, fontsize=8)
    ax.tick_params(axis="y", length=0)
    for yy, name in heads:
        ax.text(-0.012, yy, name, transform=ax.get_yaxis_transform(), ha="right", va="center", color=INK, fontsize=8.5, fontweight="bold",
                clip_on=False)
    ax.grid(axis="y", visible=False)
    ax.axvline(0, color=INK2, lw=1.2, zorder=2)
    ax.set_xlim(-0.08, 0.5)
    ax.set_xlabel("Income slope of the relative price A / B in the same storefront, normalised by the US ratio\n"
                  "(OLS of ln relative price on ln GNI per capita; bars ±1.96 currency-clustered s.e.)")
    h = [Line2D([], [], marker=mk, color=col, markerfacecolor=face, markeredgewidth=1.6, markersize=6.5, lw=1.6, label=f"A: {lab}")
         for g, (col, face, mk) in GROUP_STYLE.items() for lab in [GROUP_NAME[g]] if (w8.group_a == g).any()]
    fig.legend(handles=h, loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.01), columnspacing=1.3, handletextpad=0.5)
    fig.subplots_adjust(left=0.34, right=0.84, top=0.975, bottom=0.215 * 4.9 / fig.get_figheight())
    save(fig, "fig_relative_en")


fig_default_dev()
fig_benchmarks()
fig_relative()
