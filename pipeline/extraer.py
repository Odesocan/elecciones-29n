"""Etapa 2 · PDF → texto de cada página (con caché).

Extraer el texto de un PDF largo con pypdf tarda (el de CC pesa 69 MB), y
lo necesitan dos etapas: segmentar y verificar. Por eso se guarda en
datos/texto/{partido}.json junto con la huella del PDF, el modo de
extracción y la versión de pypdf: si cambia cualquiera de los tres, la
caché se rehace sola.

El texto se guarda TAL CUAL lo devuelve pypdf; cada etapa lo normaliza
a su manera (ver texto.py).
"""
import hashlib
import json

import pypdf
from pypdf import PdfReader

from . import config, rutas
from .perfiles import perfil


def huella(ruta) -> str:
    h = hashlib.sha256()
    with open(ruta, 'rb') as f:
        for bloque in iter(lambda: f.read(1 << 20), b''):
            h.update(bloque)
    return h.hexdigest()


def ruta_pdf(pid):
    p = config.partido(pid)
    if not p['programa']:
        raise SystemExit(f'{p["sigla"]}: su programa aún no está publicado (programa = null en config/partidos.json).')
    ruta = rutas.FUENTES / p['programa']['archivo']
    if not ruta.exists():
        raise SystemExit(f'Falta {rutas.relativa(ruta)}. Ejecuta: python3 maestro.py descargar --partido {pid}')
    return ruta


def paginas(pid, forzar=False) -> list[str]:
    """Texto bruto de cada página del programa de `pid` (desde la caché si vale)."""
    pdf = ruta_pdf(pid)
    modo = perfil(pid).modo
    firma = {'sha256': huella(pdf), 'modo': modo, 'pypdf': pypdf.__version__}
    cache = rutas.TEXTO / f'{pid}.json'
    if cache.exists() and not forzar:
        guardado = json.loads(cache.read_text(encoding='utf-8'))
        if all(guardado.get(k) == v for k, v in firma.items()):
            return guardado['paginas']

    lector = PdfReader(pdf)
    texto = [(pg.extract_text(extraction_mode='layout') if modo == 'layout' else pg.extract_text()) or ''
             for pg in lector.pages]
    rutas.TEXTO.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({**firma, 'paginas': texto}, ensure_ascii=False), encoding='utf-8')
    vacias = [i for i, t in enumerate(texto, 1) if len(t.strip()) < 40]
    print(f'   {pid}: {len(texto)} págs. extraídas en modo {modo} · casi vacías: {vacias or "ninguna"}')
    return texto


def vocabulario(pid) -> set:
    """Palabras (en minúscula) del PDF según el OTRO modo de pypdf, con caché.
    Sirve para reparar las palabras que el modo del perfil parte en dos: el
    PSOE se extrae en «plain» y se repara con «layout»; UPC, al revés."""
    import re
    pdf = ruta_pdf(pid)
    otro = 'plain' if perfil(pid).modo == 'layout' else 'layout'
    firma = {'sha256': huella(pdf), 'pypdf': pypdf.__version__, 'modo': otro}
    cache = rutas.TEXTO / f'{pid}.vocabulario.json'
    if cache.exists():
        guardado = json.loads(cache.read_text(encoding='utf-8'))
        if all(guardado.get(k) == v for k, v in firma.items()):
            return set(guardado['palabras'])
    texto = ' '.join((pg.extract_text(extraction_mode='layout') if otro == 'layout' else pg.extract_text()) or ''
                     for pg in PdfReader(pdf).pages)
    palabras = sorted(set(re.findall(r'[a-záéíóúüñç]+', texto.lower())))
    rutas.TEXTO.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({**firma, 'palabras': palabras}, ensure_ascii=False), encoding='utf-8')
    return set(palabras)


def ejecutar(pids, forzar=False):
    for pid in pids:
        paginas(pid, forzar=forzar)
        print(f'   {pid}: texto listo → {rutas.relativa(rutas.TEXTO / f"{pid}.json")}')
