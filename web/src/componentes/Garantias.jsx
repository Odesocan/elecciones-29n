import { useEffect, useId, useMemo, useRef, useState } from 'react';
import { easeCubicOut, interpolateNumber, json, select } from 'd3';
import {
  IGDS_AREAS,
  IGDS_DATOS,
  IGDS_SELLO,
  IGDS_TEXTOS as T,
  PARTIDOS,
  REPOSITORIO,
  urlDatos,
  urlPrograma,
} from '../config.js';
import { irA, plural, sinMovimiento, varsPartido } from '../util.js';
import LogoPartido from './LogoPartido.jsx';

// «Prometer no es garantizar» · el IGDS de ODESOCAN.
// · Una rejilla de 100 casillas por programa: cada casilla es 1 de cada 100
//   medidas, así se comparan programas de 75 y de 681 medidas.
// · Categorías exclusivas, en este orden: garantía completa, se acercan,
//   otras sociales, regresivas (aspa) y resto (casilla vacía). El punto marca
//   las declarativas, que pueden estar en cualquier categoría.
// · La leyenda es el mando: al elegir una categoría se resalta en los cinco
//   programas y las cifras cuentan hasta su valor.
// · Recuentos: datos/igds/igds-web.json. Textos: config/igds.json → web.
//   Las medidas literales se piden aparte (igds-medidas.json) al abrir una lista.
const D = IGDS_DATOS.partidos;
const ORDEN = IGDS_DATOS.categorias;
const LEYENDA = [...ORDEN, 'dec'];
const LEGIBLES = new Set(['g', 'near', 'reg']);
const LISTA = PARTIDOS.filter((p) => D[p.id]);
const PREGUNTA = Object.fromEntries(T.preguntas.map((q) => [q.dim, q.pregunta]));
const DURACION = 600;
const VISIBLES = 8;

const dec1 = (v) => v.toFixed(1).replace('.', ',');
const minus = (s) => s.charAt(0).toLowerCase() + s.slice(1);
const enumerar = (xs) => (xs.length < 2 ? xs.join('') : `${xs.slice(0, -1).join(', ')} y ${xs.at(-1)}`);

// Medidas de una categoría y su valor de cada 100.
function valor(d, k) {
  const n = k === 'dec' ? ORDEN.reduce((s, c) => s + d.categorias[c][1], 0) : d.categorias[k][0];
  return { n, v: d.n ? (100 * n) / d.n : 0 };
}

// Reparto de las 100 casillas. Cada categoría ocupa un tramo continuo
// (0–100) y, dentro de él, las declarativas van al final. Una casilla puede
// partirse entre dos categorías: así 0,4 se ve como 0,4 de casilla y no
// desaparece al redondear. El punto va en las casillas que son declarativas
// en más de la mitad.
function casillas(d) {
  const tramos = [];
  let pos = 0;
  for (const k of ORDEN) {
    const [n, dec] = d.categorias[k];
    const v = (100 * n) / d.n;
    const vd = (100 * dec) / d.n;
    if (v > 0) {
      tramos.push({ k, a: pos, b: pos + v - vd, dec: false });
      if (vd > 0) tramos.push({ k, a: pos + v - vd, b: pos + v, dec: true });
    }
    pos += v;
  }
  return Array.from({ length: 100 }, (_, i) => {
    const partes = [];
    let enDec = 0;
    for (const t of tramos) {
      const o = Math.min(i + 1, t.b) - Math.max(i, t.a);
      if (o > 1e-6) {
        const ult = partes.at(-1);
        if (ult && ult.k === t.k) ult.w += o;
        else partes.push({ k: t.k, x: Math.max(i, t.a) - i, w: o });
        if (t.dec) enDec += o;
      }
    }
    return { partes, dec: enDec > 0.5 };
  });
}

// Nota calculada con los datos: dónde están o qué les falta.
function notaAuto(d, k) {
  const [n] = d.categorias[k] || [0];
  if (!n) return null;
  if (k === 'near') {
    return {
      etiqueta: 'Qué les falta',
      contenido: (
        <ul className="np-gar-falta">
          {Object.entries(d.falta).map(([dim, m]) => (
            <li key={dim}>
              <strong>{m}</strong> {PREGUNTA[dim]}
            </li>
          ))}
        </ul>
      ),
    };
  }
  if (k === 'g' || k === 'reg') {
    const areas = Object.entries(d.areas[k]);
    const top = areas.slice(0, 3).map(([id, m]) => `${minus(IGDS_AREAS[id])} (${m})`);
    const resto = areas.slice(3).reduce((s, [, m]) => s + m, 0);
    if (resto) top.push(`${resto} en ${plural(areas.length - 3, 'área más', 'áreas más')}`);
    return { etiqueta: 'Dónde están', contenido: <p>{`${enumerar(top)}.`}</p> };
  }
  return null;
}

// Textos de las medidas: se piden una vez, al abrir la primera lista.
let textos = null;
function cargarTextos() {
  if (!textos) {
    const url = urlDatos('igds-medidas.json');
    textos = url ? json(url) : Promise.reject(new Error('Sin carpeta de datos'));
    textos.catch(() => {
      textos = null;
    });
  }
  return textos;
}

// Nota emergente: un botón que despliega la explicación debajo, sin tapar
// nada (se lee igual con teclado, lector de pantalla y en móvil).
function NotaEmergente({ etiqueta, children }) {
  const [abierta, setAbierta] = useState(false);
  const id = useId();
  return (
    <div className={`np-gar-nota${abierta ? ' is-abierta' : ''}`}>
      <button
        type="button"
        className="np-gar-nota-btn"
        aria-expanded={abierta}
        aria-controls={id}
        onClick={() => setAbierta((a) => !a)}
        onKeyDown={(e) => {
          if (e.key === 'Escape' && abierta) {
            e.preventDefault();
            setAbierta(false);
          }
        }}
      >
        <span className="np-gar-nota-i" aria-hidden="true">
          i
        </span>
        {etiqueta}
      </button>
      <div id={id} className="np-gar-nota-txt" hidden={!abierta}>
        {children}
      </div>
    </div>
  );
}

function Muestra({ k }) {
  return (
    <svg className="np-gar-muestra" viewBox="0 0 20 20" aria-hidden="true" focusable="false">
      {k === 'reg' ? (
        <>
          <rect className="np-gar-reg" x="1" y="1" width="18" height="18" />
          <path className="np-gar-aspa" d="M5.5 5.5L14.5 14.5M14.5 5.5L5.5 14.5" />
        </>
      ) : k === 'dec' ? (
        <>
          <rect className="np-gar-otros" width="20" height="20" />
          <circle className="np-gar-punto" cx="10" cy="10" r="4" />
        </>
      ) : k === 'fuera' ? (
        <rect className="np-gar-fuera" x="0.5" y="0.5" width="19" height="19" />
      ) : (
        <rect className={`np-gar-${k}`} width="20" height="20" />
      )}
    </svg>
  );
}

const r2 = (v) => Math.round(v * 100) / 100;
function Rejilla({ celdas }) {
  return (
    <svg className="np-gar-rejilla" viewBox="0 0 109 109" aria-hidden="true" focusable="false">
      {celdas.map((c, i) => {
        const x = (i % 10) * 11;
        const y = Math.floor(i / 10) * 11;
        return (
          <g key={i} className="np-gar-cas" data-k={c.partes.map((p) => p.k).join(' ')} data-dec={c.dec ? 1 : 0}>
            {c.partes.map((p, j) => {
              const px = r2(x + p.x * 10);
              const w = r2(p.w * 10);
              if (p.k === 'reg')
                return (
                  <g key={j}>
                    <rect className="np-gar-reg" x={px + 0.5} y={y + 0.5} width={Math.max(0, w - 1)} height={9} />
                    {w > 5 && (
                      <path
                        className="np-gar-aspa"
                        d={`M${px + 2.4} ${y + 2.4}L${r2(px + w - 2.4)} ${y + 7.6}M${r2(px + w - 2.4)} ${y + 2.4}L${px + 2.4} ${y + 7.6}`}
                      />
                    )}
                  </g>
                );
              if (p.k === 'fuera')
                return <rect key={j} className="np-gar-fuera" x={px + 0.5} y={y + 0.5} width={Math.max(0, w - 1)} height={9} />;
              return <rect key={j} className={`np-gar-${p.k}`} x={px} y={y} width={w} height={10} />;
            })}
            {c.dec && <circle className="np-gar-punto" cx={x + 5} cy={y + 5} r={2.1} />}
          </g>
        );
      })}
    </svg>
  );
}

function Panel({ p, celdas, sel, hayTextos, leyendo, idLectura, onLeer }) {
  const d = D[p.id];
  const { n, v } = valor(d, sel);
  const nombre = T.categorias[sel].nombre;
  const auto = notaAuto(d, sel);
  const editorial = T.notas_partido?.[p.id]?.[sel];
  return (
    <li className="np-gar-panel" style={varsPartido(p)}>
      <p className="np-gar-cab">
        <LogoPartido partido={p} tam="s" carga="eager" />
        <span className="np-gar-sigla">{p.sigla}</span>
      </p>
      <Rejilla celdas={celdas} />
      <p className="np-gar-cifra">
        <span className="np-gar-num" data-v={v} aria-hidden="true" />
        <span className="np-gar-de" aria-hidden="true">
          de cada 100
        </span>
        <span className="np-sr">{`${p.sigla}, ${minus(nombre)}: ${dec1(v)} de cada 100 medidas, ${n} de ${d.n}.`}</span>
      </p>
      <p className="np-gar-n" aria-hidden="true">
        {n} de {d.n} medidas
      </p>
      {auto && (
        <NotaEmergente key={`${sel}-auto`} etiqueta={auto.etiqueta}>
          {auto.contenido}
        </NotaEmergente>
      )}
      {editorial && (
        <NotaEmergente key={`${sel}-ed`} etiqueta={n === 0 ? '¿Por qué 0?' : 'Para leerlo bien'}>
          <p>{editorial}</p>
        </NotaEmergente>
      )}
      {hayTextos && LEGIBLES.has(sel) && n > 0 && (
        <button
          type="button"
          className="np-gar-leer"
          aria-expanded={leyendo}
          aria-controls={leyendo ? idLectura : undefined}
          aria-label={`Leer ${n === 1 ? 'la medida' : `las ${n} medidas`} de ${p.sigla}: ${minus(nombre)}`}
          onClick={(e) => onLeer(p.id, e.currentTarget)}
        >
          {leyendo ? 'Leyéndolas abajo' : n === 1 ? 'Leer la medida' : `Leer las ${n}`}
        </button>
      )}
    </li>
  );
}

function Lectura({ lectura, id, seccionRef, tituloRef, onCerrar }) {
  const { pid, k } = lectura;
  const p = PARTIDOS.find((x) => x.id === pid);
  const { n } = valor(D[pid], k);
  const [estado, setEstado] = useState({ cargando: true });
  const [ver, setVer] = useState(VISIBLES);
  const [intento, setIntento] = useState(0);

  useEffect(() => {
    let vivo = true;
    setEstado({ cargando: true });
    setVer(VISIBLES);
    cargarTextos()
      .then((t) => vivo && setEstado({ lista: t?.[pid]?.[k] || [] }))
      .catch(() => vivo && setEstado({ error: true }));
    return () => {
      vivo = false;
    };
  }, [pid, k, intento]);

  const pdf = urlPrograma(p);
  const lista = estado.lista || [];
  return (
    <section id={id} className="np-gar-lectura" style={varsPartido(p)} aria-labelledby={`${id}-t`} ref={seccionRef}>
      <div className="np-gar-lectura-cab">
        <h4 id={`${id}-t`} className="np-gar-lectura-tit" tabIndex={-1} ref={tituloRef}>
          {p.sigla} · {T.categorias[k].nombre}
          <span>{plural(n, 'medida', 'medidas')}</span>
        </h4>
        <button type="button" className="np-btn" onClick={onCerrar}>
          Cerrar
        </button>
      </div>
      {estado.cargando && (
        <p className="np-gar-lectura-estado" role="status">
          Cargando las medidas…
        </p>
      )}
      {estado.error && (
        <div className="np-gar-lectura-estado" role="alert">
          <p>No hemos podido cargar las medidas. Comprueba tu conexión e inténtalo de nuevo.</p>
          <button type="button" className="np-btn" onClick={() => setIntento((x) => x + 1)}>
            Reintentar
          </button>
        </div>
      )}
      {lista.length > 0 && (
        <ol className="np-gar-lista">
          {lista.slice(0, ver).map(([pagina, area, sintesis, texto, falta], i) => (
            <li key={i}>
              <p className="np-gar-sintesis">{sintesis}</p>
              <blockquote className="np-gar-cita">«{texto}»</blockquote>
              <p className="np-gar-meta">
                {IGDS_AREAS[area]} ·{' '}
                {pdf ? (
                  <a
                    href={`${pdf}#page=${pagina}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label={`Página ${pagina} del programa de ${p.sigla} (se abre en otra pestaña)`}
                  >
                    Pág. {pagina}
                  </a>
                ) : (
                  `Pág. ${pagina}`
                )}
                {falta && (
                  <>
                    {' '}
                    · <span className="np-gar-le-falta">Le falta: {PREGUNTA[falta]}</span>
                  </>
                )}
              </p>
            </li>
          ))}
        </ol>
      )}
      {lista.length > ver && (
        <button type="button" className="np-btn np-gar-mas" onClick={() => setVer((x) => x + 20)}>
          Mostrar {Math.min(20, lista.length - ver)} más
        </button>
      )}
      <p className="np-nota">La síntesis es de ODESOCAN. Entre comillas, el texto literal del programa.</p>
    </section>
  );
}

function TablaDatos() {
  return (
    <details className="np-gar-datos">
      <summary>Ver los datos en una tabla</summary>
      <div className="np-gar-tabla-env">
        <table className="np-gar-tabla">
          <caption className="np-sr">
            De cada 100 medidas de cada programa, cuántas hay en cada categoría. Entre paréntesis, el número de
            medidas.
          </caption>
          <thead>
            <tr>
              <th scope="col">De cada 100 medidas</th>
              {LISTA.map((p) => (
                <th scope="col" key={p.id}>
                  {p.sigla}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {LEYENDA.map((k) => (
              <tr key={k}>
                <th scope="row">{T.categorias[k].nombre}</th>
                {LISTA.map((p) => {
                  const { n, v } = valor(D[p.id], k);
                  return (
                    <td key={p.id}>
                      {dec1(v)} <small>({n})</small>
                    </td>
                  );
                })}
              </tr>
            ))}
            <tr className="np-gar-total">
              <th scope="row">Total de medidas</th>
              {LISTA.map((p) => (
                <td key={p.id}>{D[p.id].n}</td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
      <p className="np-nota">Las declarativas se cuentan aparte: pueden estar en cualquiera de las otras categorías.</p>
    </details>
  );
}

export default function Garantias({ seccionRef, tituloRef }) {
  const [sel, setSel] = useState('g');
  const [lectura, setLectura] = useState(null);
  const panelesRef = useRef(null);
  const lecturaRef = useRef(null);
  const tituloLecturaRef = useRef(null);
  const abridorRef = useRef(null);
  const idLectura = useId();
  const celdas = useMemo(() => Object.fromEntries(LISTA.map((p) => [p.id, casillas(D[p.id])])), []);
  const hayTextos = Boolean(urlDatos('igds-medidas.json'));
  // La frase final solo vale si la exigibilidad es la que más falta en todos.
  const cierre = T.cierre_exi && LISTA.every((p) => D[p.id].limitante.join() === 'EXI');

  // Resaltar la categoría elegida y contar hasta su valor (como las barras del paso 2).
  useEffect(() => {
    const raiz = select(panelesRef.current);
    const quieto = sinMovimiento();
    raiz.selectAll('.np-gar-cas').each(function () {
      const activa = sel === 'dec' ? this.dataset.dec === '1' : this.dataset.k.split(' ').includes(sel);
      // Lo no elegido se atenúa sin desaparecer: el reparto completo sigue a la vista.
      const op = activa ? 1 : 0.3;
      const c = select(this);
      if (quieto) c.interrupt().style('opacity', op);
      else c.transition().duration(280).style('opacity', op);
    });
    raiz.selectAll('.np-gar-num').each(function () {
      const hasta = +this.dataset.v;
      const n = select(this);
      if (quieto || this.__v === undefined) {
        n.interrupt();
        this.__v = hasta;
        this.textContent = dec1(hasta);
        return;
      }
      const i = interpolateNumber(this.__v, hasta);
      n.transition()
        .duration(DURACION)
        .ease(easeCubicOut)
        .tween('text', () => (t) => {
          this.__v = i(t);
          this.textContent = dec1(t < 1 ? this.__v : hasta);
        });
    });
  }, [sel]);

  // Al abrir una lista: llevar hasta ella. Al cerrarla: devolver el foco.
  useEffect(() => {
    if (lectura) irA(lecturaRef.current, { foco: tituloLecturaRef.current });
  }, [lectura]);

  const elegir = (k) => {
    setSel(k);
    setLectura(null);
  };
  const leer = (pid, boton) => {
    abridorRef.current = boton;
    setLectura({ pid, k: sel });
  };
  const cerrar = () => {
    setLectura(null);
    abridorRef.current?.focus();
  };

  const cat = T.categorias[sel];
  const resumen = LISTA.map((p) => `${p.sigla} ${dec1(valor(D[p.id], sel).v)}`).join('; ');

  return (
    <section className="np-seccion np-gar" aria-labelledby="np-t-gar" ref={seccionRef}>
      <div className="np-gar-intro">
        <p className="np-kicker">
          {T.kicker}
          {IGDS_SELLO && <span className="np-gar-sello">{IGDS_SELLO}</span>}
        </p>
        <h3 id="np-t-gar" className="np-titulo-cartel" tabIndex={-1} ref={tituloRef}>
          {T.titulo} <span className="np-caja np-caja-teal">{T.titulo_caja}</span>
        </h3>
        <p className="np-texto">{T.entradilla}</p>
      </div>

      <ol className="np-gar-preguntas">
        {T.preguntas.map((q, i) => (
          <li key={q.dim} className="np-gar-pregunta">
            <span className="np-gar-pnum" aria-hidden="true">
              {i + 1}
            </span>
            <p className="np-gar-preg">{q.pregunta}</p>
            <p className="np-gar-breve">{q.breve}</p>
            <NotaEmergente etiqueta="Cuándo es sí">
              <p>{q.nota}</p>
            </NotaEmergente>
          </li>
        ))}
      </ol>
      <p className="np-gar-regla">{T.regla}</p>

      <div className="np-gar-mando">
        <p className="np-leyenda-tit" id={`${idLectura}-ley`}>
          Cómo leerlo · elige qué ver
        </p>
        <div className="np-gar-leyenda" role="group" aria-labelledby={`${idLectura}-ley`}>
          {LEYENDA.map((k) => (
            <button key={k} type="button" className="np-gar-ley" aria-pressed={sel === k} onClick={() => elegir(k)}>
              <Muestra k={k} />
              <span>
                <strong>{T.categorias[k].nombre}</strong>
                <span>{T.categorias[k].corto}</span>
              </span>
            </button>
          ))}
        </div>
        <p className="np-gar-color">
          Cada casilla es 1 de cada 100 medidas, en el color de su partido: cuanto más intenso, más cerca de garantizar
          el derecho.
        </p>
        <div className="np-gar-explica">
          <p aria-live="polite">
            <strong>{cat.nombre}.</strong> {cat.explica}
            <span className="np-sr"> De cada 100 medidas: {resumen}.</span>
          </p>
          <NotaEmergente key={sel} etiqueta="Cómo se cuenta">
            <p>{cat.nota}</p>
          </NotaEmergente>
        </div>
      </div>

      <ul className="np-gar-paneles" ref={panelesRef}>
        {LISTA.map((p) => (
          <Panel
            key={p.id}
            p={p}
            celdas={celdas[p.id]}
            sel={sel}
            hayTextos={hayTextos}
            leyendo={lectura?.pid === p.id}
            idLectura={idLectura}
            onLeer={leer}
          />
        ))}
      </ul>

      {lectura && (
        <Lectura
          lectura={lectura}
          id={idLectura}
          seccionRef={lecturaRef}
          tituloRef={tituloLecturaRef}
          onCerrar={cerrar}
        />
      )}

      {cierre && <p className="np-gar-cierre">{T.cierre_exi}</p>}

      <TablaDatos />

      <div className="np-gar-metodo">
        {T.metodo.map((t) => (
          <p key={t} className="np-nota">
            {t}
          </p>
        ))}
        {REPOSITORIO && (
          <p className="np-gar-fuentes">
            <a href={`${REPOSITORIO}/blob/main/docs/CRITERIOS-IGDS.md`} target="_blank" rel="noopener noreferrer">
              Libro de códigos
            </a>{' '}
            ·{' '}
            <a href={`${REPOSITORIO}/blob/main/datos/igds/igds-medidas.csv`} target="_blank" rel="noopener noreferrer">
              Todas las medidas codificadas
            </a>
          </p>
        )}
      </div>
    </section>
  );
}
