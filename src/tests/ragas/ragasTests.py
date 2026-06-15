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
import matplotlib.pyplot as plt

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
    

def generarPreguntas(question_num, output_file=output_file, id_boe="BOE-A-2015-3439"):
    # Obtenemos el documento del que queremos hacer las preguntas
    documento = pipe.generarContextoPreguntas(id_boe)
    
    os.makedirs("data", exist_ok=True)
    
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

def guararResultados(results, name, filename):
    filename_csv = os.path.join(filename, "resultados.csv")

    os.makedirs(filename, exist_ok=True)

    # Convertir a DataFrame
    if hasattr(results, "to_pandas"):
        df = results.to_pandas()
    else:
        df = pd.DataFrame(results)

    # Construir resumen estadístico
    row = {"name": name}

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

    out_df = pd.DataFrame([row])

    # ✔ AQUÍ está la corrección importante
    file_exists = os.path.isfile(filename_csv)

    out_df.to_csv(
        filename_csv,
        mode="a",
        header=not file_exists,
        index=False,
        encoding="utf-8"
    )

    print(f"Guardado en CSV: {row}")

def make_grafica(file, title, name_col_x):
    file_input = os.path.join(file, "resultados.csv")
    
    df = pd.read_csv(file_input)

    x_col = "name"
    columnas = ["faithfulness_mean", "answer_relevancy_mean", "context_recall_mean", "context_precision_mean"]

    for col in columnas:
        if x_col not in df.columns:
            print(f"Columna '{x_col}' no encontrada")
            return

        if col not in df.columns:
            print(f"Columna '{col}' no encontrada")
            continue

        plt.figure(figsize=(10, 6))
        plt.plot(df[x_col], df[col], marker="o")

        plt.xlabel(name_col_x)
        plt.ylabel(col)
        plt.title(title)

        #plt.ylim(0, 1)
        
        # Rotar etiquetas si son nombres largos
        plt.xticks(rotation=45)

        plt.savefig(
            f"{file}/{col}.png",
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()
    
def ejecutarTest(maquina, name, filename):
    #Respondemos las preguntas:
    data= ReponderPreguntas(maquina)

    #Hacemos el test con ragas
    
    llm = Ollama(model="llama3.1:8b")

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    """
                answer_relevancy,
            context_recall,
            context_precision
    """
    result = evaluate(
        data,
        metrics=[
            faithfulness],
        llm=llm,
        embeddings=embeddings
    )

    guararResultados(result, name, filename)