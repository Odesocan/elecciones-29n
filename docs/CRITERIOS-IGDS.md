---
type: metodologia
fase: investigacion
proyecto: PE_29N
tags: [PE_29N, igds, libro-de-codigos, derechos-sociales, criterios]
status: vigente
actualizado: 2026-11-16
aliases: ["PE_29N · Libro de códigos del IGDS"]
fuente: "OBSERVATORIO/Programas electorales 29N/docs/CRITERIOS-IGDS.md"
---

# Libro de códigos del IGDS (prueba)

Índice de Garantía de Derechos Sociales de ODESOCAN aplicado a los programas
de las Elecciones Generales del 29N 2026. **Primera codificación, pendiente de
validación humana.** Su apartado en la herramienta («Prometer no es garantizar») está construido, pero retirado de la web desde el 16-11-2026.

El IGDS mide cuántas medidas de cada 100 del programa son garantías objetivas
de derechos sociales: acceso que no exige demostrar renta, merecimiento,
nacionalidad o capacidad de pago.

La parte 1 es el libro de códigos tal como lo fijó el equipo. La parte 2 son
las reglas operativas que se añaden para aplicarlo **igual a todas las
formaciones**: no cambian el libro, concretan los casos frontera. La parte 3
explica cómo se registra la codificación.

---

## 1. Libro de códigos

### Dimensiones (0/1 cada una, siempre en relación con el acceso a un derecho social)

- **UNI · Incondicionalidad/universalidad.** 1 si la titularidad corresponde a toda la población o a todo el colectivo definido por la situación protegida, sin prueba de renta ni de merecimiento. Las acciones positivas que se suman al acceso universal son compatibles. 0 si hay umbral de renta, prueba de necesidad, convocatoria competitiva, requisito de merecimiento o cotización previa.
- **EXI · Exigibilidad.** 1 si hay un instrumento con fuerza obligatoria (ley que reconoce el derecho, cartera garantizada, plazo máximo, ratio, estándar mínimo, obligación de provisión). 0 si se formula con «fomentar», «impulsar», «estudiar» o «promover», o mediante planes, campañas o convocatorias. Las declarativas valen siempre 0.
- **DES · Desmercantilización.** 1 si la medida da acceso público sin ningún tipo de copago: un servicio público que hoy es gratuito o una prestación monetaria pública. 0 si regula precios, condiciones o conductas sin proveer nada (un límite al precio no es una garantía pública), si para acceder hay que pagar una renta, una tasa o un copago, o si hay bonos, cheques, deducciones, subvenciones a la demanda o incentivos a la oferta privada. *Criterio fijado por el equipo el 16-11-2026; antes contaban también la provisión con precio regulado y la regulación del mercado.*
- **NDI · No discriminación.** 1 si el acceso no excluye por origen, situación administrativa, sexo, género u orientación (de forma explícita o por formularse para toda la población sin cláusulas de exclusión), o si la medida corrige una discriminación. 0 si contiene una exclusión o no se refiere al acceso a un derecho.

Si una medida no regula ni provee el acceso a ningún derecho social, vale 0 en
las cuatro dimensiones (no aporta garantía; no es por ello regresiva).

**g = UNI · EXI · DES · NDI.** No hay valores intermedios.

### Marcas complementarias (0/1)

- **REG · Regresiva.** Restringe, recorta o elimina una garantía existente, o introduce una exclusión por origen, situación administrativa, sexo, género u orientación. Si REG = 1, entonces NDI = 0 o la dimensión afectada = 0.
- **DEC · Declarativa.** Sin instrumento concreto (prestación, norma, estándar, plazo, ratio, dotación). Si DEC = 1, entonces EXI = 0; las demás dimensiones se codifican según lo que la medida declara.

### Áreas temáticas (cada medida va a una, según su objeto dominante)

VIV Vivienda · SAN Sanidad · SME Salud mental · EDU Educación · EMP Empleo ·
CUI Cuidados y dependencia · MAM Medio ambiente · EVE Espacios verdes ·
MIG Migración segura · IGU Igualdad y no discriminación · OTR Otras áreas.

### Índices (N = total de medidas del programa)

- I_UNI, I_EXI, I_DES, I_NDI = 100 · (suma de la dimensión) / N
- IGDS = 100 · (suma de g) / N
- IR = 100 · (suma de REG) / N · IV = 100 · (suma de DEC) / N
- Dimensión limitante: la de menor I_k.
- Los mismos cálculos por área temática, con las medidas del área como denominador.

---

## 2. Reglas operativas

### 2.1 Unidad de análisis

- **R1. Todo el programa.** Se codifican las medidas numeradas (`datos/segmentos/`) y también la prosa: prólogos, manifiestos e introducciones de capítulo. Todas las medidas entran en el denominador, también las de OTR.
- **R2. Qué es una medida.** Un compromiso o una intención de la formación de actuar o de conseguir un resultado de política:
  - verbo en primera persona: «haremos», «garantizaremos», «defenderemos», «reclamaremos», «queremos que…»;
  - o fórmula programática: «se creará», «será gratuita», «tendrá derecho a»;
  - o, dentro de una lista numerada, el enunciado nominal del titular («Rebaja masiva de impuestos…»).
- **R3. Qué no es una medida.**
  - **Diagnósticos, valoraciones y críticas.** Incluidas las frases normativas sin compromiso de la formación: «Canarias necesita…», «hace falta…», «X debe…». Si una frase «debe» está dentro de una medida numerada y expresa lo que la formación propone, sí es medida.
  - **Huecos «Permanezca atento a la campaña para conocer esta nueva medida»** del PP: no tienen contenido.
  - **Lemas y aspiraciones sin objeto de política** («recuperar la ambición», «reparar lo que se ha dañado») y los enunciados que solo engloban los objetivos de un bloque («Reparar el Estado»): no son medidas.
- **R4. Atomización.**
  - Una medida es una acción sobre un objeto. Los enunciados compuestos se dividen: «bajaremos el IRPF y el IVA de los alimentos» son dos medidas.
  - Varios instrumentos para el mismo objeto cuentan una vez: «más plazas con más personal y más financiación» es una medida.
  - El titular de una medida numerada no es una medida aparte si el texto la desarrolla.
- **R5. Repeticiones.**
  - Se cuentan una vez, donde están más desarrolladas.
  - Si la prosa repite una medida numerada, se registra con `repite` = id de esa medida y no cuenta en N.
  - Si dentro de una medida numerada se repite otra, `repite` = id de la otra.
- **R6. Fragmento.**
  - Cita literal y continua, de 25 palabras como máximo.
  - Se puede cortar al principio o al final, pero no se cambia ni se salta ninguna palabra; no se usan puntos suspensivos interiores.
  - La página la calcula el programa a partir del fragmento.

### 2.2 Qué es un derecho social (ámbito del índice)

Se toma como referencia el Pacto Internacional de Derechos Económicos, Sociales y Culturales y la Carta Social Europea, más las áreas del libro:

- **Derechos sociales:**
  - salud y salud mental;
  - educación;
  - vivienda y suministros básicos del hogar (agua, energía);
  - trabajo y condiciones laborales dignas;
  - seguridad social y garantía de ingresos (pensiones, desempleo, ingreso mínimo, prestaciones por crianza);
  - cuidados, dependencia y discapacidad;
  - protección de la infancia y de los entornos convivenciales;
  - alimentación;
  - igualdad y no discriminación, incluida la protección frente a la violencia de género;
  - medio ambiente sano y espacios verdes;
  - migración segura y protección internacional;
  - participación en la vida cultural.
- **No son, por sí mismos, derechos sociales:**
  - fiscalidad general;
  - organización del Estado e instituciones;
  - seguridad ciudadana y justicia penal;
  - defensa y política exterior;
  - infraestructuras y transporte;
  - política económica y sectorial;
  - símbolos, lengua oficial y memoria.

  Una medida de estos ámbitos se codifica en las dimensiones solo si regula o provee directamente el acceso a uno de los derechos de la lista; por ejemplo, una deducción por alquiler de vivienda. Si no lo hace: 0 en las cuatro, REG = 0 y área por su objeto (casi siempre OTR).
- **Justicia.** La asistencia jurídica gratuita, los plazos judiciales y los juzgados son organización de la justicia: 0 en las cuatro. Solo cuentan como acceso cuando forman parte del sistema de protección de un colectivo de la lista (violencia de género, infancia, trata).

### 2.3 Área (objeto dominante)

| Área | Incluye |
|---|---|
| VIV | Vivienda, alquiler, suelo residencial, desahucios y ocupación, suministros del hogar y pobreza energética |
| SAN | Sanidad, salud pública, farmacia, listas de espera, profesionales sanitarios |
| SME | Salud mental, adicciones, prevención del suicidio |
| EDU | Educación de 0 a 3 años, escuela, FP, universidad, becas, comedor escolar |
| EMP | Empleo, salarios, condiciones laborales (también las del personal de un cuerpo público: retribuciones, carrera, profesión de riesgo), personas autónomas como trabajadoras, prestación por desempleo |
| CUI | Dependencia, cuidados de larga duración, personas mayores, permisos y conciliación, servicios para personas con discapacidad |
| MAM | Clima, energía, agua, residuos, biodiversidad, contaminación |
| EVE | Parques, zonas verdes urbanas, arbolado, naturaleza en la ciudad |
| MIG | Inmigración, asilo, acogida, menores migrantes sin referentes familiares, fronteras, nacionalidad, expulsiones |
| IGU | Igualdad de género, violencia de género, LGTBI, antidiscriminación, accesibilidad universal |
| OTR | Todo lo demás: fiscalidad, instituciones, seguridad, defensa, economía, infraestructuras, pensiones, rentas mínimas, infancia y entornos convivenciales (salvo crianza y conciliación), cultura, deporte |

Las pensiones y las rentas mínimas van a OTR porque el libro no tiene un área de protección social. Es una carencia del libro que se señala en el informe.

### 2.4 Casos frontera por dimensión

**UNI**
- Evalúa solo las condiciones de renta, necesidad, convocatoria competitiva, merecimiento, cotización previa o capacidad de pago. Las exclusiones por origen o situación administrativa se evalúan en NDI, no en UNI (dimensiones independientes).
- Colectivos definidos por la situación protegida, sin prueba de renta: UNI = 1. Por ejemplo, todo el alumnado de 0 a 3 años, todas las personas en situación de dependencia reconocida, las personas jóvenes en emancipación o las víctimas de violencia de género.
- UNI = 0 cuando el acceso depende de:
  - un umbral de renta o de la condición de «vulnerable» o de «con menos recursos»;
  - el mérito («el inquilino que cumple», «el talento y el esfuerzo»);
  - una cotización previa (prestaciones contributivas);
  - poder pagar («a quien pueda pagar la hipoteca»).

**EXI**
- Lo decide el instrumento, no el verbo.
- EXI = 1 cuando hay una norma con contenido concreto que reconoce el derecho o crea una obligación:
  - prestación o gratuidad garantizada («será gratuita», «tendrá derecho a»);
  - plazo máximo, ratio o estándar mínimo;
  - obligación de provisión;
  - ley de un derecho.
- EXI = 0 para:
  - planes, estrategias, programas, campañas, convocatorias, fondos y dotaciones presupuestarias;
  - «impulsar», «fomentar», «promover» y «estudiar»;
  - «reclamar al Estado», «defender» o «exigir» que otro actúe;
  - «garantizaremos» sin instrumento (que además es DEC = 1).
- Una dotación concreta (cantidad, fondo) no es declarativa (DEC = 0), pero no da exigibilidad (EXI = 0).
- Las rebajas, deducciones y exenciones fiscales, los avales y las subvenciones no reconocen el derecho ni obligan a proveerlo: EXI = 0 aunque se aprueben por ley.
- **Reconocer un derecho en una norma con nombre** (la Constitución, una ley concreta): EXI = 1, aunque el verbo sea «impulsar». Reconocerlo sin nombrar la norma («reconocer los cuidados como derecho social»), o reafirmar un derecho que ya existe, es EXI = 0. El reconocimiento por sí solo no provee ni regula: DES = 0 si no añade un servicio o una regulación.
- **Leyes anunciadas sin contenido** («actualizar la Ley de Prevención», «aprobar una Ley de Negociación Colectiva»): EXI = 0. Con una regla, cifra, plazo, obligación o prestación concreta: EXI = 1. Las leyes ya vigentes cuentan como EXI = 1 solo si la medida se refiere a una prestación concreta que la ley reconoce.

**DES** (criterio del equipo del 16-11-2026)
- DES = 1 solo si la medida da acceso público **sin ningún tipo de copago**:
  - un servicio público que hoy es gratuito para quien lo usa: atención del Sistema Nacional de Salud, enseñanza en centros sostenidos con fondos públicos en las etapas gratuitas, servicios sociales y de protección sin copago (atención a víctimas, protección de la infancia, acogida), bienes ambientales de uso público;
  - un servicio que la medida declara gratuito («gratuita», «sin coste», «sin copago»);
  - una prestación monetaria pública (pensiones, ingreso mínimo, prestación por crianza, cotización a cargo del Estado, prestaciones de la Seguridad Social): no hay copago porque no se paga nada.
- DES = 0:
  - **regulación sin provisión:** límites o congelación de precios y rentas, regulación del mercado de la vivienda, regulación laboral (salario mínimo, jornada, despido, contratos), leyes de protección, igualdad o entornos digitales y otras normas que regulan conductas sin proveer un servicio o una prestación. Un límite al precio no es una garantía pública;
  - **vivienda pública, protegida o asequible:** se paga una renta o un precio, aunque esté limitado;
  - **servicios con tasas, copago o precio:** dependencia y cuidados de larga duración, residencias, servicios sociales con copago, universidad y enseñanzas artísticas, educación de 0 a 3 años si la medida no dice que es gratuita, comedor escolar, farmacia, suministros, transporte y cultura de pago;
  - deducciones, bonificaciones y rebajas fiscales; bonos, cheques y ayudas a la demanda; avales; incentivos a la oferta privada; ayudas ligadas a comprar en el mercado.
- Conciertos y gestión indirecta: DES = 1 solo si el servicio es gratuito para quien lo usa, con `revisar` = 1.
- Una ley que garantiza el acceso a un servicio público gratuito concreto (por ejemplo, los cuidados paliativos en el Sistema Nacional de Salud) sigue la regla del servicio. Una ley descrita solo por lo que regula, prohíbe o sanciona es regulación: DES = 0.
- Si la medida no nombra ninguna provisión, no se presume provisión pública: DES = 0.
- El cambio se aplicó a todas las medidas que tenían DES = 1 mediante tres grupos de `datos/igds/ajustes.json` («DES (16-11)»), sin tocar la codificación original. Los casos de frontera (servicios sociales, educación de 0 a 3 años, formación profesional, enseñanzas artísticas, tratamientos con copago farmacéutico) quedan para la validación humana.

**NDI**
- NDI = 0 para:
  - exclusión explícita por origen, nacionalidad, situación administrativa, sexo, género u orientación («prioridad nacional», «solo para españoles», «residencia legal de X años»);
  - medidas que no tratan del acceso a un derecho social.
- NDI = 1 cuando se formula para toda la población sin cláusulas de exclusión, o cuando corrige una discriminación.
- Nombrar a «los españoles» como destinatarios de forma genérica («los españoles pagarán menos», «todos los españoles tienen derecho a una vivienda digna») no es una cláusula de exclusión.
- Sí lo es cuando la nacionalidad delimita quién recibe una prestación o un servicio concretos, aunque no diga «solo» ni «prioridad»: «vivienda protegida para las familias españolas», «deducciones para inquilinos españoles», «prioridad nacional», «limitar a extranjeros». Entonces NDI = 0 y REG = 1.

**REG**
- Solo cuando afecta a garantías de derechos sociales del apartado 2.2 o introduce una exclusión por origen, situación administrativa, sexo, género u orientación.
- Ejemplos:
  - derogar una ley que regula el precio del alquiler;
  - suprimir prestaciones a un colectivo;
  - restringir el asilo, la regularización, el arraigo, la reagrupación o la nacionalidad;
  - derogar normas de protección frente a la violencia de género o de igualdad LGTBI;
  - prioridad por nacionalidad en vivienda, sanidad, educación o prestaciones.
- Bajar impuestos o reducir gasto general no es REG por sí mismo.
- REG = 1 implica g = 0.
- Si la medida solo suprime, recorta o restringe, sin dar ningún acceso, no provee acceso: UNI = EXI = DES = NDI = 0. La justificación lo dice: «UNI, EXI, DES, NDI 0: solo restringe el acceso, no lo provee.».
- Si da un acceso y a la vez excluye a una parte de la población, se codifica el acceso que da (cada dimensión por su regla) y NDI = 0.

**DEC**
- DEC = 1 sin instrumento concreto: «defenderemos», «apostaremos», «impulsaremos» o «garantizaremos» sin norma, prestación, estándar, plazo, ratio ni dotación.
- Un plan, programa, fondo, estrategia o partida identificados son instrumento: DEC = 0 (pero EXI = 0).
- DEC = 1 implica EXI = 0.

### 2.5 Confianza y revisión

- **Confianza:**
  - alta: la regla se aplica sin dudas;
  - media: hay una interpretación razonable;
  - baja: el texto es ambiguo.
- **`revisar` = 1** si la confianza es baja, si es un caso frontera de los anteriores o si la medida admite dos áreas. Se explica en `motivo_revision` con el formato «Motivo. Propuesta: …».

### 2.7 Ejemplos resueltos

Medidas reales de los tres programas, para calibrar. Se resumen las medidas y se omiten los fragmentos.

| Unidad | Medida | Área | UNI | EXI | DES | NDI | g | REG | DEC | Por qué |
|---|---|---|---|---|---|---|---|---|---|---|
| pp-163 | Etapa de 0 a 3 años gratuita para todas las familias que la soliciten, plazas públicas o concertadas cofinanciadas | EDU | 1 | 1 | 1 | 1 | 1 | 0 | 0 | Gratuidad garantizada a todo el colectivo. `revisar` = 1 por incluir plazas concertadas |
| cc-014 | Más financiación estatal para una oferta suficiente de plazas públicas gratuitas de 0 a 3 años | EDU | 1 | 0 | 1 | 1 | 0 | 0 | 0 | EXI 0: es una dotación, no reconoce el derecho ni fija una obligación |
| pp-226 | Ley nacional de cuidados paliativos que asegure su acceso a toda persona (equipos, dolor, pediatría, domicilio, apoyo psicológico) | SAN | 1 | 1 | 1 | 1 | 1 | 0 | 0 | Varios instrumentos para un mismo objeto: una medida |
| pp-226 | Acompañar a las familias en la enfermedad y el duelo | SAN | 1 | 0 | 1 | 1 | 0 | 0 | 1 | Otro objeto: medida aparte. Sin instrumento, declarativa |
| pp-114 | Pacto de Estado y aportación estatal del 50 % del coste público de la dependencia | CUI | 1 | 0 | 0 | 1 | 0 | 0 | 0 | EXI 0: financiación, no un derecho ni un estándar. DES 0: la dependencia tiene copago (criterio del 16-11-2026) |
| pp-114 | Deducción del 40 % de lo pagado por la atención profesional de una persona mayor dependiente | CUI | 0 | 0 | 0 | 1 | 0 | 0 | 0 | UNI 0: solo para quien puede pagar. EXI y DES 0: deducción |
| pp-114 | El Estado cotiza por quien deja de trabajar o reduce jornada para cuidar a un familiar dependiente | CUI | 1 | 1 | 1 | 1 | 1 | 0 | 0 | Cotización pública garantizada a todo el colectivo, sin prueba de renta |
| pp-153 | IVA del 4 % en la compra de la primera vivienda para menores de 40 años | VIV | 0 | 0 | 0 | 1 | 0 | 0 | 0 | UNI 0: exige poder comprar. EXI y DES 0: rebaja fiscal |
| pp-145 | Derogar la Ley de Vivienda, con sus zonas tensionadas y el índice de precios | VIV | 0 | 0 | 0 | 0 | 0 | 1 | 0 | Suprime una regulación del precio del alquiler: solo restringe |
| vox-027 | Prioridad nacional para acceder a vivienda protegida, social o a ayudas al alquiler | VIV | 0 | 0 | 0 | 0 | 0 | 1 | 0 | Exclusión por nacionalidad: solo restringe |
| cc-026 | Limitar la compra de vivienda en Canarias por personas extranjeras | VIV | 0 | 0 | 0 | 0 | 0 | 1 | 0 | Exclusión por origen. `revisar` = 1: el fin declarado es el acceso de quien reside en las islas |
| vox-022 | Que el ingreso mínimo vital atienda solo a la población española con menos recursos | OTR | 0 | 0 | 0 | 0 | 0 | 1 | 0 | Restringe por nacionalidad una prestación existente |
| vox-022 | Promover el retorno de inmigrantes que cobren el ingreso mínimo vital | MIG | 0 | 0 | 0 | 0 | 0 | 1 | 1 | Restrictiva y sin instrumento |
| cc-012 | Reclamar que los Presupuestos Generales del Estado refuercen las partidas de salud mental en Canarias | SME | 1 | 0 | 1 | 1 | 0 | 0 | 0 | Instrumento identificado (partida), pero sin fuerza obligatoria |
| pp-021 | Endurecer la respuesta penal frente a los disturbios | OTR | 0 | 0 | 0 | 0 | 0 | 0 | 0 | No trata de un derecho social |
| vox-060 | Tarjeta sanitaria única con historia clínica compartida en todo el territorio | SAN | 1 | 0 | 1 | 1 | 0 | 0 | 0 | «Todos los españoles» es genérico, no excluye. EXI 0: herramienta de gestión, no garantía |

### 2.6 Lenguaje de la síntesis y la justificación

- Español técnico y neutral: se codifica lo que el programa dice, sin valorar a la formación.
- Lenguaje inclusivo mediante colectivización («ciudadanía», «personas usuarias», «quien solicite», «población de nacionalidad española»), sin desdoblamientos ni símbolos (@, x, /).
- Guion corto «-», nunca raya.
- La justificación lleva una frase por cada dimensión que vale 0, empezando por su sigla: «UNI 0: exige umbral de renta. DES 0: es una deducción fiscal.».
- Si la medida no trata de un derecho social: «UNI, EXI, DES, NDI 0: no regula ni provee el acceso a un derecho social.».

---

### 2.8 Ajustes de coherencia entre lotes

Cuando dos lotes aplicaron una regla de forma distinta, la coordinación fija la lectura y la aplica a todas las medidas de todas las formaciones que la cumplen. También corrige las repeticiones entre lotes, incluidas las circulares (A repite B y B repite A, y no cuenta ninguna). Los ajustes no tocan los archivos de codificación: están en `datos/igds/ajustes.json`, cada grupo con su regla y su motivo, y el informe dice cuántos se aplicaron a cada formación.

## 3. Registro

- **Lotes de entrada:** `python3 maestro.py igds preparar` → `datos/igds/lotes/lote-NN.json`.
- **Codificación** (`datos/igds/codificacion/lote-NN.json`):

```json
{
  "lote": "lote-01",
  "unidades": {
    "pp-012": {
      "sin_medidas": "",
      "medidas": [
        {
          "fragmento": "cita literal de 25 palabras como máximo",
          "medida_sintesis": "Acción y objeto en una frase",
          "area": "VIV",
          "uni": 1, "exi": 0, "des": 1, "ndi": 1,
          "reg": 0, "dec": 0,
          "justificacion": "EXI 0: se formula como plan sin norma ni plazo.",
          "confianza": "media",
          "revisar": 0,
          "motivo_revision": "",
          "repite": ""
        }
      ]
    }
  }
}
```

  Cada unidad del lote tiene que aparecer. Si no contiene ninguna medida (solo diagnóstico, o un hueco por anunciar), `medidas` es `[]` y `sin_medidas` explica por qué.

- **Comprobación:** `python3 maestro.py igds validar --lote lote-01` comprueba:
  - el esquema;
  - la literalidad y la longitud del fragmento;
  - DEC → EXI = 0 y REG → g = 0;
  - que hay justificación para cada 0;
  - las rayas en los textos propios.
- **Cálculo:** `python3 maestro.py igds calcular` escribe:
  - `datos/igds/igds-medidas.csv`;
  - `datos/igds/igds-areas.csv`;
  - `datos/igds/igds-resultados.json`;
  - `datos/igds/igds-web.json` (recuentos para la herramienta) y `web/public/data/igds-medidas.json` (síntesis y fragmento literal de las medidas que se pueden leer en ella);
  - el informe `datos/informes/igds.md`.
