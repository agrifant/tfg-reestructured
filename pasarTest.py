import src.tests.ragas.ragasTests as test
import src.rag.rag as rag

with open("identificadores.txt", "r", encoding="utf-8") as f:
    PRUEBA = f.read().splitlines()



#Normal top_k=5
maquina=rag.rag(False, False, 0.0)
maquina.purgarBasesDatos()
maquina.change_top_k(5)
aux=maquina.newListBoesDocuments(PRUEBA)

if aux:
    test.ejecutarTest(maquina, "normal", "data/mecanismoBase/top_6", "data/ragas_dataset_100.jsonl")
else:
    print("Abortado")

#Normal top_k=10
maquina=rag.rag(False, False, 0.0)
maquina.purgarBasesDatos()
maquina.change_top_k(5)
aux=maquina.newListBoesDocuments(PRUEBA)

if aux:
    test.ejecutarTest(maquina, "normal", "data/mecanismoBase/top_6", "data/ragas_dataset_100.jsonl")
else:
    print("Abortado")

#Normal top_k=20
maquina=rag.rag(False, False, 0.0)
maquina.purgarBasesDatos()
maquina.change_top_k(5)
aux=maquina.newListBoesDocuments(PRUEBA)

if aux:
    test.ejecutarTest(maquina, "normal", "data/mecanismoBase/top_6", "data/ragas_dataset_100.jsonl")
else:
    print("Abortado")


#Normal top_k=50
maquina=rag.rag(False, False, 0.0)
maquina.purgarBasesDatos()
maquina.change_top_k(5)
aux=maquina.newListBoesDocuments(PRUEBA)

if aux:
    test.ejecutarTest(maquina, "normal", "data/mecanismoBase/top_6", "data/ragas_dataset_100.jsonl")
else:
    print("Abortado")

"""
#Eliminar derrogados
maquina=rag.rag(True, False, 0.0)
maquina.purgarBasesDatos()
aux=maquina.newListBoesDocuments(PRUEBA)

if aux:
    test.ejecutarTest(maquina, "delete", "data/delete/top_5", "data/ragas_dataset_100.jsonl")

#Unificar apartados
maquina=rag.rag(False, True, 0.0)
maquina.purgarBasesDatos()
aux=maquina.newListBoesDocuments(PRUEBA)

if aux:
    test.ejecutarTest(maquina, "unificate", "data/unificate/top_5", "data/ragas_dataset_100.jsonl")


#Thresholds
maquina=rag.rag(False, False, 0.0)
maquina.purgarBasesDatos()
aux=maquina.newListBoesDocuments(PRUEBA)


if aux:
    test.ejecutarTest(maquina, "0.0", "data/threshold/top_5/0_0", "data/ragas_dataset_100.jsonl")

    maquina.changeMinThreshold(0.1)
    test.ejecutarTest(maquina, "0.1", "data/threshold/top_5/0_1", "data/ragas_dataset_100.jsonl")
    
    maquina.changeMinThreshold(0.2)
    test.ejecutarTest(maquina, "0.2", "data/threshold/top_5/0_2", "data/ragas_dataset_100.jsonl")
    
    maquina.changeMinThreshold(0.3)
    test.ejecutarTest(maquina, "0.3", "data/threshold/top_5/0_3", "data/ragas_dataset_100.jsonl")
    
    maquina.changeMinThreshold(0.4)
    test.ejecutarTest(maquina, "0.4", "data/threshold/top_5/0_4", "data/ragas_dataset_100.jsonl")
    
    maquina.changeMinThreshold(0.5)
    test.ejecutarTest(maquina, "0.5", "data/threshold/top_5/0_5", "data/ragas_dataset_100.jsonl")
    
    maquina.changeMinThreshold(0.6)
    test.ejecutarTest(maquina, "0.6", "data/threshold/top_5/0_6", "data/ragas_dataset_100.jsonl")
    
    maquina.changeMinThreshold(0.7)
    test.ejecutarTest(maquina, "0.7", "data/threshold/top_5/0_7", "data/ragas_dataset_100.jsonl")
    
    maquina.changeMinThreshold(0.8)
    test.ejecutarTest(maquina, "0.8", "data/threshold/top_5/0_8", "data/ragas_dataset_100.jsonl")

    maquina.changeMinThreshold(0.9)
    test.ejecutarTest(maquina, "0.9", "data/threshold/top_5/0_9", "data/ragas_dataset_100.jsonl")



#optimoThreshold
maquina=rag.rag(False, False, 0.5)
maquina.purgarBasesDatos()
aux=maquina.newListBoesDocuments(PRUEBA)

if aux:
    test.ejecutarTest(maquina, "threshold0-5", "data/optimoThreshold/top_5", "data/ragas_dataset_100.jsonl")


#Todos
maquina=rag.rag(True, True, 0.5)
maquina.purgarBasesDatos()
aux=maquina.newListBoesDocuments(PRUEBA)

if aux:
    test.ejecutarTest(maquina, "todos", "data/todos/top_5", "data/ragas_dataset_100.jsonl")
"""