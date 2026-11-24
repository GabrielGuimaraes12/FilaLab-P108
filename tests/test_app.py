from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def calculate(app):
    next(b for b in app.button if b.label == "Calcular resultados").click().run()
    assert not app.exception


@pytest.mark.parametrize("selection", [
    "Sem limite de capacidade", "Com capacidade máxima (K)",
    "Com população finita (N)", "Atendimento variável (M/G/1)", "Com classes de prioridade",
])
def test_each_model_calculates(selection):
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    next(r for r in app.radio if r.label == "Tipo de problema").set_value(selection).run()
    if selection == "Atendimento variável (M/G/1)":
        sigma = app.number_input(key="_input_M/G/1_sigma")
        assert sigma.value is None
        calculate(app)
        assert "Informe o desvio-padrão" in app.error[0].value
        app.number_input(key="_input_M/G/1_sigma").set_value(0.0).run()
    calculate(app)
    assert not app.error
    assert app.dataframe if selection == "Com classes de prioridade" else app.metric


def test_inputs_preserved_and_units_converted():
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    app.number_input(key="_input_M/M/s_lambda").set_value(3.0).run()
    calculate(app)
    app.selectbox(key="global_unit").set_value("minuto").run()
    assert app.number_input(key="_input_M/M/s_lambda").value == pytest.approx(.05)
    assert app.warning
    for section in ["Guia manual", "Probabilidades Poisson", "Ferramentas de cálculo"]:
        app.radio(key="main_section").set_value(section).run()
        assert not app.exception
    app.radio(key="main_section").set_value("Calculadora de filas").run()
    assert app.number_input(key="_input_M/M/s_lambda").value == pytest.approx(.05)
    calculate(app)



def test_priority_comparison_keeps_both_configurations():
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    next(r for r in app.radio if r.label == "Tipo de problema").set_value("Com classes de prioridade").run()
    calculate(app)
    app.text_input[0].set_value("Equipe A").run()
    next(b for b in app.button if b.label == "Salvar cenário atual").click().run()
    app.number_input(key="_input_Prioridades M/M/s_s").set_value(2).run()
    calculate(app)
    app.text_input[0].set_value("Equipe B").run()
    next(b for b in app.button if b.label == "Salvar cenário atual").click().run()
    comparison = app.dataframe[1].value
    assert set(zip(comparison["Cenário"], comparison["s"])) == {("Equipe A", 1), ("Equipe B", 2)}
