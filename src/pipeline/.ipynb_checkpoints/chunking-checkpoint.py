import re
import bisect

# Variables globales por la que separamos el texto
saltos = (r"\n", True)
puntos = (r"\.", True)


def chunking(texto: str, out: list, MAX_TOKENS: int, MIN_TOKENS: int, OVERLAP: float, delimitador: tuple =saltos, stop: int =0)-> None:    
    """
    Divide un texto en chunks respetando límites de tokens.

    Estrategia de chunking (en orden):

    1. Intentar dividir el texto por saltos de línea (`\n`).
    2. Si aún supera el tamaño máximo, dividir por puntos (`.`).
    3. Si sigue siendo demasiado grande, aplicar división por
    ventana de tokens con solapamiento (overlap).

    El objetivo es generar chunks de tamaño cercano a MAX_TOKENS
    manteniendo el máximo contexto semántico posible.

    Nota:
        El último chunk puede superar MAX_TOKENS si su tamaño es
        menor que MIN_TOKENS y se fusiona con el anterior.

    Args:
        texto (str):
            Texto que se va a dividir.

        out (list):
            Lista donde se almacenan los chunks generados.

        MAX_TOKENS (int):
            Número máximo de tokens por chunk.

        MIN_TOKENS (int):
            Tamaño mínimo permitido para un chunk.

        OVERLAP (float):
            Porcentaje de solapamiento entre chunks cuando se usa
            la división por ventana (valor entre 0 y 1).

        delimitador (tuple):
            Expresión regular usada para dividir el texto en esta fase.

        stop (int):
            Controla el nivel de recursión del algoritmo:
                1 → dividir por saltos de línea
                2 → división por ventana con overlap

    Returns:
        None

    Resultado:
        Los chunks generados se almacenan en la lista `out`.
    """
    #Dividimos el texto en diferentes párrafos
    paragraphs= split_keep_delimiter(texto, delimitador)
    
    chunk=""
    tokens_chunk=0

    #Entre todos los párrafos que tenemos
    for p in paragraphs:
        p_tokens = len(p.split())
        overlap = int(MAX_TOKENS * OVERLAP)
        
        # Si aún no se alcanzó el máximo con el chunk actual y se puede añadir
        if(tokens_chunk + p_tokens) <= MAX_TOKENS:
            chunk+=p
            tokens_chunk+=p_tokens
        else:
            # Si no está vacío se guarda el chunk que tenemos escrito
            if chunk.strip():
                out.append(chunk)
                tokens_chunk=0
                chunk=""
            # Si el chunk no sobrepasa los límites de tamaño se añade al chunk
            if p_tokens <= MAX_TOKENS:
                chunk+=p
                tokens_chunk+=p_tokens
            else:
                if stop==0:
                    chunking(p, out, MAX_TOKENS, MIN_TOKENS, OVERLAP, puntos, stop+1)
                else:
                    sub_tokens = p.split()
                    
                    step = MAX_TOKENS - overlap

                    for i in range(0, len(sub_tokens), step):
                        out.append(" ".join(sub_tokens[i:i+MAX_TOKENS]))

                    if len(out[-1].split())<MIN_TOKENS:
                        ultimo_limpio = out[-1].split()[overlap:]
                        out[-2] = " ".join(out[-2].split() + ultimo_limpio)
                        out.pop()

                    chunk=""
                    tokens_chunk=0
    
    # Añadimos el ultimo chunk
    if chunk.strip():
        if len(chunk.split()) >= MIN_TOKENS:
            out.append(chunk)
        else:
            # Si el chunk es demasiado pequeño, intentar unirlo con el anterior
            if out:
                out[-1] = " ".join(out[-1].split() + chunk.split())
            else:
                # No hay chunk previo, añadir tal cual
                out.append(chunk)    

def split_keep_delimiter(texto: str, delimitador: tuple)-> list[str]:
    """
        Divide un texto usando un patrón de delimitador, conservando el delimitador en los fragmentos.

        La función permite controlar si el delimitador queda al **final** o al **inicio** del fragmento
        mediante un flag booleano.

        Args:
            texto (str):
                El texto que se va a dividir.
            
            delimitador (tuple):
                Tupla con la forma (patrón_regex, keep_with_previous)
                - patrón_regex (str): expresión regular que define el delimitador.
                - keep_with_previous (bool):
                    True  → el delimitador se mantiene al **final** del fragmento anterior.
                    False → el delimitador se mantiene al **inicio** del fragmento siguiente.

        Returns:
            list[str]:
                Lista de fragmentos de texto resultantes de la división, incluyendo el delimitador
                según la configuración.
    """
    if delimitador[1] ==True:
        pattern = r'(?<=' + delimitador[0] + r')'
    else:
        pattern = r'(?=' + delimitador[0] + r')'
    return re.split(pattern, texto)

def chunkear_diccionario(diccionario: dict, label:str , cont,  MAX_TOKENS: int =250, MIN_TOKENS: int =100, OVERLAP: int =0.2)-> list[dict]:
    """
        Divide el texto de un artículo en chunks respetando límites de tokens
        y devuelve una lista de diccionarios con los chunks generados.

        Cada chunk contiene:
            - id    : combinación del id original + número de chunk
            - cuerpo: texto del chunk
            - parte  : indicador de la posición del chunk (e.g., "Parte 1 de 3")

        Nota:
            - El tamaño de cada chunk está limitado por MAX_TOKENS y MIN_TOKENS,
            pero el último chunk puede sobrepasar MAX_TOKENS si es necesario para
            respetar MIN_TOKENS.
            - Los chunks se almacenan en orden de aparición en el texto original.

        Args:
            diccionario (dict): Diccionario que contiene al menos:
                - 'id'   : identificador único del artículo
                - label  : campo de texto que se desea chunkear
            label (str): Nombre del campo de texto que se va a chunkear.
            MAX_TOKENS (int, opcional): Número máximo de tokens por chunk. Default es 250.
            MIN_TOKENS (int, opcional): Número mínimo de tokens por chunk. Default es 100.
            OVERLAP (float, opcional): Porcentaje de solapamiento entre chunks (0-1). Default es 0.2.

        Returns:
            list[dict]: Lista de diccionarios, cada uno representando un chunk con la siguiente estructura:
                {
                    "id": "id_original.numero_chunk",
                    "cuerpo": "texto del chunk",
                    "parte": "Parte X de Y"
                }
    """
    diccionario_chunked=[]
    out=[]

    
    chunking(diccionario[label], out, MAX_TOKENS, MIN_TOKENS, OVERLAP)
    for i in range(len(out)):
        aux= diccionario.copy()
        aux["id"]=f"{diccionario['id']}.{cont}.{i+1}"
        aux["cuerpo"]= out[i]
        aux["cuerpo_integro"]= out[i]
        aux["parte"]=f"{i+1}"
            
        diccionario_chunked.append(aux)
    
    return diccionario_chunked

def make_chunking(diccionario):
    aux=[]

    cont=1
    for dic in diccionario:
        aux.extend(chunkear_diccionario(dic, "cuerpo", cont))
        cont+=1

    return aux

