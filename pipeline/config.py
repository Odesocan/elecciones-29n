"""Lectura de config/*.json: la misma configuración que usa la web."""
import json

from . import rutas


def _leer(nombre):
    return json.loads((rutas.CONFIG / nombre).read_text(encoding='utf-8'))


def partidos():
    return _leer('partidos.json')['partidos']


def partido(pid):
    for p in partidos():
        if p['id'] == pid:
            return p
    raise SystemExit(f'Partido desconocido: «{pid}». Ids válidos: {", ".join(p["id"] for p in partidos())}')


def publicados():
    """Partidos con programa publicado (programa ≠ null), en orden alfabético."""
    return [p for p in partidos() if p['programa']]


def temas():
    return _leer('temas.json')['temas']


def ids_temas():
    return [t['id'] for t in temas()]


def fiscal():
    return _leer('fiscal.json')['categorias']


def riesgo_viabilidad():
    """Regla de la etiqueta roja: restan > umbral × suman."""
    return _leer('fiscal.json')['riesgo_viabilidad']


def ids_fiscal():
    return [c['id'] for c in fiscal()]


def igds():
    """Libro de códigos del IGDS (prueba): dimensiones, marcas y áreas."""
    return _leer('igds.json')


def campana():
    return _leer('campana.json')


def actualizar_programa(pid, **cambios):
    """Reescribe campos de «programa» de un partido (lo usa descargar para la huella)."""
    ruta = rutas.CONFIG / 'partidos.json'
    doc = json.loads(ruta.read_text(encoding='utf-8'))
    for p in doc['partidos']:
        if p['id'] == pid:
            p['programa'].update(cambios)
    ruta.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
