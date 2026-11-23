"""Conversores determinísticos de unidades utilizados na interface do FilaLab.

Taxas representam eventos por unidade de tempo. Desvios-padrão são tempos;
variâncias são tempos ao quadrado.
"""
import math
from statistics import pstdev, stdev

SECONDS = {"segundo": 1.0, "minuto": 60.0, "hora": 3600.0, "dia": 86400.0}


def _unit(unit):
    if unit not in SECONDS:
        raise ValueError(f"Unidade desconhecida: {unit}")
    return SECONDS[unit]


def _nonnegative(value):
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError("Informe um número finito e não negativo.")
    return value


def convert_time(value, source, target):
    return _nonnegative(value) * _unit(source) / _unit(target)


def convert_rate(value, source, target):
    """Ex.: 2 eventos/minuto = 120 eventos/hora."""
    return _nonnegative(value) * _unit(target) / _unit(source)


def convert_variance(value, source, target):
    return _nonnegative(value) * (_unit(source) / _unit(target)) ** 2


def rate_to_time(rate, rate_unit, time_unit):
    rate = _nonnegative(rate)
    if not rate:
        raise ValueError("Taxa deve ser maior que zero para calcular o tempo médio.")
    return convert_time(1 / rate, rate_unit, time_unit)


def time_to_rate(time, time_unit, rate_unit):
    time = _nonnegative(time)
    if not time:
        raise ValueError("Tempo médio deve ser maior que zero para calcular a taxa.")
    return convert_rate(1 / time, time_unit, rate_unit)


def sigma_from_variance(variance):
    return math.sqrt(_nonnegative(variance))


def variance_from_sigma(sigma):
    return _nonnegative(sigma) ** 2


def parse_observations(text):
    """Aceita uma observação por linha ou valores separados por ponto-e-vírgula.

    Vírgula é decimal PT-BR (ex.: 2,5), nunca separador de observações.
    """
    values = []
    for piece in text.replace(";", "\n").splitlines():
        part = piece.strip().replace(" ", "")
        if not part:
            continue
        if "," in part and "." in part:
            raise ValueError("Use vírgula OU ponto para decimais, não ambos.")
        try:
            value = _nonnegative(float(part.replace(",", ".")))
        except ValueError as exc:
            raise ValueError(f"Observação inválida: {piece!r}. Informe um valor por linha.") from exc
        values.append(value)
    if not values:
        raise ValueError("Informe pelo menos um tempo observado.")
    return values


def observed_stats(values, sample=False):
    if not values or (sample and len(values) < 2):
        raise ValueError("Informe pelo menos dois valores para desvio-padrão amostral.")
    values = [_nonnegative(v) for v in values]
    mean = sum(values) / len(values)
    sigma = stdev(values) if sample else pstdev(values)
    return mean, sigma ** 2, sigma
