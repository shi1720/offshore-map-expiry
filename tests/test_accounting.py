import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from core import validate_map, project, tv, decompose, error_envelope, refresh


@pytest.mark.parametrize('seed',range(200))
def test_conservation_decomposition_and_envelope(seed):
    rng=np.random.default_rng(seed);n=7
    m0=rng.dirichlet(np.ones(n),size=n);m1=rng.dirichlet(np.ones(n),size=n)
    w0=rng.dirichlet(np.ones(n));w1=rng.dirichlet(np.ones(n))
    validate_map(m0);validate_map(m1)
    p0=project(w0,m0);p1=project(w1,m1)
    assert abs(p1.sum()-1)<1e-12
    dw,dm=decompose(w0,w1,m0,m1)
    np.testing.assert_allclose(dw+dm,p1-p0,atol=2e-15)
    assert tv(project(w1,m0),p1)<=error_envelope(w1,m0,m1)+1e-14
    # Independently enumerate every row and column.
    direct=[sum(float(w1[d])*float(m1[d,k]) for d in range(n)) for k in range(n)]
    np.testing.assert_allclose(p1,direct,atol=2e-15)
    indices=[1,4];updated=refresh(m0,m1,indices)
    reduced=error_envelope(w1,m0,m1)-sum(w1[d]*tv(m0[d],m1[d]) for d in indices)
    assert abs(error_envelope(w1,updated,m1)-reduced)<1e-14


def test_refresh_can_break_error_cancellation():
    w=np.array([.5,.5]);old=np.array([[1.,0],[0,1.]]);new=np.array([[0.,1],[1,0.]])
    assert tv(project(w,old),project(w,new))==0
    assert tv(project(w,refresh(old,new,[0])),project(w,new))==.5
    assert error_envelope(w,refresh(old,new,[0]),new)==.5


def test_envelope_is_sharp():
    w=np.array([.3,.7]);old=np.array([[1.,0],[1.,0]]);new=np.array([[0.,1],[0.,1]])
    assert tv(project(w,old),project(w,new))==error_envelope(w,old,new)==1.


@pytest.mark.parametrize('bad',[np.array([[.5,.4]]),np.array([[1.1,-.1]]),np.array([[np.nan,1.]])])
def test_invalid_maps_rejected(bad):
    with pytest.raises(ValueError):validate_map(bad)


@pytest.mark.parametrize('seed',range(100))
def test_passive_valuation_bounds(seed):
    rng=np.random.default_rng(seed);n=20
    shares=rng.dirichlet(np.ones(n));group=np.arange(n)<7
    lo,hi=.7,1.4;returns=rng.uniform(lo,hi,size=n)
    p=shares[group].sum();tilted=shares*returns;actual=tilted[group].sum()/tilted.sum()
    lower=lo*p/(lo*p+hi*(1-p));upper=hi*p/(hi*p+lo*(1-p))
    assert lower-1e-14<=actual<=upper+1e-14
