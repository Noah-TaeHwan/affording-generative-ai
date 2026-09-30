"""Independent audit and descriptive robustness extensions for Oh (2026), v1.8.

Run: python audit_extensions.py
Uses frozen files from the downloaded Zenodo package. Does not modify originals.
All inference is conditional on provider point estimates; their uncertainty is unavailable.
"""
from pathlib import Path
import json, hashlib, sys
import numpy as np
import pandas as pd
import scipy
from scipy import stats
import statsmodels
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parent
SRC = ROOT.parent if (ROOT.parent/'data/processed/country_panel.csv').exists() else ROOT/'original'/'affording-genai-replication'
OUT = ROOT/'audit_output'
OUT.mkdir(exist_ok=True)
rd = lambda p: pd.read_csv(p, keep_default_na=False, na_values=[''])
d = rd(SRC/'data/processed/country_panel.csv')
p = rd(SRC/'data/processed/appstore_prices_long.csv')
baseline_path = ROOT/'baseline_results_v1.8.json'
reported = json.load(open(baseline_path if baseline_path.exists() else SRC/'output/results.json'))
results = {'environment': {'python':sys.version,'numpy':np.__version__,'pandas':pd.__version__,
    'scipy':scipy.__version__,'statsmodels':statsmodels.__version__}}

def independent_hc3(x,y):
    x,y=np.asarray(x,float),np.asarray(y,float)
    X=np.column_stack([np.ones(len(x)),x]); inv=np.linalg.inv(X.T@X)
    b=inv@X.T@y; e=y-X@b
    h=np.einsum('ij,jk,ik->i',X,inv,X)
    meat=X.T@(X*((e/(1-h))**2)[:,None])
    se=np.sqrt(np.diag(inv@meat@inv))
    return {'b':float(b[1]),'se':float(se[1]),'n':len(x)}

checks=[]
for group,short in [('High income','HIC'),('Upper-middle income','UMIC'),('Lower-middle income','LMIC'),('Low income','LIC')]:
    value=float((24000/d.loc[d.income_group==group,'gni_atlas']).median())
    key=f'aab_p20_{short}'
    checks.append({'key':key,'computed':value,'reported':reported[key],'pass_6dp':round(value,6)==reported[key]})
g=d[d.gni_atlas.notna()]
value=float(g.loc[24000/g.gni_atlas>2,'pop1564'].sum()/g.pop1564.sum())
checks.append({'key':'share_wapop_aab20_gt2','computed':value,'reported':reported['share_wapop_aab20_gt2'],
               'pass_6dp':round(value,6)==reported['share_wapop_aab20_gt2']})
ms=d[(d.ms_country_specific==1)&d.gni_atlas.notna()].copy()
ms['ln_ms']=np.log(ms.ms_q2_2026/100)
both=ms[ms.aui_may26.notna()&(ms.aui_may26>0)].copy()
both['ln_aui']=np.log(both.aui_may26)
for prefix,s,y in [('ms_log_cs',ms,'ln_ms'),('tm_ms',both,'ln_ms'),('tm_aui',both,'ln_aui')]:
    fit=independent_hc3(s.ln_gni,s[y])
    for k in ['b','se','n']:
        key=f'{prefix}_{k}'
        checks.append({'key':key,'computed':fit[k],'reported':reported[key],'pass_6dp':round(fit[k],6)==reported[key]})
pd.DataFrame(checks).to_csv(OUT/'independent_headline_checks.csv',index=False)
results['headline_checks_all_pass']=all(x['pass_6dp'] for x in checks)

# Exact decomposition and age-base caveat. The clipping in the original arithmetic
# means never binds; its regression decomposition is already calculated unclipped.
c=ms.dropna(subset=['internet_pct']).copy()
ratio=c.ms_q2_2026/c.internet_pct
results['connectivity_ratio']={'n':len(c),'n_above_one':int((ratio>1).sum()),'max_ratio':float(ratio.max()),
    'max_identity_error':float(np.abs(np.log(c.ms_q2_2026/100)-np.log(c.internet_pct/100)-np.log(ratio)).max())}

# Table 5: account for shared currency-level shocks. Use G-1 t degrees of freedom.
cm=d[['iso3','iso2','gni_atlas','gni_atlas_year','income_group']].copy()
cm['storefront']=cm.iso2.str.lower()
lp=p.merge(cm,on='storefront',how='inner').dropna(subset=['gni_atlas','price_usd'])
lp=lp[(lp.gni_atlas>0)&(lp.price_usd>0)].copy()
lp['ln_p']=np.log(lp.price_usd);lp['ln_gni']=np.log(lp.gni_atlas)
plans=['chatgpt_go','gemini_plus','chatgpt_plus','claude_pro','gemini_pro','chatgpt_pro5x','claude_max5x','chatgpt_pro20x','gemini_ultra']
rows=[]
for plan in plans:
    a=lp[lp.plan==plan].copy()
    hc=smf.ols('ln_p ~ ln_gni',a).fit(cov_type='HC3')
    cl=smf.ols('ln_p ~ ln_gni',a).fit(cov_type='cluster',cov_kwds={'groups':a.currency},use_t=True)
    new=a[a.gni_atlas_year==2025]
    fit25=smf.ols('ln_p ~ ln_gni',new).fit(cov_type='HC3')
    fe=smf.ols('ln_p ~ ln_gni + C(currency)',a).fit(cov_type='cluster',cov_kwds={'groups':a.currency},use_t=True)
    lo,hi=cl.conf_int().loc['ln_gni']
    rows.append({'plan':plan,'n':len(a),'currency_clusters':a.currency.nunique(),'beta':hc.params.ln_gni,
                 'se_HC3':hc.bse.ln_gni,'se_currency_cluster':cl.bse.ln_gni,'cluster_t_p':cl.pvalues.ln_gni,
                 'cluster_t_ci_low':lo,'cluster_t_ci_high':hi,'n_2025':len(new),'beta_2025':fit25.params.ln_gni,
                 'se_2025_HC3':fit25.bse.ln_gni,'beta_currency_FE':fe.params.ln_gni,'se_currency_FE_cluster':fe.bse.ln_gni})
pd.DataFrame(rows).to_csv(OUT/'local_price_robustness.csv',index=False)

# Match PPP-price-level benchmark to each plan's observed-price estimation sample.
pl=lp.merge(d[['iso3','gni_ppp']],on='iso3').dropna(subset=['gni_ppp']).copy()
pl['ln_plr']=np.log(pl.gni_atlas/pl.gni_ppp)
pl['ln_price_relative_plr']=pl.ln_p-pl.ln_plr
pr=[]
for plan in plans:
    a=pl[pl.plan==plan]
    f=smf.ols('ln_plr ~ ln_gni',a).fit(cov_type='HC3')
    obs=smf.ols('ln_p ~ ln_gni',a).fit(cov_type='HC3')
    dif=smf.ols('ln_price_relative_plr ~ ln_gni',a).fit(cov_type='HC3')
    pr.append({'plan':plan,'n':len(a),'observed_beta':obs.params.ln_gni,'ppp_same_sample_beta':f.params.ln_gni,
        'ppp_se_HC3':f.bse.ln_gni,'observed_minus_ppp':dif.params.ln_gni,'difference_se_HC3':dif.bse.ln_gni,
        'observed_fraction_of_ppp':obs.params.ln_gni/f.params.ln_gni})
pd.DataFrame(pr).to_csv(OUT/'same_sample_ppp_comparison.csv',index=False)

# Within-storefront relative prices cancel common FX and proportional sales tax,
# if the tax applies equally to both plans; this remains descriptive menu pricing.
wide=lp.pivot(index='iso3',columns='plan',values='price_usd').join(d.set_index('iso3')[['ln_gni','gni_atlas_year','store_currency']])
rr=[]
for label,num,den in [('ChatGPT Go / Plus','chatgpt_go','chatgpt_plus'),('Google Plus / Pro','gemini_plus','gemini_pro'),
                       ('ChatGPT Pro 5x / Plus','chatgpt_pro5x','chatgpt_plus')]:
    a=wide.dropna(subset=[num,den,'ln_gni','store_currency']).copy()
    a['log_ratio']=np.log(a[num]/a[den])
    hc=smf.ols('log_ratio ~ ln_gni',a).fit(cov_type='HC3')
    cl=smf.ols('log_ratio ~ ln_gni',a).fit(cov_type='cluster',cov_kwds={'groups':a.store_currency},use_t=True)
    lo,hi=cl.conf_int().loc['ln_gni']
    rr.append({'comparison':label,'n':len(a),'currency_clusters':a.store_currency.nunique(),'slope':hc.params.ln_gni,
               'se_HC3':hc.bse.ln_gni,'se_currency_cluster':cl.bse.ln_gni,'cluster_t_ci_low':lo,'cluster_t_ci_high':hi,
               'cluster_t_p':cl.pvalues.ln_gni})
pd.DataFrame(rr).to_csv(OUT/'within_storefront_price_ratios.csv',index=False)

# Recast the cross-provider gradient gap as log vendor conversations per any-AI
# user (up to global scale), rather than paid adoption or within-user intensity.
both['log_vendor_per_anyuser']=both.ln_aui-both.ln_ms
rows=[]
specs=[('Baseline',both,''),('2025 GNI only',both[both.gni_atlas_year==2025],''),
       ('Non-high-income',both[both.income_group!='High income'],''),
       ('Region fixed effects',both,' + C(region)'),
       ('Internet, education, urbanisation',both.dropna(subset=['internet_pct','tertiary_enrol','urban_pct']),
        ' + internet_pct + tertiary_enrol + urban_pct'),
       ('Exclude China and Russia',both[~both.iso3.isin(['CHN','RUS'])],'')]
for label,a,ctl in specs:
    fits={y:smf.ols(y+' ~ ln_gni'+ctl,a).fit(cov_type='HC3') for y in ['ln_ms','ln_aui','log_vendor_per_anyuser']}
    f=fits['log_vendor_per_anyuser'];lo,hi=f.conf_int().loc['ln_gni']
    rows.append({'specification':label,'n':len(a),'any_use_slope':fits['ln_ms'].params.ln_gni,
                 'vendor_use_slope':fits['ln_aui'].params.ln_gni,'difference':f.params.ln_gni,'difference_HC3_SE':f.bse.ln_gni,
                 'difference_ci_low':lo,'difference_ci_high':hi})
# Population weighting changes the target; report explicitly as a separate estimand.
a=both.dropna(subset=['pop1564'])
fits={y:smf.wls(y+' ~ ln_gni',a,weights=a.pop1564).fit(cov_type='HC3') for y in ['ln_ms','ln_aui','log_vendor_per_anyuser']}
f=fits['log_vendor_per_anyuser'];lo,hi=f.conf_int().loc['ln_gni']
rows.append({'specification':'Working-age-population weighted (different estimand)','n':len(a),
             'any_use_slope':fits['ln_ms'].params.ln_gni,'vendor_use_slope':fits['ln_aui'].params.ln_gni,
             'difference':f.params.ln_gni,'difference_HC3_SE':f.bse.ln_gni,'difference_ci_low':lo,'difference_ci_high':hi})
pd.DataFrame(rows).to_csv(OUT/'cross_provider_gradient_robustness.csv',index=False)
loo=[]
for i in both.index:
    a=both.drop(i)
    fit=independent_hc3(a.ln_gni,a.log_vendor_per_anyuser)
    loo.append({'excluded_iso3':both.loc[i,'iso3'],'gradient_gap':fit['b']})
pd.DataFrame(loo).to_csv(OUT/'gradient_gap_leave_one_out.csv',index=False)
results['gradient_gap_leave_one_out']={'min':min(x['gradient_gap'] for x in loo),'max':max(x['gradient_gap'] for x in loo)}

# Burden sensitivity: use only same-vintage 2025 income and multiple thresholds.
br=[]
for sample,a in [('Latest 2022-2025',g),('2025 only',g[g.gni_atlas_year==2025])]:
    for threshold in [1,2,5,10]:
        for price in [5,8,20,100,200]:
            high=1200*price/a.gni_atlas>threshold
            br.append({'sample':sample,'monthly_price_usd':price,'threshold_pct':threshold,'n':len(a),
                       'n_above':int(high.sum()),'country_share_above':float(high.mean()),
                       'covered_working_age_share_above':float(a.loc[high,'pop1564'].sum()/a.pop1564.sum())})
pd.DataFrame(br).to_csv(OUT/'burden_threshold_sensitivity.csv',index=False)
bg=[]
for group,a in g.groupby('income_group'):
    for sample,b in [('Latest 2022-2025',a),('2025 only',a[a.gni_atlas_year==2025])]:
        bg.append({'income_group':group,'sample':sample,'n':len(b),'median_burden20':float((24000/b.gni_atlas).median())})
pd.DataFrame(bg).to_csv(OUT/'burden_vintage_sensitivity.csv',index=False)

# A ratio of burden percentages with different income denominators is not a ratio
# of dollar prices. Correct the interpretation using the supplied USD basket costs.
bb=d[d.gni_atlas.notna() & d.mbb_2gb_pct_gni_latest_official.notna()].copy()
bb['mixed_denominator_ratio']=(24000/bb.gni_atlas)/bb.mbb_2gb_pct_gni_latest_official
bb['dollar_ratio_2024_2gb']=20/bb.mbb_2gb_usd_2024
bb['dollar_ratio_2025_5gb']=20/bb.mbb_5gb_usd_2025
bb.groupby('income_group').agg(n=('iso3','size'),
    old_mixeddenominator_burden_ratio=('mixed_denominator_ratio','median'),
    actual_dollar_price_ratio2024_2gb=('dollar_ratio_2024_2gb','median'),
    actual_dollar_price_ratio2025_5gb=('dollar_ratio_2025_5gb','median')).to_csv(OUT/'broadband_price_comparison.csv')

upstream_record=ROOT/'upstream_validation/upstream_verification.json'
upstream_validated=upstream_record.exists() and json.load(open(upstream_record)).get('all_checks_pass',False)
results['source_access']={'zenodo_record':23006366,'package_size_bytes':4449098,
                        'package_md5':'399295b8c6aefc9a4c2bea8790893872',
                        'checksum_scope':'Size and MD5 verified on archive retrieved for audit; constants record that retrieval, not a fresh download at script runtime.',
                        'full_upstream_anthropic_itu_reconstruction':upstream_validated,
                        'note':'Anthropic/ITU upstream validation was performed separately; see upstream_validation/upstream_verification.json. This script itself uses the bundled extracts. App Store HTML and WDI upstream re-extraction were not verified.'}
results['vintage']={'n_gni':len(g),'n_gni_2025':int((g.gni_atlas_year==2025).sum()),
    'gni_atlas_ppp_year_mismatch':int(((d.gni_atlas_year!=d.gni_ppp_year)&d.gni_atlas_year.notna()&d.gni_ppp_year.notna()).sum())}
json.dump(results,open(OUT/'audit_results.json','w'),indent=2)
print(json.dumps(results,indent=2))
print('\nLOCAL PRICES\n',pd.read_csv(OUT/'local_price_robustness.csv').to_string(index=False))
print('\nWITHIN STOREFRONT RATIOS\n',pd.DataFrame(rr).to_string(index=False))
print('\nCROSS PROVIDER ROBUSTNESS\n',pd.DataFrame(rows).to_string(index=False))
