"""Apartados del programa: en qué capítulo y sección está cada medida.

Sirve de contexto para clasificar y revisar. Una viñeta corta («Crear juzgados
especializados en violencia contra la infancia») se entiende mejor sabiendo
que está en «Impulsar una justicia de calidad». Pero no decide el tema: se
clasifica por lo que la medida hace.

Cada programa marca sus apartados de una forma (campo «apartados» del perfil):

  pag       índice «1.1 TÍTULO - Pág. 12» con bloques en MAYÚSCULAS sin página (PP).
  puntos    índice «Título ........ 15» de un solo nivel, con «•» (Vox).
  sangria   índice «Título ........ 15» con tres niveles según la sangría,
            que solo se ve al extraer el índice en modo layout (PSOE).
  causas    sin índice: cabeceras «1 DEFENDER LOS DERECHOS / DE CANARIAS»
            dentro del texto (CC–1ºC).

Con un índice, los títulos se buscan en el texto en el mismo orden. Un título
cuenta si ocupa líneas enteras (de 1 a 4), así que «Universidad» no se
confunde con una frase que empiece por «Universidades». Si el título de un
bloque no está en el texto (portadilla en imagen), el bloque lo da el índice
al encontrar su primer apartado.

Resultado: {(página, nº de línea): ruta}, donde ruta es la lista de títulos
desde el capítulo hasta el apartado («[bloque, apartado]»).
"""
import re

from pypdf import PdfReader

from .extraer import ruta_pdf
from .texto import MAY, MIN, esqueleto

PUNTOS = re.compile(r'^(.*?\S)\s*(?:\.{2,}|\s\.)\s*\d{1,3}\s*$')


# ── Lectura del índice: [(nivel, título)] en orden ───────────────────────
def _indice_pag(todas):
    """PP: «REPARAR EL ESTADO» (bloque) y «1.1 TÍTULO - Pág. 12» (apartado),
    que puede ocupar dos líneas."""
    for _, ls in todas[:12]:
        if 'ÍNDICE' not in ls:
            continue
        entradas, previo = [], ''
        for l in ls[ls.index('ÍNDICE') + 1:]:
            m = re.search(r'\s*-\s*Pág\.\s*\d{1,3}\s*$', l)
            if m:
                entradas.append((2, f'{previo} {l[:m.start()]}'.strip()))
                previo = ''
            elif re.match(r'^\d+\.\d+\s', l) or previo:
                previo = f'{previo} {l}'.strip()
            elif not re.fullmatch(r'\d{1,3}', l):
                entradas.append((1, l))
        return entradas
    return []


def _indice_puntos(todas):
    """Vox: «• Título ......... 7»; un título largo sigue en la línea siguiente."""
    for _, ls in todas[:12]:
        if 'ÍNDICE' not in ls:
            continue
        entradas, previo = [], ''
        for l in ls[ls.index('ÍNDICE') + 1:]:
            m = PUNTOS.match(l)
            if m:
                entradas.append((1, re.sub(r'^•\s*', '', f'{previo} {m.group(1)}'.strip())))
                previo = ''
            elif not re.fullmatch(r'\d{1,3}', l):
                previo = f'{previo} {l}'.strip()
        return entradas
    return []


def _indice_sangria(pid, todas):
    """PSOE: los niveles solo se ven en la sangría del modo layout
    (0 = capítulo, hasta 12 espacios = apartado, más = subapartado)."""
    paginas = [i for i, ls in todas[:10] if sum(1 for l in ls if re.search(r'\.{4,}\s*\d{1,3}\s*$', l)) >= 3]
    lector = PdfReader(ruta_pdf(pid))
    entradas, previo, sangria_previa = [], '', 0
    for i in paginas:
        for l in (lector.pages[i - 1].extract_text(extraction_mode='layout') or '').splitlines():
            if not l.strip() or l.strip() == 'ÍNDICE' or re.fullmatch(r'\s*\d{1,3}\s*', l):
                continue
            sangria = len(l) - len(l.lstrip())
            m = PUNTOS.match(l.strip())
            if not m:
                previo, sangria_previa = f'{previo} {l.strip()}'.strip(), sangria if not previo else sangria_previa
                continue
            s = sangria_previa if previo else sangria
            nivel = 1 if s == 0 else 2 if s <= 12 else 3
            entradas.append((nivel, re.sub(r'\s+', ' ', f'{previo} {m.group(1)}').strip()))
            previo = ''
    return entradas


# ── Búsqueda en el texto ──────────────────────────────────────────────────
def _rutas(entradas):
    """[(nivel, título)] → [(clave, ruta)]: cada título con sus antecesores."""
    salida, pila = [], []
    for nivel, titulo in entradas:
        pila = pila[:nivel - 1] + [titulo]
        salida.append((esqueleto(titulo), list(pila)))
    return salida


def _es_titulo(ls, k, clave):
    """¿Empieza en la línea k un título que ocupa líneas enteras? Se tolera
    un número pegado al final («DEMOCRACIA02», portadilla del PP)."""
    if not re.match(f'[{MAY}0-9¿¡«"“]', ls[k]):
        return False
    for m in range(1, 5):
        junto = esqueleto(' '.join(ls[k:k + m]))
        if junto == clave or (junto.startswith(clave) and junto[len(clave):].isdigit()):
            return True
        if not clave.startswith(junto):
            return False
    return False


def _buscar(todas, entradas):
    claves = _rutas(entradas)
    desde = next((i for i, ls in todas[:12] if 'ÍNDICE' in ls or
                  sum(1 for l in ls if PUNTOS.match(l)) >= 3), 0)
    # El índice del PSOE ocupa varias páginas: se empieza después de la última.
    while desde < len(todas) and sum(1 for l in todas[desde][1] if PUNTOS.match(l)) >= 3:
        desde += 1
    marcas, j = {}, 0
    for pag, ls in todas:
        if pag <= desde:
            continue
        for k in range(len(ls)):
            # Se tolera que falten hasta 3 títulos seguidos en el texto.
            for d in range(j, min(j + 4, len(claves))):
                if _es_titulo(ls, k, claves[d][0]):
                    marcas[(pag, k)] = claves[d][1]
                    j = d + 1
                    break
    no_halladas = [e[1][-1] for e in claves if e[1] not in marcas.values()]
    return marcas, no_halladas


def _causas(todas):
    """CC–1ºC: «1 DEFENDER LOS DERECHOS» + «DE CANARIAS» (sin minúsculas)."""
    marcas = {}
    for pag, ls in todas:
        for k, l in enumerate(ls):
            if re.fullmatch(rf'\d{{1,2}} DEFENDER\b[^{MIN}]*', l):
                titulo = l
                for sig in ls[k + 1:k + 3]:
                    if re.search(f'[{MIN}]', sig) or re.match(r'\d', sig):
                        break
                    titulo = f'{titulo} {sig}'
                marcas[(pag, k)] = [titulo]
    return marcas, []


def marcas(pid, todas, modo):
    """{(página, línea): ruta} y la lista de títulos del índice no hallados."""
    if modo == 'causas':
        return _causas(todas)
    entradas = {'pag': lambda: _indice_pag(todas), 'puntos': lambda: _indice_puntos(todas),
                'sangria': lambda: _indice_sangria(pid, todas)}[modo]()
    return _buscar(todas, entradas)


def por_posicion(pid, salida, marcas):
    """En una página donde empieza un apartado, decide qué medidas van antes
    del título y cuáles después según el orden visual (modo layout), porque el
    texto normal puede salir desordenado: en el PP, las medidas 175 y 176
    están encima del título 4.4 pero el flujo las pone detrás.
    Solo cuentan los títulos más profundos (los que preceden a medidas) y las
    medidas cuyo comienzo se encuentra en el texto layout. Devuelve los ids
    corregidos."""
    orden = sorted(marcas.items())
    # Se descartan los títulos de bloque a los que sigue uno de sus apartados.
    hondos = [(pos, ruta) for i, (pos, ruta) in enumerate(orden)
              if not (i + 1 < len(orden) and orden[i + 1][1][:len(ruta)] == ruta and len(orden[i + 1][1]) > len(ruta))]
    previa = {pos: (hondos[i - 1][1] if i else []) for i, (pos, _) in enumerate(hondos)}
    paginas = sorted({pag for (pag, _), _ in hondos})
    if not paginas:
        return []
    lector = PdfReader(ruta_pdf(pid))
    corregidas = []
    for pag in paginas:
        lineas_lay = [l.strip() for l in (lector.pages[pag - 1].extract_text(extraction_mode='layout') or '').splitlines()
                      if l.strip()]
        lay = esqueleto(' '.join(lineas_lay))
        inicio_linea, n = [], 0
        for l in lineas_lay:
            inicio_linea.append(n)
            n += len(esqueleto(l))
        titulos = []
        for (p, _), ruta in hondos:
            # El título tiene que ocupar líneas enteras: «Juventud» no es la
            # palabra «juventud» dentro de una medida anterior.
            k = next((k for k in range(len(lineas_lay)) if _es_titulo(lineas_lay, k, esqueleto(ruta[-1]))), None)
            if p == pag and k is not None:
                titulos.append((inicio_linea[k], ruta))
        if not titulos:
            continue
        titulos.sort()
        entrada = previa[min(pos for pos, _ in hondos if pos[0] == pag)]
        for s in salida:
            inicio = esqueleto(s.get('titulo') or s.get('texto') or '')[:30]
            # Si el comienzo aparece más de una vez en la página (la 372 y la 374
            # del PSOE empiezan igual), no se puede situar: se deja como está.
            if s['pagina'] != pag or len(inicio) < 12 or lay.count(inicio) != 1:
                continue
            i = lay.find(inicio)
            ruta = next((r for t, r in reversed(titulos) if t < i), entrada)
            if ruta != s['apartado']:
                s['apartado'] = list(ruta)
                corregidas.append(s['id'])
    return corregidas


def en_orden(salida, marcas):
    """Las medidas están numeradas en el orden del índice, así que una medida
    no puede volver a un apartado anterior. Si el texto del PDF sale
    desordenado (en el PP, las medidas 211 a 213 aparecen antes del título
    4.7 en el flujo de la página 67), la medida toma el apartado de la
    anterior. Devuelve los ids corregidos."""
    orden = {}
    for _, ruta in sorted(marcas.items()):
        orden.setdefault(tuple(ruta), len(orden))
    corregidas, maximo = [], None
    for s in salida:  # ordenadas por número
        r = tuple(s['apartado'])
        if maximo is not None and orden.get(r, -1) < orden[maximo]:
            s['apartado'] = list(maximo)
            corregidas.append(s['id'])
        elif r in orden:
            maximo = r
    return corregidas


def texto(ruta) -> str:
    """Ruta → «Capítulo › Apartado» para la hoja de revisión y los lotes."""
    return ' › '.join(ruta or [])
