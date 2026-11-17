"""Resumen de en qué punto está cada programa (python3 maestro.py estado)."""
import csv
import json
from collections import Counter

from . import clasificar, config, obsidian, rutas
from .extraer import huella
from .segmentar import SIN_CONTENIDO_PROPIO, cargar as cargar_segmentos


def informe():
    filas_web = Counter()
    if rutas.CSV_WEB.exists():
        with open(rutas.CSV_WEB, encoding='utf-8') as f:
            filas_web = Counter(r['partido'] for r in csv.DictReader(f))

    print(f'   {"partido":<8} {"programa":<11} {"PDF":<12} {"medidas":>8} {"temas":>9} {"fiscal":>9} {"en web":>7}')
    for p in config.partidos():
        pid, prog = p['id'], p['programa']
        if not prog:
            print(f'   {p["sigla"]:<8} {"pendiente":<11} {"—":<12} {"—":>8} {"—":>9} {"—":>9} {"—":>7}')
            continue
        pdf = rutas.FUENTES / prog['archivo']
        if not pdf.exists():
            estado_pdf = 'falta'
        elif prog.get('sha256') and huella(pdf) != prog['sha256']:
            estado_pdf = 'otra huella'
        else:
            estado_pdf = 'ok'
        if (rutas.FUENTES / (pdf.stem + '.nuevo.pdf')).exists():
            estado_pdf += ' +nuevo'
        seg = [s for s in cargar_segmentos(pid) if s['aviso'] not in SIN_CONTENIDO_PROPIO]
        cla, fis = clasificar.cargar(pid), clasificar.cargar(pid, 'fiscal')
        hechas = sum(1 for s in seg if s['id'] in cla)
        fiscal = sum(1 for s in seg if s['id'] in fis)
        print(f'   {p["sigla"]:<8} {"publicado":<11} {estado_pdf:<12} {len(seg):>8} {f"{hechas}/{len(seg)}":>9} '
              f'{f"{fiscal}/{len(seg)}":>9} {filas_web.get(pid, 0):>7}')

    ver = rutas.INFORMES / 'verificacion.json'
    if ver.exists():
        inf = json.loads(ver.read_text(encoding='utf-8'))['informe']
        malas = {pid: r['no_literal'] for pid, r in inf.items() if r['no_literal']}
        print(f'   literalidad: {"todas las medidas volcadas son literales" if not malas else f"✗ NO literales: {malas}"}')

    if obsidian.VAULT.is_dir():
        est = obsidian.revisar()
        malos = {d: e for d, e in est.items() if e != 'ok'}
        print(f'   obsidian: {len(est) - len(malos)} de {len(est)} notas enlazadas en el vault'
              + (f' · ⚠ {malos} → python3 maestro.py obsidian' if malos else ''))

    js = rutas.DIVI / 'odesocan-programas.js'
    if not js.exists():
        print('   divi/: sin generar → python3 maestro.py divi')
    elif rutas.CSV_WEB.exists() and rutas.CSV_WEB.stat().st_mtime > js.stat().st_mtime:
        print('   divi/: ⚠ el CSV es más reciente que el paquete de Divi → python3 maestro.py divi')
    else:
        base = config.campana()['publicacion']['base_url']
        print(f'   divi/: al día · bloque limpio {"con URL " + base if base else "con marcadores (falta publicacion.base_url)"}')
