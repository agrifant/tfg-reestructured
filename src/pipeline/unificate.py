import re
import src.pipeline.utils as utils
import src.extractArticulo as ext
import src.llm.callToLLM as llm

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

    while True:
        return llm.call_ollama(messages)
                
def esModificativo(texto):
    patrones = [
        "modifica",
        "modificación",
        "se modifica"
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
def extraerSubarticulos(texto):
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
    
def main_unificate(BD, articulos):
    all_articulos=[]
    
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
            texto_modificacion=subarticulo["texto"]
            #Extraemos el número del artículo al que modifica
            num_art=ext.extract_articulo(texto_modificacion)
            if num_art is None:
                aux={}
                aux["cuerpo"]=texto_modificacion
                aux["titulo"]=articulo["titulo"]
                aux["id"]=articulo["id"]
                aux["estado"]="vigente"
                all_articulos.append(aux)
                continue


            
            #Obtenemos de la BD el artículo al que modifica
            texto_vigente, metadata=BD.get_article(ley, num_art)
            if texto_vigente is None:
                aux={}
                aux["cuerpo"]=texto_modificacion
                aux["titulo"]=articulo["titulo"]
                aux["id"]=articulo["id"]
                aux["estado"]="vigente"
                all_articulos.append(aux)
                continue


            
            #Generamos una consolidación del texto
            articulo_final=unifacte_norma(texto_vigente, texto_modificacion)


            
            #Como se trata de una disposición o artículo, dejamos el diccionario con los datos mínimos
            articulo_unificado={}
            articulo_unificado["cuerpo"]=articulo_final
            articulo_unificado["id"]=articulo["id"]
            
            articulo_unificado["titulo"]=metadata["titulo"]
            articulo_unificado["titulo_norma"]=metadata["titulo_norma"]
            articulo_unificado["numero_norma"]=metadata["numero_norma"]
            articulo_unificado["tipo_norma"]=metadata["tipo_norma"]
            articulo_unificado["num_articulo"]=metadata["num_articulo"]
            articulo_unificado["estado"]="vigente"
            all_articulos.append(articulo_unificado)
            
            
            #Ponemos el artículo anterior como modificado
            BD.changeMetadata([{"numero_norma":ley},{"num_articulo":num_art}], "estado", "modificado")

    return all_articulos
            