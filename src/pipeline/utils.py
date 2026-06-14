from datetime import datetime
import re
import unicodedata
import src.extractArticulo as ext

palabras=["[ignorar]", "[cabezera]", "[encabezado]"]

def extraer_ley(texto: str):
    patron = r"\b\d+/\d{4}\b"
    match = re.search(patron, texto)
    return match.group(0) if match else None

def normalizarFecha(fecha):
    return datetime.strptime(fecha, "%Y%m%d").strftime("%Y-%m-%d")

def normalizar_texto(texto: str) -> str:
    # 1. Normalización Unicode base (acentos, compatibilidad, etc.)
    texto = unicodedata.normalize("NFKC", texto)

    # 2. Convertir NBSP (espacio duro) a espacio normal
    texto = texto.replace("\xa0", " ")

    # 3. Si vienen escapes literales tipo "\\n" o "\\xa0"
    texto = texto.replace("\\n", "\n").replace("\\xa0", " ")

    return texto.strip()

def limpiarPalabras(tree):
    #Función que elimina los [ignorar] y [cabezera] de todo el docuemnto
    for elem in tree.iter():
        if elem.text:
            for palabra in palabras:
                elem.text = elem.text.replace(palabra, "")
        if elem.tail:
            for palabra in palabras:
                elem.tail = elem.tail.replace(palabra, "")
    return tree

def is_in_blockquote(elem):
    parent = elem.getparent()

    while parent is not None:
        if parent.tag in {"blockquote", "cita"}:
            return True
        parent = parent.getparent()

    return False

def extraer_texto_completo(texto_completo):
    lineas = []

    for elem in texto_completo.findall(".//p"):
        texto = ''.join(elem.itertext()).strip()

        if texto:
            atributo = elem.get("class")
            lineas.append((elem, atributo, texto))

    return lineas

def get_unique_text(datos, identificador):
    # Función que te devuelve el texto encontrado en:
    # <datos>
    #     <identificador> texto que devuelve </identificador>
    # </datos>
    nodo = datos.find(identificador)
    return nodo.text.strip() if nodo is not None and nodo.text else "None"

def get_multiple_text(datos, identificador):
    # Función que te devuelve una serire de textos en formato vector dentro de:
    # <datos>
    #     <identificador> texto 1 que devuelve dentro de un vector </identificador>
    #     <identificador> texto 2 que devuelve dentro de un vector </identificador>
    # </datos>
    if datos is None:
        return None

    lineas = datos.findall(identificador)
    resultados = []
    for nodo in lineas:
        if nodo.text and nodo.text.strip():
            resultados.append(nodo.text.strip())
    return resultados if resultados else None

def adjuntarDiccionarioCompuesto(var1, var2, clave, diccionario):
    if var1 and var2:
        diccionario[clave] = f"{var1}: {var2}"

def adjuntarDiccionarioSimple(var1, clave, diccionario):
    if var1:
        diccionario[clave] = f"{var1}"

def crear_diccionarios(elementos):
    resultado = []
    
    for texto in elementos:
        materia_id = texto.lower()
        dic = {
            "id": materia_id,
        }
        resultado.append(dic)
    
    return resultado

def separarTexto(dict):
    texto=dict["cuerpo"]
    texto=separarTextoCoincidenciaTitulo(texto)

    nuevos=[]
    for i in range(len(texto)):
        titulo_nuevo, texto_nuevo=separarTitulo(texto[i])
        aux={
            "id": f"{dict['id']}.{i+1}",
            "titulo_articulo": titulo_nuevo,
            "cuerpo": texto_nuevo
        }
        nuevos.append(aux)

    return nuevos

def separarTextoCoincidenciaTitulo(texto):
    coincidencias = [
        m.start()
        for m in re.finditer(
            r"(?i)se\s+(modifica|introduce|añade).*?art[ií]culo\s",
            texto
        )
    ]

    if not coincidencias:
        return [texto]

    chunks = []
    last = 0

    for c in coincidencias:
        # buscar salto de línea anterior al match
        cut = texto.rfind("\n", 0, c)
        if cut == -1:
            cut = 0

        chunks.append(texto[last:cut].strip())
        last = cut

    chunks.append(texto[last:].strip())

    return [c for c in chunks if c]

def separarTitulo(texto):
    partes = texto.split("\n", 1)

    titulo = partes[0]
    argumento = partes[1] if len(partes) > 1 else ""

    return titulo, argumento

def enriquecerTextos(data: dict, datos_globales):
    titulo_ley = datos_globales.get("titulo_norma", "")

    titulo_ley = descriptor_simple(titulo_ley)
    articulo = data.get("titulo", "")
    texto = data.get("cuerpo", "")

    
    partes = [
        f"{titulo_ley} \n" if titulo_ley else "",
        articulo,
        texto
    ]

    embedding_text = "\n".join([p for p in partes if p])

    return embedding_text

def makeEnriquecerTextos(diccionario, datos_globales):
    for dic in diccionario:
        dic["cuerpo"] = enriquecerTextos(
            dic,
            datos_globales
        )
    return diccionario

def descriptor_simple(texto):
    corte_punto = texto.split(".")[0]
    corte_coma = texto.split(",")[0]
    frase = corte_punto if len(corte_punto) < len(corte_coma) else corte_coma
    
    palabras = frase.lower().split()
    return " ".join(palabras)

def addMetadata(articulos, disposiciones, textos_extras, datos_globales):
    #Añadimos la metadata de estado a todos. estado="vigente" y de los datos globales
    for disposicion in disposiciones:
        #Estado
        disposicion["estado"]="vigente"

        #Datos globales
        disposicion["id_boe"]=datos_globales["id_boe"]
        disposicion["url_pdf"]=datos_globales["url_pdf"]
        disposicion["tipo_norma"]=datos_globales["tipo_norma"]
        disposicion["fecha_disposicion"]=datos_globales["fecha_disposicion"]
        disposicion["titulo_norma"]=datos_globales["titulo_norma"]
        disposicion["numero_norma"]=datos_globales["numero_norma"]
        disposicion["fecha_publicacion"]=datos_globales["fecha_publicacion"]

    for texto in textos_extras:
        #Estado
        texto["estado"]="vigente"

        #Datos globales
        texto["id_boe"]=datos_globales["id_boe"]
        texto["url_pdf"]=datos_globales["url_pdf"]
        texto["tipo_norma"]=datos_globales["tipo_norma"]
        texto["fecha_disposicion"]=datos_globales["fecha_disposicion"]
        texto["titulo_norma"]=datos_globales["titulo_norma"]
        texto["numero_norma"]=datos_globales["numero_norma"]
        texto["fecha_publicacion"]=datos_globales["fecha_publicacion"]

    
    for articulo in articulos:
        #Estado
        articulo["estado"]="vigente"

        #Datos globales
        articulo["id_boe"]=datos_globales["id_boe"]
        articulo["url_pdf"]=datos_globales["url_pdf"]
        articulo["tipo_norma"]=datos_globales["tipo_norma"]
        articulo["fecha_disposicion"]=datos_globales["fecha_disposicion"]
        articulo["titulo_norma"]=datos_globales["titulo_norma"]
        articulo["numero_norma"]=datos_globales["numero_norma"]
        articulo["fecha_publicacion"]=datos_globales["fecha_publicacion"]
        
        #Para los artículos, pueden tener un la metadata num_articulo que es opcional
        num=ext.extract_articulo(articulo["titulo"])
        if num is not None:
            articulo["num_articulo"]=num

