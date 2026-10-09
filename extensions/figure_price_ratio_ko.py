"""Figure 3, Korean labels: same-storefront ChatGPT Go/Plus price ratio (그림 3). No causal interpretation.

Same data, fit and layout as figure_price_ratio.py; only the labels are Korean. Korean text needs NanumGothic
(Debian/Ubuntu package fonts-nanum); other Korean fonts are used if it is missing, in which case the PDF is not
byte-identical to the shipped one.
"""
from pathlib import Path
import logging
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
logging.getLogger('fontTools').setLevel(logging.ERROR)  # quiet font-subsetting notices
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator

ROOT = Path(__file__).resolve().parent
SRC = ROOT.parent                      # package root
DEST = SRC / 'paper_ko/figures'        # PDF used by the Korean manuscript
PNG = SRC / 'output/figures'           # PNG preview, alongside the other figures
DEST.mkdir(exist_ok=True, parents=True); PNG.mkdir(exist_ok=True, parents=True)
d = pd.read_csv(SRC / 'data/processed/country_panel.csv', keep_default_na=False, na_values=[''])
s = d.dropna(subset=['gni_atlas', 'p_chatgpt_go', 'p_chatgpt_plus']).copy()
s['ratio'] = s.p_chatgpt_go / s.p_chatgpt_plus
b0, b1 = np.linalg.lstsq(np.column_stack([np.ones(len(s)), np.log(s.gni_atlas)]), np.log(s.ratio), rcond=None)[0]
have = {f.name for f in font_manager.fontManager.ttflist}
fonts = [f for f in ['NanumGothic', 'AppleGothic', 'Malgun Gothic', 'Noto Sans CJK KR', 'DejaVu Sans'] if f in have] or ['DejaVu Sans']
plt.rcParams.update({'font.family': fonts, 'font.size': 9, 'pdf.fonttype': 42, 'axes.unicode_minus': False,
    'axes.spines.top': False, 'axes.spines.right': False, 'axes.edgecolor': '#c3c2b7',
    'axes.labelcolor': '#52514e', 'xtick.color': '#52514e', 'ytick.color': '#52514e',
    'legend.frameon': False, 'axes.axisbelow': True})
fig, ax = plt.subplots(figsize=(7.2, 4.35))
groups = ['High income', 'Upper-middle income', 'Lower-middle income', 'Low income']
names = {'High income': '고소득국', 'Upper-middle income': '상위중소득국',
         'Lower-middle income': '하위중소득국', 'Low income': '저소득국'}
colors = ['#0d366b', '#1c5cab', '#3987e5', '#86b6ef']; marks = ['o', 'D', 's', '^']
for g, c, m in zip(groups, colors, marks):
    z = s[s.income_group == g]
    ax.scatter(z.gni_atlas, z.ratio, s=25, c=c, marker=m, label=names[g], edgecolors='white', linewidths=.5, alpha=.88)
x = np.geomspace(s.gni_atlas.min(), s.gni_atlas.max(), 300)
ax.plot(x, np.exp(b0 + b1 * np.log(x)), c='#202020', lw=1.5)
ax.set(xscale='log', yscale='log', ylim=(.1, 1), xlim=(350, 160000),
       xlabel='1인당 GNI, Atlas 방식 (현재 달러, 로그 척도)',
       ylabel='월 표시가격 비율: Go / Plus (로그 척도)')
ax.xaxis.set_major_locator(FixedLocator([500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]))
ax.xaxis.set_major_formatter(FixedFormatter(['500', '1k', '2k', '5k', '10k', '20k', '50k', '100k']))
ax.yaxis.set_major_locator(FixedLocator([.1, .2, .3, .5, 1]))
ax.yaxis.set_major_formatter(FixedFormatter(['0.1', '0.2', '0.3', '0.5', '1.0']))
ax.xaxis.set_minor_locator(NullLocator()); ax.yaxis.set_minor_locator(NullLocator())
ax.grid(axis='y', color='#e1e0d9', lw=.5)
ax.text(.02, .93, f'로그-로그 기울기 {b1:.3f}; 스토어 {len(s)}개', transform=ax.transAxes, va='top', fontsize=9)
ax.set_title('Plus 대비 ChatGPT Go 가격', loc='left', fontweight='bold', pad=26, fontsize=11)
ax.text(0, 1.035, '같은 스토어의 앱스토어 표시가격 · 2026년 9월 27일', transform=ax.transAxes, color='#52514e', fontsize=8.5)
ax.legend(loc='upper center', bbox_to_anchor=(.5, -.22), ncol=4, columnspacing=1, handletextpad=.3, fontsize=8)
fig.subplots_adjust(left=.11, right=.985, top=.82, bottom=.25)
fig.savefig(DEST / 'fig_price_ratio_ko.pdf', bbox_inches='tight', metadata={'CreationDate': None})  # no timestamp
fig.savefig(PNG / 'fig_price_ratio_ko.png', dpi=240, bbox_inches='tight')
print(DEST, 'n=', len(s), 'slope=', b1)
