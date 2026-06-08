from . import fetcher as fetcher
from . import parser as parser
from . import chunking as chunking
from . import derrogate as der
import src.pipeline.utils as utils

import json
import os
# python3 -m src.pipeline.pipeline

def pipeline(documento: str, delete_derrogations:bool, unificated_versions:bool)-> tuple:
    """
        Procesa un documento BOE y genera chunks de los textos relevantes para análisis o almacenamiento.

        Pasos del pipeline:
            1. Obtener el archivo XML del BOE mediante `fetcher.obtenerXML`.
            2. Extraer las diferentes partes del BOE de interés:
                - Artículos
                - Disposiciones
                - Texto extra
            y también los datos globales y materias mediante `parser`.
            3. Liberar memoria cerrando el archivo XML.
            4. Realizar chunking de los textos relevantes usando
            `chunking.chunkear_diccionario`:
                - Cada artículo
                - Cada disposición
                - Cada texto extra
            5. Devolver los datos procesados y los chunks generados.

        Args:
            documento (str): Identificador o ruta del BOE a procesar.

        Returns:
            tuple: Contiene los siguientes elementos:
                - datos_globales (dict): Información general del BOE extraída del XML.
                - materias (list[str]): Lista de materias asociadas al BOE.
                - articulos_chunked (list[tuple]): Lista de tuplas (articulo, chunks) donde
                `chunks` es la lista de diccionarios resultante del chunking del artículo.
                - disposiciones_chunked (list[tuple]): Lista de tuplas (disposición, chunks) similares a los artículos.
                - texto_extra_chunked (list[tuple]): Lista de tuplas (texto extra, chunks).

        Notes:
            - Se asume que cada `articulo`, `disposicion` o `texto_extra` contiene un campo `"cuerpo"` que se puede chunkear.
            - La función libera memoria cerrando el XML antes de realizar el chunking.
            - Los chunks devueltos cumplen los límites de tokens establecidos en `chunkear_diccionario`.
    """
    #Función que obtiene el boe que queremos
    boe_file = fetcher.obtenerXML(documento)

    #Obtenemos las diferentes partes del boe que nos interesan
    articulos, disposiciones, texto_extra, datos_globales, materias= parser.getDatos(boe_file, documento)

    # Liberar memoria del XML
    boe_file.close()
    del boe_file

    #Hacemos chunking sobre los datos que nos interesan
    articulos_chunked=[]
    disposiciones_chunked=[]
    texto_extra_chunked=[]

    for articulo in articulos:
        articulos_chunked.extend(chunking.chunkear_diccionario(articulo, "cuerpo"))

    for disposicion in disposiciones:
        disposiciones_chunked.extend(chunking.chunkear_diccionario(disposicion, "cuerpo"))

    for extra in texto_extra:
        texto_extra_chunked.extend(chunking.chunkear_diccionario(extra, "cuerpo"))

    #Añanidmos el texto
    for articulo in articulos_chunked:
        articulo["cuerpo"] = utils.enriquecerTextos(
            articulo,
            datos_globales,
            materias
        )

    for disp in disposiciones_chunked:
        disp["cuerpo"] = utils.enriquecerTextos(
            disp,
            datos_globales,
            materias
        )

    for text in texto_extra_chunked:
        text["cuerpo"] = utils.enriquecerTextos(
            text,
            datos_globales,
            materias
        )
    
    
    
    #Irelevante
    """
    os.makedirs("data", exist_ok=True)
    
    with open(f"data/articulos{documento}.json", "w", encoding="utf-8") as f:
        json.dump(articulos, f, ensure_ascii=False, indent=2)
        os.makedirs("data", exist_ok=True)
    
    with open(f"data/disposiciones{documento}.json", "w", encoding="utf-8") as f:
        json.dump(disposiciones, f, ensure_ascii=False, indent=2)
    
    

    with open(f"data/articulos_chunked{documento}.json", "w", encoding="utf-8") as f:
        json.dump(articulos_chunked, f, ensure_ascii=False, indent=2)
        os.makedirs("data", exist_ok=True)
    
    with open(f"data/disposiciones_chunked{documento}.json", "w", encoding="utf-8") as f:
        json.dump(disposiciones_chunked, f, ensure_ascii=False, indent=2)

    with open(f"data/texto_extra_chunked{documento}.json", "w", encoding="utf-8") as f:
        json.dump(texto_extra_chunked, f, ensure_ascii=False, indent=2)
    
    with open(f"data/datos_globales{documento}.json", "w", encoding="utf-8") as f:
        json.dump(datos_globales, f, ensure_ascii=False, indent=2)
    """

    to_delete=[]
    if delete_derrogations:
        to_delete.extend(der.main_derrogate(disposiciones))
            
    if unificated_versions:
        print("unificando")
    
    
    return datos_globales, articulos_chunked, disposiciones_chunked, texto_extra_chunked, to_delete

def generarContextoPreguntas(documento:str)->list:
    #Función que obtiene el boe que queremos
    boe_file = fetcher.obtenerXML(documento)

    #Obtenemos las diferentes partes del boe que nos interesan
    articulos, disposiciones, _, data_global, _= parser.getDatos(boe_file, documento)

    # Liberar memoria del XML
    boe_file.close()
    del boe_file

    #Hacemos chunking sobre los datos que nos interesan
    articulos_chunked=[]
    disposiciones_chunked=[]
    texto_extra_chunked=[]

    for articulo in articulos:
        articulos_chunked.extend(chunking.chunkear_diccionario(articulo, "cuerpo"))

    for disposicion in disposiciones:
        disposiciones_chunked.extend(chunking.chunkear_diccionario(disposicion, "cuerpo"))

    documentos=[]
    for articulo in articulos_chunked:
        documentos.append(data_global["titulo"]+articulo["titulo_articulo"]+articulo["cuerpo"])

    for disp in disposiciones_chunked:
        documentos.append(data_global["titulo"]+disp["titulo_articulo"]+disp["cuerpo"])

    """for text in texto_extra_chunked:
        documentos.append(text["cuerpo"])"""

    with open(f"data/datosPreguntas{documento}.json", "w", encoding="utf-8") as f:
        json.dump(documentos, f, ensure_ascii=False, indent=2)

    return documentos
#pipeline("BOE-A-2015-3439")