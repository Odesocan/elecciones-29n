// Punto de entrada para Divi / WordPress.
// Busca cada <div data-np-programas> de la página y monta la
// herramienta dentro de un Shadow DOM: los estilos del tema Divi no
// pueden romperla y los suyos no pueden afectar al resto de la web.
//
// Atributos del contenedor:
//   data-src     URL del CSV (o «#id» de un <script type="text/csv">)
//   data-hero    "false" para ocultar la cabecera de campaña
//   data-logos   carpeta (URL terminada en /) con logo-cc.png, logo-pp.png…
//                "ninguno": no se piden logos (cuadrado con el color del partido)
//   data-margen  px que ocupa la cabecera fija del tema (por defecto 96)
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import css from './estilos.css?inline';

const FUENTES =
  'https://fonts.googleapis.com/css2?family=Anton' +
  '&family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,600;0,700;1,300&display=swap';

function cargarFuentes() {
  // @font-face debe declararse en el documento, no dentro del Shadow DOM.
  if (document.querySelector('link[data-np-fuentes]')) return;
  const enlace = document.createElement('link');
  enlace.rel = 'stylesheet';
  enlace.href = FUENTES;
  enlace.dataset.npFuentes = '';
  document.head.appendChild(enlace);
}

export function montar(host) {
  if (host.shadowRoot) return;
  cargarFuentes();
  const sombra = host.attachShadow({ mode: 'open' });
  const estilo = document.createElement('style');
  estilo.textContent = css;
  const raiz = document.createElement('div');
  sombra.append(estilo, raiz);
  const margen = Number(host.dataset.margen || 96);
  raiz.style.setProperty('--np-margen-sup', `${margen}px`);
  createRoot(raiz).render(
    <App
      src={host.dataset.src || './data/programas.csv'}
      hero={host.dataset.hero !== 'false'}
      logos={host.dataset.logos === 'ninguno' ? '' : host.dataset.logos || './logos/'}
    />,
  );
}

function iniciar() {
  document.querySelectorAll('[data-np-programas]').forEach(montar);
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
else iniciar();
