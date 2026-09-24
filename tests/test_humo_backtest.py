"""Test de humo: un backtest corto de extremo a extremo sobre fixtures.

No comprueba que la estrategia sea buena —todavía no hay estrategia—, sino tres
cosas que tienen que ser ciertas desde el primer día y seguir siéndolo siempre:

1. el tren de capas arranca y llega hasta el final;
2. el dinero no se crea ni se destruye;
3. dos ejecuciones idénticas dan exactamente el mismo resultado.

El escenario de precios planos es el que permite ser tajante: si los precios no
se mueven, el patrimonio final tiene que ser **exactamente** lo aportado, al
céntimo. Cualquier céntimo de diferencia es un error de contabilidad.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from momentum.backtest import BacktestResult, run_backtest
from momentum.data.csv_source import CsvPriceSource
from momentum.execution import PaperBroker
from momentum.types import PriceSeries, Symbol, money
from tests.fakes import FixedWeightStrategy, price_lookup

pytestmark = pytest.mark.smoke

AAA = Symbol("AAA")
BBB = Symbol("BBB")

#: Reparto fijo. La estrategia de verdad llega en M4; aquí se prueba el motor.
PESOS = {AAA: 0.6, BBB: 0.4}
TOPE_POR_EMPRESA = 0.6

APORTACION = money("300.00")
DIA_DE_APORTACION = 1


def _series(carpeta: Path) -> dict[Symbol, PriceSeries]:
    fuente = CsvPriceSource(carpeta)
    rango = (date(2024, 1, 1), date(2024, 12, 31))
    return {simbolo: fuente.bars(simbolo, *rango) for simbolo in (AAA, BBB)}


def _ejecutar(carpeta: Path) -> tuple[BacktestResult, PaperBroker]:
    series = _series(carpeta)
    broker = PaperBroker()
    resultado = run_backtest(
        trading_days=series[AAA].days,
        strategy=FixedWeightStrategy(PESOS),
        broker=broker,
        price_at=price_lookup(series),
        contribution=APORTACION,
        contribution_day=DIA_DE_APORTACION,
        max_weight=TOPE_POR_EMPRESA,
    )
    return resultado, broker


def test_con_precios_planos_el_patrimonio_final_es_exactamente_lo_aportado(
    fixtures_dir: Path,
) -> None:
    resultado, _ = _ejecutar(fixtures_dir / "prices" / "flat")

    # Tres meses de fixture, una aportación al mes.
    assert resultado.total_contributed == money("900.00")
    assert resultado.final_equity == money("900.00")


def test_el_backtest_llega_hasta_el_final_y_opera(fixtures_dir: Path) -> None:
    resultado, broker = _ejecutar(fixtures_dir / "prices" / "trend")

    assert len(resultado.days) == 65
    assert sum(dia.trades for dia in resultado.days) > 0
    assert len(broker.fills) > 0
    assert all(dia.reason for dia in resultado.days), "todo día registra por qué hizo lo que hizo"


def test_cada_dia_el_patrimonio_es_caja_mas_posiciones(fixtures_dir: Path) -> None:
    resultado, _ = _ejecutar(fixtures_dir / "prices" / "trend")

    for dia in resultado.days:
        assert dia.equity is not None
        assert dia.holdings_value is not None
        assert dia.equity == money(dia.cash + dia.holdings_value)


def test_la_caja_final_cuadra_con_aportaciones_y_operaciones(fixtures_dir: Path) -> None:
    """La caja sólo cambia por dos motivos: lo que se ingresa y lo que se opera."""
    resultado, broker = _ejecutar(fixtures_dir / "prices" / "trend")

    movido_al_operar = sum((fill.cash_delta for fill in resultado.fills), start=money(0))

    assert broker.cash() == money(resultado.total_contributed + movido_al_operar)


def test_dos_ejecuciones_iguales_dan_el_mismo_resultado(fixtures_dir: Path) -> None:
    """Sin determinismo no se puede auditar nada de lo que el bot decida."""
    primera, _ = _ejecutar(fixtures_dir / "prices" / "trend")
    segunda, _ = _ejecutar(fixtures_dir / "prices" / "trend")

    assert primera.days == segunda.days
    assert primera.fills == segunda.fills
