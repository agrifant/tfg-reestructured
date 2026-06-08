import pandas as pd
import os
# python3 -m src.tests.ragas.ver
df = pd.read_csv("tus_preguntas_contestadas.csv")

for i in range(len(df)):
    row = df.iloc[i]

    print(f"\n=== EJEMPLO {i} ===\n")

    # imprimir todas las columnas dinámicamente
    for col, value in row.items():
        print(f"{col}: {value}\n")

    input("\nPulsa ENTER para ver el siguiente...")
    os.system("clear")  # Linux/Mac