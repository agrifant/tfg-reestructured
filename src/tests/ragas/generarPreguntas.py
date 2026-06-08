from ragas.testset import TestsetGenerator
from langchain_core.documents import Document
from langchain_groq import ChatGroq
from datetime import datetime
import src.pipeline.pipeline as pipe
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
import random
import pandas as pd
import json
import os
# python3 -m src.tests.ragas.generarPreguntas

#Modelo llm y embedding que vamos a usar para hacer las preguntas
load_dotenv() 

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    model_kwargs={
        "response_format": {"type": "json_object"}}
)

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

#Obtenemos el documento del que vamos a sacar las preguntas
documento=pipe.generarContextoPreguntas("BOE-A-2015-3439")
docs = [Document(page_content=text) for text in documento]

docs = [
    Document(
        page_content=(
            "IMPORTANTE: TODO DEBE SER EN ESPAÑOL. "
            "Genera preguntas y respuestas SOLO en español.\n\n"
            + text
        )
    )
    for text in documento
]

#Hacemos las preguntas con el generador
generator = TestsetGenerator.from_langchain(
    llm=llm,
    embedding_model=embedding_model
)
tests=[]
for i in range(1):
    random.shuffle(docs)
    doc_prueba = docs[0]
    testset = generator.generate_with_langchain_docs(
        [doc_prueba],
        1
    )
    tests.append(testset)

#Las guardamos en un fichero
timestamp = datetime.now().isoformat()

os.makedirs("data/questions", exist_ok=True) 
with open(f"data/questions/rag_testset_{timestamp}.json", "w", encoding="utf-8") as f:
    json.dump(
        [test.to_list() for test in tests],
        f,
        ensure_ascii=False,
        indent=2
    )