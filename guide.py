"""Guia de substituição manual e ferramentas de probabilidades."""
import streamlit as st

from analysis_tools import inverse_mg1, poisson_range

GUIDES = {
    "M/M/s": (
        "Chegadas Poisson, serviço exponencial em cada servidor e fila ilimitada. Exige λ < sμ.",
        [
            r"a=\lambda/\mu,\quad \rho=a/s,\quad w_n=a^n/n!\quad(0\le n\le s)",
            r"P_0=\left[\sum_{n=0}^{s-1}w_n+w_s/(1-\rho)\right]^{-1}",
            r"P_n=P_0w_n\ (n<s),\qquad P_{s+j}=P_0w_s\rho^j",
            r"C=P_0w_s/(1-\rho),\quad L_q=C\rho/(1-\rho),\quad L=L_q+a",
            r"P(W_q>t)=Ce^{-(s\mu-\lambda)t}\quad (t\ge0,\ \mathrm{FCFS})",
            r"s=1:\quad W=1/(\mu-\lambda),\quad \mu=\lambda+1/W,\quad \lambda=\rho^2/[(1-\rho)W_q]",
        ],
    ),
    "M/M/s/K": (
        "Chegadas Poisson externas e sistema com K vagas totais. Se o enunciado dá somente as vagas de espera, some s. Equilíbrio possível também com λ≥sμ.",
        [
            r"w_0=1,\quad w_n=w_{n-1}\lambda/[\min(n,s)\mu],\quad P_n=w_n/\sum_{j=0}^{K}w_j",
            r"P_{\mathrm{bloq}}=P_K,\quad \lambda_{ef}=\lambda(1-P_K),\quad \lambda_{\mathrm{perdida}}=\lambda P_K",
            r"L=\sum nP_n,\quad L_q=\sum \max(n-s,0)P_n",
            r"P(\mathrm{esperar}\mid\mathrm{admitido})=\frac{\sum_{n=s}^{K-1}P_n}{1-P_K}",
            r"\lambda=\lambda_{ef}/(1-P_K)\quad\text{se }P_K\text{ for conhecido}",
        ],
    ),
    "M/M/s/N": (
        "Há N fontes. Cada fonte fora da fila e do atendimento gera demanda à taxa λ. O fluxo de chegadas depende do estado.",
        [
            r"\lambda_n=(N-n)\lambda,\quad w_0=1,\quad w_n=w_{n-1}\lambda_{n-1}/[\min(n,s)\mu]",
            r"P_n=w_n/\sum_{j=0}^{N}w_j,\quad L=\sum nP_n,\quad L_q=\sum \max(n-s,0)P_n",
            r"\lambda_{ef}=\lambda(N-L),\quad A=(N-L)/N,\quad \lambda=\lambda_{ef}/(N-L)",
            r"P_{\mathrm{chegada}}(n)=\lambda_nP_n/\lambda_{ef}",
        ],
    ),
    "M/G/1": (
        "Chegadas Poisson e um servidor com distribuição de serviço geral. Informe a média e a variância ou desvio-padrão. Exige λ<μ.",
        [
            r"E[S]=1/\mu,\quad E[S^2]=\sigma^2+1/\mu^2,\quad \rho=\lambda/\mu,\quad P_0=1-\rho",
            r"W_q=\frac{\lambda E[S^2]}{2(1-\rho)},\quad L_q=\frac{\lambda^2\sigma^2+\rho^2}{2(1-\rho)}",
            r"\rho=\sqrt{L_q^2+2L_q-(\lambda\sigma)^2}-L_q,\quad \mu=\lambda/\rho",
            r"\sigma=\frac{\sqrt{2L_q(1-\rho)-\rho^2}}{\lambda}",
        ],
    ),
    "Prioridades M/M/1": (
        "Servidores idênticos, serviço exponencial com μ comum e chegadas Poisson por classe. A classe 1 tem maior prioridade. Exige Σλᵢ<sμ.",
        [
            r"R_i=\sum_{j=1}^i \lambda_j/(s\mu),\quad R_0=0,\quad D_i=(1-R_{i-1})(1-R_i)",
            r"\mathrm{Sem\ interrup\c{c}\tilde{a}o}:\quad W_{q,i}=C/(s\mu D_i),\quad W_i=W_{q,i}+1/\mu",
            r"\mathrm{Com\ retomada}:\quad L_{q,i}=L_q(\Lambda_i)-L_q(\Lambda_{i-1}),\quad W_{q,i}=L_{q,i}/\lambda_i",
            r"W_i=W_{q,i}+1/\mu,\quad L_i=\lambda_iW_i,\quad L_{q,i}=\lambda_iW_{q,i}",
        ],
    ),
}


def render_guide(unit):
    st.header("Guia manual")
    model = st.selectbox("Modelo da fórmula", list(GUIDES))
    condition, formulas = GUIDES[model]
    st.subheader("Quando usar")
    st.write(condition)
    st.subheader("Fórmulas")
    for formula in formulas:
        st.latex(formula)
    if model != "Prioridades M/M/1":
        st.latex(r"L=\lambda_{ef}W,\quad L_q=\lambda_{ef}W_q,\quad W=W_q+1/\mu")
        st.caption("Sem bloqueio ou população finita, λ efetiva = λ. Para inverter a Lei de Little, divida o número médio pelo tempo correspondente. Em M/G/1, a raiz inversa precisa ser real e resultar em 0<ρ<1.")
    if model == "M/G/1":
        with st.expander("Calcular μ a partir de λ, Lq e σ"):
            a, b, c = st.columns(3)
            lam = a.number_input(f"λ por {unit}", min_value=0.0, value=3.0, key="inv_lam")
            lq = b.number_input("Lq informado", min_value=0.0, value=2.0, key="inv_lq")
            sigma = c.number_input(f"σ em {unit}", min_value=0.0, value=0.0, key="inv_sigma")
            try:
                st.metric("μ para os dados informados", f"{inverse_mg1(lam, lq, sigma):.6g}/{unit}")
            except ValueError as exc:
                st.warning(str(exc))


def render_poisson(unit):
    st.header("Probabilidade de chegadas Poisson")
    st.write("Use para contar eventos em um intervalo com taxa constante e incrementos independentes.")
    st.latex(r"m=\lambda t,\qquad P(X=k)=e^{-m}m^k/k!")
    st.caption("Para exatamente k, use k nos dois limites. Para ao menos k, consulte a cauda superior.")
    a, b = st.columns(2)
    rate = a.number_input(f"Taxa por {unit}", min_value=0.0, value=3.0)
    duration = b.number_input(f"Duração em {unit}", min_value=0.0, value=1.0)
    tail = st.checkbox("Sem limite superior")
    low = a.number_input("Limite inferior inclusivo", min_value=0, max_value=100000, value=0)
    high = None if tail else b.number_input("Limite superior inclusivo", min_value=0, max_value=100000, value=2)
    try:
        st.metric("Probabilidade", f"{poisson_range(rate*duration, low, high):.8%}")
    except ValueError as exc:
        st.warning(str(exc))



