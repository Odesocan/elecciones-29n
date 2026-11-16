import { PARTIDOS, TEMAS } from './config.js';

export const pad = (n) => String(n).padStart(2, '0');

// ── Colores de partido accesibles ──────────────────────────────
// --p        color corporativo tal cual (barras, círculos, bordes)
// --p-fondo  mismo color, oscurecido solo si hace falta para que el
//            texto encima cumpla AA (4,5:1)
// --p-txt    blanco o navy, el que más contraste dé sobre --p-fondo
const NAVY = '#0d1b2a';
function luminancia(hex) {
  const [r, g, b] = [1, 3, 5].map((i) => {
    const c = parseInt(hex.slice(i, i + 2), 16) / 255;
    return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
const contraste = (a, b) => {
  const [x, y] = [luminancia(a), luminancia(b)].sort((m, n) => n - m);
  return (x + 0.05) / (y + 0.05);
};
const oscurecer = (hex, f) =>
  '#' + [1, 3, 5].map((i) => Math.round(parseInt(hex.slice(i, i + 2), 16) * f).toString(16).padStart(2, '0')).join('');

const cacheVars = new Map();
export function varsPartido(p) {
  if (cacheVars.has(p.id)) return cacheVars.get(p.id);
  let fondo = p.color;
  let txt = contraste(fondo, '#ffffff') >= contraste(fondo, NAVY) ? '#ffffff' : NAVY;
  for (let f = 0.95; contraste(fondo, txt) < 4.5 && f > 0.4; f -= 0.05) {
    fondo = oscurecer(p.color, f);
    txt = '#ffffff';
  }
  const vars = { '--p': p.color, '--p-fondo': fondo, '--p-txt': txt };
  cacheVars.set(p.id, vars);
  return vars;
}

export const plural = (n, uno, varios) => `${n} ${n === 1 ? uno : varios}`;

// ── Peso de un tema en un programa (fracción 0–1) ──────────────
// Se redondea a enteros: con programas de 100–250 medidas, un decimal
// sería una precisión que el dato no tiene.
export const pctNum = (v) => (v > 0 && v < 0.005 ? '<1' : String(Math.round(v * 100)));
export const pct = (v) => `${pctNum(v)} %`;
// Versión para lectores de pantalla («<1» no se lee bien).
export const pctVoz = (v) => (v > 0 && v < 0.005 ? 'menos del 1 %' : pct(v));
export const ordinal = (n) => `${n}.º`;

export const sinMovimiento = () =>
  typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;

export function irA(el, { foco = null, instantaneo = false } = {}) {
  if (!el) return;
  el.scrollIntoView({ behavior: instantaneo || sinMovimiento() ? 'auto' : 'smooth', block: 'start' });
  if (foco) foco.focus({ preventScroll: true });
}

// Días que faltan para la votación (en la zona horaria de quien visita).
export function diasHasta(fechaISO) {
  const hoy = new Date();
  hoy.setHours(0, 0, 0, 0);
  return Math.round((new Date(`${fechaISO}T00:00:00`) - hoy) / 86400000);
}

// ── Estado en la URL: ?tema=vivienda&partidos=pp+psoe ──────────
// Permite compartir un enlace que abre directamente un tema.
// (Se evita el #hash: Divi intenta hacer scroll a los anclajes.)
export function leerURL() {
  const q = new URLSearchParams(window.location.search);
  const tema = TEMAS.some((t) => t.id === q.get('tema')) ? q.get('tema') : null;
  const partidos = new Set(
    (q.get('partidos') || '').split(/[\s,]+/).filter((id) => PARTIDOS.some((p) => p.id === id)),
  );
  return { tema, partidos: partidos.size === PARTIDOS.length ? new Set() : partidos };
}

export function escribirURL(tema, partidos) {
  const url = new URL(window.location.href);
  if (tema) url.searchParams.set('tema', tema);
  else url.searchParams.delete('tema');
  if (tema && partidos.size) url.searchParams.set('partidos', [...partidos].join(' '));
  else url.searchParams.delete('partidos');
  if (url.href !== window.location.href) window.history.replaceState(window.history.state, '', url);
}

// ── «Temas leídos» (solo en el navegador de cada persona) ──────
const CLAVE = 'odesocan-29n-temas-leidos';
export function leerLeidos() {
  try {
    // Solo ids vigentes: un tema retirado (p. ej. «administraciones») no cuenta como leído.
    const ids = new Set(TEMAS.map((t) => t.id));
    return new Set(JSON.parse(localStorage.getItem(CLAVE) || '[]').filter((id) => ids.has(id)));
  } catch {
    return new Set();
  }
}
export function guardarLeidos(conjunto) {
  try {
    localStorage.setItem(CLAVE, JSON.stringify([...conjunto]));
  } catch {
    /* modo privado o almacenamiento bloqueado: no pasa nada */
  }
}

// Compartir: menú nativo en móvil; si no, copia el enlace.
export async function compartir({ titulo, texto, url }) {
  if (navigator.share) {
    try {
      await navigator.share({ title: titulo, text: texto, url });
      return 'compartido';
    } catch (e) {
      if (e && e.name === 'AbortError') return 'cancelado';
    }
  }
  try {
    await navigator.clipboard.writeText(url);
    return 'copiado';
  } catch {
    window.prompt('Copia este enlace:', url);
    return 'manual';
  }
}
