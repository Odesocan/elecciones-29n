import { useEffect, useRef, useState } from 'react';
import { easeCubicOut, scaleLinear, select } from 'd3';
import { FISCAL_POR_ID, PARTIDOS, RIESGO, TEMAS } from '../config.js';
import { enlaceArticulo } from '../datos.js';
import { plural, sinMovimiento, varsPartido } from '../util.js';
import LogoPartido from './LogoPartido.jsx';

// «La prueba de las cuentas» — la capa crítica de la herramienta.
// Pregunta, con la misma regla para todos: ¿dice cada programa cómo pagar
// lo que promete? Vocabulario pensado para todo el público:
//   RESTAN dinero a las cuentas públicas = ingresan menos o gastan más
//   SUMAN dinero a las cuentas públicas  = ingresan más o gastan menos
// Por partido:
//   · ratio «1 : x»: por cada medida que SUMA, cuántas RESTAN;
//   · barras D3 en dos bloques, «restan» y «suman», y en cada barra lo que
//     hacen las medidas («Suben el gasto», «Recortan gasto»…), en % del
//     programa (escala común a todos). Sin cruces fila × columna: así no se
//     puede leer «restan gasto» como si fuera un recorte.
//   · comprobaciones: si ponen importe, si hay memoria económica y si
//     prometen a la vez reducir el déficit o la deuda;
//   · las medidas literales de cada categoría, para que se pueda comprobar.
// Se cuentan medidas, no euros: es una prueba de coherencia, no de costes.

const fmt = (x) => {
  const r = x < 10 ? Math.round(x * 10) / 10 : Math.round(x);
  return String(r).replace('.', ',');
};
const BLOQUES = [
  { lado: 'resta', titulo: 'Restan dinero a las cuentas públicas', categorias: ['menos_ingresos', 'mas_gasto'] },
  { lado: 'suma', titulo: 'Suman dinero a las cuentas públicas', categorias: ['mas_ingresos', 'menos_gasto'] },
];

export default function CuentasProgramas({ idx, onElegirTema }) {
  const { cuentas } = idx;
  const ref = useRef(null);

  // D3: las barras crecen de izquierda a derecha.
  useEffect(() => {
    const x = scaleLinear().domain([0, Math.max(0.01, cuentas.maxPct)]).range([0, 100]);
    const quieto = sinMovimiento();
    select(ref.current)
      .selectAll('.np-bal-barra')
      .each(function () {
        const ancho = `${x(+this.dataset.v)}%`;
        const b = select(this);
        if (quieto) b.style('width', ancho);
        else b.style('width', '0%').transition().delay(150).duration(750).ease(easeCubicOut).style('width', ancho);
      });
  }, [cuentas]);

  return (
    <section className="np-seccion np-cuentas" aria-labelledby="np-t-cuentas" ref={ref}>
      <header className="np-cuentas-intro">
        <p className="np-kicker">La prueba de las cuentas</p>
        <h3 id="np-t-cuentas" className="np-titulo-cartel">
          Prometer es gratis. <span className="np-caja np-caja-teal">Pagarlo, no.</span>
        </h3>
        <p className="np-texto">
          Bajar impuestos es ingresar menos; subir el gasto, gastar más. Las dos cosas <strong>restan</strong> dinero
          a las cuentas públicas. Para que las cuentas cuadren, el programa tiene que decir de dónde saldrá ese dinero:
          con medidas que lo <strong>sumen</strong>, porque ingresan más por otro lado o gastan menos en otra cosa.
          Hemos contado, con la misma regla en todos los programas, cuántas medidas restan y cuántas suman.
        </p>
      </header>

      <p className="np-riesgo-leyenda">
        <Riesgo /> {RIESGO.regla} Es la misma regla para todos los programas.
      </p>

      <ul className="np-cuentas-lista" role="list">
        {PARTIDOS.map((p) => (
          <TarjetaCuentas key={p.id} partido={p} c={cuentas.porPartido.get(p.id)} onElegirTema={onElegirTema} />
        ))}
      </ul>

      <p className="np-nota np-cuentas-limite">
        <strong>Contamos medidas, no euros.</strong> Una sola rebaja del IRPF puede restar más dinero que diez medidas
        de gasto juntas, así que esto no calcula cuánto dinero está en juego. Es una prueba de coherencia: si cada
        programa dice cómo pagar lo que promete. No contamos como medida que suma la promesa de que algo «se pagará
        solo» con el crecimiento.
        Clasificación revisada por el equipo de ODESOCAN, con los mismos criterios para todos los programas (la de
        UPC, incorporada el 16 de noviembre, está pendiente de esa revisión).
      </p>
    </section>
  );
}

function TarjetaCuentas({ partido: p, c, onElegirTema }) {
  const [abierto, setAbierto] = useState(false);
  const idLista = `np-cuentas-${p.id}`;

  if (c?.pendiente)
    return (
      <li className="np-cuenta is-pendiente" style={varsPartido(p)}>
        <header className="np-cuenta-cab">
          <LogoPartido partido={p} tam="s" />
          <h4 className="np-cuenta-sigla">{p.sigla}</h4>
          <span className="np-cuenta-n">{plural(c.medidas, 'medida', 'medidas')}</span>
        </header>
        <p className="np-cuenta-pend">Estamos clasificando el impacto fiscal de sus medidas.</p>
      </li>
    );
  if (!c)
    return (
      <li className="np-cuenta is-pendiente" style={varsPartido(p)}>
        <header className="np-cuenta-cab">
          <LogoPartido partido={p} tam="s" />
          <h4 className="np-cuenta-sigla">{p.sigla}</h4>
        </header>
        <p className="np-cuenta-pend">Programa pendiente de publicar. Haremos la prueba en cuanto esté disponible.</p>
      </li>
    );

  const n = (id) => c.por[id].length;
  const pct = (id) => n(id) / c.medidas;
  const restan = c.restan.length;
  const suman = c.suman.length;
  const resumen =
    `${p.sigla}: ${plural(restan, 'medida resta', 'medidas restan')} dinero a las cuentas públicas ` +
    `(${n('menos_ingresos')} bajan impuestos o cotizaciones y ${n('mas_gasto')} suben el gasto) y ` +
    `${plural(suman, 'medida lo suma', 'medidas lo suman')} (${n('mas_ingresos')} suben ingresos y ` +
    `${n('menos_gasto')} recortan gasto). ` +
    (c.ratio === null
      ? 'Ninguna medida dice de dónde saldrá el dinero. '
      : `Por cada medida que suma, ${fmt(c.ratio)} restan. `) +
    `${c.conImporte.length} de ${restan} dicen en euros cuánto dinero suponen. ` +
    `${p.memoriaEconomica ? 'Incluye' : 'No incluye'} memoria económica.` +
    (c.riesgo ? ` Etiqueta: ${RIESGO.etiqueta}. ${RIESGO.regla}` : '');

  return (
    <li className="np-cuenta" style={varsPartido(p)}>
      <header className="np-cuenta-cab">
        <LogoPartido partido={p} tam="s" />
        <h4 className="np-cuenta-sigla">{p.sigla}</h4>
        {c.riesgo && <Riesgo />}
        <span className="np-cuenta-n">{plural(c.medidas, 'medida', 'medidas')}</span>
      </header>
      <p className="np-sr">{resumen}</p>

      <div className="np-cuenta-ratio" aria-hidden="true">
        {c.ratio === null ? (
          <>
            <span className="np-ratio-num is-sin">Sin contrapartidas</span>
            <span className="np-ratio-txt">
              {plural(restan, 'medida resta', 'medidas restan')} dinero y ninguna lo suma
            </span>
          </>
        ) : (
          <>
            <span className="np-ratio-num">1 : {fmt(c.ratio)}</span>
            <span className="np-ratio-txt">
              por cada medida que suma dinero a las cuentas públicas, {fmt(c.ratio)} lo restan
            </span>
          </>
        )}
      </div>

      {/* Dos bloques con barras etiquetadas · % del programa (escala común) */}
      <div className="np-flujos" aria-hidden="true">
        {BLOQUES.map((b) => (
          <div key={b.lado} className={`np-flujo is-${b.lado}`}>
            <p className="np-flujo-cab">
              <span>{b.titulo}</span>
              <strong>{plural(b.lado === 'resta' ? restan : suman, 'medida', 'medidas')}</strong>
            </p>
            {b.categorias.map((k) => (
              <div key={k} className="np-flujo-fila">
                <span className="np-flujo-nom">{FISCAL_POR_ID[k].nombre}</span>
                <span className="np-flujo-pista">
                  <span className="np-bal-barra" data-v={pct(k)} />
                </span>
                <span className="np-bal-n">{n(k)}</span>
              </div>
            ))}
          </div>
        ))}
      </div>

      <ul className="np-cuenta-checks" role="list">
        <li>
          <span>Dicen en euros cuánto dinero suponen</span>
          <strong className={c.conImporte.length ? '' : 'is-no'}>
            {c.conImporte.length} de {restan}
          </strong>
        </li>
        <li>
          <span>Memoria económica del programa</span>
          <strong className={p.memoriaEconomica ? '' : 'is-no'}>{p.memoriaEconomica ? 'Sí' : 'No'}</strong>
        </li>
        {n('consolidacion') > 0 && (
          <li>
            <span>Prometen además reducir déficit o deuda</span>
            <strong>{plural(n('consolidacion'), 'medida', 'medidas')}</strong>
          </li>
        )}
      </ul>

      <button
        type="button"
        className="np-btn np-btn-sec np-cuenta-ver"
        aria-expanded={abierto}
        aria-controls={idLista}
        onClick={() => setAbierto(!abierto)}
      >
        {abierto ? 'Ocultar las medidas' : `Ver las medidas de ${p.sigla}`}
      </button>
      {abierto && <ListaFiscal id={idLista} partido={p} c={c} onElegirTema={onElegirTema} />}
    </li>
  );
}

// Etiqueta roja de riesgo de viabilidad (regla en config/fiscal.json).
// El icono y el texto la distinguen del rojo corporativo de un partido.
function Riesgo() {
  return (
    <span className="np-riesgo" title={RIESGO.regla}>
      <span aria-hidden="true">⚠</span> {RIESGO.etiqueta}
    </span>
  );
}

// Las medidas de cada categoría, literales y con enlace al PDF.
function ListaFiscal({ id, partido, c, onElegirTema }) {
  const grupos = ['menos_ingresos', 'mas_gasto', 'mas_ingresos', 'menos_gasto', 'consolidacion'].filter(
    (k) => c.por[k].length,
  );
  return (
    <div className="np-cuenta-lista" id={id}>
      {grupos.map((k) => (
        <details key={k} className={`np-fgrupo is-${FISCAL_POR_ID[k].lado}`}>
          <summary>
            {FISCAL_POR_ID[k].nombre} <span>({c.por[k].length})</span>
          </summary>
          <ul role="list">
            {c.por[k].map((a) => {
              const href = enlaceArticulo(a, partido);
              const tema = TEMAS.find((t) => t.id === a.temas[0]);
              const texto = a.titulo || (a.texto.length > 160 ? `${a.texto.slice(0, 157)}…` : a.texto);
              return (
                <li key={a.id}>
                  <p className="np-art-meta">
                    {[a.ref, a.pagina && `Pág. ${a.pagina}`].filter(Boolean).join(' · ')}
                    {a.fiscal.includes('importe') && <span className="np-fimporte"> · con importe</span>}
                  </p>
                  <p className="np-fmedida">{texto}</p>
                  <p className="np-fmedida-acc">
                    {tema && (
                      <button type="button" className="np-tag" onClick={() => onElegirTema(tema.id)}>
                        {tema.nombre}
                      </button>
                    )}
                    {href && (
                      <a className="np-enlace-txt" href={href} target="_blank" rel="noopener">
                        Ver en el programa<span className="np-sr"> (PDF, pestaña nueva)</span> ↗
                      </a>
                    )}
                  </p>
                </li>
              );
            })}
          </ul>
        </details>
      ))}
    </div>
  );
}
