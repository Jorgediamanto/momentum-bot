"""La configuración se carga bien y se niega a arrancar si es incoherente."""

from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml

from momentum.config import ConfigError, load_config
from momentum.types import Market


def _con_cambios(
    repo_root: Path, tmp_path: Path, cambiar: Callable[[dict[str, Any]], None]
) -> Path:
    """Copia config.yaml aplicando un cambio, para probar la validación."""
    with (repo_root / "config.yaml").open(encoding="utf-8") as handle:
        raw: dict[str, Any] = yaml.safe_load(handle)
    cambiar(raw)
    destino = tmp_path / "config.yaml"
    with destino.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(raw, handle, allow_unicode=True)
    return destino


def test_carga_la_configuracion_real(repo_root: Path) -> None:
    config = load_config(repo_root / "config.yaml")

    assert set(config.markets) == set(Market)
    assert config.base_currency == "EUR"
    assert config.execution.broker == "paper"


def test_los_importes_se_leen_como_decimal_exacto(repo_root: Path) -> None:
    config = load_config(repo_root / "config.yaml")

    # Si esto fuera un float, 300.00 no valdría exactamente 300 y las cuentas
    # del backtest no cuadrarían al céntimo.
    assert config.contributions.amount == Decimal("300.00")
    assert isinstance(config.contributions.amount, Decimal)


def test_el_numero_de_valores_tiene_que_caber_entre_el_minimo_y_el_maximo(
    repo_root: Path,
) -> None:
    config = load_config(repo_root / "config.yaml")
    assert config.selection.min_n <= config.selection.top_n <= config.selection.max_n


def test_rechaza_un_broker_que_no_sea_de_papel(repo_root: Path, tmp_path: Path) -> None:
    ruta = _con_cambios(repo_root, tmp_path, lambda raw: raw["execution"].update(broker="ibkr"))

    with pytest.raises(ConfigError, match="paper"):
        load_config(ruta)


def test_rechaza_un_top_n_fuera_de_rango(repo_root: Path, tmp_path: Path) -> None:
    ruta = _con_cambios(repo_root, tmp_path, lambda raw: raw["selection"].update(top_n=500))

    with pytest.raises(ConfigError, match="top_n"):
        load_config(ruta)


def test_rechaza_pesos_de_momentum_que_no_suman_uno(repo_root: Path, tmp_path: Path) -> None:
    def romper(raw: dict[str, Any]) -> None:
        raw["momentum"]["windows"][0]["weight"] = 0.9

    ruta = _con_cambios(repo_root, tmp_path, romper)

    with pytest.raises(ConfigError, match="suman"):
        load_config(ruta)


def test_rechaza_un_importe_escrito_como_numero_decimal(repo_root: Path, tmp_path: Path) -> None:
    """Un importe sin comillas llega como float y perdería exactitud."""

    def romper(raw: dict[str, Any]) -> None:
        raw["contributions"]["amount"] = 300.0

    ruta = _con_cambios(repo_root, tmp_path, romper)

    with pytest.raises(ConfigError, match="comillas"):
        load_config(ruta)


def test_rechaza_un_tope_por_empresa_que_impide_invertir_todo(
    repo_root: Path, tmp_path: Path
) -> None:
    def romper(raw: dict[str, Any]) -> None:
        raw["selection"]["top_n"] = 20
        raw["portfolio"]["max_weight_per_stock"] = 0.01  # 20 x 1 % = 20 %

    ruta = _con_cambios(repo_root, tmp_path, romper)

    with pytest.raises(ConfigError, match="capital"):
        load_config(ruta)


def test_avisa_si_falta_el_fichero(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="No encuentro"):
        load_config(tmp_path / "no_existe.yaml")
