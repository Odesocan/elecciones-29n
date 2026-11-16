"""Etapa 1 · Descarga de los PDF oficiales y control de versiones.

Para cada partido con programa publicado (config/partidos.json):
  · Si el PDF local ya coincide con la huella SHA-256 guardada, no hace nada.
  · Si no hay huella (programa recién añadido), descarga y la guarda junto
    con el nº de páginas.
  · Si el partido ha cambiado el PDF (otra huella), NO sobrescribe el que se
    usó para verificar: lo deja como «….nuevo.pdf» y avisa. Con --aceptar se
    adopta la versión nueva (y hay que volver a segmentar y revisar).

Si una web bloquea las descargas automáticas, descarga el PDF a mano desde
el navegador y guárdalo en datos/fuentes/ con el nombre de «archivo».
"""
import shutil
import urllib.request

from pypdf import PdfReader

from . import config, rutas
from .extraer import huella

AGENTE = 'Mozilla/5.0 (compatible; lee-los-programas/0.2)'


def _bajar(url, destino):
    peticion = urllib.request.Request(url, headers={'User-Agent': AGENTE})
    with urllib.request.urlopen(peticion, timeout=120) as r, open(destino, 'wb') as f:
        shutil.copyfileobj(r, f)
    with open(destino, 'rb') as f:
        if f.read(5) != b'%PDF-':
            destino.unlink()
            raise ValueError('lo descargado no es un PDF')


def descargar(pid, aceptar=False) -> bool:
    p = config.partido(pid)
    prog = p['programa']
    if not prog:
        print(f'   · {p["sigla"]}: programa aún no publicado')
        return True
    rutas.FUENTES.mkdir(parents=True, exist_ok=True)
    local = rutas.FUENTES / prog['archivo']
    nuevo = local.with_name(local.stem + '.nuevo.pdf')

    # Documento facilitado por el partido, sin versión en línea (UPC): no hay
    # web que vigilar; solo se comprueba que la copia versionada es la registrada.
    if not prog.get('url'):
        if not local.exists():
            print(f'   ✗ {p["sigla"]}: falta {rutas.relativa(local)} (lo facilitó el partido; no se puede descargar)')
            return False
        if prog.get('sha256') and huella(local) != prog['sha256']:
            print(f'   ⚠ {p["sigla"]}: {rutas.relativa(local)} no es el que se verificó (otra huella)')
            return False
        print(f'   ✓ {p["sigla"]}: documento facilitado por el partido, sin versión en línea que vigilar')
        return True

    def adoptar(origen, motivo):
        if origen != local:
            origen.replace(local)
        paginas = len(PdfReader(local).pages)
        config.actualizar_programa(pid, sha256=huella(local), paginas=paginas)
        print(f'   ✓ {p["sigla"]}: {motivo} ({paginas} págs.) → {rutas.relativa(local)}')

    # Adoptar una versión nueva que ya se descargó y se revisó.
    if aceptar:
        if not nuevo.exists():
            print(f'   · {p["sigla"]}: no hay ninguna versión nueva pendiente')
            return True
        adoptar(nuevo, 'adoptada la versión nueva; vuelve a segmentar y revisa los cambios')
        return True

    # Primera descarga: aún no hay huella guardada.
    sha = prog.get('sha256')
    if not sha:
        try:
            _bajar(prog['url'], nuevo)
        except Exception as e:  # red, 403, 404…
            print(f'   ✗ {p["sigla"]}: no se pudo descargar ({e}). Descárgalo a mano en {rutas.relativa(local)}')
            return False
        adoptar(nuevo, 'descargado y registrada su huella')
        return True

    # Ya verificado antes: comprobar que el de la web sigue siendo el mismo.
    local_ok = local.exists() and huella(local) == sha
    try:
        _bajar(prog['url'], nuevo)
    except Exception as e:
        if local_ok:
            print(f'   ⚠ {p["sigla"]}: no se pudo comprobar la web ({e}); se usa el PDF local verificado')
            return True
        print(f'   ✗ {p["sigla"]}: no se pudo descargar ({e}). Descárgalo a mano en {rutas.relativa(local)}')
        return False
    if huella(nuevo) == sha:
        if local_ok:
            nuevo.unlink()
        else:
            nuevo.replace(local)
        print(f'   ✓ {p["sigla"]}: el PDF de la web es el mismo que se verificó')
        return True
    print(f'   ⚠ {p["sigla"]}: ¡NUEVA VERSIÓN del programa en su web! Guardada en {rutas.relativa(nuevo)}.\n'
          f'        Revísala y, para adoptarla: python3 maestro.py descargar --partido {pid} --aceptar')
    return False


def ejecutar(pids, aceptar=False):
    return all([descargar(pid, aceptar) for pid in pids])
