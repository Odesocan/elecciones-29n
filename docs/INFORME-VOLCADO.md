---
type: pipeline
fase: extraccionpdf
proyecto: PE_29N
tags: [PE_29N, volcado, extraccion-pdf, segmentacion, literalidad, clasificacion]
status: vigente
actualizado: 2026-11-16
aliases: ["PE_29N · Informe del volcado de programas"]
fuente: "OBSERVATORIO/Programas electorales 29N/docs/INFORME-VOLCADO.md"
---

# Volcado de programas · 29N · 13 de noviembre de 2026 (PSOE añadido el 15-11 y UPC el 16-11)

## Fuentes

| Candidatura | Documento | Estado |
|---|---|---|
| PP | [La reconstrucción nacional](https://www.pp.es/wp-content/uploads/2026/11/LA-RECONSTRUCCION-NACIONAL.pdf) · 82 págs. · presentado el 10-N | **241 medidas** volcadas (de 249: 8 son «Permanezca atento a la campaña para conocer esta nueva medida»: nº 83, 109, 132, 164, 167, 173, 200 y 210) |
| CC–1ºC | [Programa electoral 29N](https://coalicioncanaria.org/wp-content/uploads/2026/11/CCA-26-Programa_Electoral-29NOV.pdf) · 23 págs. | **100 medidas** volcadas |
| PSOE | [La fuerza de seguir avanzando](https://www.psoe.es/media-content/2026/11/PROGRAMAPSOE29N26.pdf) · 114 págs. · PDF creado el 14-11-2026; el equipo lo facilitó el 15-11 y coincide byte a byte con el de su web | **500 compromisos** volcados |
| Vox | «Programa electoral · 29 de noviembre de 2026» («Es sentido común») · 66 págs. · PDF creado el 4-11-2026 · [PDF oficial](https://www.voxespana.es/wp-content/uploads/2026/11/Programa-completo-A5-1.pdf), idéntico byte a byte al archivo que facilitó el equipo | **115 medidas** volcadas |
| UPC | «Manifiesto electoral de la Unidad del Pueblo Canario. Una sola papeleta. Todo un pueblo» · 6 págs. (portada y contraportada sin texto) · PDF creado el 30-10-2026. UPC lo facilitó directamente a ODESOCAN el 16-11 como su **único documento programático**; no hay versión pública en línea, así que se publica junto a los datos de la herramienta (`data/programa-upc-29n.pdf`) | **16 ejes** volcados |

PP y CC se descargaron de sus webs oficiales. Los de Vox y el PSOE llegaron primero como archivo; después se comprobó que coinciden byte a byte con el PDF de su web. El de UPC solo existe como archivo facilitado por el partido: se guarda en el proyecto con su huella (sha256) y `descargar` comprueba que no cambia.

**UPC es un manifiesto, no un programa por medidas.** Sus 16 ejes numerados («1. Autogobierno, soberanía popular y derecho a decidir»…) son las unidades que se vuelcan, igual que las medidas numeradas de los demás. Cada eje es más largo y general que una medida de otro programa (entre 47 y 116 palabras), así que los porcentajes por tema de UPC se calculan sobre 16 unidades y se leen con esa cautela.

Solo se vuelcan las **medidas numeradas**. Los manifiestos e introducciones en prosa quedan fuera.

## Método

Cada paso es una etapa del [script maestro](../maestro.py) y vive en su propio módulo de [pipeline/](../pipeline/).

1. **Extracción** del texto de cada PDF, página a página ([extraer.py](../pipeline/extraer.py)).
2. **Segmentación** automática por número de medida ([segmentar.py](../pipeline/segmentar.py), con el perfil de cada PDF en [perfiles.py](../pipeline/perfiles.py)). El texto es el del PDF: solo se unen líneas, se deshacen los guiones de fin de línea y se limpian restos de maquetación (ligaduras y comillas decorativas en los saltos de página).
3. **Apartado del programa** (16-11-2026, [apartados.py](../pipeline/apartados.py)). Al segmentar, cada medida guarda el capítulo y el apartado del programa en el que está. Sirve de contexto en la clasificación y en la hoja de revisión. La web no lo muestra y los textos no cambian. Los títulos salen del índice de cada programa y se buscan en el texto en el mismo orden: PP, 4 bloques y 28 apartados; PSOE, 7 capítulos y 66 apartados con medidas; Vox, 13 secciones. CC–1ºC no tiene índice, y sus 10 causas se toman de las cabeceras «1 DEFENDER…». Se encontraron todos los títulos y todas las medidas tienen apartado. En el PDF del PP el texto sale desordenado en tres páginas, así que el apartado de las medidas 158 a 161, 175, 176 y 211 a 213 se decide por su posición visual en la página (modo layout). Además, una medida no puede volver a un apartado anterior, porque la numeración sigue el orden del índice.
4. **Clasificación** en las 18 temáticas: hasta 3 temas por medida, el principal primero. La hizo un agente de IA por programa, con las mismas reglas escritas ([CRITERIOS-CLASIFICACION.md](CRITERIOS-CLASIFICACION.md)) y sin tocar los textos. **Es preliminar: debe revisarla el equipo.**
5. **Verificación** ([verificar.py](../pipeline/verificar.py)): cada título y cada texto se buscan en el PDF letra a letra. Entre dos trozos de una medida solo se tolera lo que hay en un salto de página: el número de página o la cabecera fija de ese programa. Resultado: **972 de 972 literales** (241 PP + 100 CC–1ºC + 500 PSOE + 16 UPC + 115 Vox), todas con tema y solo con los 18 temas válidos.

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

**UPC (16-11-2026).** Clasificación de los 16 ejes con las reglas escritas, tratando sus reclamaciones al Estado igual que las de CC–1ºC. Pendiente de revisión del equipo. Casos dudosos:
  - **upc-006** (servicios públicos y pensiones) trata sanidad, educación, dependencia y pensiones; con el máximo de tres temas lleva `sanidad` + `educacion` + `empleo` y queda fuera `dependencia`, aunque nombra el sistema público de cuidados;
  - **upc-016** (juventud) no tiene tema propio: `estado` (voto a los 16, justicia intergeneracional) + `vivienda` + `empleo`;
  - **upc-001** (autogobierno) lleva `mas_gasto` por reclamar «una financiación justa» y la participación en los presupuestos, como manda la regla de las reclamaciones al Estado; repite en parte el eje 2 (financiación autonómica);
  - **upc-011** (Canarias feminista) lleva `mas_gasto` por el sistema público de cuidados, que también aparece en upc-006;
  - **upc-004** (marco financiero de la UE) queda en `[]`, igual que cc-090: es defender fondos europeos, no un gasto del Estado;
  - **upc-012**, **upc-013** y **upc-007** quedan en `[]`: acogida digna, apoyo a la cultura y gestión pública de los recursos estratégicos, sin instrumento ni gasto concreto.

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
4. **El equipo la revisó el 16-11-2026 y la da por correcta.** Los casos dudosos de abajo se quedan como están. La de UPC, añadida el mismo día después de esa revisión, está **pendiente** de que la revise el equipo.

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
