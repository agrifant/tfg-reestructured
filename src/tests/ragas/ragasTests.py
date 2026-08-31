import os
import json
import random
import pandas as pd
from ragas import evaluate
from datasets import Dataset
from ragas.run_config import RunConfig
from langchain_community.llms import Ollama
from langchain_community.embeddings import HuggingFaceEmbeddings
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision
)

import src.llm.callToLLM as llm
import src.pipeline.pipeline as pipe


# Modelo de embedding usado para la evaluación con RAGAs 
embeddings = HuggingFaceEmbeddings(
        model_name="jinaai/jina-embeddings-v3",
        model_kwargs={
            "trust_remote_code": True,
        },
        encode_kwargs={
            "task": "text-matching",
            "truncate_dim": 1024,
        },
    )

# Modelo de LLM usado para la evaluación con RAGAs
llm = Ollama(model="llama3.1:8b")

# Funciones para generar el dataset de prueba
def make_question(texts:str)->list[json]:
    """
    Función que genera una pregunta y respuesta a partir
    de un texto legislativo proporcionado.

    Args:
        texts (str): Texto legislativo del cual se 
                            va a sacar la pregunta y respuesta.
    
    Returns:
        (json): La pregunta y respuesta generada en formato json
        {
            "question": ...,
            "ground_truth": ...,
        }
    """
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
    """
    Función que genera de un documento del BOE
    genera un dataset con preguntas sobre sus 
    artículos y disposiciones en un .jsonl
    
    Args:
        question_num (int): Número de preguntas a genera 
                                en el dataset.

        output_file (str): Nonmbre y ruta del archivo que 
                            se generará con el dataset .

        id_boe (str): Id del documento del BOE del cual se van a 
                        coger los textos para generar las preguntas
                        y respuestas.
    Returns:
        (void): El datasets con las preguntas y respuestas en la ruta
                especificada.
    """
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

#Funciones para hacer los test con RAGAs    
def ResponderPreguntas(maquina, output_file, percent):
    """
    Función que lee un fichero .jsonl y responde las preguntas
    utilizando el RAG.

    Args:
        maquina (class): El RAG que se utilizará para responder las preguntas.

        output_file (str): Nombre del fichero .jsonl que contiene
                           las preguntas.

        percent (int): Porcentaje, entre 1 y 100, de elementos que se desea
                       responder.

    Returns:
        Dataset: Dataset de Hugging Face que contiene las preguntas 
                    originales junto con sus respuestas y contextos.
    """

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

def guardarResultados(rows, carpeta, filename):
    """ 
    Guarda los resultados en un fichero CSV. 
    Si el fichero ya existe, añade los nuevos resultados al final. 
    Si no existe, crea el fichero e incluye los nombres de las columnas. 

    Args: 
        rows (list): Lista de resultados que se quieren guardar. 
                        Cada elemento debe poder convertirse en una fila de un DataFrame. 

        carpeta (str): Ruta de la carpeta donde se guardará el fichero CSV. 
                        Si la carpeta no existe, se crea automáticamente. 

        filename (str): Nombre del fichero CSV donde se guardarán los resultados. 
        
    Returns: None: No devuelve ningún valor. 
                Guarda los resultados directamente en el fichero CSV. 
    """
    os.makedirs(carpeta, exist_ok=True)

    ruta = os.path.join(carpeta, filename)

    df = pd.DataFrame(rows)

    file_exists = os.path.isfile(ruta)

    df.to_csv(
        ruta,
        mode="a",
        header=not file_exists,
        index=False,
        encoding="utf-8"
    )

def ejecutarTest(maquina, name, carpet, filename, filename_test, percent=100):
    """
    Ejecuta un test sobre el RAG, evaluando las respuestas generadas
    mediante diferentes métricas y guardando los resultados en un fichero CSV.

    Args:
        maquina: Instancia del RAG que se utilizará para responder
                 las preguntas.

        name (str): Nombre o identificador del RAG que se está evaluando.

        carpet (str): Ruta de la carpeta donde se guardarán los resultados.

        filename (str): Nombre del fichero CSV donde se guardarán
                        los resultados de la evaluación.

        filename_test (str): Nombre del fichero .jsonl que contiene
                             las preguntas del test.

        percent (int, optional): Porcentaje, entre 1 y 100, de preguntas
                                 que se desea utilizar en el test.
                                 Por defecto, 100.

    Returns:
        None: No devuelve ningún valor. Guarda los resultados de las métricas
              de evaluación en un fichero CSV.
    """

    #Respondemos las preguntas:
    print("Respondiendo preguntas")
    data= ResponderPreguntas(maquina, filename_test, percent)

    metrics = [faithfulness, answer_relevancy, context_recall, context_precision]

    all_rows = []

    # Se raliza una evaluación por cada métrica
    for metric in metrics:
        # Realizamos la evaluazión con RAGAs
        result = evaluate(
            data,
            metrics=[metric],
            llm=llm,
            embeddings=embeddings,
            run_config=RunConfig(
                max_workers=1
            )
        )

        # Guardamos los resultados en una lista
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

    # Guardamos los resultados de las evaluaciones
    guardarResultados(all_rows, carpet, filename)