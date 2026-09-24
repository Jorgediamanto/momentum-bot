# CHANGELOG

Lo que cambia de cara a quien use el bot. Lo más reciente, arriba.

Formato: [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).
Versionado semántico.

---

## [No publicado]

## [0.1.0] — 2026-09-24

Primera piedra. El esqueleto del proyecto (M0). Todavía no hay estrategia:
hay estructura, contratos y verificación automática.

### Añadido

- Estructura del proyecto por capas y contratos entre ellas.
- `config.yaml` con todos los parámetros de la estrategia en un solo sitio.
- `PaperBroker`: bróker de papel en memoria, con cuentas exactas al céntimo.
- Motor de backtest mínimo: recorre días, aporta cada mes y reajusta la
  cartera. Sin costes ni divisas todavía (eso es M5).
- Fuente de precios desde ficheros CSV locales.
- `make verify`: ruff, mypy en modo estricto, tests y test de humo.
- `make.ps1`, equivalente para Windows.
- Integración continua en GitHub Actions sobre Python 3.12 y 3.13.
- Guardia que impide que cualquier test use la red.

### Notas

- El bot **no opera con dinero real** y no va a hacerlo desde este
  repositorio.
- `report`, `run-day` y `dashboard` todavía no existen: si se invocan, fallan
  diciendo qué hito los traerá.
