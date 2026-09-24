"""Dobles de prueba.

Viven aquí, en `tests/`, y nunca en `src/`. `src/` es lo que se ejecuta de
verdad; si un doble se cuela ahí, antes o después alguien lo ejecuta creyendo
que es el sistema real.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from momentum.data import PriceLookup
from momentum.strategy import Decision
from momentum.types import PriceSeries, Symbol


@dataclass(frozen=True)
class FixedWeightStrategy:
    """Estrategia que siempre pide los mismos pesos.

    Sirve para probar el motor sin que la estrategia de verdad exista todavía:
    lo que se comprueba aquí es el motor, no la calidad de la señal.
    """

    weights: Mapping[Symbol, float]
    reason: str = "Pesos fijos (doble de prueba)"

    def decide(self, as_of: date) -> Decision:
        return Decision(as_of=as_of, weights=dict(self.weights), reason=self.reason)


def price_lookup(series: Mapping[Symbol, PriceSeries]) -> PriceLookup:
    """Construye un buscador de precios sobre series ya cargadas en memoria.

    Devuelve `None` si ese símbolo no cotizó ese día exacto: no arrastra el
    último precio conocido, porque eso sería inventarse un dato.
    """

    def buscar(symbol: Symbol, day: date) -> Decimal | None:
        serie = series.get(symbol)
        if serie is None:
            return None
        bar = serie.on(day)
        return bar.close if bar is not None else None

    return buscar
