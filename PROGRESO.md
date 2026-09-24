# PROGRESO

Diario de trabajo. Una entrada por sesión, la más reciente arriba.

Se cuenta lo que se hizo, lo que se intentó y no salió, y dónde se quedó la
cosa. Un hito a medias bien contado vale más que uno dado por terminado a la
ligera.

Formato: **fecha · hito · qué se hizo · qué queda pendiente**.

---

## 2026-09-24 · M0 · Esqueleto

**Qué se hizo.**

- Estructura del repositorio: `src/momentum/` con un módulo por capa, `tests/`,
  `reports/`, `dashboard/`, `data/cache/` (fuera de git).
- `SPEC.md` con las siete capas, el contrato de cada una y la DEFINICIÓN DE
  TERMINADO. `CLAUDE.md` con las reglas inviolables y el procedimiento de
  trabajo por hitos. `IDEAS.md` con los once hitos como checklist.
- `config.yaml` con todos los parámetros de la estrategia. Los importes van
  como texto entrecomillado para leerlos como `Decimal` exacto; el cargador
  rechaza un importe escrito como número decimal.
- Contratos entre capas como `typing.Protocol`, sin implementaciones falsas:
  las capas de M1 a M4 declaran su interfaz y nada más. Lo que sí está escrito
  es lo que M0 necesita: tipos de dinero y series, fuente de precios en CSV,
  `PaperBroker` en memoria, motor de backtest mínimo y validación de pesos.
- `make verify` = ruff + mypy estricto + pytest + test de humo. Y `make.ps1`,
  que hace lo mismo en Windows, donde no hay `make`.
- Guardia de red en `tests/conftest.py`: cualquier test que intente conectarse
  falla en el acto. Con tres tests que lo demuestran.
- 49 tests. El de humo corre un backtest de 65 sesiones sobre fixtures y
  comprueba tres cosas: que el tren de capas llega hasta el final, que con
  precios planos el patrimonio final es **exactamente** lo aportado
  (900,00 € al céntimo), y que dos ejecuciones iguales dan el mismo resultado.

**Decisiones que conviene recordar.**

- Identificadores en inglés, documentación y mensajes en castellano.
- El dinero es `Decimal` en todo el sistema; `money()` se niega a construirse
  desde un `float`.
- El cargador de configuración **rechaza arrancar** si `execution.broker` no es
  `paper`. La regla de no tocar dinero real está en el código, no sólo escrita.
- Los comandos aún no implementados (`report`, `run-day`, `dashboard`) fallan
  nombrando su hito, en vez de devolver éxito sin hacer nada.

**Qué queda pendiente.**

- Ocho dudas abiertas en `PREGUNTAS.md`. La que más urge es la contradicción
  entre M2 ("deja escrito en SPEC.md") y la regla de no editar `SPEC.md`.
- M1: datos de verdad. Nada de M1 se ha tocado hoy, a propósito.
