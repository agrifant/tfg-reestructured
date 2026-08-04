import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import wilcoxon


def make_unique_lineal_grafic(
    title,
    output_dir,
    *csv_files
):

    #calculamos la media y varianza de cada dataset y cada metrica
    data = {}
    for csv_path, label in csv_files:
        df = pd.read_csv(csv_path)

        stats = (
            df.groupby("metric")["value"]
              .agg(["mean", "var"])
        )

        for metric, row in stats.iterrows():
            if metric not in data:
                data[metric] = {
                    "x": [],
                    "mean": [],
                    "var": []
                }

            # Mantener el orden en que se reciben los datasets
            data[metric]["x"].append(label)
            data[metric]["mean"].append(row["mean"])
            data[metric]["var"].append(row["var"])

    os.makedirs(output_dir, exist_ok=True)


    
    # Grafica de la media
    plt.figure(figsize=(14, 7))

    for metric, values in data.items():
        plt.plot(
            values["x"],
            values["mean"],
            marker="o",
            linewidth=2,
            label=metric
        )

    plt.title(f"{title} - Media")
    plt.xlabel("Tamaño")
    plt.ylabel("Media")
    plt.grid(True)
    plt.legend()

    plt.savefig(
        os.path.join(output_dir, f"{title}_media.png"),
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


    # Grafica de la varianza

    plt.figure(figsize=(14, 7))

    for metric, values in data.items():
        plt.plot(
            values["x"],
            values["var"],
            marker="o",
            linewidth=2,
            label=metric
        )

    plt.title(f"{title} - Varianza")
    plt.xlabel("Tamaño")
    plt.ylabel("Varianza")
    plt.grid(True)
    plt.legend()

    plt.savefig(
        os.path.join(output_dir, f"{title}_varianza.png"),
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()
    



def make_compare_lineal_grafic(
    title,
    output_dir,
    groups
):

    def procesar(grupo):
        data = {}

        for csv_path, label in grupo:
            df = pd.read_csv(csv_path)

            stats = (
                df.groupby("metric")["value"]
                .agg(["mean", "var"])
            )

            for metric, row in stats.iterrows():
                data.setdefault(metric, {
                    "x": [],
                    "mean": [],
                    "var": []
                })

                data[metric]["x"].append(label)
                data[metric]["mean"].append(row["mean"])
                data[metric]["var"].append(row["var"])

        return data

    # Procesar todos los grupos
    processed_groups = {
        group_name: procesar(group_data)
        for group_name, group_data in groups
    }

    os.makedirs(output_dir, exist_ok=True)

    # Obtener todas las métricas presentes
    metricas = sorted({
        metric
        for data in processed_groups.values()
        for metric in data.keys()
    })

    for metric in metricas:

        # =======================
        # MEDIA
        # =======================

        plt.figure(figsize=(14, 7))

        for group_name, data in processed_groups.items():

            if metric not in data:
                continue

            plt.plot(
                data[metric]["x"],
                data[metric]["mean"],
                marker="o",
                linewidth=2,
                label=group_name
            )

        plt.title(f"{title} - {metric} (Media)")
        plt.xlabel("Tamaño")
        plt.ylabel("Media")
        plt.grid(True)
        plt.legend()

        plt.savefig(
            os.path.join(output_dir, f"{metric}_media.png"),
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        # =======================
        # VARIANZA
        # =======================

        plt.figure(figsize=(14, 7))

        for group_name, data in processed_groups.items():

            if metric not in data:
                continue

            plt.plot(
                data[metric]["x"],
                data[metric]["var"],
                marker="o",
                linewidth=2,
                label=group_name
            )

        plt.title(f"{title} - {metric} (Varianza)")
        plt.xlabel("Tamaño")
        plt.ylabel("Varianza")
        plt.grid(True)
        plt.legend()

        plt.savefig(
            os.path.join(output_dir, f"{metric}_varianza.png"),
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()



def make_boxplot(title, output_dir, csv_file):
    df = pd.read_csv(csv_file)

    # Mantener el orden de aparición de las métricas
    metrics = df["metric"].unique()

    data = [
        df[df["metric"] == metric]["value"].values
        for metric in metrics
    ]

    fig, ax = plt.subplots(figsize=(15, 8))

    bp = ax.boxplot(
        data,
        tick_labels=metrics,
        patch_artist=True,
        showmeans=True,
        meanline=True,
        widths=0.6
    )

    # Colorear las cajas
    for box in bp["boxes"]:
        box.set(facecolor="#87CEEB", edgecolor="black", linewidth=1.5)

    # Mediana
    for median in bp["medians"]:
        median.set(color="red", linewidth=2)

    # Media
    for mean in bp["means"]:
        mean.set(color="darkgreen", linewidth=2)

    # Bigotes
    for whisker in bp["whiskers"]:
        whisker.set(linewidth=1.5)

    # Extremos
    for cap in bp["caps"]:
        cap.set(linewidth=1.5)

    # Valores atípicos
    for flier in bp["fliers"]:
        flier.set(
            marker="o",
            markersize=5,
            alpha=0.6
        )

    ax.set_title(title, fontsize=18, fontweight="bold")
    ax.set_xlabel("Métrica", fontsize=13)
    ax.set_ylabel("Valor", fontsize=13)

    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.xticks(rotation=30, ha="right")

    plt.tight_layout()

    os.makedirs(output_dir, exist_ok=True)

    plt.savefig(
        os.path.join(output_dir, f"{title}_boxplot.png"),
        dpi=300
    )

    plt.close()

def make_barplot_compare(
    title,
    output_dir,
    csv1,
    label1,
    csv2,
    label2
):

    df1 = pd.read_csv(csv1)
    df2 = pd.read_csv(csv2)

    stats1 = (
        df1.groupby("metric")["value"]
        .agg(["mean", "var"])
    )

    stats2 = (
        df2.groupby("metric")["value"]
        .agg(["mean", "var"])
    )

    metrics = sorted(set(stats1.index) | set(stats2.index))

    mean1 = [stats1.loc[m, "mean"] if m in stats1.index else 0 for m in metrics]
    mean2 = [stats2.loc[m, "mean"] if m in stats2.index else 0 for m in metrics]

    var1 = [stats1.loc[m, "var"] if m in stats1.index else 0 for m in metrics]
    var2 = [stats2.loc[m, "var"] if m in stats2.index else 0 for m in metrics]

    x = np.arange(len(metrics))
    width = 0.35

    os.makedirs(output_dir, exist_ok=True)

    # =======================
    # MEDIA
    # =======================

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.bar(
        x - width / 2,
        mean1,
        width,
        label=label1
    )

    ax.bar(
        x + width / 2,
        mean2,
        width,
        label=label2
    )

    ax.set_xticks(x)
    ax.set_xticklabels(metrics, rotation=30, ha="right")

    ax.set_xlabel("Métrica")
    ax.set_ylabel("Media")
    ax.set_title(f"{title} - Media")

    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend()

    plt.tight_layout()

    plt.savefig(
        os.path.join(output_dir, f"{title}_media.png"),
        dpi=300
    )

    plt.close()

    # =======================
    # VARIANZA
    # =======================

    fig, ax = plt.subplots(figsize=(12, 7))

    ax.bar(
        x - width / 2,
        var1,
        width,
        label=label1
    )

    ax.bar(
        x + width / 2,
        var2,
        width,
        label=label2
    )

    ax.set_xticks(x)
    ax.set_xticklabels(metrics, rotation=30, ha="right")

    ax.set_xlabel("Métrica")
    ax.set_ylabel("Varianza")
    ax.set_title(f"{title} - Varianza")

    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend()

    plt.tight_layout()

    plt.savefig(
        os.path.join(output_dir, f"{title}_varianza.png"),
        dpi=300
    )

    plt.close()




alpha = 0.05

def testEstadistico(file_1, name_file_1, file_2, name_file_2, output_file):
    dataset_1 = pd.read_csv(file_1)
    dataset_2 = pd.read_csv(file_2)

    metrics = [
        "faithfulness",
        "answer_relevancy",
        "context_recall",
        "context_precision"
    ]

    resultados = []

    for metric in metrics:

        data_1 = dataset_1[dataset_1["metric"] == metric].copy()
        data_2 = dataset_2[dataset_2["metric"] == metric].copy()

        ids_1 = set(data_1["question_id"])
        ids_2 = set(data_2["question_id"])

        faltan_en_1 = ids_2 - ids_1
        faltan_en_2 = ids_1 - ids_2

        ids_comunes = ids_1 & ids_2

        data_1 = data_1[data_1["question_id"].isin(ids_comunes)]
        data_2 = data_2[data_2["question_id"].isin(ids_comunes)]

        data_1 = data_1.sort_values("question_id").reset_index(drop=True)
        data_2 = data_2.sort_values("question_id").reset_index(drop=True)

        assert data_1["question_id"].equals(data_2["question_id"])

        vector_1 = data_1["value"].to_numpy()
        vector_2 = data_2["value"].to_numpy()

        stat, p = wilcoxon(vector_1, vector_2, zero_method="pratt")

        resultados.append({
            "metric": metric.replace("_", "\\_"),
            "mean1": vector_1.mean(),
            "mean2": vector_2.mean(),
            "W": stat,
            "p": p,
            "significant": "Sí" if p < alpha else "No"
        })

    # ============================
    # Guardar tabla LaTeX
    # ============================

    with open(output_file, "w", encoding="utf8") as f:

        f.write("\\begin{tabular}{lccccc}\n")
        f.write("\\toprule\n")
        f.write(
            f"Métrica & {name_file_1} & {name_file_2} & $W$ & $p$ & Sig.\\\\\n"
        )
        f.write("\\midrule\n")

        for r in resultados:

            f.write(
                f"{r['metric']} & "
                f"{r['mean1']:.4f} & "
                f"{r['mean2']:.4f} & "
                f"{r['W']:.1f} & "
                f"{r['p']:.4f} & "
                f"{r['significant']}\\\\\n"
            )

        f.write("\\bottomrule\n")
        f.write("\\end{tabular}\n")
