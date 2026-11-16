---
type: proyecto
fase: analisis
proyecto: PE_29N
tags: [PE_29N, igds, analisis, derechos-sociales, robustez]
status: vigente
actualizado: 2026-11-16
aliases: ["PE_29N · Análisis previo del IGDS"]
fuente: "OBSERVATORIO/Programas electorales 29N/docs/ANALISIS-IGDS.md"
---

# IGDS · Análisis previo de la prueba

Índice de Garantía de Derechos Sociales aplicado a los programas de las Elecciones Generales del 29N 2026 (Cortes Generales). Estado a 15-11-2026, con el PSOE incorporado.

**Es una primera codificación, pendiente de validación humana.** La hizo una IA con el libro de códigos de [CRITERIOS-IGDS.md](CRITERIOS-IGDS.md), en lotes independientes, y la coordinación la revisó para que todas las formaciones tuvieran la misma regla. Todavía no tiene visualización. UPC no entra porque su programa aún no está publicado.

**Dónde está cada cosa:**

| Qué | Archivo |
|---|---|
| Una fila por medida, con fragmento literal, página, códigos y justificación | [datos/igds/igds-medidas.csv](../datos/igds/igds-medidas.csv) |
| Matriz por área temática | [datos/igds/igds-areas.csv](../datos/igds/igds-areas.csv) |
| Informe completo: fase 0, resultados, matriz, silencios, repeticiones, ajustes y casos dudosos | [datos/informes/igds.md](../datos/informes/igds.md) |
| Medidas con g = 1, regresivas y señales de incoherencia | [datos/informes/igds-contraste.md](../datos/informes/igds-contraste.md) |
| Ajustes de coherencia, con su regla y su motivo | [datos/igds/ajustes.json](../datos/igds/ajustes.json) |

Todo se regenera con `python3 maestro.py igds calcular`.

---

## 1. Fase 0: los cuatro programas se leen completos

| | CC–1ºC | PP | PSOE | Vox |
|---|---|---|---|---|
| Páginas | 23 | 82 | 114 | 66 |
| Índice / apartados | no / 10 causas | sí / 28 | sí / 83 | sí / 13 |
| Páginas sin texto | 1 | 14 | 4 | 26 |
| Medidas numeradas | 100 | 241 | 500 | 115 |
| Bloques de prosa fuera de las medidas | 17 (2.891 palabras) | 8 (2.696 palabras) | 85 (15.297 palabras) | 0 |
| Texto asignado a alguna unidad | 100 % | 100 % | 100 % | 99,9 % |

- Las páginas sin texto se revisaron a la vista. Son portadas, fotografías, separadores o páginas en blanco; ninguna es una imagen con medidas.
- **Particularidades de los PDF originales**, que no son fallos de lectura:
  - el PP tiene 8 huecos «Permanezca atento a la campaña» sin contenido;
  - la medida 11 de CC–1ºC y el compromiso 395 del PSOE están cortados en el propio PDF;
  - el manifiesto de CC–1ºC repite, oculto, un párrafo de la página 4 en la página 3, y se cuenta una vez;
  - el PSOE numera dos veces la misma propuesta (70 y 72).
- Se ha codificado el programa entero, no solo las medidas numeradas.
- **La prosa casi no cambia el denominador:**
  - CC–1ºC: 20 compromisos, 16 de los cuales repiten medidas numeradas;
  - PP: 46, y todos las repiten;
  - PSOE: en sus 15.297 palabras de prosa hay 125 compromisos, y solo 15 no repiten un compromiso numerado.

## 2. Resultados

| Indicador | CC–1ºC | PP | PSOE | Vox |
|---|---|---|---|---|
| N (medidas) | 174 | 617 | 681 | 256 |
| **IGDS** | **0,0** (0/174) | **2,4** (15/617) | **7,0** (48/681) | **0,4** (1/256) |
| I_UNI | 27,0 (47) | 20,3 (125) | 43,2 (294) | 23,0 (59) |
| I_EXI | 0,0 (0) | 4,9 (30) | 10,4 (71) | 0,8 (2) |
| I_DES | 16,7 (29) | 12,3 (76) | 30,8 (210) | 12,5 (32) |
| I_NDI | 32,2 (56) | 26,3 (162) | 49,5 (337) | 26,2 (67) |
| IR (regresivas) | 1,1 (2) | 3,9 (24) | 0,0 (0) | 17,2 (44) |
| IV (declarativas) | 32,8 (57) | 28,8 (178) | 31,7 (216) | 34,8 (89) |
| Dimensión limitante | EXI | EXI | EXI | EXI |
| Áreas en silencio | ninguna | EVE | EVE | EVE |

El control de calidad se cumple en las cuatro formaciones:
- IGDS ≤ mínimo de los I_k;
- DEC → EXI 0;
- g = 1 → las cuatro dimensiones a 1;
- REG → g 0;
- la suma de las áreas es igual a N;
- no hay identificadores repetidos.

## 3. Lectura

### 3.1 Las garantías completas son minoría en los cuatro programas

En ningún programa llegan a 8 de cada 100 medidas las que son garantía objetiva de un derecho social. La dimensión limitante es la misma en los cuatro: la **exigibilidad**. Los programas nombran derechos y servicios, pero pocas veces con un instrumento obligatorio (ley que reconozca el derecho, plazo máximo, ratio, estándar u obligación de provisión).

- **CC–1ºC:** 0 garantías completas. 26 medidas cumplen tres dimensiones y fallan solo en EXI.
- **PP:** 15 garantías completas, sobre todo en educación (6) y en regulación de suministros y vivienda (3). Otras 63 están a una dimensión de serlo, la mayoría (51) por EXI.
- **PSOE:** 48 garantías completas.
  - Por áreas: empleo (11), igualdad (9), otras áreas (8, sobre todo protección de menores en entornos digitales), sanidad (5), vivienda (5), cuidados (4) y educación (4).
  - Ejemplos: el salario mínimo por ley, la jornada de 37,5 horas, la prestación universal por crianza, la Ley de Servicios Sociales con cartera común, la atención psicológica pública en 30 días y la limitación de las subidas del alquiler en zonas tensionadas.
  - Otras 158 están a una dimensión, 136 de ellas por EXI.
- **Vox:** 1 garantía completa (la gratuidad de 0 a 3 años). Otras 27 están a una dimensión, 26 de ellas por EXI.

### 3.2 Entre un tercio y la mitad de cada programa trata derechos sociales

El libro pone en el denominador todas las medidas, también las que no tratan derechos sociales (OTR). Por eso conviene mirar dentro del ámbito social, es decir, las medidas que tienen alguna dimensión a 1 o son regresivas.

| | CC–1ºC | PP | PSOE | Vox |
|---|---|---|---|---|
| Medidas en el ámbito social | 58 (33,3 %) | 186 (30,1 %) | 337 (49,5 %) | 111 (43,4 %) |
| IGDS dentro del ámbito social | 0,0 | 8,1 | 14,2 | 0,9 |
| UNI · EXI · DES · NDI dentro del ámbito social | 81 · 0 · 50 · 97 | 67 · 16 · 41 · 87 | 87 · 21 · 62 · 100 | 53 · 2 · 29 · 60 |
| REG dentro del ámbito social | 3,4 | 12,9 | 0,0 | 39,6 |

El orden de las formaciones no cambia con el denominador, pero las magnitudes sí. Las dos lecturas responden a preguntas distintas:
- **sobre todo el programa:** qué parte del programa es garantía;
- **sobre el ámbito social:** cómo se garantiza lo que se propone en derechos sociales.

### 3.3 La regresividad se concentra en migración, con alcance distinto en cada programa

- **PP:** 24 regresivas, 18 de ellas en MIG (expulsiones, internamiento, asilo, regularización, nacionalidad).
- **Vox:** 44 regresivas, repartidas en 9 áreas. 16 están en MIG; las demás, en vivienda (8), educación (5), medio ambiente (4), sanidad (3) y otras. La mayoría introduce la nacionalidad como condición de acceso («prioridad nacional»).
- **CC–1ºC:** 2 regresivas: limitar la compra de vivienda por personas extranjeras y la Ley Canaria de Residencia.
- **PSOE:** ninguna. Sus medidas de migración amplían vías legales, acogida y protección internacional.

### 3.4 Alrededor de un tercio de cada programa es declarativo

El índice de declaratividad va del 28,8 al 34,8 y es parecido en las cuatro formaciones. Cerca de una de cada tres medidas carece de instrumento: ni norma, ni prestación, ni plan, ni dotación.

## 4. Robustez: qué puede mover los resultados

**1. Dos rondas de codificación.** Este es el punto más importante para leer la comparación.
   - **CC–1ºC, PP y Vox** se codificaron el 14-11 en lotes que mezclaban formaciones. Después se armonizaron con 67 ajustes.
   - **El PSOE** se codificó el 15-11, solo, con las reglas ya corregidas y calibrando con la codificación armonizada de los otros tres. Solo necesitó 7 ajustes: 5 corrigen repeticiones entre lotes y 2 aplican la regla de la justicia.
   - **Comprobaciones hechas:** sus 48 garantías completas se revisaron una a una contra los casos equivalentes de los demás. Por ejemplo, la ley contra la trata también da g = 1 en el PP, y la protección de menores en plataformas digitales también.
   - **Lo que no se puede descartar** sin validación humana es un efecto de la persona codificadora: otras instancias y otro día. La diferencia de magnitud es grande: el IGDS del PSOE es casi el triple que el del PP.
   - **Cómo se comprueba:** la muestra ciega de la hoja A incluye 30 medidas del PSOE, y la hoja B, todas sus garantías completas.

**2. Ajustes de coherencia.** Afectan a 71 medidas que cuentan en N: CC–1ºC 5, PP 37, PSOE 4 y Vox 25. Otros ajustes solo marcan repeticiones, que no cuentan.
   - **Antes de los ajustes:** IGDS 0,0 · 1,1 · 7,3 · 0,8.
   - **Después:** 0,0 · 2,4 · 7,0 · 0,4.
   - **PP:** el ajuste que más pesa es DES. Los lotes habían aplicado de forma desigual la aclaración «no se presume provisión pública», a veces dentro de la misma medida (pp-227).
   - **Vox:** la cotización por crianza «para los españoles» pasa a NDI 0, con la misma regla que cualquier prestación delimitada por nacionalidad.
   - **PSOE:** la justicia gratuita para víctimas de abusos inmobiliarios y los juicios por despido en tres meses pasan a 0 en las cuatro. Es la misma regla que ya tenía la asistencia jurídica de Vox: la justicia no cuenta salvo en violencia de género, infancia o trata.

**3. Cómo está formulado el programa.**
   - El 44,8 % de las medidas de CC–1ºC empieza por «reclamar», «exigir» o «defender» ante el Estado. En el PP es el 3,1 %, en el PSOE el 1,5 % y en Vox el 2,0 %.
   - Por regla, pedir a otro que actúe no es exigibilidad (EXI 0). Por eso el IGDS de CC–1ºC es 0, aunque en el ámbito social tenga valores altos de UNI (81), DES (50) y NDI (97).
   - **Límite del índice para comparar:** mide si la formación compromete un instrumento obligatorio. No mide la orientación de lo que pide. Afecta sobre todo a formaciones que no se presentan como Gobierno.

**4. Atomización.**
   - El denominador depende de cómo se dividen las medidas.
   - Por unidad numerada salen 1,7 medidas en CC–1ºC, 2,6 en el PP, 1,4 en el PSOE y 2,3 en Vox. Las medidas del PSOE son más cortas (39 palabras de media frente a 82 en el PP), así que la densidad por palabra es parecida en los cuatro.
   - Una persona debe revisarlo en una muestra (hoja C).

**5. Casos dudosos.** Llevan `revisar = 1`, con motivo y propuesta:
   - CC–1ºC: el 20,7 %;
   - PP: el 21,2 %;
   - PSOE: el 27,6 %;
   - Vox: el 35,2 %, sobre todo por los casos frontera de NDI y REG.

**6. Repeticiones.** Se descartaron 250: CC–1ºC 18, PP 58, PSOE 163 y Vox 11. Casi todas son compromisos de la prosa que repiten medidas numeradas.

**7. Medio ambiente y biodiversidad.** El libro cuenta el medio ambiente sano como derecho social. Por eso entran medidas como reducir la velocidad marítima para proteger cetáceos (PSOE, g = 1). Es coherente con la regla, pero conviene que el equipo confirme la frontera (punto 7 del apartado 5).

## 5. Problemas del libro de códigos que hay que decidir

1. **No hay área de protección social.** Pensiones, ingreso mínimo vital y prestaciones familiares van a OTR y se diluyen. *Propuesta:* añadir un área PRO (garantía de ingresos).
2. **DES y prestaciones monetarias.** Se ha leído que una prestación pública de garantía de ingresos es «provisión pública directa» (DES 1), y que una ayuda ligada a comprar en el mercado es DES 0. *Propuesta:* confirmarlo o fijar lo contrario.
3. **DES en igualdad y regulación.** Se ha aplicado DES 1 a las leyes de protección y a la regulación obligatoria de condiciones (alquiler, plataformas, mercado laboral). *Propuesta:* confirmarlo. Afecta mucho al PSOE, cuyas garantías completas son en buena parte regulación.
4. **EXI y las formaciones que no gobiernan.** «Reclamar al Estado» vale siempre 0. *Propuesta:* mantener la regla y añadir un indicador complementario de orientación, por ejemplo la proporción de medidas que cumplen UNI, DES y NDI aunque fallen en EXI.
5. **Motivos de regresividad.** La lista (origen, situación administrativa, sexo, género, orientación) no incluye religión ni lengua. Afecta a los menús halal, al programa de lengua árabe y a la prohibición del burka. *Propuesta:* decidir si se añaden.
6. **Regresividad implícita.** Hay medidas que no nombran la garantía que suprimen: «derecho a la vida desde la concepción», derogaciones genéricas o la legislación laboral. *Propuesta:* REG 1 solo si el texto identifica la garantía, y `revisar` en los demás casos.
7. **Medio ambiente.** No está claro dónde acaba la política energética o sectorial y dónde empieza el derecho a un medio ambiente sano. *Propuesta:* solo cuentan como derecho las medidas que actúan sobre la calidad ambiental (agua, depuración, restauración, arbolado, emisiones) y la biodiversidad.
8. **Qué es una medida.** Falta decidir si los lemas, los compromisos de conducta parlamentaria («cada investidura se valorará por…»), las peticiones de voto y las frases en presente («apostamos por», «defendemos») son medidas. *Propuesta:* las peticiones de voto y la conducta parlamentaria, no; las frases en presente, sí, cuando nombran una acción sobre un objeto.

Al codificar el PSOE se fijaron además tres reglas, ya escritas en los criterios:
- **Justicia:** la justicia gratuita y los plazos judiciales solo cuentan como acceso dentro de los sistemas de protección de violencia de género, infancia y trata.
- **Reconocer un derecho:** reconocerlo en una norma con nombre (la Constitución, una ley concreta) da EXI 1; sin nombrar la norma, EXI 0.
- **Leyes:** una ley anunciada sin contenido da EXI 0.

## 6. Antes de visualizarlo

- **Validación humana mínima:**
  - los 71 ajustes;
  - las 64 garantías completas (16 de CC–1ºC, PP y Vox, y 48 del PSOE);
  - las 70 regresivas;
  - una muestra ciega de 30 medidas por formación.

  Las hojas están en `datos/igds/validacion/` y se han ampliado con el PSOE sin cambiar las filas anteriores. Cómo rellenarlas está en [VALIDACION-IGDS.md](VALIDACION-IGDS.md).
- **Decisiones del equipo:** los 8 puntos del apartado 5. Varias cambian los resultados, sobre todo 1, 2, 3, 4 y 5.
- **Para la visualización:**
  - mostrar el **perfil de las cuatro dimensiones**, no solo el IGDS;
  - mostrar el **embudo**: todo el programa → ámbito social → a una dimensión de g = 1 → g = 1;
  - presentar la **regresividad aparte**;
  - indicar siempre el denominador y que hubo dos rondas de codificación hasta que la validación lo cierre;
  - aplicar las reglas de la herramienta: orden alfabético, las mismas reglas para todas las formaciones, fragmento literal de cada medida, y UPC «pendiente de publicar».
