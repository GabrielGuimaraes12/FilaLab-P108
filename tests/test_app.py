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
    for section in ["Guia manual", "Probabilidades Poisson", "Ferramentas de cálculo", "Revisão das listas"]:
        app.radio(key="main_section").set_value(section).run()
        assert not app.exception
    app.radio(key="main_section").set_value("Calculadora de filas").run()
    assert app.number_input(key="_input_M/M/s_lambda").value == pytest.approx(.05)
    calculate(app)
