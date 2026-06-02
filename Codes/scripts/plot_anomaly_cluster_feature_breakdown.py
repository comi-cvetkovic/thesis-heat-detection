"""Plot direct feature-based summaries for anomaly clusters."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--flow-feature-mode", choices=["raw", "stabilized_log"], default="stabilized_log")
    parser.add_argument("--tables-dir", type=Path, default=ROOT / "Results" / "tables")
    parser.add_argument("--figures-dir", type=Path, default=ROOT / "Results" / "figures")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.figures_dir.mkdir(parents=True, exist_ok=True)
    suffix = "" if args.flow_feature_mode == "raw" else f"_{args.flow_feature_mode}"

    anomalies = pd.read_csv(args.tables_dir / f"clustered_anomaly_windows{suffix}.csv")
    dominant = pd.read_csv(args.tables_dir / f"anomaly_cluster_dominant_feature_summary{suffix}.csv")

    # Figure 1: stacked composition of dominant anomalous feature by anomaly cluster.
    pivot = (
        dominant.pivot(index="anomaly_cluster", columns="dominant_anomalous_feature", values="windows")
        .fillna(0)
        .sort_index()
    )
    feature_order = [col for col in ["supply_temp_c", "return_temp_c", "stabilized_flow_log_feature", "derived_flow_kg_s"] if col in pivot.columns]
    pivot = pivot.reindex(columns=feature_order)

    fig, axis = plt.subplots(figsize=(9, 5))
    bottom = np.zeros(len(pivot))
    colors = {
        "supply_temp_c": "tab:blue",
        "return_temp_c": "tab:green",
        "stabilized_flow_log_feature": "tab:purple",
        "derived_flow_kg_s": "tab:purple",
    }
    for col in pivot.columns:
        axis.bar(
            pivot.index.astype(str),
            pivot[col].to_numpy(),
            bottom=bottom,
            label=col,
            color=colors.get(col, None),
        )
        bottom += pivot[col].to_numpy()
    axis.set_title(f"Anomaly cluster composition by dominant feature ({args.flow_feature_mode})")
    axis.set_xlabel("Anomaly cluster")
    axis.set_ylabel("Windows")
    axis.legend(loc="best")
    fig.tight_layout()
    composition_path = args.figures_dir / f"anomaly_cluster_feature_composition{suffix}.png"
    fig.savefig(composition_path, dpi=160)
    plt.close(fig)

    # Figure 2: median per-feature reconstruction MSE by anomaly cluster.
    mse_cols = [col for col in anomalies.columns if col.endswith("_reconstruction_mse") and col != "reconstruction_mse"]
    mse_summary = anomalies.groupby("anomaly_cluster", as_index=False)[mse_cols].median().sort_values("anomaly_cluster")
    x = np.arange(len(mse_summary))
    width = 0.25 if len(mse_cols) >= 3 else 0.35

    fig, axis = plt.subplots(figsize=(10, 5))
    offsets = np.linspace(-(len(mse_cols) - 1) / 2, (len(mse_cols) - 1) / 2, len(mse_cols)) * width
    for offset, col in zip(offsets, mse_cols, strict=True):
        axis.bar(x + offset, mse_summary[col].to_numpy(), width=width, label=col)
    axis.set_xticks(x)
    axis.set_xticklabels(mse_summary["anomaly_cluster"].astype(str))
    axis.set_xlabel("Anomaly cluster")
    axis.set_ylabel("Median reconstruction MSE")
    axis.set_title(f"Median per-feature reconstruction error by anomaly cluster ({args.flow_feature_mode})")
    axis.legend(loc="best")
    fig.tight_layout()
    mse_path = args.figures_dir / f"anomaly_cluster_feature_mse{suffix}.png"
    fig.savefig(mse_path, dpi=160)
    plt.close(fig)

    print(f"Wrote figures: {composition_path}, {mse_path}")


if __name__ == "__main__":
    main()
