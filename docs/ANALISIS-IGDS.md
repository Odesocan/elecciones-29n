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

Índice de Garantía de Derechos Sociales aplicado a los programas de las Elecciones Generales del 29N 2026 (Cortes Generales). Estado a 16-11-2026, con las cinco formaciones: el PSOE se incorporó el 15-11 y UPC el 16-11.

**Es una primera codificación, pendiente de validación humana.** La hizo una IA con el libro de códigos de [CRITERIOS-IGDS.md](CRITERIOS-IGDS.md), en lotes independientes, y la coordinación la revisó para que todas las formaciones tuvieran la misma regla. Su visualización, el apartado «Prometer no es garantizar» de la herramienta, se publicó el 16-11-2026 y se retiró de la web ese mismo día a petición del equipo (ver [DISENO.md](DISENO.md), apartado 4). De UPC se codifica su manifiesto «Una sola papeleta. Todo un pueblo» (6 páginas), que la formación comunicó directamente como su único documento programático para el 29N.

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

## 0. Cambio de criterio en DES (16-11-2026)

El equipo fijó que la dimensión 3 (DES) solo vale 1 cuando la medida da acceso público **sin ningún tipo de copago**: un servicio público que hoy es gratuito o una prestación monetaria pública. Pasan a DES 0:
- un límite al precio, que no es una garantía pública;
- la regulación laboral o del mercado y las leyes de protección, que regulan sin proveer;
- la vivienda con renta;
- los servicios con tasas o copago.

Se aplicó a las 363 medidas que tenían DES 1, de las que 138 pasan a 0, con tres grupos de `datos/igds/ajustes.json` y sin tocar la codificación original. La regla está en [CRITERIOS-IGDS.md](CRITERIOS-IGDS.md).

| | CC–1ºC | PP | PSOE | UPC | Vox |
|---|---|---|---|---|---|
| IGDS con el criterio anterior | 0,0 | 2,4 (15) | 7,0 (48) | 0,0 | 0,4 (1) |
| **IGDS ahora** | **0,0** | **1,5** (9) | **1,8** (12) | **0,0** | **0,4** (1) |
| I_DES antes → ahora | 16,7 → 11,5 | 12,3 → 9,6 | 30,8 → 16,9 | 21,3 → 9,3 | 12,5 → 9,4 |
| A una dimensión de la garantía (sin regresivas) | 17 | 58 | 135 | 6 | 20 |

- **Lo que queda como garantía completa:** servicios públicos gratuitos y prestaciones monetarias.
  - PP: educación de 0 a 3 años y FP gratuitas, cuidados paliativos, cotización por cuidados, atención a menores migrantes y medidas de la escuela pública.
  - PSOE: atención psicológica gratuita, salud bucodental, eutanasia, aborto, ratios y orientación en la escuela pública, coeducación, visita a domicilio, prestación por crianza, año cotizado, remuneración de cuidadoras y ayudas a huérfanos.
  - Vox: educación de 0 a 3 años gratuita.
- **Lo que deja de serlo:** la regulación laboral, del alquiler y de las plataformas digitales, y las leyes de protección. Son 36 garantías del PSOE y 6 del PP.
- **La distancia entre PSOE y PP** pasa de casi el triple a 1,8 frente a 1,5: buena parte de la diferencia anterior venía de la regulación.
- **La exigibilidad sigue siendo la dimensión limitante** en las cinco formaciones. En el PSOE, 44 de las medidas que se quedan a una dimensión fallan ahora en DES.
- **UPC:** su regulación del alquiler (upc-005-03) ya no podría cambiar su IGDS, porque ahora tiene DES 0.
- **Casos de frontera** para la validación: servicios sociales, educación de 0 a 3 años, formación profesional, enseñanzas artísticas y tratamientos con copago farmacéutico.

Los apartados 1 a 6 describen la prueba con el criterio anterior, salvo donde se indica.

---

## 1. Fase 0: los cinco programas se leen completos

| | CC–1ºC | PP | PSOE | UPC | Vox |
|---|---|---|---|---|---|
| Páginas | 23 | 82 | 114 | 6 | 66 |
| Índice / apartados | no / 10 causas | sí / 28 | sí / 83 | no / 16 ejes | sí / 13 |
| Páginas sin texto | 1 | 14 | 4 | 2 | 26 |
| Medidas numeradas | 100 | 241 | 500 | 16 | 115 |
| Bloques de prosa fuera de las medidas | 17 (2.891 palabras) | 8 (2.696 palabras) | 85 (15.297 palabras) | 1 (154 palabras) | 0 |
| Texto asignado a alguna unidad | 100 % | 100 % | 100 % | 100 % | 99,9 % |

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
  - PSOE: en sus 15.297 palabras de prosa hay 125 compromisos, y solo 15 no repiten un compromiso numerado;
  - UPC: su único bloque de prosa presenta la coalición y pide el voto, y no tiene medidas.
- **UPC es un manifiesto, no un programa extenso.** Tiene 4 páginas con texto, y sus 16 ejes numerados, 72 palabras de media. Se mide con la misma regla que los demás, pero conviene recordarlo al comparar (apartado 4).

## 2. Resultados

| Indicador | CC–1ºC | PP | PSOE | UPC | Vox |
|---|---|---|---|---|---|
| N (medidas) | 174 | 617 | 681 | 75 | 256 |
| **IGDS** | **0,0** (0/174) | **2,4** (15/617) | **7,0** (48/681) | **0,0** (0/75) | **0,4** (1/256) |
| I_UNI | 27,0 (47) | 20,3 (125) | 43,2 (294) | 44,0 (33) | 23,0 (59) |
| I_EXI | 0,0 (0) | 4,9 (30) | 10,4 (71) | 0,0 (0) | 0,8 (2) |
| I_DES | 16,7 (29) | 12,3 (76) | 30,8 (210) | 21,3 (16) | 12,5 (32) |
| I_NDI | 32,2 (56) | 26,3 (162) | 49,5 (337) | 48,0 (36) | 26,2 (67) |
| IR (regresivas) | 1,1 (2) | 3,9 (24) | 0,0 (0) | 0,0 (0) | 17,2 (44) |
| IV (declarativas) | 32,8 (57) | 28,8 (178) | 31,7 (216) | 70,7 (53) | 34,8 (89) |
| Dimensión limitante | EXI | EXI | EXI | EXI | EXI |
| Áreas en silencio | ninguna | EVE | EVE | EVE | EVE |

El control de calidad se cumple en las cinco formaciones:
- IGDS ≤ mínimo de los I_k;
- DEC → EXI 0;
- g = 1 → las cuatro dimensiones a 1;
- REG → g 0;
- la suma de las áreas es igual a N;
- no hay identificadores repetidos.

## 3. Lectura

### 3.1 Las garantías completas son minoría en los cinco programas

En ningún programa llegan a 8 de cada 100 medidas las que son garantía objetiva de un derecho social. La dimensión limitante es la misma en los cinco: la **exigibilidad**. Los programas nombran derechos y servicios, pero pocas veces con un instrumento obligatorio (ley que reconozca el derecho, plazo máximo, ratio, estándar u obligación de provisión).

- **CC–1ºC:** 0 garantías completas. 26 medidas cumplen tres dimensiones y fallan solo en EXI.
- **PP:** 15 garantías completas, sobre todo en educación (6) y en regulación de suministros y vivienda (3). Otras 63 están a una dimensión de serlo, la mayoría (51) por EXI.
- **PSOE:** 48 garantías completas.
  - Por áreas: empleo (11), igualdad (9), otras áreas (8, sobre todo protección de menores en entornos digitales), sanidad (5), vivienda (5), cuidados (4) y educación (4).
  - Ejemplos: el salario mínimo por ley, la jornada de 37,5 horas, la prestación universal por crianza, la Ley de Servicios Sociales con cartera común, la atención psicológica pública en 30 días y la limitación de las subidas del alquiler en zonas tensionadas.
  - Otras 158 están a una dimensión, 136 de ellas por EXI.
- **UPC:** 0 garantías completas. 15 medidas cumplen tres dimensiones y fallan solo en EXI: la sanidad, la educación y los servicios sociales públicos, la atención primaria, la salud mental, la educación de 0 a 3 años, los cuidados, el parque público de vivienda, la regulación del alquiler, el salario mínimo y la acogida de personas migrantes. Ninguna dice con qué norma, plazo o estándar se garantiza.
- **Vox:** 1 garantía completa (la gratuidad de 0 a 3 años). Otras 27 están a una dimensión, 26 de ellas por EXI.

### 3.2 Entre un tercio y la mitad de cada programa trata derechos sociales

El libro pone en el denominador todas las medidas, también las que no tratan derechos sociales (OTR). Por eso conviene mirar dentro del ámbito social, es decir, las medidas que tienen alguna dimensión a 1 o son regresivas.

| | CC–1ºC | PP | PSOE | UPC | Vox |
|---|---|---|---|---|---|
| Medidas en el ámbito social | 58 (33,3 %) | 186 (30,1 %) | 337 (49,5 %) | 36 (48,0 %) | 111 (43,4 %) |
| IGDS dentro del ámbito social | 0,0 | 8,1 | 14,2 | 0,0 | 0,9 |
| UNI · EXI · DES · NDI dentro del ámbito social | 81 · 0 · 50 · 97 | 67 · 16 · 41 · 87 | 87 · 21 · 62 · 100 | 92 · 0 · 44 · 100 | 53 · 2 · 29 · 60 |
| REG dentro del ámbito social | 3,4 | 12,9 | 0,0 | 0,0 | 39,6 |

El orden de las formaciones no cambia con el denominador, pero las magnitudes sí. Las dos lecturas responden a preguntas distintas:
- **sobre todo el programa:** qué parte del programa es garantía;
- **sobre el ámbito social:** cómo se garantiza lo que se propone en derechos sociales.

### 3.3 La regresividad se concentra en migración, con alcance distinto en cada programa

- **PP:** 24 regresivas, 18 de ellas en MIG (expulsiones, internamiento, asilo, regularización, nacionalidad).
- **Vox:** 44 regresivas, repartidas en 9 áreas. 16 están en MIG; las demás, en vivienda (8), educación (5), medio ambiente (4), sanidad (3) y otras. La mayoría introduce la nacionalidad como condición de acceso («prioridad nacional»).
- **CC–1ºC:** 2 regresivas: limitar la compra de vivienda por personas extranjeras y la Ley Canaria de Residencia.
- **PSOE:** ninguna. Sus medidas de migración amplían vías legales, acogida y protección internacional.
- **UPC:** ninguna. Sus medidas de migración piden vías legales y seguras, acogida digna y protección de la infancia migrante no acompañada.

### 3.4 Un tercio de cada programa es declarativo; en UPC, más de dos tercios

- **CC–1ºC, PP, PSOE y Vox:** el índice de declaratividad va del 28,8 al 34,8 y es parecido en las cuatro formaciones. Cerca de una de cada tres medidas carece de instrumento: ni norma, ni prestación, ni plan, ni dotación.
- **UPC:** el índice es 70,7. En el ámbito social son declarativas 30 de 36 medidas. El manifiesto enuncia posiciones («defendemos», «apostamos por») y casi nunca dice con qué instrumento las llevará a cabo. Es lo esperable en un manifiesto de 6 páginas, pero es su único documento programático y se mide con la misma regla.

## 4. Robustez: qué puede mover los resultados

**1. Tres rondas de codificación.** Este es el punto más importante para leer la comparación.
   - **CC–1ºC, PP y Vox** se codificaron el 14-11 en lotes que mezclaban formaciones. Después se armonizaron con 67 ajustes.
   - **El PSOE** se codificó el 15-11, solo, con las reglas ya corregidas y calibrando con la codificación armonizada de los otros tres. Solo necesitó 7 ajustes: 5 corrigen repeticiones entre lotes y 2 aplican la regla de la justicia.
   - **Comprobaciones hechas:** sus 48 garantías completas se revisaron una a una contra los casos equivalentes de los demás. Por ejemplo, la ley contra la trata también da g = 1 en el PP, y la protección de menores en plataformas digitales también.
   - **Lo que no se puede descartar** sin validación humana es un efecto de la persona codificadora: otras instancias y otro día. La diferencia de magnitud es grande: el IGDS del PSOE es casi el triple que el del PP.
   - **Cómo se comprueba:** la muestra ciega de la hoja A incluye 30 medidas del PSOE, y la hoja B, todas sus garantías completas.
   - **UPC** se codificó el 16-11, también sola, con las mismas reglas y calibrando con la codificación armonizada de las otras cuatro. No necesitó ajustes ni reglas nuevas.
   - **Qué puede mover el IGDS de UPC:** un solo caso dudoso afecta a EXI. Es la regulación de los precios del alquiler en zonas tensionadas (upc-005-03), con EXI 0 porque no dice cómo se regula (ni índice, ni límite, ni congelación). En el PSOE, la medida equivalente da g = 1 porque fija el límite. Si la validación le diera EXI 1, el IGDS de UPC pasaría a 1,3 (1/75).

**2. Ajustes de coherencia.** Afectan a 71 medidas que cuentan en N: CC–1ºC 5, PP 37, PSOE 4, UPC 0 y Vox 25. Otros ajustes solo marcan repeticiones, que no cuentan.
   - **Antes de los ajustes** (CC–1ºC · PP · PSOE · UPC · Vox): IGDS 0,0 · 1,1 · 7,3 · 0,0 · 0,8.
   - **Después:** 0,0 · 2,4 · 7,0 · 0,0 · 0,4.
   - **PP:** el ajuste que más pesa es DES. Los lotes habían aplicado de forma desigual la aclaración «no se presume provisión pública», a veces dentro de la misma medida (pp-227).
   - **Vox:** la cotización por crianza «para los españoles» pasa a NDI 0, con la misma regla que cualquier prestación delimitada por nacionalidad.
   - **PSOE:** la justicia gratuita para víctimas de abusos inmobiliarios y los juicios por despido en tres meses pasan a 0 en las cuatro. Es la misma regla que ya tenía la asistencia jurídica de Vox: la justicia no cuenta salvo en violencia de género, infancia o trata.

**3. Cómo está formulado el programa.**
   - El 44,8 % de las medidas de CC–1ºC empieza por «reclamar», «exigir» o «defender» ante el Estado. En el PP es el 3,1 %, en el PSOE el 1,5 %, en UPC el 25,3 % y en Vox el 2,0 %.
   - Por regla, pedir a otro que actúe no es exigibilidad (EXI 0). Por eso el IGDS de CC–1ºC es 0, aunque en el ámbito social tenga valores altos de UNI (81), DES (50) y NDI (97).
   - **UPC** tiene un perfil parecido en el ámbito social (UNI 92, DES 44, NDI 100) y el mismo IGDS 0. En su caso, las peticiones al Estado y a la Unión Europea se concentran en los ejes de financiación, REF y región ultraperiférica (2, 3 y 4: 13 medidas). En el resto, la EXI 0 viene de que la medida no tiene instrumento.
   - **Límite del índice para comparar:** mide si la formación compromete un instrumento obligatorio. No mide la orientación de lo que pide. Afecta sobre todo a formaciones que no se presentan como Gobierno, como CC–1ºC y UPC.

**4. Atomización.**
   - El denominador depende de cómo se dividen las medidas.
   - Por unidad numerada salen 1,7 medidas en CC–1ºC, 2,6 en el PP, 1,4 en el PSOE y 2,3 en Vox. Las medidas del PSOE son más cortas (39 palabras de media frente a 82 en el PP), así que la densidad por palabra es parecida en las cuatro formaciones: entre 2,8 y 3,9 medidas por cada 100 palabras.
   - **UPC es la excepción:** 4,7 medidas por unidad y 6,5 por cada 100 palabras. Sus ejes son enumeraciones (por ejemplo: «fortalecer la atención primaria, la salud mental, la educación pública de 0 a 3 años y un sistema público de cuidados»), y la regla R4 cuenta cada objeto como una medida. No cambia su IGDS, que es 0, pero sí el peso de cada área.
   - Una persona debe revisarlo en una muestra (hoja C, que incluye 10 de los 16 ejes de UPC).

**5. Casos dudosos.** Llevan `revisar = 1`, con motivo y propuesta:
   - CC–1ºC: el 20,7 %;
   - PP: el 21,2 %;
   - PSOE: el 27,6 %;
   - UPC: el 10,7 %, casi todos de área (agua, migración en los fondos europeos, servicios sociales y pensiones en OTR);
   - Vox: el 35,2 %, sobre todo por los casos frontera de NDI y REG.

**6. Repeticiones.** Se descartaron 256: CC–1ºC 18, PP 58, PSOE 163, UPC 6 y Vox 11. Casi todas son compromisos de la prosa que repiten medidas numeradas. En UPC son ejes que resumen otros; por ejemplo, el eje 1 (autogobierno) adelanta la financiación del eje 2.

**7. Medio ambiente y biodiversidad.** El libro cuenta el medio ambiente sano como derecho social. Por eso entran medidas como reducir la velocidad marítima para proteger cetáceos (PSOE, g = 1). Es coherente con la regla, pero conviene que el equipo confirme la frontera (punto 7 del apartado 5).

## 5. Problemas del libro de códigos que hay que decidir

1. **No hay área de protección social.** Pensiones, ingreso mínimo vital, prestaciones familiares y servicios sociales generales van a OTR y se diluyen. *Propuesta:* añadir un área PRO (garantía de ingresos).
2. **DES y prestaciones monetarias.** Se ha leído que una prestación pública de garantía de ingresos es «provisión pública directa» (DES 1), y que una ayuda ligada a comprar en el mercado es DES 0. *Propuesta:* confirmarlo o fijar lo contrario. **Decidido el 16-11-2026:** DES 1, porque una prestación monetaria pública no tiene copago.
3. **DES en igualdad y regulación.** Se ha aplicado DES 1 a las leyes de protección y a la regulación obligatoria de condiciones (alquiler, plataformas, mercado laboral). *Propuesta:* confirmarlo. Afecta mucho al PSOE, cuyas garantías completas son en buena parte regulación. **Decidido el 16-11-2026:** DES 0. Regular no es proveer, y un límite al precio no es una garantía pública (apartado 0).
4. **EXI y las formaciones que no gobiernan.** «Reclamar al Estado» vale siempre 0. Afecta a CC–1ºC y a UPC. *Propuesta:* mantener la regla y añadir un indicador complementario de orientación, por ejemplo la proporción de medidas que cumplen UNI, DES y NDI aunque fallen en EXI.
5. **Motivos de regresividad.** La lista (origen, situación administrativa, sexo, género, orientación) no incluye religión ni lengua. Afecta a los menús halal, al programa de lengua árabe y a la prohibición del burka. *Propuesta:* decidir si se añaden.
6. **Regresividad implícita.** Hay medidas que no nombran la garantía que suprimen: «derecho a la vida desde la concepción», derogaciones genéricas o la legislación laboral. *Propuesta:* REG 1 solo si el texto identifica la garantía, y `revisar` en los demás casos.
7. **Medio ambiente.** No está claro dónde acaba la política energética o sectorial y dónde empieza el derecho a un medio ambiente sano. *Propuesta:* solo cuentan como derecho las medidas que actúan sobre la calidad ambiental (agua, depuración, restauración, arbolado, emisiones) y la biodiversidad.
8. **Qué es una medida.** Falta decidir si los lemas, los compromisos de conducta parlamentaria («cada investidura se valorará por…»), las peticiones de voto y las frases en presente («apostamos por», «defendemos») son medidas. *Propuesta:* las peticiones de voto y la conducta parlamentaria, no; las frases en presente, sí, cuando nombran una acción sobre un objeto. Afecta sobre todo a UPC, cuyo manifiesto está escrito casi entero así; se ha codificado según esta propuesta, como el resto de formaciones.

Al codificar el PSOE se fijaron además tres reglas, ya escritas en los criterios (UPC no necesitó ninguna nueva):
- **Justicia:** la justicia gratuita y los plazos judiciales solo cuentan como acceso dentro de los sistemas de protección de violencia de género, infancia y trata.
- **Reconocer un derecho:** reconocerlo en una norma con nombre (la Constitución, una ley concreta) da EXI 1; sin nombrar la norma, EXI 0.
- **Leyes:** una ley anunciada sin contenido da EXI 0.

## 6. Antes de visualizarlo

- **Validación humana mínima:**
  - los 71 ajustes;
  - las 64 garantías completas (16 de CC–1ºC, PP y Vox, y 48 del PSOE; UPC no tiene);
  - las 70 regresivas;
  - una muestra ciega de 30 medidas por formación;
  - en UPC, además, la regulación del alquiler (upc-005-03), que con el criterio anterior era la única medida que podía mover su IGDS (con el de DES del 16-11, ya no).

  Las hojas están en `datos/igds/validacion/` y se han ampliado con el PSOE y con UPC sin cambiar las filas anteriores. Cómo rellenarlas está en [VALIDACION-IGDS.md](VALIDACION-IGDS.md).
- **Decisiones del equipo:** los 8 puntos del apartado 5. Varias cambian los resultados, sobre todo 1, 2, 3, 4 y 5.
- **Para la visualización:**
  - mostrar el **perfil de las cuatro dimensiones**, no solo el IGDS;
  - mostrar el **embudo**: todo el programa → ámbito social → a una dimensión de g = 1 → g = 1;
  - presentar la **regresividad aparte**;
  - indicar siempre el denominador y que hubo tres rondas de codificación hasta que la validación lo cierre;
  - indicar que el documento de UPC es un manifiesto de 6 páginas, su único documento programático;
  - aplicar las reglas de la herramienta: orden alfabético, las mismas reglas para todas las formaciones y fragmento literal de cada medida.

  **Cómo se resolvió (16-11-2026).** El apartado «Prometer no es garantizar» ([DISENO.md](DISENO.md), apartado 4) presenta el embudo dentro de una rejilla de 100 casillas por programa. Las regresivas van aparte, con un aspa y sin restar del índice, y las declarativas, con un punto. Muestra siempre el denominador («48 de 681 medidas»), el sello de provisional y la nota sobre el manifiesto de UPC, y deja leer el fragmento literal de cada medida. Del perfil de las cuatro dimensiones enseña lo que más pesa en la lectura: qué pregunta falla en las medidas que se acercan. El perfil completo sigue en el informe.
