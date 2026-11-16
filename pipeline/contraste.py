"""Control de calidad de la clasificación fiscal (python3 maestro.py clasificar contrastar).

La clasificación la hace una IA y la revisa el equipo. Para dirigir esa
revisión, este módulo busca SEÑALES en el texto de cada medida (palabras que
suelen indicar un efecto fiscal) y lista las discrepancias con la etiqueta:

  · señal sin etiqueta   el texto habla de, p. ej., «deducción» y la medida
                         no lleva «menos_ingresos». Puede ser correcto (una
                         deducción que se suprime es «mas_ingresos»), pero
                         hay que mirarlo.
  · etiqueta sin señal   la medida lleva una etiqueta del lado «suma» sin
                         ninguna palabra que la respalde. Como las medidas que
                         suman son pocas y deciden el ratio, se revisan una a una.

Las señales NO clasifican: solo señalan qué leer. El resultado se escribe en
datos/informes/contraste-fiscal.md.
"""
import re

from . import clasificar, config, obsidian, rutas

SENALES = {
    'menos_ingresos': re.compile(
        r'(rebaj|reduc|baj|supr|elimin|deflact|exim)\w*[^.]{0,60}\b(impuest|irpf|iva\b|igic|tribut|cotizaci|'
        r'sucesiones|donaciones|patrimonio|fiscal)|deducci|exenci|exent[oa]s?\b|bonificaci\w+ fiscal|'
        r'incentivos? fiscal|tarifa plana|rebaja fiscal|tipo (reducido|superreducido)', re.I),
    'mas_ingresos': re.compile(
        r'fraude fiscal|econom[ií]a sumergida|nuevo impuesto|nueva tasa|(subir|elevar|aumentar|incrementar)\w*'
        r'[^.]{0,40}\b(impuest|tipo impositivo|tasa|tribut)|privatiz|venta de (participaciones|activos)|'
        r'vender\w*[^.]{0,60}participaci|gravamen|'
        r'(suprim|elimin)\w*[^.]{0,30}(deducci|beneficios? fiscal|exenci)', re.I),
    'menos_gasto': re.compile(
        r'(suprim|elimin|cerr|reduc|recort|fusion|disolv|liquid)\w*[^.]{0,60}\b(organismo|ministerio|subvenci|'
        r'asesor|cargos|gasto (pol[ií]tico|superfluo|ideol)|chiringuito|agencia|observatorio|empresas p[uú]blicas|'
        r'fundaci|duplicidad)|prioridad nacional', re.I),
    'consolidacion': re.compile(
        r'd[eé]ficit (p[uú]blico|estructural)|deuda p[uú]blica|reducir (el d[eé]ficit|la deuda)|reglas fiscales|'
        r'estabilidad presupuestaria|techo de gasto', re.I),
    'importe': re.compile(r'\d[\d.,]*\s*(mil millones|millones de euros|millones|€|euros)\b', re.I),
}
SUMAN = {'mas_ingresos', 'menos_gasto'}  # suman dinero a las cuentas públicas


def contrastar(pids) -> bool:
    lineas = ['# Contraste de la clasificación fiscal', '',
              'Discrepancias entre señales del texto y etiquetas. **Las señales no clasifican: indican qué leer.**', '']
    total = 0
    for pid in pids:
        fis = clasificar.cargar(pid, 'fiscal')
        if not fis:
            continue
        sigla = config.partido(pid)['sigla']
        bloque = []
        for s in clasificar.a_clasificar(pid):
            texto = f"{s['titulo']}. {s['texto']}"
            etiquetas = set(fis.get(s['id'], []))
            for etiqueta, patron in SENALES.items():
                m = patron.search(texto)
                if m and etiqueta not in etiquetas:
                    contexto = texto[max(0, m.start() - 50):m.end() + 50].replace('\n', ' ')
                    bloque.append(f'- `{s["id"]}` señal de **{etiqueta}** sin etiqueta '
                                  f'(lleva {sorted(etiquetas) or "[]"}): «…{contexto}…»')
            for etiqueta in sorted(etiquetas & SUMAN):
                if not SENALES[etiqueta].search(texto):
                    bloque.append(f'- `{s["id"]}` lleva **{etiqueta}** sin señal en el texto: '
                                  f'«{(s["titulo"] or s["texto"])[:110]}»')
        total += len(bloque)
        lineas += [f'## {sigla} · {len(bloque)} casos para revisar', '', *(bloque or ['Ninguno.']), '']
        print(f'   {pid}: {len(bloque)} casos para revisar')
    destino = rutas.INFORMES / 'contraste-fiscal.md'
    destino.parent.mkdir(parents=True, exist_ok=True)
    cab = obsidian.cabecera('proyecto', 'analisis', ['impacto-fiscal', 'contraste', 'revision-humana'],
                            'Contraste de la clasificación fiscal', 'datos/informes/contraste-fiscal.md')
    destino.write_text(cab + '\n'.join(lineas), encoding='utf-8')
    print(f'   {total} casos → {rutas.relativa(destino)}')
    return True
