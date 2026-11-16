// ─────────────────────────────────────────────────────────────
//  Configuración de la herramienta
//  NO se edita aquí: viene de ../../config/*.json, la misma que usa
//  el pipeline de datos (fuente única de verdad). Este módulo solo la
//  adapta a lo que necesitan los componentes.
// ─────────────────────────────────────────────────────────────
import { partidos } from '../../config/partidos.json';
import { temas } from '../../config/temas.json';
import campana from '../../config/campana.json';
import igds from '../../config/igds.json';
// Resumen del IGDS que genera «python3 maestro.py igds calcular» (solo recuentos;
// los textos de las medidas se piden aparte, ver urlDatos).
import igdsDatos from '../../datos/igds/igds-web.json';

// Votación y cuenta atrás (hora canaria; el 29-N Canarias está en UTC+0).
export const FECHA_ELECCION = campana.eleccion.fecha;
export const APERTURA_COLEGIOS = campana.eleccion.apertura_colegios;
export const CIERRE_COLEGIOS = campana.eleccion.cierre_colegios;

// Franja de aviso superior ('' = sin franja) y modo boceto.
export const MODO_BOCETO = campana.boceto.activo;
export const AVISO = campana.boceto.aviso;
// Última comprobación de programas publicados (se muestra en los pendientes).
export const FECHA_COMPROBACION = campana.fecha_comprobacion;

// Partidos en orden ALFABÉTICO por sigla: orden neutro, sin jerarquía.
// `programa`: URL del PDF oficial ('' si aún no está publicado). Se usa para
// el enlace «Programa (PDF)» y, si una fila del CSV no trae `url`, para
// construir el enlace a la página concreta (#page=N).
// `pdfPropio`: el partido facilitó el documento sin versión en línea (UPC);
// se publica junto al CSV y se enlaza con urlPrograma().
export const PARTIDOS = partidos.map(({ id, sigla, nombre, color, logo, programa }) => ({
  id,
  sigla,
  nombre,
  color,
  logo,
  programa: programa?.url || '',
  pdfPropio: programa?.pdf_propio ? programa.archivo : '',
}));

// Carpeta de los datos publicados (la del CSV), para enlazar los PDF propios.
// La fija App con su «src»; si el CSV va incrustado (data:), no hay carpeta
// y esos PDF quedan sin enlace.
let baseDatos = '';
export function fijarBaseDatos(src) {
  try {
    baseDatos = src && !/^(data:|#)/.test(src) ? new URL('.', new URL(src, window.location.href)).href : '';
  } catch {
    baseDatos = '';
  }
}
export function urlPrograma(partido) {
  if (partido?.programa) return partido.programa;
  return partido?.pdfPropio && baseDatos ? new URL(partido.pdfPropio, baseDatos).href : '';
}
// Otro archivo publicado junto al CSV ('' si el CSV va incrustado).
export const urlDatos = (archivo) => (baseDatos ? new URL(archivo, baseDatos).href : '');

// ── IGDS · «Prometer no es garantizar» ──────────────────────────
// Se muestra si campana.igds.activo es true. En el servidor de desarrollo se
// ve siempre, para que el equipo lo revise antes de publicarlo.
export const IGDS_ACTIVO = Boolean(campana.igds?.activo) || import.meta.env.DEV;
export const IGDS_SELLO = campana.igds?.sello || '';
export const IGDS_TEXTOS = igds.web;
export const IGDS_DATOS = igdsDatos;
export const IGDS_AREAS = Object.fromEntries(igds.areas.map((a) => [a.id, a.nombre]));
export const REPOSITORIO = campana.publicacion?.repositorio || '';

// Las temáticas (18 desde el 16-11-2026). `alcance` es la regla de clasificación, visible al público.
export const TEMAS = temas;

// Cuántos artículos se ven por partido antes de pulsar «Mostrar más».
export const ARTICULOS_VISIBLES = campana.articulos_visibles;

export const ENLACES = campana.enlaces;
