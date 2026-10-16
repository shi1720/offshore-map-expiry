"""Prespecified support checks and explicitly secondary benchmark comparisons."""
from pathlib import Path
from zipfile import ZipFile
import io
import numpy as np
import pandas as pd
from analyze import load, ROOT
from core import project,tv

CENTERS=set('BMU VGB CYM CUW GGY IRL IMN JEY LBR LUX NLD MLT MHL MUS PAN CHE'.split())


def main():
    codes,ci,maps,support,books,pos,stats,signed=load(ROOT/'data/raw')
    errors=pd.read_csv(ROOT/'results/errors.csv');records=[]
    for r in errors[errors.model=='last'].itertuples():
        x=books[(r.investor,r.asset,r.year)];w=x/x.sum()
        m=maps[('Fund Holdings',r.investor,r.asset,r.year)]
        m0=maps[('Fund Holdings',r.investor,r.asset,r.origin)]
        # Both vintages keep non-center rows on the residence diagonal.
        wc=w*np.array([c in CENTERS for c in codes])
        center_error=project(wc,m-m0)
        wt=w*np.array([c not in ['ANT','BES','CUW','SXM'] for c in codes]);wt/=wt.sum()
        records.append(dict(investor=r.investor,asset=r.asset,year=r.year,horizon=r.horizon,full_tv=r.tv,center_route_tv=float(np.abs(center_error).sum()/2),no_territorial_tv=tv(project(wt,m),project(wt,m0))))
    pd.DataFrame(records).to_csv(ROOT/'results/route_sensitivity.csv',index=False,float_format='%.12g')
    with ZipFile(ROOT/'data/raw/fed_portfolio_holdings.zip') as z:
        f=pd.read_csv(io.BytesIO(z.read('common_stock_data_table.csv')))
    series=pd.read_csv(ROOT/'results/series.csv')
    fed=[]
    for year in range(2007,2025):
        total=float(f.loc[f.cntry_code==99996,f'market_value_residence_{year}'].iloc[0])
        for name,pattern in [('China','CHINA, MAINLAND'),('Russia','RUSSIA')]:
            g=f[f.cntry_name==pattern]
            res=float(g[f'market_value_residence_{year}'].iloc[0]);nat=float(g[f'market_value_nationality_{year}'].iloc[0])
            match=series[(series.investor=='USA')&(series.asset=='E')&(series.year==year)&(series.target==name)]
            fed.append(dict(year=year,target=name,total_musd=total,residence_share=res/total,nationality_share=nat/total,cmns_share=float(match.share.iloc[0]) if len(match) else np.nan))
    pd.DataFrame(fed).to_csv(ROOT/'results/fed_comparison.csv',index=False,float_format='%.12g')


if __name__=='__main__':main()
