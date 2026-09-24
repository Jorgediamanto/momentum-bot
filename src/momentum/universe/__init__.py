"""Capa de universo: quién formaba parte de un índice en una fecha dada.

Esta es la capa donde es más fácil engañarse. Preguntar "¿qué empresas están
hoy en el S&P 500?" y usar esa lista para un backtest de hace diez años produce
**sesgo de supervivencia**: se evalúan sólo las que sobrevivieron, el resultado
sale bonito y es mentira.

Por eso la interfaz obliga a pasar `as_of`. Una implementación que devuelva
siempre la misma lista al menos lo estará haciendo de forma visible, y tendrá
que declararlo (ver M2 en `IDEAS.md`).

Pendiente de M2. Aquí sólo vive el contrato.
"""

from __future__ import annotations

from datetime import date
from typing import Protocol

from momentum.types import Market, Symbol


class UniverseUnavailable(RuntimeError):
    """No se puede saber quién componía ese índice en esa fecha."""


class UniverseSource(Protocol):
    """Contrato de la capa de universo."""

    def constituents(self, market: Market, as_of: date) -> tuple[Symbol, ...]:
        """Los valores que componían `market` el día `as_of`.

        Prohibido mirar composiciones posteriores a `as_of`.
        """
        ...

    def has_survivorship_bias(self) -> bool:
        """`True` si esta fuente no sabe reconstruir la composición histórica.

        Está en la interfaz, y no en un comentario, para que los informes
        puedan preguntarlo y avisar al lector. Una limitación que el código
        conoce es una limitación que se puede imprimir.
        """
        ...
