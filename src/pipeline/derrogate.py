import re
import json
import src.pipeline.utils as utils
import src.llm.callToLLM as llm

def es_disposicion_derrogatoria(texto: str) -> bool:
    """
    Comprueba si un texto contiene la expresión "disposición derogatoria".

    Args:
        texto (str): Texto en el que se quiere comprobar la existencia
                    de una disposición derogatoria.

    Returns:
        bool: True si el texto contiene "disposición derogatoria".
            False en caso contrario.
    """
    patron = r"\bdisposici[oó]n\s+derogatoria\b"
    return re.search(patron, texto, re.IGNORECASE) is not None

def identificar_derrogaciones(text:str)->list[json]:
    """
    Identifica las derogaciones expresas presentes en un texto jurídico
    utilizando un modelo de lenguaje y devuelve la información
    estructurada en formato JSON.

    Args:
        text (str): Texto jurídico del que se quieren extraer las derogaciones.

    Returns:
        list[json]: Lista de objetos JSON con la norma afectada y los artículos
                    que se derogan. Devuelve una lista vacía si no se encuentran
                    derogaciones válidas o si no se obtiene una respuesta válida
                    tras varios intentos.
    """

    intentos=3
    intento=0
    format = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "target_norma": {"type": "string"},
                "que_afecta": {"type": "string"}
            },
            "required": ["target_norma", "que_afecta"]
        }
    }

    system_prompt = """
    Eres un extractor jurídico. Tu única función es detectar DEROGACIONES EXPRESAS y devolver SOLO JSON.
    
    SALIDA:
    - Solo un array JSON válido
    - Si no hay resultados: []
    
    FORMATO:
    [
      {
        "target_norma": "nombre de la norma",
        "que_afecta": "artículos o 'todo'"
      }
    ]
    
    REGLAS:
    - target_norma: identificador de la norma
    - que_afecta:
      - SOLO números de artículos (ej: "2.3, 10, 29.1.a, 29.1.d")
      - si derogación total o no especifica artículos: "todo"
      - NUNCA usar frases como "artículos mencionados"
    
    NORMALIZACIÓN:
    - eliminar palabras como "artículo(s)"
    - quitar paréntesis finales "ej: 29.1.a) → 29.1.a"
    - separar por comas
    
    PROHIBIDO:
    - copiar encabezados completos como target_norma
    - inferir información no explícita
    - añadir texto explicativo
    - devolver frases en que_afecta
    
    UNA DEROGACIÓN = UN OBJETO
    """
    

    user_prompt=f"""
            Extraeme las derrogaciones de la siguiente disposición:
            {text}
        """

    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}]

    while True:
        response= llm.call_ollama(messages, format)

        try:
            data = json.loads(response)
            return data
        except Exception:
        
            intento+=1
            if intento>=intentos:
                print("salida forzada")
                return []

def extraer_numeros_leyes_modificadas(texto: dict):
    """
    Extrae los números de los artículos indicados en el texto.

    Args:
        texto (dict): Texto del que se quieren extraer los números de los
                    artículos afectados.

    Returns:
        list[str]: Lista de números de artículos encontrados, incluyendo
                números simples, artículos con decimales y combinaciones
                como "29.1.a".
    """
    
    patron = r"\d+(?:\.\d+)*(?:\.[a-z])?\)?"

    resultados = re.findall(patron, texto)

    return [r.rstrip(")") for r in resultados]
    
def limpiarSalidaLLM(data):
    """
    Limpia y normaliza la salida generada por el modelo de lenguaje,
    extrayendo la ley afectada y transformando los artículos indicados
    en un formato estructurado.

    Args:
        data (list): Lista de derogaciones generadas por el modelo,
                    con la norma afectada y los elementos que se derogan.

    Returns:
        list: Lista de diccionarios con las derogaciones normalizadas.
            Las derogaciones totales se identifican por tipo "ley",
            mientras que las derogaciones de artículos se identifican
            por tipo "articulo".
    """
    out=[]
    for i in data:
        ley=utils.extraer_ley(i["target_norma"])

        if ley is not None:
            if i["que_afecta"]=="todo":
                out.append({"tipo":"ley", "target":ley})
            else:
                articulos=extraer_numeros_leyes_modificadas(i["que_afecta"])
                if articulos != []:
                    for articulo in articulos:
                        out.append({"tipo":"articulo", "ley": ley, "target": articulo})

    return out

def main_derrogate(BD, disposiciones):
    """
    Identifica y procesa las derogaciones contenidas en un conjunto de
    disposiciones, utilizando un LLM para detectar las normas y artículos
    derogados y actualizando su estado en la base de datos.

    Args:
        BD: Base de datos sobre la que se actualizará el estado de las normas
            y artículos derogados.

        disposiciones (list): Lista de disposiciones que se analizarán para
                            identificar aquellas que contienen derogaciones.

    Returns:
        tuple: Número de normas completas y número de artículos cuyo estado
            se ha actualizado correctamente a "derrogado".
    """
    
    to_delete=[]
    derrogaciones=[]
    #Identificamos la disposición de las derrogaciones
    for disposicion in disposiciones:
        if es_disposicion_derrogatoria(disposicion["titulo"]):
            derrogaciones.append(disposicion)

    for i in derrogaciones:
        #Identificamos las leyes y normas que se derrogan con un llm
        data=identificar_derrogaciones(i["cuerpo"])

        #limpiamos la salida del llm
        data=limpiarSalidaLLM(data)
        
        #Eliminamos los datos encontrados de la bd
        for norma in data:
            if norma["tipo"] == "ley":
                to_delete.append([{"numero_norma": norma["target"]}])
            else:
                to_delete.append([
                    {"numero_norma": norma["ley"]},
                    {"num_articulo": norma["target"]}
                ])

    files_deleted=0
    art_deleted=0
    #Cambiamos de la metadata el estado a derrogado
    if to_delete != []:
        for i in to_delete:
            out = BD.changeMetadata(i, "estado", "derrogado")
            if out==True:
                if len(i)==1:
                    files_deleted+=1
                else:
                    art_deleted+=1

    return files_deleted, art_deleted