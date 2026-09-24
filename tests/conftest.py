"""Configuración común de los tests.

Lo más importante de este fichero es el guardia de red. La regla "ningún test
usa la red" no se sostiene con buena voluntad: se sostiene rompiendo el socket.
Un test que intente conectarse falla en el acto, con un mensaje que explica qué
hacer en su lugar.
"""

from __future__ import annotations

import socket
from collections.abc import Iterator
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"


class NetworkForbidden(RuntimeError):
    """Un test ha intentado usar la red."""


_MENSAJE = (
    "Los tests no pueden usar la red (ver CLAUDE.md). Si necesitas datos "
    "reales, guarda un recorte en tests/fixtures/ y léelo desde ahí."
)


@pytest.fixture(autouse=True)
def sin_red(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Corta cualquier conexión saliente durante todos los tests."""

    def _bloquear(*_args: object, **_kwargs: object) -> None:
        raise NetworkForbidden(_MENSAJE)

    monkeypatch.setattr(socket.socket, "connect", _bloquear)
    monkeypatch.setattr(socket.socket, "connect_ex", _bloquear)
    monkeypatch.setattr(socket, "create_connection", _bloquear)
    yield


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES
