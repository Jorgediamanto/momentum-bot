# Fixtures

Datos de prueba. **Todos son sintéticos**: ninguno procede de un mercado real.
Están hechos a mano para que el resultado esperado se pueda calcular con papel
y lápiz, que es lo que hace útil a un test.

## `prices/`

Formato de cada fichero, un `<SÍMBOLO>.csv` por valor:

```
date,open,high,low,close,volume
2024-01-01,100.00,101.00,99.00,100.00,1000000
```

Los precios se suponen **ya ajustados** por splits y dividendos, igual que los
entregará la capa de datos real. Las columnas van en inglés porque así las dan
las fuentes públicas de precios.

Las fechas son los 65 días entre semana del 1 de enero y el 29 de marzo de
2024. No se han quitado festivos a propósito: los calendarios reales, con sus
festivos distintos por mercado, son cosa de M1 y llevarán sus propios fixtures.

### `prices/flat/`

Precios que no se mueven: `AAA` a 100,00 y `BBB` a 50,00 todos los días.

Sirve para el test de conservación del dinero. Si los precios no cambian, el
patrimonio final tiene que ser exactamente lo aportado. Cualquier céntimo de
diferencia es un error de contabilidad, y no hay forma de discutirlo.

### `prices/trend/`

Precios en movimiento lineal: `AAA` sube 0,50 al día desde 100,00 y `BBB` baja
0,10 al día desde 50,00. Fuerza compras y ventas de verdad, para que el motor
tenga que reajustar la cartera.

Los pasos son de dos decimales exactos a propósito, para que los importes no
arrastren redondeos que no vengan del código que se está probando.
