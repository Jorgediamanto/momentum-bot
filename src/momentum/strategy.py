"""La estrategia vista desde fuera: un día entra, unos pesos salen.

Esta es la costura que permite que el backtest (M5) y el runner diario (M8)
sean **el mismo código recorrido de dos formas distintas**: el backtest llama a
`decide()` una vez por cada día histórico, el runner lo llama una vez, para
hoy. Si ambos comparten esta interfaz, lo que se prueba en el backtest es
exactamente lo que se ejecutaría en producción.

La estrategia de verdad —la que compone universo, señales, selección y
cartera— es el resultado de los hitos M1 a M4. Aquí sólo está el contrato.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from typing import Protocol

from momentum.types import Market, Symbol


@dataclass(frozen=True, slots=True)
class Decision:
    """Qué cartera se quiere tener al cierre de `as_of`, y por qué.

    `reason` es obligatorio y se guarda. Una decisión que no se sabe explicar
    no se puede auditar, y auditar decisiones pasadas es la mitad del valor de
    este proyecto.
    """

    as_of: date
    weights: Mapping[Symbol, float]
    reason: str
    market: Market | None = None


class Strategy(Protocol):
    """Contrato entre las capas de decisión y los dos motores que las recorren."""

    def decide(self, as_of: date) -> Decision:
        """Cartera objetivo para `as_of`, sin mirar nada posterior a esa fecha."""
        ...
