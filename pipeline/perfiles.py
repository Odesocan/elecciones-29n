"""Perfil de cada programa: cómo están numeradas y maquetadas sus medidas.

Cada PDF es distinto («1 TÍTULO EN MAYÚSCULAS», «1. Frase.», viñetas…), así
que esta es la única pieza que cambia de un partido a otro. Para añadir un
programa nuevo (PSOE, UPC…) basta con:

  1. Mirar en el PDF cómo empieza una medida y si hay cabeceras fijas en
     cada página (el lema de campaña, la fecha…).
  2. Añadir aquí su Perfil (copiar el más parecido) y ejecutar
     «python3 maestro.py segmentar --partido psoe»: el resumen dice cuántas
     medidas encuentra, qué números faltan y cuáles parecen cortadas.

Campos:
  inicio     regex de la línea donde empieza una medida; el grupo 1 es el número.
  valida     comprobación extra del resto de esa línea (evita falsos inicios
             como una cifra suelta a principio de línea).
  titulo     cómo separar el titular del texto: 'mayusculas' (PP), 'frase'
             (CC), 'vox' (hasta el primer punto o la primera viñeta) o 'lineas'
             (UPC: el titular son las líneas hasta la que cumple «fin_titulo»).
  modo       extracción de pypdf: 'plain' o 'layout' (columnas o tipografía
             que se descolocan en 'plain').
  cabeceras  líneas fijas de cada página que no forman parte de ninguna
             medida. Se omiten al segmentar y se toleran al verificar entre
             dos trozos de una medida que cruza de página.
  indice     si el PDF tiene un índice con «Pág. N» (solo informativo).

Opcionales (para PDF más difíciles, como el del PSOE):
  numero_suelto   une «419.» solo en su línea con la línea siguiente.
  cierres         regex de líneas que cierran la medida en curso (p. ej. «Compromisos»).
  cierra_indice   las líneas que empiezan un título del índice («Título ....... 15»)
                  cierran la medida: sirve cuando los apartados no van en MAYÚSCULAS.
  salto_max       un número solo abre medida si no salta más de N sobre el mayor visto
                  (evita que una lista interna «4. …» robe el número de una medida).
  reparar_palabras  pypdf (modo plain) parte algunas palabras en dos («competitivid ad»):
                  se unen cuando la palabra entera está en el vocabulario del modo layout,
                  y se quitan los espacios antes de puntuación. El «esqueleto» no cambia,
                  así que la literalidad se verifica igual.
  subtitulos_sueltos  quita un subapartado sin número pegado al final de una medida.
  punto_final_opcional  una medida sin punto final no se marca como cortada salvo que
                  acabe en una palabra cortada que solo aparece una vez en el documento.
  cortadas        ids de medidas cortadas en el propio PDF que la regla no detecta (se
                  comprueban a mano y se anotan aquí).
  numeros_en_salto  cuántos números sueltos (página, restos de listas) puede haber, al
                  verificar, entre dos trozos de una medida que cruza de página.
  vineta          carácter con el que el PDF dibuja las viñetas («o» en el del PSOE):
                  a principio de línea y ante mayúscula se convierte en «•», también
                  al verificar.
  fin_titulo      (con titulo='lineas') regex de la primera línea del texto: las anteriores
                  son el titular, que no acaba en punto y puede ocupar dos líneas.
  apartados       cómo marca el programa sus capítulos y apartados, para guardar en
                  cada medida en cuál está: 'pag', 'puntos', 'sangria' o 'causas'
                  (ver pipeline/apartados.py)."""
import re
from dataclasses import dataclass, field
from typing import Callable

from .texto import MAY, MIN


def valida_mayusculas(resto):
    # PP: el titular empieza en MAYÚSCULAS (al menos dos palabras sin minúsculas)
    cabeza = re.split(r'\.\s', resto, maxsplit=1)[0][:24]
    return not re.search(f'[{MIN}]', cabeza) and len(re.findall(f'[{MAY}]{{2,}}', cabeza)) >= 2


def valida_frase(resto):
    # CC: frase corta que acaba en punto
    return re.match(rf'^[{MAY}¿¡«"][^.]{{3,160}}\.', resto) is not None


def valida_inicio(resto):
    # PSOE: el titular empieza en mayúscula y puede seguir en la línea siguiente
    return re.match(rf'^[{MAY}¿¡«"“]\S*\s+\S', resto) is not None


def valida_frase_o_vinetas(resto):
    # Vox: frase que acaba en punto o da paso a viñetas «•»
    return re.match(rf'^[{MAY}¿¡«"][^.•]{{3,400}}(\.|•|$)', resto) is not None


@dataclass(frozen=True)
class Perfil:
    inicio: re.Pattern
    valida: Callable[[str], bool]
    titulo: str
    modo: str = 'plain'
    cabeceras: tuple = ()
    indice: bool = False
    notas: str = ''
    numero_suelto: bool = False
    cierres: tuple = ()
    cierra_indice: bool = False
    salto_max: int = 0
    reparar_palabras: bool = False
    subtitulos_sueltos: bool = False
    punto_final_opcional: bool = False
    cortadas: tuple = ()
    numeros_en_salto: int = 1
    vineta: str = ''
    apartados: str = ''
    fin_titulo: str = ''
    _omitir: re.Pattern = field(init=False, repr=False, compare=False)

    def __post_init__(self):
        patron = '|'.join([*(re.escape(c) for c in self.cabeceras), r'\d{1,3}'])
        object.__setattr__(self, '_omitir', re.compile(rf'^({patron})$'))

    def omitir(self, linea):
        """¿Es una línea de maquetación (nº de página o cabecera fija)?"""
        return self._omitir.match(linea) is not None

    def con_vinetas(self, texto):
        """«o Acelerar…» a principio de línea → «• Acelerar…» (si el perfil tiene viñeta)."""
        if not self.vineta:
            return texto
        texto = re.sub(r'(?m)^[ \t]*[●▪■][ \t]*', '• ', texto)  # otras viñetas del mismo PDF
        return re.sub(rf'(?m)^[ \t]*{re.escape(self.vineta)}[ \t]+(?=[{MAY}])', '• ', texto)

    def cierra(self, linea):
        """¿Cierra la línea la medida en curso (p. ej. «Compromisos»)?"""
        return any(re.match(c, linea) for c in self.cierres)


PERFILES = {
    'pp': Perfil(
        inicio=re.compile(rf'^(\d{{1,3}})\s*(?=[{MAY}¿¡«"])'),
        valida=valida_mayusculas,
        titulo='mayusculas',
        modo='plain',  # en 'layout' las citas destacadas de la columna lateral se intercalan
        indice=True,
        apartados='pag',
        notas='«83 EN CIEN DÍAS…»: número pegado al titular en mayúsculas. 8 medidas «Permanezca atento…».',
    ),
    'cc': Perfil(
        inicio=re.compile(rf'^(\d{{1,3}})\.\s+(?=[{MAY}¿¡«"])'),
        valida=valida_frase,
        titulo='frase',
        modo='layout',
        cabeceras=('DEFIENDE', 'CANARIAS', '29 DE NOVIEMBRE DE 2026'),
        apartados='causas',
        notas='«1. Cumplir el Estatuto. Exigiremos…». La medida 11 está cortada en el propio PDF.',
    ),
    'vox': Perfil(
        inicio=re.compile(rf'^(\d{{1,3}})\.\s+(?=[{MAY}¿¡«"])'),
        valida=valida_frase_o_vinetas,
        titulo='vox',
        modo='plain',
        cabeceras=('ES SENTIDO COMÚN',),
        apartados='puntos',
        notas='«1. Titular. Texto» o «1. Titular:» seguido de viñetas «•». Hay medidas de una sola frase.',
    ),
    'psoe': Perfil(
        inicio=re.compile(rf'^(\d{{1,3}})\.\s+(?=[{MAY}¿¡«"“])'),
        valida=valida_inicio,
        titulo='frase_flexible',
        modo='plain',  # en 'layout' el número sale duplicado («1 1.») y se pierden 45 inicios
        numero_suelto=True,
        cierres=(r'^Compromisos$',),
        cierra_indice=True,
        salto_max=5,
        reparar_palabras=True,
        subtitulos_sueltos=True,
        punto_final_opcional=True,
        cortadas=('psoe-395',),
        numeros_en_salto=6,
        apartados='sangria',
        vineta='o',  # las viñetas de Word salen como «o Acelerar…»  # al pie de página quedan números de lista sueltos («134 136 137»)  # «…el correcto desempeño de sus funcione» y salta a la 396
        notas='500 compromisos con numeración correlativa, en bloques «Compromisos» tras la prosa de cada '
              'apartado. Los títulos de apartado van en minúscula: se cierran con el índice. «419.» lleva el '
              'titular en la línea siguiente.',
    ),
    'upc': Perfil(
        inicio=re.compile(rf'^(\d{{1,2}})\.\s+(?=[{MAY}])'),
        valida=valida_inicio,
        titulo='lineas',
        fin_titulo=rf'^[{MAY}][{MIN}]+mos\b',  # «Defendemos», «Exigimos», «Reclamamos», «Defenderemos»…
        modo='layout',  # en 'plain' pypdf parte palabras («pol ítico», «canari as»)
        reparar_palabras=True,  # el layout también parte alguna («s ean»): se repara con el vocabulario de 'plain'
        notas='Manifiesto de 16 ejes «N. Título» (sin punto, a veces en dos líneas) seguidos de uno o dos '
              'párrafos que empiezan en primera persona del plural. Sin índice ni apartados: los ejes son las medidas.',
    ),
}


def perfil(pid) -> Perfil:
    if pid not in PERFILES:
        raise SystemExit(
            f'No hay perfil de segmentación para «{pid}». Añádelo en pipeline/perfiles.py '
            '(instrucciones al principio del archivo).'
        )
    return PERFILES[pid]
