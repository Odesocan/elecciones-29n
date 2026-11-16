"""Utilidades de texto compartidas por segmentar y verificar."""
import re
import unicodedata

# Ligaduras tipográficas y guion blando que dejan los PDF.
LIGADURAS = {'ﬁ': 'fi', 'ﬂ': 'fl', 'ﬀ': 'ff', 'ﬃ': 'ffi', 'ﬄ': 'ffl', '­': ''}
MAY = 'A-ZÁÉÍÓÚÜÑ'
MIN = 'a-záéíóúüñ'


def normalizar_glifos(t: str) -> str:
    """Sustituye ligaduras y nombres de glifo coladores («75/uni00A0%» → «75 %»)."""
    for a, b in LIGADURAS.items():
        t = t.replace(a, b)
    return re.sub(r'/uni([0-9A-Fa-f]{4})', lambda m: chr(int(m.group(1), 16)), t)


def lineas(pagina: str) -> list[str]:
    """Líneas no vacías de una página, con los espacios compactados."""
    return [re.sub(r'\s+', ' ', l).strip() for l in normalizar_glifos(pagina).splitlines() if l.strip()]


def esqueleto(t: str) -> str:
    """Solo letras y cifras, en minúscula: la huella con la que se compara
    un texto con el PDF. Tolera saltos de línea, espacios y guiones de corte,
    pero no una sola palabra cambiada."""
    t = unicodedata.normalize('NFC', normalizar_glifos(t)).lower()
    return re.sub(r'[^0-9a-záéíóúüñç]', '', t)
