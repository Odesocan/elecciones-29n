import { forwardRef, useEffect, useRef, useState } from 'react';
import { easeCubicOut, scaleSqrt, select } from 'd3';
import { PARTIDOS, TEMAS } from '../config.js';
import { pad, plural, sinMovimiento, varsPartido } from '../util.js';

// Paso 1: las temáticas (config/temas.json). Cada botón lleva una mini-gráfica D3 de
// 5 barritas (una por programa, en orden alfabético): el PESO del tema en
// cada programa (% de sus medidas), para ver de un vistazo quién habla de qué
// sin que gane siempre el programa más largo. Es un apoyo visual: aria-hidden, porque
// el detalle accesible está en el mapa y en cada tema.
//
// En móvil (contenedor de menos de 560 px) la lista va plegada tras un botón
// desplegable para que los 18 temas no ocupen varias pantallas; en tableta y
// escritorio el botón no se ve y la rejilla está siempre abierta (estilos.css).
// «abrir» es un contador que sube App cuando se pulsa «Otro tema»: abre la
// lista en el mismo render, para que el foco pueda ir al tema que se leía.
const SelectorTemas = forwardRef(function SelectorTemas({ idx, tema, leidos, onElegir, abrir = 0 }, ref) {
  const listaRef = useRef(null);
  const n = leidos.size;
  const [abierto, setAbierto] = useState(false);
  const [abrirVisto, setAbrirVisto] = useState(abrir);
  if (abrir !== abrirVisto) {
    setAbrirVisto(abrir);
    setAbierto(true);
  }
  const actual = TEMAS.find((t) => t.id === tema);
  const elegir = (id) => {
    setAbierto(false);
    onElegir(id);
  };

  useEffect(() => {
    if (!idx) return;
    // Escala raíz, como las burbujas del mapa: con un máximo del ~40 % y casi
    // todos los temas por debajo del 10 %, la lineal dejaba barritas de 3-4 px
    // indistinguibles. Es un índice visual; las cifras están en el mapa y en cada tema.
    const y = scaleSqrt().domain([0, Math.max(0.01, idx.maxCuota)]).range([0, 100]);
    const quieto = sinMovimiento();
    select(listaRef.current)
      .selectAll('.np-mini-b')
      .each(function () {
        const v = +this.dataset.v;
        const alto = v === 0 ? '8%' : `${Math.max(14, y(v))}%`;
        const b = select(this).classed('is-cero', v === 0);
        if (quieto) b.style('height', alto);
        else
          b.style('height', '0%')
            .transition()
            .delay(+this.dataset.i * 25 + +this.dataset.j * 40)
            .duration(550)
            .ease(easeCubicOut)
            .style('height', alto);
      });
  }, [idx]);

  return (
    <section className={`np-seccion np-temas-sec${abierto ? ' is-abierto' : ''}`} aria-labelledby="np-t-temas" ref={ref}>
      <div className="np-cab-sec">
        <div>
          <p className="np-kicker">Paso 1 · Qué quieres leer</p>
          <h3 id="np-t-temas" className="np-titulo-cartel">
            Elige un tema
          </h3>
        </div>
        <div className="np-cab-lateral">
          <div className="np-progreso">
            <p>
              {n === 0
                ? 'Aún no has abierto ningún tema'
                : n === TEMAS.length
                  ? `Has leído los ${TEMAS.length} temas. No se lo esperaban.`
                  : `Has leído ${n} de ${TEMAS.length} temas`}
            </p>
            <span className="np-progreso-barra" aria-hidden="true">
              <span style={{ width: `${(n / TEMAS.length) * 100}%` }} />
            </span>
          </div>
          <p className="np-mini-leyenda" aria-hidden="true">
            <span className="np-mini-leyenda-tit">Barritas = % del programa de</span>
            {PARTIDOS.map((p) => (
              <span
                key={p.id}
                className={`np-muestra${idx && !idx.disponibles.has(p.id) ? ' is-pendiente' : ''}`}
                style={varsPartido(p)}
              >
                {p.sigla}
              </span>
            ))}
            {idx && idx.disponibles.size < PARTIDOS.length && (
              <span className="np-mini-leyenda-pend">(tachado: programa aún no publicado)</span>
            )}
          </p>
        </div>
      </div>

      <button
        type="button"
        className="np-temas-toggle"
        aria-expanded={abierto}
        aria-controls="np-lista-temas"
        onClick={() => setAbierto((a) => !a)}
      >
        <span className="np-temas-toggle-txt">
          <span className="np-temas-toggle-etq">{actual ? 'Tema que lees' : `${TEMAS.length} temas`}</span>
          <span className="np-temas-toggle-nombre">
            {actual ? actual.nombre : 'Elige uno'}
          </span>
        </span>
        <span className="np-temas-toggle-accion">{abierto ? 'Cerrar' : actual ? 'Cambiar' : 'Ver temas'}</span>
        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
          <path d="M6 9l6 6 6-6" fill="none" stroke="currentColor" strokeWidth="2.5" />
        </svg>
      </button>

      <ul className="np-temas" id="np-lista-temas" role="list" ref={listaRef}>
        {TEMAS.map((t, i) => {
          const activo = t.id === tema;
          const leido = leidos.has(t.id);
          const total = idx ? idx.totalTema.get(t.id) : null;
          return (
            <li key={t.id}>
              <button
                type="button"
                className="np-tema"
                aria-pressed={activo}
                onClick={() => elegir(t.id)}
                aria-label={`${t.nombre}${total === null ? '' : `, ${plural(total, 'artículo', 'artículos')}`}${leido && !activo ? ', ya leído' : ''}`}
              >
                <span className="np-tema-top">
                  <span className="np-tema-num">{pad(i + 1)}</span>
                  {activo ? (
                    <span className="np-tema-estado">Leyendo</span>
                  ) : (
                    leido && <span className="np-tema-estado">✓ Leído</span>
                  )}
                </span>
                <span className="np-tema-nombre">{t.nombre}</span>
                <span className="np-tema-pie">
                  <span className="np-mini">
                    {PARTIDOS.map((p, j) => (
                      <span
                        key={p.id}
                        className="np-mini-b"
                        style={varsPartido(p)}
                        data-v={idx ? idx.cuota.get(t.id).get(p.id) || 0 : 0}
                        data-i={i}
                        data-j={j}
                      />
                    ))}
                  </span>
                  <span className="np-tema-total">{total === null ? '…' : plural(total, 'artículo', 'artículos')}</span>
                </span>
              </button>
            </li>
          );
        })}
      </ul>
    </section>
  );
});

export default SelectorTemas;
