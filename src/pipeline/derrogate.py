import re
import json
import src.pipeline.utils as utils
import src.llm.callToLLM as llm

def es_disposicion_derrogatoria(texto: str) -> bool:
    patron = r"\bdisposici[oó]n\s+derogatoria\b"
    return re.search(patron, texto, re.IGNORECASE) is not None

def identificar_derrogaciones(text:str)->list[json]:
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
    Extrae todos los números de 'que_afecta' en una lista.
    Incluye: artículos con decimales, números simples y combinaciones tipo 29.1.a
    """
    
    patron = r"\d+(?:\.\d+)*(?:\.[a-z])?\)?"

    resultados = re.findall(patron, texto)

    return [r.rstrip(")") for r in resultados]
    
def limpiarSalidaLLM(data):
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

def main_derrogate(disposiciones):
    to_delete=[]
    derrogaciones=[]
    #Identificamos la disposición de las derrogaciones
    for disposicion in disposiciones:
        if es_disposicion_derrogatoria(disposicion["titulo_articulo"]):
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

    #Cambiamos de la metadata el estado a derrogado
    if to_delete != []:
        for i in to_delete:
            BD.changeMetadata(i, "estado", "derrogado")