# SPEC — Bot de momentum sobre tres mercados

Documento de referencia del proyecto. Describe **qué** hace el sistema y **cómo
encajan sus piezas**. No describe el estado de avance: eso vive en `IDEAS.md`
(hitos), `PROGRESO.md` (diario de trabajo) y `CHANGELOG.md`.

> Este fichero no se edita durante el desarrollo. Si algo aquí está mal,
> incompleto o entra en conflicto con un hito, se anota en `PREGUNTAS.md` y se
> deja como está. Ver `CLAUDE.md`.

---

## 1. Qué hace el bot

Cada día de mercado el bot ejecuta esta secuencia:

1. Descarga (o lee de caché) los precios diarios ajustados de tres mercados y de
   sus índices de referencia: **S&P 500** (EE. UU.), **Europa** y **España**.
2. Mide la **tendencia** de cada uno de los tres mercados y elige **uno solo**:
   el de mejor tendencia. Si ninguno supera el filtro de tendencia, el bot puede
   quedarse fuera del mercado.
3. Dentro del mercado elegido, calcula el **momentum** de cada empresa del
   universo point-in-time de ese día y se queda con las **N mejores**
   (N configurable, entre 20 y 100).
4. Reparte el capital entre esas empresas **en proporción a su momentum**, con un
   **peso máximo por empresa** para que ninguna domine la cartera.
5. Compara la cartera objetivo con la real y emite las órdenes necesarias a
   través de la interfaz `Broker`.
6. Registra lo ocurrido y actualiza informes y dashboard.

Se supone una **aportación fija mensual de unos 300 €**, configurable. El
inversor reside en España, así que la contabilidad fiscal sigue las reglas
españolas (hito M6).

### Qué NO hace

- **No opera con dinero real.** No hay, ni habrá en este repositorio, código que
  conecte con un bróker real, ni credenciales, ni claves. La única
  implementación de `Broker` que vive aquí es de papel (`PaperBroker`). La
  conexión real, si algún día ocurre, se hará a mano y fuera de este repo.
- **No es asesoramiento financiero ni fiscal.** El módulo de fiscalidad (M6)
  implementa las reglas españolas como las entiende el autor, para poder estimar
  el impacto de los impuestos en el backtest. No sustituye a un asesor ni vale
  como declaración.
- **No promete un retorno.** El objetivo declarado es que funcione solo y que
  elija bien entre mercados. Un backtester honesto que enseña sus propias
  limitaciones vale más que uno con resultados bonitos.

### Prioridades, en este orden

1. Que el sistema funcione solo, sin supervisión, y que ante la duda **no haga
   nada**.
2. Que la elección entre los tres mercados esté bien hecha y sea explicable.
3. Que los resultados que reporta sean honestos, incluidos los malos.
4. El retorno.

---

## 2. Arquitectura por capas

El flujo va en una sola dirección. Ninguna capa conoce a la que tiene por
encima; todas se comunican por interfaces (`typing.Protocol`) y objetos de datos
inmutables.

```
                   config.yaml  (todos los parámetros de estrategia)
                        |
                        v
  +----------+   +----------+   +----------+   +-----------+
  |  DATOS   |-->| UNIVERSO |-->| SEÑALES  |-->| SELECCIÓN |
  +----------+   +----------+   +----------+   +-----------+
   precios         quién          momentum       mercado
   ajustados       cotizaba       + tendencia    ganador +
   + FX            ese día                       top N
                                                      |
                        +-----------------------------+
                        v
                  +----------+   +-----------+   +----------+
                  | CARTERA  |-->| EJECUCIÓN |-->| INFORMES |
                  +----------+   +-----------+   +----------+
                   pesos           órdenes         HTML +
                   objetivo        (Broker)        dashboard
```

El **motor de backtest** (M5) y el **runner diario** (M8) no son capas: son dos
formas distintas de recorrer el mismo tren de capas. El backtest lo recorre una
vez por cada día histórico; el runner lo recorre una vez, para hoy. Esto es
deliberado: si ambos usan el mismo código, lo que se prueba en el backtest es
exactamente lo que se ejecuta en producción.

### 2.1 Regla transversal: `as_of`

Toda función que mire datos recibe una fecha `as_of` y **tiene prohibido leer
nada posterior a esa fecha**. No es una recomendación: es la propiedad que el
test anti look-ahead de M5 comprueba alterando los precios posteriores a `t` y
exigiendo que ninguna decisión hasta `t` cambie.

### 2.2 Regla transversal: dinero

Todo importe monetario es `decimal.Decimal`, nunca `float`. Los precios también.
Sólo son `float` las magnitudes adimensionales: puntuaciones de momentum, pesos,
rentabilidades. La razón es el test de conservación del dinero de M5, que debe
cuadrar **al céntimo**, y la contabilidad FIFO de M6.

### 2.3 Convención de idioma

- **Identificadores, nombres de fichero y columnas de datos: en inglés.** Es lo
  que hablan las librerías y las fuentes de precios.
- **Documentación, comentarios, docstrings y mensajes de error: en castellano.**

---

## 3. Las capas, una a una

### 3.1 Datos — `momentum.data`

Entrega series de precios **diarios y ajustados por splits y dividendos**, de
fuentes públicas gratuitas, con caché local en `data/cache/` (ignorada por git).
Es la única capa que toca la red.

Contrato:

```python
class PriceSource(Protocol):
    def bars(self, symbol: Symbol, start: date, end: date) -> PriceSeries: ...
    def fx(self, pair: str, start: date, end: date) -> PriceSeries: ...
```

- `PriceSeries` es una secuencia inmutable de `Bar`, ordenada por fecha y sin
  fechas repetidas.
- Un `Bar` lleva fecha, OHLC y volumen. Los precios ya vienen ajustados; la capa
  de arriba nunca vuelve a ajustar nada.
- Los días no negociados sencillamente **no existen** en la serie. Cada mercado
  tiene su propio calendario y sus propios festivos: la serie de Madrid y la de
  Nueva York no coinciden, y ninguna capa puede suponer que sí.
- `fx("EURUSD", ...)` devuelve el tipo de cambio como si fuera una serie de
  precios, para convertir a euros los mercados que no cotizan en euros.
- Si falta un dato, la capa **lo dice**; no lo rellena ni lo interpola por su
  cuenta. Quien decide qué hacer ante un hueco es la política de robustez (M10).

### 3.2 Universo — `momentum.universe`

Responde a "¿qué empresas formaban este índice **este día**?".

```python
class UniverseSource(Protocol):
    def constituents(self, market: Market, as_of: date) -> tuple[Symbol, ...]: ...
```

Esta es la capa con más riesgo de engañarnos. Usar la composición **de hoy** para
un backtest de hace diez años produce **sesgo de supervivencia**: se evalúan sólo
las empresas que sobrevivieron, y el resultado sale bonito y es mentira.

Si no aparece una fuente gratuita y fiable de composición histórica, se
implementa la interfaz con la mejor aproximación disponible y la limitación se
declara **en este documento** (sección 6) **y en cada informe generado**. No se
esconde.

### 3.3 Señales — `momentum.signals`

Convierte precios en números comparables. Dos familias:

```python
class MomentumModel(Protocol):
    def score(self, prices: PriceSeries, as_of: date) -> float | None: ...

class TrendModel(Protocol):
    def score(self, index_prices: PriceSeries, as_of: date) -> float | None: ...
```

- **Momentum de empresa**: 12-1 y 6-1 meses (rentabilidad de los últimos 12 o 6
  meses saltándose el mes más reciente, que históricamente revierte). La mezcla
  de ambos y sus ventanas exactas viven en `config.yaml`.
- **Tendencia de mercado**: mide si un índice está en tendencia alcista.
- `None` significa "no hay datos suficientes para puntuar esto". No es cero. Una
  empresa sin histórico suficiente **no compite**; no compite con un cero.

### 3.4 Selección — `momentum.selection`

Decide **dónde** se invierte.

```python
class Selector(Protocol):
    def select(self, market_scores: Mapping[Market, float | None],
               stock_scores: Mapping[Symbol, float],
               as_of: date) -> Selection: ...
```

`Selection` lleva el mercado elegido (o ninguno), los símbolos elegidos y **el
motivo**, en texto legible. El motivo no es decorativo: es lo que el dashboard
enseña cada día en "qué mercado se eligió y por qué", y lo que permite auditar
una decisión meses después.

### 3.5 Cartera — `momentum.portfolio`

Convierte una selección en pesos objetivo.

```python
class PortfolioBuilder(Protocol):
    def weights(self, selection: Selection,
                stock_scores: Mapping[Symbol, float]) -> dict[Symbol, float]: ...
```

Invariantes que M4 comprueba como propiedades, no como ejemplos:

- los pesos suman 1 (o 0 si se está fuera del mercado);
- ningún peso supera el máximo por empresa de `config.yaml`;
- ningún peso es negativo: **el bot no va corto y no apalanca**;
- el mismo input produce exactamente el mismo output.

### 3.6 Ejecución — `momentum.execution`

Convierte la diferencia entre cartera real y cartera objetivo en órdenes.

```python
class Broker(Protocol):
    def cash(self) -> Decimal: ...
    def positions(self) -> Mapping[Symbol, Position]: ...
    def submit(self, order: Order) -> Fill: ...
```

- La **única** implementación en este repositorio es `PaperBroker`. Ver
  "Qué NO hace".
- El runner diario debe ser **idempotente**: ejecutar dos veces el mismo día no
  puede duplicar órdenes. Se consigue con una clave de idempotencia por
  (fecha, símbolo, intención), persistida en SQLite (M8).

### 3.7 Informes — `momentum.reports`

Genera el informe HTML y alimenta el dashboard estático.

```python
class ReportBuilder(Protocol):
    def build(self, run: BacktestResult, out_dir: Path) -> Path: ...
```

Todo informe incluye, obligatoriamente:

- comparación contra las **tres referencias**: comprar el índice cada mes, MTUM,
  y elegir mercado al azar;
- métricas, drawdowns, rotación e impuestos;
- una sección de **limitaciones** que enumera lo que el backtest no sabe
  simular;
- si la estrategia pierde contra comprar el índice, **lo dice en la primera
  línea**.

---

## 4. Configuración

**Todos** los parámetros de la estrategia viven en un único `config.yaml`:
ventanas de momentum, filtro de tendencia, número de valores, peso máximo,
aportación mensual, costes, slippage, fechas del backtest y tipos fiscales.

No hay parámetros de estrategia repartidos por el código ni valores por defecto
escondidos en funciones. Si un parámetro no está en `config.yaml`, no es un
parámetro: es una decisión de diseño, y se justifica en este documento.

`config.yaml` sólo lo cambia Jorge.

---

## 5. Almacenamiento

| Ruta | Qué guarda | ¿En git? |
|---|---|---|
| `data/cache/` | precios descargados | no |
| `data/*.sqlite` | estado del paper trading: órdenes, posiciones, caja | no |
| `reports/` | informes HTML generados | no (sólo `.gitkeep`) |
| `dashboard/dist/` | dashboard estático construido | no |
| `progreso/<fecha>/` | capturas de pantalla del agente nocturno | sí |
| `tests/fixtures/` | datos sintéticos y recortes reales para tests | sí |

Nada de lo que está fuera de git es necesario para que `make verify` pase: se
regenera o se sustituye por fixtures.

---

## 6. Limitaciones conocidas

Sección viva por naturaleza, pero **de sólo lectura durante el desarrollo**: si
aparece una limitación nueva, se anota en `PREGUNTAS.md` para que Jorge la
incorpore aquí.

- **Sesgo de supervivencia en el universo (M2).** Mientras no exista una fuente
  gratuita y fiable de composición histórica de los índices, el universo
  point-in-time será una aproximación. Todo informe generado debe declararlo.
- **Precios ajustados de fuentes gratuitas.** Los ajustes por splits y
  dividendos de las fuentes públicas no siempre coinciden entre proveedores ni
  son estables en el tiempo.
- **Ejecución idealizada.** El backtest supone que se puede comprar al precio de
  cierre. Los costes y el slippage se modelan (M5), pero el impacto de mercado,
  la liquidez y los huecos de apertura no.
- **Fiscalidad estimada.** M6 implementa FIFO y la regla de los dos meses como
  las entiende el autor. No es asesoramiento fiscal.
- **Sin dividendos en efectivo por separado.** Se trabaja con series ajustadas,
  que incorporan el dividendo al precio; el flujo de caja real de un dividendo y
  su retención en origen no se simulan.

---

## 7. DEFINICIÓN DE TERMINADO

- `make verify` verde en main y en CI.
- `make report` genera el informe completo con referencias y limitaciones.
- `make run-day` funciona en paper trading y es idempotente.
- Replay de 90 días sin errores.
- Dashboard generado, con capturas.
- Ni secretos ni código de ejecución real en el repo.
- README explica cómo instalarlo, cómo usarlo y qué NO hace.
