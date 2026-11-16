"""IGDS (prueba) · Índice de Garantía de Derechos Sociales.

Cuántas medidas de cada 100 del programa son garantías objetivas de derechos
sociales. Libro de códigos y reglas operativas: docs/CRITERIOS-IGDS.md.
Produce datos, un informe para analizarlos y el resumen que usa el apartado
«Prometer no es garantizar» de la herramienta (retirado de la web el 16-11-2026).

    python3 maestro.py igds fase0      ¿se lee completo cada programa?
    python3 maestro.py igds preparar   lotes de codificación (medidas + prosa)
    python3 maestro.py igds validar    comprueba la codificación   [--lote lote-01]
    python3 maestro.py igds contrastar señales para la revisión humana y posibles repeticiones
    python3 maestro.py igds calcular   índices, control de calidad, CSV e informe
    python3 maestro.py igds muestra    hojas de validación humana (pipeline/igds_validacion.py)
    python3 maestro.py igds concordancia  acuerdo entre la codificación y la validación humana

La unidad de entrada es TODO el programa: las medidas numeradas que ya usa la
herramienta (datos/segmentos/) y los bloques de prosa que quedan fuera de
ellas (prólogos, manifiestos, introducciones de capítulo). La codificación
(atomizar y codificar) la hace una persona o una IA siguiendo los criterios;
este módulo prepara, comprueba y calcula, sin decidir nada por su cuenta.
"""
import csv
import json
import re
from collections import Counter

from pypdf import PdfReader

from . import config, obsidian, rutas
from .extraer import paginas, ruta_pdf, vocabulario
from .perfiles import perfil
from .segmentar import cargar, es_cabecera, reparar_palabras, unir
from .texto import esqueleto, lineas

DIMS = ['uni', 'exi', 'des', 'ndi']
MARCAS = ['reg', 'dec']
CONFIANZA = {'alta', 'media', 'baja'}
CAMPOS_CSV = ['id_medida', 'formacion', 'eleccion', 'pagina', 'fragmento', 'medida_sintesis', 'area',
              'uni', 'exi', 'des', 'ndi', 'g', 'reg', 'dec', 'justificacion', 'confianza', 'revisar']

# Páginas que se leen en modo «plain» para la prosa: en «layout» el manifiesto
# a dos columnas de CC mezcla las líneas de ambas.
PROSA_PLANA = {'cc': range(2, 8)}
# Apartados del programa (para la fase 0): títulos numerados o entradas del índice.
APARTADOS = {
    'pp': re.compile(r'^(\d\.\d{1,2})\s+[A-ZÁÉÍÓÚÑ]'),
    'cc': re.compile(r'^(\d{1,2})\s+DEFENDER\b'),
    'psoe': re.compile(r'^(.*?\S)\s*(?:\.{2,}|\s\.)\s*\d{1,3}\s*$'),  # entradas del índice
    'vox': re.compile(r'^•\s*(\S.*?)\s*(?:\.{3,}.*)?$'),
}
HUECO = re.compile(r'^(\d{1,3})?\s*(Permanezca|atento a la|campaña para|conocer esta|nueva medida)', re.I)
INDICE = re.compile(r'Pág\.\s*\d|\.{4,}|^ÍNDICE$')


# ── Prosa fuera de las medidas numeradas ────────────────────────────────
def _paginas_planas(pid, nums):
    lector = PdfReader(ruta_pdf(pid))
    return {n: lector.pages[n - 1].extract_text() or '' for n in nums}


def _lineas_pagina(pid, pag, vocab=None):
    """Líneas de una página normalizadas como en la segmentación (viñetas y,
    si el perfil lo pide, palabras partidas): no cambia el «esqueleto»."""
    c = perfil(pid)
    ls = lineas(c.con_vinetas(pag))
    if c.reparar_palabras:
        vocab = vocab if vocab is not None else vocabulario(pid)
        ls = [reparar_palabras(l, vocab) for l in ls]
    return ls


def _es_ruido(pid, l):
    c = perfil(pid)
    return (c.omitir(l) or c.inicio.match(l) or es_cabecera(l) or INDICE.search(l) or HUECO.match(l)
            or len(esqueleto(l)) < 4)


def bloques_prosa(pid):
    """Texto de cada página que no pertenece a ninguna medida numerada:
    [{'id': 'pp-p06', 'pagina': 6, 'texto': …}]. Solo bloques de 15 palabras o más."""
    seg = cargar(pid)
    corpus = '|'.join(esqueleto(s['titulo']) + esqueleto(s['texto']) for s in seg)
    planas = _paginas_planas(pid, PROSA_PLANA.get(pid, []))
    por_pagina = []
    vocab = vocabulario(pid) if perfil(pid).reparar_palabras else None
    for n, pag in enumerate(paginas(pid), 1):
        ls = lineas(planas[n]) if n in planas else _lineas_pagina(pid, pag, vocab)
        por_pagina.append((n, [l for l in ls if not _es_ruido(pid, l) and esqueleto(l) not in corpus]))
    # Desbordes ocultos del maquetado: un párrafo que en el PDF está en una
    # página y, invisible, también en la anterior (CC, págs. 3 y 4). Se
    # conserva la última aparición, que es la que se ve.
    vistas, bloques = set(), []
    for n, ls in reversed(por_pagina):
        propias = []
        for l in ls:
            e = esqueleto(l)
            if len(e) >= 30 and e in vistas:
                continue
            vistas.add(e)
            propias.append(l)
        texto = unir(propias)
        if len(texto.split()) >= 15:
            bloques.append({'id': f'{pid}-p{n:02d}', 'pagina': n, 'texto': texto})
    return bloques[::-1]


# ── Fase 0 ──────────────────────────────────────────────────────────────
def fase0(pids):
    """¿Se lee completo cada programa? Páginas, apartados, páginas sin texto,
    medidas numeradas, prosa y texto que no se asigna a nada."""
    salida = {}
    for pid in pids:
        p = config.partido(pid)
        pags = paginas(pid)
        seg = cargar(pid)
        prosa = bloques_prosa(pid)
        corpus = '|'.join([esqueleto(s['titulo']) + esqueleto(s['texto']) for s in seg] +
                          [esqueleto(b['texto']) for b in prosa])
        planas = _paginas_planas(pid, PROSA_PLANA.get(pid, []))
        apartados, total, cubierto, sueltas = set(), 0, 0, []
        for n, pag in enumerate(pags, 1):
            for l in (lineas(planas[n]) if n in planas else _lineas_pagina(pid, pag)):
                # En Vox los apartados solo se cuentan en el índice (las viñetas «•» se usan en todo el texto).
                en_indice = pid not in ('vox', 'psoe') or bool(re.search(r'\.{4,}\s*\d', pag))
                m = APARTADOS[pid].match(l) if pid in APARTADOS and en_indice else None
                if m:
                    apartados.add(m.group(1))
                if _es_ruido(pid, l):
                    continue
                e = esqueleto(l)
                total += len(e)
                if e in corpus:
                    cubierto += len(e)
                else:
                    sueltas.append((n, l))
        vacias = [n for n, t in enumerate(pags, 1) if len(t.strip()) < 40]
        salida[pid] = {
            'sigla': p['sigla'],
            'programa': p['programa']['titulo'],
            'paginas': len(pags),
            'indice': any('ÍNDICE' in t for t in pags[:10]),
            'apartados': len(apartados),
            'paginas_sin_texto': vacias,
            'numeradas': sum(1 for s in seg if s['aviso'] != 'por anunciar'),
            'por_anunciar': [s['id'] for s in seg if s['aviso'] == 'por anunciar'],
            'cortadas': [s['id'] for s in seg if s['aviso'] and s['aviso'] != 'por anunciar'],
            'bloques_prosa': [b['id'] for b in prosa],
            'palabras_prosa': sum(len(b['texto'].split()) for b in prosa),
            'cobertura': round(cubierto / total, 4) if total else 0,
            'lineas_sueltas': [f'p{n}: {l}' for n, l in sueltas],
        }
        r = salida[pid]
        print(f'   {r["sigla"]}: {r["paginas"]} págs. · índice {"sí" if r["indice"] else "no"} · '
              f'{r["apartados"]} apartados · sin texto {len(vacias)} · {r["numeradas"]} medidas numeradas '
              f'(+{len(r["por_anunciar"])} por anunciar) · {len(prosa)} bloques de prosa '
              f'({r["palabras_prosa"]} palabras) · texto asignado {r["cobertura"]:.1%}')
        for x in r['lineas_sueltas'][:8]:
            print(f'        sin asignar → {x[:110]}')
    rutas.IGDS.mkdir(parents=True, exist_ok=True)
    ruta = rutas.IGDS / 'fase0.json'
    previa = json.loads(ruta.read_text(encoding='utf-8')) if ruta.exists() else {}
    ruta.write_text(json.dumps({**previa, **salida}, ensure_ascii=False, indent=1), encoding='utf-8')
    return salida


# ── Lotes ───────────────────────────────────────────────────────────────
def _unidades_numeradas(pid):
    sigla = config.partido(pid)['sigla']
    temas = json.loads((rutas.CLASIFICACION / f'{pid}.json').read_text(encoding='utf-8'))
    return [{'id': s['id'], 'formacion': sigla, 'tipo': 'medida numerada', 'ref': s['ref'],
             'pagina': s['pagina'], 'apartado': ' › '.join(s.get('apartado') or []),
             'titulo': s['titulo'], 'texto': s['texto'],
             'temas_herramienta': temas.get(s['id'], [])}
            for s in cargar(pid) if s['aviso'] != 'por anunciar']


def _palabras(u):
    return len((u.get('titulo', '') + ' ' + u['texto']).split())


def formaciones_con_lotes():
    """Formaciones que ya tienen lotes del IGDS (codificados o no)."""
    return {u['id'].split('-')[0] for f in _lotes()
            for u in json.loads(f.read_text(encoding='utf-8'))['unidades']}


def formaciones_codificadas():
    """Formaciones con TODOS sus lotes codificados: solo esas entran en el
    cálculo y en la muestra de validación."""
    lotes_de = {}
    for f in _lotes():
        for pid in {u['id'].split('-')[0] for u in json.loads(f.read_text(encoding='utf-8'))['unidades']}:
            lotes_de.setdefault(pid, []).append(f.name)
    return {pid for pid, nombres in lotes_de.items()
            if all((rutas.IGDS_CODIFICACION / n).exists() for n in nombres)}


def preparar(pids, forzar=False):
    """Lotes temáticos que mezclan formaciones (la misma persona codificadora
    aplica la misma regla a medidas parecidas de partidos distintos) y, al
    final, los lotes de prosa con la lista de medidas numeradas de referencia
    para detectar repeticiones.

    Si ya hay lotes, NO se rehacen (la codificación va ligada a su número):
    solo se añaden, con números nuevos, los de las formaciones que aún no
    tienen. Rehacerlo todo exige --forzar y deja huérfana la codificación."""
    cfg = config.igds()
    existentes = _lotes()
    primero = 1
    if existentes and not forzar:
        ya = formaciones_con_lotes()
        pids = [p for p in pids if p not in ya]
        if not pids:
            print(f'   Ya hay lotes para {", ".join(sorted(ya))}. No se rehacen: la codificación depende de ellos.')
            print('   (Para empezar de cero, con la codificación ya hecha huérfana: igds preparar --forzar)')
            return True
        primero = max(int(f.stem.split('-')[1]) for f in existentes) + 1
        print(f'   Se añaden lotes para {", ".join(pids)} a partir de lote-{primero:02d}; los existentes no se tocan.')
    orden = {t: i for i, t in enumerate(config.ids_temas())}
    numeradas = [u for pid in pids for u in _unidades_numeradas(pid)]
    numeradas.sort(key=lambda u: (orden.get((u['temas_herramienta'] or ['zzz'])[0], 99), u['id']))
    lotes, actual, palabras = [], [], 0
    tope = cfg.get('unidades_por_lote', 10 ** 6)  # programas de medidas cortas (PSOE): no más de N unidades
    for u in numeradas:
        if actual and (palabras + _palabras(u) > cfg['palabras_por_lote'] or len(actual) >= tope):
            lotes.append(actual)
            actual, palabras = [], 0
        actual.append(u)
        palabras += _palabras(u)
    if actual and lotes and palabras < 0.3 * cfg['palabras_por_lote']:
        lotes[-1] += actual  # un resto pequeño se suma al último lote
    elif actual:
        lotes.append(actual)

    for pid in pids:  # lotes de prosa por formación, con sus medidas numeradas de referencia
        sigla = config.partido(pid)['sigla']
        prosa, palabras = [], 0
        for b in bloques_prosa(pid):
            u = {**b, 'formacion': sigla, 'tipo': 'prosa', 'titulo': ''}
            if prosa and palabras + _palabras(u) > cfg['palabras_por_lote']:
                lotes.append(prosa)
                prosa, palabras = [], 0
            prosa.append(u)
            palabras += _palabras(u)
        if prosa:
            lotes.append(prosa)

    rutas.IGDS_LOTES.mkdir(parents=True, exist_ok=True)
    if primero == 1:
        if forzar and any(rutas.IGDS_CODIFICACION.glob('lote-*.json')):
            print('   ⚠ --forzar: los lotes se rehacen y la codificación de datos/igds/codificacion/ queda huérfana.')
        for f in rutas.IGDS_LOTES.glob('lote-*.json'):
            f.unlink()
    for i, unidades in enumerate(lotes, primero):
        nombre = f'lote-{i:02d}'
        doc = {'lote': nombre, 'criterios': 'docs/CRITERIOS-IGDS.md',
               'salida': f'datos/igds/codificacion/{nombre}.json', 'unidades': unidades}
        if unidades[0]['tipo'] == 'prosa':
            doc['referencia'] = {}
            for pid in sorted({u['id'].split('-')[0] for u in unidades}):
                numeradas_pid = _unidades_numeradas(pid)
                corto = 18 if len(numeradas_pid) > 300 else 30  # programas largos: referencia más breve
                doc['referencia'][pid] = [{'id': u['id'], 'titulo': u['titulo'],
                                           'inicio': ' '.join(u['texto'].split()[:corto])} for u in numeradas_pid]
        (rutas.IGDS_LOTES / f'{nombre}.json').write_text(json.dumps(doc, ensure_ascii=False, indent=1),
                                                         encoding='utf-8')
        cuenta = Counter(u['formacion'] for u in unidades)
        print(f'   {nombre}: {len(unidades)} unidades · {sum(_palabras(u) for u in unidades)} palabras · '
              f'{dict(cuenta)}{" · prosa" if unidades[0]["tipo"] == "prosa" else ""}')
    return True


# ── Validación ──────────────────────────────────────────────────────────
def _lotes():
    return sorted(rutas.IGDS_LOTES.glob('lote-*.json'))


def _ids_validos():
    ids = set()
    for f in _lotes():
        ids |= {u['id'] for u in json.loads(f.read_text(encoding='utf-8'))['unidades']}
    return ids


def validar_lote(ruta_lote, ids_validos=None):
    cfg = config.igds()
    areas = {a['id'] for a in cfg['areas']}
    maxp = cfg['fragmento_max_palabras']
    lote = json.loads(ruta_lote.read_text(encoding='utf-8'))
    salida = rutas.IGDS_CODIFICACION / f'{lote["lote"]}.json'
    if not salida.exists():
        return None, []
    try:
        cod = json.loads(salida.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        return {}, [f'JSON no válido: {e}']
    errores = []
    unidades = {u['id']: u for u in lote['unidades']}
    got = cod.get('unidades', {})
    for falta in sorted(set(unidades) - set(got)):
        errores.append(f'{falta}: falta la unidad')
    for sobra in sorted(set(got) - set(unidades)):
        errores.append(f'{sobra}: la unidad no es de este lote')
    for uid, reg in got.items():
        if uid not in unidades:
            continue
        u = unidades[uid]
        fuente = esqueleto((u.get('titulo') or '') + ' ' + u['texto'])
        meds = reg.get('medidas')
        if not isinstance(meds, list):
            errores.append(f'{uid}: «medidas» tiene que ser una lista')
            continue
        if not meds and not str(reg.get('sin_medidas', '')).strip():
            errores.append(f'{uid}: sin medidas y sin explicar por qué («sin_medidas»)')
        for k, m in enumerate(meds, 1):
            tag = f'{uid} #{k}'
            for campo in ['fragmento', 'medida_sintesis', 'area', *DIMS, *MARCAS, 'justificacion',
                          'confianza', 'revisar']:
                if campo not in m:
                    errores.append(f'{tag}: falta «{campo}»')
            if any(campo not in m for campo in [*DIMS, *MARCAS, 'fragmento', 'area']):
                continue
            if any(m[d] not in (0, 1) for d in [*DIMS, *MARCAS, 'revisar'] if d in m):
                errores.append(f'{tag}: las dimensiones, marcas y «revisar» valen 0 o 1')
                continue
            frag = str(m['fragmento']).strip()
            if not frag:
                errores.append(f'{tag}: fragmento vacío')
            elif len(frag.split()) > maxp:
                errores.append(f'{tag}: fragmento de {len(frag.split())} palabras (máx. {maxp})')
            elif esqueleto(frag) not in fuente:
                errores.append(f'{tag}: el fragmento no es literal: «{frag[:70]}»')
            if m['area'] not in areas:
                errores.append(f'{tag}: área «{m["area"]}» desconocida')
            if m['dec'] == 1 and m['exi'] == 1:
                errores.append(f'{tag}: DEC = 1 exige EXI = 0')
            if m['reg'] == 1 and all(m[d] == 1 for d in DIMS):
                errores.append(f'{tag}: REG = 1 exige alguna dimensión a 0')
            just = str(m.get('justificacion', ''))
            for d in DIMS:
                if m[d] == 0 and d.upper() not in just:
                    errores.append(f'{tag}: {d.upper()} vale 0 y la justificación no lo explica')
            if m.get('confianza') not in CONFIANZA:
                errores.append(f'{tag}: confianza «{m.get("confianza")}» (alta, media o baja)')
            if m.get('confianza') == 'baja' and m.get('revisar') != 1:
                errores.append(f'{tag}: confianza baja exige revisar = 1')
            if m.get('revisar') == 1 and not str(m.get('motivo_revision', '')).strip():
                errores.append(f'{tag}: revisar = 1 sin «motivo_revision»')
            for campo in ['medida_sintesis', 'justificacion', 'motivo_revision']:
                if re.search('[—–]', str(m.get(campo, ''))):
                    errores.append(f'{tag}: raya en «{campo}» (usa guion corto o reformula)')
            rep = str(m.get('repite', '') or '')
            if rep and ids_validos is not None and rep not in ids_validos:
                errores.append(f'{tag}: «repite» apunta a «{rep}», que no existe')
            if rep and rep.split('-')[0] != uid.split('-')[0]:
                errores.append(f'{tag}: «repite» apunta a otra formación')
    return cod, errores


def validar(lote=None):
    rutas.IGDS_CODIFICACION.mkdir(parents=True, exist_ok=True)
    ids = _ids_validos()
    rutas_lotes = [rutas.IGDS_LOTES / f'{lote}.json'] if lote else _lotes()
    if not rutas_lotes or not rutas_lotes[0].exists():
        print('   No hay lotes. Ejecuta antes: python3 maestro.py igds preparar')
        return False
    ok, pendientes = True, []
    for r in rutas_lotes:
        cod, errores = validar_lote(r, ids)
        if cod is None:
            pendientes.append(r.stem)
            continue
        n = sum(len(v.get('medidas', [])) for v in cod.get('unidades', {}).values())
        if errores:
            ok = False
            print(f'   ✗ {r.stem}: {len(errores)} errores ({n} medidas)')
            for e in errores[:40]:
                print(f'        {e}')
            if len(errores) > 40:
                print(f'        … y {len(errores) - 40} más')
        else:
            print(f'   ✓ {r.stem}: {n} medidas sin errores')
    if pendientes:
        print(f'   Sin codificar todavía: {", ".join(pendientes)}')
    return ok and not pendientes


# ── Cálculo ─────────────────────────────────────────────────────────────
def _pct(a, b):
    return round(100 * a / b, 1) if b else None


def _fmt(v):
    return '-' if v is None else f'{v:.1f}'.replace('.', ',')


def _pagina(frag, u, esq_pags):
    """Página donde aparece el fragmento (la medida puede cruzar de página)."""
    e = esqueleto(frag)
    desde = u['pagina']
    for n in range(desde, min(desde + 4, len(esq_pags) + 1)):
        if e in esq_pags[n - 1] or e[:40] in esq_pags[n - 1]:
            return n
    return desde


def _indices(filas):
    n = len(filas)
    s = {k: sum(f[k] for f in filas) for k in [*DIMS, 'g', *MARCAS]}
    r = {'n': n, 'sumas': s}
    for d in DIMS:
        r[f'i_{d}'] = _pct(s[d], n)
    r['igds'] = _pct(s['g'], n)
    r['ir'] = _pct(s['reg'], n)
    r['iv'] = _pct(s['dec'], n)
    if n:
        minimo = min(r[f'i_{d}'] for d in DIMS)
        r['limitante'] = [d.upper() for d in DIMS if r[f'i_{d}'] == minimo]
    return r


AJUSTES = 'ajustes.json'


def _ajustes():
    """Ajustes de coherencia entre lotes (datos/igds/ajustes.json): la misma
    regla aplicada igual a todas las formaciones cuando dos lotes la leyeron
    distinto. No se tocan los archivos de codificación: cada ajuste queda a
    la vista, con su regla, para la validación humana."""
    ruta = rutas.IGDS / AJUSTES
    if not ruta.exists():
        return {}
    doc = json.loads(ruta.read_text(encoding='utf-8'))
    salida = {}
    # Una medida puede estar en varios grupos (p. ej., un ajuste de coherencia
    # y después un cambio de criterio): se aplican en el orden del archivo y,
    # si dos tocan el mismo campo, manda el último.
    for grupo in doc['grupos']:
        nuevo = {'regla': grupo['regla'], 'cambios': grupo['cambios'], 'nota': grupo.get('nota', '')}
        for i in grupo['ids']:
            previo = salida.get(i)
            salida[i] = nuevo if not previo else {
                'regla': f'{previo["regla"]} · {nuevo["regla"]}',
                'cambios': {**previo['cambios'], **nuevo['cambios']},
                'nota': ' '.join(x for x in (previo['nota'], nuevo['nota']) if x),
            }
    return salida


SIGLAS = re.compile(r'^((?:UNI|EXI|DES|NDI|REG|DEC)(?:,\s*|\s+y\s+)?)+\s*[01]\s*:')


def _rehacer_justificacion(texto, cambiadas, nota):
    """Quita las frases que justificaban el valor anterior de lo que cambia
    («DES 0: …» si DES pasa a 1) y añade la nota del ajuste."""
    frases = [f for f in re.split(r'(?<=\.)\s+', texto.strip()) if f]
    quedan = []
    for f in frases:
        m = SIGLAS.match(f)
        if m and set(re.findall(r'UNI|EXI|DES|NDI|REG|DEC', m.group(0))) & {c.upper() for c in cambiadas}:
            continue
        quedan.append(f)
    return ' '.join(quedan + ([nota] if nota else [])).strip()


def _medidas(pids, ajustar=True):
    """Todas las medidas codificadas, con los ajustes de coherencia aplicados.
    Devuelve (medidas, repeticiones, errores de ajuste)."""
    cfg = config.igds()
    ajustes = _ajustes() if ajustar else {}
    filas, repetidas, vistos = [], [], set()
    for r in _lotes():
        lote = json.loads(r.read_text(encoding='utf-8'))
        ruta = rutas.IGDS_CODIFICACION / r.name
        if not ruta.exists():
            continue
        cod = json.loads(ruta.read_text(encoding='utf-8'))
        for u in lote['unidades']:
            pid = u['id'].split('-')[0]
            if pid not in pids or u['id'] not in cod['unidades']:
                continue
            for k, m in enumerate(cod['unidades'][u['id']]['medidas'], 1):
                fila = {
                    'pid': pid, 'unidad': u['id'], 'tipo': u['tipo'],
                    'id_medida': f'{u["id"]}-{k:02d}', 'formacion': u['formacion'], 'eleccion': cfg['eleccion'],
                    'pagina': u['pagina'], 'fragmento': m['fragmento'].strip(),
                    'medida_sintesis': m['medida_sintesis'].strip(), 'area': m['area'],
                    **{d: m[d] for d in DIMS}, **{x: m[x] for x in MARCAS},
                    'justificacion': m['justificacion'].strip(),
                    'confianza': m['confianza'], 'revisar': m['revisar'],
                    'motivo_revision': str(m.get('motivo_revision', '')).strip(),
                    'repite': str(m.get('repite', '') or ''), 'ajuste': '',
                }
                a = ajustes.get(fila['id_medida'])
                if a:
                    vistos.add(fila['id_medida'])
                    cambiadas = [k for k, v in a['cambios'].items() if k in DIMS + MARCAS and fila[k] != v]
                    fila.update(a['cambios'])
                    if cambiadas or a['nota']:
                        fila['justificacion'] = _rehacer_justificacion(fila['justificacion'], cambiadas, a['nota'])
                    fila['ajuste'] = a['regla']
                fila['g'] = int(all(fila[d] for d in DIMS))
                (repetidas if fila['repite'] else filas).append(fila)
    errores = [f'ajuste para «{i}», que no existe' for i in sorted(set(ajustes) - vistos) if i.split('-')[0] in pids]
    for f in filas:
        if f['ajuste']:
            if f['dec'] and f['exi']:
                errores.append(f'{f["id_medida"]}: tras el ajuste, DEC = 1 con EXI = 1')
            if f['reg'] and f['g']:
                errores.append(f'{f["id_medida"]}: tras el ajuste, REG = 1 con g = 1')
            for d in DIMS:
                if f[d] == 0 and d.upper() not in f['justificacion']:
                    errores.append(f'{f["id_medida"]}: tras el ajuste, {d.upper()} 0 sin justificar')
    return filas, repetidas, errores


def calcular(pids):
    if not validar():
        print('   ✗ La codificación tiene errores o lotes pendientes: no se calcula.')
        return False
    cfg = config.igds()
    areas = [a['id'] for a in cfg['areas']]
    nombre_area = {a['id']: a['nombre'] for a in cfg['areas']}
    f0 = json.loads((rutas.IGDS / 'fase0.json').read_text(encoding='utf-8')) if (rutas.IGDS / 'fase0.json').exists() else fase0(pids)

    filas, repetidas, errores = _medidas(pids)
    if errores:
        print('   ✗ Ajustes de coherencia con errores (datos/igds/ajustes.json):')
        for e in errores:
            print(f'        {e}')
        return False

    esq = {pid: [esqueleto(p) for p in paginas(pid)] for pid in pids}
    unidades = {u['id']: u for r in _lotes() for u in json.loads(r.read_text(encoding='utf-8'))['unidades']}
    for f in filas:
        if f['tipo'] == 'medida numerada':
            f['pagina'] = _pagina(f['fragmento'], unidades[f['unidad']], esq[f['pid']])

    orden_pid = {pid: i for i, pid in enumerate(pids)}
    # Primero las medidas numeradas y después las que salen de la prosa.
    filas.sort(key=lambda f: (orden_pid[f['pid']], f['tipo'] == 'prosa', f['id_medida']))

    rutas.IGDS.mkdir(parents=True, exist_ok=True)
    with open(rutas.IGDS / 'igds-medidas.csv', 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh, delimiter=';')
        w.writerow(CAMPOS_CSV)
        for f in filas:
            w.writerow([f[c] for c in CAMPOS_CSV])

    resultados = {}
    with open(rutas.IGDS / 'igds-areas.csv', 'w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh, delimiter=';')
        w.writerow(['formacion', 'area', 'n', 'i_uni', 'i_exi', 'i_des', 'i_ndi', 'igds', 'ir', 'iv'])
        for pid in pids:
            fp = [f for f in filas if f['pid'] == pid]
            g = _indices(fp)
            por_area = {a: _indices([f for f in fp if f['area'] == a]) for a in areas}
            for a in areas:
                x = por_area[a]
                w.writerow([config.partido(pid)['sigla'], a, x['n'],
                            *[_fmt(x[k]) for k in ['i_uni', 'i_exi', 'i_des', 'i_ndi', 'igds', 'ir', 'iv']]])
            control = {
                'igds_menor_o_igual_que_min_ik': g['n'] == 0 or g['igds'] <= min(g[f'i_{d}'] for d in DIMS),
                'dec_implica_exi_0': all(not (f['dec'] and f['exi']) for f in fp),
                'g_1_implica_todas_1': all(f['g'] == int(all(f[d] for d in DIMS)) for f in fp),
                'reg_implica_g_0': all(not (f['reg'] and f['g']) for f in fp),
                'suma_areas_igual_n': sum(por_area[a]['n'] for a in areas) == g['n'],
                'sin_ids_duplicados': len({f['id_medida'] for f in fp}) == len(fp),
            }
            resultados[pid] = {
                'sigla': config.partido(pid)['sigla'], 'global': g, 'areas': por_area,
                'silencio': [a for a in areas if por_area[a]['n'] == 0],
                'control': control,
                'medidas_de_prosa': sum(1 for f in fp if f['tipo'] == 'prosa'),
                'repeticiones_descartadas': [
                    {'unidad': r['unidad'], 'sintesis': r['medida_sintesis'], 'repite': r['repite']}
                    for r in repetidas if r['pid'] == pid],
                'dudosos': [{'id': f['id_medida'], 'area': f['area'], 'sintesis': f['medida_sintesis'],
                             'motivo': f['motivo_revision'], 'confianza': f['confianza']}
                            for f in fp if f['revisar']],
                'confianza': dict(Counter(f['confianza'] for f in fp)),
                'ajustes': dict(Counter(f['ajuste'] for f in fp if f['ajuste'])),
            }
    (rutas.IGDS / 'igds-resultados.json').write_text(json.dumps(resultados, ensure_ascii=False, indent=1),
                                                     encoding='utf-8')
    _web(pids, filas, resultados)
    _informe(pids, resultados, f0, nombre_area, cfg)
    for pid in pids:
        g = resultados[pid]['global']
        print(f'   {resultados[pid]["sigla"]}: N {g["n"]} · IGDS {_fmt(g["igds"])} · UNI {_fmt(g["i_uni"])} · '
              f'EXI {_fmt(g["i_exi"])} · DES {_fmt(g["i_des"])} · NDI {_fmt(g["i_ndi"])} · IR {_fmt(g["ir"])} · '
              f'IV {_fmt(g["iv"])} · limitante {"/".join(g.get("limitante", []))} · '
              f'control {"✓" if all(resultados[pid]["control"].values()) else "✗"}')
    print(f'   → {rutas.relativa(rutas.IGDS / "igds-medidas.csv")} · {rutas.relativa(rutas.IGDS / "igds-areas.csv")} · '
          f'{rutas.relativa(rutas.INFORMES / "igds.md")}')
    return all(all(r['control'].values()) for r in resultados.values())


# ── Resumen para la herramienta ─────────────────────────────────────────
# Cada medida va a UNA categoría, en este orden (es también el orden de las
# casillas en el gráfico «De cada 100 medidas»). La marca DEC se cuenta
# aparte dentro de cada categoría: una declarativa puede estar en cualquiera.
CATEGORIAS_WEB = ['g', 'near', 'otros', 'reg', 'fuera']
# Categorías cuyas medidas se pueden leer en la herramienta (fragmento literal).
LEGIBLES_WEB = ['g', 'near', 'reg']
WEB_JSON = 'igds-web.json'                                    # resumen: va dentro del JS
WEB_MEDIDAS = rutas.WEB / 'public' / 'data' / 'igds-medidas.json'  # textos: se piden al abrir una lista


def _categoria(f):
    """g: las cuatro dimensiones · reg: regresiva · near: tres de cuatro (sin
    ser regresiva) · otros: una o dos · fuera: ninguna (no trata un derecho social)."""
    s = sum(f[d] for d in DIMS)
    if f['g']:
        return 'g'
    if f['reg']:
        return 'reg'
    return 'near' if s == 3 else 'otros' if s else 'fuera'


def _web(pids, filas, resultados):
    """Lo que necesita el apartado IGDS de la web (web/src/componentes/Garantias.jsx),
    en dos archivos para no cargar el JS de la herramienta con textos:
      · datos/igds/igds-web.json (va dentro del JS): recuentos por categoría,
        la dimensión que falta en las medidas a una respuesta y las áreas;
      · web/public/data/igds-medidas.json (se publica junto al CSV y se pide
        solo al abrir una lista): síntesis y fragmento literal de las medidas
        de las categorías que se pueden leer, con su página.
    Se genera aquí para que la web no recalcule nada: la regla es la de este módulo."""
    resumen = {
        '_leeme': 'Generado por «python3 maestro.py igds calcular»: no se edita a mano. Lo usa la web '
                  '(apartado IGDS). Categorías exclusivas en este orden; cada una con [medidas, de ellas declarativas].',
        'categorias': CATEGORIAS_WEB,
        'partidos': {},
    }
    textos = {'_leeme': 'Generado por «python3 maestro.py igds calcular». Por partido y categoría: '
                        '[página, área, síntesis, fragmento literal] y, en «near», la dimensión que falta.'}
    for pid in pids:
        fp = [f for f in filas if f['pid'] == pid]
        cats = {k: [0, 0] for k in CATEGORIAS_WEB}
        medidas = {k: [] for k in LEGIBLES_WEB}
        areas = {k: Counter() for k in LEGIBLES_WEB}
        falta = Counter()
        for f in fp:
            k = _categoria(f)
            cats[k][0] += 1
            cats[k][1] += f['dec']
            if k not in medidas:
                continue
            m = [f['pagina'], f['area'], f['medida_sintesis'], f['fragmento']]
            if k == 'near':
                d = next(d for d in DIMS if not f[d])
                m.append(d)
                falta[d] += 1
            medidas[k].append(m)
            areas[k][f['area']] += 1
        g = resultados[pid]['global']
        resumen['partidos'][pid] = {
            'n': len(fp), 'igds': g['igds'], 'ir': g['ir'], 'iv': g['iv'],
            'limitante': g.get('limitante', []), 'categorias': cats,
            'falta': dict(falta.most_common()),
            'areas': {k: dict(v.most_common()) for k, v in areas.items()},
        }
        textos[pid] = medidas
    (rutas.IGDS / WEB_JSON).write_text(json.dumps(resumen, ensure_ascii=False, indent=1), encoding='utf-8')
    WEB_MEDIDAS.parent.mkdir(parents=True, exist_ok=True)
    WEB_MEDIDAS.write_text(json.dumps(textos, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')


def _informe(pids, res, f0, nombre_area, cfg):
    L = ['# IGDS · Resultados de la prueba', '',
         f'{cfg["eleccion"]}. **Primera codificación, pendiente de validación humana.** '
         'Libro de códigos y reglas operativas: [docs/CRITERIOS-IGDS.md](../../docs/CRITERIOS-IGDS.md). '
         'Tabla de medidas: [datos/igds/igds-medidas.csv](../igds/igds-medidas.csv). '
         'Generado por `python3 maestro.py igds calcular`: no se edita a mano.', '',
         *[f'{x["sigla"]} no se codifica: ' + ('su programa aún no está publicado.' if not x['programa']
                                                else 'su programa aún no está codificado.')
           for x in config.partidos() if x['id'] not in pids], '']

    L += ['## Resumen', '', '| Formación | N | IGDS | I_UNI | I_EXI | I_DES | I_NDI | IR | IV | Limitante |',
          '|---|---|---|---|---|---|---|---|---|---|']
    for pid in pids:
        g = res[pid]['global']
        L.append(f'| {res[pid]["sigla"]} | {g["n"]} | {_fmt(g["igds"])} | {_fmt(g["i_uni"])} | {_fmt(g["i_exi"])} | '
                 f'{_fmt(g["i_des"])} | {_fmt(g["i_ndi"])} | {_fmt(g["ir"])} | {_fmt(g["iv"])} | '
                 f'{"/".join(g.get("limitante", []))} |')
    L.append('')

    for pid in pids:
        r, g, f = res[pid], res[pid]['global'], f0.get(pid, {})
        s = g['sumas']
        L += [f'## {r["sigla"]}', '', '### 1. Fase 0 · Viabilidad', '']
        L += [
            f'- «{f.get("programa")}»: {f.get("paginas")} páginas; índice {"sí" if f.get("indice") else "no"}; '
            f'{f.get("apartados")} apartados detectados.',
            f'- Páginas sin texto: {len(f.get("paginas_sin_texto", []))} (portadas, fotografías, separadores o en blanco; '
            'revisadas a la vista: ninguna es una imagen con medidas).',
            f'- {f.get("numeradas")} medidas numeradas y {len(f.get("bloques_prosa", []))} bloques de prosa '
            f'({f.get("palabras_prosa")} palabras); texto asignado a una unidad: {_fmt(f.get("cobertura", 0) * 100)} % '
            '(el resto son títulos, índice y numeración).',
            f'- Huecos «por anunciar» del propio PDF: {len(f.get("por_anunciar", []))}'
            f'{" (" + ", ".join(f["por_anunciar"]) + ")" if f.get("por_anunciar") else ""}; '
            f'medidas cortadas en el original: {", ".join(f.get("cortadas", [])) or "ninguna"}.',
            '- Texto completo y legible: se codifica.', '']
        L += ['### 3. Resultados globales', '', '| Indicador | Valor | Numerador / denominador |', '|---|---|---|']
        for etq, k, num in [('I_UNI', 'i_uni', s['uni']), ('I_EXI', 'i_exi', s['exi']), ('I_DES', 'i_des', s['des']),
                            ('I_NDI', 'i_ndi', s['ndi']), ('**IGDS**', 'igds', s['g']), ('IR', 'ir', s['reg']),
                            ('IV', 'iv', s['dec'])]:
            L.append(f'| {etq} | {_fmt(g[k])} | {num} / {g["n"]} |')
        L += ['', f'N = {g["n"]} medidas ({r["medidas_de_prosa"]} salen de la prosa). '
              f'Dimensión limitante: **{"/".join(g.get("limitante", []))}**. '
              f'Confianza: {", ".join(f"{k} {v}" for k, v in sorted(r["confianza"].items()))}.', '']
        L += ['### 4. Matriz por área temática', '', '| area | n | i_uni | i_exi | i_des | i_ndi | igds | ir | iv |',
              '|---|---|---|---|---|---|---|---|---|']
        for a, x in r['areas'].items():
            if x['n']:
                L.append(f'| {a} {nombre_area[a]} | {x["n"]} | {_fmt(x["i_uni"])} | {_fmt(x["i_exi"])} | '
                         f'{_fmt(x["i_des"])} | {_fmt(x["i_ndi"])} | {_fmt(x["igds"])} | {_fmt(x["ir"])} | {_fmt(x["iv"])} |')
        L += ['', '### 5. Silencios, control de calidad y casos dudosos', '',
              f'**Áreas en silencio:** {", ".join(f"{a} {nombre_area[a]}" for a in r["silencio"]) or "ninguna"}.', '',
              '**Control de calidad:** ' + ' · '.join(f'{k.replace("_", " ")} {"✓" if v else "✗"}'
                                                     for k, v in r['control'].items()) + '.', '',
              f'**Repeticiones descartadas** (no cuentan en N): {len(r["repeticiones_descartadas"])}.', '']
        for x in r['repeticiones_descartadas']:
            L.append(f'- {x["unidad"]}: {x["sintesis"]} → repite {x["repite"]}')
        L += ['', f'**Ajustes de coherencia aplicados** (datos/igds/ajustes.json): '
              f'{sum(r["ajustes"].values())}.', '']
        for regla, n in r['ajustes'].items():
            L.append(f'- {n} · {regla}')
        L += ['', f'**Casos dudosos:** {len(r["dudosos"])}.', '']
        for x in r['dudosos']:
            L.append(f'- `{x["id"]}` ({x["area"]}, confianza {x["confianza"]}): {x["sintesis"]}. {x["motivo"]}')
        L.append('')
    rutas.INFORMES.mkdir(parents=True, exist_ok=True)
    cab = obsidian.cabecera('proyecto', 'analisis', ['igds', 'resultados'], 'IGDS · resultados', 'datos/informes/igds.md')
    (rutas.INFORMES / 'igds.md').write_text(cab + '\n'.join(L) + '\n', encoding='utf-8')


# ── Contraste ───────────────────────────────────────────────────────────
# Señales de texto que suelen ir con un código concreto. No corrigen nada:
# listan para revisión humana las medidas cuyo código no casa con la señal,
# para comprobar que la misma regla se ha aplicado igual a todas las formaciones.
SENALES = [
    ('fiscal', re.compile(r'deducc|desgrav|bonific|exenci|\biva\b|\birpf\b|tipo reducido|rebaja fiscal|incentivos? fiscal', re.I),
     lambda m: m['des'] == 0 and m['exi'] == 0, 'beneficio fiscal: se espera DES 0 y EXI 0'),
    ('blando', re.compile(r'\b(impuls|foment|promov|estudiar|estudio\b|campaña|convocatoria)', re.I),
     lambda m: m['exi'] == 0, 'verbo blando, plan o convocatoria: se espera EXI 0'),
    ('exclusion', re.compile(r'prioridad nacional|españoles primero|únicamente|solo (a|para) (los )?españoles|extranjer|ilegal|irregular', re.I),
     lambda m: m['ndi'] == 0, 'posible cláusula de exclusión: se espera NDI 0'),
    ('gratuidad', re.compile(r'gratuit', re.I),
     lambda m: m['des'] == 1, 'gratuidad: se espera DES 1'),
]
VACIAS = set('de la el los las y a en por para con del al que se un una su sus o lo como más sin entre '
             'sobre todo toda todos todas este esta estos estas'.split())


def _contenido(t):
    return {w for w in re.findall(r'[a-záéíóúüñ]{4,}', t.lower()) if w not in VACIAS}


def contrastar(pids):
    """Informe para la revisión humana: medidas con g = 1, medidas regresivas,
    señales de texto que no casan con el código y posibles repeticiones entre
    lotes. Escribe datos/informes/igds-contraste.md."""
    vivas, _, errores = _medidas(pids)
    for e in errores:
        print(f'   ✗ {e}')
    for f in vivas:
        f['sigla'], f['id'] = f['formacion'], f['id_medida']

    def linea(f):
        return (f'- `{f["id"]}`{" ⚙" if f.get("ajuste") else ""} {f["sigla"]} · {f["area"]} · '
                f'{"".join(str(f[d]) for d in DIMS)} g{f["g"]} R{f["reg"]} D{f["dec"]} · {f["medida_sintesis"]}')

    L = ['# IGDS · Contraste para la revisión humana', '',
         'Generado por `python3 maestro.py igds contrastar`, con los ajustes de coherencia ya aplicados '
         '(marcados con ⚙). Códigos: UNI EXI DES NDI, g, REG (R), DEC (D).', '']
    L += [f'## Medidas con g = 1 ({sum(f["g"] for f in vivas)})', '']
    L += [linea(f) for f in vivas if f['g']]
    L += ['', f'## Medidas regresivas ({sum(f["reg"] for f in vivas)})', '']
    L += [linea(f) for f in vivas if f['reg']]
    L += ['', '## Señales de texto que no casan con el código', '',
          'Solo medidas que tratan un derecho social (alguna dimensión a 1) o, para la exclusión, todas.', '']
    for nombre, rx, espera, texto in SENALES:
        raras = [f for f in vivas if rx.search(f['fragmento'] + ' ' + f['medida_sintesis'])
                 and (nombre == 'exclusion' or any(f[d] for d in DIMS)) and not espera(f)]
        L += [f'### {nombre} · {texto} ({len(raras)})', ''] + [linea(f) for f in raras] + ['']
    L += ['## Posibles repeticiones entre unidades (misma formación, síntesis parecidas)', '']
    pares = []
    for pid in pids:
        fp = [f for f in vivas if f['pid'] == pid]
        conj = [(f, _contenido(f['medida_sintesis'])) for f in fp]
        for i, (a, ca) in enumerate(conj):
            for b, cb in conj[i + 1:]:
                if a['unidad'] == b['unidad'] or not ca or not cb:
                    continue
                j = len(ca & cb) / len(ca | cb)
                if j >= 0.5:
                    pares.append((j, a, b))
    for j, a, b in sorted(pares, key=lambda x: -x[0]):
        L.append(f'- {j:.2f} · `{a["id"]}` {a["medida_sintesis"]} ↔ `{b["id"]}` {b["medida_sintesis"]}')
    rutas.INFORMES.mkdir(parents=True, exist_ok=True)
    cab = obsidian.cabecera('proyecto', 'analisis', ['igds', 'contraste', 'revision-humana'], 'IGDS · contraste para la revisión',
                            'datos/informes/igds-contraste.md')
    (rutas.INFORMES / 'igds-contraste.md').write_text(cab + '\n'.join(L) + '\n', encoding='utf-8')
    print(f'   {len(vivas)} medidas · g = 1: {sum(f["g"] for f in vivas)} · REG: {sum(f["reg"] for f in vivas)} · '
          f'posibles repeticiones: {len(pares)} → {rutas.relativa(rutas.INFORMES / "igds-contraste.md")}')
    return True


def ejecutar(accion, pids, lote=None, forzar=False, explicitos=False):
    # Sin --partido, el cálculo y la validación solo usan las formaciones que ya
    # tienen lotes: un programa recién cargado no cambia los resultados ni la
    # muestra de validación hasta que se codifique.
    if accion in ('calcular', 'contrastar', 'muestra', 'concordancia') and not explicitos:
        ya = formaciones_codificadas()
        pids = [p for p in pids if p in ya]
    if accion == 'fase0':
        fase0(pids)
        return True
    if accion == 'preparar':
        fase0(pids)
        return preparar(pids, forzar=forzar)
    if accion == 'validar':
        return validar(lote)
    if accion == 'calcular':
        return calcular(pids)
    if accion == 'contrastar':
        return contrastar(pids)
    if accion in ('muestra', 'concordancia'):
        from . import igds_validacion  # aquí y no arriba: igds_validacion importa este módulo
        if accion == 'muestra':
            return igds_validacion.muestra(pids, forzar=forzar)
        return igds_validacion.concordancia(pids)
    raise SystemExit(f'Acción desconocida: {accion}')
