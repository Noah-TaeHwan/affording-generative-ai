"""Compare regenerated source-derived files and independently verify May AUI.

Run in original workspace, or supply --package-root, --raw-root, --reconstruction-root.
Does not fetch sources or mutate originals. Raw inputs must have recorded SHA256s.
"""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
import pandas as pd

p=argparse.ArgumentParser()
here=Path(__file__).resolve().parent
p.add_argument('--package-root',type=Path,default=here.parent/'original/affording-genai-replication')
p.add_argument('--raw-root',type=Path,default=here)
p.add_argument('--reconstruction-root',type=Path,default=here/'reconstruction')
p.add_argument('--out-dir',type=Path,default=here)
args=p.parse_args();args.out_dir.mkdir(exist_ok=True,parents=True)
rd=lambda f:pd.read_csv(f,keep_default_na=False,na_values=[''])
results={'scope':'Anthropic country outputs for all five windows and ITU workbook reconstruction. App Store HTML and World Bank upstream extraction are outside this check.'}
comparisons=[]
for file in ['anthropic/anthropic_country_latest.csv','anthropic/anthropic_country_latest_wide.csv',
             'anthropic/anthropic_country_panel.csv','anthropic/anthropic_gdp_elasticity_replication.csv',
             'itu/itu_price_baskets_long.csv','itu/itu_affordability_latest.csv']:
    original=args.package_root/'data/raw'/file
    rebuilt=args.reconstruction_root/'data/raw'/file
    a,b=rd(original),rd(rebuilt)
    status='match'
    try:pd.testing.assert_frame_equal(a,b,check_dtype=False,check_exact=False,rtol=1e-12,atol=1e-12)
    except AssertionError as e:status=str(e)
    numeric=[]
    if a.shape==b.shape:
        for c in a.select_dtypes(include='number').columns:
            if c in b and pd.api.types.is_numeric_dtype(b[c]):
                z=np.abs(a[c].to_numpy()-b[c].to_numpy())
                if np.isfinite(z).any():numeric.append(float(np.nanmax(z)))
    comparisons.append({'file':file,'rows_original':len(a),'rows_rebuilt':len(b),
        'columns':len(a.columns),'comparison':status,'max_numeric_difference':max(numeric,default=0),
        'byte_identical':original.read_bytes()==rebuilt.read_bytes()})
results['regenerated_files']=comparisons

# Independently select published country AUI rows from full raw CSV, without
# invoking author's construction functions or relying on derived country files.
raw=args.raw_root/'aei_claude_ai_2026-06-26.csv'
selected=[]
for chunk in pd.read_csv(raw,keep_default_na=False,na_values=[''],chunksize=100000):
    s=chunk[(chunk.geo_level=='country')&(chunk.category_name=='overall')&
            (chunk.metric_id=='usage_per_capita_index')&(chunk.date_start=='2026-05-01')]
    selected.append(s[['geo_id','value']])
a=pd.concat(selected).rename(columns={'geo_id':'iso3','value':'upstream_may_aui'})
d=rd(args.package_root/'data/processed/country_panel.csv')
joined=d[['iso3','aui_may26','ln_gni','ms_q2_2026','ms_country_specific']].merge(a,on='iso3',how='outer')
both=joined.dropna(subset=['aui_may26','upstream_may_aui'])
results['independent_may_AUI']={'published_country_rows':len(a),'matched_WB_country_rows':len(both),
    'processed_nonmissing':int(joined.aui_may26.notna().sum()),
    'max_absolute_difference':float((both.aui_may26-both.upstream_may_aui).abs().max()),
    'raw_only_iso3':joined.loc[joined.aui_may26.isna()&joined.upstream_may_aui.notna(),'iso3'].tolist()}
s=both[(both.ms_country_specific==1)&both.ln_gni.notna()&both.ms_q2_2026.notna()&(both.upstream_may_aui>0)]
X=np.column_stack([np.ones(len(s)),s.ln_gni]);y=np.log(s.upstream_may_aui)
b=np.linalg.lstsq(X,y,rcond=None)[0];inv=np.linalg.inv(X.T@X);e=np.asarray(y)-X@b
h=np.einsum('ij,jk,ik->i',X,inv,X);cov=inv@(X.T@(X*((e/(1-h))**2)[:,None]))@inv
results['independent_primary_regression_from_upstream_AUI']={'n':len(s),'slope':float(b[1]),'HC3_SE':float(np.sqrt(cov[1,1]))}
joined.to_csv(args.out_dir/'may_aui_upstream_comparison.csv',index=False)
hashes=[]
for f,url in [(raw,'https://huggingface.co/datasets/Anthropic/EconomicIndex/resolve/2ea58ff75e4247d26810c37f10c179edc2466cac/release_2026_06_26/data/aei_claude_ai_2026-06-26.csv'),
    (args.raw_root/'ITU_ICTPriceBaskets_2008-2025.xlsx','https://www.itu.int/en/ITU-D/Statistics/Documents/ICT_Prices/ITU_ICTPriceBaskets_2008-2025.xlsx')]:
    h=hashlib.sha256()
    with f.open('rb') as z:
        for v in iter(lambda:z.read(2**20),b''):h.update(v)
    hashes.append({'file':f.name,'size':f.stat().st_size,'sha256':h.hexdigest(),'retrieved_from':url})
results['source_hashes']=hashes
for f in sorted((args.reconstruction_root/'data/raw/anthropic').glob('release_*/*.csv')):
    if f.name==raw.name:continue
    h=hashlib.sha256()
    with f.open('rb') as z:
        for v in iter(lambda:z.read(2**20),b''):h.update(v)
    hashes.append({'file':str(f.relative_to(args.reconstruction_root/'data/raw/anthropic')),'size':f.stat().st_size,'sha256':h.hexdigest(),
                   'source_commit':'2ea58ff75e4247d26810c37f10c179edc2466cac'})
results['all_checks_pass']=all(c['comparison']=='match' for c in comparisons) and results['independent_may_AUI']['max_absolute_difference']==0
json.dump(results,open(args.out_dir/'upstream_verification.json','w'),indent=2)
print(json.dumps(results,indent=2))
