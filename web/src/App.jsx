import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { AVISO, PARTIDOS, TEMAS, fijarBaseDatos } from './config.js';
import { cargarArticulos, indexar } from './datos.js';
import { escribirURL, guardarLeidos, irA, leerLeidos, leerURL, pctVoz, plural } from './util.js';
import Hero from './componentes/Hero.jsx';
import SelectorTemas from './componentes/SelectorTemas.jsx';
import MapaProgramas from './componentes/MapaProgramas.jsx';
import VistaTema from './componentes/VistaTema.jsx';
import CuentasProgramas from './componentes/CuentasProgramas.jsx';
import Cierre from './componentes/Cierre.jsx';
import { ContextoLogos } from './componentes/LogoPartido.jsx';

export default function App({ src, hero = true, logos = './logos/' }) {
  fijarBaseDatos(src); // para enlazar los PDF que se publican junto al CSV (UPC)
  const inicial = useMemo(leerURL, []);
  const [estado, setEstado] = useState('cargando');
  const [intento, setIntento] = useState(0);
  const [articulos, setArticulos] = useState([]);
  const [tema, setTema] = useState(inicial.tema);
  const [partidos, setPartidos] = useState(inicial.partidos); // vacío = todos
  const [leidos, setLeidos] = useState(leerLeidos);
  const [anuncio, setAnuncio] = useState('');
  // Tras cambiar de vista, a dónde llevar el scroll y el foco.
  // Si se llega con un enlace compartido (?tema=…), salto directo, sin animación.
  const [salto, setSalto] = useState(inicial.tema ? { a: 'vista', foco: false, instantaneo: true } : null);

  const temasRef = useRef(null);
  const vistaRef = useRef(null);
  const tituloVistaRef = useRef(null);
  const mapaRef = useRef(null);
  const tituloMapaRef = useRef(null);

  useEffect(() => {
    let vivo = true;
    setEstado('cargando');
    cargarArticulos(src)
      .then((a) => vivo && (setArticulos(a), setEstado('listo')))
      .catch((e) => {
        console.error('[ODESOCAN · programas]', e);
        if (vivo) setEstado('error');
      });
    return () => {
      vivo = false;
    };
  }, [src, intento]);

  const idx = useMemo(() => indexar(articulos), [articulos]);

  useEffect(() => escribirURL(tema, partidos), [tema, partidos]);

  useEffect(() => {
    if (!tema) return;
    setLeidos((prev) => {
      if (prev.has(tema)) return prev;
      const nuevo = new Set(prev).add(tema);
      guardarLeidos(nuevo);
      return nuevo;
    });
  }, [tema]);

  useEffect(() => {
    if (!salto || estado !== 'listo') return;
    const destino = {
      vista: [vistaRef.current, tituloVistaRef.current],
      mapa: [mapaRef.current, tituloMapaRef.current],
      temas: [temasRef.current, temasRef.current?.querySelector('[aria-pressed="true"]') || temasRef.current?.querySelector('button')],
    }[salto.a];
    // useEffect corre tras pintar: el DOM nuevo ya existe. (Sin rAF:
    // en pestañas en segundo plano no se dispara y el enlace compartido
    // no llevaría al tema.)
    irA(destino[0], { foco: salto.foco ? destino[1] : null, instantaneo: salto.instantaneo });
    setSalto(null);
  }, [salto, estado]);

  const elegirTema = useCallback(
    (id) => {
      setTema(id);
      setSalto({ a: 'vista', foco: true });
      const t = TEMAS.find((x) => x.id === id);
      if (estado === 'listo') setAnuncio(`${t.nombre}: ${plural(idx.totalTema.get(id), 'artículo', 'artículos')}.`);
    },
    [estado, idx],
  );

  // Desde una burbuja del mapa: abre el tema con TODOS los partidos
  // visibles y lleva directamente al bloque del partido pulsado.
  const [enfoque, setEnfoque] = useState(null);
  const elegirPartido = useCallback(
    (temaId, partidoId) => {
      setTema(temaId);
      setPartidos(new Set());
      setEnfoque({ partido: partidoId, n: Date.now() });
      const t = TEMAS.find((x) => x.id === temaId);
      const p = PARTIDOS.find((x) => x.id === partidoId);
      const v = idx.cuota.get(temaId).get(partidoId);
      setAnuncio(
        `${t.nombre}, ${p.sigla}: ${plural(idx.indice.get(temaId).get(partidoId).length, 'artículo', 'artículos')}` +
          (v === null ? ' (programa aún no publicado).' : `, ${pctVoz(v)} de su programa.`),
      );
    },
    [idx],
  );

  // El mapa ya está siempre visible: solo hay que llevar hasta él.
  const verMapa = useCallback(() => setSalto({ a: 'mapa', foco: true }), []);

  // En móvil la lista de temas va plegada: «Otro tema» también la despliega.
  const [abrirTemas, setAbrirTemas] = useState(0);
  const cambiarTema = useCallback(() => {
    setAbrirTemas((n) => n + 1);
    setSalto({ a: 'temas', foco: true });
  }, []);

  // El anuncio del filtro sale del estado ya aplicado (no de un cierre
  // antiguo), así dos pulsaciones seguidas no se pisan.
  const anunciarFiltroRef = useRef(false);
  useEffect(() => {
    if (!anunciarFiltroRef.current || !tema || estado !== 'listo') return;
    anunciarFiltroRef.current = false;
    const visibles = partidos.size ? PARTIDOS.filter((p) => partidos.has(p.id)) : PARTIDOS;
    const n = visibles.reduce((s, p) => s + idx.indice.get(tema).get(p.id).length, 0);
    setAnuncio(`Mostrando ${plural(n, 'artículo', 'artículos')} de ${plural(visibles.length, 'programa', 'programas')}.`);
  }, [partidos, tema, estado, idx]);

  const togglePartido = (id) => {
    anunciarFiltroRef.current = true;
    setPartidos((prev) => {
      const siguiente = new Set(prev);
      if (siguiente.has(id)) siguiente.delete(id);
      else siguiente.add(id);
      return siguiente.size === PARTIDOS.length ? new Set() : siguiente;
    });
  };

  const todosPartidos = () => {
    anunciarFiltroRef.current = true;
    setPartidos(new Set());
  };

  const mostrarPartido = (id) => {
    if (partidos.size && !partidos.has(id)) {
      const siguiente = new Set(partidos).add(id);
      setPartidos(siguiente.size === PARTIDOS.length ? new Set() : siguiente);
    }
  };

  return (
    <ContextoLogos.Provider value={logos}>
    <div className="np-prog" lang="es">
      {AVISO && (
        <p className="np-aviso" role="note">
          {AVISO}
        </p>
      )}

      {/* Banda teal: el cartel + el selector forman una sola pieza */}
      <div className="np-banda np-banda-teal">
        <div className="np-in">
          {hero && <Hero />}
          <SelectorTemas
            ref={temasRef}
            idx={estado === 'listo' ? idx : null}
            tema={tema}
            leidos={leidos}
            onElegir={elegirTema}
            abrir={abrirTemas}
          />
        </div>
      </div>

      {estado === 'cargando' && (
        <p className="np-estado" role="status">
          Cargando los programas…
        </p>
      )}

      {estado === 'error' && (
        <div className="np-estado np-estado-error" role="alert">
          <p>No hemos podido cargar los programas. Comprueba tu conexión e inténtalo de nuevo.</p>
          <button type="button" className="np-btn" onClick={() => setIntento((n) => n + 1)}>
            Reintentar
          </button>
        </div>
      )}

      {/* Banda blanca: la lectura */}
      {estado === 'listo' && tema && (
        <div className="np-banda">
          <div className="np-in">
            <VistaTema
              seccionRef={vistaRef}
              tituloRef={tituloVistaRef}
              tema={tema}
              idx={idx}
              partidos={partidos}
              onTogglePartido={togglePartido}
              onTodos={todosPartidos}
              onMostrarPartido={mostrarPartido}
              onElegirTema={elegirTema}
              onVerMapa={verMapa}
              onCambiarTema={cambiarTema}
              enfoque={enfoque}
            />
          </div>
        </div>
      )}

      {/* La vista de conjunto, siempre visible */}
      {estado === 'listo' && (
        <div className="np-banda np-banda-mapa">
          <div className="np-in">
            <MapaProgramas
              seccionRef={mapaRef}
              tituloRef={tituloMapaRef}
              idx={idx}
              temaActual={tema}
              onElegir={elegirTema}
              onElegirPartido={elegirPartido}
            />
          </div>
        </div>
      )}

      {/* La prueba de las cuentas: la lectura crítica (solo si hay clasificación fiscal) */}
      {estado === 'listo' && idx.cuentas.hay && (
        <div className="np-banda np-banda-cuentas">
          <div className="np-in">
            <CuentasProgramas idx={idx} onElegirTema={elegirTema} />
          </div>
        </div>
      )}

      <Cierre />

      <p className="np-sr" aria-live="polite" aria-atomic="true">
        {anuncio}
      </p>
    </div>
    </ContextoLogos.Provider>
  );
}
