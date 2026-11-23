---
type: pipeline
fase: extraccionpdf
proyecto: PE_29N
tags: [PE_29N, volcado, extraccion-pdf, segmentacion, literalidad, clasificacion]
status: vigente
actualizado: 2026-11-23
aliases: ["PE_29N · Informe del volcado de programas"]
fuente: "OBSERVATORIO/Programas electorales 29N/docs/INFORME-VOLCADO.md"
---

# Volcado de programas · 29N · 13 de noviembre de 2026 (PSOE añadido el 15-11; UPC, el 16-11, y su programa, que sustituye al manifiesto, el 23-11)

## Fuentes

| Candidatura | Documento | Estado |
|---|---|---|
| PP | [La reconstrucción nacional](https://www.pp.es/wp-content/uploads/2026/11/LA-RECONSTRUCCION-NACIONAL.pdf) · 82 págs. · presentado el 10-N | **241 medidas** volcadas (de 249: 8 son «Permanezca atento a la campaña para conocer esta nueva medida»: nº 83, 109, 132, 164, 167, 173, 200 y 210) |
| CC–1ºC | [Programa electoral 29N](https://coalicioncanaria.org/wp-content/uploads/2026/11/CCA-26-Programa_Electoral-29NOV.pdf) · 23 págs. | **100 medidas** volcadas |
| PSOE | [La fuerza de seguir avanzando](https://www.psoe.es/media-content/2026/11/PROGRAMAPSOE29N26.pdf) · 114 págs. · PDF creado el 14-11-2026; el equipo lo facilitó el 15-11 y coincide byte a byte con el de su web | **500 compromisos** volcados |
| Vox | «Programa electoral · 29 de noviembre de 2026» («Es sentido común») · 66 págs. · PDF creado el 4-11-2026 · [PDF oficial](https://www.voxespana.es/wp-content/uploads/2026/11/Programa-completo-A5-1.pdf), idéntico byte a byte al archivo que facilitó el equipo | **115 medidas** volcadas |
| UPC | «Líneas básicas del programa electoral de la Unidad del Pueblo Canario (UPC). Una sola papeleta para defender a todo un pueblo» · 19 págs. (portada en imagen) · 5 bloques y 16 ejes · PDF creado con Word el 16-11-2026. Sustituye desde el 23-11-2026 al manifiesto «Una sola papeleta. Todo un pueblo» (6 págs.), que UPC había facilitado el 16-11 como su único documento programático. El equipo de ODESOCAN lo incorporó como archivo; no hay una dirección oficial de descarga, así que se publica junto a los datos de la herramienta (`data/programa-upc-29n.pdf`) | **143 fragmentos** volcados (párrafos y viñetas de sus 16 ejes) |

PP y CC se descargaron de sus webs oficiales. Los de Vox y el PSOE llegaron primero como archivo; después se comprobó que coinciden byte a byte con el PDF de su web. El de UPC solo existe como archivo: se guarda en el proyecto con su huella (sha256) y `descargar` comprueba que no cambia. El manifiesto del 16-11 queda en el historial de git (commit af384bf y anteriores), con sus segmentos y su clasificación.

**UPC numera sus ejes, no sus medidas: la unidad es el fragmento.** El programa tiene 5 bloques y 16 ejes numerados («1. La vivienda es un derecho y no un negocio.»). Dentro de cada eje hay párrafos y viñetas sin numerar, y a veces subapartados sin número («Pesca artesanal y gestión sostenible del medio marino»). Cada párrafo o viñeta es un **fragmento**: es la unidad que se vuelca y se clasifica, como las medidas numeradas de los demás. Cada fragmento guarda su ruta bloque › eje › subapartado, y en la web se cita como «Eje N» con su página. Hasta el 23-11 la unidad era el eje entero (16 unidades del manifiesto), así que los porcentajes de UPC de antes y de después no se comparan sin más: ver «UPC: del manifiesto al programa», más abajo.

Solo se vuelcan las **medidas numeradas** (en UPC, los fragmentos de sus ejes). Los manifiestos e introducciones en prosa quedan fuera; en UPC, la presentación anterior al bloque 1 y el lema final.

## Método

Cada paso es una etapa del [script maestro](../maestro.py) y vive en su propio módulo de [pipeline/](../pipeline/).

1. **Extracción** del texto de cada PDF, página a página ([extraer.py](../pipeline/extraer.py)).
2. **Segmentación** automática por número de medida; en UPC, por párrafo o viñeta de cada eje ([segmentar.py](../pipeline/segmentar.py), con el perfil de cada PDF en [perfiles.py](../pipeline/perfiles.py)). El texto es el del PDF: solo se unen líneas, se deshacen los guiones de fin de línea y se limpian restos de maquetación (ligaduras y comillas decorativas en los saltos de página).
3. **Apartado del programa** (16-11-2026, [apartados.py](../pipeline/apartados.py)). Al segmentar, cada medida guarda el capítulo y el apartado del programa en el que está. Sirve de contexto en la clasificación y en la hoja de revisión. La web no lo muestra y los textos no cambian. Los títulos salen del índice de cada programa y se buscan en el texto en el mismo orden: PP, 4 bloques y 28 apartados; PSOE, 7 capítulos y 66 apartados con medidas; Vox, 13 secciones. CC–1ºC no tiene índice, y sus 10 causas se toman de las cabeceras «1 DEFENDER…». Se encontraron todos los títulos y todas las medidas tienen apartado. En el PDF del PP el texto sale desordenado en tres páginas, así que el apartado de las medidas 158 a 161, 175, 176 y 211 a 213 se decide por su posición visual en la página (modo layout). Además, una medida no puede volver a un apartado anterior, porque la numeración sigue el orden del índice.
4. **Clasificación** en las 18 temáticas: hasta 3 temas por medida, el principal primero. La hizo un agente de IA por programa (en UPC, cuatro por bloques y tres auditoras por temas; ver abajo), con las mismas reglas escritas ([CRITERIOS-CLASIFICACION.md](CRITERIOS-CLASIFICACION.md)) y sin tocar los textos. **Es preliminar: debe revisarla el equipo.**
5. **Verificación** ([verificar.py](../pipeline/verificar.py)): cada título y cada texto se buscan en el PDF letra a letra. Entre dos trozos de una medida solo se tolera lo que hay en un salto de página: el número de página o la cabecera fija de ese programa. Resultado: **1099 de 1099 literales** (241 PP + 100 CC–1ºC + 500 PSOE + 143 UPC + 115 Vox), todas con tema y solo con los 18 temas válidos.

## Incidencias del propio PDF

- **CC, medida 11** («Acercar los servicios a las personas»): el texto está cortado en el PDF original. Se muestra con un aviso y un enlace a la página.
- **PP, medida 85**: el final aparecía en otro punto del PDF. Se ha recolocado y verificado por piezas.
- **PP, medidas 106 y 110**: llevaban pegados subtítulos del documento. Se han retirado.
- **Vox**: 21 medidas son una sola frase. Si es corta va como titular; si es larga (14 medidas, hasta 506 caracteres), como texto. Las viñetas «•» se conservan, cada una en su línea. Hay erratas del original que se respetan, por ejemplo «…clases extraescolares. y la gratuidad real…» en la 94 o un espacio antes de coma en la 46.

- **PSOE** (perfil propio en `pipeline/perfiles.py`):
  - **Estructura.** Cada apartado empieza con prosa y sigue con un bloque «Compromisos» numerado del 1 al 500 de forma correlativa. Los títulos de apartado no van en mayúsculas, así que la medida se cierra cuando empieza un título del índice. Cuatro subapartados sin número pegados a una medida se han retirado (tras la 71, 72, 75 y 78).
  - **Texto.** pypdf partía palabras en dos («competitivid ad»). Se unen solo cuando la palabra entera aparece en la otra extracción del mismo PDF, y se quitan los espacios antes de la puntuación. Las viñetas de Word («o Acelerar…») se muestran como «•». Nada de esto cambia ni una letra: la verificación literal es la misma.
  - **Numeración.** «419.» lleva el titular en la línea siguiente. En los saltos de página quedan restos de numeración de listas («134 136 137»), que se toleran al verificar.
  - **Medidas que introducen las siguientes:** la 54 («Destinar una financiación sin precedentes a vivienda:») y la 176 (becas) solo abren las que vienen detrás. Se muestran con la nota «Introduce las medidas siguientes».
  - **Medida 395:** está cortada en el propio PDF («…el correcto desempeño de sus funcione»).
  - **Sin punto final:** muchas medidas acaban sin punto en el original y no se marcan como cortadas.
  - **Medidas 70 y 72:** son la misma propuesta, el impuesto a las viviendas de grandes tenedores que no se destinan al alquiler asequible. El PDF las numera dos veces y se cuentan las dos, como hace el programa.

- **UPC, programa del 23-11-2026** (perfil propio en `pipeline/perfiles.py`, `unidad='parrafo'`):
  - **Estructura.** Solo numera los 16 ejes. Un fragmento termina en la línea en blanco que separa párrafos (si su texto acaba en puntuación final; si no, sigue en la página siguiente), en una viñeta «-» o «•», en un eje, en un bloque o en un subapartado. Tres párrafos no van separados por una línea en blanco en el PDF y se cortan por su comienzo (`cortes_parrafo`): «Incremento de la deducción por gastos de vivienda…», «Reorientar el modelo turístico…» y «Unidad del Pueblo Canario exige al Estado…».
  - **Regla de unidad.** Un párrafo del PDF es un fragmento, aunque junte dos propuestas (upc-036 jornada y Convenio 189; upc-061 POSEI y pesca; upc-080 deflactación y resumen fiscal; upc-138 observatorio de bulos y democracia participativa) o continúe la frase del anterior (upc-098, upc-136, upc-137, upc-142). Así la regla es la misma en todo el documento. Las agentes de clasificación lo señalaron y no se ha partido nada a mano.
  - **Conector sin contenido.** «Defendiendo entre otras actuaciones:» (eje 3) solo abre una lista y no es un fragmento.
  - **Fragmentos que abren una lista:** upc-001, 003, 045, 050, 060 y 127 acaban en «:» y se muestran con la nota «Introduce las medidas siguientes», como en el PSOE.
  - **Titulares.** Las viñetas «• Mejora de los salarios: incremento…» (ejes 3 y 14, 13 fragmentos) llevan como titular lo que va antes de los dos puntos. Por eso el texto empieza en minúscula, como en el original.
  - **Texto.** Se extrae en modo layout, porque en plain pypdf parte más palabras («posi bilidades», «1 .800», «3 4 horas»), y se repara con el vocabulario de la otra extracción. Word no parte palabras con guion: «afectivo-sexual» y «Pueblo Palestino - denunciando» se respetan. Erratas del original que se mantienen: «cambio climático . que incluya» (upc-026), «soluciones menos invasiva» (upc-092), «gestión activa de espacios protegidos y medidas.» (upc-104).

## Casos dudosos que conviene revisar

**PP**
- 47 (seguridad de infraestructuras y servicios esenciales): economía + justicia (emergencias), por la regla de seguridad de infraestructuras.
- 98 (acceso a prestaciones según el arraigo): está como empleo + migraciones, aunque el texto no menciona a inmigrantes.
- 99 (despoblación): medio ambiente solo por el criterio de «territorio rural».
- 128 (protección de los símbolos del Estado): está en memoria, pero son símbolos actuales.
- 143 (nacionalidad de descendientes de exiliados): migraciones + memoria.
- 159 (ayuda a la maternidad, fertilidad): infancia + sanidad + igualdad, desde que existe el tema (16-11).
- 158 y 166 (deducción familiar, pobreza infantil): infancia primero, desde el 16-11; antes iban en empleo como protección social.
- 188 (retorno de investigadores): economía + educación + migraciones.
- 229 (impuestos de la factura eléctrica, bono social): medio ambiente (energía) + economía + empleo.

**CC–1ºC**
- 1 (traspasos del Estatuto, incluidos los permisos de trabajo): estado + migraciones.
- 15 (pobreza infantil): tres temas, y quedan fuera otros que también toca.
- 26 (Ley Canaria de Residencia): vivienda + migraciones + estado.
- 48, 49 y 93 (investigación e innovación): idi primero, desde el 16-11; antes iban en economía o educación.
- 67 (Centro Nacional de Vulcanología) y 73 (emergencias, UME): justicia (protección civil) + medio ambiente; la 73, también defensa.

**Vox**
- 18, 19, 22, 27, 32 y 74 («prioridad nacional»): el sector va primero y después migraciones. Si abarca muchas prestaciones, migraciones va primero.
- 71 (prohibición del burka y el niqab): justicia + educación. No se añade migraciones ni igualdad porque el texto no lo dice.
- 73 (fin del programa de Lengua Árabe y Cultura Marroquí): educación + migraciones. 72 (menús halal): solo educación.
- 98 (derecho a la vida, objeción de conciencia, cuidados paliativos): sanidad + dependencia.
- 64 (salud de la mujer) y 78 (deporte femenino «con criterios biológicos»): llevan igualdad. Es discutible.
- 105 (símbolos nacionales, con penas más duras): estado + justicia + cultura, no memoria.
- 111 (libertad de expresión frente a la «censura»): va en estado (libertades públicas).
- 77 (tauromaquia): solo cultura, sin animales.

**PSOE**
- 202 a 204 (Ley y sistema de servicios sociales): no hay tema propio; van en empleo (protección social) más dependencia o estado.
- 195 y 201 (acogimiento familiar, jóvenes extutelados): solo infancia desde el 16-11; el empleo estaba como sustituto.
- 193 (Cuenta de Futuro de 1.000 € al nacer): infancia + empleo + economía desde el 16-11.
- 370 (unión de amistad): infancia (formas de convivencia) + dependencia + igualdad, desde el 16-11.
- 352 (penas y medidas cautelares digitales): lleva igualdad por el bloque en el que está, aunque el texto no nombra a las mujeres.
- Consumo (034–036, 094–097): no tiene tema propio; va en economía, más digital si es en línea.

**Revisión cruzada de la clasificación del PSOE (16-11-2026).** El PSOE se clasificó el 15-11, después que los otros tres, y no tuvo la revisión cruzada que tuvieron ellos. Para hacerla:
- se leyeron completas sus 500 medidas, agrupadas por apartado del programa, con sus temas y sus etiquetas fiscales;
- se revisaron los 29 casos del PSOE en [contraste-fiscal.md](../datos/informes/contraste-fiscal.md);
- se compararon medidas equivalentes de los cuatro programas: atención presencial y ventanilla única, SMI, IMV, Tribunal Constitucional y CGPJ, ocupación, protección civil y UME, red consular, acoso escolar, mecenazgo, cooperación, pesca, ferrocarril, IVA y otras.

La clasificación se sostiene casi entera. Cambian cinco medidas:
  - **psoe-280** (sistema integrado de transporte público): `economia` → `economia` + `medioambiente`, igual que psoe-028, que es la misma medida;
  - **psoe-338** (ayudas a los huérfanos y huérfanas de la violencia de género): se añade `infancia`, porque se dirige expresamente a los hijos e hijas;
  - **psoe-417** (plan contra el acoso escolar y en el deporte): se añade `infancia`;
  - **pp-214** (protocolo nacional contra el acoso escolar): se añade `infancia`, por coherencia con psoe-417. Es la única corrección fuera del PSOE;
  - **psoe-127** («Ingresos nuevos para derechos nuevos»): pasa de `mas_gasto` + `mas_ingresos` a solo `mas_ingresos`. La medida dice cómo se paga la prestación por crianza, que ya cuenta como gasto en psoe-192. Es el mismo criterio que vox-043, que dice cómo se paga la bajada de impuestos y solo lleva `menos_gasto`. El PSOE pasa de 243 a 242 medidas que restan y su ratio, de 1 : 15,2 a 1 : 15,1.

Se añadieron dos reglas: el acoso escolar lleva `infancia`, y una medida que solo dice cómo se paga otra lleva solo su propio lado. Además se precisó cuándo la seguridad de las infraestructuras lleva `justicia`.

Casos dudosos que quedaban para el equipo (los fiscales se revisaron el 16-11-2026 y se mantienen como están):
  - psoe-127 y psoe-192 citan el mismo ingreso, la tributación de los grandes patrimonios, y los dos cuentan como medidas que suman. 192 lo lleva porque trae su propia contrapartida, como manda la regla;
  - psoe-250 (Fondo de Reparación financiado por los productores) está en `[]`. Si el fondo es público, serían `mas_gasto` + `mas_ingresos`, como la autoridad financiada con una tasa de psoe-097;
  - psoe-022 (pacto de seguridad ferroviaria con una comisión técnica nueva) y psoe-437 (modernizar la justicia con digitalización e IA) están en `[]`, aunque podrían suponer algo de gasto;
  - psoe-162 y psoe-224 son el mismo Plan de Educación Inclusiva, y psoe-325 y psoe-326 la misma medida de conciliación. Se cuentan dos veces porque el programa las repite.

**UPC (23-11-2026): programa por fragmentos.** La clasificación del manifiesto (16 ejes, 16-11) se sustituyó entera. Los 143 fragmentos se clasificaron en dos pasadas, con las reglas escritas y calibrando con las medidas equivalentes de los otros cuatro programas:
  1. **Por bloques del programa:** cuatro agentes de IA, cada una con un tramo coherente (bloque 1; bloque 2, ejes 5 a 8; bloque 2, ejes 9 y 10; bloques 3 a 5).
  2. **Por temáticas:** tres agentes auditoras, cada una responsable de seis temas, recorrieron los 143 fragmentos buscando falsos positivos, falsos negativos y el orden del tema principal. Propusieron cinco cambios y se aplicaron todos: upc-064 y upc-065 pierden `empleo` (los salarios son una coletilla, como en pp-194 y cc-035); upc-033 pasa a `igualdad` + `empleo` (regla de la conciliación); upc-050 pierde `estado` (el REF solo lleva `estado` si trata de competencias o del Estatuto); upc-135 pasa a `justicia` + `estado` (transparencia y corrupción a la vez). No hay ningún fragmento sin tema.

  Pendiente de revisión del equipo. Casos dudosos:
  - **upc-017** (limitar la compra de vivienda a extranjeros no residentes): `vivienda` + `migraciones`, como cc-026, que es casi idéntica. Es discutible porque comprar sin residir no es migrar; vox-035 va en `vivienda` + `economia`.
  - **upc-008** (incentivos fiscales para sacar viviendas vacías al alquiler): `vivienda` + `economia`, por la regla de vivienda con herramientas fiscales (psoe-066, vox-030). cc-024, casi igual, va solo en `vivienda`: conviene revisar cc-024.
  - **upc-020** (servicios públicos y sociales): `sanidad` + `educacion` + `empleo`. `empleo` representa los servicios sociales, como en psoe-202 a 204, porque el esquema no tiene un tema de servicios sociales.
  - **upc-023** (derecho subjetivo a la atención temprana): `infancia` + `dependencia`. El orden inverso también es defendible (pp-112 la pone en `dependencia`; psoe-196, en `infancia`).
  - **upc-056** (programa contra la pobreza del REF): `empleo` como protección social, como cc-016. No hay tema para la pobreza general.
  - **upc-059** (inversión territorializada): `economia` + `estado`, como cc-007. Quitar `estado` sería defendible por la regla del REF.
  - **upc-063** (fondos europeos para la acogida de menores no acompañados): `migraciones` + `infancia` + `estado`. La alternativa sería `defensa` (UE) como tercer tema.
  - **upc-065 y upc-090** (moratoria turística): solo upc-090 lleva `medioambiente`, porque es el que explicita los efectos sobre el territorio y los recursos naturales.
  - **upc-069** (investigación pesquera aplicada con las universidades): lleva `idi` en tercer lugar.
  - **upc-072 y upc-073** (suelo agrario y rústico): `economia` + `medioambiente`; cc-041, más general, va solo en `economia`.
  - **upc-136 y upc-137** (participación y transfuguismo): `estado` + `justicia`, frente a upc-135, que lleva `justicia` primero porque pide prevenir y castigar la corrupción.
  - **upc-041** (juventud): `vivienda` + `empleo` + `educacion`; la salud mental queda fuera por el máximo de tres temas.

**Huecos del esquema**: ya no queda ninguno.

**Temas nuevos de «Infancia y entornos convivenciales (familias)» e «I+D+i (innovación)» (16-11-2026).** El equipo hizo una revisión parcial y concluyó que la clasificación funciona bien, salvo por la falta de estos dos temas. El esquema pasó a tener 18 temas, y «Medio ambiente y energía» se llama ahora «Medio ambiente, aguas y energía». Se revisaron, leyéndolas completas, 250 medidas candidatas, buscadas por palabras clave y por el apartado del programa. 47 llevan ahora `infancia` (CC–1ºC 3, PP 11, PSOE 29, Vox 4) y 24 `idi` (CC–1ºC 5, PP 4, PSOE 13, Vox 2). Las reglas están en [CRITERIOS-CLASIFICACION.md](CRITERIOS-CLASIFICACION.md). Los casos más discutibles para la revisión son:
  - los menores infractores (PP 25 y 26; Vox 80), que llevan `justicia` + `infancia`;
  - los permisos por nacimiento y la reducción de jornada por hijos (PP 160; PSOE 105, 325 y 326), que llevan `infancia` en tercer lugar, frente a la conciliación general (PP 162), que no la lleva;
  - la unión de amistad (PSOE 370) como «entorno convivencial»;
  - el Centro Nacional de Vulcanología (CC–1ºC 67) y el asesoramiento científico a las administraciones (PSOE 13), que van primero en `idi`;
  - la investigación sanitaria dentro de una medida más amplia (Vox 65), que lleva `idi` en segundo lugar.

**División de «Administraciones públicas» (15-11-2026).** El tema se dividió en «Estructura del Estado» (`estado`) y «Justicia y seguridad» (`justicia`), y el esquema pasó a tener 16 temas. Se reclasificaron a mano las 236 medidas que lo llevaban, sin tocar sus otros temas: 143 llevan ahora `estado` y 102 `justicia` (9 llevan los dos). En el primer reparto (15-11) se leyó el titular y el principio del texto. El 16-11 se releyeron completas las 172 medidas con un texto más largo, y no cambió ningún reparto.

Al leerlas enteras aparecieron dos medidas que quizá deberían llevar un tema más. No se tocaron, porque la revisión solo cubría el reparto entre `estado` y `justicia`:
  - PSOE 433 (ley de justicia gratuita): incluye formación en violencia de género; ¿añadir `igualdad`?
  - PP 19 (crimen organizado): incluye un plan de empleo, formación y vivienda a diez años para los jóvenes; ¿añadir `empleo`?

Las reglas de reparto están en [CRITERIOS-CLASIFICACION.md](CRITERIOS-CLASIFICACION.md). Los casos más discutibles para la revisión son:
  - el Tribunal de Cuentas y la trazabilidad del gasto (PP 80 y 84; PSOE 448), en `estado` como control y transparencia y no como corrupción;
  - el Centro Nacional de Vulcanología (CC–1ºC 67), en `justicia` como prevención de riesgos (protección civil). Desde el 16-11 va primero en `idi`, como centro de investigación;
  - la crisis de Ceuta (PP 13), en `justicia` por los medios policiales;
  - la gestión de Adif y Renfe (PSOE 25), en `estado`, frente al pacto de seguridad ferroviaria (PSOE 22), en `justicia`;
  - las multas de tráfico (Vox 45), en `estado` como potestad sancionadora de la Administración.

## UPC: del manifiesto al programa (23-11-2026)

**Pregunta:** ¿el programa nuevo amplía el alcance temático de UPC respecto a su manifiesto? Se comparan la clasificación del manifiesto (16 ejes, 16-11-2026, recuperada de git) y la del programa (143 fragmentos, 23-11-2026), con las mismas 18 temáticas. El cálculo es reproducible y lee los dos estados del repositorio.

**Cautela de método.** La unidad cambió: antes, un eje entero con hasta 3 temas; ahora, un párrafo. El % de unidades (la métrica de la web) depende del tamaño de la unidad: un eje largo marcaba hasta 3 temas a la vez y la tapa de 3 dejaba fuera temas que el eje sí nombraba. Por eso se añade el **% de las palabras** del programa que están en unidades de cada tema, que no depende del tamaño de la unidad, y las **palabras** dedicadas a cada tema. Se cuentan textos, no compromisos ni euros.

- **Extensión:** de 16 ejes y 1.149 palabras a 143 fragmentos y 5.410 palabras (× 4.7).
- **Cobertura:** de 13 a 17 de los 18 temas. Entran `dependencia` (8 fragmentos), `idi` (3), `digital` (2) y `animales` (1). Solo `memoria` sigue sin nada.

| Tema | Manifiesto: % de los 16 ejes | Programa: % de los 143 fragmentos | % de las palabras (antes → ahora) | Palabras (antes → ahora) | Puesto entre los 5 (antes → ahora) |
|---|---|---|---|---|---|
| Economía | 37,5 % (6) | 33,6 % (48) | 37,0 → 36,1 | 425 → 1.951 | 1.º → 3.º |
| Vivienda | 18,8 % (3) | 18,2 % (26) | 18,8 → 19,2 | 216 → 1.041 | 1.º → 1.º |
| Medio ambiente, aguas y energía | 6,2 % (1) | 16,8 % (24) | 6,3 → 14,6 | 72 → 791 | 5.º → 2.º |
| Estructura del Estado | 37,5 % (6) | 15,4 % (22) | 33,2 → 15,3 | 382 → 827 | 1.º → 3.º |
| Empleo | 25,0 % (4) | 12,6 % (18) | 29,0 → 13,1 | 333 → 708 | 1.º → 3.º |
| Igualdad | 12,5 % (2) | 11,2 % (16) | 12,4 → 9,1 | 142 → 492 | 2.º → 2.º |
| Educación | 6,2 % (1) | 6,3 % (9) | 6,4 → 6,1 | 74 → 330 | 4.º → 4.º |
| Migraciones | 6,2 % (1) | 6,3 % (9) | 6,3 → 5,0 | 72 → 268 | 4.º → 4.º |
| Defensa y política internacional | 18,8 % (3) | 6,3 % (9) | 21,0 → 5,7 | 241 → 311 | 1.º → 5.º |
| Dependencia y discapacidad | 0,0 % (0) | 5,6 % (8) | 0,0 → 8,2 | 0 → 443 | 5.º → 2.º |
| Justicia y seguridad | 6,2 % (1) | 4,9 % (7) | 5,0 → 3,7 | 57 → 199 | 4.º → 4.º |
| Sanidad | 6,2 % (1) | 3,5 % (5) | 6,4 → 3,4 | 74 → 182 | 3.º → 5.º |
| Infancia y entornos convivenciales (familias) | 6,2 % (1) | 2,8 % (4) | 6,3 → 4,0 | 72 → 219 | 1.º → 5.º |
| Cultura y deporte | 6,2 % (1) | 2,8 % (4) | 4,1 → 2,1 | 47 → 113 | 1.º → 5.º |
| I+D+i (innovación) | 0,0 % (0) | 2,1 % (3) | 0,0 → 2,1 | 0 → 111 | 5.º → 3.º |
| Derechos digitales y tecnología | 0,0 % (0) | 1,4 % (2) | 0,0 → 1,3 | 0 → 68 | 5.º → 5.º |
| Bienestar animal | 0,0 % (0) | 0,7 % (1) | 0,0 → 0,7 | 0 → 36 | 4.º → 3.º |
| Memoria democrática | 0,0 % (0) | 0,0 % (0) | 0,0 → 0,0 | 0 → 0 | 4.º → 4.º |

**Lectura:**
- **Crece en todos los temas en palabras**, salvo memoria democrática. El salto no es solo de extensión: el programa baja a instrumentos (control de precios y renovación automática de los contratos de alquiler, parque público del 9 %, SMI de 1.800 €, jornada de 37,5 y 34 horas, partidas concretas del REF, IRPF por tramos, refugios climáticos, Ley de Biodiversidad…).
- **Más peso relativo en derechos sociales y territorio:**
  - **Medio ambiente, aguas y energía** pasa de 1 eje (6 %) a 24 fragmentos (17 %; del 6 % al 15 % de las palabras), y del último al segundo puesto entre los cinco, por detrás de CC–1ºC.
  - **Dependencia** pasa de una línea sin tema propio (la tapa de 3 temas la dejaba fuera) a 8 fragmentos con medidas propias: cuidados de larga duración, atención temprana como derecho subjetivo, soledad no deseada, respiro familiar y Convenio 189 de la OIT. Es el 2.º que más peso le da, tras el PSOE.
  - **Vivienda** sigue siendo su seña: el 18 % del programa, primer puesto entre los cinco, con casi cinco veces más texto (de 216 a 1.041 palabras).
- **Menos peso relativo en lo institucional e internacional:** Estructura del Estado (del 33 % al 15 % de las palabras), empleo (del 29 % al 13 %) y defensa y política internacional (del 21 % al 6 %) crecen en palabras, pero mucho menos que el resto. En el manifiesto, autogobierno, financiación y UE ocupaban buena parte del texto.
- **Sigue débil en sanidad:** 5 fragmentos y el 3,5 % del programa, el último de los cinco, aunque con más del doble de texto que antes. Infancia y cultura también quedan al final de los cinco en peso relativo.

## La prueba de las cuentas (impacto fiscal) · 14-11-2026 · descartada el 16-11-2026

> **Descartada el 16-11-2026.** El equipo decidió no publicarla por tres motivos:
>
> 1. es difícil de interpretar;
> 2. una de sus lecturas principales puntúa en positivo la austeridad económica, al margen de la garantía de derechos;
> 3. otra lectura anima a la abstención, porque todos los programas llevaban la alerta de riesgo de viabilidad.
>
> Se conserva aquí como registro de lo que se hizo. Se han quitado de la tabla el ratio y la etiqueta de riesgo, que eran el veredicto.

**Pregunta:** ¿dice cada programa cómo pagar lo que promete? Cada medida se etiquetó según el efecto presupuestario que declara: baja ingresos, sube el gasto, sube ingresos, recorta gasto, promete reducir el déficit o la deuda, o pone importe en euros. Las reglas están en [CRITERIOS-IMPACTO-FISCAL.md](CRITERIOS-IMPACTO-FISCAL.md).

**Método:**
1. Clasificó un agente de IA por programa, con las mismas instrucciones escritas.
2. `clasificar contrastar` cruzó las etiquetas con señales del texto y generó [contraste-fiscal.md](../datos/informes/contraste-fiscal.md).
3. Se revisaron a mano todas las medidas que «suman», porque son pocas, y los casos cruzados entre partidos.
4. **El equipo la revisó el 16-11-2026 y la da por correcta.** Los casos dudosos de abajo se quedan como están. La de UPC se hizo sobre su manifiesto, el mismo día y después de esa revisión. Se retiró el 23-11-2026, cuando el programa sustituyó al manifiesto: las cifras de UPC de abajo son del manifiesto y quedan como registro.

| | CC–1ºC | PP | PSOE | UPC | Vox |
|---|---|---|---|---|---|
| Medidas que **restan** dinero a las cuentas públicas | 69 (69 %) | 109 (45 %) | 242 (48 %) | 8 (50 %) | 58 (50 %) |
| · bajan impuestos o cotizaciones | 5 | 32 | 10 | 1 | 14 |
| · suben el gasto | 68 | 86 | 234 | 7 | 55 |
| Medidas que lo **suman** | 0 | 6 (2 %) | 16 (3 %) | 2 (13 %) | 15 (13 %) |
| · suben ingresos | 0 | 2 | 15 | 2 | 2 |
| · recortan gasto | 0 | 5 | 1 | 0 | 13 |
| Dicen en euros cuánto dinero suponen | 0 de 69 | 2 de 109 (pp-117, pp-126) | 9 de 242 | 0 de 8 | 0 de 58 |
| Prometen reducir déficit o deuda | 0 | 2 (pp-004, pp-107) | 3 (psoe-125, 126, 129) | 0 | 1 (vox-003) |
| Memoria económica | no | no | no | no | no |

Notas sobre la tabla:

- Una medida puede tener efecto en los dos lados o en dos categorías. Por eso las subcategorías pueden sumar más que el total de medidas únicas.
- La memoria económica se comprobó buscando en el texto completo de cada PDF «memoria económica», tablas de coste y cifras en euros.
- Solo dos medidas del PP cuantifican dinero público: las de infraestructuras (300.000 M€ en 15 años, junto al sector privado) y agua (40.000 M€ hasta 2030).

**Contrapartidas que declaran los propios programas:**

- **Vox** dice expresamente que se recortarán todos los gastos superfluos de la Administración «para compensar la bajada masiva de impuestos». Concreta la supresión de subvenciones a partidos, sindicatos, patronales y ONG (vox-043).
- **El PP** liga la lucha contra el fraude a bajar impuestos (pp-183).
- **CC–1ºC** no incluye ninguna contrapartida. Buena parte de su gasto son reclamaciones de financiación al Estado para Canarias.
- **UPC** suma con dos medidas de ingresos: una tasa turística para no residentes (upc-008) y una reforma fiscal progresiva para grandes empresas, patrimonios, rentas del capital, banca y energéticas (upc-009), que también mejora deducciones por alquiler.
- **El PSOE** suma sobre todo con impuestos: a solares ociosos, a viviendas de grandes tenedores (70 y 72), a pernoctaciones turísticas, a rentas del capital, a grandes tecnológicas, a megayates y jets privados, un recargo en Sociedades ligado a la brecha salarial y la tasa Tobin. Liga dos de ellos a pagar la prestación por crianza (127 y 192). Su único recorte es retirar la financiación pública a prácticas que amparen el maltrato animal (295).

**Correcciones de coherencia hechas al revisar:**

- **vox-020** («dotándolo de los medios necesarios»): se añade `mas_gasto`. Así se trata igual que vox-083 y que las reclamaciones de «recursos suficientes» de CC.
- **vox-014** (deportación de delincuentes): pasa a `[]`, igual que pp-044. Las dos fijan a quién se expulsa sin mencionar medios nuevos. Las medidas que sí refuerzan medios para ejecutar retornos (pp-045, vox-012) mantienen `mas_gasto`.

**Casos dudosos** (revisados por el equipo el 16-11-2026: se mantienen como están):

- **CC–1ºC**
  - cc-001 y cc-052: traspasos «con medios suficientes», dejados en `[]`.
  - cc-005: impedir que el REF compute como financiación ordinaria, en `[]`.
  - cc-076: nuevas conexiones entre islas verdes, con `mas_gasto`.
  - cc-085: cooperación al desarrollo, con `mas_gasto`.
  - cc-097: uso de remanentes, con `mas_gasto`.
- **PP**
  - pp-001: auditoría con supresión de gastos «según lo que concluya», en `[]`.
  - pp-012: sustituir subvenciones por créditos fiscales, en `[]`.
  - pp-075: menos puestos de confianza en el CIS, con `menos_gasto`.
  - pp-175: atajar el absentismo, con `menos_gasto`.
  - pp-185: libertad autonómica para bajar impuestos, en `[]`.
  - pp-230 y pp-231: redes eléctricas pagadas con peajes, en `[]`.
- **PSOE** (clasificación del 15-11, con revisión cruzada el 16-11)
  - psoe-103: el coste de mejorar los coeficientes reductores «se podría compensar» con aportaciones de empresas con beneficios que hagan ERE. Lleva `mas_ingresos` aunque sea condicional.
  - psoe-116: obligar a cotizar al RETA en lugar de a las mutualidades, como `mas_ingresos`.
  - psoe-457: impuesto mínimo global a las grandes fortunas, en `[]` por ser una propuesta internacional, como la defensa de presupuestos de la UE.
  - psoe-231 (el Estado asume 83.000 M€ de deuda autonómica) y psoe-099 (el Estado paga las prestaciones no contributivas): `mas_gasto` por la regla de «cambiar quién paga».
  - psoe-023 frente a psoe-128: los mismos 19.000 M€ del ferrocarril, `mas_gasto` + `importe` donde se amplían y `[]` donde se «mantienen».
  - psoe-093 (bono social único): `mas_gasto`, aunque una parte la pagan las eléctricas.
- **Vox**
  - vox-032: restringir los derechos del padrón, con `menos_gasto`. Es la más débil de las que suman.
  - vox-035: fiscalidad diferenciada, con tres etiquetas.
  - vox-012 y vox-015: repatriaciones, con `mas_gasto`.
  - vox-077 frente a vox-098: «potenciar» la tauromaquia, en `[]`, frente a «potenciar» los paliativos, con `mas_gasto`.
  - vox-110: «acabar con el despilfarro» de RTVE, en `[]`.

**Límites, que se dicen en la propia herramienta:**

- Se cuentan medidas, no euros.
- No se acepta la autofinanciación («se pagará sola») como contrapartida.
- La etiqueta de riesgo es una regla mecánica, la misma para todos: «restan» es más del doble de «suman». Con los datos actuales la llevan los cuatro programas publicados.

## Cómo revisar y corregir

- [revision-clasificacion.csv](../datos/revision/revision-clasificacion.csv) tiene una fila por medida, con columnas para marcar `revisado_ok` y escribir la `correccion` (temas separados por «;», el principal primero). Se abre en Excel o en cualquier hoja de cálculo; el separador es «;».
- Para aplicar las correcciones a `datos/clasificacion/*.json`:

  ```bash
  python3 maestro.py clasificar revision
  ```

  Después se regeneran el CSV y el bloque de Divi:

  ```bash
  python3 maestro.py
  ```

  Las columnas manuales de la hoja se conservan.
