"""Capa de selección: decide en qué mercado se invierte y qué valores se compran.

El resultado lleva siempre un `reason` en texto legible. No es decoración: es
lo que el dashboard enseña cada día en "qué mercado se eligió y por qué", y lo
que permite auditar una decisión seis meses después sin volver a ejecutar nada.

Pendiente de M4. Aquí viven el contrato y el objeto que viaja a la capa de
cartera.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from typing import Protocol

from momentum.types import Market, Symbol


@dataclass(frozen=True, slots=True)
class Selection:
    """Qué se ha decidido para un día concreto.

    `market is None` significa quedarse en liquidez: ningún mercado superó el
    filtro de tendencia. Es una decisión legítima, no un fallo.
    """

    as_of: date
    market: Market | None
    symbols: tuple[Symbol, ...]
    reason: str

    @property
    def in_cash(self) -> bool:
        return self.market is None


class Selector(Protocol):
    """Contrato de la capa de selección."""

    def select(
        self,
        market_scores: Mapping[Market, float | None],
        stock_scores: Mapping[Symbol, float],
        as_of: date,
    ) -> Selection:
        """Elige mercado ganador y los `top_n` mejores valores de ese mercado."""
        ...
