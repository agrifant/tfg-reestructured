from ragas.testset import TestsetGenerator
from langchain_core.documents import Document
from langchain_groq import ChatGroq
from datetime import datetime
import src.pipeline.pipeline as pipe
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
import random
import time
import pandas as pd
import os
import groq

# python3 -m src.tests.ragas.generarPreguntas2


#Obtenemos el documento del que vamos a sacar las preguntas
documento=pipe.generarContextoPreguntas("BOE-A-2015-3439")


tests=[]
for i in range(3):
    random.shuffle(documento)
    content = documento[0]
    prompt=f"Generame una pregunta en relación con este texto:\n\n{content}"
    client = groq(api_key=os.environ.get("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",  
            messages=[
                {"role": "system", "content": "Eres un generador de preguntas para testear un RAG"},
                {"role": "user",   "content": f"{prompt}"}
            ],
    )
    tests.append(response.choices[0].message.content)

#Las guardamos en un fichero
timestamp = datetime.now().isoformat()
dfs = []
for test in tests:
    dfs.append(test.to_pandas())

final_df = pd.concat(dfs, ignore_index=True)
final_df.to_csv(f"rag_testset_{timestamp}.csv", index=False)