"""El guardia de red funciona.

Si estos tests dejaran de pasar, la regla "ningún test usa la red" pasaría a
ser un buen propósito escrito en un fichero, que es como no tenerla.

Se usa una IP literal y no un nombre de dominio para que ni siquiera haya una
consulta de DNS: la idea es que el test no toque la red ni para fallar.
"""

from __future__ import annotations

import socket
import urllib.request

import pytest

from tests.conftest import NetworkForbidden

DESTINO = ("127.0.0.1", 9)  # puerto descarte, no escucha nadie


def test_no_se_puede_abrir_una_conexion() -> None:
    with pytest.raises(NetworkForbidden):
        socket.create_connection(DESTINO)


def test_no_se_puede_conectar_un_socket_a_mano() -> None:
    with pytest.raises(NetworkForbidden):
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(DESTINO)


def test_una_descarga_http_tambien_falla() -> None:
    with pytest.raises(NetworkForbidden):
        urllib.request.urlopen("http://127.0.0.1:9/", timeout=1)
