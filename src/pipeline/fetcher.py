import requests
from io import BytesIO

def obtenerXML(num_boe: str) -> BytesIO | None:
    """
    Obtiene el contenido de una disposición del BOE en memoria como XML.

    Args:
        num_boe (str): Identificador de la disposición, por ejemplo 'BOE-A-2024-12345'.

    Returns:
        BytesIO: Objeto tipo archivo en memoria con el contenido XML, si la descarga fue correcta.
        None: Si la descarga falla (status distinto de 200).
    """
    BOE_url = f"https://www.boe.es/diario_boe/xml.php?id={num_boe}"
    
    try: 
        response = requests.get(BOE_url, timeout=10)

        if response.status_code == 200:
            return BytesIO(response.content)
        
        return None
    
    except requests.RequestException:
        return None

def DescargaXML(num_boe: str) -> None:
    """
    Descarga el contenido de una disposición del BOE en la carpeta data/num_boe.

    Args:
        num_boe (str): Identificador de la disposición, por ejemplo 'BOE-A-2024-12345'.

    """
    BOE_url = f"https://www.boe.es/diario_boe/xml.php?id={num_boe}"
    response = requests.get(BOE_url)

    if response.status_code == 200:
        #Este código guarda en data el fichero, para no estar obteniendo todo el rato el docuemnto
        xml_filename = f"data/{num_boe}.xml"
        with open(xml_filename, "wb") as f:
            f.write(response.content)

        print("Descarga generada con exito!")
    else:
        print("Error, no se ha podido acceder a ese docuento")

#DescargaXML("BOE-A-1995-25444")
    