"""El bróker de papel lleva las cuentas exactas y se niega a lo imposible."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from momentum.data import PriceUnavailable
from momentum.execution import (
    InsufficientCash,
    InsufficientShares,
    Order,
    PaperBroker,
    Side,
    equity,
    holdings_value,
)
from momentum.types import Symbol, money

DIA = date(2024, 1, 2)
AAA = Symbol("AAA")


def _orden(side: Side, cantidad: str, precio: str) -> Order:
    return Order(day=DIA, symbol=AAA, side=side, quantity=Decimal(cantidad), price=Decimal(precio))


def test_comprar_descuenta_la_caja_y_abre_posicion() -> None:
    broker = PaperBroker(money("1000.00"))

    broker.submit(_orden(Side.BUY, "3", "100.00"))

    assert broker.cash() == money("700.00")
    assert broker.positions()[AAA].quantity == Decimal("3")
    assert broker.positions()[AAA].average_price == Decimal("100.00")


def test_el_precio_medio_se_promedia_al_ampliar_la_posicion() -> None:
    broker = PaperBroker(money("1000.00"))

    broker.submit(_orden(Side.BUY, "1", "100.00"))
    broker.submit(_orden(Side.BUY, "1", "200.00"))

    assert broker.positions()[AAA].quantity == Decimal("2")
    assert broker.positions()[AAA].average_price == Decimal("150.00")


def test_vender_devuelve_la_caja_y_cierra_la_posicion() -> None:
    broker = PaperBroker(money("1000.00"))
    broker.submit(_orden(Side.BUY, "3", "100.00"))

    broker.submit(_orden(Side.SELL, "3", "110.00"))

    assert broker.cash() == money("1030.00")
    assert broker.positions() == {}


def test_no_se_puede_comprar_sin_caja() -> None:
    broker = PaperBroker(money("50.00"))

    with pytest.raises(InsufficientCash):
        broker.submit(_orden(Side.BUY, "1", "100.00"))

    assert broker.cash() == money("50.00")


def test_no_se_puede_vender_lo_que_no_se_tiene() -> None:
    """El bot no va corto. Vender de más no es un error redondeable."""
    broker = PaperBroker(money("1000.00"))
    broker.submit(_orden(Side.BUY, "1", "100.00"))

    with pytest.raises(InsufficientShares):
        broker.submit(_orden(Side.SELL, "2", "100.00"))


def test_una_orden_de_cantidad_cero_no_es_una_orden() -> None:
    with pytest.raises(ValueError, match="Cantidad"):
        _orden(Side.BUY, "0", "100.00")


def test_el_patrimonio_es_caja_mas_posiciones() -> None:
    broker = PaperBroker(money("1000.00"))
    broker.submit(_orden(Side.BUY, "3", "100.00"))

    def precio(symbol: Symbol, day: date) -> Decimal | None:
        return Decimal("120.00")

    assert holdings_value(broker, precio, DIA) == money("360.00")
    assert equity(broker, precio, DIA) == money("1060.00")


def test_sin_precio_no_se_valora_la_cartera_a_ojo() -> None:
    """Valorar con un número inventado contamina todas las decisiones siguientes."""
    broker = PaperBroker(money("1000.00"))
    broker.submit(_orden(Side.BUY, "3", "100.00"))

    def sin_precio(symbol: Symbol, day: date) -> Decimal | None:
        return None

    with pytest.raises(PriceUnavailable):
        equity(broker, sin_precio, DIA)
