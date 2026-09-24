"""Fuente de precios que lee ficheros CSV de un directorio local.

No es un doble de prueba: es código de verdad. La caché local de M1 guardará
sus descargas en este mismo formato, y los tests la usan sobre
`tests/fixtures/` precisamente porque es la fuente real leyendo datos reales
guardados en disco.

Formato esperado, un fichero `<SÍMBOLO>.csv` por símbolo, con cabecera:

    date,open,high,low,close,volume
    2024-01-02,100.00,101.00,99.50,100.50,1200000

Las columnas van en inglés porque así las entregan las fuentes públicas de
precios. Los precios se suponen **ya ajustados** por splits y dividendos.
"""

from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from momentum.data import PriceUnavailable
from momentum.types import Bar, PriceSeries, Symbol

COLUMNS = ("date", "open", "high", "low", "close", "volume")


class CsvPriceSource:
    """Lee series de precios de `<root>/<símbolo>.csv`."""

    def __init__(self, root: Path) -> None:
        self._root = root

    def path_for(self, symbol: Symbol) -> Path:
        return self._root / f"{symbol}.csv"

    def bars(self, symbol: Symbol, start: date, end: date) -> PriceSeries:
        ruta = self.path_for(symbol)
        if not ruta.is_file():
            raise PriceUnavailable(f"No hay fichero de precios para {symbol} en {ruta}.")
        bars = tuple(b for b in self._read(symbol, ruta) if start <= b.day <= end)
        return PriceSeries(symbol, bars)

    def fx(self, pair: str, start: date, end: date) -> PriceSeries:
        """El tipo de cambio se guarda como un símbolo más, p. ej. `EURUSD.csv`."""
        return self.bars(Symbol(pair), start, end)

    def _read(self, symbol: Symbol, ruta: Path) -> list[Bar]:
        with ruta.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            faltan = set(COLUMNS) - set(reader.fieldnames or ())
            if faltan:
                columnas = ", ".join(sorted(faltan))
                raise PriceUnavailable(f"A {ruta} le faltan columnas: {columnas}.")
            return [self._to_bar(symbol, row, ruta, numero) for numero, row in enumerate(reader, 2)]

    @staticmethod
    def _to_bar(symbol: Symbol, row: dict[str, str], ruta: Path, numero: int) -> Bar:
        try:
            return Bar(
                day=date.fromisoformat(row["date"]),
                open=Decimal(row["open"]),
                high=Decimal(row["high"]),
                low=Decimal(row["low"]),
                close=Decimal(row["close"]),
                volume=int(row["volume"]),
            )
        except (ValueError, InvalidOperation, KeyError) as exc:
            raise PriceUnavailable(
                f"Línea {numero} de {ruta} ilegible para {symbol}: {exc}"
            ) from exc
