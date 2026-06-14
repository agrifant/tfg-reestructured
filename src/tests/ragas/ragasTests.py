import src.pipeline.pipeline as pipe
import src.llm.callToLLM as llm
import src.rag.rag as rag
from ragas import evaluate
from datasets import Dataset
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
import random
import json
import os
import pandas as pd
import numpy as np

from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision
)

output_file= "data/ragas_dataset.jsonl"

def make_question(texts:str)->list[json]:
    intentos=3
    intento=0
    
    format = {
        "type": "object",
        "properties": {
                "question": {"type": "string"},
                "answer": {"type": "string"}
            },
        "required": ["question", "answer"]
    }
    system_prompt = """
        Eres un experto en generación de datasets de evaluación para sistemas RAG.
        
        Tu tarea es crear preguntas y sus respuestas que puedan responderse exclusivamente con la información proporcionada.
        
        Reglas:
        - La pregunta debe ser clara, específica y natural.
        - No inventes información que no aparezca en el contexto.
        - Evita preguntas ambiguas o demasiado genéricas.
        - La respuesta debe encontrarse explícitamente en el contexto.
        - Genera una única pregunta.
        - La pregunta debe referirse explícitamente a elementos concretos presentes en el texto (artículos, penas, conceptos mencionados).
        - No se permiten referencias genéricas como "los hechos descritos en la ley", "el texto anterior" o "la ley mencionada".
        - Evita cualquier formulación hipotética o condicional que introduzca sujetos no mencionados literalmente en el contexto.
        - La pregunta debe poder responderse copiando o extrayendo directamente una parte del texto.

        Formato:
        Devuelve un JSON con este formato EXACTO:
        
        {{
          "question": "...",
          "answer": "..."
        }}
        """
    

    user_prompt = f"""
        Contexto:
        
        {texts}
        
        Genera una pregunta cuya respuesta pueda obtenerse directamente del contexto anterior.
        """

    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}]

    while True:
        response= llm.call_ollama(messages, format)

        try:
            data = json.loads(response)
            return data
        except Exception:
            intento+=1
            if intento>=intentos:
                print("salida forzada")
                return []
    

def generarPreguntas(question_num, id_boe="BOE-A-2015-3439", output_file=output_file):
    # Obtenemos el documento del que queremos hacer las preguntas
    documento = pipe.generarContextoPreguntas(id_boe)

    with open(output_file, "w", encoding="utf-8") as f:
        for i in range(question_num):

            # Barajamos los contextos
            random.shuffle(documento)
            context = documento[0]

            # Generamos pregunta y respuesta (deberías adaptar make_question)
            qa = make_question(context)

            # Esperado: qa = {"question": "...", "answer": "..."}
            record = {
                "question": qa["question"],
                "ground_truth": qa["answer"],
                "meta": context
            }

            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Dataset guardado en {output_file}")
        
def ReponderPreguntas(maquina, output_file=output_file):
    all_questions_responded=[]
    with open(output_file, "r", encoding="utf-8") as f:
        for line in f:
            data=json.loads(line)
            answer, texts= maquina.preguntar(data["question"], True)
            data["contexts"]=texts
            data["answer"]=answer
            all_questions_responded.append(data)

    return Dataset.from_list(all_questions_responded)

def guararResultados(results, name, filename="data/ragas_results.csv"):

    #Convertir a DataFrame
    if hasattr(results, "to_pandas"):
        df = results.to_pandas()
    else:
        df = pd.DataFrame(results)

    # Construir resumen estadístico
    row = {
        "name": name
    }

    ignore_cols = {"question", "answer", "contexts", "ground_truth"}

    for col in df.columns:
        if col in ignore_cols:
            continue

        try:
            values = df[col].dropna().astype(float)

            row[f"{col}_mean"] = float(np.mean(values))
            row[f"{col}_var"] = float(np.var(values))

        except Exception:
            pass


    # 3. Añadimos a CSV 
    file_exists = os.path.isfile(filename)

    out_df = pd.DataFrame([row])

    out_df.to_csv(
        filename,
        mode="a",
        header=not file_exists,
        index=False,
        encoding="utf-8"
    )

    print(f"Guardado en CSV: {row}")
    
def ejecutarTest(maquina, name):
    #Respondemos las preguntas:
    data= ReponderPreguntas(maquina)

    #Hacemos el test con ragas
    """result = evaluate(
        dataset,
        metrics=[
            faithfulness,
            answer_relevancy
        ],
    )"""
    
    llm = Ollama(model="llama3.1:8b")

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    result = evaluate(
        data,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_recall,
            context_precision],
        llm=llm,
        embeddings=embeddings
    )

    guararResultados(result, name)