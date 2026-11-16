"""Etapa 5 · Literalidad: cada titular y texto está LITERALMENTE en el PDF.

Se compara el «esqueleto» (solo letras y cifras, en minúscula) de la medida
con el del documento entero. Así se toleran saltos de línea, espacios y
guiones de corte, pero no una sola palabra cambiada.

Una medida que cruza de página puede tener en medio, en el PDF, el número de
página o la cabecera fija del programa: es lo ÚNICO que se permite entre dos
trozos consecutivos (perfil.cabeceras y perfil.numeros_en_salto, que en el
PSOE admite los restos de numeración de listas al pie de página).
"""
import re

from .extraer import paginas
from .perfiles import perfil
from .texto import esqueleto


def documento(pid) -> str:
    c = perfil(pid)
    return esqueleto(''.join(c.con_vinetas(p) for p in paginas(pid)))


def hueco_permitido(pid) -> re.Pattern:
    c = perfil(pid)
    cabecera = esqueleto(''.join(c.cabeceras))
    medio = f'({re.escape(cabecera)})?' if cabecera else ''
    n = c.numeros_en_salto
    return re.compile(rf'^(\d{{1,3}}){{0,{n}}}{medio}(\d{{1,3}}){{0,{n}}}$')


def es_literal(texto, doc, hueco) -> bool:
    """Busca el texto en el documento por trozos lo más largos posible
    (búsqueda binaria); entre trozo y trozo solo puede haber `hueco`."""
    x, i, pos, primero = esqueleto(texto), 0, 0, True
    while i < len(x):
        lo, hi, mejor = 1, len(x) - i, None
        while lo <= hi:
            mid = (lo + hi) // 2
            j = doc.find(x[i:i + mid], pos)
            if j >= 0:
                mejor, lo = (mid, j), mid + 1
            else:
                hi = mid - 1
        if not mejor:
            return False
        n, j = mejor
        if not primero and not hueco.match(doc[pos:j]):
            return False
        pos, i, primero = j + n, i + n, False
    return True


class Verificador:
    """Prepara el documento una vez y verifica todas las medidas de un partido."""

    def __init__(self, pid):
        self.doc = documento(pid)
        self.hueco = hueco_permitido(pid)

    def medida(self, s) -> bool:
        piezas = s.get('piezas') or [s['texto']]
        return all(es_literal(x, self.doc, self.hueco) for x in piezas) and es_literal(s['titulo'], self.doc, self.hueco)
