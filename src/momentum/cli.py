"""Línea de comandos del bot.

Los comandos que todavía no existen **fallan diciendo qué hito los trae**, en
vez de no hacer nada y devolver éxito. Un comando que calla y devuelve cero es
peor que uno que no existe: parece que ha funcionado.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from momentum import __version__
from momentum.config import ConfigError, load_config

#: Comandos pendientes y el hito que los implementa.
PENDIENTES = {
    "report": ("M7", "informe HTML completo con referencias y limitaciones"),
    "run-day": ("M8", "un día completo de paper trading registrado en SQLite"),
    "dashboard": ("M9", "dashboard web estático"),
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="momentum",
        description="Bot de momentum sobre tres mercados. Sólo opera en papel.",
    )
    parser.add_argument("--version", action="version", version=f"momentum {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("config", help="Carga config.yaml, lo valida y lo resume")
    for nombre, (hito, descripcion) in PENDIENTES.items():
        sub.add_parser(nombre, help=f"[{hito}, pendiente] {descripcion}")
    return parser


def _show_config() -> int:
    try:
        config = load_config()
    except ConfigError as exc:
        print(f"config.yaml no es válido: {exc}")
        return 1

    print(f"Moneda base .......... {config.base_currency}")
    print(f"Mercados ............. {', '.join(m.label for m in config.markets.values())}")
    ventanas = ", ".join(
        f"{w.months}-{w.skip_months} ({w.weight:g})" for w in config.momentum.windows
    )
    print(f"Ventanas de momentum . {ventanas}")
    print(f"Valores en cartera ... {config.selection.top_n}")
    print(f"Peso máximo .......... {config.portfolio.max_weight_per_stock:.0%} por empresa")
    print(f"Aportación ........... {config.contributions.amount} {config.contributions.currency}")
    print(f"Backtest ............. {config.backtest.start} a {config.backtest.end}")
    print(f"Bróker ............... {config.execution.broker} (dinero imaginario)")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.command == "config":
        return _show_config()

    hito, descripcion = PENDIENTES[args.command]
    print(
        f"'{args.command}' todavía no existe: lo trae el hito {hito} ({descripcion}).\n"
        "Consulta IDEAS.md para ver en qué punto está el proyecto."
    )
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
