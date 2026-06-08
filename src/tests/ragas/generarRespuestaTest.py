import pandas as pd
import src.rag.rag as rag
import ast
# python3 -m src.tests.ragas.generarRespuestaTest

maquina = rag.rag()
df = pd.read_csv("rag_test.csv")

# Renombrar columnas
df = df.rename(columns={
    "user_input": "question",
    "reference": "ground_truth",
    "reference_contexts": "reference_contexts"
})

# Convertir a lista
df["reference_contexts"] = df["reference_contexts"].apply(ast.literal_eval)

def rag_pipeline(question):
    result, context = maquina.preguntarTest(question)
    return result, context

answers = []
contexts_rag = []

for _, row in df.iterrows():
    answer, contexts = rag_pipeline(row["question"])
    answers.append(answer)
    contexts_rag.append(contexts)

# Guardar resultados
df["answer"] = answers
df["contexts"] = contexts_rag  # ← contextos del RAG (predicción)

# Guardar CSV final
df.to_csv("tus_preguntas_contestadas.csv", index=False)