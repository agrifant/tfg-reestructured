import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import wilcoxon

def make_grafica(
    file1,
    file2,
    title,
    name_col_x="name",
    dataset1_name="Dataset 1",
    dataset2_name="Dataset 2"
):
    df1 = pd.read_csv(os.path.join(file1, "resultados.csv"))
    df2 = pd.read_csv(os.path.join(file2, "resultados.csv"))

    df1["dataset"] = dataset1_name
    df2["dataset"] = dataset2_name

    df = pd.concat([df1, df2], ignore_index=True)

    x_col = name_col_x

    required_cols = {x_col, "metric", "value", "dataset"}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        print(f"Faltan columnas: {missing}")
        return

    metrics = sorted(df["metric"].dropna().unique())
    datasets = [dataset1_name, dataset2_name]

    x = np.arange(len(metrics))

    width = 0.35  # dos barras → centradas

    colors = {
        dataset1_name: "steelblue",
        dataset2_name: "orange"
    }

    plt.figure(figsize=(14, 7))

    for i, dataset in enumerate(datasets):

        subset = df[df["dataset"] == dataset]

        values = (
            subset.groupby("metric")["value"]
            .mean()
            .reindex(metrics)
            .values
        )

        # 🔥 clave: centrado perfecto por métrica
        offset = (i - 0.5) * width

        plt.bar(
            x + offset,
            values,
            width=width,
            label=dataset,
            color=colors[dataset],
            alpha=0.9
        )

    plt.xticks(x, metrics, rotation=25)
    plt.ylabel("Score")
    plt.title(title)

    plt.legend(title="Dataset")
    plt.tight_layout()

    plt.savefig(
        os.path.join(file1, "metricas_comparadas.png"),
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

def make_grafica_lineas(
    *csv_files,
    output_dir=".",
    title="Comparación de métricas",
    name_col_x="name",
):
    """
    Recibe un número indeterminado de carpetas que contienen un
    'resultados.csv' y genera una gráfica de líneas para cada métrica.

    Ejemplo:
        make_grafica_lineas(
            "data/top1",
            "data/top3",
            "data/top5",
            output_dir="graficas"
        )
    """

    dfs = []

    for folder in csv_files:
        csv_path = os.path.join(folder, "resultados.csv")

        df = pd.read_csv(csv_path)

        required = {name_col_x, "metric", "value"}
        if not required.issubset(df.columns):
            raise ValueError(
                f"{csv_path} no contiene las columnas {required}"
            )

        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)

    metrics = sorted(df["metric"].unique())

    for metric in metrics:

        plt.figure(figsize=(10, 6))

        subset = (
            df[df["metric"] == metric]
            .groupby(name_col_x, as_index=False)["value"]
            .mean()
            .sort_values(name_col_x)
        )

        plt.plot(
            subset[name_col_x],
            subset["value"],
            marker="o",
            linewidth=2
        )

        plt.title(f"{title} - {metric}")
        plt.xlabel("Threshold")
        plt.ylabel("Score")
        plt.ylim(0, 1)
        plt.grid(True, alpha=0.3)

        plt.tight_layout()

        plt.savefig(
            os.path.join(output_dir, f"{metric}.png"),
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()


alpha = 0.05

def testEstadistico(file_1, name_file_1, file_2, name_file_2):
    dataset_1 = pd.read_csv(os.path.join(file_1, "resultados.csv"))
    dataset_2 = pd.read_csv(os.path.join(file_2, "resultados.csv"))

    metrics = ["faithfulness", "answer_relevancy", "context_recall", "context_precision"]

    for metric in metrics:
        data_1 = dataset_1[dataset_1["metric"] == metric].copy()
        data_2 = dataset_2[dataset_2["metric"] == metric].copy()

        ids_1 = set(data_1["question_id"])
        ids_2 = set(data_2["question_id"])

        # IDs que faltan
        faltan_en_1 = ids_2 - ids_1
        faltan_en_2 = ids_1 - ids_2

        # Mostrar mensajes
        #for qid in sorted(faltan_en_1):
            # print(f"[{metric}] question_id {qid} no presente en dataset 1. Se elimina del dataset 2.")

        #for qid in sorted(faltan_en_2):
            # print(f"[{metric}] question_id {qid} no presente en dataset 2. Se elimina del dataset 1.")

        # Eliminar los IDs que no están en ambos
        ids_comunes = ids_1 & ids_2
        data_1 = data_1[data_1["question_id"].isin(ids_comunes)]
        data_2 = data_2[data_2["question_id"].isin(ids_comunes)]

        # Ordenar para que ambas tablas tengan el mismo orden
        data_1 = data_1.sort_values("question_id").reset_index(drop=True)
        data_2 = data_2.sort_values("question_id").reset_index(drop=True)

        # Comprobación final
        assert data_1["question_id"].equals(data_2["question_id"])

        # Obtenemos los vectores

        vector_1 = data_1["value"].to_numpy()
        vector_2 = data_2["value"].to_numpy()

        stat, p = wilcoxon(vector_1, vector_2, zero_method="pratt")

        print(f"\n{metric}")
        print(f"W = {stat:.3f}")
        print(f"p = {p:.4f}")
        print(f"Media {name_file_1}: {vector_1.mean():.4f}")
        print(f"Media {name_file_2}: {vector_2.mean():.4f}")
        print(f"No se han tenido en cuenta {len(faltan_en_1) + len(faltan_en_2)} preguntas")
        if p < alpha:
            print("Diferencia estadísticamente significativa\n")
        else:
            print("No se detectan diferencias significativas\n")
