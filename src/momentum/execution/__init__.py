"""Capa de ejecución: la interfaz `Broker` y la única implementación que habrá.

**Aquí no hay ni habrá brókers reales.** Ni APIs, ni credenciales, ni claves.
`PaperBroker` opera sobre dinero imaginario y es lo único que este repositorio
va a contener. Si algún día hay conexión real, se hará a mano y fuera de aquí.
Ver `SPEC.md`, "Qué NO hace", y `CLAUDE.md`, reglas inviolables.

El `PaperBroker` de M0 vive en memoria y es deliberadamente simple: sin
comisiones, sin slippage y sin persistencia. Los costes entran en M5 y la
persistencia en SQLite con claves de idempotencia entra en M8.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Protocol

from momentum.data import PriceLookup, PriceUnavailable
from momentum.types import ZERO, Symbol, money


class Side(StrEnum):
    BUY = "buy"
    SELL = "sell"


class InsufficientCash(RuntimeError):
    """No hay caja suficiente para pagar la orden."""


class InsufficientShares(RuntimeError):
    """No se pueden vender más acciones de las que se tienen. El bot no va corto."""


@dataclass(frozen=True, slots=True)
class Order:
    """Una orden a mercado, con el precio de referencia del día."""

    day: date
    symbol: Symbol
    side: Side
    quantity: Decimal
    price: Decimal

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError(f"Cantidad no positiva en la orden de {self.symbol}.")
        if self.price <= 0:
            raise ValueError(f"Precio no positivo en la orden de {self.symbol}.")


@dataclass(frozen=True, slots=True)
class Fill:
    """Una orden ya ejecutada. `cash_delta` es negativo en las compras."""

    day: date
    symbol: Symbol
    side: Side
    quantity: Decimal
    price: Decimal
    cash_delta: Decimal


@dataclass(frozen=True, slots=True)
class Position:
    """Una posición abierta.

    `average_price` sirve para valorar y para informes. La contabilidad FIFO
    real, con sus lotes individuales, la necesita M6 y no se puede reconstruir
    a partir de una media: cuando llegue M6 habrá que guardar los lotes.
    """

    symbol: Symbol
    quantity: Decimal
    average_price: Decimal

    @property
    def cost_basis(self) -> Decimal:
        return money(self.quantity * self.average_price)


class Broker(Protocol):
    """Contrato de la capa de ejecución."""

    def cash(self) -> Decimal: ...

    def positions(self) -> Mapping[Symbol, Position]: ...

    def submit(self, order: Order) -> Fill: ...


class PaperBroker:
    """Bróker de papel en memoria. Dinero imaginario, cuentas exactas."""

    def __init__(self, cash: Decimal = ZERO) -> None:
        self._cash = money(cash)
        self._positions: dict[Symbol, Position] = {}
        self._fills: list[Fill] = []

    # -- consulta ----------------------------------------------------------- #

    def cash(self) -> Decimal:
        return self._cash

    def positions(self) -> Mapping[Symbol, Position]:
        return dict(self._positions)

    @property
    def fills(self) -> tuple[Fill, ...]:
        return tuple(self._fills)

    # -- movimientos -------------------------------------------------------- #

    def deposit(self, amount: Decimal) -> None:
        """Ingresa la aportación periódica."""
        if amount <= 0:
            raise ValueError("Una aportación tiene que ser positiva.")
        self._cash = money(self._cash + amount)

    def submit(self, order: Order) -> Fill:
        if order.side is Side.BUY:
            return self._buy(order)
        return self._sell(order)

    def _buy(self, order: Order) -> Fill:
        importe = money(order.quantity * order.price)
        if importe > self._cash:
            raise InsufficientCash(
                f"{order.symbol}: la compra cuesta {importe} y sólo hay {self._cash}."
            )
        self._cash = money(self._cash - importe)

        actual = self._positions.get(order.symbol)
        if actual is None:
            self._positions[order.symbol] = Position(order.symbol, order.quantity, order.price)
        else:
            cantidad = actual.quantity + order.quantity
            coste = actual.quantity * actual.average_price + importe
            self._positions[order.symbol] = Position(order.symbol, cantidad, coste / cantidad)

        return self._record(order, -importe)

    def _sell(self, order: Order) -> Fill:
        actual = self._positions.get(order.symbol)
        disponible = actual.quantity if actual else Decimal(0)
        if order.quantity > disponible:
            raise InsufficientShares(
                f"{order.symbol}: se intentan vender {order.quantity} y sólo hay {disponible}."
            )
        assert actual is not None  # lo garantiza la comprobación de arriba

        importe = money(order.quantity * order.price)
        self._cash = money(self._cash + importe)

        restante = actual.quantity - order.quantity
        if restante == 0:
            del self._positions[order.symbol]
        else:
            self._positions[order.symbol] = Position(order.symbol, restante, actual.average_price)

        return self._record(order, importe)

    def _record(self, order: Order, cash_delta: Decimal) -> Fill:
        fill = Fill(
            day=order.day,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=order.price,
            cash_delta=cash_delta,
        )
        self._fills.append(fill)
        return fill


def holdings_value(broker: Broker, price_at: PriceLookup, day: date) -> Decimal:
    """Valor de mercado de las posiciones abiertas.

    Si falta el precio de algo que se tiene en cartera, lanza `PriceUnavailable`
    en vez de valorarlo a ojo: una valoración inventada contamina todas las
    decisiones posteriores.
    """
    total = ZERO
    for symbol, position in broker.positions().items():
        precio = price_at(symbol, day)
        if precio is None:
            raise PriceUnavailable(f"Sin precio de {symbol} el {day} para valorar la cartera.")
        total += position.quantity * precio
    return money(total)


def equity(broker: Broker, price_at: PriceLookup, day: date) -> Decimal:
    """Patrimonio total: caja más valor de mercado de las posiciones."""
    return money(broker.cash() + holdings_value(broker, price_at, day))
