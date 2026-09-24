"""Motor de backtest: recorre días, aporta, reajusta la cartera y lo apunta todo.

ESTADO: versión esqueleto (M0). Recorre los días, ingresa la aportación
mensual, lleva la cartera a sus pesos objetivo y registra el resultado. Con
eso basta para que el test de humo demuestre que el tren de capas está bien
enganchado y que el dinero no se crea ni se destruye.

Lo que le falta, y que es trabajo explícito de M5:

* comisiones y slippage (ahora se ejecuta al precio de cierre, sin coste);
* conversión EUR/USD para los mercados que no cotizan en euros;
* el test anti look-ahead completo;
* el test de conservación del dinero al céntimo con costes de por medio.

Lo que ya respeta desde ahora, porque cuesta lo mismo hacerlo bien:

* el orden de los símbolos es determinista, para que dos ejecuciones iguales
  den exactamente lo mismo;
* si falta un precio, el día se registra y **no se opera**;
* todo el dinero es `Decimal`.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_DOWN, Decimal

from momentum.data import PriceLookup, PriceUnavailable
from momentum.execution import Fill, Order, PaperBroker, Side, equity, holdings_value
from momentum.portfolio import validate_weights
from momentum.strategy import Strategy
from momentum.types import ZERO, Symbol, money


@dataclass(frozen=True, slots=True)
class DayRecord:
    """Qué pasó un día concreto.

    `holdings_value` y `equity` son `None` cuando faltó algún precio y no se
    pudo valorar la cartera. Se deja constancia del día en blanco en vez de
    inventar una valoración.
    """

    day: date
    cash: Decimal
    holdings_value: Decimal | None
    equity: Decimal | None
    contributed_today: Decimal
    trades: int
    reason: str


@dataclass(frozen=True, slots=True)
class BacktestResult:
    days: tuple[DayRecord, ...]
    total_contributed: Decimal
    final_equity: Decimal | None
    fills: tuple[Fill, ...]


def run_backtest(
    *,
    trading_days: Sequence[date],
    strategy: Strategy,
    broker: PaperBroker,
    price_at: PriceLookup,
    contribution: Decimal,
    contribution_day: int,
    max_weight: float,
) -> BacktestResult:
    """Recorre `trading_days` en orden y devuelve el registro de lo ocurrido.

    El bróker es siempre de papel. No existe otra opción y no va a existir.
    """
    registros: list[DayRecord] = []
    aportado_total = ZERO
    meses_aportados: set[tuple[int, int]] = set()

    for day in trading_days:
        aportado_hoy = _contribute(broker, day, contribution, contribution_day, meses_aportados)
        aportado_total = money(aportado_total + aportado_hoy)

        decision = strategy.decide(day)
        validate_weights(decision.weights, max_weight)

        try:
            patrimonio = equity(broker, price_at, day)
            operaciones = _rebalance(broker, decision.weights, patrimonio, price_at, day)
            valor_posiciones = holdings_value(broker, price_at, day)
            patrimonio = money(broker.cash() + valor_posiciones)
            motivo = decision.reason
        except PriceUnavailable as exc:
            operaciones = 0
            valor_posiciones = None
            patrimonio = None
            motivo = f"Sin operar, faltan datos: {exc}"

        registros.append(
            DayRecord(
                day=day,
                cash=broker.cash(),
                holdings_value=valor_posiciones,
                equity=patrimonio,
                contributed_today=aportado_hoy,
                trades=operaciones,
                reason=motivo,
            )
        )

    return BacktestResult(
        days=tuple(registros),
        total_contributed=aportado_total,
        final_equity=registros[-1].equity if registros else None,
        fills=broker.fills,
    )


def _contribute(
    broker: PaperBroker,
    day: date,
    amount: Decimal,
    day_of_month: int,
    ya_aportados: set[tuple[int, int]],
) -> Decimal:
    """Ingresa la aportación del mes el primer día hábil a partir del día fijado."""
    mes = (day.year, day.month)
    if mes in ya_aportados or day.day < day_of_month:
        return ZERO
    broker.deposit(amount)
    ya_aportados.add(mes)
    return amount


def _rebalance(
    broker: PaperBroker,
    weights: Mapping[Symbol, float],
    patrimonio: Decimal,
    price_at: PriceLookup,
    day: date,
) -> int:
    """Lleva la cartera a sus pesos objetivo. Devuelve cuántas órdenes se emitieron.

    Primero vende y después compra, para que el dinero de las ventas esté
    disponible. Los símbolos se recorren ordenados para que el resultado sea
    reproducible.
    """
    posiciones = broker.positions()
    simbolos = sorted(set(posiciones) | set(weights))

    precios: dict[Symbol, Decimal] = {}
    objetivos: dict[Symbol, Decimal] = {}
    for symbol in simbolos:
        precio = price_at(symbol, day)
        if precio is None or precio <= 0:
            # Sin precio fiable no se toca esa posición. Ante la duda, nada.
            continue
        precios[symbol] = precio
        valor_objetivo = patrimonio * Decimal(str(weights.get(symbol, 0.0)))
        objetivos[symbol] = (valor_objetivo / precio).to_integral_value(rounding=ROUND_DOWN)

    ordenes = 0

    for symbol in sorted(objetivos):
        actual = posiciones[symbol].quantity if symbol in posiciones else Decimal(0)
        exceso = actual - objetivos[symbol]
        if exceso > 0:
            broker.submit(Order(day, symbol, Side.SELL, exceso, precios[symbol]))
            ordenes += 1

    for symbol in sorted(objetivos):
        posicion = broker.positions().get(symbol)
        actual = posicion.quantity if posicion else Decimal(0)
        falta = objetivos[symbol] - actual
        if falta <= 0:
            continue
        asequible = (broker.cash() / precios[symbol]).to_integral_value(rounding=ROUND_DOWN)
        cantidad = min(falta, asequible)
        if cantidad > 0:
            broker.submit(Order(day, symbol, Side.BUY, cantidad, precios[symbol]))
            ordenes += 1

    return ordenes
