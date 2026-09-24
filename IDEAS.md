# IDEAS — hitos del proyecto

Se trabajan **en este orden**. No se empieza uno hasta que el anterior cumple su
"Hecho cuando".

El "Hecho cuando" es el criterio de terminación. No se interpreta, no se
negocia, no se sustituye por otro que parezca equivalente. Si un hito parece
mal planteado, se anota en `PREGUNTAS.md` y **se deja el hito como está**: este
fichero no se reordena ni se reescribe.

---

- [ ] **M0 Esqueleto.**
      Hecho cuando: `make verify` y CI en GitHub Actions en verde.

- [ ] **M1 Datos** de precios diarios ajustados de los tres mercados y sus
      índices, desde fuentes públicas gratuitas, con caché local y una sola
      interfaz.
      Hecho cuando: tests con fixtures cubren splits, dividendos, huecos y
      festivos distintos por mercado.

- [ ] **M2 Universo point-in-time**: universo(mercado, fecha) devuelve los
      constituyentes que había ese día. Si no hay fuente gratuita fiable,
      implementa la interfaz con la mejor aproximación y deja escrito en SPEC.md
      y en cada informe que hay sesgo de supervivencia.
      Hecho cuando: un test demuestra que una empresa que salió del índice
      aparece antes de su salida, o un test marca la limitación explícitamente.

- [ ] **M3 Señales**: momentum de empresa (12-1 y 6-1 meses) y tendencia de
      mercado.
      Hecho cuando: tests con series sintéticas de resultado conocido.

- [ ] **M4 Selección y cartera**: mercado ganador, top N configurable, pesos por
      momentum con peso máximo por empresa.
      Hecho cuando: tests de propiedades (pesos suman 1, respeta límites, mismo
      input da mismo output).

- [ ] **M5 Motor de backtest**: evaluación diaria, aportación mensual, costes,
      slippage, EUR/USD.
      Hecho cuando: pasa un test anti look-ahead (alterar precios posteriores a
      t no cambia ninguna decisión hasta t) y un test de conservación del dinero
      que cuadra al céntimo.

- [ ] **M6 Fiscalidad España**: FIFO, ganancias patrimoniales y regla de los dos
      meses en recompras de valores homogéneos.
      Hecho cuando: tests con casos calculados a mano. SPEC.md aclara que no es
      asesoramiento fiscal.

- [ ] **M7 Validación walk-forward** contra tres referencias: comprar el índice
      cada mes, MTUM, y elegir mercado al azar. Informe HTML con métricas,
      drawdowns, rotación, impuestos y sección de limitaciones.
      Hecho cuando: `make report` lo genera desde cero sin errores.

- [ ] **M8 Paper trading**: interfaz Broker + PaperBroker. `make run-day`
      ejecuta un día completo y lo registra en SQLite.
      Hecho cuando: un replay de 90 días históricos seguidos funciona y un test
      demuestra que ejecutar dos veces el mismo día no duplica órdenes.

- [ ] **M9 Dashboard web estático**: capital frente a referencias, mercado
      elegido cada día y por qué, posiciones, operaciones, alertas.
      Hecho cuando: build sin errores y Playwright guarda capturas en
      progreso/<fecha>/.

- [ ] **M10 Robustez**: fallo de descarga, mercado cerrado, precio ausente.
      Hecho cuando: hay test de cada fallo y el bot nunca opera con datos
      incompletos; ante la duda, no hace nada.

- [ ] **M11 Auditoría final** contra la DEFINICIÓN DE TERMINADO, con la
      evidencia de cada punto escrita en DONE.md.
