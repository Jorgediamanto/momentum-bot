# momentum-bot

Un bot que cada día mira tres mercados —**S&P 500**, **Europa** y **España**—,
elige el que mejor tendencia tiene, compra las empresas con más momentum de ese
mercado y reparte el capital entre ellas según su momentum. Aportación fija
mensual. Contabilidad fiscal española.

**Opera siempre en papel.** Con dinero imaginario. Ver [Qué NO hace](#qué-no-hace).

[![CI](https://github.com/Jorgediamanto/momentum-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/Jorgediamanto/momentum-bot/actions/workflows/ci.yml)

---

## Estado

En construcción, por hitos. El proyecto va por **M0: esqueleto**.

Lo que hay hoy: la estructura, los contratos entre capas, la configuración, el
bróker de papel, un motor de backtest mínimo y la verificación automática. Lo
que **no** hay todavía: datos reales, señales, selección, informes ni
dashboard. El estado exacto está en [`IDEAS.md`](IDEAS.md), con una casilla por
hito.

Si un comando no está implementado, falla diciendo qué hito lo trae. Nunca
devuelve éxito sin hacer nada.

## Qué NO hace

Esto es lo primero que hay que leer, no una nota al pie.

- **No opera con dinero real.** No hay en este repositorio, ni va a haber, APIs
  de brókers reales, credenciales ni claves. La única implementación de la
  interfaz `Broker` es `PaperBroker`, que mueve dinero imaginario. Si alguna
  vez hay conexión real, se hará a mano y fuera de aquí.
- **No es asesoramiento financiero ni fiscal.** El módulo de fiscalidad
  española sirve para estimar el impacto de los impuestos en un backtest. No
  sustituye a un asesor y no vale como declaración.
- **No promete rentabilidad.** El objetivo es que funcione solo y que elija
  bien entre mercados. Los informes enseñan los resultados malos igual que los
  buenos: si la estrategia pierde contra comprar el índice, el informe lo dice
  en su primera línea.
- **No opera con datos incompletos.** Si falla una descarga, falta un precio o
  el mercado está cerrado, el bot no hace nada. Ante la duda, quieto.

## Instalación

Hace falta **Python 3.12 o superior**. Nada más.

```bash
git clone https://github.com/Jorgediamanto/momentum-bot.git
cd momentum-bot
make setup
```

En Windows no hay `make`. El atajo equivalente hace exactamente lo mismo:

```powershell
.\make.ps1 setup
```

## Uso

```bash
make verify        # ruff + mypy + tests + humo. El único juez del proyecto
make test          # sólo los tests unitarios
momentum config    # enseña la configuración cargada y validada
```

Y, según avance el proyecto:

```bash
make report        # informe HTML completo con referencias y limitaciones  [M7]
make run-day       # un día de paper trading                               [M8]
make dashboard     # dashboard web estático                                [M9]
```

## Configuración

Todos los parámetros de la estrategia están en un único fichero:
[`config.yaml`](config.yaml). Ventanas de momentum, filtro de tendencia, número
de valores, peso máximo por empresa, aportación mensual, costes, fechas del
backtest y tipos fiscales.

No hay parámetros escondidos en el código. Si algo no está en `config.yaml`, no
es un parámetro: es una decisión de diseño y está justificada en
[`SPEC.md`](SPEC.md).

## Cómo está montado

Siete capas, en una sola dirección:

```
datos → universo → señales → selección → cartera → ejecución → informes
```

Cada capa habla con la siguiente a través de una interfaz (`typing.Protocol`) y
objetos inmutables. El backtest y el runner diario no son capas: son dos formas
de recorrer el mismo tren, y por eso lo que se prueba en el backtest es
exactamente lo que se ejecutaría.

El detalle está en [`SPEC.md`](SPEC.md).

## Documentación

| Fichero | Para qué |
|---|---|
| [`SPEC.md`](SPEC.md) | qué es el sistema, sus capas y sus límites |
| [`IDEAS.md`](IDEAS.md) | los hitos, en orden, con su criterio de terminación |
| [`CLAUDE.md`](CLAUDE.md) | cómo se trabaja en este repositorio |
| [`PROGRESO.md`](PROGRESO.md) | diario de trabajo |
| [`CHANGELOG.md`](CHANGELOG.md) | qué cambia en cada versión |
| [`PREGUNTAS.md`](PREGUNTAS.md) | dudas y decisiones pendientes |

## Licencia

MIT. Ver [`LICENSE`](LICENSE).
