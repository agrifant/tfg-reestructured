import json
import os
import pipeline.fetcher as fetcher
import pipeline.parser as parser


# python3 -m tests.prueba1

# Esta función descarga los archivos de la constitución y 
# mueve toda la información obtenida por limpieza de datos
# a dos archivos .json en la carpeta data 
def DescargaArticulos():
    #Nombre identificativo del boe a buscar
    documento = input("Introduce Identificador documento: ")

    #Función que obtiene el boe que queremos
    boe_file = fetcher.obtenerXML(documento)

    #Limpiamos los datos para obtener los artículos y texto no definido del boe
    articulos, disposiciones, texto_extra = parser.obtenerArticulos(boe_file, documento)

    datos_globales, materias = parser.obtenerDatosGlobales(boe_file)

    # Liberar memoria del XML
    boe_file.close()
    del boe_file

    ruta = "data/documentos"+documento
    if not os.path.exists(ruta):
        os.makedirs(ruta)

    with open(ruta+"/disposiciones.json", "w", encoding="utf-8") as f:
        json.dump(disposiciones, f, indent=4, ensure_ascii=False)

    with open(ruta+"/articulos.json", "w", encoding="utf-8") as f:
        json.dump(articulos, f, indent=4, ensure_ascii=False)

    with open(ruta+"/textos_extra.json", "w", encoding="utf-8") as f:
        json.dump(texto_extra, f, indent=4, ensure_ascii=False)

    with open(ruta+"/documento.json", "w", encoding="utf-8") as f:
        json.dump(datos_globales, f, indent=4, ensure_ascii=False)

    with open(ruta+"/materias.json", "w", encoding="utf-8") as f:
        json.dump(materias, f, indent=4, ensure_ascii=False)

    print(f"Archivos generados en {ruta}")

DescargaArticulos()