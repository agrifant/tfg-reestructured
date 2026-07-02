#!/bin/bash

set -e

echo "Iniciando Chroma..."
chroma run --host localhost --port 8001 > /dev/null 2>&1 &
CHROMA_PID=$!

echo "Esperando a que Chroma esté listo..."
until curl -s http://localhost:8001/api/v2/heartbeat > /dev/null; do
    sleep 1
done

# Apagar Chroma al salir del script
trap "kill $CHROMA_PID" EXIT

echo "Ejecutando test..."
python3 pasarTest.py

echo "Test finalizado."