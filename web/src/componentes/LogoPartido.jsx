import { createContext, useContext, useState } from 'react';
import { MODO_BOCETO } from '../config.js';
import { varsPartido } from '../util.js';

// Carpeta de los logos (atributo data-logos del bloque Divi).
export const ContextoLogos = createContext('./logos/');

// Logos que ya fallaron: no se vuelven a pedir en cada bloque.
const fallidos = new Set();

// Logo oficial del partido. Es decorativo (alt=""): la sigla siempre va
// escrita al lado. Si el archivo no existe, cuadrado con su color (y, con
// «rotulo», la sigla dentro: donde el logo es la única marca visible).
// No se dibujan imitaciones de logos: solo se usan los archivos oficiales.
export default function LogoPartido({ partido, tam = 'm', rotulo = '', carga = 'lazy' }) {
  const base = useContext(ContextoLogos);
  const url = base + partido.logo;
  // Sin carpeta de logos (data-logos="ninguno") no se pide nada.
  const [fallo, setFallo] = useState(!base || !partido.logo || fallidos.has(url));
  const clase = `np-logo np-logo-${tam}`;

  if (fallo)
    return (
      <span className={`${clase} is-sin-logo`} style={varsPartido(partido)} aria-hidden="true">
        {rotulo || (MODO_BOCETO && tam !== 's' ? 'logo' : '')}
      </span>
    );
  return (
    <span className={clase} aria-hidden="true">
      <img
        src={url}
        alt=""
        loading={carga}
        decoding="async"
        onError={() => {
          fallidos.add(url);
          setFallo(true);
        }}
      />
    </span>
  );
}
