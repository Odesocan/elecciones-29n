---
type: metodologia
fase: investigacion
proyecto: PE_29N
tags: [PE_29N, igds, validacion, kappa, fiabilidad]
status: vigente
actualizado: 2026-11-17
aliases: ["PE_29N · Validación humana del IGDS"]
fuente: "OBSERVATORIO/Programas electorales 29N/docs/VALIDACION-IGDS.md"
---

# Validación humana del IGDS

La primera codificación del IGDS la hizo una IA ([ANALISIS-IGDS.md](ANALISIS-IGDS.md)). Antes de visualizarla, el equipo comprueba tres cosas:

- si la regla se aplica bien;
- si se aplica igual a todas las formaciones;
- si el número de medidas (el denominador) es correcto.

Hay tres hojas en `datos/igds/validacion/`. Son archivos CSV con «;» que se abren en Excel o en cualquier hoja de cálculo; guárdalos en el mismo formato.

| Hoja | Qué contiene | Qué mide | Tiempo aproximado |
|---|---|---|---|
| **A · codificación ciega** (`A-codificacion-ciega.csv`) | 150 medidas al azar, 30 por formación, sin la codificación de la IA | Fiabilidad: acuerdo y kappa por dimensión | 5 h |
| **B · verificación** (`B-verificacion.csv`) | Todas las medidas que más pesan en el resultado: garantías completas, regresivas y medidas con ajuste de coherencia (189) | Si las decisiones clave se sostienen | 3 h |
| **C · atomización** (`C-atomizacion.csv`) | 50 unidades, 10 por formación, con su texto completo y las medidas que salieron de él | Si el denominador está bien construido | 2,5 h |

**Ampliación con el PSOE (15-11-2026).** El PSOE se añadió al final de cada hoja con su propia semilla, sin cambiar ni una fila de las anteriores:
- hoja A: códigos A-091 a A-120 (hasta que se rehízo la hoja A el 17-11-2026, más abajo);
- hoja B: 52 filas;
- hoja C: 10 unidades.

**Ampliación con UPC (16-11-2026).** UPC se añadió igual, al final de cada hoja y con su propia semilla:
- hoja A: códigos A-121 a A-150 (hasta que se rehízo la hoja A el 17-11-2026);
- hoja B: ninguna fila, porque UPC no tiene garantías completas, medidas regresivas ni ajustes de coherencia;
- hoja C: 10 de sus 16 ejes. Conviene mirarlos con atención: UPC es la formación con más medidas por eje (4,7), porque sus ejes son enumeraciones.

**Cambio de criterio en DES (16-11-2026).** DES solo vale 1 si la medida da acceso público sin ningún tipo de copago ([CRITERIOS-IGDS.md](CRITERIOS-IGDS.md)). El cambio se aplicó con tres grupos «DES (16-11)» de `ajustes.json`, y 138 medidas pasan a DES 0. Las hojas se generaron antes, así que hay que tenerlo en cuenta al revisarlas:
- **Hoja A (ciega):** se rehízo el 17-11-2026, después de este cambio, y sigue sin mostrar la codificación. Hay que codificar DES con el criterio nuevo.
- **Hoja B:** muestra DES con el criterio anterior y no incluye los nuevos ajustes. Al revisarla, se aplica el criterio nuevo. Las garantías completas que dejaron de serlo (6 del PP y 36 del PSOE) siguen en la hoja.
- **UPC:** la regulación del alquiler (`upc-005-03`) ya no puede cambiar su IGDS, porque ahora tiene DES 0.

En las hojas B y C, si alguien ya había empezado, solo tiene que seguir por el final. La hoja A vigente, rehecha el 17-11-2026, mezcla las filas de las cinco formaciones.

Se puede repartir entre varias personas, pero **la hoja A tiene que hacerla primero alguien que no haya visto la codificación**: ni `igds-medidas.csv`, ni `datos/igds/codificacion/`, ni la hoja B, ni los informes, ni `clave-A.json`, que es la que traduce los códigos A-001… a medidas. Si se ve antes, la persona se ancla en lo que decidió la IA y el acuerdo sale inflado.

**La clave de la hoja A no se publica.** `datos/igds/validacion/clave-A.json` está fuera del repositorio público (en `.gitignore`) y la guarda el equipo de ODESOCAN. Hace falta para dos cosas: calcular la concordancia (`igds concordancia`) y ampliar la muestra con una formación nueva (`igds muestra`). Sin ella, `igds muestra` se para en lugar de rehacer la hoja A con otros códigos, y si la clave no corresponde a la hoja A (por ejemplo, una copia de una clave anterior), `igds muestra` e `igds concordancia` también se paran, para no calcular la kappa comparando medidas distintas. Conviene guardar una copia en el almacenamiento interno del equipo. El resto de la codificación de la IA sí es pública, así que quien haga la hoja A tampoco debe consultar el repositorio ni la web de la herramienta en la parte del IGDS.

### La hoja A se rehízo el 17-11-2026

La clave se subió por error al repositorio en los commits `e1d94de` y `4f26d4c` (16-11-2026) y se retiró en `9693c5d`, pero sigue en el historial público de `main`, donde cualquiera puede recuperarla, y descifraba las 150 filas de la hoja A de entonces. Como nadie había empezado esa hoja (0 de 150 medidas codificadas), se rehízo con `python3 maestro.py igds muestra --rehacer-a`:

- La hoja A tiene una muestra nueva de 150 medidas, 30 por formación con los mismos estratos (20 del ámbito social y 10 del resto, fuera de la hoja B), con las cinco formaciones mezcladas. La muestra es independiente de la anterior, así que 30 medidas coinciden con las de entonces, pero con otro código.
- Ninguna de las claves del historial corresponde a la hoja vigente: aplicadas a ella, no aciertan ninguna de las 150 medidas.
- Las hojas B y C no cambian.
- La semilla de la hoja A ya no es la de `config/igds.json`, que es pública: con ella y los datos públicos se podría volver a generar la muestra y, con ella, la clave. Ahora se sortea al generar la hoja y solo se guarda en `clave-A.json`.
- Las claves anteriores ya no sirven. Quien tenga una copia en local debe borrarla y sustituirla por la vigente, que guarda el equipo de ODESOCAN.
- El historial no se ha reescrito. Eliminar el archivo exigiría un force-push a `main` que debe decidir el equipo, y tampoco cerraría la vía que se explica a continuación.

### Hasta dónde llega la codificación ciega

La codificación de la IA es pública (`datos/igds/igds-medidas.csv` y `datos/igds/codificacion/`), y las columnas `fragmento` y `medida_sintesis` de la hoja A son las mismas que las de `igds-medidas.csv`, de modo que basta buscar una fila de la hoja A en ese archivo para ver cómo la codificó la IA, sin necesidad de clave: en la comprobación del 17-11-2026, ese cruce identificó sin ambigüedad las 150 filas de la hoja vigente. Mantener la clave fuera del repositorio evita el atajo más directo, pero que la hoja A sea ciega depende de que la persona que la codifica no consulte el repositorio, la web de la herramienta ni los informes. Por eso conviene entregarle solo el archivo de la hoja A, junto con los criterios, y no el enlace al repositorio.

Antes de empezar, lee [CRITERIOS-IGDS.md](CRITERIOS-IGDS.md): el libro (apartado 1), qué es un derecho social (2.2), los casos frontera (2.4) y los ejemplos resueltos (2.7).

## Hoja A · codificación ciega

Cada fila es una medida, que se describe en `medida_sintesis`. El `fragmento` es la cita literal y `texto_de_la_unidad` es el contexto. Codifica solo esa medida, no la unidad entera.

Columnas que se rellenan:

| Columna | Qué poner |
|---|---|
| `area` | VIV, SAN, SME, EDU, EMP, CUI, MAM, EVE, MIG, IGU u OTR |
| `uni`, `exi`, `des`, `ndi` | 0 o 1, cada una con su regla y sin mirar las demás |
| `reg`, `dec` | 0 o 1 |
| `comentario` | Opcional: dudas o por qué te apartas de la regla |

## Hoja B · verificación

Aquí sí se ve la codificación, con su justificación. La columna `estrato` dice por qué está la medida en la hoja (g = 1, regresiva o ajuste) y `ajuste` dice qué regla de coherencia se le aplicó.

| Columna | Qué poner |
|---|---|
| `de_acuerdo` | «sí» o «no» |
| `correccion` | Solo si es «no»: los campos que cambian, con el formato `campo=valor; campo=valor` (por ejemplo, `des=0; reg=1`). Campos posibles: area, uni, exi, des, ndi, reg, dec, repite |
| `comentario` | Por qué |

## Hoja C · atomización

Cada fila es una unidad del programa (una medida numerada o un bloque de prosa) con las medidas que la IA sacó de ella. Las marcadas «repite» no cuentan en el denominador.

| Columna | Qué poner |
|---|---|
| `valoracion` | «bien», «faltan», «sobran» o «mal divididas» |
| `n_medidas_propuesto` | Opcional: cuántas medidas debería haber |
| `comentario` | Cuáles faltan o sobran |

Recuerda la regla de atomización: una medida es una acción sobre un objeto, y varios instrumentos para un mismo objeto cuentan una vez. Los diagnósticos y los lemas no son medidas.

## Después

```bash
python3 maestro.py igds concordancia
```

Escribe `datos/informes/igds-validacion.md` con lo siguiente:
- **Hoja A:** porcentaje de acuerdo y kappa de Cohen por dimensión y por formación, más la lista de discrepancias.
- **Hoja B:** porcentaje de acuerdo por grupo y las correcciones propuestas.
- **Hoja C:** valoración de la atomización.

Si una hoja tiene un valor no válido, el informe lo dice.

**Cómo leer la kappa:** a partir de 0,80 la regla es fiable; entre 0,67 y 0,80, provisional; por debajo de 0,67, hay que reescribir la regla. Con categorías poco frecuentes (EXI, g, REG) la kappa es inestable aunque el acuerdo sea alto. Por eso se lee junto al porcentaje de acuerdo y a la hoja B, que revisa todos esos casos.

**Precisión:** con 90 medidas, el acuerdo global tiene un margen aproximado de ± 7 puntos; por formación (30 medidas), de ± 13. Es una validación piloto, suficiente para detectar reglas que fallan, no para certificar cifras.

**Qué se hace con los resultados:**
1. El equipo decide qué correcciones acepta.
2. Las aceptadas se añaden como un grupo nuevo «Validación humana» en `datos/igds/ajustes.json`, con su motivo. Los archivos de codificación no se tocan.
3. Si una dimensión no llega a 0,67, se reescribe su regla en los criterios y se vuelve a codificar esa dimensión en todas las formaciones.
4. Se recalcula con `python3 maestro.py igds calcular`.

**La muestra es fija.**
- **Hoja A:** se elige al azar con una semilla secreta, que se guarda en `clave-A.json` y no en `config/igds.json`. Por formación son 20 medidas del ámbito social y 10 del resto, y no incluye las que ya están en la hoja B. Una formación que se codifique después se añade al final con una semilla derivada de la secreta y de su id, sin tocar lo anterior.
- **Hoja C:** 10 unidades al azar por formación, con la semilla pública de `config/igds.json`.
- **Rehacer la muestra:** `igds muestra` se niega a sobrescribir hojas en las que ya hay trabajo, y si ya cubre todas las formaciones no rehace nada; las tres hojas solo se rehacen con `--forzar`. No la rehagas una vez repartidas las hojas.
- **Rehacer solo la hoja A**, con una clave nueva y sin tocar B ni C (por ejemplo, si la clave deja de ser secreta): `igds muestra --rehacer-a`. Se niega si la hoja A ya tiene trabajo, salvo con `--forzar`.
