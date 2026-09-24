"""Capa de señales: convierte precios en números comparables.

Dos familias de señal, con la misma forma:

* **momentum de empresa** — 12-1 y 6-1 meses: la rentabilidad de los últimos 12
  (o 6) meses saltándose el mes más reciente. El salto es intencionado: el
  último mes tiende a revertir y ensucia la señal.
* **tendencia de mercado** — si un índice está o no en tendencia alcista, que es
  lo que decide qué mercados son elegibles.

`None` no es cero. `None` significa "no tengo datos suficientes para puntuar
esto", y una empresa sin histórico suficiente no compite. Si `None` se
convirtiera en cero, competiría, y ganaría a todas las que van mal.

Pendiente de M3. Aquí sólo vive el contrato.
"""

from __future__ import annotations

from datetime import date
from typing import Protocol

from momentum.types import PriceSeries


class MomentumModel(Protocol):
    """Puntúa el momentum de un valor."""

    def score(self, prices: PriceSeries, as_of: date) -> float | None:
        """Puntuación en `as_of`, o `None` si no hay histórico suficiente.

        Prohibido mirar barras posteriores a `as_of`: empieza por
        `prices.up_to(as_of)`.
        """
        ...


class TrendModel(Protocol):
    """Mide la tendencia de un mercado a partir de la serie de su índice."""

    def score(self, index_prices: PriceSeries, as_of: date) -> float | None:
        """Puntuación de tendencia en `as_of`, o `None` si no hay histórico."""
        ...

    def is_eligible(self, index_prices: PriceSeries, as_of: date) -> bool:
        """`True` si el mercado supera el filtro de tendencia de `config.yaml`.

        Separado de `score` a propósito: una cosa es ordenar los mercados entre
        sí y otra decidir si alguno merece siquiera estar invertido.
        """
        ...
