# CLAUDE.md — instrucciones para el agente

Este repositorio lo desarrolla un agente autónomo que trabaja **sin supervisión
en tiempo real**. Jorge revisa el resultado después. Todo lo que sigue está
escrito partiendo de esa base: cuando no haya nadie a quien preguntar, la
respuesta correcta es **parar y escribirlo**, no improvisar.

Lee también `SPEC.md` (qué es el sistema) y `IDEAS.md` (qué toca hacer ahora).

---

## REGLAS INVIOLABLES

- Nunca dinero real: ni APIs de brókers reales, ni credenciales, ni claves. Si
  un hito parece requerirlo, para y escríbelo en PREGUNTAS.md.
- Nunca ficheros .env ni secretos en git.
- Nunca modifiques un test para que pase.
- Nunca ajustes parámetros de la estrategia para mejorar el backtest. Viven en
  config.yaml y solo los cambia Jorge.
- Se reportan todos los resultados, también los malos. Si la estrategia pierde
  contra comprar el índice, el informe lo dice en su primera línea.
- main siempre pasa `make verify`.
- No añadas dependencias que el hito no justifique.
- No edites SPEC.md ni reordenes IDEAS.md; si algo está mal, a PREGUNTAS.md.
- No juzgues lo visual: deja capturas y una nota en PREGUNTAS.md.

---

## Cómo se trabaja un hito

Se trabaja **un hito cada vez**, en el orden de `IDEAS.md`. No se empieza el
siguiente hasta que el anterior cumple su "Hecho cuando".

1. **Leer** el hito en `IDEAS.md` y su "Hecho cuando". Ese "Hecho cuando" es el
   criterio, no tu criterio.
2. **Escribir los tests primero**, derivados literalmente de ese "Hecho cuando".
   Si no sabes escribir el test, todavía no has entendido el hito: anótalo en
   `PREGUNTAS.md` y trabaja en otra parte del mismo hito.
3. **Implementar** hasta que los tests pasen sin tocar los tests.
4. **`make verify`** en verde, entero.
5. **Commit** con mensaje que empiece por el hito: `M3: momentum 12-1 y 6-1`.
6. **Anotar** en `PROGRESO.md` qué se hizo y qué quedó pendiente, y en
   `CHANGELOG.md` lo que cambia de cara al usuario.
7. **Marcar la casilla** del hito en `IDEAS.md` sólo cuando su "Hecho cuando" se
   cumple de verdad. Marcar una casilla sin cumplirla es la peor cosa que puedes
   hacer en este repositorio: destruye la única señal de avance que Jorge tiene.

Si un hito se queda a medias, no pasa nada: deja `main` verde, cuenta en
`PROGRESO.md` dónde te quedaste y por qué. Un hito a medias bien contado vale
más que uno "terminado" con la casilla marcada a la ligera.

---

## Los cuatro ficheros donde se escribe

| Fichero | Qué va aquí | Quién escribe |
|---|---|---|
| `PROGRESO.md` | diario de trabajo: qué se hizo, qué se intentó, dónde te quedaste | el agente |
| `CHANGELOG.md` | cambios visibles para quien use el bot | el agente |
| `PREGUNTAS.md` | dudas, bloqueos, limitaciones detectadas, decisiones que no te tocan | el agente |
| `DONE.md` | evidencia de la auditoría final (M11) | el agente, sólo en M11 |

`SPEC.md`, `IDEAS.md` y `config.yaml` **no los tocas**.

### Cuándo escribir en PREGUNTAS.md

Escribe una entrada en cuanto se dé cualquiera de estas situaciones, y sigue
trabajando en lo que no dependa de la respuesta:

- un hito parece pedir credenciales, una API de pago o una conexión real;
- descubres una limitación de los datos que el `SPEC.md` no recoge;
- dos cosas del proyecto se contradicen;
- necesitas una decisión que es de Jorge (un parámetro, una fuente de datos, un
  bróker, algo de dinero);
- tienes una opinión sobre el aspecto visual de algo. Esa opinión no vale: deja
  la captura y la nota.

Formato de cada entrada: fecha, hito, qué te has encontrado, qué has hecho
mientras tanto, y qué necesitas exactamente para desbloquearlo.

---

## Reglas técnicas

### Tests

- **Ningún test toca la red.** Hay un guardia automático en
  `tests/conftest.py` que revienta cualquier conexión durante los tests. Si
  necesitas datos reales, guarda un recorte en `tests/fixtures/`.
- Los tests son deterministas. Nada de `datetime.now()`, nada de aleatoriedad
  sin semilla fija, nada de depender del orden de un `set`.
- Los dobles de prueba (fakes, stubs) viven en `tests/`, **nunca en `src/`**.
  `src/` es lo que se ejecuta de verdad.

### Dinero

`decimal.Decimal` para todo importe y todo precio. `float` sólo para
puntuaciones, pesos y rentabilidades. Nunca construyas un `Decimal` a partir de
un `float` (`Decimal(0.1)` no vale): usa cadenas o enteros.

### `as_of`

Ninguna función mira datos posteriores a su `as_of`. Cuando dudes de si algo
mira al futuro, escribe el test que lo demuestra antes de seguir.

### Ante la duda, no hacer nada

Datos incompletos, precio ausente, mercado cerrado, descarga fallida: el bot
**no opera**. No estima, no interpola, no "aproxima". Se queda quieto y lo
registra. Esta regla gana a cualquier otra consideración de rentabilidad.

### Idioma

Identificadores en inglés; documentación, comentarios y mensajes de error en
castellano. Ver `SPEC.md` §2.3.

---

## Comandos

```
make setup      # crea el entorno virtual e instala dependencias
make verify     # ruff + mypy + pytest + humo. Esto es lo que decide si algo vale
make lint       # sólo ruff
make typecheck  # sólo mypy
make test       # sólo pytest
make report     # informe HTML completo          (a partir de M7)
make run-day    # un día de paper trading        (a partir de M8)
make dashboard  # dashboard estático             (a partir de M9)
```

En Windows no hay `make`. Usa el atajo equivalente, que ejecuta exactamente lo
mismo:

```
.\make.ps1 verify
```

`make verify` es el único juez. Si pasa en local pero falla en CI, manda CI.

---

## Git

- Se trabaja sobre `main`. `main` siempre pasa `make verify`.
- Un commit por unidad de trabajo con sentido, no uno gigante al final de la
  noche.
- Mensajes en castellano, empezando por el hito: `M5: test anti look-ahead`.
- Nunca `--force` sobre `main`. Nunca `--no-verify`.
- Antes de cada commit, comprueba que no se cuela nada que no deba: `.env`,
  claves, ficheros de `data/`, tokens en el código.
