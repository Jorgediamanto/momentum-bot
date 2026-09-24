"""Tipos básicos que comparten todas las capas.

Dos decisiones que atraviesan el proyecto entero y que conviene tener presentes
al leer este módulo:

* **El dinero es `Decimal`, nunca `float`.** Un `float` no puede representar
  0,10 € exactamente, y el test de conservación del dinero de M5 tiene que
  cuadrar al céntimo. Sólo son `float` las magnitudes sin unidades:
  puntuaciones, pesos y rentabilidades.
* **`as_of` manda.** `PriceSeries.up_to()` es la herramienta con la que una capa
  se ata las manos para no mirar al futuro. Casi todo el código que lea precios
  debería empezar recortando la serie con ella.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum
from typing import NewType

#: Identificador de un valor cotizado, tal y como lo nombra la fuente de datos.
Symbol = NewType("Symbol", str)

#: Unidad mínima de dinero con la que se trabaja.
CENT = Decimal("0.01")


class Market(StrEnum):
    """Los tres mercados entre los que el bot elige uno cada día."""

    SP500 = "sp500"
    EUROPA = "europa"
    ESPANA = "espana"


def money(value: str | int | Decimal) -> Decimal:
    """Devuelve un importe redondeado al céntimo.

    Rechaza `float` a propósito: `Decimal(0.1)` no vale 0,10 y ese error se
    arrastraría en silencio hasta descuadrar las cuentas. Pásalo como cadena.
    """
    if isinstance(value, float):
        raise TypeError(
            "No construyas dinero a partir de un float: usa una cadena, "
            "por ejemplo money('300.00')."
        )
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


ZERO = money(0)


@dataclass(frozen=True, slots=True)
class Bar:
    """Una sesión de cotización, ya ajustada por splits y dividendos.

    Que los precios lleguen aquí ya ajustados es parte del contrato de la capa
    de datos: ninguna capa superior vuelve a ajustar nada.
    """

    day: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int


@dataclass(frozen=True, slots=True)
class PriceSeries:
    """Serie diaria de un símbolo, ordenada y sin fechas repetidas.

    Los días sin negociación (fines de semana, festivos) sencillamente no
    existen en la serie. Cada mercado tiene su propio calendario: no supongas
    que dos series tienen las mismas fechas ni la misma longitud.
    """

    symbol: Symbol
    bars: tuple[Bar, ...]

    def __post_init__(self) -> None:
        days = [bar.day for bar in self.bars]
        if days != sorted(days):
            raise ValueError(f"La serie de {self.symbol} no está ordenada por fecha.")
        if len(set(days)) != len(days):
            raise ValueError(f"La serie de {self.symbol} tiene fechas repetidas.")

    def __len__(self) -> int:
        return len(self.bars)

    def __iter__(self) -> Iterator[Bar]:
        return iter(self.bars)

    @property
    def days(self) -> tuple[date, ...]:
        return tuple(bar.day for bar in self.bars)

    def up_to(self, as_of: date) -> PriceSeries:
        """Recorta la serie hasta `as_of` incluido.

        Es la defensa de base contra el look-ahead: una función que trabaja
        sobre el resultado de `up_to(as_of)` no puede ver el futuro aunque
        quiera.
        """
        return PriceSeries(self.symbol, tuple(b for b in self.bars if b.day <= as_of))

    def on(self, day: date) -> Bar | None:
        """La sesión de ese día exacto, o `None` si ese día no se negoció."""
        for bar in self.bars:
            if bar.day == day:
                return bar
            if bar.day > day:
                break
        return None

    def last_close(self, as_of: date) -> Decimal | None:
        """Último cierre conocido en `as_of`, o `None` si no hay ninguno.

        Devolver `None` es deliberado: quien llama decide qué hacer sin datos.
        La política del proyecto ante la duda es no operar.
        """
        candidates = [b for b in self.bars if b.day <= as_of]
        return candidates[-1].close if candidates else None
