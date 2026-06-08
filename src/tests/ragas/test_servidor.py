from datasets import Dataset
from ragas import evaluate
import json
import pandas as pd
from langchain_ollama import ChatOllama
from ragas.metrics import (
    faithfulness,
    answer_relevancy
)

llm = ChatOllama(
    model="llama3.1:8b",
    temperature=0
)

with open("data/questions/preguntas.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

dataset = Dataset.from_pandas(df)

result = evaluate(
    dataset,
    metrics=[faithfulness],
    llm=llm
)

print(result)