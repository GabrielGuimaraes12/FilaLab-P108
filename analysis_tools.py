"""Probabilidades, inversão e custos para os modelos estacionários."""
import math


def state_range(result, low, high=None):
    """P(low ≤ X ≤ high), com cauda geométrica exata em M/M/s."""
    if low < 0 or (high is not None and high < low):
        raise ValueError("Informe um intervalo inteiro válido.")
    if result.probabilities is None:
        raise ValueError("O modelo requer a distribuição do serviço para esta consulta.")
    if result.model != "M/M/s" or result.rho == 0:
        return math.fsum(result.probabilities[low:None if high is None else high + 1])
    s = result.servers
    lower_mass = math.fsum(result.probabilities[low:s if high is None else min(s, high + 1)])
    if high is not None and high < s:
        return lower_mass
    tail_start = max(low, s)
    tail = result.probabilities[s] * result.rho**(tail_start - s) / (1 - result.rho)
    if high is not None:
        tail *= -math.expm1((high - tail_start + 1) * math.log(result.rho))
    return min(1.0, lower_mass + tail)


def arrival_wait(result):
    """Fração das chegadas admitidas que encontram todos os servidores ocupados."""
    if result.effective_rate == 0:
        return 0.0
    if result.model == "M/M/s/N":
        population = len(result.probabilities) - 1
        return math.fsum(
            (population - n) * result.lam * p
            for n, p in enumerate(result.probabilities)
            if n >= result.servers
        ) / result.effective_rate
    if result.model == "M/M/s/K":
        return state_range(result, result.servers, len(result.probabilities) - 2) / (
            result.effective_rate / result.lam
        ) if len(result.probabilities) - 1 > result.servers else 0.0
    if result.model == "M/G/1":
        return result.rho
    return state_range(result, result.servers)


def inverse_mg1(lam, lq, sigma):
    """Recupera μ de λ, Lq e σ conhecidos, com solução física finita."""
    if not all(math.isfinite(x) for x in (lam, lq, sigma)) or lam <= 0 or lq <= 0 or sigma < 0:
        raise ValueError("Use λ e Lq positivos e σ não negativo.")
    difference = 2*lq - (lam*sigma)**2
    if difference <= 0:
        raise ValueError("Não há μ finito compatível com estes valores.")
    rho = difference / (math.sqrt(lq*lq + difference) + lq)
    return lam / rho


def poisson_range(mean, low, high=None):
    """Probabilidade de um intervalo de contagens Poisson inclusivo."""
    if not math.isfinite(mean) or not 0 <= mean <= 10000 or not 0 <= low <= 100000:
        raise ValueError("Use média entre 0 e 10.000 e limite inferior entre 0 e 100.000.")
    if high is not None and not low <= high <= 100000:
        raise ValueError("O limite superior deve estar entre o inferior e 100.000.")
    if mean == 0:
        return float(low == 0)
    # Beyond this bound the remaining upper tail is below floating-point precision.
    end = max(low + 100, math.ceil(mean + 40*math.sqrt(mean + 1))) if high is None else high
    if low == 0 and high is None:
        return 1.0
    return min(1.0, math.fsum(
        math.exp(-mean + n*math.log(mean) - math.lgamma(n+1))
        for n in range(low, end + 1)
    ))


def operating_cost(servers, server_cost, customers, customer_cost, losses, loss_cost):
    return servers*server_cost + customers*customer_cost + losses*loss_cost


def time_tail(result, time, total=False):
    """FCFS em M/M/s. Condicionada à espera, Wq é exponencial."""
    if result.model != "M/M/s" or not math.isfinite(time) or time < 0:
        raise ValueError("Use M/M/s e um tempo finito não negativo.")
    decay = result.servers * result.mu - result.lam
    wait = arrival_wait(result)
    if not total:
        return wait * math.exp(-decay*time)
    service_tail = math.exp(-result.mu*time)
    gap = abs(result.mu - decay)
    integral = -math.expm1(-gap*time)/gap if gap else time
    return min(1.0, service_tail + wait*result.mu*math.exp(-min(decay, result.mu)*time)*integral)


def two_technician_occupancy(result):
    """Ocupações com dois técnicos, despacho preferencial para o primeiro."""
    if result.model != "M/M/s/N" or result.servers != 2:
        raise ValueError("Esta regra de despacho exige dois técnicos e população finita.")
    population = len(result.probabilities) - 1
    p_only_second = result.mu * result.probabilities[2] / (
        result.mu + (population - 1)*result.lam
    )
    p_both = state_range(result, 2)
    return p_both + result.probabilities[1] - p_only_second, p_both + p_only_second
