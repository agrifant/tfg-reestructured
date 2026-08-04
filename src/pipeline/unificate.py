import re
import src.pipeline.utils as utils
import src.extractArticulo as ext
import src.llm.callToLLM as llm
import json

def unifacte_norma(old_text, new_text)->list[json]:
    intentos=3
    intento=0

    system_prompt = """
        Eres un experto en consolidación legislativa.
        
        Tu tarea es integrar modificaciones normativas en un texto legal existente.
        
        Instrucciones:
        - Recibirás un texto legal vigente y un texto que contiene modificaciones.
        - Debes aplicar las modificaciones sobre el texto vigente.
        - Conserva exactamente el contenido que no haya sido modificado.
        - No inventes contenido ni introduzcas interpretaciones jurídicas.
        - Si una modificación sustituye un artículo completo, reemplázalo íntegramente.
        - Si añade texto, incorpóralo en la ubicación correspondiente.
        - Si elimina texto, suprímelo.
        - Devuelve únicamente el texto consolidado final.
        - No incluyas explicaciones, comentarios ni justificaciones.

        IMPORTANTE:
        - No añadas texto exta, solo devuelve el artículo tal cual
        """
    

    user_prompt = f"""
        TEXTO VIGENTE
        
        {old_text}
        
        MODIFICACIÓN
        
        {new_text}
        
        Genera la versión consolidada resultante tras aplicar la modificación al texto vigente.
        """

    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}]

    num_old_words = len(old_text.split())
    num_new_words = len(old_text.split())
    
    # Aproximación: 1 palabra ≈ 1.3 tokens
    num_predict = int((num_old_words + num_new_words) * 1.3) + 100
    while True:
        return llm.call_ollama(messages, None, num_predict)
                
def esModificativo(texto):
    patrones = [
        "modifica",
        "modificación",
        "se modifica",
        "se añade",
        "se adiciona"
    ]

    return any(p in texto for p in patrones)

def extraerIntro(texto):
    PATRON_INICIO = re.compile(r"^(uno)\.\s")
    lineas = []

    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea:
            continue

        # si empieza la numeración, paramos
        if PATRON_INICIO.match(linea):
            break

        lineas.append(linea)

    return " ".join(lineas).strip()

import re

def extraerSubarticulos(texto):
    patrones = re.compile(
        r"\b(se modifica|modifica|modificación|se añade|se adiciona)\b",
        re.IGNORECASE
    )

    con_patron = []
    bloque_actual = None

    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea:
            continue

        # Si detecta patrón → nuevo bloque
        if patrones.search(linea):
            if bloque_actual:
                con_patron.append(bloque_actual)

            bloque_actual = linea
        else:
            # si ya hay bloque abierto, lo extendemos
            if bloque_actual:
                bloque_actual += " " + linea
            else:
                # si aún no hay patrón, lo ignoramos o lo puedes guardar aparte
                continue

    # cerrar último bloque
    if bloque_actual:
        con_patron.append(bloque_actual)

    return con_patron

"""
def extraerSubarticulos_prev(texto):
    PATRON = re.compile(r"^(uno|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|\d+)\.\s")
    
    subarticulos = []
    actual = None

    for linea in texto.splitlines():
        linea = linea.strip()
        if not linea:
            continue

        m = PATRON.match(linea)

        if m:
            actual = {
                "numero": m.group(1),
                "texto": linea[len(m.group(0)):].strip()
            }
            subarticulos.append(actual)
        else:
            # continuidad del anterior
            if actual:
                actual["texto"] += " " + linea

    return subarticulos
"""

def main_unificate(BD, articulos, datos_globales):
    all_articulos=[]
    num_art_unificate=0
    
    for articulo in articulos:
        titulo=articulo["titulo"]
        texto=articulo["cuerpo"]
        texto_total = (titulo + " " + texto).lower()
        
        #Si no es un artículo que es modificativo paramos la iteracion
        if not esModificativo(texto_total):
            all_articulos.append(articulo)
            continue

        
        #Buscamos la ley a la que modifica
        intro=extraerIntro(texto_total)
        ley=utils.extraer_ley(intro)
        if ley is None:
            all_articulos.append(articulo)
            continue


        #Dividimos la norma en subartículos (suele estar compuesta por varios artículos)
        subarticulos=extraerSubarticulos(texto_total)
        if subarticulos == []:
            all_articulos.append(articulo)
            continue



        for subarticulo in subarticulos:
            texto_modificacion=subarticulo

            #Extraemos el número del artículo al que modifica
            num_art=ext.extract_articulo(texto_modificacion)
            if num_art is None:
                aux=[{
                    "cuerpo":texto_modificacion,
                    "titulo": articulo["titulo"],
                    "id":articulo["id"]
                }]
                
                utils.addMetadata(aux, [], [], datos_globales)
                all_articulos.append(aux[0])
                continue


            
            #Obtenemos de la BD el artículo al que modifica
            texto_vigente, metadata=BD.get_article(ley, num_art)
            if texto_vigente is None:
                aux=[{
                    "cuerpo":texto_modificacion,
                    "titulo": articulo["titulo"],
                    "id":articulo["id"]
                }]
                
                utils.addMetadata(aux, [], [], datos_globales)
                all_articulos.append(aux[0])
                continue


            
            #Si los textos son demasiado grandes para que lo soporte el llm no se pasa
            if (len(texto_modificacion)+len(texto_vigente)>20000):
                aux=[{
                    "cuerpo":texto_modificacion,
                    "titulo": articulo["titulo"],
                    "id":articulo["id"]
                }]
                
                utils.addMetadata(aux, [], [], datos_globales)
                all_articulos.append(aux[0])

                continue
            
            #Generamos una consolidación del texto
            articulo_final=unifacte_norma(texto_vigente, texto_modificacion)


            
            #Como se trata de una disposición o artículo, dejamos el diccionario con los datos mínimos
            articulo_unificado=metadata.copy()
            articulo_unificado["cuerpo"]=articulo_final
            articulo_unificado["id"]=articulo["id"]
            all_articulos.append(articulo_unificado)

            num_art_unificate+=1
            
            
            #Ponemos el artículo anterior como modificado
            BD.changeMetadata([{"numero_norma":ley},{"num_articulo":num_art}], "estado", "modificado")

    return all_articulos, num_art_unificate
            