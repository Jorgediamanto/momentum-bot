"""Capa de datos: precios diarios ajustados y tipos de cambio.

Es la única capa que tiene permiso para tocar la red, y sólo a partir de M1.
Hasta entonces la única implementación es `CsvPriceSource`, que lee de disco.

Regla de la capa: si falta un dato, se dice. No se rellena, no se interpola y
no se aproxima. Quien decide qué hacer ante un hueco es la capa de robustez.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from decimal import Decimal
from typing import Protocol

from momentum.types import PriceSeries, Symbol

#: Cómo pregunta el resto del sistema por el precio de un símbolo un día dado.
#: Devuelve `None` si ese día no hay precio conocido.
PriceLookup = Callable[[Symbol, date], Decimal | None]


class PriceUnavailable(RuntimeError):
    """No hay precio para ese símbolo y esa fecha.

    Se lanza en vez de inventar un valor. Ver `SPEC.md` §3.1.
    """


class PriceSource(Protocol):
    """Contrato de la capa de datos hacia el resto del sistema."""

    def bars(self, symbol: Symbol, start: date, end: date) -> PriceSeries:
        """Serie diaria ajustada de `symbol`, entre `start` y `end` incluidos."""
        ...

    def fx(self, pair: str, start: date, end: date) -> PriceSeries:
        """Tipo de cambio como serie de precios, por ejemplo `pair='EURUSD'`."""
        ...
