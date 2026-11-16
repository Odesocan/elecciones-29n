"""Todas las rutas del proyecto, en un solo sitio."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

CONFIG = RAIZ / 'config'
DOCS = RAIZ / 'docs'

DATOS = RAIZ / 'datos'
FUENTES = DATOS / 'fuentes'              # PDF oficiales (no van a git)
TEXTO = DATOS / 'texto'                  # caché de extracción (no va a git)
SEGMENTOS = DATOS / 'segmentos'          # {partido}.jsonl
CLASIFICACION = DATOS / 'clasificacion'  # {partido}.json
LOTES = CLASIFICACION / 'lotes'          # entradas para clasificar (no van a git)
FISCAL = DATOS / 'fiscal'                # impacto fiscal: {partido}.json
REVISION = DATOS / 'revision' / 'revision-clasificacion.csv'
INFORMES = DATOS / 'informes'
IGDS = DATOS / 'igds'                    # índice de garantía de derechos sociales (prueba)
IGDS_LOTES = IGDS / 'lotes'              # entradas para codificar
IGDS_CODIFICACION = IGDS / 'codificacion'  # codificación de cada lote

WEB = RAIZ / 'web'
# Interfaz entre el pipeline y la web: el único archivo que se pasan.
CSV_WEB = WEB / 'public' / 'data' / 'programas.csv'

DIVI = RAIZ / 'divi'


def relativa(ruta: Path) -> str:
    """Ruta para mostrar en pantalla, relativa a la raíz del proyecto."""
    try:
        return str(Path(ruta).resolve().relative_to(RAIZ))
    except ValueError:
        return str(ruta)
