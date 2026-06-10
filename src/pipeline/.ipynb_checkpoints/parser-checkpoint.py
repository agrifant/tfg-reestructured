from lxml import etree
from . import utils as utils
from enum import Enum
from io import BytesIO
import src.extractArticulo as ext

class tipoTexto(Enum):
    """
    Clase que guarda 3 diferentes tipos:
        - Articulo
        - Extra
        - None
    """
    ARTICULO = "articulo"
    EXTRA = "extra"
    NONE = "NONE"


class DocumentoBOE:
    """
    Clase que se encarga de guardar los diferentes objetos(articulo, texto extra)
    """
    def __init__(self) -> None:
        """
        Constructor de la clase
        """
        #Variables que contienen toda la información
        self.list_articulos = []
        self.list_extra = []

        #Variables internas de procesamiento
        self.current_articulo = None
        self.current_extra = None
        self.is_texto=tipoTexto.NONE

    def cambioTipoTexto(self, nuevo:tipoTexto) -> None:
        """
        Función que se encarga de cambiar de contexto de forma segura, cambiando por ejemplo de texto extra a artículo.

        Args:
            nuevo (tipoTexto): El nuevo tipo que se va a tratar
        """
        #Guardamos artículo o extra cuando se cambia el tipo
        if self.is_texto == tipoTexto.ARTICULO:
            self.current_articulo["cuerpo"]=self.current_articulo["cuerpo"].strip()
            self.list_articulos.append(self.current_articulo)
            self.current_articulo=None

        elif self.is_texto == tipoTexto.EXTRA:
            self.current_extra["cuerpo"]=self.current_extra["cuerpo"].strip()
            self.list_extra.append(self.current_extra)
            self.current_extra=None

        self.is_texto=nuevo  

def obtenerArticulos(boe_XML: BytesIO, boe: str)-> tuple[list[dict], list[dict], list[dict]]:
    """
    Extrae del XML del BOE los artículos, disposiciones y otros textos relevantes.

    Args:
    boe_XML (BytesIO): Archivo XML del BOE cargado en memoria.
    boe (str): Identificador del documento BOE (por ejemplo, 'BOE-A-2024-12345').

    Returns:
    tuple: Una tupla con:
    - articulos (list[dict]): Lista de diccionarios de artículos.
    - disposiciones (list[dict]): Lista de diccionarios de disposiciones
    - texto_extra (list[dict]): Lista con diccionario de datos que no se supo identificar.
    """
    #Creamos el objeto BOE
    documento = DocumentoBOE()

    # Diferentes variables
    libro_num=None
    libro_tit=None
    apartado_num=None
    apartado_tit=None
    capitulo_num=None
    capitulo_tit=None
    seccion=None
    num_texto_extra=0
    
    # articulo_compuesto=["parrafo", "parrafo_2", "cita_con_pleca", "cita"]
    texto_extra_no_compuesto=["articulo", "titulo_num", "anexo_num"]

    #variables a no tener en cuenta ni guardar
    noTenerEncuenta=["firma_rey", "firma_ministro"]
    #Archivo a leer
    tree = etree.parse(boe_XML)
    
    #Eliminamos algunas palabras que no necesitamos
    tree=utils.limpiarPalabras(tree)
    
    root = tree.getroot()

    texto_completo = root.find("texto")

    #Nos quedamos con las lineas que sólo tienen <p>
    lineas = utils.extraer_texto_completo(texto_completo)

    #Sobre cada linea <p>
    for elem, atributo, texto in lineas:
        bq = utils.is_in_blockquote(elem)
        texto=utils.normalizar_texto(texto)
        # Comienza un nuevo artículo
        if atributo == "articulo" and bq==False:
            documento.cambioTipoTexto(tipoTexto.ARTICULO)
            #Estructura mínima
            documento.current_articulo = {
                "titulo_articulo": texto,
                "cuerpo": ""
            }

            utils.adjuntarDiccionarioCompuesto(libro_num, libro_tit, "titulo", documento.current_articulo)
            utils.adjuntarDiccionarioCompuesto(apartado_num, apartado_tit, "apartado", documento.current_articulo)
            utils.adjuntarDiccionarioCompuesto(capitulo_num, capitulo_tit, "capitulo", documento.current_articulo)
            utils.adjuntarDiccionarioSimple(seccion, "seccion", documento.current_articulo)
        
        
        elif atributo == "libro_num":
            libro_num=texto
            libro_tit=None
            capitulo_num=None
            capitulo_tit=None
            seccion=None
            documento.cambioTipoTexto(tipoTexto.NONE)
        
        elif atributo == "libro_tit":
            libro_tit=texto
            capitulo_num=None
            capitulo_tit=None
            seccion=None
            documento.cambioTipoTexto(tipoTexto.NONE)

        elif atributo == "titulo_num":
            apartado_num=texto
            #Si comienza un nuevo apartado, capitulo y sección puede no tener el nuevo apartado
            capitulo_num=None
            capitulo_tit=None
            seccion=None
            documento.cambioTipoTexto(tipoTexto.NONE)

        elif atributo == "titulo_tit":
            apartado_tit=texto
            documento.cambioTipoTexto(tipoTexto.NONE)

        elif atributo == "capitulo_num":
            capitulo_num=texto
            #Si comienza un nuevo capitulo, puede no tener sección el nuevo capitulo
            seccion=None
            documento.cambioTipoTexto(tipoTexto.NONE)

        elif atributo == "capitulo_tit":
            capitulo_tit=texto
            documento.cambioTipoTexto(tipoTexto.NONE)

        elif atributo == "seccion":
            seccion = texto
            documento.cambioTipoTexto(tipoTexto.NONE)

        elif atributo == "anexo_num":
            capitulo_num=texto
            capitulo_tit=None
            seccion=None
            documento.cambioTipoTexto(tipoTexto.NONE)
        
        elif atributo =="anexo_tit":
            capitulo_tit=texto
            seccion=None
            documento.cambioTipoTexto(tipoTexto.NONE)
        
        elif atributo in noTenerEncuenta:
            documento.cambioTipoTexto(tipoTexto.NONE)
        
        #Sigue a un artículo
        elif documento.is_texto==tipoTexto.ARTICULO:
            documento.current_articulo["cuerpo"]+= "\n" + texto

        #Sigue a un texto extra
        elif documento.is_texto==tipoTexto.EXTRA:
            #Ya no es texto extra
            if atributo in texto_extra_no_compuesto:
                documento.cambioTipoTexto(tipoTexto.NONE)
            else:
                documento.current_extra["cuerpo"]+= "\n" + texto
        
        # Comienza un nuevo texto extra nuevo
        else:
            num_texto_extra+=1
            #Estructura mínima
            documento.current_extra = {
                "id": f"{boe}_txe_{num_texto_extra}",
                "cuerpo": texto
            }

            utils.adjuntarDiccionarioCompuesto(libro_num, libro_tit, "titulo", documento.current_extra)
            utils.adjuntarDiccionarioCompuesto(apartado_num, apartado_tit, "apartado", documento.current_extra)
            utils.adjuntarDiccionarioCompuesto(capitulo_num, capitulo_tit, "capitulo", documento.current_extra)
            utils.adjuntarDiccionarioSimple(seccion, "seccion", documento.current_extra)
            documento.cambioTipoTexto(tipoTexto.EXTRA)
            
    # Guardar el último artículo válido
    if documento.is_texto==tipoTexto.ARTICULO:
        documento.current_articulo["cuerpo"]=documento.current_articulo["cuerpo"].strip()
        documento.list_articulos.append(documento.current_articulo)
    
    # Guardar el último texto extra válido
    if documento.is_texto == tipoTexto.EXTRA and documento.current_extra:
        documento.current_extra["cuerpo"] = documento.current_extra["cuerpo"].strip()
        documento.list_extra.append(documento.current_extra)
        
    #Separamos los artículos y las disposiciones
    articulos, disposiciones = separarArticulosDisposiciones(documento.list_articulos, boe)

    return articulos, disposiciones,  documento.list_extra

def separarArticulosDisposiciones(lista_datos: list[dict], boe: str) -> tuple[list[dict], list[dict]]:
    """
    Diferencia sobre una lista de diccionarios cuales son artículos y cuales disposiciones

    Args:
    lista_datos (list[dict]): Lista de diccionario con las disposiciones y artículos.
    boe (str): Identificador del documento BOE (por ejemplo, 'BOE-A-2024-12345').

    Returns:
    tuple: Una tupla con:
    - articulos (list[dict]): Lista de diccionarios de artículos.
    - disposiciones (list[dict]): Lista de diccionarios de disposiciones
    """
    disposiciones = []
    articulos = []
    num_art=0
    num_disp=0
    for elemento in lista_datos:
        # Comprobamos que sea una disposicion
        if isDisposicion(elemento):
            num_disp+=1
            id=f"{boe}_disp_{num_disp}"
            utils.adjuntarDiccionarioSimple(id, "id", elemento)
            disposiciones.append(elemento)
        # Comprovamos que sea un artículo
        else:
            num_art+=1
            id=f"{boe}_art_{num_art}"
            utils.adjuntarDiccionarioSimple(id, "id", elemento)
            articulos.append(elemento)

    return articulos, disposiciones

def isDisposicion(diccionario: dict) -> bool:
    """
    Determina si un diccionario corresponde a una disposición del BOE.

    Args:
        diccionario (dict): Diccionario que contiene los datos de un elemento del BOE.

    Returns:
        bool: True si el elemento es una disposición, False en caso contrario.
    """
    titulo = diccionario.get("titulo_articulo", "").lower()
    return titulo.startswith("disposición") or titulo.startswith("[precepto]")

def isArticulo(diccionario: dict) -> bool:
    """
    Determina si un diccionario corresponde a un artículo del BOE.

    Args:
        diccionario (dict): Diccionario que contiene los datos de un elemento del BOE.

    Returns:
        bool: True si el elemento es un artículo, False en caso contrario.
    """
    titulo = diccionario.get("titulo_articulo", "").lower()
    return titulo.startswith("artículo")

def obtenerDatosGlobales(boe_XML: BytesIO)->tuple[dict, dict]:
    """
    Obtiene los datos globales de un documento del BOE.

    Args:
        boe_XML (BytesIO): Archivo XML del BOE cargado en memoria.

    Returns:
        tuple[dict, dict]:
            datos_globales: Diccionario con los metadatos relevantes del documento (id, título, tipo de norma, fechas, etc.).
            materias: Diccionario con las materias asociadas al documento.
    """
    #Archivo a leer
    tree = etree.parse(boe_XML)
    root = tree.getroot()

    #En la sección <metadatos> se encuentra la mayoría de los metadatos
    metadatos = root.find("metadatos")

    # En <analisis> se encunetra tanto <materias> como <notas>
    # Siendo buenos datos extra para recabar
    analisis = root.find("analisis")
    materias = analisis.find("materias") if analisis is not None else None
    notas = analisis.find("notas") if analisis is not None else None


    fecha_publicacion=utils.normalizarFecha(utils.get_unique_text(metadatos, "fecha_publicacion"))
    fecha_disposicion=utils.normalizarFecha(utils.get_unique_text(metadatos, "fecha_disposicion"))

    datos_globales= {  
        # Identificador único para poder encontrar el documento de la norma (Ej: BOE-A-1978-31229)
        "id_boe": utils.get_unique_text(metadatos, "identificador"),

        # Indica que peso tiene la ley sobre otras (si es ley, decreto, ...)
        "tipo_norma": utils.get_unique_text(metadatos, "rango"),
        
        # Indica el número oficial por el que se referencia a la norma en otras normas
        "numero_norma": utils.get_unique_text(metadatos, "numero_oficial") ,

        # EL título que tiene la norma
        "titulo": utils.get_unique_text(metadatos, "titulo"),

        # Url para ver la norma en pdf
        "url_pdf": "https://www.boe.es" + utils.get_unique_text(metadatos, "url_pdf") ,

        # Que departamento escribió la ley
        "departamento": utils.get_unique_text(metadatos, "departamento"),

        # Que origen legislativo tiene la ley
        "origen_legislativo":utils.get_unique_text(metadatos, "origen_legislativo"),

        # El día en el que la norma fue publicada
        "fecha_publicacion": fecha_publicacion,

        # La fecha en la que la disposición fue aprobada
        "fecha_disposicion": fecha_disposicion
    }
    
    #Metadatos que puede tener opcionalmente
    # Notas que tiene la norma
    texto_notas= utils.get_multiple_text(notas, "nota")

    # Apartado donde se indican las competencias relacionadas con la norma
    texto_materias= utils.get_multiple_text(materias, "materia")
    
    utils.adjuntarDiccionarioSimple(texto_notas, "notas", datos_globales)
    
    return datos_globales, texto_materias

def getDatos(boe_file, documento):
    articulos, disposiciones, texto_extra = obtenerArticulos(boe_file, documento)
    datos_globales, materias = obtenerDatosGlobales(boe_file)

    #Tratamos los artículos para guardar el específico
    for articulo in articulos:
        num=ext.extract_articulo(articulo["titulo_articulo"])
        if num is not None:
            articulo["num_articulo"]=num
            
        articulo["estado"]="vigente"
    
    return articulos, disposiciones, texto_extra, datos_globales, materias