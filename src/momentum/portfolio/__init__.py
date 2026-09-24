"""Capa de cartera: convierte una selección en pesos objetivo.

La construcción de los pesos (proporcionales al momentum, con tope por empresa)
es trabajo de M4. Lo que sí vive ya aquí es `validate_weights`, que enuncia los
invariantes que M4 tendrá que cumplir. Está escrito antes que la
implementación a propósito: así el criterio no se puede "ajustar" luego para
que el resultado encaje.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol

from momentum.selection import Selection
from momentum.types import Symbol

#: Margen de tolerancia al comprobar que los pesos suman 1. Es holgura para el
#: error de coma flotante, no permiso para desviarse.
WEIGHT_TOLERANCE = 1e-9


class InvalidWeights(ValueError):
    """Los pesos propuestos incumplen algún invariante de la cartera."""


class PortfolioBuilder(Protocol):
    """Contrato de la capa de cartera."""

    def weights(
        self,
        selection: Selection,
        stock_scores: Mapping[Symbol, float],
    ) -> dict[Symbol, float]:
        """Pesos objetivo por símbolo. Suman 1, o 0 si se está en liquidez."""
        ...


def validate_weights(weights: Mapping[Symbol, float], max_weight: float) -> None:
    """Comprueba los invariantes de una cartera objetivo.

    Lanza `InvalidWeights` si alguno se incumple:

    * ningún peso negativo (el bot no va corto);
    * ningún peso por encima del tope por empresa;
    * la suma es 1 (invertido) o 0 (en liquidez), nunca algo intermedio ni
      mayor que 1, porque eso sería apalancarse.
    """
    for symbol, weight in weights.items():
        if weight < 0:
            raise InvalidWeights(f"Peso negativo en {symbol}: {weight}. El bot no va corto.")
        if weight > max_weight + WEIGHT_TOLERANCE:
            raise InvalidWeights(
                f"{symbol} pesa {weight}, por encima del tope por empresa {max_weight}."
            )

    total = sum(weights.values())
    if abs(total) <= WEIGHT_TOLERANCE:
        return
    if abs(total - 1.0) > WEIGHT_TOLERANCE:
        raise InvalidWeights(
            f"Los pesos suman {total}. Tienen que sumar 1 (invertido) o 0 (en liquidez)."
        )
