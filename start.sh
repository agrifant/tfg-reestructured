#!/bin/bash

# export NEO4J_TOKEN=tu_password
# ./start.sh

# ChromaDB
echo "Iniciando ChromaDB..."
chroma run --host localhost --port 8001 &

echo "Esperando a ChromaDB..."
until nc -z localhost 8001; do
  sleep 2
done

# FastAPI
echo "Iniciando FastAPI..."
uvicorn src.actions.api:app --reload --port 8002 &

echo "Esperando a FastAPI..."
until nc -z localhost 8002; do
  sleep 2
done

# Streamlit
echo "Iniciando Streamlit..."
streamlit run src/front/front.py --server.port 8501 &

echo "Todos los servicios iniciados."

# Esperar procesos
echo "Pulsa cualquier cosa para apagar"
wait

echo "Deteniendo servicios..."

# ChromaDB
lsof -ti:8001 | xargs -r kill -9

# FastAPI
lsof -ti:8002 | xargs -r kill -9

# Streamlit
lsof -ti:8501 | xargs -r kill -9

echo "Todos los servicios detenidos."