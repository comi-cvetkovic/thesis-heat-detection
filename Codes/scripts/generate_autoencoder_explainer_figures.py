"""Generate simple explainer figures for the supervisor update."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def draw_concept_diagram(output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 3.6))
    ax.axis("off")

    boxes = [
        (0.05, 0.34, 0.16, 0.32, "Input window\n3 channels x 96 steps"),
        (0.28, 0.34, 0.16, 0.32, "Encoder\nConv + Pool"),
        (0.51, 0.34, 0.16, 0.32, "Latent\nrepresentation"),
        (0.74, 0.34, 0.16, 0.32, "Decoder\nTranspose Conv"),
    ]
    for x, y, w, h, label in boxes:
        rect = plt.Rectangle((x, y), w, h, fill=False, linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=11)

    ax.annotate("", xy=(0.28, 0.5), xytext=(0.21, 0.5), arrowprops=dict(arrowstyle="->", lw=1.6))
    ax.annotate("", xy=(0.51, 0.5), xytext=(0.44, 0.5), arrowprops=dict(arrowstyle="->", lw=1.6))
    ax.annotate("", xy=(0.74, 0.5), xytext=(0.67, 0.5), arrowprops=dict(arrowstyle="->", lw=1.6))

    # reconstruction branch
    rect = plt.Rectangle((0.74, 0.06), 0.16, 0.18, fill=False, linewidth=1.5)
    ax.add_patch(rect)
    ax.text(0.82, 0.15, "Reconstructed\nwindow", ha="center", va="center", fontsize=11)

    ax.annotate("", xy=(0.82, 0.24), xytext=(0.82, 0.34), arrowprops=dict(arrowstyle="->", lw=1.6))
    ax.annotate("", xy=(0.13, 0.24), xytext=(0.74, 0.15), arrowprops=dict(arrowstyle="-", lw=1.2, linestyle="--"))
    ax.text(0.43, 0.11, "Compare original vs reconstructed window\nReconstruction error = anomaly score", ha="center", va="center", fontsize=10)

    ax.set_title("Autoencoder concept used in this project", fontsize=13)
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def draw_training_history(history_csv: Path, output_path: Path, title: str) -> None:
    history = pd.read_csv(history_csv)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(history["epoch"], history["train_loss"], marker="o", linewidth=1.8)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Training loss (MSE)")
    ax.set_title(title)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def main() -> None:
    figures_dir = ROOT / "Results" / "figures"
    tables_dir = ROOT / "Results" / "tables"
    figures_dir.mkdir(parents=True, exist_ok=True)

    draw_concept_diagram(figures_dir / "autoencoder_concept_diagram.png")
    draw_training_history(
        tables_dir / "autoencoder_training_history_cons_hostatgeria_underfloor_hea_stabilized_log.csv",
        figures_dir / "autoencoder_training_history_cons_hostatgeria_underfloor_hea_stabilized_log.png",
        "Training loss: underfloor heating joint autoencoder (stabilized flow)",
    )


if __name__ == "__main__":
    main()
