
from datasets import Dataset
from ragas import evaluate
import ast
import pandas as pd
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# python3 -m src.tests.ragas.test
load_dotenv() 

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    model_kwargs={
        "response_format": {"type": "json_object"}}
)

df = pd.read_csv("tus_preguntas_contestadas.csv")
df["contexts"] = df["contexts"].apply(ast.literal_eval)
df["reference_contexts"] = df["reference_contexts"].apply(ast.literal_eval)

dataset = Dataset.from_pandas(df)

from ragas.metrics import (
    faithfulness,
    answer_relevancy
)

"""result = evaluate(
    dataset,
    metrics=[
        faithfulness,
        answer_relevancy
    ],
)"""

result = evaluate(
    dataset,
    metrics=[
        faithfulness
    ],
    llm=llm
)

print(result)