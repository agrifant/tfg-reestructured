from . import fetcher as fetcher
from . import parser as parser
from . import chunking as chunking
from . import derrogate as der
from . import unificate as un
import src.pipeline.utils as utils

import json
import os
# python3 -m src.pipeline.pipeline

def pipeline(documento: str, BD, delete_derrogations:bool, unificated_versions:bool, dim:int)-> tuple:
    """
    Ejecuta el pipeline completo de extracción y procesamiento de datos
    del documento y almacena los resultados en la base de datos.

    Args:
        documento (str): Documento que se procesará mediante el pipeline.

        BD: Base de datos en la que se almacenarán los resultados obtenidos.

        delete_derrogations (bool): Indica si se deben procesar y aplicar
                                    las derogaciones detectadas.

        unificated_versions (bool): Indica si se deben unificar las diferentes
                                    versiones de las normas.

        dim (int): Dimensión utilizada en el embedding en la BD.

    Returns:
        bool: Si se ha podido realizar exitosamente o no
    """
    art_unificated=0

    #Obtenemos el fichero del BOE en formato XML
    intentos = 3

    for _ in range(intentos):
        boe_file = fetcher.obtenerXML(documento)
        if boe_file is not None:
            break
    else:
        return False, 0, 0, 0
        

    
    #Obtenemos los diferentes datos que vamos a extraer del fichero del BOE
    articulos, disposiciones, texto_extra, datos_globales= parser.getDatos(boe_file, documento)


    
    # Liberamos de la memoria el documento XML
    boe_file.close()
    del boe_file



    #Añadimos el metadata necesaria
    utils.addMetadata(articulos, disposiciones, texto_extra, datos_globales)


    
    #Comprobamos si se tratan de artículos o disposiciones que modifican a otras y dejamos el artículo con la versión correspondiente
    if unificated_versions:
        articulos, aux= un.main_unificate(BD, articulos, datos_globales)
        art_unificated+=aux
        disposiciones, aux = un.main_unificate(BD, disposiciones, datos_globales)
        art_unificated+=aux

        
        
    #Hacemos chunking sobre los datos que nos interesan
    articulos_chunked = chunking.make_chunking(articulos)
    disposiciones_chunked = chunking.make_chunking(disposiciones)
    texto_extra_chunked = chunking.make_chunking(texto_extra)


    #Añanidmos el texto
    articulos_chunked=utils.makeEnriquecerTextos(articulos_chunked, datos_globales)
    disposiciones_chunked=utils.makeEnriquecerTextos(disposiciones_chunked, datos_globales)
    texto_extra_chunked=utils.makeEnriquecerTextos(texto_extra_chunked, datos_globales)
    
    

    #Comprobamos si hay que eliminar algo que sea derrogado
    art_delete = 0
    files_delete = 0
    if delete_derrogations:
        art_delete, files_delete = der.main_derrogate(BD, disposiciones)

    
    #Irelevante
    """
    os.makedirs("data", exist_ok=True)    

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

    #Añadimos los chunks a la BD
    return BD.addDocument(articulos_chunked, disposiciones_chunked, texto_extra_chunked, documento, dim), art_unificated, art_delete, files_delete

def generarContextoPreguntas(documento:str)->list:
    """
    Extre sobre el documento indicado los artículos y disposiciones.

    Args:
        documento (str): Identificador del BOE que se procesará mediante el pipeline.

    Returns:
        bool: Lista de los diferentes artículos y disposiciones detectadas
    """
    #Función que obtiene el boe que queremos
    boe_file = fetcher.obtenerXML(documento)

    #Obtenemos las diferentes partes del boe que nos interesan
    articulos, disposiciones, _, datos_globales = parser.getDatos(boe_file, documento)

    # Liberar memoria del XML
    boe_file.close()
    del boe_file

    #Añadimos el metadata necesaria
    utils.addMetadata(articulos, disposiciones, _, datos_globales)

    #Hacemos chunking sobre los datos que nos interesan
    articulos_chunked=chunking.make_chunking(articulos)
    disposiciones_chunked=chunking.make_chunking(disposiciones)

    #Añadimos metadata necesaria
    documentos=[]
    for articulo in articulos_chunked:
        documentos.append(datos_globales["titulo_norma"]+articulo["titulo"]+articulo["cuerpo"])

    for disp in disposiciones_chunked:
        documentos.append(datos_globales["titulo_norma"]+disp["titulo"]+disp["cuerpo"])

    return documentos