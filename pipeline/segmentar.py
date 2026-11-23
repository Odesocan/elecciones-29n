"""Etapa 3 · Texto → medidas numeradas (datos/segmentos/{partido}.jsonl).

El texto de cada medida es el del PDF tal cual: solo se unen líneas, se
deshacen los guiones de fin de línea y se sustituyen ligaduras (ﬁ → fi).

El orden del texto dentro del PDF no siempre es el de lectura (en el del
PP la medida 175 aparece en el flujo después de la 179), así que no se
exige que los números lleguen en secuencia: cada inicio «N TÍTULO» abre
una medida y al final se ordenan por número y se comprueban los huecos.

Formato de salida (una línea JSON por medida):
  id        «pp-083»  (partido + número con 3 cifras: clave de la clasificación)
  partido, ref («Medida 83»), pagina
  titulo, texto
  apartado  [capítulo, apartado, …]: dónde está la medida en el programa
            (ver apartados.py); contexto para clasificar y revisar
  aviso     '' · 'por anunciar' · 'Texto incompleto en el PDF original'
  piezas    (opcional) trozos que se verifican por separado si una medida
            se recompuso a partir de dos sitios del PDF
"""
import json
import re
from collections import Counter

from . import apartados, rutas
from .extraer import paginas, vocabulario
from .perfiles import perfil
from .texto import MAY, MIN, esqueleto, lineas, normalizar_glifos

# Medidas «por anunciar» (PP): «83Permanezca atento a la campaña…»
POR_ANUNCIAR = re.compile(r'(?:^|\s)(\d{1,3})\s*Permanezca\b', re.I)


def es_cabecera(l):
    """Línea en mayúsculas: título de apartado (cierra la medida en curso)."""
    return len(re.sub(rf'[^{MAY}{MIN}]', '', l)) >= 8 and not re.search(f'[{MIN}]', l)


def unir(ls):
    out = ''
    for l in ls:
        if l.startswith('•'):
            out = (out.rstrip() + '\n' + l) if out else l
            continue
        if out.endswith('-') and (re.match(f'[{MIN}]', l) or
                                  (re.search(f'[{MAY}]{{2}}-$', out) and re.match(f'[{MAY}]{{2}}', l))):
            out = out[:-1].rstrip() + l  # «deci-|siones», «INFRAES-|TRUCTURAS», «inme -|diato»
        elif re.search(r'\d-$', out) and re.match(r'\d', l):
            out = out + l  # rango partido en dos líneas: «2028-|2034»
        else:
            out = (out + ' ' + l) if out else l
    # Comillas decorativas sueltas que el PDF deja en los saltos de página («para ‘‘ qué»)
    out = re.sub(r'\s[‘’“”]{2}\s', ' ', out)
    out = re.sub(r'[ \t ]+', ' ', out)
    return re.sub(r' ?\n ?', '\n', out).strip()


# ── Ayudas para PDF difíciles (opcionales en el perfil) ─────────────────
# «Título ........ 15»; a veces Word deja un solo punto («… entorno digital . 84»)
TITULO_INDICE = re.compile(r'^(.*?\S)\s*(?:\.{2,}|\s\.)\s*\d{1,3}\s*$')
LETRAS = 'A-Za-zÁÉÍÓÚÜÑáéíóúüñ'


def titulos_indice(todas):
    """Títulos del índice («Título ......... 15»), en «esqueleto». Un título que
    ocupa dos líneas en el índice se une con la anterior, que no lleva puntos."""
    titulos, previo = [], ''
    for _, ls in todas[:10]:
        if sum(1 for l in ls if re.search(r'\.{4,}\s*\d{1,3}\s*$', l)) < 3:
            continue
        for l in ls:
            m = TITULO_INDICE.match(l)
            if m:
                titulos.append(esqueleto(f'{previo} {m.group(1)}'))
                previo = ''
            elif not re.fullmatch(r'\d{1,3}|ÍNDICE', l):
                previo = f'{previo} {l}'.strip()
    return [x for x in titulos if x]


def aperturas(ls, titulos):
    """Índices de las líneas de una página donde empieza un apartado del índice:
    la línea empieza en mayúscula y, unida a las dos siguientes, contiene el
    título entero (o es exactamente un título corto como «Juventud»)."""
    salida = set()
    for i, l in enumerate(ls):
        if not re.match(f'[{MAY}¿¡«"“]', l):
            continue
        junto = esqueleto(' '.join(ls[i:i + 3]))
        if esqueleto(l) in titulos or any(len(x) >= 8 and junto.startswith(x) for x in titulos):
            salida.add(i)
    return salida


def unir_numero_suelto(ls):
    """«419.» solo en su línea + la línea siguiente → «419. Impulsar…»."""
    out = []
    for l in ls:
        if out and re.fullmatch(r'\d{1,3}\.', out[-1]):
            out[-1] = f'{out[-1]} {l}'
        else:
            out.append(l)
    return out


def reparar_palabras(l, vocab):
    """Une las palabras que pypdf partió en dos («competitivid ad») cuando la
    palabra entera está en el vocabulario del modo layout y alguna de las dos
    piezas no lo está, y quita los espacios espurios antes de la puntuación.
    No cambia el «esqueleto»: la literalidad se verifica igual."""
    out = []
    for tok in l.split(' '):
        if out:
            pa = re.fullmatch(rf'(\W*)([{LETRAS}]+)', out[-1])
            pb = re.fullmatch(rf'([a-záéíóúüñ]+)(\W*)', tok)
            if pa and pb:
                a, b = pa.group(2).lower(), pb.group(1).lower()
                # «A probar» → «Aprobar»: letra mayúscula suelta a principio de frase
                inicial = len(a) == 1 and pa.group(2).isupper() and (len(out) == 1 or out[-2].endswith(('.', ':')))
                # «c on» → «con»: una consonante suelta no es palabra en castellano, aunque
                # el otro modo de extracción la parta igual (y por eso esté en el vocabulario)
                suelta = len(a) == 1 and a in 'bcdfghjklmnñpqrstvwxz'
                if (a + b) in vocab and (a not in vocab or b not in vocab or inicial or suelta):
                    out[-1] += tok
                    continue
        out.append(tok)
    l = ' '.join(out)
    l = re.sub(r'(?<=\S) +([,.;:)\]»”])', r'\1', l)
    l = re.sub(r'([(\[«“]) +', r'\1', l)
    return re.sub(r'(?<=\w) -(?=\w)', '-', l)


def _palabra_cortada(texto, frecuencias, vocab):
    """¿Acaba la medida en una palabra cortada («sus funcione»)? Sí si esa palabra
    solo aparece una vez en el documento y hay otra más larga que empieza igual."""
    ultima = (re.findall(r'[a-záéíóúüñç]+', texto.lower()) or [''])[-1]
    return frecuencias[ultima] <= 1 and any(w != ultima and w.startswith(ultima) for w in vocab)


def separar_titulo(texto, modo):
    if modo == 'mayusculas':
        for m in re.finditer(r'\.\s', texto):
            if not re.search(f'[{MIN}]', texto[:m.start()]):
                return texto[:m.start()].strip(), texto[m.end():].strip()
        return '', texto
    if modo == 'vox':
        # Hasta el primer punto (a veces con espacio delante: «Canarias .») o la primera viñeta
        m = re.match(r'^(.{4,400}?[^\s\.])\s?(\.\s+|\.$|\n(?=•))', texto)
        if m:
            return m.group(1).strip(), texto[m.end():].strip()
        return texto.split('\n')[0].strip(), '\n'.join(texto.split('\n')[1:]).strip()
    largo = 300 if modo == 'frase_flexible' else 180  # PSOE: titulares más largos
    m = re.match(rf'^(.{{4,{largo}}}?[^\s\.])\.\s+(?=[{MAY}¿¡«"“])', texto)
    return (m.group(1), texto[m.end():].strip()) if m else ('', texto)


def paginas_de_seccion(todas):
    # Páginas donde empieza un apartado según el índice («… - Pág. 28»):
    # allí lo primero es una introducción en prosa, no una medida.
    idx = ' '.join(' '.join(ls) for _, ls in todas[:10] if any('ÍNDICE' in l for l in ls))
    return {int(n) for n in re.findall(r'Pág\.\s*(\d{1,3})', idx)}


def segmentar(pid):
    c = perfil(pid)
    if c.unidad == 'parrafo':
        return segmentar_parrafos(pid, c)
    todas = [(i, lineas(c.con_vinetas(t))) for i, t in enumerate(paginas(pid), 1)]
    if c.numero_suelto:
        todas = [(i, unir_numero_suelto(ls)) for i, ls in todas]
    # El índice se lee antes de reparar palabras: la reparación quita el espacio
    # de «… entorno digital . 84», que es lo que lo distingue de una frase.
    titulos = titulos_indice(todas) if c.cierra_indice else []
    marcas, no_halladas = apartados.marcas(pid, todas, c.apartados) if c.apartados else ({}, [])
    if c.reparar_palabras:
        vocab = vocabulario(pid)
        todas = [(i, [reparar_palabras(l, vocab) for l in ls]) for i, ls in todas]
    vocab_layout = vocabulario(pid) if c.punto_final_opcional else set()
    frecuencias = Counter(re.findall(r'[a-záéíóúüñç]+', ' '.join(paginas(pid)).lower())) if c.punto_final_opcional else Counter()
    secciones = paginas_de_seccion(todas) if c.indice else set()
    bloques, vistos, actual, ruta = [], set(), None, []
    for pag, ls in todas:
        # Página separadora de capítulo (casi sin texto): lo que viene después
        # es la introducción en prosa del capítulo, no la medida anterior.
        if sum(len(l) for l in ls) < 60:
            actual = None
        abren = aperturas(ls, titulos) if titulos else set()
        for k, l in enumerate(ls):
            ruta = marcas.get((pag, k), ruta)
            if c.omitir(l):
                continue
            pend = POR_ANUNCIAR.search(l)
            if pend:
                n = int(pend.group(1))
                if n not in vistos:
                    vistos.add(n)
                    bloques.append({'n': n, 'pagina': pag, 'apartado': ruta, 'lineas': [], 'pendiente': True})
                actual = None
                continue
            m = c.inicio.match(l)
            salto_ok = not c.salto_max or not m or int(m.group(1)) <= max(vistos, default=0) + c.salto_max
            if m and int(m.group(1)) not in vistos and c.valida(l[m.end():]) and salto_ok:
                n = int(m.group(1))
                vistos.add(n)
                actual = {'n': n, 'pagina': pag, 'apartado': ruta, 'lineas': [l[m.end():]]}
                bloques.append(actual)
                continue
            if actual is None:
                continue
            if c.cierra(l) or k in abren:
                actual = None  # empieza un apartado (o el bloque «Compromisos»): la medida terminó
                continue
            en_titulo = c.titulo == 'mayusculas' and not re.search(f'[{MIN}]', ' '.join(actual['lineas']))
            if es_cabecera(l) and not en_titulo:
                actual = None  # empieza un apartado: la medida terminó
                continue
            actual['lineas'].append(l)

    salida = []
    for b in sorted(bloques, key=lambda b: b['n']):
        base = {'id': f'{pid}-{b["n"]:03d}', 'partido': pid, 'ref': f'Medida {b["n"]}', 'pagina': b['pagina'],
                'apartado': b['apartado']}
        if b.get('pendiente'):
            salida.append({**base, 'titulo': '', 'texto': '', 'aviso': 'por anunciar'})
            continue
        completo = unir(b['lineas'])
        if c.subtitulos_sueltos:
            # Subapartado sin número entre dos medidas («… especulativos. Según los
            # usos de la vivienda»): se quita antes de separar el titular.
            m = re.search(r'([\.\!\?»"\)])\s+([A-ZÁÉÍÓÚÜÑ][^\.\!\?]{3,70})$', completo)
            if m:
                completo = completo[:m.start(2)].strip()
        if c.titulo == 'lineas':
            # UPC: el titular son las líneas anteriores a la que abre el texto.
            k = next((i for i in range(1, len(b['lineas'])) if re.match(c.fin_titulo, b['lineas'][i])), len(b['lineas']))
            titulo, texto = unir(b['lineas'][:k]), unir(b['lineas'][k:])
        else:
            titulo, texto = separar_titulo(completo, c.titulo)
        # Subtítulo del PDF pegado al final («… Reconstruiremos el pacto entre
        # generaciones»): frase corta sin punto final tras la última frase.
        m = re.search(r'([\.\!\?»"\)])\s+([A-ZÁÉÍÓÚÜÑ][^\.\!\?]{3,70})$', texto)
        if m:
            texto = texto[:m.start(2)].strip()
        # Medida de una sola frase muy larga: se muestra como texto, no como titular.
        if not texto and len(titulo) > 140:
            titulo, texto = '', titulo + '.'
        # Medida de una sola frase (todo es título): está completa.
        aviso = '' if (not texto or re.search(r'[\.\!\?»"\)]$', texto)) else 'Texto incompleto en el PDF original'
        if aviso and c.punto_final_opcional and not _palabra_cortada(texto, frecuencias, vocab_layout):
            aviso = ''  # PSOE: muchas medidas acaban sin punto en el propio PDF
        if base['id'] in c.cortadas:
            aviso = 'Texto incompleto en el PDF original'
        if texto.endswith(':'):  # PSOE: «54. Destinar … a vivienda:» y las siguientes la desarrollan
            aviso = 'Introduce las medidas siguientes'
        salida.append({**base, 'titulo': titulo, 'texto': texto, 'aviso': aviso})
    reparar_continuaciones(salida)
    reordenadas = apartados.por_posicion(pid, salida, marcas) if marcas else []
    reordenadas += apartados.en_orden(salida, marcas)
    return salida, secciones, {'no_halladas': no_halladas, 'reordenadas': sorted(set(reordenadas))}


# ── Programas que solo numeran sus ejes (UPC desde el 23-11-2026) ────────
BLOQUE = re.compile(r'^BLOQUE\s+(\d+)\.\s*(.*)$')
VINETA = re.compile(r'^[-•]\s*(?=\S)')
FINAL = re.compile(r'[\.\:\;\!\?»"\)]$')  # un párrafo que acaba así puede cerrarse en la línea en blanco
CONECTOR = 6  # «Defendiendo entre otras actuaciones:»: hasta 6 palabras y dos puntos, sin contenido propio
# Un subapartado no acaba en una palabra de enlace: «… como mínimo del 0,7%, de los» es una línea cortada.
NEXOS = {'a', 'al', 'con', 'de', 'del', 'el', 'en', 'la', 'las', 'lo', 'los', 'o', 'para', 'por', 'que', 'se',
         'su', 'sus', 'un', 'una', 'y', 'e', 'u', 'ni', 'como', 'sobre', 'entre', 'hacia', 'desde', 'sin'}


def lineas_con_blancos(pagina):
    """Como texto.lineas, pero la línea en blanco se conserva como '' (separa párrafos)."""
    return [re.sub(r'\s+', ' ', l).strip() for l in normalizar_glifos(pagina).splitlines()]


def unir_sin_cortes(ls):
    """Une las líneas de un párrafo de Word, que no parte palabras con guion: el guion
    de final de línea es parte del texto («afectivo-|sexual» → «afectivo-sexual»;
    «Palestino -|denunciando» → «Palestino - denunciando»)."""
    out = ''
    for l in ls:
        if not out:
            out = l
        elif re.search(rf'[{LETRAS}]-$', out):
            out += l
        else:
            out += ' ' + l
    return re.sub(r'[ \t ]+', ' ', out).strip()


def segmentar_parrafos(pid, c):
    """Fragmentos de un programa sin medidas numeradas: cada párrafo o viñeta de
    un eje. Los ejes («1. La vivienda es un derecho y no un negocio.») y los
    bloques («BLOQUE 1. VIDA DIGNA…») dan la ruta que se guarda en «apartado»; el
    texto previo al primer eje (presentación) y el lema final no son fragmentos.

    Un fragmento termina en una línea en blanco si su texto acaba en puntuación
    final (si no, el párrafo sigue en la página siguiente), en una viñeta, en un
    eje, bloque o subapartado, o en un comienzo de «cortes_parrafo». Un
    subapartado es una línea corta sin puntuación final tras una línea en blanco
    («Agricultura y ganadería»)."""
    vocab = vocabulario(pid) if c.reparar_palabras else set()
    todas = []
    for pag, t in enumerate(paginas(pid), 1):
        for l in lineas_con_blancos(t):
            if l and c.omitir(l):
                continue  # número de página
            todas.append((pag, reparar_palabras(l, vocab) if (l and vocab) else l))

    bloques, ruta, eje, sub = [], {}, 0, ''
    actual, titulo_eje, en_bloque, fin, conectores = None, None, False, False, []

    def cerrar():
        nonlocal actual
        if actual and actual['lineas']:
            bloques.append(actual)
        actual = None

    def nuevo(pag, l):
        nonlocal actual
        cerrar()
        actual = {'pagina': pag, 'apartado': [x for x in (ruta.get('bloque'), ruta.get('eje'), sub) if x],
                  'eje': eje, 'vineta': bool(VINETA.match(l)), 'lineas': [VINETA.sub('', l)]}

    for k, (pag, l) in enumerate(todas):
        if fin:
            break
        if not l:  # línea en blanco
            if titulo_eje is not None:
                ruta['eje'] = re.sub(r'\.$', '', unir_sin_cortes(titulo_eje))
                titulo_eje = None
            en_bloque = False
            if actual and FINAL.search(actual['lineas'][-1]):
                cerrar()
            continue
        m = BLOQUE.match(l)
        if m:
            cerrar()
            ruta, sub, en_bloque = {'bloque': f'Bloque {m.group(1)}. {m.group(2)}'.strip()}, '', True
            continue
        if es_cabecera(l):
            if en_bloque:  # el título del bloque sigue en la línea siguiente («… DE» / «CANARIAS»)
                ruta['bloque'] += ' ' + l
                continue
            if eje:  # lema final en mayúsculas: el programa terminó
                cerrar()
                fin = True
            continue
        en_bloque = False
        m = c.inicio.match(l)
        if m and int(m.group(1)) == eje + 1 and c.valida(l[m.end():]):
            cerrar()
            eje, sub, titulo_eje = eje + 1, '', [l[m.end():]]
            continue
        if titulo_eje is not None:  # el título del eje ocupa dos líneas
            titulo_eje.append(l)
            continue
        if not eje:
            continue  # presentación anterior al primer eje
        siguiente = next((x for _, x in todas[k + 1:] if x), '')
        ultima = (l.split() or [''])[-1].lower()
        if (actual is None and not VINETA.match(l) and len(l) <= 75 and not FINAL.search(l)
                and re.match(f'[{MAY}]', l) and re.match(rf'[{MAY}\-•]', siguiente)
                and ultima not in NEXOS and not re.search(r'\d', l)):
            sub = l  # subapartado sin número
            continue
        if VINETA.match(l) or actual is None or any(l.startswith(x) for x in c.cortes_parrafo):
            nuevo(pag, l)
        else:
            actual['lineas'].append(l)
    cerrar()

    salida = []
    for b in bloques:
        texto = unir_sin_cortes(b['lineas'])
        if texto.endswith(':') and len(texto.split()) <= CONECTOR:
            conectores.append(texto)  # sin contenido propio: abre la lista que sigue
            continue
        titulo = ''
        m = re.match(rf'^([{MAY}][^.:;]{{3,60}}?)\s*:\s+(?=\S)', texto) if b['vineta'] else None
        if m and len(m.group(1).split()) <= 8:
            titulo, texto = m.group(1).strip(), texto[m.end():].strip()  # «• Mejora de los salarios: incremento…»
        n = len(salida) + 1
        salida.append({'id': f'{pid}-{n:03d}', 'partido': pid, 'ref': f'Eje {b["eje"]}', 'pagina': b['pagina'],
                       'apartado': b['apartado'], 'titulo': titulo, 'texto': texto,
                       'aviso': 'Introduce las medidas siguientes' if texto.endswith(':') else ''})
    if conectores:
        print(f'        conectores sin contenido propio (no son fragmentos): {conectores}')
    return salida, set(), {'no_halladas': [], 'reordenadas': []}


def reparar_continuaciones(salida):
    # Si una medida acaba cortada («… sancionar los in-») y en otra aparece al
    # final una continuación huérfana que empieza en minúscula tras un punto
    # («… legislatura. cumplimientos. Exigiremos…»), se devuelve a su sitio.
    # Se guardan las dos piezas para verificar cada una contra el PDF.
    # Solo cuando la palabra quedó partida con guion («in-»): señal inequívoca.
    # (En el PDF de Vox hay un «extraescolares. y la gratuidad…» literal que no es huérfano.)
    cortadas = [s for s in salida if s['aviso'] and s['aviso'] != 'por anunciar' and s['texto'].endswith('-')]
    for s in salida:
        m = re.search(r'(?<=[\.\!\?])\s+([a-záéíóúüñ][^\n]*[\.\!\?»"\)])$', s['texto'])
        if not m or not cortadas:
            continue
        previas = [c for c in cortadas if c['id'] < s['id']]
        if not previas:
            continue
        destino, huerfana = previas[-1], m.group(1)
        s['texto'] = s['texto'][:m.start()].strip()
        if destino['texto'].endswith('-'):
            destino['texto'] = destino['texto'][:-1] + huerfana
        else:
            destino['texto'] = destino['texto'] + ' ' + huerfana
        destino['piezas'] = [destino['texto'][:len(destino['texto']) - len(huerfana)], huerfana]
        destino['aviso'] = ''
        cortadas.remove(destino)
        print(f'   reparada {destino["id"]} con la continuación hallada al final de {s["id"]}')


def cargar(pid) -> list[dict]:
    ruta = rutas.SEGMENTOS / f'{pid}.jsonl'
    if not ruta.exists():
        return []
    return [json.loads(l) for l in ruta.read_text(encoding='utf-8').splitlines() if l.strip()]


def ejecutar(pids):
    rutas.SEGMENTOS.mkdir(parents=True, exist_ok=True)
    for pid in pids:
        anterior = {s['id']: (s['titulo'], s['texto']) for s in cargar(pid)}
        seg, secciones, ap = segmentar(pid)
        ruta = rutas.SEGMENTOS / f'{pid}.jsonl'
        with open(ruta, 'w', encoding='utf-8') as f:
            for s in seg:
                f.write(json.dumps(s, ensure_ascii=False) + '\n')

        nums = [int(s['id'].split('-')[1]) for s in seg]
        huecos = sorted(set(range(1, max(nums) + 1)) - set(nums)) if nums else []
        pend = [s['id'] for s in seg if s['aviso'] == 'por anunciar']
        cortes = [s['id'] for s in seg if s['aviso'] and s['aviso'] != 'por anunciar']
        sin_tit = [s['id'] for s in seg if not s['titulo'] and s['aviso'] != 'por anunciar']
        print(f'   {pid}: {len(seg)} medidas (máx. nº {max(nums) if nums else 0}) → {rutas.relativa(ruta)}')
        print(f'        números que faltan: {huecos or "ninguno"} · por anunciar: {len(pend)} · '
              f'posibles cortes: {cortes or "ninguno"} · sin titular: {len(sin_tit)}')
        if perfil(pid).indice:
            print(f'        págs. de apartado según el índice: {sorted(secciones)}')
        if perfil(pid).apartados:
            n_ap = len({apartados.texto(s['apartado']) for s in seg if s['apartado']})
            sin_ap = [s['id'] for s in seg if not s['apartado']]
            print(f'        apartados: {n_ap} con medidas · medidas sin apartado: {sin_ap or "ninguna"}'
                  + (f' · situadas por su posición en la página (el texto del PDF sale desordenado): {ap["reordenadas"]}'
                     if ap['reordenadas'] else '')
                  + (f' · ⚠ títulos del índice no hallados en el texto: {ap["no_halladas"]}' if ap['no_halladas'] else ''))
        # Cambios respecto a la versión anterior: si un texto cambia, su
        # clasificación hay que revisarla (el id se mantiene, el contenido no).
        if anterior:
            nuevo = {s['id']: (s['titulo'], s['texto']) for s in seg}
            cambian = sorted(i for i in nuevo if i in anterior and nuevo[i] != anterior[i])
            altas = sorted(set(nuevo) - set(anterior))
            bajas = sorted(set(anterior) - set(nuevo))
            if cambian or altas or bajas:
                print(f'        ⚠ respecto a lo anterior: cambian {cambian or "—"} · nuevas {altas or "—"} · '
                      f'desaparecen {bajas or "—"} → revisa su clasificación')
            else:
                print('        sin cambios respecto a lo anterior')
