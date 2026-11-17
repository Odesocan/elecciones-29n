"""IGDS · Validación humana de la primera codificación.

    python3 maestro.py igds muestra        hojas de validación en datos/igds/validacion/
    python3 maestro.py igds muestra --rehacer-a   rehace solo la hoja A (clave nueva); B y C no cambian
    python3 maestro.py igds concordancia   acuerdo entre la codificación y la validación humana

Tres hojas (CSV con «;» en UTF-8, que se abren en Excel u otra hoja de cálculo):

  A · codificación ciega   Muestra aleatoria estratificada. La persona codifica sin ver
                           la codificación ni la formación. Mide la fiabilidad (kappa).
  B · verificación         Censo de lo que más pesa en los resultados: garantías completas
                           (g = 1), medidas regresivas y medidas con ajuste de coherencia.
                           La persona ve la codificación y dice si está de acuerdo.
  C · atomización          Muestra de unidades con su texto completo y las medidas que
                           salieron de él. Comprueba el denominador.

Semillas: la de config/igds.json es pública y fija la hoja C. La de la hoja A es secreta: se
sortea al generar la hoja y solo se guarda en clave-A.json, que no se publica; si fuera pública,
cualquiera podría rehacer la clave con ella. Una vez repartidas, las hojas no se sobrescriben si
alguien ya ha escrito en ellas (salvo con --forzar).
Instrucciones para el equipo: docs/VALIDACION-IGDS.md.
"""
import csv
import json
import random
import re
import secrets
from collections import Counter, defaultdict

from . import config, obsidian, rutas
from .igds import DIMS, MARCAS, _fmt, _lotes, _medidas

CARPETA = rutas.IGDS / 'validacion'
HOJAS = {'A': 'A-codificacion-ciega.csv', 'B': 'B-verificacion.csv', 'C': 'C-atomizacion.csv'}
CLAVE_A = 'clave-A.json'

COLS_A = ['codigo', 'pagina', 'texto_de_la_unidad', 'fragmento', 'medida_sintesis']
MANUAL_A = ['area', 'uni', 'exi', 'des', 'ndi', 'reg', 'dec', 'comentario']
COLS_B = ['id_medida', 'formacion', 'estrato', 'pagina', 'fragmento', 'medida_sintesis', 'area',
          *DIMS, 'g', *MARCAS, 'justificacion', 'ajuste']
MANUAL_B = ['de_acuerdo', 'correccion', 'comentario']
COLS_C = ['unidad', 'formacion', 'pagina', 'texto_de_la_unidad', 'medidas_extraidas', 'n_medidas']
MANUAL_C = ['valoracion', 'n_medidas_propuesto', 'comentario']
VALORACIONES = ['bien', 'faltan', 'sobran', 'mal divididas']
CAMPOS_CORRECCION = {*DIMS, *MARCAS, 'area', 'repite'}


def _textos_unidades():
    unidades = {}
    for r in _lotes():
        for u in json.loads(r.read_text(encoding='utf-8'))['unidades']:
            titulo = (u.get('titulo') or '').strip()
            unidades[u['id']] = {**u, 'completo': (f'{titulo}. ' if titulo else '') + u['texto']}
    return unidades


def _leer(ruta):
    if not ruta.exists():
        return []
    with open(ruta, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter=';'))


def _escribir(ruta, columnas, filas):
    with open(ruta, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(columnas)
        for fila in filas:
            w.writerow([fila.get(c, '') for c in columnas])


def _con_trabajo(carpeta):
    """Hojas en las que alguien ya ha escrito algo en las columnas manuales."""
    manuales = {'A': MANUAL_A, 'B': MANUAL_B, 'C': MANUAL_C}
    return [h for h, nombre in HOJAS.items()
            if any(any((f.get(c) or '').strip() for c in manuales[h]) for f in _leer(carpeta / nombre))]


# ── Muestra ─────────────────────────────────────────────────────────────
def _semilla_a():
    """Semilla de la hoja A: al azar y guardada solo en la clave. La de
    config/igds.json es pública y, con ella y los datos públicos, cualquiera
    podría rehacer la muestra y, con ella, la clave."""
    return secrets.randbits(63)


def _ciega(fp, rng, cfg, excluir):
    """Filas de la hoja A de una formación: al azar dentro de cada estrato,
    entre las medidas que no están en la hoja B (excluir)."""
    resto = [f for f in fp if f['id_medida'] not in excluir]
    social = [f for f in resto if any(f[d] for d in DIMS)]
    no_social = [f for f in resto if not any(f[d] for d in DIMS)]
    ciega = []
    for estrato, grupo, n in [('ambito social', social, cfg['ciega_ambito_social']),
                              ('resto', no_social, cfg['ciega_resto'])]:
        for f in rng.sample(grupo, min(n, len(grupo))):
            ciega.append({**f, 'estrato': estrato})
    return ciega, {'ambito social': len(social), 'resto': len(no_social)}


def _de(pid, filas):
    return sorted((f for f in filas if f['pid'] == pid), key=lambda f: f['id_medida'])


def _muestrear(pid, filas, rng_a, rng_c, cfg):
    """Muestra de una formación: filas para A (aleatorias por estrato, con la
    semilla secreta), censo para B y unidades para C (con la pública). El orden
    de las llamadas a cada rng importa: la muestra tiene que salir idéntica cada vez."""
    fp = _de(pid, filas)
    censo = [f for f in fp if f['g'] or f['reg'] or f['ajuste']]
    ciega, poblacion = _ciega(fp, rng_a, cfg, {f['id_medida'] for f in censo})
    verificar = []
    for f in censo:
        etiquetas = [e for e, si in [('g = 1', f['g']), ('regresiva', f['reg']), ('ajuste', f['ajuste'])] if si]
        verificar.append({**f, 'estrato': ', '.join(etiquetas)})
    ids_unidad = sorted({f['unidad'] for f in fp})
    atomizar = rng_c.sample(ids_unidad, min(cfg['unidades_atomizacion'], len(ids_unidad)))
    return ciega, verificar, atomizar, poblacion


def _clave_ajena(doc, medidas, carpeta):
    """Códigos de la hoja A cuya fila no es la medida que dice la clave: la
    clave es de otra hoja A (por ejemplo, la anterior a rehacerla)."""
    ia = {f['id_medida']: f for f in medidas}
    presentes = {f['pid'] for f in medidas}
    malos = []
    for fila in _leer(carpeta / HOJAS['A']):
        meta = doc['codigos'].get(fila['codigo'])
        if meta and meta['pid'] not in presentes:  # formación que no se está calculando (--partido)
            continue
        m = ia.get(meta['id_medida']) if meta else None
        if not m or m['fragmento'] != (fila.get('fragmento') or '').strip():
            malos.append(fila['codigo'])
    return malos


def _aviso_clave_ajena(malos):
    print(f'   ✗ {CLAVE_A} no corresponde a la hoja A ({len(malos)} códigos no cuadran: {", ".join(malos[:3])}…).')
    print('     Puede ser la clave de una hoja A anterior: pide al equipo de ODESOCAN la vigente.')


def _filas_a(ciega, unidades, primero=1):
    clave, filas = {}, []
    for i, f in enumerate(ciega, primero):
        codigo = f'A-{i:03d}'
        clave[codigo] = {'id_medida': f['id_medida'], 'pid': f['pid'], 'estrato': f['estrato']}
        filas.append({'codigo': codigo, 'pagina': f['pagina'], 'texto_de_la_unidad': unidades[f['unidad']]['completo'],
                      'fragmento': f['fragmento'], 'medida_sintesis': f['medida_sintesis']})
    return clave, filas


def _filas_b(verificar):
    return [{**f, 'justificacion': f['justificacion'] or 'Ninguna dimensión vale 0.'} for f in verificar]


def _filas_c(atomizar, todas, unidades):
    filas = []
    for uid in atomizar:
        ms = sorted((f for f in todas if f['unidad'] == uid), key=lambda f: f['id_medida'])
        filas.append({
            'unidad': uid, 'formacion': ms[0]['formacion'], 'pagina': unidades[uid]['pagina'],
            'texto_de_la_unidad': unidades[uid]['completo'],
            'medidas_extraidas': '\n'.join(f'{m["id_medida"]}: {m["medida_sintesis"]}'
                                           + (f' (repite {m["repite"]}, no cuenta)' if m['repite'] else '')
                                           for m in ms),
            'n_medidas': sum(1 for m in ms if not m['repite']),
        })
    return filas


def _resumen(filas_a, verificar, filas_c, por_a, siglas):
    print(f'   A · codificación ciega: {len(filas_a)} medidas ({", ".join(f"{s} {por_a[p]}" for p, s in siglas)}), '
          f'mezcladas y sin formación ni códigos · unas {_fmt(len(filas_a) * 2 / 60)} h')
    porb = Counter(f['formacion'] for f in verificar)
    print(f'   B · verificación: {len(verificar)} medidas ({", ".join(f"{k} {v}" for k, v in porb.items())}): '
          f'g = 1, regresivas y ajustadas · unas {_fmt(len(verificar) / 60)} h')
    print(f'   C · atomización: {len(filas_c)} unidades · unas {_fmt(len(filas_c) * 3 / 60)} h')


def muestra(pids, forzar=False, rehacer_a=False):
    cfg = config.igds()['validacion']
    filas, repetidas, errores = _medidas(pids)
    if errores:
        print('   ✗ Hay errores en los ajustes de coherencia; corrige antes: python3 maestro.py igds calcular')
        return False
    unidades = _textos_unidades()
    orden = {p['id']: i for i, p in enumerate(config.partidos())}
    pids = sorted(pids, key=lambda p: orden[p])
    if rehacer_a:
        return _rehacer_a(pids, filas, unidades, cfg, forzar)

    # Formación nueva con la muestra ya repartida: se AMPLÍA al final de las
    # hojas, con su propia semilla, sin cambiar ni una fila de las existentes.
    if (CARPETA / CLAVE_A).exists() and not forzar:
        doc = json.loads((CARPETA / CLAVE_A).read_text(encoding='utf-8'))
        malos = _clave_ajena(doc, filas + repetidas, CARPETA)
        if malos:
            _aviso_clave_ajena(malos)
            return False
        nuevas = [p for p in pids if p not in doc['poblacion']]
        if nuevas:
            return _ampliar(nuevas, doc, filas, repetidas, unidades, cfg)
        # Sin formaciones nuevas no hay nada que hacer: rehacer las tres hojas
        # cambiaría la B (codificación posterior) y la C. Solo con --forzar.
        print('   La muestra ya cubre todas las formaciones: no se rehace.')
        print('     Rehacer solo la hoja A: igds muestra --rehacer-a · las tres hojas: igds muestra --forzar')
        return True

    # Sin la clave (no se publica en el repositorio), rehacer la muestra cambiaría
    # los códigos de una hoja A ya repartida: mejor parar y pedirla.
    if not (CARPETA / CLAVE_A).exists() and (CARPETA / HOJAS['A']).exists() and not forzar:
        print(f'   ✗ Falta datos/igds/validacion/{CLAVE_A}: no está en el repositorio público, para que la hoja A siga siendo ciega.')
        print('     Pide la clave al equipo de ODESOCAN y cópiala en esa carpeta. No rehagas la muestra.')
        return False

    ocupadas = _con_trabajo(CARPETA)
    if ocupadas and not forzar:
        print(f'   ✗ Las hojas {", ".join(ocupadas)} ya tienen trabajo del equipo: no se sobrescriben.')
        print('     Si de verdad quieres rehacer la muestra: python3 maestro.py igds muestra --forzar')
        return False

    semilla_a = _semilla_a()
    rng_a, rng_c = random.Random(semilla_a), random.Random(cfg['semilla'])
    ciega, verificar, atomizar, poblacion = [], [], [], {}
    for pid in pids:
        c, v, a, pob = _muestrear(pid, filas, rng_a, rng_c, cfg)
        ciega += c
        verificar += v
        atomizar += a
        poblacion[pid] = pob
    rng_a.shuffle(ciega)  # mezcla formaciones y estratos: la persona no codifica por bloques

    CARPETA.mkdir(parents=True, exist_ok=True)
    clave, filas_a = _filas_a(ciega, unidades)
    _escribir(CARPETA / HOJAS['A'], COLS_A + MANUAL_A, filas_a)
    _guardar_clave({'semilla': cfg['semilla'], 'semilla_a': semilla_a, 'poblacion': poblacion, 'codigos': clave})
    _escribir(CARPETA / HOJAS['B'], COLS_B + MANUAL_B, _filas_b(verificar))
    filas_c = _filas_c(atomizar, filas + repetidas, unidades)
    _escribir(CARPETA / HOJAS['C'], COLS_C + MANUAL_C, filas_c)

    _resumen(filas_a, verificar, filas_c, Counter(c['pid'] for c in clave.values()),
             [(p, config.partido(p)['sigla']) for p in pids])
    print(f'   → {rutas.relativa(CARPETA)}/  (instrucciones: docs/VALIDACION-IGDS.md)')
    print(f'   ⚠ {CLAVE_A} no se publica: guarda una copia en el almacenamiento interno del equipo.')
    return True


def _guardar_clave(doc):
    (CARPETA / CLAVE_A).write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding='utf-8')


def _rehacer_a(pids, filas, unidades, cfg, forzar):
    """Rehace SOLO la hoja A, con una semilla secreta nueva, y su clave. Las
    hojas B y C no se tocan. Sirve cuando la clave anterior ha dejado de ser
    secreta: la hoja nueva no se puede descifrar con ella."""
    if not (CARPETA / HOJAS['B']).exists() or not (CARPETA / HOJAS['C']).exists():
        print('   ✗ No hay hojas B y C. Para hacer la muestra completa: python3 maestro.py igds muestra')
        return False
    if 'A' in _con_trabajo(CARPETA) and not forzar:
        print('   ✗ La hoja A ya tiene trabajo del equipo: no se rehace.')
        print('     Si de verdad quieres rehacerla: python3 maestro.py igds muestra --rehacer-a --forzar')
        return False
    # Las mismas formaciones que en la C: si faltara alguna, la hoja A nueva la perdería.
    siglas = {config.partido(p)['sigla'] for p in pids}
    fuera = sorted({f['formacion'] for f in _leer(CARPETA / HOJAS['C'])} - siglas)
    if fuera:
        print(f'   ✗ Faltan formaciones que están en las hojas B y C: {", ".join(fuera)}. Ejecuta sin --partido.')
        return False

    # Fuera de la A, lo que ya está en la hoja B vigente (no el censo de hoy, que
    # puede haber cambiado después): así A y B siguen sin solaparse.
    en_b = {f['id_medida'] for f in _leer(CARPETA / HOJAS['B'])}
    semilla_a = _semilla_a()
    rng = random.Random(semilla_a)
    ciega, poblacion = [], {}
    for pid in pids:
        c, pob = _ciega(_de(pid, filas), rng, cfg, en_b)
        ciega += c
        poblacion[pid] = pob
    rng.shuffle(ciega)  # todas las formaciones mezcladas, también las que se añadieron después

    clave, filas_a = _filas_a(ciega, unidades)
    _escribir(CARPETA / HOJAS['A'], COLS_A + MANUAL_A, filas_a)
    _guardar_clave({'semilla': cfg['semilla'], 'semilla_a': semilla_a, 'poblacion': poblacion, 'codigos': clave})
    por = Counter(c['pid'] for c in clave.values())
    print(f'   Hoja A REHECHA con una semilla secreta nueva: {len(filas_a)} medidas '
          f'({", ".join(f"{config.partido(p)["sigla"]} {por[p]}" for p in pids)}), todas mezcladas.')
    print('   Las hojas B y C no cambian. Cualquier clave anterior deja de servir.')
    print(f'   → {rutas.relativa(CARPETA / HOJAS["A"])} · {rutas.relativa(CARPETA / CLAVE_A)} (no se publica)')
    print(f'   ⚠ Guarda {CLAVE_A} en el almacenamiento interno del equipo y borra las copias de la anterior.')
    return True


def _ampliar(nuevas, doc, filas, repetidas, unidades, cfg):
    """Añade al final de las hojas A, B y C la muestra de las formaciones nuevas.
    Las filas existentes, y lo que el equipo haya escrito en ellas, no cambian.
    La A sale de la semilla secreta de la clave; la C, de la pública."""
    semilla_a = doc.setdefault('semilla_a', _semilla_a())
    ciega, verificar, atomizar = [], [], []
    for pid in nuevas:
        c, v, a, pob = _muestrear(pid, filas, random.Random(f'{semilla_a}:{pid}'),
                                  random.Random(f'{cfg["semilla"]}:{pid}'), cfg)
        ciega += c
        verificar += v
        atomizar += a
        doc['poblacion'][pid] = pob
    random.Random(f'{semilla_a}:{"+".join(nuevas)}').shuffle(ciega)

    previas_a = _leer(CARPETA / HOJAS['A'])
    clave, nuevas_a = _filas_a(ciega, unidades, primero=len(doc['codigos']) + 1)
    doc['codigos'].update(clave)
    _escribir(CARPETA / HOJAS['A'], COLS_A + MANUAL_A, previas_a + nuevas_a)
    _guardar_clave(doc)
    _escribir(CARPETA / HOJAS['B'], COLS_B + MANUAL_B, _leer(CARPETA / HOJAS['B']) + _filas_b(verificar))
    nuevas_c = _filas_c(atomizar, filas + repetidas, unidades)
    _escribir(CARPETA / HOJAS['C'], COLS_C + MANUAL_C, _leer(CARPETA / HOJAS['C']) + nuevas_c)

    siglas = [(p, config.partido(p)['sigla']) for p in nuevas]
    print(f'   Muestra AMPLIADA con {", ".join(s for _, s in siglas)} (semilla propia); las filas anteriores no cambian:')
    _resumen(nuevas_a, verificar, nuevas_c, Counter(c['pid'] for c in clave.values()), siglas)
    print(f'   → códigos A-{len(doc["codigos"]) - len(nuevas_a) + 1:03d} a A-{len(doc["codigos"]):03d} · '
          f'{rutas.relativa(CARPETA)}/')
    return True


# ── Concordancia ────────────────────────────────────────────────────────
def _kappa(pares):
    """Kappa de Cohen entre dos codificaciones (lista de pares)."""
    n = len(pares)
    if not n:
        return None
    po = sum(a == b for a, b in pares) / n
    ca, cb = Counter(a for a, _ in pares), Counter(b for _, b in pares)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return None if pe == 1 else (po - pe) / (1 - pe)


def _fk(k):
    return '-' if k is None else _fmt(round(k, 2) + 0.0)


def _lectura_kappa(k):
    if k is None:
        return 'sin variación'
    if k >= 0.80:
        return 'fiable'
    if k >= 0.67:
        return 'provisional'
    return 'revisar la regla'


def concordancia(pids, carpeta=None):
    carpeta = carpeta or CARPETA
    if not (carpeta / CLAVE_A).exists():
        if (carpeta / HOJAS['A']).exists():
            print(f'   ✗ Falta {CLAVE_A}: no está en el repositorio público. Pídela al equipo de ODESOCAN y cópiala en {carpeta}.')
        else:
            print('   No hay muestra. Ejecuta antes: python3 maestro.py igds muestra')
        return False
    filas, repetidas, _ = _medidas(pids)
    ia = {f['id_medida']: f for f in filas + repetidas}
    areas = {a['id'] for a in config.igds()['areas']}
    clave = json.loads((carpeta / CLAVE_A).read_text(encoding='utf-8'))
    malos = _clave_ajena(clave, filas + repetidas, carpeta)
    if malos:  # con la clave de otra hoja A, la kappa compararía medidas distintas
        _aviso_clave_ajena(malos)
        return False
    errores, L = [], []

    # A · codificación ciega
    pares = defaultdict(list)  # (variable, pid | 'todas', estrato | 'todos') → [(ia, humano)]
    discrepancias, hechas, pendientes = [], 0, 0
    for fila in _leer(carpeta / HOJAS['A']):
        cod = fila['codigo']
        meta = clave['codigos'].get(cod)
        valores = {c: (fila.get(c) or '').strip() for c in MANUAL_A if c != 'comentario'}
        if not any(valores.values()):
            pendientes += 1
            continue
        if not meta or meta['id_medida'] not in ia:
            errores.append(f'A {cod}: código desconocido')
            continue
        malos = [c for c in [*DIMS, *MARCAS] if valores[c] not in ('0', '1')]
        if valores['area'].upper() not in areas:
            malos.append('area')
        if malos:
            errores.append(f'A {cod}: falta o no es válido: {", ".join(malos)}')
            continue
        hechas += 1
        h = {c: int(valores[c]) for c in [*DIMS, *MARCAS]}
        h['area'] = valores['area'].upper()
        h['g'] = int(all(h[d] for d in DIMS))
        m = ia[meta['id_medida']]
        for var in [*DIMS, 'g', *MARCAS, 'area']:
            par = (m[var], h[var])
            for clave_p in [(var, 'todas', 'todos'), (var, meta['pid'], 'todos'), (var, meta['pid'], meta['estrato'])]:
                pares[clave_p].append(par)
            if par[0] != par[1]:
                discrepancias.append((cod, meta['id_medida'], var, par[0], par[1], (fila.get('comentario') or '').strip()))

    L += ['# IGDS · Validación humana', '',
          'Generado por `python3 maestro.py igds concordancia`. Compara la codificación (con los ajustes de '
          'coherencia) con la validación humana de las hojas de `datos/igds/validacion/`. '
          'Kappa de Cohen: ≥ 0,80 fiable · 0,67 a 0,80 provisional · < 0,67 hay que revisar la regla.', '',
          f'## A · Codificación ciega ({hechas} medidas codificadas, {pendientes} pendientes)', '']
    if hechas:
        L += ['| Variable | Acuerdo | Kappa | Lectura | ' + ' | '.join(config.partido(p)['sigla'] + ' (acuerdo)' for p in pids) + ' |',
              '|---|---|---|---|' + '---|' * len(pids)]
        for var in [*DIMS, 'g', *MARCAS, 'area']:
            todos = pares[(var, 'todas', 'todos')]
            k = _kappa(todos)
            acuerdo = 100 * sum(a == b for a, b in todos) / len(todos)
            por = []
            for p in pids:
                pp = pares[(var, p, 'todos')]
                por.append(_fmt(100 * sum(a == b for a, b in pp) / len(pp)) if pp else '-')
            L.append(f'| {var.upper()} | {_fmt(acuerdo)} % | {_fk(k)} | '
                     f'{_lectura_kappa(k)} | ' + ' | '.join(por) + ' |')
        L += ['', 'Con categorías poco frecuentes (EXI, g, REG) la kappa es inestable aunque el acuerdo sea alto: '
              'se lee junto al porcentaje de acuerdo y a la hoja B, que revisa todas las garantías completas y regresivas.',
              '', f'**Discrepancias** ({len(discrepancias)}): codificación → validación humana.', '']
        for cod, mid, var, a, b, com in sorted(discrepancias, key=lambda x: (x[1], x[2])):
            L.append(f'- {cod} `{mid}` {var.upper()}: {a} → {b}{" · " + com if com else ""}')
    L.append('')

    # B · verificación
    filas_b = _leer(carpeta / HOJAS['B'])
    por_estrato, correcciones, pend_b = defaultdict(lambda: [0, 0]), [], 0
    for fila in filas_b:
        ac = (fila.get('de_acuerdo') or '').strip().lower()
        if not ac:
            pend_b += 1
            continue
        if ac not in ('sí', 'si', 'no'):
            errores.append(f'B {fila["id_medida"]}: de_acuerdo tiene que ser «sí» o «no»')
            continue
        si = ac in ('sí', 'si')
        for e in [x.strip() for x in fila['estrato'].split(',')] + [fila['formacion']]:
            por_estrato[e][0] += si
            por_estrato[e][1] += 1
        corr = (fila.get('correccion') or '').strip()
        if not si:
            cambios = {}
            for trozo in filter(None, (t.strip() for t in re.split(r'[;,]', corr))):
                campo, _, valor = trozo.partition('=')
                campo, valor = campo.strip().lower(), valor.strip()
                if campo not in CAMPOS_CORRECCION or not valor:
                    errores.append(f'B {fila["id_medida"]}: corrección no válida «{trozo}» (usa campo=valor)')
                    continue
                cambios[campo] = valor
            if not cambios:
                errores.append(f'B {fila["id_medida"]}: «no» sin corrección (por ejemplo: des=0; reg=1)')
            correcciones.append((fila['id_medida'], cambios, (fila.get('comentario') or '').strip()))
    L += [f'## B · Verificación ({len(filas_b) - pend_b} revisadas, {pend_b} pendientes)', '']
    if por_estrato:
        L += ['| Grupo | De acuerdo |', '|---|---|']
        for e, (si, n) in sorted(por_estrato.items()):
            L.append(f'| {e} | {si} de {n} ({_fmt(100 * si / n)} %) |')
        L += ['', f'**Correcciones propuestas** ({len(correcciones)}):', '']
        for mid, cambios, com in correcciones:
            L.append(f'- `{mid}`: {"; ".join(f"{k}={v}" for k, v in cambios.items())}{" · " + com if com else ""}')
    L.append('')

    # C · atomización
    filas_c = _leer(carpeta / HOJAS['C'])
    val, difs, pend_c = defaultdict(Counter), [], 0
    for fila in filas_c:
        v = (fila.get('valoracion') or '').strip().lower()
        if not v:
            pend_c += 1
            continue
        if v not in VALORACIONES:
            errores.append(f'C {fila["unidad"]}: valoración «{v}» ({", ".join(VALORACIONES)})')
            continue
        val[fila['formacion']][v] += 1
        prop = (fila.get('n_medidas_propuesto') or '').strip()
        if prop:
            if prop.isdigit():
                difs.append(int(prop) - int(fila['n_medidas']))
            else:
                errores.append(f'C {fila["unidad"]}: n_medidas_propuesto tiene que ser un número')
    L += [f'## C · Atomización ({len(filas_c) - pend_c} unidades revisadas, {pend_c} pendientes)', '']
    if val:
        L += ['| Formación | ' + ' | '.join(VALORACIONES) + ' |', '|---|' + '---|' * len(VALORACIONES)]
        for f, c in val.items():
            L.append(f'| {f} | ' + ' | '.join(str(c[v]) for v in VALORACIONES) + ' |')
        if difs:
            L += ['', f'Diferencia media entre las medidas propuestas y las extraídas: '
                      f'{_fmt(sum(difs) / len(difs))} por unidad ({len(difs)} unidades con número propuesto).']
    L.append('')

    if errores:
        L += ['## Errores de las hojas', ''] + [f'- {e}' for e in errores] + ['']
    rutas.INFORMES.mkdir(parents=True, exist_ok=True)
    cab = obsidian.cabecera('proyecto', 'analisis', ['igds', 'validacion', 'kappa'], 'IGDS · concordancia de la validación',
                            'datos/informes/igds-validacion.md')
    (rutas.INFORMES / 'igds-validacion.md').write_text(cab + '\n'.join(L) + '\n', encoding='utf-8')
    if hechas:
        kg = _kappa(pares[('g', 'todas', 'todos')])
        ke = _kappa(pares[('exi', 'todas', 'todos')])
        print(f'   A: {hechas} codificadas · kappa EXI {_fk(ke)} · kappa g {_fk(kg)} · {len(discrepancias)} discrepancias')
    print(f'   B: {len(filas_b) - pend_b} de {len(filas_b)} revisadas · {len(correcciones)} correcciones')
    print(f'   C: {len(filas_c) - pend_c} de {len(filas_c)} unidades revisadas')
    for e in errores[:20]:
        print(f'   ✗ {e}')
    print(f'   → {rutas.relativa(rutas.INFORMES / "igds-validacion.md")}')
    return not errores
