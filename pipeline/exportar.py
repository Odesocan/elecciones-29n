"""Etapa 6 · Segmentos + clasificación + verificación → salidas.

  web/public/data/programas.csv        lo que lee la web (solo medidas literales y con tema)
  datos/revision/revision-clasificacion.csv
                                       hoja para que el equipo revise los temas; al
                                       regenerarla se CONSERVAN sus columnas manuales
  datos/informes/verificacion.json     qué se volcó, qué no y por qué

Columnas de programas.csv (contrato con la web, ver web/src/datos.js):
  partido  id del partido (config/partidos.json)
  tema     ids de tema separados por «;», el principal primero
  ref      «Medida 83»       pagina   página del PDF (para el enlace #page=N)
  titulo, texto              literales del programa
  url      enlace propio (vacío: se construye con la URL del PDF y la página)
  nota     aviso visible en la ficha («Texto incompleto en el PDF original»)
  fiscal   etiquetas de impacto fiscal separadas por «;» (config/fiscal.json);
           vacío = sin impacto presupuestario directo · «pendiente» = aún sin clasificar
"""
import csv
import json
import shutil

from . import apartados, clasificar, config, rutas
from .segmentar import cargar as cargar_segmentos
from .verificar import Verificador

COLUMNAS_WEB = ['partido', 'tema', 'ref', 'pagina', 'titulo', 'texto', 'url', 'nota', 'fiscal']
COLUMNAS_REVISION = ['partido', 'medida', 'pagina', 'apartado', 'titulo', 'tema_principal', 'otros_temas',
                     'impacto_fiscal',
                     'revisado_ok', 'correccion', 'correccion_fiscal', 'comentario']
MANUALES = ['revisado_ok', 'correccion', 'correccion_fiscal', 'comentario']


def _filas_partido(pid, temas_validos):
    seg = cargar_segmentos(pid)
    cla = clasificar.cargar(pid)
    fis = clasificar.cargar(pid, 'fiscal')
    r = {'medidas': len(seg), 'filas': 0, 'por_anunciar': [], 'faltan_en_clasificacion': [],
         'temas_raros': [], 'no_literal': [], 'sin_tema': [], 'notas': [], 'sin_fiscal': []}
    if not seg:
        return [], r
    verificador = Verificador(pid)
    filas = []
    for s in seg:
        if s['aviso'] == 'por anunciar':
            r['por_anunciar'].append(s['id'])
            continue
        if s['id'] not in cla:
            r['faltan_en_clasificacion'].append(s['id'])
            continue
        temas = [t for t in cla[s['id']] if t in temas_validos]
        r['temas_raros'] += [f"{s['id']}:{t}" for t in cla[s['id']] if t not in temas_validos]
        if not verificador.medida(s):
            r['no_literal'].append(s['id'])
            continue
        if not temas:
            r['sin_tema'].append(s['id'])
            continue
        if s['aviso']:
            r['notas'].append(s['id'])
        if s['id'] not in fis:
            r['sin_fiscal'].append(s['id'])
        filas.append({'partido': pid, 'tema': ';'.join(dict.fromkeys(temas)), 'ref': s['ref'],
                      'pagina': s['pagina'], 'titulo': s['titulo'], 'texto': s['texto'], 'url': '',
                      'nota': s['aviso'],
                      'fiscal': ';'.join(fis[s['id']]) if s['id'] in fis else 'pendiente',
                      'apartado': apartados.texto(s.get('apartado'))})  # solo para la hoja de revisión
        r['filas'] += 1
    return filas, r


def _escribir_revision(filas):
    # Conservar lo que el equipo ya haya escrito en la hoja.
    previas = {}
    if rutas.REVISION.exists():
        for f in clasificar._leer_revision():
            previas[(f.get('partido', ''), f.get('medida', ''))] = {k: f.get(k, '') for k in MANUALES}
    rutas.REVISION.parent.mkdir(parents=True, exist_ok=True)
    with open(rutas.REVISION, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(COLUMNAS_REVISION)
        for r in filas:
            t = r['tema'].split(';')
            clave = (r['partido'].upper(), r['ref'])
            manual = previas.get(clave, {})
            w.writerow([*clave, r['pagina'], r['apartado'], r['titulo'] or r['texto'][:120], t[0], ', '.join(t[1:]),
                        r['fiscal'].replace(';', ', ') or 'ninguno', *(manual.get(k, '') for k in MANUALES)])


def volcar() -> bool:
    temas_validos = config.ids_temas()
    filas, informe = [], {}
    for p in config.publicados():
        f, r = _filas_partido(p['id'], set(temas_validos))
        if r['medidas']:
            filas += f
            informe[p['id']] = r

    rutas.CSV_WEB.parent.mkdir(parents=True, exist_ok=True)
    with open(rutas.CSV_WEB, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLUMNAS_WEB, extrasaction='ignore')  # el apartado no va a la web
        w.writeheader()
        w.writerows(filas)
    _escribir_revision(filas)
    # Programas sin versión en línea (UPC): la web enlaza la copia que se publica junto a los datos.
    for p in config.publicados():
        if p['programa'].get('pdf_propio') and (rutas.FUENTES / p['programa']['archivo']).exists():
            shutil.copy2(rutas.FUENTES / p['programa']['archivo'], rutas.CSV_WEB.parent / p['programa']['archivo'])

    por_tema = {t: {pid: 0 for pid in informe} for t in temas_validos}
    for fl in filas:
        for t in fl['tema'].split(';'):
            por_tema[t][fl['partido']] += 1
    cuentas = prueba_de_las_cuentas(filas, list(informe))
    rutas.INFORMES.mkdir(parents=True, exist_ok=True)
    (rutas.INFORMES / 'verificacion.json').write_text(
        json.dumps({'informe': informe, 'por_tema': por_tema, 'cuentas': cuentas}, ensure_ascii=False, indent=1) + '\n',
        encoding='utf-8')

    ok = True
    for pid, r in informe.items():
        problemas = {k: r[k] for k in ('faltan_en_clasificacion', 'temas_raros', 'no_literal') if r[k]}
        ok &= not problemas
        print(f"   {'✓' if not problemas else '✗'} {pid}: {r['filas']} de {r['medidas']} medidas a la web · "
              f"por anunciar {len(r['por_anunciar'])} · con nota {r['notas'] or '—'}"
              + (f' · sin tema {r["sin_tema"]}' if r['sin_tema'] else ''))
        for k, v in problemas.items():
            print(f'        ✗ {k.replace("_", " ")}: {v}')
    for pid, c in cuentas.items():
        if c.get('pendiente'):
            print(f'   ⚠ {pid}: {len(informe[pid]["sin_fiscal"])} medidas sin clasificar en impacto fiscal')
        else:
            print(f"   · {pid} · cuentas: {c['restan']} restan ({c['menos_ingresos']} menos ingresos, "
                  f"{c['mas_gasto']} más gasto) · {c['suman']} suman ({c['mas_ingresos']} más ingresos, "
                  f"{c['menos_gasto']} menos gasto) · ratio 1:{c['ratio'] if c['ratio'] is not None else '∞'} · "
                  f"con importe {c['con_importe']}" + (' · RIESGO DE VIABILIDAD' if c['riesgo_viabilidad'] else ''))
    total = sum(r['filas'] for r in informe.values())
    literales = sum(r['filas'] + len(r['sin_tema']) for r in informe.values())
    revisables = sum(r['medidas'] - len(r['por_anunciar']) - len(r['faltan_en_clasificacion']) for r in informe.values())
    print(f'   {total} filas → {rutas.relativa(rutas.CSV_WEB)} · literales {literales}/{revisables}')
    print(f'   hoja de revisión → {rutas.relativa(rutas.REVISION)} · informe → datos/informes/verificacion.json')
    return ok


def prueba_de_las_cuentas(filas, pids):
    """Recuento fiscal por partido (el mismo cálculo que hace la web en datos.js)."""
    out = {}
    umbral = config.riesgo_viabilidad()['umbral']
    for pid in pids:
        mias = [set(f['fiscal'].split(';')) - {''} for f in filas if f['partido'] == pid]
        if any('pendiente' in e for e in mias):
            out[pid] = {'pendiente': True}
            continue
        # Restan dinero a las cuentas públicas (ingresan menos o gastan más) /
        # lo suman (ingresan más o gastan menos).
        restan = sum(1 for e in mias if e & {'menos_ingresos', 'mas_gasto'})
        suman = sum(1 for e in mias if e & {'mas_ingresos', 'menos_gasto'})
        out[pid] = {
            'medidas': len(mias),
            **{k: sum(1 for e in mias if k in e)
               for k in ('menos_ingresos', 'mas_gasto', 'mas_ingresos', 'menos_gasto', 'consolidacion')},
            'restan': restan,
            'suman': suman,
            'ratio': round(restan / suman, 1) if suman else None,
            # Riesgo de viabilidad: restan > umbral × suman (config/fiscal.json)
            'riesgo_viabilidad': restan > 0 and restan > umbral * suman,
            'con_importe': sum(1 for e in mias if 'importe' in e and e & {'menos_ingresos', 'mas_gasto'}),
        }
    return out
