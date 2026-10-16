"""Generate all paper tables and figures directly from saved experiment records."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'results';G=ROOT/'paper/generated';G.mkdir(exist_ok=True)
F=ROOT/'figures';F.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.2,'pdf.fonttype':42,'figure.dpi':160})
COLORS=['#153f66','#c06631','#288475','#95659a']
e=pd.read_csv(R/'errors.csv');t=pd.read_csv(R/'targets.csv');f=pd.read_csv(R/'refresh.csv');s=pd.read_csv(R/'series.csv');d=pd.read_csv(R/'decomposition.csv');routes=pd.read_csv(R/'routes.csv')
base=e[e.model=='last']
def save(fig,name):
    fig.tight_layout(pad=1.1);fig.savefig(F/f'{name}.pdf',bbox_inches='tight');fig.savefig(F/f'{name}.png',bbox_inches='tight',dpi=180);plt.close(fig)
def table(name,headers,rows,align=None):
    align=align or ('l'+'r'*(len(headers)-1))
    lines=['\\begin{tabular}{'+align+'}','\\toprule',' & '.join(headers)+r' \\','\\midrule']
    lines += [' & '.join(map(str,row))+r' \\' for row in rows]
    lines += [r'\bottomrule',r'\end{tabular}']
    (G/f'{name}.tex').write_text('\n'.join(lines)+'\n')

# Figure 1: no common vertical scale conceals the asset-class differences.
fig,axs=plt.subplots(2,2,figsize=(7.0,5.2))
names={'E':'Common equity','BC':'Corporate bonds','BG':'Government bonds','BSF':'Asset-backed securities'}
for ax,(asset,name),color in zip(axs.flat,names.items(),COLORS):
    g=base[(base.investor=='USA')&(base.asset==asset)].groupby('horizon').tv
    ax.plot(g.mean().index,100*g.mean(),color=color,marker='o',label='Mean')
    ax.plot(g.max().index,100*g.max(),color=color,linestyle=':',label='Maximum')
    ax.set(title=name,xlabel='Map age (years)',ylabel='TV distance (pp)',xticks=[1,2,3,5],ylim=(0,None));ax.legend(frameon=False,fontsize=8)
save(fig,'age_errors')

fig,axs=plt.subplots(1,2,figsize=(7.0,3.1))
for ax,asset,target,origin,end,title in [(axs[0],'E','China',2017,2020,'China: common equity'),(axs[1],'BC','Russia',2012,2015,'Russia: corporate bonds')]:
    current=s[(s.investor=='USA')&(s.asset==asset)&(s.target==target)&s.year.between(origin,end)]
    old=t[(t.investor=='USA')&(t.asset==asset)&(t.target==target)&(t.origin==origin)&t.year.between(origin+1,end)].sort_values('year')
    years=[origin]+old.year.tolist();frozen=[float(current[current.year==origin].share.iloc[0])]+old.frozen.tolist()
    ax.plot(current.year,100*current.share,marker='o',color=COLORS[0],label='Current map')
    ax.plot(years,100*np.array(frozen),marker='s',linestyle='--',color=COLORS[1],label=f'Map fixed at {origin}')
    ax.set(title=title,xlabel='Year',ylabel='Share of external-residence book (%)',xticks=list(range(origin,end+1)));ax.legend(frameon=False,fontsize=8)
save(fig,'country_examples')

fig,axs=plt.subplots(1,2,figsize=(7.0,3.7))
for ax,asset,title in [(axs[0],'E','Common equity'),(axs[1],'BC','Corporate bonds')]:
    v=routes[(routes.investor=='USA')&(routes.asset==asset)].groupby('residence').envelope_contribution.mean().nlargest(8).sort_values()
    ax.barh(v.index,100*v.values,color=COLORS[0]);ax.set(title=title,xlabel='Mean weighted row-TV contribution (pp)')
save(fig,'route_contributions')

fig,axs=plt.subplots(1,2,figsize=(7.0,3.2))
for ax,asset,title in [(axs[0],'E','Common equity'),(axs[1],'BC','Corporate bonds')]:
    sub=f[(f.investor=='USA')&(f.asset==asset)]
    for policy,label,color,style in [('instability','Historical instability',COLORS[0],'-'),('weight','Current book weight',COLORS[1],'--'),('random_mean','Random (mean)',COLORS[3],':'),('oracle','Ex post row bound',COLORS[2],'-.')]:
        g=sub[sub.policy==policy].groupby('k').tv.mean()
        baseline=sub[sub.policy==policy].baseline_tv.mean()
        ax.plot([0]+g.index.tolist(),100*np.r_[baseline,g.values],label=label,color=color,linestyle=style,marker='o',markersize=3)
    ax.set(title=title,xlabel='Rows refreshed exactly',ylabel='Mean residual TV distance (pp)',xticks=[0,1,3,5,10],ylim=(0,None))
axs[0].legend(frameon=False,fontsize=7)
save(fig,'selective_refresh')

# An exact decomposition of annual changes; no transaction interpretation.
fig,axs=plt.subplots(1,2,figsize=(7.0,3.0))
for ax,asset,target,title in [(axs[0],'E','China','China: common equity'),(axs[1],'BC','Russia','Russia: corporate bonds')]:
    sub=d[(d.investor=='USA')&(d.asset==asset)&(d.target==target)].sort_values('year')
    ax.bar(sub.year-.18,100*sub.weight,width=.36,label='Residence weights',color=COLORS[0])
    ax.bar(sub.year+.18,100*sub.mapping,width=.36,label='Within-residence map',color=COLORS[1])
    ax.axhline(0,color='black',lw=.6);ax.set(title=title,xlabel='Year',ylabel='Contribution to annual change (pp)',xticks=[2008,2012,2016,2020])
axs[0].legend(frameon=False,fontsize=7)
save(fig,'decomposition')

fc=pd.read_csv(R/'fed_comparison.csv')
fig,axs=plt.subplots(1,2,figsize=(7.0,3.0))
for ax,target in zip(axs,['China','Russia']):
    g=fc[fc.target==target]
    ax.plot(g.year,100*g.nationality_share,color=COLORS[0],label='Bertaut et al.: nationality')
    ax.plot(g.year,100*g.residence_share,color=COLORS[1],linestyle='--',label='Bertaut et al.: residence')
    ax.plot(g.year,100*g.cmns_share,color=COLORS[2],linestyle=':',label='CMNS: nationality')
    ax.axvline(2020,color='grey',lw=.7);ax.set(title=target,xlabel='Year',ylabel='Common-equity share (%)',xticks=[2007,2012,2017,2020,2024])
axs[0].legend(frameon=False,fontsize=6.5)
save(fig,'external_comparison')

rows=[]
for a,name in names.items():
    for h in [1,2,3,5]:
        v=base[(base.investor=='USA')&(base.asset==a)&(base.horizon==h)].tv
        rows.append([name if h==1 else '',h,len(v),f'{100*v.mean():.2f}',f'{100*v.median():.2f}',f'{100*v.max():.2f}'])
table('age_table',['Asset class','Age','N','Mean','Median','Maximum'],rows)
rows=[]
for a,name in names.items():
    for target in ['China','Russia']:
        v=t[(t.investor=='USA')&(t.asset==a)&(t.horizon==3)&(t.target==target)]
        rows.append([name if target=='China' else '',target,len(v),int(v.sign_reversal.sum()),int(v.material_reversal.sum()),f'{100*v.error.abs().mean():.2f}'])
table('reversal_table',['Asset class','Target','N','Any reversal','Material','Mean abs. error'],rows)
rows=[]
for model,label in [('last','Latest investor map'),('mean3','Mean of latest three maps'),('peer_mean','Other-investor mean'),('issuance','Issuance map')]:
    v=e[(e.investor=='USA')&(e.asset=='E')&(e.horizon==3)&(e.year>=2012)&(e.model==model)].tv
    rows.append([label,len(v),f'{100*v.mean():.2f}',f'{100*v.max():.2f}'])
table('predictor_table',['Map used','N','Mean TV (pp)','Maximum TV (pp)'],rows)
rows=[]
for i in ['CAN','CHE','DNK','EMU','GBR','NOR','SWE']:
    v=base[(base.investor==i)&(base.asset=='B')&(base.horizon==3)]
    rows.append([i,len(v),f'{100*v.tv.mean():.2f}',f'{100*v.tv.max():.2f}',f'{100*v.missing_old.max():.3f}'])
table('extension_table',['Investor','N','Mean TV (pp)','Maximum TV (pp)','Unmapped weight (\%)'],rows)
rows=[]
for i,a,name in [('USA','E','U.S. equity'),('USA','BC','U.S. corporate'),('USA','BG','U.S. government'),('USA','BSF','U.S. asset-backed')]+[(i,'B',i+' bonds') for i in ['CAN','CHE','DNK','EMU','GBR','NOR','SWE']]:
    v=f[(f.investor==i)&(f.asset==a)&(f.k==5)]
    vals=[v.baseline_tv.mean()]+[v[v.policy==p].tv.mean() for p in ['instability','weight','oracle']]
    rows.append([name]+[f'{100*z:.2f}' for z in vals])
table('refresh_table',['Book','Stale','Instability','Weight','Ex post bound'],rows)
sens=pd.read_csv(R/'route_sensitivity.csv')
rows=[]
for a,name in names.items():
    v=sens[(sens.investor=='USA')&(sens.asset==a)&(sens.horizon==3)]
    rows.append([name]+[f'{100*v[c].mean():.2f}' for c in ['full_tv','center_route_tv','no_territorial_tv']])
table('route_table',['Asset class','Full','Center routes','Territorial-code exclusion'],rows)
rows=[]
for year in [2017,2020,2024]:
    for target in ['China','Russia']:
        v=fc[(fc.year==year)&(fc.target==target)].iloc[0]
        rows.append([year,target,f'{100*v.nationality_share:.2f}',f'{100*v.residence_share:.2f}',f'{100*v.cmns_share:.2f}' if np.isfinite(v.cmns_share) else '--'])
table('fed_table',['Year','Target','BBC nationality','BBC residence','CMNS nationality'],rows)

summary={
 'primary_mean_tv_h3_pp':100*base.query('investor=="USA" and asset=="E" and horizon==3').tv.mean(),
 'refresh_equity_reduction_percent':100*(1-f.query('investor=="USA" and asset=="E" and k==5 and policy=="instability"').tv.mean()/f.query('investor=="USA" and asset=="E" and k==5 and policy=="instability"').baseline_tv.mean()),
 'max_signed_tv_sensitivity_pp':100*(e.tv-e.signed_tv).abs().max(),
 'max_common_support_sensitivity_pp':100*(e.tv-e.common_support_tv).abs().max(),
 'negative_cells':sum(x['negative_cells'] for x in json.load(open(R/'audit.json'))['negative_cleaning']),
}
(R/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
