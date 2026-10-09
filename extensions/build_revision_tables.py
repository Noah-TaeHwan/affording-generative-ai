"""Rebuild the six revised numerical LaTeX table bodies from frozen data.

Run from any working directory:
    python extensions/build_revision_tables.py
    python extensions/build_revision_tables.py --check

Run audit_extensions.py first to regenerate the audit CSVs. This script never
edits manuscript prose, original analysis tables, Korean files or source data.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
AUDIT = HERE / 'audit_output'
TABLES = ROOT / 'paper_en/tables'
GROUPS = ['High income', 'Upper-middle income', 'Lower-middle income', 'Low income']
END = r' \\'


def read_csv(path):
    return pd.read_csv(path, keep_default_na=False, na_values=[''])


def table_rows(rows):
    # Deliberately preserve the manuscript's current newline/rounding conventions.
    return '\n'.join(' & '.join(row) + END for row in rows)


def construct_tables():
    countries = read_csv(ROOT / 'data/processed/country_panel.csv')
    countries = countries[countries.gni_atlas.gt(0)].copy()
    tables = {}

    # Compute country ratios before taking medians. Ratios of group-median income
    # need not be the median of individual ratios in an even-sized group.
    rows = []
    for group in GROUPS:
        s = countries[countries.income_group == group]
        burden = {fee: (1200 * fee / s.gni_atlas).median() for fee in [8, 20, 100, 200]}
        rows.append([group, str(len(s)), f'{burden[8]:,.2f}',
            r'\textbf{' + f'{burden[20]:,.2f}' + '}', f'{burden[100]:,.2f}',
            f'{burden[200]:,.2f}', f'{(24000/s.hfce_pc).median():,.2f}',
            f'{(24000/s.gni_ppp).median():,.2f}'])
    tables['tab_burden_compact.tex'] = table_rows(rows)

    # Synthetic quintile scales preserve the original construction. Broadband
    # columns use their own available samples, not the quintile-data subsample.
    rows = []
    for group in GROUPS:
        s = countries[countries.income_group == group]
        q = s[s.q1_share.notna()]
        vals = [(24000 / (q.gni_atlas * q[f'q{k}_share'] / 20)).median() for k in [1, 3, 5]]
        broadband = s[s.mbb_2gb_pct_gni_latest_official.notna()]
        rows.append([group, str(len(q))] + [f'{x:,.1f}' for x in vals] + [
            f'{broadband.mbb_2gb_pct_gni_latest_official.median():,.2f}',
            f'{(20/broadband.mbb_2gb_usd_2024).median():,.1f}'])
    tables['tab_quintile.tex'] = table_rows(rows)

    threshold = read_csv(AUDIT / 'burden_threshold_sensitivity.csv')
    threshold = threshold[(threshold['sample'] == 'Latest 2022-2025') &
                          (threshold.monthly_price_usd == 20)].sort_values('threshold_pct')
    rows = [[f'{r.threshold_pct:.0f}' + r'\%', str(int(r.n_above)),
             f'{100*r.country_share_above:.1f}' + r'\%',
             f'{100*r.covered_working_age_share_above:.1f}' + r'\%']
            for r in threshold.itertuples()]
    tables['tab_thresholds.tex'] = table_rows(rows)

    prices = read_csv(AUDIT / 'local_price_robustness.csv').set_index('plan')
    names = [('chatgpt_go', 'ChatGPT Go'), ('chatgpt_plus', 'ChatGPT Plus'),
             ('claude_pro', 'Claude Pro'), ('gemini_pro', 'Google AI Pro')]
    rows = []
    for key, name in names:
        r = prices.loc[key]
        ci_digits = 4 if key == 'chatgpt_plus' else 3
        rows.append([name, f'{r.beta:.3f}', f'{r.se_HC3:.3f}', f'{r.se_currency_cluster:.3f}',
                     f'[{r.cluster_t_ci_low:.{ci_digits}f}, {r.cluster_t_ci_high:.{ci_digits}f}]', str(int(r.n))])
    ratios = read_csv(AUDIT / 'within_storefront_price_ratios.csv').set_index('comparison')
    r = ratios.loc['ChatGPT Go / Plus']
    rows.append(['Go / Plus ratio', f'{r.slope:.3f}', f'{r.se_HC3:.3f}', f'{r.se_currency_cluster:.3f}',
                 f'[{r.cluster_t_ci_low:.3f}, {r.cluster_t_ci_high:.3f}]', str(int(r.n))])
    tables['tab_price_revision.tex'] = table_rows(rows)

    gaps = read_csv(AUDIT / 'cross_provider_gradient_robustness.csv')
    gaps = gaps[gaps.specification != 'Exclude China and Russia']
    rows = []
    for r in gaps.itertuples():
        name = r.specification.replace('Working-age-population weighted (different estimand)', 'Population weighted')
        rows.append([name, f'{r.difference:.3f}', f'{r.difference_HC3_SE:.3f}',
                     f'[{r.difference_ci_low:.3f}, {r.difference_ci_high:.3f}]', str(int(r.n))])
    tables['tab_gap_revision.tex'] = table_rows(rows)

    # The September 29 fee is a U.S. web observation. These columns are common-fee
    # scenarios on the frozen national-income sample, not a new local-price audit.
    rows, scenario = [], []
    for group in GROUPS:
        s = countries[countries.income_group == group]
        vals = [(1200 * fee / s.gni_atlas).median() for fee in [20, 200, 500]]
        rows.append([group, str(len(s))] + [f'{x:.2f}' for x in vals])
        scenario.append(dict(income_group=group, n=len(s), burden20=vals[0], burden200=vals[1], burden500=vals[2]))
    tables['tab_500_scenario.tex'] = table_rows(rows)
    return tables, pd.DataFrame(scenario)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Compare without changing table or scenario files; exit 1 on a difference.')
    args = parser.parse_args()
    tables, scenario = construct_tables()
    report = []
    for name, content in tables.items():
        path = TABLES / name
        expected = content.encode('utf-8')
        current = path.read_bytes() if path.exists() else None
        match = current == expected
        report.append({'file':str(path.relative_to(ROOT)), 'matches_before_write':match,
                       'sha256_generated':hashlib.sha256(expected).hexdigest()})
        if not args.check:
            path.write_bytes(expected)
    scenario_path = AUDIT / 'pro500_reference_scenario.csv'
    scenario_expected = scenario.to_csv(index=False).encode('utf-8')
    scenario_match = scenario_path.exists() and scenario_path.read_bytes() == scenario_expected
    if not args.check:
        scenario_path.write_bytes(scenario_expected)
    record = {'mode':'check' if args.check else 'write','tables':report,
              'all_tables_match_before_write':all(r['matches_before_write'] for r in report),
              'scenario_csv_matches_before_write':scenario_match,
              'source_files':['data/processed/country_panel.csv',
                  'extensions/audit_output/burden_threshold_sensitivity.csv',
                  'extensions/audit_output/local_price_robustness.csv',
                  'extensions/audit_output/within_storefront_price_ratios.csv',
                  'extensions/audit_output/cross_provider_gradient_robustness.csv']}
    (AUDIT / 'revision_table_verification.json').write_text(json.dumps(record,indent=2))
    print(json.dumps(record,indent=2))
    if args.check and (not record['all_tables_match_before_write'] or not scenario_match):
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
