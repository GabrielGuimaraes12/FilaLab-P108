"""FilaLab — interface orientada a problemas para teoria das filas (P108)."""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from engine import mg1, mm_s, mm_sk, mm_sn, priorities_m1
from tools_page import render_tools
from guide import render_guide, render_poisson
from converters import convert_rate, convert_time
from results_ui import render_extras

st.set_page_config(page_title="FilaLab | Otimização II", page_icon="📊", layout="wide")
st.markdown("""
<style>
.block-container{max-width:1250px;padding-top:1.7rem;padding-bottom:3rem}
.hero{background:linear-gradient(115deg,#19365a,#102237);border:1px solid #385477;border-radius:20px;padding:25px 29px;margin:0 0 19px}
.hero h1{color:#f4f8ff;letter-spacing:-.05em;margin:0;font-size:2.4rem}.hero p{color:#c1d0e5;margin:.35rem 0 0}
.pill{display:inline-block;padding:4px 11px;border-radius:40px;background:#193a5b;color:#dcecff;border:1px solid #426586;font-size:.8rem;margin-bottom:10px}
.modelcard{background:#182e48;border:1px solid #385371;border-radius:14px;padding:17px 20px;margin:10px 0 20px}
.modelcard strong{color:#f5faff;font-size:1.1rem}.modelcard p{color:#c8d8e9;margin:6px 0 0}
[data-testid="stMetric"]{background:#192c45;border:1px solid #344b66;padding:15px;border-radius:14px}
[data-testid="stForm"]{border:1px solid #37495f;border-radius:18px;padding:19px}
[data-testid="stSidebar"]{border-right:1px solid #2b4058}
</style>
""", unsafe_allow_html=True)

MODELS = {
    "Sem limite de capacidade": ("M/M/s", "Chegadas e atendimentos aleatórios, com fila sem limite de vagas."),
    "Com capacidade máxima (K)": ("M/M/s/K", "O sistema comporta somente K pessoas, contando quem está em atendimento."),
    "Com população finita (N)": ("M/M/s/N", "Há N fontes que podem solicitar serviço, como máquinas sujeitas a falhas."),
    "Atendimento variável (M/G/1)": ("M/G/1", "Um servidor com tempo de serviço genérico. Informe o desvio-padrão do atendimento."),
    "Com classes de prioridade": ("Prioridades M/M/1", "Servidores idênticos atendem classes por ordem de prioridade, com ou sem interrupção e retomada."),
}

st.markdown('<div class="hero"><span class="pill">P108 · Otimização II</span><h1>FilaLab</h1><p>Calculadora de filas e guia de fórmulas · v2.0</p></div>', unsafe_allow_html=True)

def change_unit():
    current = st.session_state.global_unit
    previous = st.session_state.input_unit
    for model_name, fields in st.session_state.get("saved_inputs", {}).items():
        for field, value in fields.items():
            if field in ("lambda", "mu") or field.startswith("class_") and field != "class_count":
                fields[field] = convert_rate(value, previous, current)
            elif field == "sigma":
                fields[field] = convert_time(value, previous, current)
        for field in ("lambda", "mu_rate", "mu_time", "sigma", *(f"class_{i}" for i in range(5))):
            st.session_state.pop(f"_input_{model_name}_{field}", None)
    st.session_state.input_unit = current


st.session_state.setdefault("input_unit", "hora")
with st.sidebar:
    st.markdown("### Navegação")
    st.caption("1. Escolha o cenário · 2. Informe os dados · 3. Analise o resultado")
    st.divider()
    section = st.radio("Área", ["Calculadora de filas", "Guia manual", "Probabilidades Poisson", "Ferramentas de cálculo", "Revisão das listas"], key="main_section")
    unit = st.selectbox("Unidade de tempo do modelo", ["hora", "minuto", "dia", "segundo"], key="global_unit", on_change=change_unit, help="Todas as taxas dos modelos devem se referir à mesma unidade de tempo.")
    st.info("**Dica:** λ é a taxa de chegada; μ é a taxa de atendimento **de cada servidor**.")
    st.caption("Nos modelos com população finita, λ corresponde à taxa de cada fonte que está disponível.")

if section == "Revisão das listas":
    report = Path(__file__).with_name("REVISAO_P108.md")
    st.markdown(report.read_text(encoding="utf-8"))
    st.stop()

if section == "Guia manual":
    render_guide(unit)
    st.stop()

if section == "Probabilidades Poisson":
    render_poisson(unit)
    st.stop()

if section == "Ferramentas de cálculo":
    render_tools()
    st.stop()

st.markdown("### 1. Qual situação você deseja analisar?")
selection = st.radio("Tipo de problema", list(MODELS), horizontal=False, label_visibility="visible")
model, description = MODELS[selection]
st.markdown(f'<div class="modelcard"><strong>{model}</strong><p>{description}</p></div>', unsafe_allow_html=True)

if model in ("M/M/s", "M/M/s/K", "M/M/s/N"):
    st.caption("O número de servidores é ajustável: com s = 1, o modelo corresponde a M/M/1 (ou sua versão com K/N).")

st.markdown("### 2. Preencha os parâmetros")
st.caption("💾 Os valores são preservados ao trocar de modelo ou de μ para 1/μ durante esta sessão.")

# Streamlit exclui o estado de um widget quando ele deixa de ser exibido.
# Os valores definitivos ficam em saved_inputs, separados por modelo; os widgets
# temporários (_field_...) podem ser removidos sem perda de informações.
if "saved_inputs" not in st.session_state:
    st.session_state.saved_inputs = {}

saved = st.session_state.saved_inputs.setdefault(model, {})

def remember(field, widget_key, transform=None):
    value = st.session_state[widget_key]
    saved[field] = transform(value) if transform else value


def numeric(field, label, default, *, min_value=0.0, step=0.25, fmt="%.10g", help=None, max_value=None, transform=None):
    key = f"_input_{model}_{field}"
    # Inicializar a cada vez que o widget reaparece; não reinicializar se já existe.
    if key not in st.session_state:
        st.session_state[key] = saved.get(field, default)
    saved.setdefault(field, st.session_state[key])
    kwargs = {"min_value": min_value, "step": step, "format": fmt,
              "key": key, "help": help,
              "on_change": remember, "args": (field, key, transform)}
    if max_value is not None:
        kwargs["max_value"] = max_value
    return st.number_input(label, **kwargs)

def change_mode():
    remember("entry_mode", mode_key)
    # Remove the widget for the newly selected representation so that its
    # value is recomputed from the canonical saved μ when it is rendered.
    target = "mu_rate" if st.session_state[mode_key].startswith("Taxa") else "mu_time"
    st.session_state.pop(f"_input_{model}_{target}", None)

mode_key = f"_mode_{model}"
if mode_key not in st.session_state:
    st.session_state[mode_key] = saved.get("entry_mode", "Taxa de atendimento (μ)")

st.markdown("**Como deseja informar o atendimento?**")
rate_mode = st.radio(
    "Forma de entrada",
    ["Taxa de atendimento (μ)", "Tempo médio por atendimento (1/μ)"],
    horizontal=True, key=mode_key,
    on_change=change_mode,
)

# μ é a fonte da verdade: alternar para 1/μ exibe o recíproco sem apagar valores.
mu_saved = saved.setdefault("mu", 3.0)
a, b = st.columns(2)
with a:
    if model != "Prioridades M/M/1":
        lambda_value = numeric("lambda", f"Chegadas por {unit} (λ)", 2.0,
            help="Média de chegadas por unidade de tempo. Em M/M/s/N, taxa de cada fonte disponível.")
    else:
        lambda_value = None

    if rate_mode.startswith("Taxa"):
        rate_key = f"_input_{model}_mu_rate"
        if rate_key not in st.session_state:
            st.session_state[rate_key] = mu_saved
        mu = st.number_input(f"Atendimentos por servidor por {unit} (μ)",
            min_value=1e-12, step=0.25, format="%.10g", key=rate_key,
            help="Taxa de serviço de cada servidor.",
            on_change=remember, args=("mu", rate_key))
    else:
        time_key = f"_input_{model}_mu_time"
        # A cada mudança de modo, atualizar o espelho usando μ preservado.
        # O valor salvo do modo anterior é atualizado no callback do próprio campo.
        if time_key not in st.session_state:
            st.session_state[time_key] = 1.0 / mu_saved
        service_time = st.number_input(f"Tempo médio por atendimento ({unit})",
            min_value=1e-12, step=0.05, format="%.10g", key=time_key,
            help="Tempo médio para um único atendimento. μ = 1 / tempo médio.",
            on_change=remember, args=("mu", time_key, lambda t: 1.0 / t))
        mu = 1.0 / service_time
        st.caption(f"Taxa equivalente: μ = {mu:.6f} atendimentos/{unit}")

with b:
    s = numeric("s", "Servidores em paralelo (s)", 2,
        min_value=1, max_value=100, step=1, fmt="%d",
        help="Quantidade de servidores simultâneos.") if model in ("M/M/s", "M/M/s/K", "M/M/s/N") else 1
    K = numeric("K", "Capacidade TOTAL do sistema (K)", 5,
        min_value=1, max_value=1000, step=1, fmt="%d",
        help="Inclui clientes atendidos e na fila.") if model == "M/M/s/K" else None
    N = numeric("N", "Número de fontes / população (N)", 10,
        min_value=1, max_value=1000, step=1, fmt="%d",
        help="Total de fontes que podem solicitar atendimento.") if model == "M/M/s/N" else None
    sigma = numeric("sigma", f"Desvio-padrão do atendimento (σ, {unit})", 0.3333,
        step=0.05, help="σ=0 representa tempo de atendimento constante.") if model == "M/G/1" else None

if model == "Prioridades M/M/1":
    s = numeric("s", "Servidores de prioridade (s)", 1, min_value=1, max_value=100, step=1, fmt="%d")
    st.markdown("**Chegadas por prioridade (1 = prioridade mais alta)**")
    count_key = f"_count_{model}"
    if count_key not in st.session_state:
        st.session_state[count_key] = saved.get("class_count", 3)
    class_count = st.selectbox("Número de classes", [2, 3, 4, 5],
        key=count_key, on_change=remember, args=("class_count", count_key))
    clscols = st.columns(class_count)
    defaults = [0.2, 0.6, 1.2, 0.1, 0.1]
    rates = []
    for i, col in enumerate(clscols):
        with col:
            rates.append(numeric(f"class_{i}", f"Classe {i+1} (λ{i+1})", defaults[i],
                step=0.1, help="Chegadas desta classe por unidade de tempo."))
    priority_key = f"_rule_{model}"
    if priority_key not in st.session_state:
        st.session_state[priority_key] = saved.get("rule", "Sem interrupção")
    preemptive = st.radio("Regra de atendimento", ["Sem interrupção", "Com interrupção"],
        horizontal=True, key=priority_key, on_change=remember,
        args=("rule", priority_key),
        help="Com interrupção: clientes de maior prioridade podem interromper atendimentos em andamento.") == "Com interrupção"

st.caption(f"Taxas em clientes/{unit}. Tempos de espera em {unit}(s).")
if model == "M/G/1":
    st.caption("Confira σ antes de calcular. A média sozinha não determina a espera. Use σ=0 apenas se o serviço for constante.")
parameters_now = dict(lam=lambda_value, mu=mu, s=int(s), K=K, N=N, sigma=sigma)
if model == "Prioridades M/M/1":
    parameters_now.update(rates=rates, preemptive=preemptive)
submitted = st.button("Calcular resultados", type="primary", use_container_width=True)

if not submitted and "last_result" not in st.session_state:
    st.info("Preencha os campos acima e clique em **Calcular resultados**. O painel exibirá os indicadores e gráficos do seu cenário.")
    st.stop()

if submitted:
    try:
        if model == "M/M/s/K" and K < s:
            raise ValueError("A capacidade total K deve ser maior ou igual ao número de servidores s.")
        if model == "M/M/s/N" and N < s:
            raise ValueError("A população N deve ser maior ou igual ao número de servidores s.")
        if model == "Prioridades M/M/1":
            answer = priorities_m1(rates, mu, preemptive, int(s))
        elif model == "M/M/s":
            answer = mm_s(lambda_value, mu, int(s))
        elif model == "M/M/s/K":
            answer = mm_sk(lambda_value, mu, int(s), int(K))
        elif model == "M/M/s/N":
            answer = mm_sn(lambda_value, mu, int(s), int(N))
        else:
            answer = mg1(lambda_value, mu, sigma)
        st.session_state.last_result = (model, answer, unit, parameters_now)
    except ValueError as exc:
        st.error(f"Não foi possível calcular: {exc}")
        st.stop()

previous_model, answer, result_unit, parameters = st.session_state.last_result
if previous_model != model or result_unit != unit or parameters_now != parameters:
    st.warning("Você alterou os parâmetros. Clique em **Calcular resultados** para atualizar o painel.")
    st.stop()

st.divider()
st.markdown("### 3. Resultados e interpretação")
if previous_model == "Prioridades M/M/1":
    df = pd.DataFrame(answer)
    st.dataframe(df.rename(columns={"classe": "Classe", "lambda": "λ", "W": "W", "Wq": "Wq", "L": "L", "Lq": "Lq"}), hide_index=True, use_container_width=True)
    st.plotly_chart(px.bar(df, x="classe", y="Wq", title="Espera média na fila por classe", labels={"classe": "Classe de prioridade", "Wq": f"Tempo ({result_unit})"}), use_container_width=True)
    st.caption("As métricas representam cada classe individualmente. Com retomada, Wq inclui o tempo de interrupção. Classes com λ=0 não têm observações.")
    export = df.to_csv(index=False).encode("utf-8-sig")
else:
    r = answer
    row1 = st.columns(4)
    for col, (name, value, info) in zip(row1, [
        ("Wq · espera na fila", r.Wq, result_unit),
        ("W · tempo total", r.W, result_unit),
        ("Lq · pessoas na fila", r.Lq, "pessoas"),
        ("L · pessoas no sistema", r.L, "pessoas"),
    ]):
        col.metric(name, f"{value:.4f}", help=f"Medido em {info}.")
    row2 = st.columns(4)
    row2[0].metric("Carga nominal ρ", f"{r.rho:.1%}")
    row2[1].metric("P₀ · sistema vazio", f"{r.p0:.2%}")
    row2[2].metric("Taxa efetiva", f"{r.effective_rate:.4f}/{result_unit}")
    row2[3].metric("Bloqueio Pₖ", f"{r.blocking:.2%}" if previous_model == "M/M/s/K" else "Não aplicável")
    if previous_model == "M/M/s/N":
        st.caption("Na população finita, ρ é a carga nominal Nλ/(sμ) e não a ocupação real. A taxa efetiva considera somente as fontes disponíveis.")
    if previous_model == "M/M/s/K":
        st.caption("Um sistema com capacidade limitada pode operar mesmo quando ρ ≥ 1, pois novas chegadas são bloqueadas ao atingir K.")
    left, right = st.columns([1.4, 1])
    with left:
        if r.probabilities is not None:
            probs = pd.DataFrame({"Número de clientes no sistema": range(len(r.probabilities)), "Probabilidade": r.probabilities})
            st.plotly_chart(px.bar(probs, x="Número de clientes no sistema", y="Probabilidade", title="Distribuição P(n)"), use_container_width=True)
            if previous_model == "M/M/s":
                st.caption("Distribuição ilustrada para os primeiros estados; a cauda pode continuar após o último valor mostrado.")
        else:
            st.info("Para M/G/1, a distribuição completa P(n) depende de mais informações sobre os tempos de serviço.")
    with right:
        st.markdown("#### O que significam os resultados?")
        st.write(f"Em média, **{r.Lq:.2f}** clientes aguardam na fila por **{r.Wq:.2f} {result_unit}(s)**.")
        st.write(f"A permanência total média é de **{r.W:.2f} {result_unit}(s)**.")
        if r.explanation:
            st.info(r.explanation)
        st.markdown("**Lei de Little**")
        st.latex(r"L=\lambda_{ef}W\qquad L_q=\lambda_{ef}W_q")
    with st.expander("Detalhes da substituição matemática", expanded=False):
        st.write(f"λ = {parameters['lam']} · μ = {parameters['mu']:.6f} · s = {parameters['s']}")
        if previous_model == "M/M/s/K":
            st.write(f"K = {parameters['K']}; taxa efetiva = λ × (1 − Pₖ) = {r.effective_rate:.6f}")
        elif previous_model == "M/M/s/N":
            st.write(f"N = {parameters['N']}; taxa efetiva = λ × (N − L) = {r.effective_rate:.6f}")
        elif previous_model == "M/G/1":
            st.write(f"σ = {parameters['sigma']}")
            st.latex(r"L_q=\frac{\lambda^2\sigma^2+\rho^2}{2(1-\rho)}")
        st.write(f"Wq = Lq / λ efetiva = {r.Wq:.6f}; W = L / λ efetiva = {r.W:.6f}")
        st.caption("Com λ = 0, W representa o tempo hipotético de serviço de uma chegada eventual.")
    render_extras(r, result_unit, parameters)
    export = pd.DataFrame([{
        "modelo": previous_model, "lambda": parameters["lam"], "mu": parameters["mu"], "s": parameters["s"],
        "K": parameters["K"], "N": parameters["N"], "sigma": parameters["sigma"],
        "L": r.L, "Lq": r.Lq, "W": r.W, "Wq": r.Wq, "rho": r.rho, "P0": r.p0,
        "lambda_efetiva": r.effective_rate, "bloqueio": r.blocking,
    }]).to_csv(index=False).encode("utf-8-sig")

st.download_button("Exportar resultados em CSV", export, file_name="filalab_resultados.csv", mime="text/csv")
with st.expander("Glossário dos símbolos"):
    st.markdown("**λ**: taxa de chegada; **μ**: atendimento por servidor; **s**: servidores em paralelo; **K**: capacidade total (fila + atendimento); **N**: população finita; **σ**: desvio-padrão do tempo de serviço; **L/Lq**: número médio no sistema/na fila; **W/Wq**: tempo médio no sistema/na fila; **P₀**: chance de sistema vazio.")




