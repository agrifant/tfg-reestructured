import src.tests.ragas.ragasTests as test
import src.rag.rag as rag

with open("identificadores.txt", "r", encoding="utf-8") as f:
    PRUEBA = f.read().splitlines()


maquina=rag.rag(False, False, 0.0)

"""
humbrales=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]


# Elección optimo threshold
maquina.purgarBasesDatos()
aux=maquina.newListBoesDocuments(PRUEBA)

if aux:
    for i in humbrales:
        nombre = str(i).replace(".", "_")
        
        maquina.changeMinThreshold(i)
        test.ejecutarTest(maquina, f"{i}", "data/chooseThreshols/", f"{nombre}.csv", "data/ragas_dataset_100.jsonl", 30)
else:
    print("Abortado")
"""
        




dimensions = [1024, 768, 512, 384, 256, 128, 64, 32, 16, 8, 4]


for dim in dimensions:
    maquina.change_dim(dim)

    
    print(f"MecanismoBase con dim {dim}")
    maquina.purgarBasesDatos()
        
    maquina.changeDerogations(False)
    maquina.changeUnificate(False)
    maquina.changeMinThreshold(0.0)
    
    aux=maquina.newListBoesDocuments(PRUEBA)
        
    if aux:
        test.ejecutarTest(maquina, "mecanismoBase", f"data/{dim}/","mecanismoBase.csv", "data/ragas_dataset_100.jsonl")
    else:
        print("Abortado")



    
    print(f"Delete con dim {dim}")
    maquina.purgarBasesDatos()
        
    maquina.changeDerogations(True)
    maquina.changeUnificate(False)
    maquina.changeMinThreshold(0.0)
    
    aux=maquina.newListBoesDocuments(PRUEBA)
        
    if aux:
        test.ejecutarTest(maquina, "Delete", f"data/{dim}/", "delete.csv", "data/ragas_dataset_100.jsonl")
    else:
        print("Abortado")


    print(f"Unificate con dim {dim}")
    maquina.purgarBasesDatos()
        
    maquina.changeDerogations(False)
    maquina.changeUnificate(True)
    maquina.changeMinThreshold(0.0)
    
    aux=maquina.newListBoesDocuments(PRUEBA)
        
    if aux:
        test.ejecutarTest(maquina, "Unificate", f"data/{dim}/", "unificate.csv", "data/ragas_dataset_100.jsonl")
    else:
        print("Abortado")
    

    print(f"Threshold con dim {dim}")
    maquina.purgarBasesDatos()
        
    maquina.changeDerogations(False)
    maquina.changeUnificate(False)
    maquina.changeMinThreshold(0.5)
    
    aux=maquina.newListBoesDocuments(PRUEBA)
        
    if aux:
        test.ejecutarTest(maquina, "Threshold", f"data/{dim}/", "threshold.csv", "data/ragas_dataset_100.jsonl")
    else:
        print("Abortado")