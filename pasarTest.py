"""
import src.tests.ragas.test as t
import src.rag.rag as rag

prueba1=['BOE-A-1995-25444', 'BOE-A-2003-21538', 'BOE-A-2010-9953', 'BOE-A-2015-3439']
prueba2 = [
    'BOE-A-1978-31229','BOE-A-1882-6036', 'BOE-A-1889-4763',  
    'BOE-A-1985-12666',  'BOE-A-1992-26318',  'BOE-A-1995-24292',  
    'BOE-A-1995-25444', 'BOE-A-1995-15781','BOE-A-1996-8930',
    'BOE-A-2000-323',   'BOE-A-2003-21538','BOE-A-2010-9953',
    'BOE-A-2015-3439'
]

prueba3 = [
    'BOE-A-1978-31229','BOE-A-1882-6036','BOE-A-1889-4763',
    'BOE-A-1985-12666','BOE-A-1986-6859','BOE-A-1992-26318',
    'BOE-A-1995-15781','BOE-A-1995-24292',
    'BOE-A-1995-25444','BOE-A-1996-8930','BOE-A-1998-8789',
    'BOE-A-2000-323','BOE-A-2000-544','BOE-A-2002-13758',
    'BOE-A-2003-21538','BOE-A-2004-21760','BOE-A-2007-22439',
    'BOE-A-2010-9953','BOE-A-2011-4117','BOE-A-2011-17887',
    'BOE-A-2012-9110','BOE-A-2013-12913','BOE-A-2015-3439'
]


#Inicializamos el rag
maquina1 = rag.rag("default", 0.5)
maquina2 = rag.rag("default", 0.6)
maquina3 = rag.rag("default", 0.7)
maquina4 = rag.rag("default", 0.8)
maquina5 = rag.rag("default", 0.9)

t.make_test(maquina1, "Threshold=0.5", prueba2, 1, 1)
t.make_test(maquina2, "Threshold=0.6", prueba2, 1, 1)
t.make_test(maquina3, "Threshold=0.7", prueba2, 1, 1)
t.make_test(maquina4, "Threshold=0.8", prueba2, 1, 1)
t.make_test(maquina4, "Threshold=0.9", prueba2, 1, 1)
"""


PRUEBA=['BOE-A-1889-4763' , 'BOE-A-1981-16216', 'BOE-A-1981-11198', 'BOE-A-1983-28123',
        'BOE-A-1987-25627', 'BOE-A-1990-25089', 'BOE-A-1999-21569', 'BOE-A-2000-323',
        'BOE-A-2005-11864', 'BOE-A-2005-20662', 'BOE-A-2011-13241', 'BOE-A-2015-3439'
       ]
AHH=['BOE-A-2015-3439']
import src.tests.ragas.ragasTests as test
import src.rag.rag as rag

"""
#Normal
maquina=rag.rag(False, False, 0.0)
maquina.purgarBasesDatos()
aux=maquina.newListBoesDocuments(PRUEBA)

if aux:
    test.ejecutarTest(maquina, "normal", "data/dataset1", "data/ragas_dataset_100.jsonl")


#Eliminar derrogados
maquina=rag.rag(True, False, 0.0)
maquina.purgarBasesDatos()
aux=maquina.newListBoesDocuments(PRUEBA)

if aux:
    test.ejecutarTest(maquina, "delete", "data/dataset1", "data/ragas_dataset_100.jsonl")

#Unificar apartados
maquina=rag.rag(False, True, 0.0)
maquina.purgarBasesDatos()
aux=maquina.newListBoesDocuments(PRUEBA)

if aux:
    test.ejecutarTest(maquina, "unificate", "data/dataset1", "data/ragas_dataset_100.jsonl")
"""

#Unificar apartados
maquina=rag.rag(False, False, 0.2)
maquina.purgarBasesDatos()
aux=maquina.newListBoesDocuments(PRUEBA)

if aux:
    test.ejecutarTest(maquina, "0.2", "data/threshold", "data/ragas_dataset_100.jsonl")

    maquina.changeMinThreshold(0.4)
    test.ejecutarTest(maquina, "0.4", "data/threshold", "data/ragas_dataset_100.jsonl")

    maquina.changeMinThreshold(0.6)
    test.ejecutarTest(maquina, "0.6", "data/threshold", "data/ragas_dataset_100.jsonl")

    maquina.changeMinThreshold(0.8)
    test.ejecutarTest(maquina, "0.8", "data/threshold", "data/ragas_dataset_100.jsonl")


test.make_grafica("data/threshold", "Distintos threshold", "Distintas funcionalidades")
