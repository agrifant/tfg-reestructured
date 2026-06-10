import re

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
    
def main_unificate(articulos):
    for articulo in articulos:
        titulo=articulo["titulo_articulo"]
        texto=articulo["cuerpo"]
        texto_total = (titulo + " " + texto).lower()
        #Comprobamos si se trata de un artículo que modifica a otra ley
        if esModificativo(texto_total):
            intro=extraerIntro(texto_total)
            articulos=extraerSubarticulos(texto_total)
            print(intro)
            print("\n")
            for i in articulos:
                print(i)
                print("\n")