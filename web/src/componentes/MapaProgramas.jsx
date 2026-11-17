import { useEffect, useRef, useState } from 'react';
import { easeCubicOut, scaleSqrt, select, ticks } from 'd3';
import { PARTIDOS, TEMAS } from '../config.js';
import { pad, pct, pctNum, pctVoz, plural, sinMovimiento, varsPartido } from '../util.js';

// «En qué temas ponen el foco» — matriz D3 tema × partido.
// · Área del círculo ∝ PESO del tema en el programa: % de sus medidas que lo
//   tratan (escala sqrt), en el color del partido. Así se comparan programas
//   de distinta extensión. Anillo discontinuo = ninguno localizado.
// · Pulsar el NOMBRE del tema abre el tema; pulsar una BURBUJA abre el tema
//   y lleva al bloque de ese partido (con el resto de partidos a la vista).
// · Teclado: una sola parada de tabulador; las flechas recorren la matriz
//   (patrón «roving tabindex»), Inicio/Fin van al principio/fin de la fila.
// · Las siglas de la cabecera resaltan la columna de un partido.
const R_MAX = 15;
const R_MIN = 3.5;
// Escala de área (sqrt) desde 0, con un radio mínimo para que un tema con
// una sola medida (<1 %) siga viéndose.
const escalaRadio = (maxCuota) => {
  const s = scaleSqrt().domain([0, Math.max(0.01, maxCuota)]).range([0, R_MAX]).clamp(true);
  return (v) => (v > 0 ? Math.max(R_MIN, s(v)) : 0);
};
const COLS = PARTIDOS.length + 1; // nombre del tema + 5 partidos

export default function MapaProgramas({ idx, temaActual, onElegir, onElegirPartido, seccionRef, tituloRef }) {
  const tablaRef = useRef(null);
  const [resaltado, setResaltado] = useState(null);
  const [activo, setActivo] = useState({ f: 0, c: 0 });

  // Entrada: los círculos crecen fila a fila.
  useEffect(() => {
    const radio = escalaRadio(idx.maxCuota);
    const quieto = sinMovimiento();
    select(tablaRef.current)
      .selectAll('circle.np-punto')
      .each(function () {
        const c = select(this);
        const r = radio(+this.dataset.v);
        if (quieto) return c.attr('r', r);
        c.interrupt('entrada')
          .attr('r', 0)
          .transition('entrada')
          .delay(+this.dataset.fila * 45 + +this.dataset.col * 20)
          .duration(700)
          .ease(easeCubicOut)
          .attr('r', r);
      });
  }, [idx]);

  // Resaltar un partido: el resto de columnas se apaga.
  useEffect(() => {
    const quieto = sinMovimiento();
    select(tablaRef.current)
      .selectAll('.np-mapa-celda svg')
      .each(function () {
        const op = resaltado === null || +this.dataset.col === resaltado ? 1 : 0.14;
        const s = select(this);
        if (quieto) s.style('opacity', op);
        else s.transition('resaltar').duration(280).style('opacity', op);
      });
  }, [resaltado]);

  const mover = (e) => {
    // Posición del elemento con foco (no del estado: puede ir un render por detrás)
    const f = Number(e.target.dataset.f ?? activo.f);
    const c = Number(e.target.dataset.c ?? activo.c);
    const destino = {
      ArrowRight: { f, c: Math.min(COLS - 1, c + 1) },
      ArrowLeft: { f, c: Math.max(0, c - 1) },
      ArrowDown: { f: Math.min(TEMAS.length - 1, f + 1), c },
      ArrowUp: { f: Math.max(0, f - 1), c },
      Home: { f, c: 0 },
      End: { f, c: COLS - 1 },
    }[e.key];
    if (!destino) return;
    e.preventDefault();
    setActivo(destino);
    tablaRef.current.querySelector(`[data-f="${destino.f}"][data-c="${destino.c}"]`)?.focus();
  };
  const tab = (f, c) => (activo.f === f && activo.c === c ? 0 : -1);

  const radioLeyenda = escalaRadio(idx.maxCuota);
  // Muestras redondas (10 %, 20 %, 30 %…) por debajo del máximo real.
  const muestras = ticks(0, idx.maxCuota * 100, 3)
    .filter((v) => v > 0)
    .map((v) => v / 100);

  const pResaltado = resaltado === null ? null : PARTIDOS[resaltado];
  const resumen = !pResaltado
    ? ''
    : !idx.disponibles.has(pResaltado.id)
      ? `${pResaltado.sigla}: programa aún no publicado.`
      : `${pResaltado.sigla} · lo que más pesa en su programa: ${idx.destacados
          .get(pResaltado.id)
          .map((t) => `${TEMAS.find((x) => x.id === t).nombre} (${pct(idx.cuota.get(t).get(pResaltado.id))})`)
          .join(', ')
          .replace(/, ([^,]*)$/, ' y $1')}.`;

  return (
    <section className="np-seccion np-mapa" aria-labelledby="np-t-mapa" ref={seccionRef}>
      <div className="np-mapa-intro">
        <p className="np-kicker">El mapa de los programas</p>
        <h3 id="np-t-mapa" className="np-titulo-cartel" tabIndex={-1} ref={tituloRef}>
          En qué temas ponen el <span className="np-subrayado">foco</span>
        </h3>
        <p className="np-texto">
          Qué parte de su programa dedica cada partido a cada tema. Lo medimos en <strong>porcentaje</strong> para
          poder comparar programas largos y cortos. <strong>Pulsa una burbuja</strong> para ir a lo que dice ese
          partido, o el nombre del tema para verlos todos.
        </p>

        <div className="np-leyenda" aria-hidden="true">
          <p className="np-leyenda-tit">% de las medidas de cada programa</p>
          <div className="np-leyenda-items">
            {muestras.map((v) => (
              <span key={v} className="np-leyenda-item">
                <svg viewBox="-16 -16 32 32" focusable="false">
                  <circle className="np-punto np-punto-neutro" r={radioLeyenda(v)} />
                </svg>
                {pct(v)}
              </span>
            ))}
            <span className="np-leyenda-item">
              <svg viewBox="-16 -16 32 32" focusable="false">
                <circle className="np-punto-cero" r="6" />
              </svg>
              Ninguno localizado
            </span>
            {idx.disponibles.size < PARTIDOS.length && (
              <span className="np-leyenda-item">
                <svg viewBox="-16 -16 32 32" focusable="false">
                  <line className="np-punto-pend" x1="-5" y1="0" x2="5" y2="0" />
                </svg>
                Programa aún no publicado
              </span>
            )}
          </div>
        </div>

        <p className="np-nota">
          Una medida puede tratar hasta tres temas, así que los porcentajes de un programa suman más de 100. Más peso
          no significa mejores propuestas: significa más espacio. Lo que dicen solo se sabe leyendo.
        </p>
      </div>

      <div className="np-mapa-tabla" ref={tablaRef}>
        {/* Al resaltar un partido: sus tres temas con más peso */}
        <p className={`np-mapa-resumen${pResaltado ? ' is-activo' : ''}`} role="status" style={pResaltado ? varsPartido(pResaltado) : undefined}>
          {resumen || 'Pulsa unas siglas para ver qué temas pesan más en ese programa.'}
        </p>
        <div className="np-mapa-cab" role="group" aria-label="Resaltar un partido en el mapa">
          <span className="np-mapa-cab-tema" aria-hidden="true">
            Tema
          </span>
          {PARTIDOS.map((p, j) => (
            <button
              type="button"
              key={p.id}
              className="np-mapa-sigla"
              style={varsPartido(p)}
              aria-pressed={resaltado === j}
              aria-label={`Resaltar ${p.sigla}${idx.disponibles.has(p.id) ? '' : ' (programa pendiente de publicar)'}`}
              onClick={() => setResaltado(resaltado === j ? null : j)}
            >
              {p.sigla}
              {!idx.disponibles.has(p.id) && <small className="np-mapa-pend">pendiente</small>}
            </button>
          ))}
          <span aria-hidden="true" title="Peso medio entre los programas publicados">
            Media
          </span>
        </div>

        <p className="np-sr">Usa las flechas para moverte por el mapa.</p>

        <ul role="list" onKeyDown={mover}>
          {TEMAS.map((t, i) => {
            const porPartido = idx.indice.get(t.id);
            const actual = t.id === temaActual;
            const total = idx.totalTema.get(t.id);
            const media = idx.mediaTema.get(t.id);
            return (
              <li key={t.id} className={`np-mapa-fila${actual ? ' is-actual' : ''}`}>
                <button
                  type="button"
                  className="np-mapa-tema"
                  data-f={i}
                  data-c={0}
                  tabIndex={tab(i, 0)}
                  onFocus={() => setActivo({ f: i, c: 0 })}
                  onClick={() => onElegir(t.id)}
                  aria-current={actual ? 'true' : undefined}
                  aria-label={`${t.nombre}: ${media === null ? '' : `de media, ${pctVoz(media)} de cada programa publicado; `}${plural(total, 'artículo', 'artículos')} en total. Ver el tema${actual ? ' (lo estás leyendo)' : ''}.`}
                >
                  <span className="np-mapa-num" aria-hidden="true">
                    {pad(i + 1)}
                  </span>
                  <span>{t.nombre}</span>
                </button>
                {PARTIDOS.map((p, j) => {
                  const n = porPartido.get(p.id).length;
                  const pendiente = !idx.disponibles.has(p.id);
                  const v = idx.cuota.get(t.id).get(p.id);
                  const totalP = idx.totalPartido.get(p.id);
                  return (
                    <button
                      type="button"
                      key={p.id}
                      className={`np-mapa-celda${resaltado === j ? ' is-resaltada' : ''}`}
                      style={varsPartido(p)}
                      data-f={i}
                      data-c={j + 1}
                      tabIndex={tab(i, j + 1)}
                      onFocus={() => setActivo({ f: i, c: j + 1 })}
                      onClick={() => onElegirPartido(t.id, p.id)}
                      aria-label={
                        pendiente
                          ? `${p.sigla} en ${t.nombre}: programa aún no publicado.`
                          : n === 0
                            ? `${p.sigla} en ${t.nombre}: ninguna de sus ${totalP} medidas. Ir a su bloque.`
                            : `${p.sigla} en ${t.nombre}: ${pctVoz(v)} de su programa, ${n} de ${totalP} medidas. Ir a sus artículos.`
                      }
                    >
                      <svg viewBox="-16 -16 32 32" focusable="false" aria-hidden="true" data-col={j}>
                        {pendiente ? (
                          <line className="np-punto-pend" x1="-5" y1="0" x2="5" y2="0" />
                        ) : n === 0 ? (
                          <circle className="np-punto-cero" r="6" />
                        ) : (
                          <circle className="np-punto" r="0" data-v={v} data-fila={i} data-col={j} />
                        )}
                      </svg>
                      <span className="np-mapa-n" aria-hidden="true">
                        {pendiente ? '' : (
                          <span>
                            {pctNum(v)}
                            <small>%</small>
                          </span>
                        )}
                      </span>
                    </button>
                  );
                })}
                <span className="np-mapa-total" aria-hidden="true">
                  {media === null ? '—' : (
                    <>
                      {pctNum(media)}
                      <small>%</small>
                    </>
                  )}
                </span>
              </li>
            );
          })}
        </ul>
      </div>
    </section>
  );
}
