import sys
from pathlib import Path
from itertools import combinations
import numpy as np
from scipy.optimize import linprog
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from core import exposure_interval


@pytest.mark.parametrize('seed',range(80))
def test_sharp_interval_against_linear_program(seed):
    rng=np.random.default_rng(seed);n,d=4,5
    m=rng.dirichlet(np.ones(d),size=n);w=rng.dirichlet(np.ones(n));r=rng.uniform(0,1,n)
    lo,hi,width=exposure_interval(w,m,[0,1],r)
    independent=[]
    for i in range(n):
        # Variables q followed by nonnegative absolute deviations u.
        c=np.r_[[-1.,-1.,0,0,0],np.zeros(d)]
        A=np.vstack([np.c_[np.eye(d),-np.eye(d)],np.c_[-np.eye(d),-np.eye(d)],np.r_[np.zeros(d),np.ones(d)][None,:]])
        b=np.r_[m[i],-m[i],2*r[i]]
        ae=np.r_[np.ones(d),np.zeros(d)][None,:]
        upper=linprog(c,A_ub=A,b_ub=b,A_eq=ae,b_eq=[1.],bounds=(0,None),method='highs')
        lower=linprog(-c,A_ub=A,b_ub=b,A_eq=ae,b_eq=[1.],bounds=(0,None),method='highs')
        assert upper.success and lower.success
        independent.append((lower.fun,-upper.fun))
    np.testing.assert_allclose([lo,hi],np.sum(w[:,None]*independent,axis=0),atol=1e-9)
    best=max(sum(width[j] for j in s) for s in combinations(range(n),2))
    assert abs(sum(np.sort(width)[-2:])-best)<1e-12
