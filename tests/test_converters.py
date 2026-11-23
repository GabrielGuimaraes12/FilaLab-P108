import pytest
from converters import (convert_time, convert_rate, convert_variance,
                        rate_to_time, time_to_rate, parse_observations,
                        observed_stats, sigma_from_variance, variance_from_sigma)


def test_time():
    assert convert_time(15, "minuto", "hora") == pytest.approx(0.25)
    assert convert_time(2, "hora", "minuto") == pytest.approx(120)


def test_rates():
    assert convert_rate(2, "minuto", "hora") == pytest.approx(120)
    assert convert_rate(60, "hora", "minuto") == pytest.approx(1)


def test_reciprocal_cross_unit():
    assert time_to_rate(15, "minuto", "hora") == pytest.approx(4)
    assert rate_to_time(4, "hora", "minuto") == pytest.approx(15)


def test_variance_square_units():
    assert convert_variance(3600, "minuto", "hora") == pytest.approx(1)
    assert sigma_from_variance(16) == pytest.approx(4)
    assert variance_from_sigma(4) == pytest.approx(16)


def test_observed_population():
    mean, var, sigma = observed_stats(parse_observations('4\n6\n8\n10\n12'))
    assert mean == pytest.approx(8)
    assert var == pytest.approx(8)
    assert sigma == pytest.approx(8 ** 0.5)


def test_decimal_and_sample():
    vals = parse_observations('2,5; 3,5; 4,5')
    assert observed_stats(vals, True)[2] == pytest.approx(1)


def test_errors():
    with pytest.raises(ValueError):
        rate_to_time(0, 'hora', 'minuto')
    with pytest.raises(ValueError):
        parse_observations('3\nabc')
    with pytest.raises(ValueError):
        observed_stats([2], sample=True)
    with pytest.raises(ValueError):
        convert_time(-1, 'hora', 'minuto')
