# uvicorn actions.api:app --reload --port 8002
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import src.rag.rag as rag
import traceback
import math

# Inicializamos el rag
maquina = rag.rag()

app = FastAPI(title="TFG API")

# --- Modelos de datos ---
class IdRequest(BaseModel):
    id_documento: str


class QueryRequest(BaseModel):
    query: str


class boleanRequest(BaseModel):
    value: bool


class floatRequest(BaseModel):
    value: float

class intRequest(BaseModel):
    value: int


class pageRequest(BaseModel):
    page: int
    num_docs_page: int


@app.post("/preguntar")
def preguntar_api(req: QueryRequest):
    try:
        respuesta = maquina.preguntar(req.query)
        return {"respuesta": respuesta}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/addDocument")
def addDocument(req: IdRequest):
    try:
        respuesta = maquina.newBoeDocument(req.id_documento)
        return {"respuesta": respuesta}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

    
@app.post("/deleteDocument")
def deleteDocument(req: IdRequest):
    try:
        respuesta = maquina.deleteDocument(req.id_documento)
        return {"respuesta": respuesta}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/purgar")
def purgarBD():
    try:
        maquina.purgarBasesDatos()
        return {"status": "ok"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents")
def listarDocuments(req: pageRequest):
    try:
        docs = maquina.print_all_document()

        #Calcular numero de páginas
        total_docs = len(docs)
        total_paginas = math.ceil(total_docs / req.num_docs_page)

        #Calcular documentos devueltos
        inicio = (req.page - 1) * req.num_docs_page
        fin = inicio + req.num_docs_page

        docs_pagina = docs[inicio:fin]

        out={
            "docs_pagina": docs_pagina,
            "total_docs": total_docs,
            "total_paginas": total_paginas
        }

        return out
    
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mecanismoDelete")
def getDelete():
    try:
        return maquina.getDerogations()
    
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mecanismoDelete")
def postDelete(req: boleanRequest):
    try:
        maquina.changeDerogations(req.value)
    
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mecanismoUnificate")
def getUnificate():
    try:
        return maquina.getUnificate()
    
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mecanismoUnificate")
def postUnificate(req: boleanRequest):
    try:
        maquina.changeUnificate(req.value)
    
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mecanismoThreshold")
def getThreshold():
    try:
        return maquina.getMinThreshold()
    
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mecanismoThreshold")
def postThreshold(req: floatRequest):
    try:
        maquina.changeMinThreshold(req.value)
    
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dimensions")
def getDimensions():
    try:
        return maquina.get_dim()
    
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/dimensions")
def postDimensions(req: intRequest):
    try:
        maquina.change_dim(req.value)
    
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory")
def getDimensions():
    try:
        return maquina.getMemory()
    
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/memory")
def postDimensions(req: boleanRequest):
    try:
        maquina.change_memory(req.value)
    
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
