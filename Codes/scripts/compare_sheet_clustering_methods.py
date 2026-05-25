"""Compare feature-space and latent-space clustering for one sheet."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Codes.scripts.prepare_autoencoder_windows import DEFAULT_WORKBOOK, clean_name, load_feature_frame, make_windows
from Codes.src.autoencoder import Conv1dAutoencoder


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sheet", default="cons_hostatgeria_underfloor_hea")
    parser.add_argument("--workbook", type=Path, default=DEFAULT_WORKBOOK)
    parser.add_argument("--resample-interval", default="15min")
    parser.add_argument("--window-hours", type=int, default=24)
    parser.add_argument("--stride-hours", type=int, default=12)
    parser.add_argument("--flow-feature-mode", choices=["raw", "stabilized_log"], default="stabilized_log")
    parser.add_argument("--min-delta-t-c", type=float, default=2.0)
    parser.add_argument("--flow-clip-quantile", type=float, default=0.995)
    parser.add_argument("--min-active-fraction", type=float, default=0.6)
    parser.add_argument("--min-complete-fraction", type=float, default=0.85)
    parser.add_argument("--clusters", type=int, default=4)
    parser.add_argument("--tables-dir", type=Path, default=ROOT / "Results" / "tables")
    parser.add_argument("--figures-dir", type=Path, default=ROOT / "Results" / "figures")
    parser.add_argument("--models-dir", type=Path, default=ROOT / "Results" / "models")
    return parser.parse_args()


def cluster_and_summarize(
    matrix: np.ndarray,
    windows: pd.DataFrame,
    prefix: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    scaler = StandardScaler()
    scaled = scaler.fit_transform(matrix)
    kmeans = KMeans(n_clusters=args.clusters, n_init=20, random_state=42)
    labels = kmeans.fit_predict(scaled)
    windows = windows.copy()
    windows["cluster"] = labels
    windows["distance_to_center"] = np.linalg.norm(scaled - kmeans.cluster_centers_[labels], axis=1)

    summary = (
        windows.groupby("cluster", as_index=False)
        .agg(
            windows=("cluster", "size"),
            anomaly_windows=("is_reconstruction_anomaly", "sum"),
            anomaly_rate=("is_reconstruction_anomaly", "mean"),
            reconstruction_mse_median=("reconstruction_mse", "median"),
            distance_to_center_median=("distance_to_center", "median"),
        )
        .sort_values("cluster")
    )

    pca = PCA(n_components=2, random_state=42)
    projected = pca.fit_transform(scaled)
    windows[f"{prefix}_pca_1"] = projected[:, 0]
    windows[f"{prefix}_pca_2"] = projected[:, 1]

    metrics = pd.DataFrame(
        [
            {
                "method": prefix,
                "clusters": args.clusters,
                "silhouette_score": silhouette_score(scaled, labels) if len(np.unique(labels)) > 1 else np.nan,
                "anomaly_clusters_used": int(windows.loc[windows["is_reconstruction_anomaly"], "cluster"].nunique()),
                "max_cluster_anomaly_rate": float(summary["anomaly_rate"].max()),
            }
        ]
    )
    return windows, summary, metrics


def build_feature_summary(
    windows_np: np.ndarray,
    starts: pd.DatetimeIndex,
    feature_names: list[str],
    scores: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    score_map = {
        pd.Timestamp(row.window_start): (float(row.reconstruction_mse), bool(row.is_reconstruction_anomaly), str(row.split))
        for row in scores.itertuples(index=False)
    }
    for window, start in zip(windows_np, starts, strict=True):
        start_ts = pd.Timestamp(start)
        row: dict[str, object] = {"window_start": start_ts}
        for idx, name in enumerate(feature_names):
            values = window[idx]
            row[f"{name}_median"] = float(np.median(values))
            row[f"{name}_std"] = float(np.std(values))
        delta_t = window[0] - window[1]
        row["delta_t_median"] = float(np.median(delta_t))
        row["delta_t_p05"] = float(np.quantile(delta_t, 0.05))
        row["delta_t_min"] = float(np.min(delta_t))
        reconstruction_mse, is_anomaly, split = score_map[start_ts]
        row["reconstruction_mse"] = reconstruction_mse
        row["is_reconstruction_anomaly"] = is_anomaly
        row["split"] = split
        rows.append(row)
    return pd.DataFrame(rows)


def make_scatter(windows: pd.DataFrame, prefix: str, figure_path: Path) -> None:
    fig, axis = plt.subplots(figsize=(9, 7))
    scatter = axis.scatter(
        windows[f"{prefix}_pca_1"],
        windows[f"{prefix}_pca_2"],
        c=windows["cluster"],
        cmap="tab10",
        s=18,
        alpha=0.75,
    )
    anomalous = windows[windows["is_reconstruction_anomaly"]]
    axis.scatter(
        anomalous[f"{prefix}_pca_1"],
        anomalous[f"{prefix}_pca_2"],
        s=36,
        facecolors="none",
        edgecolors="black",
        linewidths=0.8,
    )
    axis.set_title(f"{args.sheet}: {prefix} clustering")
    axis.set_xlabel("PCA 1")
    axis.set_ylabel("PCA 2")
    fig.colorbar(scatter, ax=axis, label="Cluster")
    fig.tight_layout()
    fig.savefig(figure_path, dpi=160)
    plt.close(fig)


def main() -> None:
    global args
    args = parse_args()
    args.tables_dir.mkdir(parents=True, exist_ok=True)
    args.figures_dir.mkdir(parents=True, exist_ok=True)

    slug = clean_name(args.sheet)
    suffix = "" if args.flow_feature_mode == "raw" else f"_{args.flow_feature_mode}"
    windows_path = ROOT / "Results" / "processed_data" / f"autoencoder_windows_{slug}{suffix}.npz"
    model_path = args.models_dir / f"autoencoder_{slug}{suffix}.pt"
    scores_path = args.tables_dir / f"autoencoder_scores_{slug}{suffix}.csv"

    data = np.load(windows_path, allow_pickle=True)
    windows_np = data["windows"].astype(np.float32)
    starts = pd.to_datetime(data["window_start"])
    feature_names = [str(value) for value in data["feature_names"]]
    scores = pd.read_csv(scores_path, parse_dates=["window_start"])

    base_windows = build_feature_summary(windows_np, starts, feature_names, scores)
    feature_matrix = base_windows[
        [col for col in base_windows.columns if col.endswith("_median") or col.endswith("_std") or col.startswith("delta_t_")]
    ].to_numpy(dtype=np.float32)

    feature_windows, feature_summary, feature_metrics = cluster_and_summarize(feature_matrix, base_windows, "feature")

    model = Conv1dAutoencoder(channels=windows_np.shape[1])
    checkpoint = torch.load(model_path, map_location="cpu", weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    with torch.no_grad():
        latent = model.encode(torch.from_numpy(windows_np)).cpu().numpy()
    latent_matrix = latent.reshape(latent.shape[0], -1)
    latent_windows, latent_summary, latent_metrics = cluster_and_summarize(latent_matrix, base_windows, "latent")

    comparison = pd.concat([feature_metrics, latent_metrics], ignore_index=True)
    feature_summary_path = args.tables_dir / f"feature_cluster_summary_{slug}{suffix}.csv"
    latent_summary_path = args.tables_dir / f"latent_cluster_summary_{slug}{suffix}.csv"
    comparison_path = args.tables_dir / f"clustering_method_comparison_{slug}{suffix}.csv"
    feature_scatter_path = args.figures_dir / f"feature_cluster_scatter_{slug}{suffix}.png"
    latent_scatter_path = args.figures_dir / f"latent_cluster_scatter_{slug}{suffix}.png"

    feature_summary.to_csv(feature_summary_path, index=False)
    latent_summary.to_csv(latent_summary_path, index=False)
    comparison.to_csv(comparison_path, index=False)
    make_scatter(feature_windows, "feature", feature_scatter_path)
    make_scatter(latent_windows, "latent", latent_scatter_path)

    print(comparison.to_string(index=False))
    print(f"\nWrote feature summary: {feature_summary_path}")
    print(f"Wrote latent summary: {latent_summary_path}")
    print(f"Wrote comparison: {comparison_path}")
    print(f"Wrote figures: {feature_scatter_path}, {latent_scatter_path}")


if __name__ == "__main__":
    main()
