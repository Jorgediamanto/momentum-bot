"""La línea de comandos.

Lo que más importa aquí: los comandos que todavía no existen **fallan**. Un
comando pendiente que devolviera cero parecería haber funcionado, y el agente
nocturno daría por buenos hitos que no ha hecho.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from momentum.cli import PENDIENTES, main


@pytest.fixture(autouse=True)
def _apunta_al_config_del_repo(repo_root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MOMENTUM_CONFIG", str(repo_root / "config.yaml"))


def test_config_resume_la_configuracion(capsys: pytest.CaptureFixture[str]) -> None:
    codigo = main(["config"])

    salida = capsys.readouterr().out
    assert codigo == 0
    assert "paper" in salida
    assert "300.00" in salida


@pytest.mark.parametrize("comando", sorted(PENDIENTES))
def test_los_comandos_pendientes_fallan_diciendo_de_que_hito_son(
    comando: str, capsys: pytest.CaptureFixture[str]
) -> None:
    codigo = main([comando])

    salida = capsys.readouterr().out
    hito = PENDIENTES[comando][0]
    assert codigo == 1
    assert hito in salida


def test_un_config_invalido_no_revienta_con_traza(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    roto = tmp_path / "config.yaml"
    roto.write_text("markets: {}\n", encoding="utf-8")
    monkeypatch.setenv("MOMENTUM_CONFIG", str(roto))

    codigo = main(["config"])

    assert codigo == 1
    assert "no es válido" in capsys.readouterr().out
