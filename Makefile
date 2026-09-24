# Makefile del bot de momentum.
#
# `make verify` es el único juez del proyecto: si pasa, el trabajo vale; si no,
# no vale. Es lo mismo que ejecuta CI.
#
# En Windows no hay make. Usa `.\make.ps1 <objetivo>`, que hace exactamente lo
# mismo con los mismos comandos.

PYTHON ?= python

.PHONY: help setup verify lint format typecheck test smoke report run-day dashboard clean

help:
	@echo "setup      crea .venv e instala el proyecto con sus dependencias de desarrollo"
	@echo "verify     lint + typecheck + tests + humo. El único juez"
	@echo "lint       ruff: reglas y formato"
	@echo "format     ruff format: reformatea el código"
	@echo "typecheck  mypy en modo estricto"
	@echo "test       tests unitarios (sin el de humo)"
	@echo "smoke      test de humo: backtest corto sobre fixtures"
	@echo "report     informe HTML completo             [pendiente, M7]"
	@echo "run-day    un día de paper trading           [pendiente, M8]"
	@echo "dashboard  dashboard web estático            [pendiente, M9]"
	@echo "clean      borra cachés y artefactos de build"

setup:
	$(PYTHON) -m venv .venv
	.venv/bin/python -m pip install --upgrade pip
	.venv/bin/python -m pip install -e ".[dev]"
	@echo "Listo. Activa el entorno con: source .venv/bin/activate"

verify: lint typecheck test smoke
	@echo ""
	@echo "verify OK"

lint:
	$(PYTHON) -m ruff check src tests
	$(PYTHON) -m ruff format --check src tests

format:
	$(PYTHON) -m ruff format src tests
	$(PYTHON) -m ruff check --fix src tests

typecheck:
	$(PYTHON) -m mypy

test:
	$(PYTHON) -m pytest -m "not smoke"

smoke:
	$(PYTHON) -m pytest -m smoke

report:
	$(PYTHON) -m momentum.cli report

run-day:
	$(PYTHON) -m momentum.cli run-day

dashboard:
	$(PYTHON) -m momentum.cli dashboard

clean:
	rm -rf .mypy_cache .ruff_cache .pytest_cache build dist src/*.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
