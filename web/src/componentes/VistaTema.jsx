import { useEffect, useRef, useState } from 'react';
import { easeCubicOut, interpolateNumber, scaleLinear, select } from 'd3';
import { ARTICULOS_VISIBLES, ENLACES, FECHA_COMPROBACION, PARTIDOS, TEMAS, urlPrograma } from '../config.js';
import { enlaceArticulo } from '../datos.js';
import { compartir, irA, ordinal, pad, pct, pctNum, pctVoz, plural, sinMovimiento, varsPartido } from '../util.js';
import LogoPartido from './LogoPartido.jsx';

export default function VistaTema({
  tema,
  idx,
  partidos,
  onTogglePartido,
  onTodos,
  onMostrarPartido,
  onElegirTema,
  onVerMapa,
  onCambiarTema,
  seccionRef,
  tituloRef,
  enfoque,
}) {
  const i = TEMAS.findIndex((t) => t.id === tema);
  const t = TEMAS[i];
  const porPartido = idx.indice.get(tema);
  const visibles = partidos.size ? PARTIDOS.filter((p) => partidos.has(p.id)) : PARTIDOS;
  const total = idx.totalTema.get(tema);
  const conArticulos = PARTIDOS.filter((p) => porPartido.get(p.id).length > 0).length;
  const publicados = PARTIDOS.filter((p) => idx.disponibles.has(p.id)).length;
  const pendientes = PARTIDOS.length - publicados;
  const anterior = TEMAS[i - 1];
  const siguiente = TEMAS[i + 1];
  // Con 2 o 3 partidos elegidos, en pantallas anchas se leen en columnas.
  const comparar = visibles.length >= 2 && visibles.length <= 3;

  const grupos = useRef(new Map());
  const [destino, setDestino] = useState(null);
  const [aviso, setAviso] = useState('');

  useEffect(() => {
    if (!destino) return;
    const el = grupos.current.get(destino);
    irA(el, { foco: el?.querySelector('h4') });
    setDestino(null);
  }, [destino]);

  // Llegada desde una burbuja del mapa: ir al partido y destacarlo un momento.
  const [destacado, setDestacado] = useState(null);
  useEffect(() => {
    if (!enfoque) return;
    setDestino(enfoque.partido);
    setDestacado(enfoque.partido);
    const t = setTimeout(() => setDestacado(null), 1800);
    return () => clearTimeout(t);
  }, [enfoque]);

  const irAPartido = (id) => {
    onMostrarPartido(id);
    setDestino(id);
  };

  const compartirTema = async () => {
    const r = await compartir({
      titulo: `${t.nombre} · Lee los programas · 29N`,
      texto: `Qué proponen los programas electorales sobre ${t.nombre.toLowerCase()}. Léelos antes de votar.`,
      url: window.location.href,
    });
    if (r === 'copiado') {
      setAviso('Enlace copiado');
      setTimeout(() => setAviso(''), 2500);
    }
  };

  return (
    <section className="np-seccion np-vista" aria-labelledby="np-t-vista" ref={seccionRef}>
      <header className="np-vista-cab">
        <p className="np-kicker">
          Tema {pad(i + 1)} de {TEMAS.length}
        </p>
        <h3 id="np-t-vista" className="np-vista-titulo" tabIndex={-1} ref={tituloRef}>
          {t.nombre}
        </h3>
        <p className="np-vista-alcance">{t.alcance}</p>
        <p className="np-dateline">
          {plural(total, 'artículo', 'artículos')} · {conArticulos} de {plural(publicados, 'programa publicado', 'programas publicados')}{' '}
          {conArticulos === 1 ? 'habla' : 'hablan'} de ello
          {pendientes > 0 && ` · ${pendientes} ${pendientes === 1 ? 'pendiente' : 'pendientes'} de publicar`}
        </p>
        <div className="np-vista-acciones">
          <button type="button" className="np-btn np-btn-sec" onClick={onCambiarTema}>
            <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
              <path d="M12 5l-7 7h4.5v7h5v-7H19z" fill="currentColor" />
            </svg>
            Otro tema
          </button>
          <button type="button" className="np-btn np-btn-sec" onClick={compartirTema}>
            <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
              <path
                d="M18 16a3 3 0 0 0-2.4 1.2l-6.7-3.4a3 3 0 0 0 0-1.6l6.7-3.4A3 3 0 1 0 15 7l-6.7 3.4a3 3 0 1 0 0 3.2L15 17a3 3 0 1 0 3-1z"
                fill="currentColor"
              />
            </svg>
            Compartir este tema
          </button>
          <span className="np-aviso-copia" role="status">
            {aviso}
          </span>
        </div>
      </header>

      <FiltroPartidos partidos={partidos} onToggle={onTogglePartido} onTodos={onTodos} />

      <BarrasPartidos tema={t} idx={idx} partidos={partidos} onIr={irAPartido} />

      {comparar && (
        <p className="np-comparando">
          <span aria-hidden="true">⇆</span> Comparando{' '}
          {visibles
            .map((p) => p.sigla)
            .join(', ')
            .replace(/, ([^,]*)$/, ' y $1')}{' '}
          en paralelo
        </p>
      )}

      <div
        className={`np-grupos${comparar ? ' is-comparar' : ''}`}
        style={comparar ? { '--n': visibles.length } : undefined}
        key={tema}
      >
        {visibles.map((p) => (
          <GrupoPartido
            key={p.id}
            partido={p}
            tema={t}
            articulos={porPartido.get(p.id)}
            peso={idx.cuota.get(tema).get(p.id)}
            totalPartido={idx.totalPartido.get(p.id)}
            puesto={idx.puesto.get(p.id)?.get(tema)}
            registrar={(el) => (el ? grupos.current.set(p.id, el) : grupos.current.delete(p.id))}
            onElegirTema={onElegirTema}
            destacado={destacado === p.id}
            disponible={idx.disponibles.has(p.id)}
          />
        ))}
      </div>

      <nav className="np-pasos" aria-label="Seguir leyendo">
        {anterior ? (
          <button type="button" className="np-paso-btn" onClick={() => onElegirTema(anterior.id)}>
            <span className="np-paso-dir">← Tema anterior</span>
            <span className="np-paso-nombre">{anterior.nombre}</span>
          </button>
        ) : (
          <span />
        )}
        {siguiente && (
          <button type="button" className="np-paso-btn np-paso-sig" onClick={() => onElegirTema(siguiente.id)}>
            <span className="np-paso-dir">Siguiente tema →</span>
            <span className="np-paso-nombre">{siguiente.nombre}</span>
          </button>
        )}
      </nav>
      <p className="np-volver-mapa">
        <button type="button" className="np-enlace-txt" onClick={onVerMapa}>
          Ver el mapa de todos los temas ↓
        </button>
      </p>
    </section>
  );
}

// ── Paso 2: filtro por partido (multiselección, «filtrar hacia dentro») ──
function FiltroPartidos({ partidos, onToggle, onTodos }) {
  const todos = partidos.size === 0;
  const Check = () => (
    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
      <path d="M9 16.2l-3.5-3.5L4 14.2l5 5 11-11-1.5-1.5z" fill="currentColor" />
    </svg>
  );
  return (
    <div className="np-filtro" role="group" aria-labelledby="np-t-filtro">
      <p id="np-t-filtro" className="np-kicker">
        Paso 2 · Filtra por partido{' '}
        <span className="np-kicker-sub">(elige 2 o 3 para leerlos en paralelo)</span>
      </p>
      <div className="np-chips">
        <button type="button" className="np-chip" aria-pressed={todos} onClick={onTodos}>
          <Check />
          Todos
        </button>
        {PARTIDOS.map((p) => (
          <button
            type="button"
            key={p.id}
            className="np-chip np-chip-partido"
            style={varsPartido(p)}
            aria-pressed={partidos.has(p.id)}
            onClick={() => onToggle(p.id)}
            title={p.nombre !== p.sigla ? p.nombre : undefined}
          >
            <span className="np-chip-punto" aria-hidden="true" />
            <Check />
            {p.sigla}
          </button>
        ))}
      </div>
    </div>
  );
}

// ── D3: barras «qué peso tiene el tema en cada programa» ──
// Peso = % de las medidas del programa que tratan el tema: compara
// programas de distinta extensión. Escala común a todos los temas →
// al cambiar de tema la animación muestra diferencias reales.
// Cada barra arranca en el logo del partido (origen común, para que las
// longitudes se puedan comparar) y lleva su porcentaje en la punta. El
// porcentaje cuenta del valor anterior al nuevo mientras crece la barra.
const DURACION = 600;
function BarrasPartidos({ tema, idx, partidos, onIr }) {
  const ref = useRef(null);
  const porPartido = idx.indice.get(tema.id);
  const cuotas = idx.cuota.get(tema.id);
  useEffect(() => {
    const x = scaleLinear().domain([0, Math.max(0.01, idx.maxCuota)]).range([0, 100]);
    const quieto = sinMovimiento();
    const raiz = select(ref.current);
    raiz.selectAll('.np-barra').each(function () {
      const ancho = `${x(+this.dataset.v)}%`;
      const b = select(this);
      if (quieto) b.interrupt().style('width', ancho);
      else b.transition().duration(DURACION).ease(easeCubicOut).style('width', ancho);
    });
    // Contador: D3 es dueño del texto de .np-barra-num (React no le pone hijos).
    // Si se cambia de tema a media animación, sigue desde el valor que se ve.
    raiz.selectAll('.np-barra-num').each(function () {
      const hasta = +this.dataset.v;
      const n = select(this);
      if (quieto) {
        n.interrupt();
        this.__v = hasta;
        this.textContent = pctNum(hasta);
        return;
      }
      const i = interpolateNumber(this.__v ?? 0, hasta);
      n.transition()
        .duration(DURACION)
        .ease(easeCubicOut)
        .tween('text', () => (t) => {
          this.__v = i(t);
          this.textContent = t < 1 ? String(Math.round(this.__v * 100)) : pctNum(hasta);
        });
    });
  }, [tema, idx]);

  return (
    <div className="np-barras" ref={ref}>
      <p className="np-kicker">Qué parte de cada programa trata de {tema.nombre.toLowerCase()}</p>
      <ul role="list">
        {PARTIDOS.map((p) => {
          const n = porPartido.get(p.id).length;
          const v = cuotas.get(p.id) || 0;
          const total = idx.totalPartido.get(p.id);
          const oculto = partidos.size > 0 && !partidos.has(p.id);
          const pendiente = !idx.disponibles.has(p.id);
          return (
            <li key={p.id}>
              <button
                type="button"
                className={`np-barra-fila${oculto ? ' is-oculto' : ''}`}
                style={varsPartido(p)}
                onClick={() => onIr(p.id)}
                aria-label={
                  pendiente
                    ? `${p.sigla}: programa aún no publicado.`
                    : `${p.sigla}: ${pctVoz(v)} de su programa, ${n} de sus ${total} medidas. Ir a sus artículos${oculto ? ' (ahora filtrado)' : ''}.`
                }
              >
                <span className="np-barra-pista">
                  <span className="np-barra-chip">
                    <LogoPartido partido={p} tam="b" rotulo={p.sigla} carga="eager" />
                  </span>
                  <span className={`np-barra-zona${pendiente ? ' is-pendiente' : ''}`}>
                    {pendiente ? (
                      <span className="np-barra-pend">Pendiente de publicar</span>
                    ) : (
                      <span className="np-barra" data-v={v}>
                        <span className="np-barra-n" aria-hidden="true">
                          <span className="np-barra-num" data-v={v} />
                          <span className="np-barra-pc">{'\u202f%'}</span>
                        </span>
                      </span>
                    )}
                  </span>
                </span>
                {!pendiente && (
                  <span className="np-barra-base" aria-hidden="true">
                    {n} de {total} medidas
                  </span>
                )}
              </button>
            </li>
          );
        })}
      </ul>
      <p className="np-nota">
        En porcentaje sobre todas las medidas de cada programa, para comparar programas largos y cortos. Más peso no
        significa mejores propuestas. Léelos.
      </p>
    </div>
  );
}

// ── Artículos de un partido para el tema elegido ──
function GrupoPartido({ partido, tema, articulos, peso, totalPartido, puesto, registrar, onElegirTema, destacado, disponible }) {
  const [todos, setTodos] = useState(false);
  const n = articulos.length;
  const lista = todos ? articulos : articulos.slice(0, ARTICULOS_VISIBLES);
  const idTitulo = `np-g-${partido.id}`;

  return (
    <section
      className={`np-grupo${destacado ? ' is-destacado' : ''}`}
      style={varsPartido(partido)}
      ref={registrar}
      aria-labelledby={idTitulo}
    >
      {/* Barra fija al hacer scroll: siempre sabes de quién es lo que lees.
          Solo el logo: la sigla al lado era redundante, y el nombre completo va
          justo debajo. La sigla queda en el título para lectores de pantalla y,
          si el logo no carga, escrita en su lugar. */}
      <header className="np-grupo-cab">
        <h4 id={idTitulo} className="np-grupo-titulo" tabIndex={-1}>
          <LogoPartido partido={partido} rotulo={partido.sigla} />
          <span className="np-sr">{partido.sigla}</span>
        </h4>
        <p className="np-grupo-n">{disponible ? plural(n, 'artículo', 'artículos') : 'Pendiente'}</p>
      </header>
      {/* Nombre + PDF fuera de la barra fija (así cabe en una línea en móvil).
          Siempre presente para que las columnas del modo comparar casen. */}
      <div className="np-grupo-sub">
        <p className="np-grupo-nombre">{partido.nombre !== partido.sigla ? partido.nombre : ''}</p>
        {urlPrograma(partido) ? (
          <a className="np-enlace-txt np-grupo-pdf" href={urlPrograma(partido)} target="_blank" rel="noopener">
            Programa (PDF)<span className="np-sr"> completo de {partido.sigla}, pestaña nueva</span> ↗
          </a>
        ) : (
          <span className="np-pendiente np-grupo-pdf">PDF pendiente</span>
        )}
      </div>

      {!disponible ? (
        <div className="np-vacio np-vacio-pendiente">
          <p>
            <strong>Este programa aún no se ha publicado</strong> (última comprobación: {FECHA_COMPROBACION}). Lo
            incorporaremos en cuanto esté disponible.
          </p>
        </div>
      ) : n === 0 ? (
        <div className="np-vacio">
          <p>
            No hemos localizado artículos de este programa sobre {tema.nombre.toLowerCase()}.
          </p>
          <a className="np-enlace-txt" href={ENLACES.contacto} target="_blank" rel="noopener">
            ¿Crees que falta alguno? Escríbenos
          </a>
        </div>
      ) : (
        <>
          {/* Peso del tema en este programa y su puesto entre los 15 */}
          <p className="np-grupo-peso">
            <strong>{pct(peso)}</strong>{' '}
            <span>
              de su programa ({n} de sus {totalPartido} medidas).{' '}
              {puesto && (
                <>
                  Es su {ordinal(puesto.n)} tema de {TEMAS.length}
                  {puesto.empate ? ' (empatado)' : ''}.
                </>
              )}
            </span>
          </p>
          <ul className="np-articulos" role="list">
            {lista.map((a) => (
              <li key={a.id}>
                <Tarjeta articulo={a} partido={partido} tema={tema} onElegirTema={onElegirTema} />
              </li>
            ))}
          </ul>
          {n > ARTICULOS_VISIBLES && (
            <button type="button" className="np-btn np-btn-mas" aria-expanded={todos} onClick={() => setTodos(!todos)}>
              {todos ? 'Mostrar menos' : `Mostrar ${plural(n - ARTICULOS_VISIBLES, 'artículo más', 'artículos más')} de ${partido.sigla}`}
            </button>
          )}
        </>
      )}
    </section>
  );
}

function Tarjeta({ articulo: a, partido, tema, onElegirTema }) {
  const [abierto, setAbierto] = useState(false);
  const largo = a.texto.length > 220;
  const href = enlaceArticulo(a, partido);
  const idTexto = `np-txt-${a.id}`;
  const otros = a.temas.filter((x) => x !== tema.id).map((x) => TEMAS.find((tt) => tt.id === x));
  const meta = [a.ref, a.pagina && `Pág. ${a.pagina}`].filter(Boolean).join(' · ');

  return (
    <article className="np-art">
      {meta && <p className="np-art-meta">{meta}</p>}
      {a.titulo && <h5 className="np-art-titulo">{a.titulo}</h5>}
      {a.texto && (
        <p id={idTexto} className={`np-art-texto${largo && !abierto ? ' is-recortado' : ''}`}>
          {/* Comillas para el texto corrido; las listas con viñetas van tal cual */}
          {a.texto.startsWith('•') ? a.texto : `«${a.texto}»`}
        </p>
      )}
      {a.nota && (
        <p className="np-art-nota">
          <span aria-hidden="true">⚠</span> {a.nota}: consulta el documento.
        </p>
      )}
      {otros.length > 0 && (
        <p className="np-art-tambien">
          También en:{' '}
          {otros.map((o) => (
            <button type="button" key={o.id} className="np-tag" onClick={() => onElegirTema(o.id)}>
              {o.nombre}
            </button>
          ))}
        </p>
      )}
      <div className="np-art-acciones">
        {largo && (
          <button
            type="button"
            className="np-enlace-txt"
            aria-expanded={abierto}
            aria-controls={idTexto}
            onClick={() => setAbierto(!abierto)}
          >
            {abierto ? 'Leer menos' : 'Leer completo'}
          </button>
        )}
        {href ? (
          <a className="np-enlace-txt" href={href} target="_blank" rel="noopener">
            Ver en el programa<span className="np-sr"> (PDF, pestaña nueva)</span> ↗
          </a>
        ) : (
          <span className="np-pendiente">Enlace al PDF pendiente</span>
        )}
      </div>
    </article>
  );
}
