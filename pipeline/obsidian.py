"""Las notas del proyecto en el vault de Obsidian (python3 maestro.py obsidian).

Los md del proyecto están en el vault OBSERVATORIO/Obsidian como enlaces
simbólicos, en una subcarpeta «PE_29N» dentro de la carpeta del vault que les
corresponde. Así se editan desde Obsidian y el cambio es el del proyecto (no
hay copias que se desincronicen). El índice del proyecto en el vault es
1_investigacion/01_proyectos/PE_29N/00_indice_PE_29N.md, que es una nota
propia del vault, no un enlace.

El vault cataloga las notas por su frontmatter (type, fase, tags, status,
actualizado, aliases, fuente). Los informes que genera el pipeline se
reescriben en cada ejecución, así que el frontmatter lo pone quien los escribe.
"""
import os
from datetime import date
from pathlib import Path

from . import rutas

ID = 'PE_29N'
VAULT = Path(os.environ.get('VAULT_ODESOCAN', rutas.RAIZ.parent / 'Obsidian'))

# archivo del proyecto → ruta en el vault
ENLACES = {
    'README.md': f'1_investigacion/01_proyectos/{ID}/{ID}_README.md',
    'docs/CRITERIOS-CLASIFICACION.md': f'1_investigacion/03_metodologia/{ID}/CRITERIOS-CLASIFICACION.md',
    'docs/CRITERIOS-IMPACTO-FISCAL.md': f'1_investigacion/03_metodologia/{ID}/CRITERIOS-IMPACTO-FISCAL.md',
    'docs/CRITERIOS-IGDS.md': f'1_investigacion/03_metodologia/{ID}/CRITERIOS-IGDS.md',
    'docs/VALIDACION-IGDS.md': f'1_investigacion/03_metodologia/{ID}/VALIDACION-IGDS.md',
    'docs/INFORME-VOLCADO.md': f'4_extracionpdf/{ID}/INFORME-VOLCADO.md',
    'docs/DISENO.md': f'7_visualizacion/{ID}/DISENO.md',
    'docs/ANALISIS-IGDS.md': f'8_analisis/{ID}/ANALISIS-IGDS.md',
    'datos/informes/igds.md': f'8_analisis/{ID}/igds.md',
    'datos/informes/igds-contraste.md': f'8_analisis/{ID}/igds-contraste.md',
    'datos/informes/igds-validacion.md': f'8_analisis/{ID}/igds-validacion.md',
    'datos/informes/contraste-fiscal.md': f'8_analisis/{ID}/contraste-fiscal.md',
}


def revisar():
    """Estado de cada enlace: 'ok', 'falta', 'copia' (un archivo normal donde
    debía haber un enlace: alguien lo sustituyó y ya no es el del proyecto) u
    'otro destino'. Devuelve {ruta_en_vault: estado}."""
    estado = {}
    for origen, destino in ENLACES.items():
        v = VAULT / destino
        if v.is_symlink():
            estado[destino] = 'ok' if v.resolve() == (rutas.RAIZ / origen).resolve() else 'otro destino'
        elif v.exists():
            estado[destino] = 'copia'
        else:
            estado[destino] = 'falta'
    return estado


def enlazar() -> bool:
    """Crea los enlaces que falten. No toca una copia ni un enlace a otro sitio: los señala."""
    if not VAULT.is_dir():
        print(f'   ✗ No encuentro el vault en {VAULT} (variable VAULT_ODESOCAN para otra ruta).')
        return False
    ok = True
    for destino, est in revisar().items():
        origen = rutas.RAIZ / next(o for o, d in ENLACES.items() if d == destino)
        if est == 'falta':
            if not origen.exists():
                print(f'   · {destino}: el archivo del proyecto aún no existe')
                continue
            (VAULT / destino).parent.mkdir(parents=True, exist_ok=True)
            (VAULT / destino).symlink_to(origen)
            print(f'   + {destino}')
        elif est == 'ok':
            print(f'   ✓ {destino}')
        else:
            ok = False
            print(f'   ✗ {destino}: es {"una copia" if est == "copia" else "un enlace a otro sitio"}; '
                  'compárala con el archivo del proyecto, guarda lo que valga y bórrala para volver a enlazar')
    return ok


def cabecera(tipo, fase, tags, alias, fuente):
    """Frontmatter YAML de una nota del proyecto (termina en línea en blanco)."""
    etiquetas = ', '.join([ID, *tags, 'generado-por-pipeline'])
    return (
        '---\n'
        f'type: {tipo}\n'
        f'fase: {fase}\n'
        f'proyecto: {ID}\n'
        f'tags: [{etiquetas}]\n'
        'status: vigente\n'
        f'actualizado: {date.today().isoformat()}\n'
        f'aliases: ["{ID} · {alias}"]\n'
        f'fuente: "OBSERVATORIO/Programas electorales 29N/{fuente}"\n'
        '---\n\n'
    )


def sin_cabecera(texto):
    """Quita el frontmatter (para copiar un documento dentro de otro)."""
    if texto.startswith('---\n'):
        fin = texto.find('\n---\n', 4)
        if fin != -1:
            return texto[fin + 5:].lstrip('\n')
    return texto
