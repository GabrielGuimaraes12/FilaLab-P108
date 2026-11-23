import pytest
from engine import mm_s, mm_sk, mm_sn, mg1, priorities_m1

def test_mm1():
    r=mm_s(3,4,1)
    assert r.Lq==pytest.approx(2.25)
    assert r.L==pytest.approx(3)
    assert r.Wq==pytest.approx(.75)
    assert r.W==pytest.approx(1)

def test_mms_hospital():
    r=mm_s(2,3,2)
    assert r.Lq==pytest.approx(1/12)
    assert r.Wq==pytest.approx(1/24)
    assert r.p0==pytest.approx(.5)

def test_finite_capacity():
    r=mm_sk(2,4,1,5)
    assert r.p0==pytest.approx(.5079365)
    assert r.L==pytest.approx(.9047619,rel=1e-4)
    assert sum(r.probabilities)==pytest.approx(1)
    assert r.effective_rate==pytest.approx(2*(1-r.blocking))

def test_finite_population():
    r=mm_sn(.1,.125,1,2)
    assert sum(r.probabilities)==pytest.approx(1)
    assert r.effective_rate==pytest.approx(.1*(2-r.L))
    assert r.W-r.Wq==pytest.approx(1/.125)

def test_mg1():
    r=mg1(.2,.25,4)
    assert r.Lq==pytest.approx(3.2)
    assert r.Wq==pytest.approx(16)

def test_priority():
    r=priorities_m1([2,4,2],10,True)
    assert [x['W'] for x in r]==pytest.approx([.125,.3125,1.25])
    rr=priorities_m1([2,4,2],10,False)
    assert [x['W'] for x in rr]==pytest.approx([.2,.35,1.1])

def test_instability():
    with pytest.raises(ValueError): mm_s(6,3,2)
    assert mm_sk(6,3,2,5).L >= 0
