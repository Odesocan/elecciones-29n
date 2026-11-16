// Módulo 3 · Empaquetado para Divi.
// Tras `vite build` (web/dist/), monta la carpeta divi/ del proyecto:
//
//   divi/bloque-divi.html               ← EL BLOQUE LIMPIO: lo que se pega en el módulo «Código»
//   divi/odesocan-programas.js          ┐
//   divi/data/programas.csv             ├ lo que se publica (GitHub + jsDelivr o Mediateca)
//   divi/logos/                         ┘ (solo si hay logos oficiales en web/public/logos/)
//   divi/bloque-divi-autocontenido.html   alternativa sin alojar nada (≈700 KB · no va a git)
//   divi/prueba/ · divi/index.html        páginas con CSS «hostil» de tema WordPress (no van a git)
//
// Las URL salen de config/campana.json → publicacion.base_url.
import { copyFileSync, mkdirSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { csvParse } from 'd3';

const raiz = (ruta) => fileURLToPath(new URL(`../../${ruta}`, import.meta.url));
const leerJSON = (ruta) => JSON.parse(readFileSync(raiz(ruta), 'utf8'));

const { publicacion } = leerJSON('config/campana.json');
const { version } = leerJSON('web/package.json');
const BASE = publicacion.base_url.trim();
const MARGEN = Number(publicacion.margen_cabecera) || 96;
const HERO = publicacion.hero === false ? ' data-hero="false"' : '';
const MARCADOR = '‹URL_BASE›';
const hoy = new Date().toISOString().slice(0, 10);

if (BASE && !BASE.endsWith('/')) {
  console.error('✗ publicacion.base_url debe terminar en «/» (config/campana.json)');
  process.exit(1);
}

// ── 1 · Carpeta divi/ desde cero (todo lo que hay dentro es generado) ──
const DIVI = raiz('divi');
rmSync(DIVI, { recursive: true, force: true });
for (const d of ['', 'data', 'prueba']) mkdirSync(`${DIVI}/${d}`, { recursive: true });

copyFileSync(raiz('web/dist/odesocan-programas.js'), `${DIVI}/odesocan-programas.js`);
copyFileSync(raiz('web/public/data/programas.csv'), `${DIVI}/data/programas.csv`);
// Programas que el partido facilitó sin versión en línea (pdf_propio, UPC): se publican junto al CSV.
const pdfsPropios = readdirSync(raiz('web/public/data')).filter((f) => f.endsWith('.pdf'));
for (const f of pdfsPropios) copyFileSync(raiz(`web/public/data/${f}`), `${DIVI}/data/${f}`);

const logos = readdirSync(raiz('web/public/logos')).filter((f) => /\.(png|webp|jpe?g|svg)$/i.test(f));
if (logos.length) {
  mkdirSync(`${DIVI}/logos`);
  for (const f of logos) copyFileSync(raiz(`web/public/logos/${f}`), `${DIVI}/logos/${f}`);
}

// ── 2 · Bloque LIMPIO (enlazado) ──
// Sin instrucciones dentro (están en el README): solo el contenedor y el script.
const RESPALDO = '<p>Para comparar los programas electorales necesitas activar JavaScript.</p>';
const bloque = (base, { logosURL = logos.length ? `${base}logos/` : 'ninguno', margen = MARGEN } = {}) =>
  `<!-- ODESOCAN · Lee los programas 29N · v${version} · ${hoy} -->
<div id="lee-los-programas" data-np-programas data-src="${base}data/programas.csv" data-logos="${logosURL}" data-margen="${margen}"${HERO}>
  ${RESPALDO}
</div>
<script src="${base}odesocan-programas.js" defer></script>
`;
writeFileSync(`${DIVI}/bloque-divi.html`, bloque(BASE || MARCADOR));

// ── 3 · Bloque AUTOCONTENIDO (JS y datos en base64) ──
// WordPress/Divi pueden alterar el código pegado (& → &#038;, marcadores en
// los saltos de línea, [corchetes] como shortcodes…). El base64 solo usa
// [A-Za-z0-9+/=] en una sola línea: no hay nada que alterar.
const js = readFileSync(`${DIVI}/odesocan-programas.js`);
const csv = readFileSync(`${DIVI}/data/programas.csv`, 'utf8').trim();
const jsURL = `data:text/javascript;charset=utf-8;base64,${js.toString('base64')}`;
const datosURL = `data:application/json;base64,${Buffer.from(JSON.stringify(csvParse(csv))).toString('base64')}`;
const autocontenido = (logosURL) =>
  `<!-- ODESOCAN · Lee los programas 29N · v${version} · ${hoy} · versión autocontenida -->
<div id="lee-los-programas" data-np-programas data-src="${datosURL}" data-logos="${logosURL}" data-margen="${MARGEN}"${HERO}>${RESPALDO}</div>
<script src="${jsURL}" defer></script>
`;
writeFileSync(
  `${DIVI}/bloque-divi-autocontenido.html`,
  autocontenido(logos.length && BASE ? `${BASE}logos/` : 'ninguno'),
);

// ── 4 · Páginas de prueba con el CSS «hostil» de un tema WordPress ──
const hostil = `<style>
  * { box-sizing: content-box; }
  body { margin:0; font: 14px/1.7em 'Open Sans', Arial, sans-serif; color:#666; letter-spacing:.02em; background:#fff; }
  p { padding-bottom: 1em; margin: 0; }
  h1,h2,h3,h4,h5,h6 { color:#333; padding-bottom:10px; line-height:1em; font-weight:500; }
  ul { list-style-type: disc; padding: 0 0 23px 1em; line-height: 26px; }
  a { color:#2ea3f2; text-decoration:none; }
  button { background:#2ea3f2 !important; color:#fff !important; border-radius:0 !important; font-size:20px !important; }
  svg { width: 100px !important; }
  .et_pb_section { padding: 54px 0; } .et_pb_row { width: 80%; max-width: 1080px; margin: auto; }
  .et_pb_code_inner { text-align: center; }
  .sim-cab { position: sticky; top: 0; z-index: 9; height: 80px; background:#fff; box-shadow: 0 1px 0 rgba(0,0,0,.1);
    display:flex; align-items:center; padding:0 24px; font:700 20px Arial; color:#0d1b2a; }
</style>`;
const pagina = (titulo, contenido) => `<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${titulo}</title>${hostil}</head>
<body>
<header class="sim-cab">ODESOCAN · ${titulo}</header>
<div class="et_pb_section"><div class="et_pb_row"><div class="et_pb_module et_pb_code"><div class="et_pb_code_inner">
${contenido}
</div></div></div></div>
<div class="et_pb_section"><div class="et_pb_row"><h2>Otro módulo de la portada</h2><p>Texto con los estilos del tema, que no deben cambiar.</p><button>Botón del tema</button></div></div>
</body></html>
`;
const logosPrueba = logos.length ? '../logos/' : 'ninguno';
writeFileSync(`${DIVI}/prueba/enlazado.html`, pagina('Prueba Divi · bloque limpio', bloque('../', { logosURL: logosPrueba, margen: 96 })));
writeFileSync(`${DIVI}/prueba/autocontenido.html`, pagina('Prueba Divi · autocontenido', autocontenido(logosPrueba)));
writeFileSync(
  `${DIVI}/index.html`, // portada del servidor de pruebas (python3 maestro.py probar); no va a git
  `<!doctype html><html lang="es"><meta charset="utf-8"><title>Pruebas Divi</title>
<body style="font:16px/1.6 sans-serif;max-width:40rem;margin:3rem auto;padding:0 1rem">
<h1>Pruebas del bloque de Divi</h1>
<p>Simulan un tema WordPress con estilos globales agresivos: la herramienta no debe verse afectada ni afectar al resto.</p>
<ul><li><a href="prueba/enlazado.html">Bloque limpio (enlazado)</a></li><li><a href="prueba/autocontenido.html">Bloque autocontenido</a></li></ul>
</body></html>
`,
);

// ── 5 · index.html de la raíz: la herramienta publicada (GitHub Pages) ──
// Carga el mismo JS, CSV y logos que el bloque de Divi, con rutas relativas a divi/.
// .nojekyll: que GitHub Pages sirva los archivos tal cual, sin procesarlos con Jekyll.
const REPO = (publicacion.repositorio || '').trim();
writeFileSync(
  raiz('index.html'),
  `<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lee los programas · Elecciones Generales 29N · ODESOCAN</title>
<meta name="description" content="Compara, con sus textos literales, lo que proponen en 18 temas los programas electorales de CC–1ºC, PP, PSOE, UPC y Vox para las Elecciones Generales del 29 de noviembre de 2026. Herramienta del Observatorio de Derechos Sociales de Canarias (ODESOCAN).">
<!-- Generado por web/scripts/empaquetar-divi.mjs (python3 maestro.py divi): no se edita a mano. -->
<style>
  body { margin: 0; background: #fff; color: #1a1a24; font: 15px/1.6 'IBM Plex Sans', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif; }
  .pagina { max-width: 1120px; margin: 0 auto; padding: 24px 16px 0; }
  .pie { max-width: 1120px; margin: 0 auto; padding: 24px 16px 40px; font: 12px/1.6 'IBM Plex Mono', ui-monospace, Menlo, monospace; color: #5f6b7a; }
  .pie a { color: #0d1b2a; }
</style>
</head>
<body>
<main class="pagina">
${bloque('divi/', { logosURL: logos.length ? 'divi/logos/' : 'ninguno', margen: 16 })}</main>
<footer class="pie">
  Observatorio de Derechos Sociales de Canarias (ODESOCAN) · <a href="https://odesocan.org">odesocan.org</a>${REPO ? ` · Código, datos y método: <a href="${REPO}">${REPO.replace(/^https:\/\//, '')}</a> · <a href="${REPO}/blob/main/LICENSE-DATOS.md">Licencias</a>: código MIT, datos CC BY 4.0; los textos de los programas y los logos son de cada partido` : ''} · Versión ${version} · ${hoy}
</footer>
</body>
</html>
`,
);
writeFileSync(raiz('.nojekyll'), '');

// ── Resumen ──
const kb = (f) => `${(statSync(`${DIVI}/${f}`).size / 1024).toFixed(0)} KB`.padStart(7);
console.log(`\n   divi/ · v${version}`);
console.log(`   ${kb('bloque-divi.html')}  bloque-divi.html                ← pegar en el módulo Código de Divi`);
console.log(`   ${kb('odesocan-programas.js')}  odesocan-programas.js           ┐ publicar en`);
console.log(`   ${kb('data/programas.csv')}  data/programas.csv              ┘ ${BASE || '(falta publicacion.base_url)'}`);
for (const f of pdfsPropios) console.log(`   ${kb(`data/${f}`)}  data/${f.padEnd(28)}  (programa sin versión en línea: también se publica)`);
console.log(`   ${logos.length ? `${String(logos.length).padStart(4)} arch.` : '   sin  '}  logos/${logos.length ? '' : '  (sin logos oficiales: se ve el color del partido)'}`);
console.log(`   ${kb('bloque-divi-autocontenido.html')}  bloque-divi-autocontenido.html  (alternativa sin alojar nada)`);
console.log('             prueba/  index.html             python3 maestro.py probar → http://127.0.0.1:4173');
if (!BASE) {
  console.log(
    `\n   ⚠ config/campana.json → publicacion.base_url está vacío: bloque-divi.html lleva el marcador ${MARCADOR}.` +
      '\n     Rellénalo (ver README → «Publicar en Divi») y vuelve a ejecutar: python3 maestro.py divi',
  );
}
