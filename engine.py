"""FilaLab: stationary queueing models. Rates use a common time unit."""
from dataclasses import dataclass
import math

@dataclass
class Result:
    model: str
    lam: float
    mu: float
    servers: int
    rho: float
    p0: float
    L: float
    Lq: float
    W: float
    Wq: float
    effective_rate: float
    blocking: float = 0.0
    probabilities: list[float] | None = None
    explanation: str = ''


def _validate(lam, mu, s):
    if not all(math.isfinite(x) for x in (lam, mu, s)) or lam < 0 or mu <= 0 or int(s) != s or s < 1:
        raise ValueError('Use λ ≥ 0, μ > 0 e s inteiro ≥ 1.')


def _birth_death(births, deaths, model, lam, mu, s, rho):
    # Recursion with dynamic renormalization to avoid overflow at heavy loads.
    weights = [1.0]
    for i, birth in enumerate(births):
        w = weights[-1] * birth / deaths[i]
        weights.append(w)
        peak = max(weights)
        if peak > 1e100:
            weights = [x / peak for x in weights]
    z = math.fsum(weights)
    p = [x / z for x in weights]
    L = math.fsum(i * v for i, v in enumerate(p))
    Lq = math.fsum(max(i - s, 0) * v for i, v in enumerate(p))
    admitted_rate = math.fsum(b * p[i] for i, b in enumerate(births))
    W = L / admitted_rate if admitted_rate > 0 else 1 / mu
    Wq = Lq / admitted_rate if admitted_rate > 0 else 0
    return Result(model, lam, mu, s, rho, p[0], L, Lq, W, Wq, admitted_rate,
                  (p[-1] if 'K' in model else 0), p)


def mm_s(lam: float, mu: float, s: int = 1) -> Result:
    _validate(lam, mu, s)
    rho = lam / (s * mu)
    if rho >= 1:
        raise ValueError('Sistema sem equilíbrio: λ deve ser menor que s × μ.')
    if lam == 0:
        return Result('M/M/s', lam, mu, s, 0, 1, 0, 0, 1/mu, 0, 0, probabilities=[1])
    a = lam / mu
    # Erlang C using the normalized distribution for n < s, followed by geometric tail.
    log_weights = [0.0]
    for n in range(1, s):
        log_weights.append(log_weights[-1] + math.log(a / n))
    log_tail = log_weights[-1] + math.log(rho)
    peak = max(max(log_weights), log_tail)
    weights = [math.exp(w - peak) for w in log_weights]
    tail_start = math.exp(log_tail - peak)
    denom = math.fsum(weights) + tail_start / (1-rho)
    p0 = weights[0] / denom
    pwait = (tail_start / (1-rho)) / denom
    Lq = pwait * rho / (1-rho)
    L = Lq + a
    Wq = Lq / lam
    W = Wq + 1 / mu
    probs = [weight / denom for weight in weights]
    probs.append(tail_start / denom)
    for n in range(s + 1, 20):
        probs.append(probs[-1] * rho)
    return Result('M/M/s', lam, mu, s, rho, p0, L, Lq, W, Wq, lam,
                  probabilities=probs,
                  explanation=f'P(esperar) = {pwait:.5f} (Erlang C); Lq = P(esperar) × ρ/(1−ρ).')


def mm_sk(lam: float, mu: float, s: int, K: int) -> Result:
    _validate(lam, mu, s)
    if not isinstance(K, int) or K < s:
        raise ValueError('A capacidade total K precisa ser inteira e ≥ s.')
    births = [lam] * K
    deaths = [min(n, s) * mu for n in range(1, K+1)]
    result = _birth_death(births, deaths, 'M/M/s/K', lam, mu, s, lam/(s*mu))
    result.explanation = 'K inclui clientes em atendimento e em espera. λ efetiva = λ × (1 − PK).'
    return result


def mm_sn(per_source_lam: float, mu: float, s: int, N: int) -> Result:
    _validate(per_source_lam, mu, s)
    if not isinstance(N, int) or N < 1 or s > N:
        raise ValueError('A população N deve ser inteira e ≥ s.')
    births = [(N-n)*per_source_lam for n in range(N)]
    deaths = [min(n,s)*mu for n in range(1,N+1)]
    result = _birth_death(births, deaths, 'M/M/s/N', per_source_lam, mu, s,
                          N*per_source_lam/(s*mu))
    result.blocking = 0
    result.explanation = 'λ é a taxa por fonte disponível, não a taxa de chegada total. λ efetiva = λ × (N − L).'
    return result


def mg1(lam: float, mu: float, sigma: float) -> Result:
    _validate(lam, mu, 1)
    if not math.isfinite(sigma) or sigma < 0:
        raise ValueError('O desvio-padrão σ não pode ser negativo.')
    rho = lam / mu
    if rho >= 1:
        raise ValueError('Sistema sem equilíbrio: λ deve ser menor que μ.')
    Lq = (lam**2 * sigma**2 + rho**2) / (2*(1-rho))
    L = Lq + rho
    Wq = Lq/lam if lam else 0
    W = Wq + 1/mu
    return Result('M/G/1',lam,mu,1,rho,1-rho,L,Lq,W,Wq,lam,
                  explanation='Pollaczek–Khinchine: Lq = (λ²σ² + ρ²) / [2(1−ρ)].')



def priorities_m1(rates: list[float], mu: float, preemptive: bool, servers: int = 1) -> list[dict]:
    """Shared exponential service rate, strict priorities and resume on interruption."""
    if not rates or any(not math.isfinite(x) or x < 0 for x in rates):
        raise ValueError('Informe taxas de chegada não negativas e finitas.')
    total = math.fsum(rates)
    system = mm_s(total, mu, servers)
    erlang_c = system.Lq * (1-system.rho) / system.rho if total else 0
    out = []
    previous_rate = previous_lq = 0.0
    for i, rate in enumerate(rates):
        current_rate = previous_rate + rate
        if preemptive and rate:
            # Higher-priority subsets behave as isolated M/M/s queues.
            cumulative_lq = mm_s(current_rate, mu, servers).Lq
            Wq = max(0, cumulative_lq - previous_lq) / rate
            previous_lq = cumulative_lq
        elif preemptive:
            Wq = 0.0
        else:
            denominator = (1-previous_rate/(servers*mu))*(1-current_rate/(servers*mu))
            Wq = erlang_c / (servers*mu*denominator)
        W = Wq + 1/mu
        out.append({'classe': i+1, 'lambda': rate, 'W': W, 'Wq': Wq,
                    'L': rate*W, 'Lq': rate*Wq})
        previous_rate = current_rate
    return out
