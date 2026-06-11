from . import fetcher as fetcher
from . import parser as parser
from . import chunking as chunking
from . import derrogate as der
from . import unificate as un
import src.pipeline.utils as utils

import json
import os
# python3 -m src.pipeline.pipeline

def pipeline(documento: str, BD, delete_derrogations:bool, unificated_versions:bool)-> tuple:
    #Obtenemos el fichero del BOE en formato XML
    boe_file = fetcher.obtenerXML(documento)
    if boe_file is None:
        return False

    
    #Obtenemos los diferentes datos que vamos a extraer del fichero del BOE
    articulos, disposiciones, texto_extra, datos_globales= parser.getDatos(boe_file, documento)


    
    # Liberamos de la memoria el documento XML
    boe_file.close()
    del boe_file

    

    #Comprobamos si se tratan de artículos o disposiciones que modifican a otras y dejamos el artículo con la versión correspondiente
    if unificated_versions:
        articulos = un.main_unificate(BD, articulos)
        disposiciones = un.main_unificate(BD, disposiciones)

    
        
    #Añadimos el metadata necesaria
    utils.addMetadata(articulos, disposiciones, texto_extra, datos_globales)




    #Hacemos chunking sobre los datos que nos interesan
    articulos_chunked = chunking.make_chunking(articulos)
    disposiciones_chunked = chunking.make_chunking(disposiciones)
    texto_extra_chunked = chunking.make_chunking(texto_extra)


    #Añanidmos el texto
    articulos_chunked=utils.makeEnriquecerTextos(articulos_chunked, datos_globales)
    disposiciones_chunked=utils.makeEnriquecerTextos(disposiciones_chunked, datos_globales)
    texto_extra_chunked=utils.makeEnriquecerTextos(texto_extra_chunked, datos_globales)
    
    

    #Comprobamos si hay que eliminar algo que sea derrogado
    if delete_derrogations:
        der.main_derrogate(BD, disposiciones)

    
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
    return BD.addDocument(articulos_chunked, disposiciones_chunked, texto_extra_chunked, documento)

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