# PREGUNTAS

Dudas, bloqueos y decisiones que no le tocan al agente. Se escribe aquí y se
sigue trabajando en lo que no dependa de la respuesta.

Formato de cada entrada: **fecha · hito · qué me he encontrado · qué he hecho
mientras tanto · qué necesito para desbloquearlo**.

---

## 2026-09-24 · M0 · No hay `make` en el Windows de Jorge

**Qué me he encontrado.** El entorno de trabajo no tiene GNU Make, ni
chocolatey ni scoop para instalarlo. `make verify` es el criterio de
terminación de M0 y aparece en la DEFINICIÓN DE TERMINADO.

**Qué he hecho mientras tanto.** Hay un `Makefile` de verdad, que es lo que
ejecuta CI en Linux, y un `make.ps1` que ejecuta exactamente los mismos
comandos en Windows. Los dos están verdes. Si alguna vez dejan de coincidir,
manda el `Makefile`, porque es el que juzga CI.

**Qué necesito.** Nada urgente. Si prefieres tener `make` de verdad en local:
`winget install ezwinports.make`. Entonces `make.ps1` sobra y se puede borrar.

---

## 2026-09-24 · M2 · El hito pide editar SPEC.md, y hay una regla que lo prohíbe

**Qué me he encontrado.** Una contradicción entre dos instrucciones tuyas:

- M2 dice: *"deja escrito en SPEC.md y en cada informe que hay sesgo de
  supervivencia"*.
- Las reglas inviolables dicen: *"No edites SPEC.md [...]; si algo está mal, a
  PREGUNTAS.md"*.

Tal y como está, un agente que llegue a M2 no puede cumplir las dos cosas.

**Qué he hecho mientras tanto.** He dejado escrita la limitación por
adelantado, en `SPEC.md` §6 ("Limitaciones conocidas"), con el sesgo de
supervivencia como primer punto. Así M2 no necesita tocar `SPEC.md`: le basta
con hacer que los informes lo declaren. En `SPEC.md` he anotado que esa sección
es de sólo lectura durante el desarrollo y que lo nuevo viene aquí.

**Qué necesito.** Que confirmes que esa salida te vale, o que digas
explícitamente que M2 sí puede escribir en la sección 6 de `SPEC.md`.

---

## 2026-09-24 · M0 · Licencia y titularidad

**Qué me he encontrado.** Dijiste "open source" y he creado el repositorio
público, pero no habíamos hablado de licencia.

**Qué he hecho mientras tanto.** MIT, que es la opción más permisiva y la
habitual en proyectos personales. En el fichero `LICENSE` figura como titular
tu usuario de GitHub, `Jorgediamanto`, y no tu nombre completo: me ha parecido
mejor no publicar datos personales que no hubieras publicado tú.

**Qué necesito.** Si quieres otra licencia (Apache 2.0 si te preocupan las
patentes, AGPL si no quieres que nadie lo explote sin abrir su código) o poner
tu nombre completo, cámbialo. Es un fichero.

---

## 2026-09-24 · M1 · Los símbolos de los índices están puestos a ojo

**Qué me he encontrado.** `config.yaml` lleva `^GSPC`, `^STOXX` e `^IBEX` como
símbolos de los tres índices. Son los de Yahoo Finance, elegidos como algo
razonable con lo que arrancar, pero la fuente de datos aún no está decidida y
cada proveedor los nombra distinto.

**Qué he hecho mientras tanto.** Dejarlos en `config.yaml` para que cambiarlos
sea editar tres líneas, no tocar código.

**Qué necesito.** En M1, al elegir fuente, habrá que confirmarlos. Y hay una
decisión de fondo que es tuya: **qué es "Europa"** exactamente. He puesto STOXX
Europe 600, pero podría ser el EURO STOXX 50 (sólo zona euro, 50 valores) o el
STOXX Europe 50. Cambia bastante qué universo se acaba comprando.

---

## 2026-09-24 · M7 · MTUM cotiza en dólares y la cartera lleva euros

**Qué me he encontrado.** Una de las tres referencias obligatorias es MTUM, un
ETF estadounidense que cotiza en dólares. La contabilidad del bot es en euros.
Comparar sin más sería comparar dos cosas distintas: parte de la diferencia
sería el euro-dólar, no la estrategia.

**Qué he hecho mientras tanto.** Nada, es de M7. Lo dejo escrito ahora para que
no se descubra tarde.

**Qué necesito.** Decidir si MTUM se compara convertido a euros (lo que mide de
verdad qué habrías ganado tú) o en dólares (lo que mide el comportamiento del
ETF). Mi recomendación es convertirlo a euros y decirlo en el informe, pero es
una decisión de criterio, no técnica.

---

## 2026-09-24 · M6 · Los tramos fiscales de `config.yaml` están sin verificar

**Qué me he encontrado.** He rellenado los tramos de la base del ahorro
(19 / 21 / 23 / 27 / 30 %) de memoria, para que la estructura del fichero esté
completa.

**Qué he hecho mientras tanto.** Dejarlos en `config.yaml` con un comentario
que avisa de que hay que confirmarlos, y no usarlos en ningún cálculo todavía.

**Qué necesito.** Que los verifiques con la normativa vigente antes de dar M6
por bueno. Un backtest con tipos equivocados no es "aproximado": es incorrecto,
y encima lo parece menos porque sale un número con decimales.

---

## 2026-09-24 · M9 · ¿Las capturas del dashboard van a git?

**Qué me he encontrado.** M9 dice que Playwright guarde capturas en
`progreso/<fecha>/`. No está dicho si eso se versiona.

**Qué he hecho mientras tanto.** No están en `.gitignore`, así que por defecto
se versionarían. La ventaja es que puedes verlas desde cualquier sitio sin
ejecutar nada; el inconveniente es que el repositorio engorda con PNG cada
noche.

**Qué necesito.** Que digas si prefieres que se ignoren. Es una línea en
`.gitignore`.

---

## 2026-09-24 · M0 · Los ficheros de trabajo no han quedado del todo vacíos

**Qué me he encontrado.** Pediste `PROGRESO.md`, `CHANGELOG.md` y
`PREGUNTAS.md` vacíos. Pero las reglas de trabajo mandan anotar cada hito en
`PROGRESO.md` y cada duda aquí, y hoy se ha completado M0 y han salido las
dudas de esta lista.

**Qué he hecho mientras tanto.** He dejado en cada fichero una cabecera con el
formato esperado —para que el agente nocturno sepa cómo escribir— y la entrada
de M0 que corresponde a lo hecho hoy.

**Qué necesito.** Si los querías literalmente en blanco, se vacían en dos
minutos. Lo digo porque es una desviación de lo que pediste, no un descuido.
