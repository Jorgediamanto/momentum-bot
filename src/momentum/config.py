"""Carga y validación de `config.yaml`.

`config.yaml` es el único sitio donde viven los parámetros de la estrategia.
Este módulo lo lee, lo convierte en objetos inmutables y tipados, y lo valida.

La validación no es cosmética: prefiere reventar al arrancar, con un mensaje
claro, antes que dejar correr una noche entera de trabajo sobre una
configuración incoherente.
"""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

from momentum.types import Market, money


class ConfigError(ValueError):
    """La configuración es inválida o le falta algo."""


# --------------------------------------------------------------------------- #
# Estructura
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class MarketConfig:
    key: Market
    label: str
    index: str
    currency: str


@dataclass(frozen=True, slots=True)
class MomentumWindow:
    """Rentabilidad de los últimos `months` meses saltándose `skip_months`."""

    months: int
    skip_months: int
    weight: float


@dataclass(frozen=True, slots=True)
class MomentumConfig:
    windows: tuple[MomentumWindow, ...]
    min_history_days: int


@dataclass(frozen=True, slots=True)
class TrendConfig:
    sma_days: int
    require_above_sma: bool
    lookback_months: int
    skip_months: int


@dataclass(frozen=True, slots=True)
class SelectionConfig:
    top_n: int
    min_n: int
    max_n: int
    allow_cash: bool


@dataclass(frozen=True, slots=True)
class PortfolioConfig:
    max_weight_per_stock: float
    min_weight_per_stock: float
    fractional_shares: bool
    rebalance: str


@dataclass(frozen=True, slots=True)
class ContributionsConfig:
    amount: Decimal
    currency: str
    day_of_month: int


@dataclass(frozen=True, slots=True)
class CostsConfig:
    commission_per_order: Decimal
    commission_pct: Decimal
    slippage_bps: int
    fx_spread_bps: int


@dataclass(frozen=True, slots=True)
class BacktestConfig:
    start: date
    end: date
    initial_cash: Decimal


@dataclass(frozen=True, slots=True)
class TaxBracket:
    """Tramo de la base del ahorro. `up_to = None` es el tramo final."""

    up_to: Decimal | None
    rate: Decimal


@dataclass(frozen=True, slots=True)
class TaxesConfig:
    country: str
    method: str
    wash_sale_days: int
    savings_brackets: tuple[TaxBracket, ...]


@dataclass(frozen=True, slots=True)
class ExecutionConfig:
    broker: str
    database: str


@dataclass(frozen=True, slots=True)
class Config:
    markets: Mapping[Market, MarketConfig]
    base_currency: str
    momentum: MomentumConfig
    trend: TrendConfig
    selection: SelectionConfig
    portfolio: PortfolioConfig
    contributions: ContributionsConfig
    costs: CostsConfig
    backtest: BacktestConfig
    taxes: TaxesConfig
    execution: ExecutionConfig


# --------------------------------------------------------------------------- #
# Lectura
# --------------------------------------------------------------------------- #


def _require(data: Mapping[str, Any], key: str, where: str) -> Any:
    if key not in data:
        raise ConfigError(f"Falta '{key}' en la sección '{where}' de config.yaml.")
    return data[key]


def _mapping(data: Mapping[str, Any], key: str, where: str) -> Mapping[str, Any]:
    value = _require(data, key, where)
    if not isinstance(value, Mapping):
        raise ConfigError(f"'{key}' en '{where}' debería ser un bloque de claves.")
    return value


def _sequence(data: Mapping[str, Any], key: str, where: str) -> Sequence[Any]:
    value = _require(data, key, where)
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        raise ConfigError(f"'{key}' en '{where}' debería ser una lista.")
    return value


def _as_date(value: Any, where: str) -> date:
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    raise ConfigError(f"'{where}' no es una fecha válida: {value!r}")


def _as_money(value: Any, where: str) -> Decimal:
    if isinstance(value, float):
        raise ConfigError(
            f"El importe '{where}' está escrito como número decimal. "
            "Ponlo entre comillas en config.yaml para que se lea exacto."
        )
    return money(str(value))


def _parse_market(key: str, raw: Mapping[str, Any]) -> MarketConfig:
    try:
        market = Market(key)
    except ValueError as exc:
        conocidos = ", ".join(m.value for m in Market)
        raise ConfigError(f"Mercado desconocido '{key}'. Los válidos son: {conocidos}.") from exc
    where = f"markets.{key}"
    return MarketConfig(
        key=market,
        label=str(_require(raw, "label", where)),
        index=str(_require(raw, "index", where)),
        currency=str(_require(raw, "currency", where)),
    )


def _parse_momentum(raw: Mapping[str, Any]) -> MomentumConfig:
    windows = tuple(
        MomentumWindow(
            months=int(_require(item, "months", "momentum.windows")),
            skip_months=int(_require(item, "skip_months", "momentum.windows")),
            weight=float(_require(item, "weight", "momentum.windows")),
        )
        for item in _sequence(raw, "windows", "momentum")
    )
    return MomentumConfig(
        windows=windows,
        min_history_days=int(_require(raw, "min_history_days", "momentum")),
    )


def _parse_taxes(raw: Mapping[str, Any]) -> TaxesConfig:
    brackets: list[TaxBracket] = []
    for item in _sequence(raw, "savings_brackets", "taxes"):
        limit = item.get("up_to")
        brackets.append(
            TaxBracket(
                up_to=None if limit is None else _as_money(limit, "taxes.savings_brackets.up_to"),
                rate=Decimal(str(_require(item, "rate", "taxes.savings_brackets"))),
            )
        )
    return TaxesConfig(
        country=str(_require(raw, "country", "taxes")),
        method=str(_require(raw, "method", "taxes")),
        wash_sale_days=int(_require(raw, "wash_sale_days", "taxes")),
        savings_brackets=tuple(brackets),
    )


def _build(raw: Mapping[str, Any]) -> Config:
    markets_raw = _mapping(raw, "markets", "raíz")
    markets = {
        cfg.key: cfg
        for cfg in (
            _parse_market(key, _mapping(markets_raw, key, "markets")) for key in markets_raw
        )
    }

    selection_raw = _mapping(raw, "selection", "raíz")
    portfolio_raw = _mapping(raw, "portfolio", "raíz")
    trend_raw = _mapping(raw, "trend", "raíz")
    contrib_raw = _mapping(raw, "contributions", "raíz")
    costs_raw = _mapping(raw, "costs", "raíz")
    backtest_raw = _mapping(raw, "backtest", "raíz")
    execution_raw = _mapping(raw, "execution", "raíz")

    return Config(
        markets=markets,
        base_currency=str(_require(raw, "base_currency", "raíz")),
        momentum=_parse_momentum(_mapping(raw, "momentum", "raíz")),
        trend=TrendConfig(
            sma_days=int(_require(trend_raw, "sma_days", "trend")),
            require_above_sma=bool(_require(trend_raw, "require_above_sma", "trend")),
            lookback_months=int(_require(trend_raw, "lookback_months", "trend")),
            skip_months=int(_require(trend_raw, "skip_months", "trend")),
        ),
        selection=SelectionConfig(
            top_n=int(_require(selection_raw, "top_n", "selection")),
            min_n=int(_require(selection_raw, "min_n", "selection")),
            max_n=int(_require(selection_raw, "max_n", "selection")),
            allow_cash=bool(_require(selection_raw, "allow_cash", "selection")),
        ),
        portfolio=PortfolioConfig(
            max_weight_per_stock=float(
                _require(portfolio_raw, "max_weight_per_stock", "portfolio")
            ),
            min_weight_per_stock=float(
                _require(portfolio_raw, "min_weight_per_stock", "portfolio")
            ),
            fractional_shares=bool(_require(portfolio_raw, "fractional_shares", "portfolio")),
            rebalance=str(_require(portfolio_raw, "rebalance", "portfolio")),
        ),
        contributions=ContributionsConfig(
            amount=_as_money(
                _require(contrib_raw, "amount", "contributions"), "contributions.amount"
            ),
            currency=str(_require(contrib_raw, "currency", "contributions")),
            day_of_month=int(_require(contrib_raw, "day_of_month", "contributions")),
        ),
        costs=CostsConfig(
            commission_per_order=_as_money(
                _require(costs_raw, "commission_per_order", "costs"), "costs.commission_per_order"
            ),
            commission_pct=Decimal(str(_require(costs_raw, "commission_pct", "costs"))),
            slippage_bps=int(_require(costs_raw, "slippage_bps", "costs")),
            fx_spread_bps=int(_require(costs_raw, "fx_spread_bps", "costs")),
        ),
        backtest=BacktestConfig(
            start=_as_date(_require(backtest_raw, "start", "backtest"), "backtest.start"),
            end=_as_date(_require(backtest_raw, "end", "backtest"), "backtest.end"),
            initial_cash=_as_money(
                _require(backtest_raw, "initial_cash", "backtest"), "backtest.initial_cash"
            ),
        ),
        taxes=_parse_taxes(_mapping(raw, "taxes", "raíz")),
        execution=ExecutionConfig(
            broker=str(_require(execution_raw, "broker", "execution")),
            database=str(_require(execution_raw, "database", "execution")),
        ),
    )


# --------------------------------------------------------------------------- #
# Validación
# --------------------------------------------------------------------------- #


def validate(config: Config) -> None:
    """Comprueba que la configuración es coherente. Lanza `ConfigError` si no."""
    sel = config.selection
    if not sel.min_n <= sel.top_n <= sel.max_n:
        raise ConfigError(
            f"selection.top_n ({sel.top_n}) tiene que estar entre "
            f"min_n ({sel.min_n}) y max_n ({sel.max_n})."
        )

    pesos = sum(w.weight for w in config.momentum.windows)
    if abs(pesos - 1.0) > 1e-9:
        raise ConfigError(f"Los pesos de momentum.windows suman {pesos}, deberían sumar 1.")
    for window in config.momentum.windows:
        if window.months <= window.skip_months:
            raise ConfigError(
                f"Una ventana de momentum de {window.months} meses no puede saltarse "
                f"{window.skip_months}: no quedaría nada que medir."
            )

    pf = config.portfolio
    if not 0 < pf.max_weight_per_stock <= 1:
        raise ConfigError("portfolio.max_weight_per_stock tiene que estar entre 0 y 1.")
    if not 0 <= pf.min_weight_per_stock < pf.max_weight_per_stock:
        raise ConfigError(
            "portfolio.min_weight_per_stock tiene que ser menor que max_weight_per_stock."
        )
    # Con un tope por empresa demasiado bajo sería imposible invertir el 100 %.
    if pf.max_weight_per_stock * sel.top_n < 1.0:
        raise ConfigError(
            f"Con {sel.top_n} valores y un tope de {pf.max_weight_per_stock} por empresa "
            "no se puede llegar a invertir todo el capital."
        )

    if config.backtest.start >= config.backtest.end:
        raise ConfigError("backtest.start tiene que ser anterior a backtest.end.")

    if config.contributions.amount <= 0:
        raise ConfigError("contributions.amount tiene que ser positivo.")
    if not 1 <= config.contributions.day_of_month <= 28:
        raise ConfigError(
            "contributions.day_of_month tiene que estar entre 1 y 28, para que exista "
            "en todos los meses."
        )

    # Esto no es una preferencia: es la regla inviolable del proyecto.
    if config.execution.broker != "paper":
        raise ConfigError(
            f"execution.broker es '{config.execution.broker}'. El único valor admitido "
            "es 'paper': este repositorio no opera con dinero real (ver SPEC.md)."
        )

    faltan = {m for m in Market} - set(config.markets)
    if faltan:
        nombres = ", ".join(sorted(m.value for m in faltan))
        raise ConfigError(f"Faltan mercados en config.yaml: {nombres}.")


# --------------------------------------------------------------------------- #
# Punto de entrada
# --------------------------------------------------------------------------- #

REPO_ROOT = Path(__file__).resolve().parents[2]


def default_config_path() -> Path:
    """Dónde buscar `config.yaml`: variable de entorno, directorio actual, repo."""
    desde_entorno = os.environ.get("MOMENTUM_CONFIG")
    if desde_entorno:
        return Path(desde_entorno)
    en_cwd = Path.cwd() / "config.yaml"
    if en_cwd.is_file():
        return en_cwd
    return REPO_ROOT / "config.yaml"


def load_config(path: Path | None = None) -> Config:
    """Lee, construye y valida la configuración."""
    ruta = path or default_config_path()
    if not ruta.is_file():
        raise ConfigError(f"No encuentro config.yaml en {ruta}.")
    with ruta.open(encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    if not isinstance(raw, Mapping):
        raise ConfigError(f"{ruta} no contiene un diccionario YAML.")
    config = _build(raw)
    validate(config)
    return config
