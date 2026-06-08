"""Create an interpretable heatmap for anomaly-cluster median features."""

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


def main() -> None:
    suffix = "_stabilized_log"
    tables_dir = ROOT / "Results" / "tables"
    figures_dir = ROOT / "Results" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    anomalies = pd.read_csv(tables_dir / f"clustered_anomaly_windows{suffix}.csv")
    heatmap_cols = [
        "supply_median",
        "return_median",
        "flow_median",
        "delta_t_median",
        "supply_temp_c_reconstruction_mse",
        "return_temp_c_reconstruction_mse",
        "stabilized_flow_log_feature_reconstruction_mse",
    ]
    heatmap_df = anomalies.groupby("anomaly_cluster")[heatmap_cols].median().sort_index()

    fig, ax = plt.subplots(figsize=(10, 4.8))
    im = ax.imshow(heatmap_df.to_numpy(), aspect="auto", cmap="viridis")
    ax.set_xticks(range(len(heatmap_cols)))
    ax.set_xticklabels(heatmap_cols, rotation=30, ha="right")
    ax.set_yticks(range(len(heatmap_df.index)))
    ax.set_yticklabels([str(i) for i in heatmap_df.index])
    ax.set_xlabel("Median feature in anomaly cluster")
    ax.set_ylabel("Anomaly cluster")
    ax.set_title("Anomaly-cluster feature heatmap (stabilized flow)")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Feature value")
    fig.tight_layout()
    out = figures_dir / "anomaly_cluster_feature_heatmap_stabilized_log.png"
    fig.savefig(out, dpi=160)
    plt.close(fig)
    print(f"Wrote figure: {out}")


if __name__ == "__main__":
    main()
