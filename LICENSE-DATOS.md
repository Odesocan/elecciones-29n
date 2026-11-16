# Licencias del repositorio

Este repositorio tiene dos licencias, según lo que se reutilice, y contenidos de terceros que no cubre ninguna de ellas.

## Código: MIT

El código está bajo la licencia **MIT** ([LICENSE](LICENSE)). Incluye:

- `maestro.py` y `pipeline/`;
- `web/`, salvo `web/public/logos/` y `web/public/data/`;
- los archivos que genera el pipeline: `divi/odesocan-programas.js`, `divi/bloque-divi.html` e `index.html`.

Se puede usar, copiar, modificar y redistribuir, también con fines comerciales, siempre que se conserve el aviso de copyright y la licencia.

## Datos, clasificaciones y documentación de ODESOCAN: CC BY 4.0

El trabajo propio del Observatorio de Derechos Sociales de Canarias (ODESOCAN) se publica bajo **Creative Commons Atribución 4.0 Internacional (CC BY 4.0)**: https://creativecommons.org/licenses/by/4.0/deed.es. Incluye:

- la clasificación temática y fiscal de las medidas (`datos/clasificacion/`, `datos/fiscal/`, y las columnas `tema` y `fiscal` de los CSV);
- la segmentación en medidas y sus metadatos (identificadores, páginas, apartados, avisos), sin el texto de los programas;
- la codificación, los resultados y las hojas de validación del IGDS (`datos/igds/`);
- los informes (`datos/informes/`) y la hoja de revisión (`datos/revision/`);
- los criterios, el análisis y la documentación (`docs/`, `README.md`) y la configuración de temas (`config/temas.json`).

Se puede compartir y adaptar para cualquier fin, también comercial, siempre que se reconozca la autoría, se enlace la licencia y se indique si se han hecho cambios. Atribución sugerida:

> ODESOCAN, Observatorio de Derechos Sociales de Canarias (2026). *Lee los programas · Elecciones Generales 29N*. https://github.com/Odesocan/elecciones-29n. CC BY 4.0.

## Contenidos de terceros: no están cubiertos por estas licencias

- **Textos de los programas electorales.** Los títulos y textos literales de las medidas están en `datos/segmentos/`, en las columnas `titulo` y `texto` de `web/public/data/programas.csv` y de `divi/data/programas.csv`, y en los fragmentos citados en `datos/igds/`. Son de CC–1ºC, PP, PSOE, UPC y Vox, cada uno sobre su programa. Se reproducen tal cual, sin modificarlos, con fines informativos y de análisis, y con enlace al documento original.
- **El manifiesto de UPC** (`datos/fuentes/programa-upc-29n.pdf` y `divi/data/programa-upc-29n.pdf`). Es de la Unidad del Pueblo Canario, que lo facilitó a ODESOCAN como su programa electoral. Se publica para que se pueda consultar el original, porque no tiene versión en línea.
- **Logos de los partidos y coaliciones** (`web/public/logos/` y `divi/logos/`). Son marcas de sus titulares. Se usan solo para identificar a cada candidatura.

Quien reutilice estos contenidos debe hacerlo con los permisos o las excepciones legales que le correspondan, no con las licencias de este repositorio.
