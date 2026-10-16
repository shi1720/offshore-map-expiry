"""Reproduce the historical accounting experiment from the public CMNS release."""
from pathlib import Path
import argparse
import json
import hashlib
import sys
import numpy as np
import pandas as pd
from core import validate_map, tv, decompose, error_envelope, refresh, project

ROOT = Path(__file__).resolve().parents[1]
EMU = set('AUT BEL CYP DEU ESP EST FIN FRA GRC IRL ITA LTU LUX LVA MLT NLD PRT SVK SVN'.split())
INVESTORS = ['CAN','CHE','DNK','EMU','GBR','NOR','SWE']
TARGETS = {'China':['CHN'], 'Russia':['RUS'], 'China_Russia':['CHN','RUS'], 'China_HongKong':['CHN','HKG']}


def load(raw):
    maps = pd.read_stata(raw/'Restatement_Matrices.dta')
    pos = pd.read_stata(raw/'Restated_Bilateral_External_Portfolios.dta')
    if pos.Year.min() != 2007 or maps.Year.min() != 2007:
        raise ValueError('Incomplete or unexpected source release')
    codes = sorted(set(maps.Destination) | set(maps.Destination_Restated) | set(pos.Issuer))
    ci = {c:i for i,c in enumerate(codes)}
    identity = np.eye(len(codes))
    matrices, support = {}, {}
    select = maps[maps.Methodology.isin(['Fund Holdings','Issuance','Enhanced Fund Holdings'])]
    for (method,investor,asset,year),g in select.groupby(['Methodology','Investor','Asset_Class_Code','Year'],observed=True):
        m = identity.copy()
        destinations = g.Destination.unique()
        idx = [ci[c] for c in destinations]
        m[idx,:] = 0
        if g.duplicated(['Destination','Destination_Restated']).any():
            raise ValueError('Duplicate matrix cells')
        m[g.Destination.map(ci).to_numpy(),g.Destination_Restated.map(ci).to_numpy()] = g.Value.to_numpy()
        validate_map(m)
        # Remove binary32 source roundoff, max deviation recorded separately.
        m /= m.sum(axis=1,keepdims=True)
        key=(str(method),str(investor),str(asset),int(year))
        matrices[key]=m
        support[key]=set(destinations)
    books={};cleaning=[];signed_books={}
    p=pos[pos.Methodology=='Fund Holdings']
    for (investor,asset,year),g in p.groupby(['Investor','Asset_Class_Code','Year'],observed=True):
        investor,asset,year=str(investor),str(asset),int(year)
        if not ((investor=='USA' and asset in ['E','BC','BG','BSF']) or (investor in INVESTORS and asset=='B')):
            continue
        domestic=EMU if investor=='EMU' else {investor}
        g=g[~g.Issuer.isin(domestic)]
        x=np.zeros(len(codes))
        if g.Position_Residency.isna().any():
            raise ValueError(f'Unexpected missing positions {investor} {asset} {year}')
        if g.duplicated('Issuer').any():raise ValueError('Duplicate positions')
        x[g.Issuer.map(ci).to_numpy()]=g.Position_Residency.to_numpy()
        if x.sum()<=0:raise ValueError('Invalid external book')
        signed_books[(investor,asset,year)]=x.copy()
        cleaning.append(dict(investor=investor,asset=asset,year=year,negative_cells=int((x<0).sum()),negative_musd=float(-x[x<0].sum()),signed_total_musd=float(x.sum()),negative_fraction=float(-x[x<0].sum()/x.sum())))
        x=np.maximum(x,0)
        books[(investor,asset,year)]=x
    stats={'maps_rows':len(maps),'positions_rows':len(pos),'country_codes':len(codes),
           'books':len(books),'source_row_sum_max_error':float((select.groupby(['Methodology','Investor','Asset_Class_Code','Year','Destination'],observed=True).Value.sum()-1).abs().max())}
    stats['negative_cleaning']=cleaning
    return codes,ci,matrices,support,books,pos,stats,signed_books


def run(raw):
    codes,ci,maps,support,books,pos,stats,signed_books=load(raw)
    out=ROOT/'results';out.mkdir(exist_ok=True)
    def get(i,a,y,method='Fund Holdings'):
        return maps[(method,'World' if method=='Issuance' else i,a,y)]
    def has(i,a,y,method='Fund Holdings'):
        return (method,'World' if method=='Issuance' else i,a,y) in maps
    rows=[];target_rows=[];routes=[];series=[];dec=[];refresh_rows=[];recon=[];enhanced=[]
    rng=np.random.default_rng(1720406)
    for (i,a,t),x in sorted(books.items()):
        w=x/x.sum();m=get(i,a,t);p=project(w,m)
        for name,cs in TARGETS.items():
            idx=[ci[c] for c in cs]
            series.append(dict(investor=i,asset=a,year=t,target=name,share=float(p[idx].sum()),residence_share=float(w[idx].sum()),total_musd=x.sum()))
        # Compare external-only reconstruction with published ex-domestic positions.
        # For EMU only non-EMU destinations are directly comparable after intra-EMU removal.
        if i!='EMU':
            gp=pos[(pos.Methodology=='Fund Holdings')&(pos.Investor==i)&(pos.Asset_Class_Code==a)&(pos.Year==t)]
            pub=gp.set_index('Issuer').Restatement_Ex_Domestic.reindex(codes).fillna(0).to_numpy(dtype=float)
            # Ex-domestic source preserves original domestic stocks on its diagonal.
            pub[ci[i]]-=float(gp.loc[gp.Issuer==i,'Position_Residency'].fillna(0).sum())
            recon.append(dict(investor=i,asset=a,year=t,max_abs_musd=float(np.abs(project(x,m)-pub).max()),tv_scaled=tv(project(x,m),pub)/x.sum()))
        for h in [1,2,3,5]:
            s=t-h
            if (i,a,s) not in books or not has(i,a,s):continue
            m0=get(i,a,s);w0=books[(i,a,s)]/books[(i,a,s)].sum();p0=project(w0,m0)
            old=project(w,m0);bound=error_envelope(w,m0,m)
            missing_current=sum(w[ci[c]] for c in codes if c not in support[('Fund Holdings',i,a,t)])
            missing_old=sum(w[ci[c]] for c in codes if c not in support[('Fund Holdings',i,a,s)])
            common=support[('Fund Holdings',i,a,s)] & support[('Fund Holdings',i,a,t)]
            cw=w*np.array([c in common for c in codes]);cw/=cw.sum()
            if has(i,a,t,'Enhanced Fund Holdings') and has(i,a,s,'Enhanced Fund Holdings'):
                me=get(i,a,t,'Enhanced Fund Holdings');me0=get(i,a,s,'Enhanced Fund Holdings')
                enhanced.append(dict(investor=i,asset=a,year=t,origin=s,horizon=h,tv=tv(project(w,me),project(w,me0)),benchmark_gap_tv=tv(p,project(w,me))))
            predictors={'last':m0}
            if all(has(i,a,s-j) for j in range(3)):
                predictors['mean3']=sum(get(i,a,s-j) for j in range(3))/3
            peers=[get(j,a,s) for j in INVESTORS+['USA'] if j!=i and has(j,a,s)]
            if peers:predictors['peer_mean']=sum(peers)/len(peers)
            if has(i,a,s,'Issuance'):predictors['issuance']=get(i,a,s,'Issuance')
            for model,mp in predictors.items():
                pp=project(w,mp)
                signed=signed_books[(i,a,t)];sw=signed/signed.sum()
                rows.append(dict(investor=i,asset=a,year=t,origin=s,horizon=h,model=model,tv=tv(pp,p),common_support_tv=tv(project(cw,mp),project(cw,m)),signed_tv=tv(project(sw,mp),project(sw,m)),envelope=error_envelope(w,mp,m),total_musd=x.sum(),missing_current=missing_current,missing_old=missing_old))
            for name,cs in TARGETS.items():
                idx=[ci[c] for c in cs];actual=float(p[idx].sum()-p0[idx].sum());frozen=float(old[idx].sum()-p0[idx].sum())
                target_rows.append(dict(investor=i,asset=a,year=t,origin=s,horizon=h,target=name,current=float(p[idx].sum()),frozen=float(old[idx].sum()),base=float(p0[idx].sum()),error=float(old[idx].sum()-p[idx].sum()),actual_change=actual,frozen_change=frozen,sign_reversal=actual*frozen < -1e-16,material_reversal=actual*frozen < -1e-16 and abs(actual)>=.001 and abs(frozen)>=.001))
            if h==1:
                dw,dm=decompose(w0,w,m0,m)
                for name,cs in TARGETS.items():
                    idx=[ci[c] for c in cs]
                    dec.append(dict(investor=i,asset=a,year=t,target=name,weight=float(dw[idx].sum()),mapping=float(dm[idx].sum()),total=float(p[idx].sum()-p0[idx].sum())))
            if h==3:
                for c,r in ci.items():
                    contribution=w[r]*(m0[r]-m[r])
                    routes.append(dict(investor=i,asset=a,year=t,origin=s,residence=c,weight=w[r],row_tv=tv(m0[r],m[r]),envelope_contribution=w[r]*tv(m0[r],m[r]),china_error=float(contribution[ci['CHN']]),russia_error=float(contribution[ci['RUS']])))
            # Historical instability uses only differences ending at/before origin.
            if h==3 and s>=2010:
                row_delta=w[:,None]*(m-m0)
                row_bound=w*np.abs(m0-m).sum(axis=1)/2
                prior=[np.abs(get(i,a,v)-get(i,a,v-1)).sum(axis=1)/2 for v in range(max(2008,s-2),s+1) if has(i,a,v-1)]
                score=w*np.mean(prior,axis=0)
                eligible=np.flatnonzero(w>0)
                risk_order=eligible[np.argsort(-score[eligible],kind='stable')]
                weight_order=eligible[np.argsort(-w[eligible],kind='stable')]
                oracle_order=eligible[np.argsort(-(w*np.abs(m0-m).sum(axis=1)/2)[eligible],kind='stable')]
                for k in [1,3,5,10]:
                    for model,rank in [('instability',risk_order),('weight',weight_order),('oracle',oracle_order)]:
                        chosen=rank[:k];v=tv(old+row_delta[chosen].sum(axis=0),p)
                        refresh_rows.append(dict(investor=i,asset=a,year=t,origin=s,k=k,policy=model,tv=v,envelope=bound-row_bound[chosen].sum(),baseline_tv=tv(old,p),baseline_envelope=bound,worse=float(v>tv(old,p)+1e-12)))
                    values=[];bounds=[]
                    for _ in range(200):
                        selected=rng.choice(eligible,size=min(k,len(eligible)),replace=False)
                        values.append(tv(old+row_delta[selected].sum(axis=0),p));bounds.append(bound-row_bound[selected].sum())
                    refresh_rows.append(dict(investor=i,asset=a,year=t,origin=s,k=k,policy='random_mean',tv=float(np.mean(values)),envelope=float(np.mean(bounds)),baseline_tv=tv(old,p),baseline_envelope=bound,worse=float(np.mean(np.array(values)>tv(old,p)+1e-12))))
    tables={'errors':rows,'targets':target_rows,'routes':routes,'series':series,'decomposition':dec,'refresh':refresh_rows,'reconciliation':recon,'enhanced':enhanced}
    for name,records in tables.items():pd.DataFrame(records).to_csv(out/f'{name}.csv',index=False,float_format='%.12g')
    stats['raw_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in raw.glob('*.dta')}
    stats['seed']=1720406
    stats['experiment_rows']={k:len(v) for k,v in tables.items()}
    (out/'audit.json').write_text(json.dumps(stats,indent=2)+'\n')
    print(json.dumps(stats,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--raw',type=Path,default=ROOT/'data/raw')
    run(parser.parse_args().raw)
