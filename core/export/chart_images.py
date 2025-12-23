import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

def render_chart_to_image(
    df: pd.DataFrame,
    chart_type: str,
    output_path: Path,
):
    plt.figure(figsize=(6, 4))

    if chart_type == "line":
        x = df.iloc[:, 0]
        y = df.iloc[:, 1]
        plt.plot(x, y)
        plt.xticks(rotation=45)

    elif chart_type == "bar":
        x = df.iloc[:, 0]
        y = df.iloc[:, 1]
        plt.bar(x, y)
        plt.xticks(rotation=45)

    else:
        return None

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

    return output_path