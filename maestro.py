#!/usr/bin/env python3
"""Script maestro · Lee los programas (29N) · ODESOCAN

Orquesta los tres módulos del proyecto:

    pipeline/  PDF oficiales → CSV         (Python)
    web/       herramienta React + D3      (Node · Vite)
    divi/      bloque listo para pegar     (lo genera web/scripts/empaquetar-divi.mjs)

Uso:  python3 maestro.py [etapa] [opciones]

    todo         (por defecto) extraer → segmentar → validar → volcar → divi
    estado       en qué punto está cada programa
    descargar    baja los PDF oficiales y avisa si un partido cambia el suyo
    extraer      PDF → texto por página (caché en datos/texto/)
    segmentar    texto → medidas numeradas (datos/segmentos/)
    clasificar   preparar | validar | revision | contrastar   [--dimension temas|fiscal|todas]
                 (criterios en docs/CRITERIOS-CLASIFICACION.md y docs/CRITERIOS-IMPACTO-FISCAL.md)
    volcar       verifica literalidad y escribe el CSV de la web y la hoja de revisión
    igds         fase0 | preparar | validar | contrastar | calcular   [--lote lote-01]
                 muestra | concordancia   validación humana (--forzar rehace la muestra;
                                          --rehacer-a, solo la hoja A con una clave nueva)
                 índice de garantía de derechos sociales, en prueba (docs/CRITERIOS-IGDS.md)
    obsidian     enlaza los md del proyecto en el vault de Obsidian (subcarpetas PE_29N)
    divi         compila la web y genera divi/ (bloque limpio + archivos a publicar)
    servir       servidor local de desarrollo  → http://127.0.0.1:5173
    probar       sirve divi/ con CSS «hostil»  → http://127.0.0.1:4173

Opciones:  --partido pp [--partido vox …]   limita la etapa a esos partidos
           --forzar                          rehace la extracción aunque haya caché
           --aceptar                         (descargar) adopta la versión nueva de un PDF
           --descargar                       (todo) empieza por comprobar los PDF en la web

Cada etapa lee y escribe en rutas fijas (pipeline/rutas.py), así que se pueden
ejecutar por separado y en cualquier momento.
"""
import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))  # funciona también con «python3 -I»
sys.stdout.reconfigure(line_buffering=True)  # que los títulos salgan antes que la salida de npm

from pipeline import clasificar, config, descargar, estado, exportar, extraer, igds, obsidian, rutas, segmentar  # noqa: E402


def titulo(texto):
    print(f'\n▸ {texto}')


def pids(args):
    if args.partido:
        for pid in args.partido:
            config.partido(pid)  # valida el id
        return args.partido
    return [p['id'] for p in config.publicados()]


def npm(*argumentos):
    if not shutil.which('npm'):
        raise SystemExit('Falta Node.js (npm). Instálalo desde https://nodejs.org/ (versión 20 o superior).')
    if not (rutas.WEB / 'node_modules').exists():
        titulo('Instalando dependencias de la web (solo la primera vez)')
        subprocess.run(['npm', 'ci'], cwd=rutas.WEB, check=True)
    return subprocess.run(['npm', *argumentos], cwd=rutas.WEB).returncode == 0


# ── Etapas ─────────────────────────────────────────────────────────────
def e_estado(args):
    titulo('Estado')
    estado.informe()
    return True


def e_descargar(args):
    titulo('Descargar y comprobar los PDF oficiales')
    return descargar.ejecutar(pids(args), aceptar=args.aceptar)


def e_extraer(args):
    titulo('Extraer el texto de los PDF')
    extraer.ejecutar(pids(args), forzar=args.forzar)
    return True


def e_segmentar(args):
    titulo('Segmentar en medidas')
    segmentar.ejecutar(pids(args))
    return True


def e_clasificar(args):
    accion = args.accion or 'validar'
    # En «todo» se validan las dos dimensiones; a mano, la que se pida.
    dim = args.dimension or {'validar': 'todas', 'contrastar': 'fiscal'}.get(accion, 'temas')
    titulo(f'Clasificación · {accion} · {dim}')
    return clasificar.ejecutar(accion, pids(args), dim)


def e_volcar(args):
    titulo('Verificar literalidad y volcar a la web')
    if args.partido:
        print('   (el volcado siempre recorre todos los programas: el CSV es uno solo)')
    return exportar.volcar()


def e_obsidian(args):
    titulo(f'Notas del proyecto en el vault de Obsidian ({obsidian.VAULT})')
    return obsidian.enlazar()


def e_igds(args):
    accion = args.accion or 'validar'
    titulo(f'IGDS (prueba) · {accion}')
    return igds.ejecutar(accion, pids(args), args.lote, forzar=args.forzar, explicitos=bool(args.partido),
                         rehacer_a=args.rehacer_a)


def e_divi(args):
    titulo('Compilar la web y generar divi/')
    return npm('run', 'build')


def e_servir(args):
    titulo('Servidor de desarrollo → http://127.0.0.1:5173  (Ctrl+C para parar)')
    return npm('run', 'dev')


def e_probar(args):
    titulo('Páginas de prueba de divi/ → http://127.0.0.1:4173  (Ctrl+C para parar)')
    return npm('run', 'prueba')


def e_todo(args):
    pasos = [e_extraer, e_segmentar, e_clasificar, e_volcar, e_divi, e_estado]
    if args.descargar:
        pasos.insert(0, e_descargar)
    for paso in pasos:
        if not paso(args):
            print(f'\n✗ Se detiene en «{paso.__name__[2:]}». Corrige lo indicado y vuelve a ejecutar.')
            return False
    return True


ETAPAS = {
    'todo': e_todo, 'estado': e_estado, 'descargar': e_descargar, 'extraer': e_extraer,
    'segmentar': e_segmentar, 'clasificar': e_clasificar, 'volcar': e_volcar, 'igds': e_igds, 'divi': e_divi,
    'obsidian': e_obsidian,
    'servir': e_servir, 'probar': e_probar,
}


def main():
    ap = argparse.ArgumentParser(
        prog='python3 maestro.py',
        description='Lee los programas (29N): de los PDF oficiales al bloque de Divi.',
        epilog='Arquitectura y flujos de trabajo: README.md',
    )
    ap.add_argument('etapa', nargs='?', default='todo', choices=ETAPAS)
    ap.add_argument('accion', nargs='?',
                    choices=['preparar', 'validar', 'revision', 'contrastar', 'fase0', 'calcular', 'muestra', 'concordancia'],
                    help='clasificar: preparar | validar | revision | contrastar · igds: fase0 | preparar | validar | contrastar | calcular | muestra | concordancia')
    ap.add_argument('--partido', action='append', metavar='ID', help='id de config/partidos.json (repetible)')
    ap.add_argument('--dimension', choices=['temas', 'fiscal', 'todas'],
                    help='(clasificar) temas · fiscal · todas; por defecto, «todas» al validar y «temas» al preparar')
    ap.add_argument('--lote', metavar='lote-NN', help='(igds validar) comprueba solo ese lote')
    ap.add_argument('--forzar', action='store_true',
                    help='rehacer la extracción aunque haya caché · (igds muestra) rehacer las hojas aunque tengan trabajo')
    ap.add_argument('--rehacer-a', action='store_true',
                    help='(igds muestra) rehacer solo la hoja A con una clave nueva; B y C no cambian')
    ap.add_argument('--aceptar', action='store_true', help='adoptar la versión nueva de un PDF')
    ap.add_argument('--descargar', action='store_true', help='«todo» empieza comprobando los PDF en la web')
    args = ap.parse_args()
    validas = {'clasificar': {'preparar', 'validar', 'revision', 'contrastar'},
               'igds': {'fase0', 'preparar', 'validar', 'contrastar', 'calcular', 'muestra', 'concordancia'}}
    if args.accion and args.accion not in validas.get(args.etapa, set()):
        ap.error(f'«{args.accion}» no es una acción de la etapa «{args.etapa}»')

    inicio = time.time()
    try:
        ok = ETAPAS[args.etapa](args)
    except KeyboardInterrupt:
        ok = True
    print(f'\n{"✓ Hecho" if ok else "✗ Con errores"} en {time.time() - inicio:.0f} s')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
