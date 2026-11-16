import { useState } from 'react';
import { FECHA_ELECCION, TEMAS } from '../config.js';
import { compartir, diasHasta } from '../util.js';

// Franja final de campaña: el cartel vuelve a cerrar la pieza.
export default function Cierre() {
  const [aviso, setAviso] = useState('');
  const votado = diasHasta(FECHA_ELECCION) < 0;

  const compartirHerramienta = async () => {
    const url = new URL(window.location.href);
    url.searchParams.delete('tema');
    url.searchParams.delete('partidos');
    const r = await compartir({
      titulo: 'Lee, no se lo esperan · Programas electorales 29N',
      texto: `Compara artículo a artículo qué proponen los programas electorales en ${TEMAS.length} temas. Léelos antes de votar.`,
      url: url.href,
    });
    if (r === 'copiado') {
      setAviso('Enlace copiado');
      setTimeout(() => setAviso(''), 2500);
    }
  };

  return (
    <div className="np-banda np-banda-teal">
      <div className="np-in np-final">
        <div>
          <p className="np-hero-kicker">{votado ? 'Elecciones generales' : 'El próximo 29 de noviembre'}</p>
          <p className="np-final-lema">
            <span className="np-sr">Lee. Compara. Decide.</span>
            <span aria-hidden="true">Lee. Compara. </span>
            <span className="np-caja" aria-hidden="true">
              Decide.
            </span>
          </p>
        </div>
        <div className="np-final-accion">
          <button type="button" className="np-boton np-boton-navy" onClick={compartirHerramienta}>
            <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" focusable="false">
              <path d="M18 16a3 3 0 0 0-2.4 1.2l-6.7-3.4a3 3 0 0 0 0-1.6l6.7-3.4A3 3 0 1 0 15 7l-6.7 3.4a3 3 0 1 0 0 3.2L15 17a3 3 0 1 0 3-1z" />
            </svg>
            Pásaselo a alguien
          </button>
          <span className="np-aviso-copia" role="status">
            {aviso}
          </span>
          <p className="np-final-firma">www.odesocan.org</p>
        </div>
      </div>
    </div>
  );
}
