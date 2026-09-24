"""La fuente de precios en CSV lee bien y avisa claro cuando no puede leer."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from momentum.data import PriceUnavailable
from momentum.data.csv_source import CsvPriceSource
from momentum.types import Symbol

AAA = Symbol("AAA")
TODO_2024 = (date(2024, 1, 1), date(2024, 12, 31))


def test_lee_una_serie_completa(fixtures_dir: Path) -> None:
    fuente = CsvPriceSource(fixtures_dir / "prices" / "flat")

    serie = fuente.bars(AAA, *TODO_2024)

    assert len(serie) == 65
    assert serie.days[0] == date(2024, 1, 1)
    assert serie.bars[0].close == Decimal("100.00")


def test_recorta_por_rango_de_fechas(fixtures_dir: Path) -> None:
    fuente = CsvPriceSource(fixtures_dir / "prices" / "flat")

    serie = fuente.bars(AAA, date(2024, 2, 1), date(2024, 2, 29))

    assert all(date(2024, 2, 1) <= d <= date(2024, 2, 29) for d in serie.days)
    assert len(serie) == 21


def test_si_no_hay_fichero_lo_dice(tmp_path: Path) -> None:
    fuente = CsvPriceSource(tmp_path)

    with pytest.raises(PriceUnavailable, match="No hay fichero"):
        fuente.bars(AAA, *TODO_2024)


def test_si_faltan_columnas_lo_dice(tmp_path: Path) -> None:
    (tmp_path / "AAA.csv").write_text("date,close\n2024-01-01,100.00\n", encoding="utf-8")
    fuente = CsvPriceSource(tmp_path)

    with pytest.raises(PriceUnavailable, match="faltan columnas"):
        fuente.bars(AAA, *TODO_2024)


def test_si_una_linea_esta_corrupta_lo_dice_con_su_numero(tmp_path: Path) -> None:
    (tmp_path / "AAA.csv").write_text(
        "date,open,high,low,close,volume\n"
        "2024-01-01,100.00,101.00,99.00,100.00,1000\n"
        "2024-01-02,100.00,101.00,99.00,ochenta,1000\n",
        encoding="utf-8",
    )
    fuente = CsvPriceSource(tmp_path)

    with pytest.raises(PriceUnavailable, match="Línea 3"):
        fuente.bars(AAA, *TODO_2024)
