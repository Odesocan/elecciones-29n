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
3. **Mirar con sentido crítico.** La prueba de las cuentas se descartó el 16-11-2026 (apartado 4). Hoy la herramienta no tiene capa crítica; está previsto que la aporte el IGDS cuando el equipo lo valide.

### Arco narrativo (de arriba abajo)

| Paso | Momento | Pieza | Qué consigue |
|---|---|---|---|
| 1 | **Gancho** | Cartel «LEE, NO SE LO ESPERAN.» y cuenta atrás | Reconocer la campaña y crear urgencia |
| 2 | **Elegir** | «Elige un tema»: 18 mosaicos (desplegable en móvil) | Entrar por lo que le importa a cada persona |
| 3 | **Leer** | Vista de tema: medidas literales por partido | El corazón: leer y comparar |
| 4 | **Ver el conjunto** | Mapa «Lo que dicen. Y lo que no.» | Qué peso da cada programa a cada tema |
| 5 | **Actuar** | «Lee. Compara. Decide.» y compartir | Pasarlo a otra persona |

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
- **Barras:** «Qué parte de cada programa trata de…», en % del programa con la base debajo («18 de 241 medidas»). Si un programa está pendiente, la barra aparece rayada con «Pendiente de publicar».
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

### Codificación visual

- **Mapa:** área de la burbuja ∝ peso, con escala raíz cuadrada. Radio entre 3,5 y 15 px; el mínimo sirve para que un tema con una sola medida se vea.
- **Barritas de los mosaicos:** escala raíz. Son un índice visual; las cifras exactas están en el mapa y en cada tema.
- **Barras de tema:** escala **lineal** y **común a todos los partidos y temas**. Al cambiar de tema, la animación enseña diferencias reales, no reescaladas.
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
- **Sin veredictos:** la herramienta muestra textos literales y pesos de cada tema; no puntúa ni etiqueta los programas.
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
| 16-11 | Se descarta **la prueba de las cuentas**: es difícil de interpretar, una de sus lecturas premia la austeridad al margen de la garantía de derechos y la alerta de riesgo, común a todos los programas, podía animar a la abstención |

---

## 11. Pendiente de diseño

- [ ] Confirmar el color de CC–1ºC.
- [ ] Decidir si se recupera en algún sitio discreto la explicación del método, que hoy solo está en este repositorio.
- [ ] Valorar si se oculta la sigla cuando el logo ya la contiene (PP, PSOE, Vox), por ejemplo «PSOE/♥ PSOE».
- [x] Contraste entre el teal de UPC y el teal de «suman»: las barras de las cuentas usan el navy y el teal de «suman», no el color del partido, así que no se confunden (comprobado al entrar UPC, 16-11).
- [x] Quitar el modo boceto (franja de aviso y «logo» en los huecos sin logo): desactivado el 16-11-2026 (`boceto.activo: false`, `boceto.aviso: ""`).
