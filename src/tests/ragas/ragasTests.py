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
from ragas.run_config import RunConfig

from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision
)


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
    Eres un experto en generación de datasets de evaluación para sistemas RAG jurídicos.
    
    Tu tarea es crear una pregunta y su respuesta basadas únicamente en el contexto proporcionado.
    
    Reglas:
    - Genera una única pregunta.
    - La pregunta debe sonar como una consulta real que haría una persona.
    - La pregunta debe ser clara, específica y breve.
    - La respuesta debe encontrarse explícitamente en el contexto.
    - No inventes información.
    - Evita copiar literalmente frases completas del texto.
    - Evita referencias como:
      - "artículo anterior"
      - "inciso precedente"
      - "texto anterior"
      - "norma anterior"
      - "conducta descrita anteriormente"
    - La pregunta debe ser autocontenida y entendible por sí sola.
    - No generes casos hipotéticos.
    - La pregunta debe identificar explícitamente la norma, ley, reglamento o documento cuando dicha información esté disponible en el contexto.
    - Evita preguntas que puedan tener múltiples respuestas válidas en distintos documentos.
    - No utilices únicamente referencias estructurales como "artículo 5", "disposición final quinta" o "anexo II" sin mencionar el documento al que pertenecen.
    
    Formato:
    {
      "question": "...",
      "answer": "..."
    }
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
    

def generarPreguntas(question_num, output_file, id_boe="BOE-A-2015-3439"):
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
        
def ResponderPreguntas(maquina, output_file, percent):
    with open(output_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    total = len(lines)
    num_preguntas = max(1, int(total * percent / 100))

    all_questions_responded = []

    for i, line in enumerate(lines[:num_preguntas], start=1):
        data = json.loads(line)

        answer, texts = maquina.preguntar(data["question"], True)
        data["contexts"] = texts
        data["answer"] = answer

        all_questions_responded.append(data)

        print(f"Respondida pregunta {i}/{num_preguntas}")

    return Dataset.from_list(all_questions_responded)

def guararResultados(rows, filename):
    filename_csv = os.path.join(filename, "resultados.csv")
    os.makedirs(filename, exist_ok=True)

    df = pd.DataFrame(rows)

    file_exists = os.path.isfile(filename_csv)

    df.to_csv(
        filename_csv,
        mode="a",
        header=not file_exists,
        index=False,
        encoding="utf-8"
    )

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
    
def ejecutarTest(maquina, name, filename, filename_test, percent=100):
    #Respondemos las preguntas:
    print("Respondiendo preguntas")
    data= ResponderPreguntas(maquina, filename_test, percent)

    #Hacemos el test con ragas
    
    llm = Ollama(model="llama3.1:8b")

    embeddings = HuggingFaceEmbeddings(
        model_name="jinaai/jina-embeddings-v3",
        model_kwargs={
            "trust_remote_code": True,
        },
        encode_kwargs={
            "task": "text-matching",
            "truncate_dim": 32,
        },
    )

    metrics = [faithfulness, answer_relevancy, context_recall, context_precision]

    all_rows = []
    
    for metric in metrics:
        result = evaluate(
            data,
            metrics=[metric],
            llm=llm,
            embeddings=embeddings,
            run_config=RunConfig(
                max_workers=1
            )
        )
    
        df = result.to_pandas()
    
        score_cols = [
            "faithfulness",
            "answer_relevancy",
            "context_recall",
            "context_precision"
        ]
    

        df = result.to_pandas()

        col = metric.name
    
        values = pd.to_numeric(df[col], errors="coerce")
    
        for i, value in enumerate(values):
            if pd.isna(value):
                continue
    
            all_rows.append({
                "name": name,
                "metric": col,
                "question_id": i,
                "value": float(value)
            })

    guararResultados(all_rows, filename)