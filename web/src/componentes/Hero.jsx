import { PARTIDOS, TEMAS } from '../config.js';
import CuentaAtras from './CuentaAtras.jsx';

// Cabecera compacta: el cartel de calle «LEE, NO SE LO ESPERAN.»
// convertido en la entrada del selector (comparten el mismo bloque teal).
export default function Hero() {
  const siglas = PARTIDOS.map((p) => p.sigla);
  const lista = `${siglas.slice(0, -1).join(', ')} y ${siglas.at(-1)}`;

  return (
    <header className="np-hero">
      <div className="np-hero-top">
        <p className="np-hero-kicker">Elecciones generales / 29 de noviembre</p>
        <CuentaAtras />
      </div>

      <h2 className="np-hero-lema">
        <span className="np-sr">Lee, no se lo esperan.</span>
        <span className="np-hero-lee" aria-hidden="true">
          Lee,
        </span>
        <span className="np-hero-resto" aria-hidden="true">
          <span>No se lo</span>
          <span className="np-caja">Esperan.</span>
        </span>
      </h2>

      <p className="np-hero-sumario">Compara qué proponen {lista} en {TEMAS.length} temas.</p>
    </header>
  );
}
