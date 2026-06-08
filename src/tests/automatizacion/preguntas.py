import json
import src.rag.rag as rag
# python3 -m src.tests.automatizacion.preguntas


def CalcularPrecisiónRetrieval(maquina):
    #Cargamos las preguntas del json
    with open("src/tests/automatizacion/preguntas.json", "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)

    #Calculamos la nota
    nota=0
    for dato in datos:
        ids=maquina.preguntarTest(dato["question"])
        print(ids)
        if dato["answer"] in ids:
            nota+=1

    return (nota/len(datos))

def test():
    maquina=rag.rag()
    #Eliminamos todos los datos de la bd.
    print("Purgando base de datos")
    maquina.purgarBasesDatos()

    #Añadimos los ficheros necesarios
    print("Añadimos el fichero que queremos:")
    maquina.newBoeDocument("BOE-A-2015-3439")

    #Hacemos la pregunta
    response=maquina.preguntar("¿Puede existir responsabilidad penal de una persona jurídica aunque no se identifique a la persona física responsable?")

    print(response)

    input()
    response=maquina.preguntar("¿Qué circunstancias atenuantes de la responsabilidad penal de las personas jurídicas recoge el artículo 31 quater?")
    print(response)
    #Metemos nuevos ficheros

    #Calculamos la nota

test()