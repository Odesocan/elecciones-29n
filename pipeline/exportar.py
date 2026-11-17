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

No se publican las unidades sin contenido propio (segmentar.SIN_CONTENIDO_PROPIO):
los huecos «por anunciar» del PP y las medidas que solo introducen las siguientes
(PSOE 54 y 176). Tampoco cuentan en el total de medidas del partido.

La prueba de las cuentas (impacto fiscal) se descartó el 16-11-2026: la etiqueta
fiscal ya no va a la web; solo queda, archivada, en la hoja de revisión interna.
"""
import csv
import json
import shutil

from . import apartados, clasificar, config, rutas
from .segmentar import INTRODUCTORIA, cargar as cargar_segmentos
from .verificar import Verificador

COLUMNAS_WEB = ['partido', 'tema', 'ref', 'pagina', 'titulo', 'texto', 'url', 'nota']
COLUMNAS_REVISION = ['partido', 'medida', 'pagina', 'apartado', 'titulo', 'tema_principal', 'otros_temas',
                     'impacto_fiscal',
                     'revisado_ok', 'correccion', 'correccion_fiscal', 'comentario']
MANUALES = ['revisado_ok', 'correccion', 'correccion_fiscal', 'comentario']


def _filas_partido(pid, temas_validos):
    seg = cargar_segmentos(pid)
    cla = clasificar.cargar(pid)
    fis = clasificar.cargar(pid, 'fiscal')
    r = {'medidas': len(seg), 'filas': 0, 'por_anunciar': [], 'introductorias': [], 'faltan_en_clasificacion': [],
         'temas_raros': [], 'no_literal': [], 'sin_tema': [], 'notas': [], 'sin_fiscal': []}
    if not seg:
        return [], r
    verificador = Verificador(pid)
    filas = []
    for s in seg:
        if s['aviso'] == 'por anunciar':
            r['por_anunciar'].append(s['id'])
            continue
        if s['aviso'] == INTRODUCTORIA:  # solo abre la lista de las siguientes: no se publica
            r['introductorias'].append(s['id'])
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
        w = csv.DictWriter(f, fieldnames=COLUMNAS_WEB, extrasaction='ignore')  # ni el apartado ni lo fiscal van a la web
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
    rutas.INFORMES.mkdir(parents=True, exist_ok=True)
    (rutas.INFORMES / 'verificacion.json').write_text(
        json.dumps({'informe': informe, 'por_tema': por_tema}, ensure_ascii=False, indent=1) + '\n',
        encoding='utf-8')

    ok = True
    for pid, r in informe.items():
        problemas = {k: r[k] for k in ('faltan_en_clasificacion', 'temas_raros', 'no_literal') if r[k]}
        ok &= not problemas
        print(f"   {'✓' if not problemas else '✗'} {pid}: {r['filas']} de {r['medidas']} medidas a la web · "
              f"por anunciar {len(r['por_anunciar'])} · introductorias {r['introductorias'] or '—'}"
              f" · con nota {r['notas'] or '—'}"
              + (f' · sin tema {r["sin_tema"]}' if r['sin_tema'] else ''))
        for k, v in problemas.items():
            print(f'        ✗ {k.replace("_", " ")}: {v}')
    total = sum(r['filas'] for r in informe.values())
    literales = sum(r['filas'] + len(r['sin_tema']) for r in informe.values())
    revisables = sum(r['medidas'] - len(r['por_anunciar']) - len(r['introductorias']) - len(r['faltan_en_clasificacion'])
                     for r in informe.values())
    print(f'   {total} filas → {rutas.relativa(rutas.CSV_WEB)} · literales {literales}/{revisables}')
    print(f'   hoja de revisión → {rutas.relativa(rutas.REVISION)} · informe → datos/informes/verificacion.json')
    return ok
