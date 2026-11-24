"""Ferramentas de cálculo independentes, com cópia e envio explicitamente autorizado."""
import streamlit as st
from converters import (SECONDS, convert_time, convert_rate, convert_variance,
                        rate_to_time, time_to_rate, sigma_from_variance,
                        variance_from_sigma, parse_observations, observed_stats)

UNITS = list(SECONDS)
MODEL_NAMES = ["M/M/s", "M/M/s/K", "M/M/s/N", "M/G/1", "Prioridades M/M/s"]


def fmt(value):
    return f"{value:,.8f}".rstrip('0').rstrip('.').replace(',', '_').replace('.', ',').replace('_', '.')


def send_to_model(value, source_unit, kind, key):
    """Normalize rates and standard deviations to the selected calculator unit."""
    target_model = st.session_state[f"{key}_model"]
    target_unit = st.session_state['global_unit']
    if kind == 'mu':
        normalized = convert_rate(value, source_unit, target_unit)
    elif kind == 'lambda':
        normalized = convert_rate(value, source_unit, target_unit)
    elif kind == 'sigma':
        normalized = convert_time(value, source_unit, target_unit)
    else:
        raise ValueError('Tipo de parâmetro inválido')
    saved = st.session_state.setdefault('saved_inputs', {}).setdefault(target_model, {})
    saved[kind] = normalized
    if kind == 'mu':
        # Alteração futura aparece em ambos os modos de entrada.
        st.session_state.pop(f'_input_{target_model}_mu_rate', None)
        st.session_state.pop(f'_input_{target_model}_mu_time', None)
    else:
        st.session_state.pop(f'_input_{target_model}_{kind}', None)
    return target_model, normalized


def send_widget(value, unit, kind, key):
    if kind == 'sigma':
        models = ['M/G/1']
    elif kind == 'lambda':
        models = [x for x in MODEL_NAMES if x != 'Prioridades M/M/s']
    else:
        models = MODEL_NAMES
    with st.expander('Enviar resultado a um modelo (opcional)', expanded=False):
        st.caption('Só altera o parâmetro escolhido após clicar em **Enviar**. Os demais dados ficam preservados.')
        st.selectbox('Modelo de destino', models, key=f'{key}_model')
        if st.button('Enviar resultado', key=f'{key}_send', type='secondary'):
            model, normalized = send_to_model(value, unit, kind, key)
            st.success(f'{kind} de {model} atualizado: {fmt(normalized)} na unidade {st.session_state["global_unit"]}. Abra a Calculadora para conferir.')


def render_tools():
    st.markdown('### Ferramentas de cálculo')
    st.caption('Converta unidades sem modificar os exercícios. Os dados ficam preservados durante a sessão.')
    tool = st.radio('Escolha uma ferramenta',
        ['Tempo', 'Taxas', 'μ ↔ 1/μ', 'Variância e σ', 'Tempos observados'],
        horizontal=True, key='converter_selected')
    st.divider()
    if tool in ('Tempo', 'Taxas', 'Variância e σ'):
        col1, col2, col3 = st.columns([1.2, 1, 1])
        with col1:
            number = st.number_input('Valor para converter', min_value=0.0, value=15.0, step=0.25, format='%.6f', key=f'conv_{tool}_value')
        with col2:
            origin = st.selectbox('De', UNITS, index=1, key=f'conv_{tool}_from')
        with col3:
            target = st.selectbox('Para', UNITS, index=2, key=f'conv_{tool}_to')
        if tool == 'Tempo':
            result = convert_time(number, origin, target)
            suffix = target
            st.latex(r't_{destino}=t_{origem}\cdot\frac{segundos\ por\ unidade_{origem}}{segundos\ por\ unidade_{destino}}')
        elif tool == 'Taxas':
            result = convert_rate(number, origin, target)
            suffix = f'eventos/{target}'
            st.latex(r'\lambda_{destino}=\lambda_{origem}\cdot\frac{segundos\ por\ unidade_{destino}}{segundos\ por\ unidade_{origem}}')
        else:
            variance_kind = st.radio('O valor representa', ['Variância (σ²)', 'Desvio-padrão (σ)'], horizontal=True, key='conv_var_kind')
            if variance_kind.startswith('Variância'):
                result = convert_variance(number, origin, target)
                suffix = f'{target}²'
                st.caption('Variância é tempo ao quadrado: o fator de conversão também é elevado ao quadrado.')
            else:
                result = convert_time(number, origin, target)
                suffix = target
        st.metric('Resultado convertido', f'{fmt(result)} {suffix}')
        if tool == 'Taxas':
            send_widget(result, target, 'lambda', 'send_conv_rate')
        elif tool == 'Variância e σ':
            if variance_kind.startswith('Variância'):
                sigma = sigma_from_variance(result)
                st.info(f'Desvio-padrão correspondente: **σ = {fmt(sigma)} {target}**')
                send_widget(sigma, target, 'sigma', 'send_conv_variance')
            else:
                st.info(f'Variância correspondente: **σ² = {fmt(variance_from_sigma(result))} {target}²**')
                send_widget(result, target, 'sigma', 'send_conv_variance')
        else:
            st.info('Para informar μ ao modelo a partir de um tempo, use a ferramenta **μ ↔ 1/μ**.')
    elif tool == 'μ ↔ 1/μ':
        direction = st.radio('Sentido da conversão', ['Tempo médio → taxa μ', 'Taxa μ → tempo médio'], horizontal=True, key='conv_reciprocal_dir')
        c1, c2, c3 = st.columns(3)
        with c1:
            value = st.number_input('Valor informado', min_value=0.000001, value=15.0, format='%.6f', key=f'conv_reciprocal_{direction}')
        with c2:
            origin = st.selectbox('Unidade de entrada', UNITS, index=1 if direction.startswith('Tempo') else 2, key=f'conv_reciprocal_from_{direction}')
        with c3:
            target = st.selectbox('Unidade de saída', UNITS, index=2 if direction.startswith('Tempo') else 1, key=f'conv_reciprocal_to_{direction}')
        if direction.startswith('Tempo'):
            result = time_to_rate(value, origin, target)
            st.metric('Taxa de atendimento μ', f'{fmt(result)} atendimentos/{target}')
            send_widget(result, target, 'mu', 'reciprocal_to_mu')
        else:
            result = rate_to_time(value, origin, target)
            st.metric('Tempo médio 1/μ', f'{fmt(result)} {target}')
            st.info('O equivalente de μ pode ser enviado aos parâmetros do modelo.')
            rate = convert_rate(value, origin, st.session_state['global_unit'])
            send_widget(rate, st.session_state['global_unit'], 'mu', 'reciprocal_from_mu')
        st.latex(r'\text{Tempo médio}=\frac{1}{\mu}\quad\text{(com unidades compatíveis)}')
    else:
        st.markdown('**Cole os tempos de atendimento** — um valor por linha ou separados por `;`.')
        st.caption('Use vírgula como separador decimal: `2,5` significa dois e meio.')
        text = st.text_area('Tempos observados', value='4\n6\n8\n10\n12', height=135, key='converter_observations')
        c1, c2 = st.columns(2)
        with c1:
            unit = st.selectbox('Unidade dos tempos', UNITS, index=1, key='converter_obs_unit')
        with c2:
            sample = st.toggle('Dados representam uma amostra (n−1)', key='converter_obs_sample')
        try:
            values = parse_observations(text)
            mean, variance, sigma = observed_stats(values, sample)
            m1, m2, m3 = st.columns(3)
            m1.metric('Média', f'{fmt(mean)} {unit}')
            m2.metric('Variância', f'{fmt(variance)} {unit}²')
            m3.metric('Desvio-padrão σ', f'{fmt(sigma)} {unit}')
            st.caption(f'{len(values)} observações. Para o modelo M/G/1, use σ e mantenha a unidade compatível com μ.')
            send_widget(sigma, unit, 'sigma', 'sigma_observations')
        except ValueError as exc:
            st.warning(str(exc))
    st.divider()
    st.caption('Os resultados desta área não alteram nenhum modelo, salvo se você clicar explicitamente em “Enviar resultado”.')
