"""Create more interpretable anomaly-cluster visuals than PCA scatter alone."""

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

from Codes.scripts.prepare_autoencoder_windows import DEFAULT_WORKBOOK, load_feature_frame
from Codes.scripts.inspect_autoencoder_windows import load_baseline_frame


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--flow-feature-mode", choices=["raw", "stabilized_log"], default="stabilized_log")
    parser.add_argument("--workbook", type=Path, default=DEFAULT_WORKBOOK)
    parser.add_argument("--resample-interval", default="15min")
    parser.add_argument("--window-hours", type=int, default=24)
    parser.add_argument("--min-delta-t-c", type=float, default=2.0)
    parser.add_argument("--flow-clip-quantile", type=float, default=0.995)
    parser.add_argument("--tables-dir", type=Path, default=ROOT / "Results" / "tables")
    parser.add_argument("--figures-dir", type=Path, default=ROOT / "Results" / "figures")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.figures_dir.mkdir(parents=True, exist_ok=True)
    suffix = "" if args.flow_feature_mode == "raw" else f"_{args.flow_feature_mode}"

    anomalies = pd.read_csv(args.tables_dir / f"clustered_anomaly_windows{suffix}.csv", parse_dates=["window_start"])

    # Heatmap of cluster medians on interpretable variables.
    heatmap_cols = [
        "supply_median",
        "return_median",
        "flow_median",
        "delta_t_median",
        "supply_temp_c_reconstruction_mse",
        "return_temp_c_reconstruction_mse",
        [col for col in anomalies.columns if col.endswith("_reconstruction_mse") and col not in ("reconstruction_mse", "supply_temp_c_reconstruction_mse", "return_temp_c_reconstruction_mse")][0],
    ]
    heatmap_df = anomalies.groupby("anomaly_cluster")[heatmap_cols].median().sort_index()

    fig, ax = plt.subplots(figsize=(10, 4.8))
    im = ax.imshow(heatmap_df.to_numpy(), aspect="auto", cmap="viridis")
    ax.set_xticks(np.arange(len(heatmap_cols)))
    ax.set_xticklabels(heatmap_cols, rotation=30, ha="right")
    ax.set_yticks(np.arange(len(heatmap_df.index)))
    ax.set_yticklabels([str(idx) for idx in heatmap_df.index])
    ax.set_xlabel("Median feature in anomaly cluster")
    ax.set_ylabel("Anomaly cluster")
    ax.set_title(f"Anomaly-cluster feature heatmap ({args.flow_feature_mode})")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Feature value")
    fig.tight_layout()
    heatmap_path = args.figures_dir / f"anomaly_cluster_feature_heatmap{suffix}.png"
    fig.savefig(heatmap_path, dpi=160)
    plt.close(fig)

    # Representative window per anomaly cluster: pick highest reconstruction mse in each cluster.
    reps = anomalies.sort_values(["anomaly_cluster", "reconstruction_mse"], ascending=[True, False]).groupby("anomaly_cluster", as_index=False).head(1)
    reps = reps.sort_values("anomaly_cluster")

    n = len(reps)
    fig, axes = plt.subplots(n, 4, figsize=(14, 3.8 * n), sharex=False)
    if n == 1:
        axes = np.array([axes])

    for row_idx, row in enumerate(reps.itertuples(index=False)):
        feature_frame, feature_columns = load_feature_frame(
            args.workbook,
            row.sheet,
            args.resample_interval,
            args.flow_feature_mode,
            args.min_delta_t_c,
            args.flow_clip_quantile,
        )
        baseline_frame = load_baseline_frame(args.workbook, row.sheet).set_index("Time stamp")
        flow_feature_name = feature_columns[-1]
        start = row.window_start
        end = start + pd.Timedelta(hours=args.window_hours)
        window_features = feature_frame.loc[(feature_frame.index >= start) & (feature_frame.index < end)]
        window_baseline = baseline_frame.loc[(baseline_frame.index >= start) & (baseline_frame.index < end)]

        axes[row_idx, 0].plot(window_features.index, window_features["supply_temp_c"], linewidth=0.9)
        axes[row_idx, 0].set_ylabel(f"Cluster {row.anomaly_cluster}\nSupply C")
        axes[row_idx, 1].plot(window_features.index, window_features["return_temp_c"], linewidth=0.9, color="tab:green")
        axes[row_idx, 1].set_ylabel("Return C")
        axes[row_idx, 2].plot(window_features.index, window_features[flow_feature_name], linewidth=0.9, color="tab:purple")
        axes[row_idx, 2].set_ylabel(flow_feature_name)
        axes[row_idx, 3].plot(window_baseline.index, window_baseline["delta_t_c"], linewidth=0.9, color="tab:orange")
        overlapping = window_baseline[window_baseline["is_low_delta_t_anomaly"].fillna(False)]
        if not overlapping.empty:
            axes[row_idx, 3].scatter(overlapping.index, overlapping["delta_t_c"], s=16, color="tab:red")
        axes[row_idx, 3].set_ylabel("Delta-T C")

        title = (
            f"{row.sheet} | {start:%Y-%m-%d %H:%M}\n"
            f"mse={row.reconstruction_mse:.3f} | dominant={row.dominant_anomalous_feature}"
        )
        axes[row_idx, 0].set_title(title, fontsize=10)

    for col in range(4):
        axes[-1, col].set_xlabel("Timestamp")
    fig.tight_layout()
    reps_path = args.figures_dir / f"anomaly_cluster_representative_windows{suffix}.png"
    fig.savefig(reps_path, dpi=160)
    plt.close(fig)

    print(f"Wrote figures: {heatmap_path}, {reps_path}")


if __name__ == "__main__":
    main()
