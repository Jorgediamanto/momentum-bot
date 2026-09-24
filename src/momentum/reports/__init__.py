"""Capa de informes: convierte un backtest en algo que una persona puede juzgar.

Un informe que sólo enseña lo que salió bien no informa: convence. Por eso las
secciones obligatorias están escritas aquí, en el código, y no como un buen
propósito en un documento. M7 tendrá que producirlas todas.

La primera línea del informe no la elige quien lo escribe: si la estrategia
pierde contra comprar el índice, la primera línea lo dice.

Pendiente de M7. Aquí sólo vive el contrato.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from momentum.backtest import BacktestResult

#: Referencias contra las que todo informe se compara. No son opcionales.
BENCHMARKS = (
    "comprar el índice cada mes",
    "MTUM",
    "elegir mercado al azar",
)

#: Secciones que todo informe tiene que contener.
REQUIRED_SECTIONS = (
    "veredicto",
    "metricas",
    "drawdowns",
    "rotacion",
    "impuestos",
    "limitaciones",
)


class ReportBuilder(Protocol):
    """Contrato de la capa de informes."""

    def build(self, run: BacktestResult, out_dir: Path) -> Path:
        """Genera el informe y devuelve la ruta del HTML producido."""
        ...
