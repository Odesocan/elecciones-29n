---
type: visualizacion
fase: visualizacion
proyecto: PE_29N
tags: [PE_29N, diseno, react, d3, divi, sistema-np]
status: vigente
actualizado: 2026-11-16
aliases: ["PE_29N · Diseño de la herramienta"]
fuente: "OBSERVATORIO/Programas electorales 29N/docs/DISENO.md"
---

# Diseño de «Lee los programas · 29N»

*Resumen del diseño de la herramienta de ODESOCAN para la portada de odesocan.org en la campaña de las Elecciones Generales del 29 de noviembre de 2026. Estado a 14-11-2026.*

La arquitectura técnica (módulos, script maestro, publicación) está en el [README](../README.md). Este documento trata del **diseño**: el relato, el sistema visual, los componentes, las métricas y las decisiones tomadas con el equipo.

---

## 1. Concepto

Es la versión digital de la campaña de calle **«LEE, NO SE LO ESPERAN.»**. Invita a leer los programas electorales y da herramientas para compararlos con rigor. Tiene tres principios:

1. **Leer, no resumir.** Todas las medidas son **texto literal** del programa, verificado letra a letra contra el PDF oficial y con un enlace a su página.
2. **Comparar con justicia.** Las mismas reglas valen para todos los partidos, las métricas son relativas para que el programa más largo no gane por extensión, y los partidos van en orden alfabético.
3. **Mirar con sentido crítico.** La prueba de las cuentas se descartó el 16-11-2026 y el apartado del IGDS, «Prometer no es garantizar» (apartado 4), se retiró de la web ese mismo día a petición del equipo. Hoy la herramienta publicada no tiene capa crítica. El IGDS sigue construido y se puede volver a encender con `igds.activo` en `config/campana.json`.

### Arco narrativo (de arriba abajo)

| Paso | Momento | Pieza | Qué consigue |
|---|---|---|---|
| 1 | **Gancho** | Cartel «LEE, NO SE LO ESPERAN.» y cuenta atrás | Reconocer la campaña y crear urgencia |
| 2 | **Elegir** | «Elige un tema»: 18 mosaicos (desplegable en móvil) | Entrar por lo que le importa a cada persona |
| 3 | **Leer** | Vista de tema: medidas literales por partido | El corazón: leer y comparar |
| 4 | **Ver el conjunto** | Mapa «Lo que dicen. Y lo que no.» | Qué peso da cada programa a cada tema |
| 5 | **Mirar con sentido crítico** | «Prometer no es garantizar»: el IGDS, de cada 100 medidas. **Retirado de la web el 16-11-2026** | Saber cuántas medidas garantizan un derecho y qué preguntar a cada candidatura |
| 6 | **Actuar** | «Lee. Compara. Decide.» y compartir | Pasarlo a otra persona |

---

## 2. Recorrido de la página

```
┌ Franja de aviso (rayada), solo en modo boceto: desactivada desde el 16-11-2026
├ BANDA TEAL ───────────────────────────────────────────────────────────────
│  Antetítulo «Elecciones generales / 29 de noviembre»   QUEDAN [14][20][51][48]
│  LEE,  NO SE LO / [ESPERAN.]
│  ▌Compara qué proponen CC–1ºC, PP, PSOE, UPC y Vox en 18 temas.
│  PASO 1 · ELIGE UN TEMA   (progreso «Has leído X de 18» · leyenda de barritas)
│  [01 Igualdad ▂▃_▅] [02 Vivienda …] … 18 mosaicos
├ BANDA BLANCA (solo con un tema abierto) ──────────────────────────────────
│  Tema 02 de 18 · VIVIENDA · alcance · dateline · [Otro tema] [Compartir]
│  PASO 2 · Filtra por partido (chips; con 2 o 3 se leen en paralelo)
│  Barras «Qué parte de cada programa trata de vivienda»
│  Bloques por partido → fichas de medida → ← Tema anterior · Siguiente tema →
├ BANDA DEL MAPA (blanca, filete navy) ─────────────────────────────────────
│  «LO QUE DICEN. [Y LO QUE NO.]» · matriz 18 temas × 5 partidos + Media
├ BANDA DEL IGDS (blanca, filete navy; solo con igds.activo, apagado desde el 16-11) ──────────────
│  «PROMETER NO ES [GARANTIZAR.]» · las cuatro preguntas · leyenda-mando
│  5 rejillas de 100 casillas · notas emergentes · lista de medidas literales
└ FRANJA FINAL TEAL ─ «El próximo 29 de noviembre · LEE. COMPARA. [DECIDE.]» · Pásaselo a alguien
```

---

## 3. Sistema visual

Se basa en el sistema editorial **`.np`** de ODESOCAN, con el eco del cartel de calle.

### Paleta

| Uso | Color | Notas |
|---|---|---|
| Teal de marca | `#00C8B4` | Bandas del cartel y la franja final; cajas de los titulares |
| Navy | `#0D1B2A` | Tipografía del cartel y cifras del reloj |
| Tinta / cuerpo | `#1A1A24` / `#2B2B38` | Texto |
| Gris de metadatos | `#5F6B7A` | Versión AA (5,4:1) del `#7A8898` de la guía |
| Teal claro | `#E3F8F5` | Fondos suaves, fila activa del mapa |

### Colores de partido

Los colores de partido marcan **solo de quién es algo**: la barra, la burbuja, el borde de su bloque o el chip. El marco de la herramienta es siempre de ODESOCAN.

| Partido | Color | Origen |
|---|---|---|
| CC–1ºC | `#FFC800` | Amarillo común a sus dos logos. **Pendiente de confirmar** |
| PP | `#1E4B8F` | Su logo |
| PSOE | `#DA0200` | Su logo |
| UPC | `#3D9E9A` | La «P» de su logo; no se usa su amarillo, que se confunde con CC |
| Vox | `#5AC035` | Su logo |

- Cuando un color de partido hace de fondo de texto (chips, etiquetas), la herramienta calcula sola si el texto va en blanco o en navy y oscurece el fondo si hace falta para llegar a 4,5:1 (`varsPartido()`).
- **Logos oficiales** en `web/public/logos/`: PNG transparentes de 240 px de alto que se muestran a 40 px. El de CC–1ºC une, sin redibujar, el de Coalición Canaria y el de Primero Canarias. No se dibujan imitaciones de ningún logo.

### Tipografía

| Familia | Papel |
|---|---|
| **Anton** | La voz del cartel: lema, titulares en mayúsculas, números grandes (ratio, cifras del reloj, nº de tema) |
| **IBM Plex Sans** | Lectura: sumarios, textos de las medidas, explicaciones |
| **IBM Plex Mono** | El dato frío: antetítulos, etiquetas, metadatos («Medida 26 · Pág. 23»), botones |

La DM Serif Display del sistema `.np` (la voz de las citas) se dejó de cargar el 14-11: desde que se quitó la cita del cierre no la usaba nada.

### Recursos gráficos recurrentes

- **Caja** (`np-caja`): una palabra en caja blanca o teal dentro de un titular, como «ESPERAN.» en el cartel. Se repite en «Y LO QUE NO.» y «DECIDE.».
- **Filete izquierdo** de 4 px en el color de su contexto: sumario, avisos, el peso del tema en cada partido.
- **Bandas** a todo el ancho para marcar los actos del relato: teal, blanca, mapa, teal.

---

## 4. Componentes

### Cabecera de campaña (`Hero` + `CuentaAtras`)

- **Antetítulo y reloj:** «Elecciones generales / 29 de noviembre» y, en la misma fila, **QUEDAN [días][horas][min][seg]**. En móvil el reloj baja a una segunda línea, siempre en una sola fila. No tiene botón de pausa.
- **Lema:** «LEE,» a la izquierda y «NO SE LO / ESPERAN.» a la derecha en todos los anchos, como en el cartel.
- **Sumario:** «Compara qué proponen CC–1ºC, PP, PSOE, UPC y Vox en 18 temas.».
- **Día de la votación:** el reloj se cambia por «Hoy se vota · colegios abiertos hasta las 20:00».

### Selector de temas (`SelectorTemas`)

- **Mosaicos:** 18, con el número en Anton, el estado («Leyendo» o «✓ Leído»), el nombre y **cinco barritas**, una por partido, con el peso del tema en cada programa.
- **Progreso:** «Has leído X de 18 temas», guardado en el navegador.
- **Leyenda:** las siglas de los partidos con su color. Las de los programas no publicados aparecen tachadas.
- **Rejilla:** 2 columnas en móvil, 3 desde 560 px y 6 desde 1000 px, para que las 18 piezas llenen siempre las filas.
- **Móvil (contenedor de menos de 560 px): desplegable.** La lista va plegada tras un botón que dice el tema que se lee («Tema que lees · Vivienda · Cambiar») o «18 temas · Elige uno». Al abrirlo, los temas salen en filas compactas: número, nombre, estado, barritas y total. Al elegir uno, la lista se pliega y la página baja al tema. «Otro tema» la vuelve a abrir con el foco en el tema que se leía. La leyenda de las barritas solo aparece con la lista abierta. Desde 560 px no hay desplegable.
### Vista de tema (`VistaTema`)

- **Cabecera:**
  - «Tema 02 de 18», título en Anton y el **alcance** del tema, que es la regla de clasificación a la vista.
  - Dateline: «39 artículos · 3 de 3 programas publicados hablan de ello · 2 pendientes».
  - Botones «Otro tema» y «Compartir este tema».
- **Paso 2 · filtro por partido:** chips multiselección. Con 2 o 3 partidos elegidos, en pantallas anchas se leen **en paralelo, en columnas**.
- **Barras:** «Qué parte de cada programa trata de…», en % del programa.
  - **Sin eje de nombres:** cada barra arranca en el **logo** del partido, en una pastilla blanca con el borde de su color. La pastilla tiene el mismo ancho en todas las filas: es el origen común que permite comparar longitudes. Si el logo no carga, en su lugar aparece la sigla.
  - **Porcentaje en la punta** de la barra (etiquetado directo), en IBM Plex Mono 600 de 18 a 24 px, color tinta, con cifras de ancho fijo. La base («18 de 241 medidas») va debajo, alineada con el origen de la barra, a 13 px.
  - **Contador:** al cambiar de tema, el porcentaje cuenta desde el valor anterior hasta el nuevo mientras la barra crece (600 ms, la misma curva). Con «reducir movimiento» se muestra el valor final directamente.
  - **Lector de pantalla:** cada fila es un botón con la frase completa («PP: 7 % de su programa, 18 de sus 241 medidas…»); el contador y la base se ocultan para que no se lean dos veces.
  - Si un programa está pendiente, la barra aparece rayada con «Pendiente de publicar».
- **Bloque de cada partido:**
  - Cabecera fija al hacer scroll, con logo, sigla y nº de artículos, para saber siempre de quién es lo que se lee.
  - Nombre completo y enlace «Programa (PDF) ↗».
  - **Peso del tema:** «**8 %** de su programa (18 de sus 241 medidas). Es su 6.º tema de 18».
  - Se ven 3 fichas y el resto con «Mostrar N más».
- **Ficha de medida:**
  - Meta «Medida N · Pág. X», titular y **texto literal entre comillas angulares**, con «Leer completo» si es largo.
  - Aviso «⚠ Texto incompleto en el PDF original» cuando procede.
  - «También en: otros temas».
  - «Ver en el programa ↗», que abre el PDF en su página.
- **Programa pendiente:** recuadro «Este programa aún no se ha publicado (última comprobación…)». Nunca se muestra como «no propone nada».
- **Ningún artículo:** «No hemos localizado artículos… ¿Crees que falta alguno? Escríbenos», con enlace a la página de contacto.

### Mapa (`MapaProgramas`) · «Lo que dicen. Y lo que no.»

- **Matriz:** 18 temas × 5 partidos. Cada **burbuja** tiene el área proporcional al peso del tema en ese programa.
- **Casos especiales:** el anillo discontinuo significa ninguna medida localizada y la raya, programa no publicado.
- **Columna «Media»:** el peso medio del tema entre los programas publicados.
- **Al pulsar:**
  - Una burbuja abre el tema y lleva al bloque de ese partido, con todos los partidos a la vista.
  - El nombre de un tema abre el tema.
  - Las siglas resaltan su columna y muestran sus **tres temas con más peso**.

### Garantías (`Garantias`) · «Prometer no es garantizar»

La capa crítica: el IGDS de ODESOCAN ([CRITERIOS-IGDS.md](CRITERIOS-IGDS.md)). **Retirado de la web el 16-11-2026 a petición del equipo**, el mismo día en que se publicó. El componente y los datos se conservan: se enciende con `igds.activo` en `config/campana.json`, y en el servidor de desarrollo se ve siempre. Mientras sea provisional lleva el sello de `igds.sello`.

- **Las cuatro preguntas**, en lenguaje llano y numeradas: ¿llega a toda la población? (UNI), ¿se puede reclamar? (EXI), ¿es público y sin copago? (DES), ¿no excluye a nadie? (NDI). Cada una tiene una nota emergente «Cuándo es sí» con la regla del libro de códigos, con ejemplos genéricos, no medidas de ningún partido. La regla del índice va en una línea: cuatro síes, garantía completa.
- **De cada 100 medidas:** una rejilla de 10 × 10 casillas por programa, en orden alfabético. Cada casilla es 1 de cada 100 medidas, así que la escala es relativa y común. Las casillas pueden partirse, para que 0,4 se vea como 0,4 de casilla y no desaparezca al redondear.
- **Categorías exclusivas, en este orden:**
  - garantía completa, en el color del partido;
  - se acercan (tres síes), al 55 %;
  - otras medidas sociales (uno o dos síes), al 20 %;
  - regresivas, en blanco con aspa navy y sin color de partido;
  - resto del programa, casilla vacía.

  Más intenso significa más cerca de garantizar el derecho. Las **declarativas** llevan un punto navy encima de su casilla, porque pueden estar en cualquier categoría.
- **La leyenda es el mando.** Seis botones (`aria-pressed`), cada uno con su muestra, su nombre y una línea de explicación. Al elegir uno, esa categoría se resalta en los cinco programas (el resto se atenúa al 30 %, sin desaparecer) y las cifras cuentan hasta su valor, con el mismo contador que las barras del paso 2. **Al volver a pulsarlo se deselecciona.** Sin categoría elegida se ve el reparto completo y las cifras son el IGDS. Debajo de cada cifra, en mono, la categoría a la que corresponde. La caja de explicación y su nota «Cómo se cuenta», que iban bajo la leyenda, se quitaron a petición del equipo el 16-11-2026. Para lectores de pantalla, una región `aria-live` anuncia la categoría y las cinco cifras.
- **Notas en cada panel:**
  - calculadas con los datos: «Dónde están» (áreas de las garantías o de las regresivas) y «Qué les falta» (qué pregunta falla en las que se acercan);
  - editoriales, desde `config/igds.json → web.notas_partido`: «¿Por qué 0?» en CC–1ºC (pedir al Estado no es comprometer una ley propia) y en UPC (manifiesto de 6 páginas).

  Las notas emergentes se despliegan debajo de su botón, sin tapar nada, y se cierran con Escape.
- **Leer las medidas.** En garantía completa, se acercan y regresivas, cada panel ofrece «Leer las N». Abre debajo la lista con la síntesis de ODESOCAN, el fragmento literal entre comillas, el área, el enlace a la página del PDF y, en las que se acercan, «Le falta: …». Los textos (`igds-medidas.json`) se publican junto al CSV y solo se piden al abrir la primera lista. En la versión autocontenida no hay carpeta de datos y el botón no aparece.
- **Cierre:** «En los cinco programas, la respuesta que más falta es la segunda… Es una buena pregunta para hacer a cada candidatura.» Solo aparece si la exigibilidad es la dimensión limitante en todos los programas. Se calcula, no se da por supuesto.
- **Tabla de datos** desplegable con todas las categorías y formaciones. Las notas de método y los enlaces al libro de códigos y al CSV se quitaron a petición del equipo (16-11-2026); el sello de provisional se mantiene.
- **Textos:** `config/igds.json → web`, editables sin tocar el código. **Cifras:** `datos/igds/igds-web.json`, que genera `maestro.py igds calcular`. La web no recalcula nada.

### La prueba de las cuentas · descartada el 16-11-2026

La banda «Prometer es gratis. Pagarlo, no.» (`CuentasProgramas`) contaba, por partido, las medidas que restan y las que suman dinero a las cuentas públicas, y ponía una etiqueta roja de «Riesgo de viabilidad». También mostraba en cada ficha de medida su efecto en las cuentas públicas. El equipo la descartó por tres motivos:

1. es difícil de interpretar;
2. una de sus lecturas principales puntúa en positivo la austeridad económica, al margen de la garantía de derechos;
3. otra lectura anima a la abstención, porque todos los programas llevaban la alerta de riesgo de viabilidad.

Se quitaron la banda, las etiquetas de las fichas, la columna `fiscal` del CSV publicado y la regla de riesgo. La clasificación fiscal se conserva como archivo ([CRITERIOS-IMPACTO-FISCAL.md](CRITERIOS-IMPACTO-FISCAL.md)).

### Franja final (`Cierre`)

«El próximo 29 de noviembre» sobre **LEE. COMPARA. [DECIDE.]**, con el botón **«Pásaselo a alguien»**: menú de compartir del móvil, o copia del enlace en escritorio.

---

## 5. Métricas y visualización de datos

| Métrica | Cálculo | Dónde | Por qué |
|---|---|---|---|
| **Peso de un tema** | medidas del partido en el tema ÷ total de medidas del partido | Barritas, barras, mapa, bloque de partido | Comparar programas de 100 y de 241 medidas. El recuento absoluto premiaba al más largo |
| **Puesto del tema** | Orden de los 18 temas por peso dentro de cada programa, con aviso de empate | Bloque de partido | Responder a «qué importa más a cada uno» |
| **Media** | Peso medio entre programas publicados | Columna del mapa | Una referencia común sin sesgo de extensión |
| **IGDS** | medidas con las cuatro dimensiones a 1 ÷ total de medidas del programa × 100 | Rejillas del IGDS | Cuántas de cada 100 garantizan un derecho; relativo, como el peso de un tema |
| **Se acercan · otras sociales · resto** | medidas con 3, con 1 o 2 y con 0 dimensiones a 1 (sin las regresivas) ÷ total × 100 | Rejillas del IGDS | El embudo: dónde se quedan las medidas que no llegan a garantía |
| **IR · IV** | regresivas y declarativas ÷ total × 100 | Rejillas del IGDS (aspa y punto) | Las marcas complementarias del libro, a la vista y sin restar del IGDS |

### Codificación visual

- **Mapa:** área de la burbuja ∝ peso, con escala raíz cuadrada. Radio entre 3,5 y 15 px; el mínimo sirve para que un tema con una sola medida se vea.
- **Barritas de los mosaicos:** escala raíz. Son un índice visual; las cifras exactas están en el mapa y en cada tema.
- **Barras de tema:** escala **lineal** y **común a todos los partidos y temas**. Al cambiar de tema, la animación enseña diferencias reales, no reescaladas.
- **Rejillas del IGDS:** gráfico de unidades, 1 casilla por cada 100 medidas, con casillas partidas para los decimales. Las cifras del IGDS llevan un decimal (0,4 no es 0). El partido se reconoce por su logo, su sigla y su posición; el color lo refuerza, pero no es lo único que lo identifica: amarillo, verde y rojo se confunden con daltonismo.
- **Reparto del trabajo:** D3 calcula escalas y anima (anchos, radios, opacidades) y React pinta la estructura. Con «reducir movimiento» no hay animaciones.

---

## 6. Interacción

- **URL compartible:** `?tema=vivienda&partidos=pp+vox`. Se actualiza con `replaceState` y no con `#`, porque Divi salta a las anclas. Un enlace compartido abre el tema directamente.
- **Saltos con foco:** al elegir un tema, la vista baja hasta él y pone el foco en su título. Desde una burbuja, baja al bloque del partido y lo destaca un momento.
- **Filtro de partidos:** si se eligen los 5, vuelve a «Todos». Cada cambio se anuncia en voz para lectores de pantalla («Mostrando N artículos de M programas»).
- **Temas leídos:** se recuerdan en el propio navegador del lector.

---

## 7. Accesibilidad

- **Interacción:**
  - Objetivos táctiles de al menos 44 px.
  - Botones con `aria-pressed` y `aria-expanded`.
  - Región `aria-live` para los cambios.
- **Mapa:** una sola parada de tabulador; las flechas, Inicio y Fin recorren la matriz. Cada celda tiene su etiqueta completa («PP en Vivienda: 7 % de su programa, 18 de 241 medidas»).
- **Gráficos:** son `aria-hidden` y siempre van acompañados de una frase equivalente para lector de pantalla.
- **Contraste:**
  - Gris de metadatos al 5,4:1.
  - Colores de partido con texto calculado para AA.
  - El teal de «suman» se oscurece.
  - Modo de alto contraste (`forced-colors`) contemplado.
- **Movimiento:** con `prefers-reduced-motion` no hay animaciones y el reloj se actualiza cada minuto, sin segundos.
- **Cuenta atrás:** el lector de pantalla oye una frase estable, no un aviso cada segundo.
  - ⚠ **Por decisión del equipo no tiene botón de pausa.** WCAG 2.2.2 (nivel A) lo pide para contenido que se actualiza solo.

---

## 8. Responsive e integración en Divi

- **Se adapta al contenedor, no a la ventana:** `@container` sobre el ancho real de la columna de Divi.
  - **560 px:** el mapa crece y aparecen los números de tema; el selector de temas deja de ser un desplegable.
  - **760 px:** cambios de rejilla intermedios.
  - **900 px:** mapa con su introducción al lado y modo de lectura en paralelo.
- **Shadow DOM:** los estilos del tema WordPress no entran en la herramienta y los de la herramienta no salen. Se ha probado con una página de CSS «hostil».
- **Cabecera fija de Divi:** `data-margen` compensa su altura en los saltos y en las cabeceras fijas de cada partido.
- **Bloque limpio:** un comentario, un contenedor y un script. Los datos, el JS y los logos se publican aparte (ver el README).

---

## 9. Neutralidad y rigor

- **Orden:** alfabético por sigla en toda la herramienta.
- **Atribución:** solo se atribuye a un partido lo que dice su texto literal, con enlace a la página del PDF.
- **Clasificación:** la temática sigue criterios escritos e iguales para todos ([CRITERIOS-CLASIFICACION.md](CRITERIOS-CLASIFICACION.md)). La fiscal ya no se publica (apartado 4).
- **Sin veredictos:** la herramienta muestra textos literales y pesos de cada tema; no puntúa ni etiqueta los programas. El IGDS cuenta cuántas medidas cumplen una regla escrita e igual para todos. No da una nota global ni resta las regresivas, enseña los límites del índice y deja leer las medidas literales que lo respaldan.
- **Peso ≠ calidad:** más espacio no significa mejores propuestas, y se recuerda junto a cada gráfico.

---

## 10. Decisiones tomadas con el equipo

| Fecha | Decisión |
|---|---|
| 13-11 | Tono «más campaña de calle»; solo siglas de partido; cuenta atrás en días, horas, minutos y segundos; sumario corto «Compara qué proponen…» |
| 13-11 | Colores corporativos en barras y bloques de partido; gráficos sobre fondo claro, no navy; «Escríbenos» lleva a la página de contacto; sin la etiqueta «Literal» |
| 13-11 | Pulsar una burbuja del mapa lleva al bloque del partido sin perder el tema ni al resto de partidos |
| 13-11 | Métrica principal **relativa** (% del programa) en lugar del recuento absoluto |
| 14-11 | Nueva capa crítica: **la prueba de las cuentas**. Tono sin veredictos, con hechos y reglas |
| 14-11 | Vocabulario «restan / suman»; barras etiquetadas en lugar de balanza |
| 14-11 | Etiqueta roja **Riesgo de viabilidad** cuando las medidas que restan son más del doble de las que suman |
| 14-11 | Se quitan el bloque de conclusión de las cuentas y, en el cierre, la cita, la lista de PDF y el apartado de método |
| 14-11 | Franja final «El próximo 29 de noviembre»; reloj en una fila y sin pausa |
| 14-11 | UPC en el teal de su «P»; logos oficiales de los cinco; colores de PP y PSOE tomados de sus logos |
| 14-11 | Se deja de cargar DM Serif Display, sin uso desde que se quitó la cita |
| 16-11 | Se quita el modo boceto: sin franja de aviso |
| 16-11 | Barras del paso 2: logo al comienzo de cada barra en lugar del nombre tras el eje, porcentaje más grande en la punta y contador al cambiar de tema |
| 16-11 | Se descarta **la prueba de las cuentas**: es difícil de interpretar, una de sus lecturas premia la austeridad al margen de la garantía de derechos y la alerta de riesgo, común a todos los programas, podía animar a la abstención |
| 16-11 | Capa crítica: el **IGDS** en rejillas de «de cada 100 medidas», con las declarativas (punto) y las regresivas (aspa) en el mismo gráfico y una leyenda explicativa que hace de mando. Se descartaron el radar (el área engaña: UPC tenía el más lleno con IGDS 0), las barras (tres intensidades del mismo color no se distinguen en amarillo y verde) y el treemap (cuenta medidas en absoluto y borra a quien tiene 0). Oculto hasta la validación humana |
| 16-11 | Se publica el IGDS (`igds.activo: true`) antes de cerrar la validación, con el sello «Provisional · pendiente de validación humana» |
| 16-11 | IGDS: sin la sanidad pública como ejemplo de garantía (hoy no funciona como un derecho social); «entornos convivenciales» en lugar de «familias»; sin la caja de explicación bajo la leyenda ni el bloque de método; la leyenda se deselecciona al volver a pulsarla |
| 16-11 | **Cambio de criterio en DES:** solo cuenta el acceso público sin ningún tipo de copago (servicio público gratuito o prestación monetaria pública). Un límite al precio, la regulación y la vivienda con renta pasan a DES 0. IGDS: PP 2,4 → 1,5; PSOE 7,0 → 1,8 ([ANALISIS-IGDS.md](ANALISIS-IGDS.md), apartado 0) |
| 16-11 | Se **retira de la web** el apartado del IGDS («Prometer no es garantizar»): `igds.activo: false`. Se conservan el componente, los datos y el método |

---

## 11. Pendiente de diseño

- [ ] Confirmar el color de CC–1ºC.
- [x] Publicar el IGDS: se publicó el 16-11-2026 con el sello de provisional y se retiró de la web ese mismo día a petición del equipo (`igds.activo: false`).
- [ ] Si se recupera el IGDS: cerrar antes la validación humana, recalcular (`igds calcular`), revisar los textos de `config/igds.json → web`, decidir el sello y encender `igds.activo`.
- [ ] Decidir si se recupera en algún sitio discreto la explicación del método, que hoy solo está en este repositorio.
- [ ] Valorar si se oculta la sigla cuando el logo ya la contiene (PP, PSOE, Vox), por ejemplo «PSOE/♥ PSOE».
- [x] Contraste entre el teal de UPC y el teal de «suman»: las barras de las cuentas usan el navy y el teal de «suman», no el color del partido, así que no se confunden (comprobado al entrar UPC, 16-11).
- [x] Quitar el modo boceto (franja de aviso y «logo» en los huecos sin logo): desactivado el 16-11-2026 (`boceto.activo: false`, `boceto.aviso: ""`).
