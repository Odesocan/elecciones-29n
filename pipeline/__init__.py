"""Pipeline de datos: de los PDF oficiales al CSV que lee la web.

Etapas (cada una en su módulo, en este orden):

    descargar   → datos/fuentes/*.pdf           PDF oficiales + huella SHA-256
    extraer     → datos/texto/*.json            texto de cada página (caché)
    segmentar   → datos/segmentos/*.jsonl       una línea por medida numerada
    clasificar  → datos/clasificacion/*.json    temas de cada medida (IA + revisión humana)
    verificar   ·                               cada texto está literalmente en el PDF
    exportar    → web/public/data/programas.csv CSV de la web + hoja de revisión + informe

Se orquesta desde ../maestro.py. Ningún módulo lee rutas ni ajustes por su
cuenta: las rutas están en rutas.py y los ajustes en ../config/*.json.
"""
