# uvicorn actions.api:app --reload --port 8002
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import src.rag.rag as rag
import traceback

# Inicializamos el rag
maquina = rag.rag()

app = FastAPI(title="TFG API")

# --- Modelos de datos ---
class IdRequest(BaseModel):
    id_documento: str

class QueryRequest(BaseModel):
    query: str

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
def listarDocuments():
    try:
        return maquina.print_all_document()
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))