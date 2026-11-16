import { useEffect, useState } from 'react';
import { APERTURA_COLEGIOS, CIERRE_COLEGIOS } from '../config.js';
import { pad, sinMovimiento } from '../util.js';

// Cuenta atrás hasta la apertura de los colegios, en una sola fila:
// «QUEDAN [días] [horas] [min] [seg]». Sin botón de pausa (decisión del
// equipo, 14-11-2026). Accesibilidad que se mantiene: con «reducir
// movimiento» se actualiza cada minuto y sin segundos; las cifras que
// cambian son aria-hidden y el lector de pantalla lee una frase estable.
// Clases «np-reloj-*» (no «np-cuenta»: ese nombre es de las tarjetas de
// la prueba de las cuentas).
export default function CuentaAtras() {
  const [quieto] = useState(sinMovimiento);
  const [ahora, setAhora] = useState(() => Date.now());

  useEffect(() => {
    setAhora(Date.now());
    const id = setInterval(() => setAhora(Date.now()), quieto ? 60000 : 1000);
    return () => clearInterval(id);
  }, [quieto]);

  const apertura = Date.parse(APERTURA_COLEGIOS);
  const cierre = Date.parse(CIERRE_COLEGIOS);
  if (ahora >= cierre) return null;
  if (ahora >= apertura)
    return <p className="np-reloj-hoy">Hoy se vota · colegios abiertos hasta las 20:00 (hora canaria)</p>;

  let s = Math.floor((apertura - ahora) / 1000);
  const d = Math.floor(s / 86400);
  s %= 86400;
  const h = Math.floor(s / 3600);
  s %= 3600;
  const m = Math.floor(s / 60);
  s %= 60;
  const partes = [
    [d, d === 1 ? 'día' : 'días'],
    [h, h === 1 ? 'hora' : 'horas'],
    [m, 'min'],
    ...(quieto ? [] : [[s, 'seg']]),
  ];

  return (
    <div className="np-reloj">
      <p className="np-sr">
        Quedan {d} {d === 1 ? 'día' : 'días'} y {h} {h === 1 ? 'hora' : 'horas'} para que abran los colegios
        electorales.
      </p>
      <span className="np-reloj-tit" aria-hidden="true">
        Quedan
      </span>
      {partes.map(([v, et]) => (
        <span className="np-reloj-parte" key={et} aria-hidden="true">
          <b>{pad(v)}</b>
          <small>{et}</small>
        </span>
      ))}
    </div>
  );
}
