"""Independent sparse-dictionary implementation; does not import analysis/core code."""
from pathlib import Path
from collections import defaultdict
import json
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data/raw'


def main():
    m=pd.read_stata(RAW/'Restatement_Matrices.dta')
    m=m[m.Methodology=='Fund Holdings']
    maps={}
    for key,g in m.groupby(['Investor','Asset_Class_Code','Year'],observed=True):
        rows={}
        for d,gg in g.groupby('Destination',observed=True):
            total=sum(float(v) for v in gg.Value)
            rows[str(d)]=[(str(k),float(v)/total) for k,v in zip(gg.Destination_Restated,gg.Value)]
        maps[(str(key[0]),str(key[1]),int(key[2]))]=rows
    p=pd.read_stata(RAW/'Restated_Bilateral_External_Portfolios.dta')
    p=p[p.Methodology=='Fund Holdings']
    emu=set('AUT BEL CYP DEU ESP EST FIN FRA GRC IRL ITA LTU LUX LVA MLT NLD PRT SVK SVN'.split())
    books={}
    for key,g in p.groupby(['Investor','Asset_Class_Code','Year'],observed=True):
        i,a,y=str(key[0]),str(key[1]),int(key[2])
        if (i=='USA' and a in ['E','BC','BG','BSF']) or (i in ['CAN','CHE','DNK','EMU','GBR','NOR','SWE'] and a=='B'):
            domestic=emu if i=='EMU' else {i}
            x={str(d):max(float(v),0.) for d,v in zip(g.Issuer,g.Position_Residency) if str(d) not in domestic}
            total=sum(x.values());books[(i,a,y)]={d:v/total for d,v in x.items()}
    def proj(w,rows):
        result=defaultdict(float)
        for d,weight in w.items():
            for k,share in rows.get(d,[(d,1.)]):result[k]+=weight*share
        return result
    checks=pd.read_csv(ROOT/'results/errors.csv');checks=checks[checks.model=='last']
    targets=pd.read_csv(ROOT/'results/targets.csv')
    max_error=0.;max_target_error=0.;count=0
    for r in checks.itertuples():
        w=books[(r.investor,r.asset,r.year)]
        current=proj(w,maps[(r.investor,r.asset,r.year)])
        old=proj(w,maps[(r.investor,r.asset,r.origin)])
        direct=sum(abs(current[k]-old[k]) for k in set(current)|set(old))/2
        max_error=max(max_error,abs(direct-r.tv));count+=1
        for name,codes in {'China':['CHN'],'Russia':['RUS'],'China_Russia':['CHN','RUS'],'China_HongKong':['CHN','HKG']}.items():
            rr=targets[(targets.investor==r.investor)&(targets.asset==r.asset)&(targets.year==r.year)&(targets.horizon==r.horizon)&(targets.target==name)].iloc[0]
            err=sum(old[k]-current[k] for k in codes)
            max_target_error=max(max_target_error,abs(err-rr.error))
    d=pd.read_csv(ROOT/'results/decomposition.csv')
    residual=float((d.weight+d.mapping-d.total).abs().max())
    assert max_error<1e-10 and max_target_error<1e-10 and residual<1e-10
    report={'sparse_projections_checked':int(count),'target_errors_checked':int(count*4),'max_tv_difference':max_error,'max_target_difference':max_target_error,'max_decomposition_residual':residual,'passed':True}
    (ROOT/'results/independent_verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
