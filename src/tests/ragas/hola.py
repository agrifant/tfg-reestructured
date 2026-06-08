from ragas.testset import TestsetGenerator
from langchain_core.documents import Document
from datetime import datetime
import src.pipeline.pipeline as pipe
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
import random
import os
from ragas.llms import LangchainLLMWrapper
import json

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

llm = ChatOllama(
    model="llama3.1:8b",
    temperature=0
)

ragas_llm = LangchainLLMWrapper(llm)

generator = TestsetGenerator.from_langchain(
    llm=ragas_llm,
    embedding_model=embedding_model
)

def generateCuestions(n, id_document="BOE-A-2015-3439"):
    documento = pipe.generarContextoPreguntas(id_document)

    docs = [Document(page_content=text) for text in documento]

    tests = []

    for i in range(n):
        random.shuffle(docs)

        testset = generator.generate_with_langchain_docs(
            [docs[0]],
            1,
            transforms=[],
            raise_exceptions=True
        )

        tests.extend(testset.to_list())

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    os.makedirs("data/questions", exist_ok=True)

    with open(f"data/questions/rag_testset_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(tests, f, ensure_ascii=False, indent=2)