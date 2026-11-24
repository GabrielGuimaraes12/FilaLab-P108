import pytest
from engine import mm_s, mm_sk, mm_sn, mg1, priorities_m1
from analysis_tools import state_range, arrival_wait, inverse_mg1, poisson_range, operating_cost

def test_airport():
    r = mm_sk(15, 20, 1, 4)
    assert r.Lq == pytest.approx((0.75**2 + 2*0.75**3 + 3*0.75**4)*.25 / (1-.75**5))
    assert r.effective_rate == pytest.approx(15*(1-r.blocking))

def test_finite_source():
    r = mm_sn(1, 2, 1, 2)
    assert r.probabilities == pytest.approx([.4, .4, .2])
    assert r.effective_rate == pytest.approx(2-r.L)
    assert arrival_wait(r) == pytest.approx(1/3)
    assert operating_cost(1, 10, r.Lq, 5, 0, 0) == pytest.approx(11)

def test_infinite_tail_and_large_server_pool():
    r = mm_s(1, 2)
    assert state_range(r, 100) == pytest.approx(.5**100)
    assert state_range(r, 2, 3) == pytest.approx(.1875)
    assert 0 < arrival_wait(mm_s(995, 1, 1000)) < 1

def test_mg1_hypotheses():
    assert mg1(3, 4, 0).Lq == pytest.approx(1.125)
    assert mg1(3, 4, .25).Lq == pytest.approx(mm_s(3, 4).Lq)
    for sigma in [0, .2, .5]:
        assert mg1(3, inverse_mg1(3, 2, sigma), sigma).Lq == pytest.approx(2)

def test_priority_conservation():
    for preemptive in (False, True):
        rows = priorities_m1([1, 2], 4, preemptive)
        assert rows[0]['W'] < rows[1]['W']
        assert sum(row['L'] for row in rows) == pytest.approx(3)

def test_poisson_and_invalid_input():
    assert poisson_range(0, 0, 0) == 1
    assert poisson_range(2, 1) == pytest.approx(.8646647167633873)
    assert poisson_range(2, 20) > 0
    with pytest.raises(ValueError):
        mm_s(float('nan'), 2)



def test_course_priority_and_finite_technicians():
    from analysis_tools import two_technician_occupancy
    r = mm_sn(.01, .1, 2, 4)
    first, second = two_technician_occupancy(r)
    assert first > second > 0
    assert first + second == pytest.approx(r.effective_rate / r.mu)
    assert state_range(r, 1) == pytest.approx(.318011321)
    assert (4-r.L)/4 == pytest.approx(.908068091)
    for preemptive in [False, True]:
        rows = priorities_m1([.1, .4, 1.5], 3, preemptive, 2)
        assert sum(row['Lq'] for row in rows) == pytest.approx(1/12)
        assert rows[2]['Wq'] == pytest.approx(.0547785548 if preemptive else 1/22)


@pytest.mark.parametrize('args, expected', [
    ((1, 4/3, 1, 4), (1.4443021767, .8614285714)),
    ((15, 20, 2, 5), (.84946656, .00701705)),
    ((3, 4, 2, 5), (.84946656, .03508526)),
])
def test_course_finite_capacity(args, expected):
    r = mm_sk(*args)
    assert (r.L, r.Wq) == pytest.approx(expected, abs=1e-7)
    assert sum(r.probabilities) == pytest.approx(1)
    assert r.L-r.Lq == pytest.approx(r.effective_rate/r.mu)


def test_hospital_and_airport_tails():
    from analysis_tools import time_tail
    assert time_tail(mm_s(2, 3, 2), 1, total=True) == pytest.approx(.065522783)
    assert time_tail(mm_s(1, 2, 2), 0, total=True) == 1
    assert 1 - state_range(mm_s(25, 20, 2), 7) == pytest.approx(.9541502732496995)
    assert state_range(mm_s(10, 15), 0, 1) == pytest.approx(5/9)


def test_erlang_equal_rates():
    from analysis_tools import time_tail
    import math
    r = mm_s(2, 2, 2)
    assert time_tail(r, 1, total=True) == pytest.approx(math.exp(-2)*(1+2/3))



def test_finite_source_time_tail():
    from analysis_tools import finite_source_time_tail
    import math

    r = mm_sn(1, 2, 1, 2)
    assert finite_source_time_tail(r, 1) == pytest.approx(math.exp(-2) / 3)
    assert finite_source_time_tail(r, 1, total=True) == pytest.approx(5*math.exp(-2) / 3)
    assert finite_source_time_tail(r, 0, total=True) == pytest.approx(1)
