// Carga y normaliza los artículos de los programas.
// Acepta:
//  · una URL a CSV (Mediateca de WordPress, Google Sheets publicado como CSV…)
//  · una URL a JSON o un data:application/json;base64,… (versión autocontenida)
//  · «#id» de un <script type="text/csv"> de la propia página
import { csv, csvParse, json } from 'd3';
import { PARTIDOS, TEMAS, urlPrograma } from './config.js';

const IDS_PARTIDO = new Set(PARTIDOS.map((p) => p.id));
const IDS_TEMA = new Set(TEMAS.map((t) => t.id));

// Divi sustituye los saltos de línea del módulo Código por este marcador.
const SALTO_DIVI = /<!--\s*\[et_pb_line_break_holder\]\s*-->/g;

export async function cargarArticulos(src) {
  let filas;
  if (src.startsWith('#')) {
    const nodo = document.querySelector(src);
    if (!nodo) throw new Error(`No encuentro el bloque de datos ${src}`);
    filas = csvParse(nodo.textContent.replace(SALTO_DIVI, '\n').trim());
  } else if (src.startsWith('data:application/json') || /\.json(\?|$)/i.test(src)) {
    filas = await json(src);
  } else {
    filas = await csv(src);
  }
  return normalizar(filas);
}

function normalizar(filas) {
  const avisos = [];
  const articulos = [];
  filas.forEach((f, i) => {
    const partido = String(f.partido || '').trim().toLowerCase();
    const temas = String(f.tema || '')
      .split(/[;|]/)
      .map((t) => t.trim().toLowerCase())
      .filter(Boolean);
    if (!IDS_PARTIDO.has(partido)) return avisos.push(`fila ${i + 2}: partido «${f.partido}» desconocido`);
    const validos = temas.filter((t) => IDS_TEMA.has(t));
    if (!validos.length) return avisos.push(`fila ${i + 2}: tema «${f.tema}» desconocido`);
    articulos.push({
      id: `${partido}-${i}`,
      partido,
      temas: validos,
      ref: String(f.ref || '').trim(),
      pagina: f.pagina ? Number(f.pagina) : null,
      titulo: String(f.titulo || '').trim(),
      texto: String(f.texto || '').trim(),
      url: String(f.url || '').trim(),
      nota: String(f.nota || '').trim(),
    });
  });
  if (avisos.length) console.warn('[ODESOCAN · programas] Filas descartadas:\n' + avisos.join('\n'));
  return articulos;
}

// Índice tema → partido → [artículos] y recuentos para D3.
export function indexar(articulos) {
  const indice = new Map(TEMAS.map((t) => [t.id, new Map(PARTIDOS.map((p) => [p.id, []]))]));
  for (const a of articulos) for (const t of a.temas) indice.get(t).get(a.partido).push(a);
  // Dentro de cada tema, primero las medidas cuyo tema PRINCIPAL es ese;
  // después, las que lo tocan como tema secundario (orden del programa).
  for (const [t, porPartido] of indice)
    for (const lista of porPartido.values()) lista.sort((x, y) => x.temas.indexOf(t) - y.temas.indexOf(t));
  let maximo = 0;
  const totalTema = new Map();
  for (const [t, porPartido] of indice) {
    let suma = 0;
    for (const lista of porPartido.values()) {
      maximo = Math.max(maximo, lista.length);
      suma += lista.length;
    }
    totalTema.set(t, suma);
  }
  // Programas con al menos un artículo cargado. Los demás se tratan como
  // «aún no publicados», que no es lo mismo que «no dice nada».
  const disponibles = new Set(articulos.map((a) => a.partido));

  // ── Métrica relativa ──
  // Los programas tienen extensiones muy distintas (de 100 a 241 medidas),
  // así que el nº absoluto de artículos premia al más largo. El PESO de un
  // tema en un programa es la parte de sus medidas que lo tratan:
  //   cuota = artículos del partido en el tema / total de medidas del partido
  // Una medida puede tratar hasta 3 temas, por eso las cuotas de un mismo
  // programa suman más de 100 %. null = programa aún no publicado.
  const totalPartido = new Map(PARTIDOS.map((p) => [p.id, 0]));
  for (const a of articulos) totalPartido.set(a.partido, totalPartido.get(a.partido) + 1);

  const cuota = new Map();
  let maxCuota = 0;
  for (const [t, porPartido] of indice) {
    const fila = new Map();
    for (const [p, lista] of porPartido) {
      const total = totalPartido.get(p);
      const v = total ? lista.length / total : null;
      fila.set(p, v);
      if (v > maxCuota) maxCuota = v;
    }
    cuota.set(t, fila);
  }

  // Peso medio del tema entre los programas publicados (columna «Media»).
  const mediaTema = new Map();
  for (const [t, fila] of cuota) {
    const vals = [...fila.values()].filter((v) => v !== null);
    mediaTema.set(t, vals.length ? vals.reduce((s, v) => s + v, 0) / vals.length : null);
  }

  // Puesto del tema dentro de cada programa (1 = el que más pesa).
  // Se compara con nº de artículos: mismo denominador y sin errores de coma flotante.
  const puesto = new Map();
  const destacados = new Map();
  for (const p of disponibles) {
    const ns = TEMAS.map((t) => [t.id, indice.get(t.id).get(p).length]);
    const porTema = new Map();
    for (const [t, n] of ns) {
      if (n === 0) {
        porTema.set(t, null);
        continue;
      }
      porTema.set(t, {
        n: 1 + ns.filter(([, m]) => m > n).length,
        empate: ns.filter(([, m]) => m === n).length > 1,
      });
    }
    puesto.set(p, porTema);
    destacados.set(
      p,
      ns
        .filter(([, n]) => n > 0)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 3)
        .map(([t]) => t),
    );
  }

  return {
    indice, maximo, totalTema, disponibles, totalPartido, cuota, maxCuota, mediaTema, puesto, destacados,
  };
}

export function enlaceArticulo(articulo, partido) {
  if (articulo.url) return articulo.url;
  const pdf = urlPrograma(partido);
  if (pdf) return articulo.pagina ? `${pdf}#page=${articulo.pagina}` : pdf;
  return '';
}
