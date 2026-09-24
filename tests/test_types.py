"""Tipos básicos: el dinero es exacto y las series no dejan mirar al futuro."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from momentum.types import Bar, PriceSeries, Symbol, money


def _bar(dia: int, cierre: str) -> Bar:
    precio = Decimal(cierre)
    return Bar(
        day=date(2024, 1, dia),
        open=precio,
        high=precio,
        low=precio,
        close=precio,
        volume=1000,
    )


def test_el_dinero_se_redondea_al_centimo() -> None:
    assert money("300") == Decimal("300.00")
    assert money("10.005") == Decimal("10.01")


def test_el_dinero_no_se_puede_construir_desde_un_float() -> None:
    """`Decimal(0.1)` no vale 0,10 y el error se arrastraría sin avisar."""
    with pytest.raises(TypeError, match="float"):
        money(0.1)  # type: ignore[arg-type]


def test_una_serie_desordenada_no_se_acepta() -> None:
    with pytest.raises(ValueError, match="ordenada"):
        PriceSeries(Symbol("AAA"), (_bar(3, "10"), _bar(2, "10")))


def test_una_serie_con_fechas_repetidas_no_se_acepta() -> None:
    with pytest.raises(ValueError, match="repetidas"):
        PriceSeries(Symbol("AAA"), (_bar(2, "10"), _bar(2, "11")))


def test_up_to_recorta_el_futuro() -> None:
    serie = PriceSeries(Symbol("AAA"), (_bar(1, "10"), _bar(2, "11"), _bar(3, "12")))

    recortada = serie.up_to(date(2024, 1, 2))

    assert len(recortada) == 2
    assert recortada.days == (date(2024, 1, 1), date(2024, 1, 2))


def test_on_devuelve_none_si_ese_dia_no_se_nego() -> None:
    serie = PriceSeries(Symbol("AAA"), (_bar(1, "10"), _bar(3, "12")))

    assert serie.on(date(2024, 1, 2)) is None
    assert serie.on(date(2024, 1, 3)) is not None


def test_last_close_es_el_ultimo_conocido_y_nunca_el_siguiente() -> None:
    serie = PriceSeries(Symbol("AAA"), (_bar(1, "10"), _bar(3, "12")))

    assert serie.last_close(date(2024, 1, 2)) == Decimal("10")
    assert serie.last_close(date(2024, 1, 3)) == Decimal("12")


def test_last_close_devuelve_none_si_no_hay_nada_antes() -> None:
    serie = PriceSeries(Symbol("AAA"), (_bar(5, "10"),))

    assert serie.last_close(date(2024, 1, 1)) is None
