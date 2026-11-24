"""Consultas ligadas ao resultado e comparação de cenários."""
import pandas as pd
import streamlit as st

from analysis_tools import arrival_wait, finite_source_time_tail, operating_cost, state_range, time_tail, two_technician_occupancy


def render_extras(result, unit, parameters):
    r = result
    busy = r.effective_rate / r.mu
    st.subheader("Ocupação e probabilidades")
    columns = st.columns(3)
    columns[0].metric("Servidores ocupados em média", f"{busy:.4f}")
    columns[1].metric("Ocupação média por servidor", f"{busy/r.servers:.2%}")
    columns[2].metric("Admitidos que esperam", f"{arrival_wait(r):.2%}" if r.effective_rate else "—")
    st.caption("Com encaminhamento simétrico, a média por servidor vale para cada técnico.")
    if r.model == "M/M/s/N":
        population = parameters["N"]
        st.write(f"Fontes operando em média **{population-r.L:.4f}** · disponibilidade por fonte **{(population-r.L)/population:.2%}** · intervalo médio entre reparos concluídos **{1/r.effective_rate:.4g} {unit}(s)**" if r.effective_rate else "Todas as fontes operam quando λ=0.")
        with st.expander("Quantidade de técnicos ocupados"):
            st.write("P(B≥j) indica a frequência com pelo menos j técnicos ocupados. As probabilidades individuais exigem acompanhar a identidade dos técnicos no estado.")
            st.dataframe(pd.DataFrame({"Técnicos simultaneamente ocupados (pelo menos)": range(1, r.servers+1),
                                       "Probabilidade": [state_range(r, n) for n in range(1, r.servers+1)]}), hide_index=True)
        if r.servers == 2:
            first, second = two_technician_occupancy(r)
            with st.expander("Comparar a ocupação individual de dois técnicos"):
                st.caption("Com despacho preferencial ao técnico 1 e sem transferência de reparos em andamento.")
                a, b = st.columns(2)
                a.metric("Técnico 1", f"{first:.2%}")
                b.metric("Técnico 2", f"{second:.2%}")
    if r.probabilities is not None:
        with st.expander("Consultar uma probabilidade de contagem"):
            measure = st.radio("Contar", ["No sistema", "Somente na fila"], horizontal=True)
            a, b = st.columns(2)
            low = a.number_input("De", min_value=0, max_value=100000, value=0, key="state_low")
            open_end = a.checkbox("Sem limite superior", key="state_tail")
            high = None if open_end else b.number_input("Até", min_value=0, max_value=100000, value=2, key="state_high")
            if high is not None and high < low:
                st.warning("O limite superior precisa ser maior ou igual ao inferior.")
            else:
                if measure == "Somente na fila":
                    low = low + r.servers if low else 0
                    high = high + r.servers if high is not None else None
                st.metric("Probabilidade do intervalo", f"{state_range(r, low, high):.6%}")
    tail = None
    if r.model == "M/M/s":
        tail = time_tail
    elif r.model == "M/M/s/N" and r.servers == 1 and r.effective_rate:
        tail = finite_source_time_tail
    if tail is not None:
        with st.expander("Probabilidade de exceder um tempo"):
            t = st.number_input(f"Tempo limite em {unit}(s)", min_value=0.0, value=0.5)
            a, b = st.columns(2)
            a.metric("P(Wq > limite)", f"{tail(r, t):.6%}")
            b.metric("P(W > limite)", f"{tail(r, t, total=True):.6%}")
    render_costs_and_scenarios(r, unit, parameters)


def render_costs_and_scenarios(r, unit, parameters):
    with st.expander("Custos do cenário"):
        a, b, c, d = st.columns(4)
        staff = a.number_input(f"R$ por servidor/{unit}", min_value=0.0)
        customer = b.number_input(f"R$ por cliente/{unit}", min_value=0.0)
        loss = c.number_input("R$ por chegada bloqueada", min_value=0.0, disabled=r.model != "M/M/s/K")
        duration = d.number_input(f"Duração em {unit}(s)", min_value=0.0, value=1.0)
        base = st.radio("Custo de clientes", ["No sistema", "Somente na fila"], horizontal=True)
        paid = st.radio("Custo da equipe", ["Turno inteiro", "Somente tempo ocupado"], horizontal=True)
        cost = duration * operating_cost(
            r.servers if paid == "Turno inteiro" else r.effective_rate/r.mu, staff,
            r.L if base == "No sistema" else r.Lq, customer,
            r.lam*r.blocking, loss,
        )
        st.metric("Custo esperado no período", f"R$ {cost:.4f}")
        st.caption("Compare valores calculados para a mesma duração física e os mesmos critérios de custo.")
    render_scenarios("filas", [{
        "Modelo": r.model, "Unidade": unit, "λ": r.lam, "μ": r.mu, "s": r.servers,
        "K": parameters["K"], "N": parameters["N"], "σ": parameters["sigma"],
        "L": r.L, "Lq": r.Lq, "W": r.W, "Wq": r.Wq, "R$ no período": cost, "Duração": duration,
    }])


def render_scenarios(group, rows):
    with st.expander("Comparar cenários da sessão"):
        scenarios = st.session_state.setdefault(f"scenarios_{group}", {})
        name = st.text_input("Nome do cenário", max_chars=60).strip()
        if st.button("Salvar cenário atual", disabled=not name):
            scenarios[name] = [{"Cenário": name, **row} for row in rows]
        if scenarios:
            frame = pd.DataFrame(row for scenario in scenarios.values() for row in scenario)
            st.dataframe(frame, hide_index=True)
            st.download_button("Baixar cenários em CSV", frame.to_csv(index=False).encode("utf-8-sig"), "filalab_cenarios.csv")
            remove = st.selectbox("Cenário para remover", list(scenarios))
            if st.button("Remover cenário"):
                del scenarios[remove]
                st.rerun()
