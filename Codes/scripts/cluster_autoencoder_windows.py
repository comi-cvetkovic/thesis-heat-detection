"""Cluster daily DHC windows using summary features derived from autoencoder inputs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Codes.scripts.prepare_autoencoder_windows import load_feature_frame, make_windows


DEFAULT_TARGETS = {
    "cons_abat_cisneros": ROOT / "Data" / "DHC network" / "data" / "District Heating_updated_16_07_2025_1.xlsx",
    "cons_abat_garriga": ROOT / "Data" / "DHC network" / "data" / "District Heating_updated_16_07_2025_1.xlsx",
    "cons_abat_marcet": ROOT / "Data" / "DHC network" / "data" / "District Heating_updated_16_07_2025_1.xlsx",
    "cons_abat_oliba": ROOT / "Data" / "DHC network" / "data" / "District Heating_updated_16_07_2025_2.xlsx",
    "cons_hostatgeria_underfloor_hea": ROOT / "Data" / "DHC network" / "data" / "District Heating_updated_16_07_2025_2.xlsx",
    "cons_hostatgeria_DHW_radiators": ROOT / "Data" / "DHC network" / "data" / "District Heating_updated_16_07_2025_2.xlsx",
    "cons_nostra_senyora": ROOT / "Data" / "DHC network" / "data" / "District Heating_updated_16_07_2025_2.xlsx",
}
DEFAULT_SHEETS = tuple(DEFAULT_TARGETS)


def clean_name(value: str) -> str:
    return value.lower().replace(" ", "_").replace("/", "_").replace("\\", "_")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, default=None)
    parser.add_argument("--sheets", nargs="+", default=list(DEFAULT_SHEETS))
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
    return parser.parse_args()


def build_window_feature_rows(args: argparse.Namespace) -> pd.DataFrame:
    steps_per_hour = pd.Timedelta(hours=1) / pd.Timedelta(args.resample_interval)
    window_steps = int(args.window_hours * steps_per_hour)
    stride_steps = int(args.stride_hours * steps_per_hour)
    rows: list[dict[str, object]] = []

    for sheet in args.sheets:
        workbook = args.workbook if args.workbook is not None else DEFAULT_TARGETS[sheet]
        feature_frame, feature_columns = load_feature_frame(
            workbook,
            sheet,
            args.resample_interval,
            args.flow_feature_mode,
            args.min_delta_t_c,
            args.flow_clip_quantile,
        )
        windows, starts = make_windows(
            feature_frame,
            feature_columns,
            feature_frame.index,
            window_steps,
            stride_steps,
            args.min_active_fraction,
            args.min_complete_fraction,
        )
        flow_feature_name = feature_columns[-1]
        scores_suffix = "" if args.flow_feature_mode == "raw" else f"_{args.flow_feature_mode}"
        scores_path = args.tables_dir / f"autoencoder_scores_{clean_name(sheet)}{scores_suffix}.csv"
        score_map: dict[pd.Timestamp, tuple[float, bool]] = {}
        if scores_path.exists():
            scores = pd.read_csv(scores_path, parse_dates=["window_start"])
            score_map = {
                pd.Timestamp(row.window_start): (float(row.reconstruction_mse), bool(row.is_reconstruction_anomaly))
                for row in scores.itertuples(index=False)
            }

        for window, start in zip(windows, starts, strict=True):
            start_ts = pd.Timestamp(start)
            supply = window[0]
            return_ = window[1]
            flow = window[2]
            delta_t = supply - return_
            active_slice = feature_frame.loc[(feature_frame.index >= start_ts) & (feature_frame.index < start_ts + pd.Timedelta(hours=args.window_hours)), "active_fraction"]
            reconstruction_mse, auto_flag = score_map.get(start_ts, (np.nan, False))
            rows.append(
                {
                    "sheet": sheet,
                    "window_start": start_ts,
                    "flow_feature_mode": args.flow_feature_mode,
                    "supply_median": float(np.median(supply)),
                    "supply_std": float(np.std(supply)),
                    "return_median": float(np.median(return_)),
                    "return_std": float(np.std(return_)),
                    "flow_median": float(np.median(flow)),
                    "flow_std": float(np.std(flow)),
                    "delta_t_median": float(np.median(delta_t)),
                    "delta_t_p05": float(np.quantile(delta_t, 0.05)),
                    "delta_t_min": float(np.min(delta_t)),
                    "active_fraction_mean": float(np.nanmean(active_slice.to_numpy(dtype=float))),
                    "reconstruction_mse": reconstruction_mse,
                    "is_reconstruction_anomaly": auto_flag,
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    args = parse_args()
    args.tables_dir.mkdir(parents=True, exist_ok=True)
    args.figures_dir.mkdir(parents=True, exist_ok=True)

    windows = build_window_feature_rows(args)
    feature_cols = [
        "supply_median",
        "supply_std",
        "return_median",
        "return_std",
        "flow_median",
        "flow_std",
        "delta_t_median",
        "delta_t_p05",
        "delta_t_min",
        "active_fraction_mean",
    ]

    scaler = StandardScaler()
    scaled = scaler.fit_transform(windows[feature_cols])
    kmeans = KMeans(n_clusters=args.clusters, n_init=20, random_state=42)
    windows["cluster"] = kmeans.fit_predict(scaled)
    windows["distance_to_center"] = np.linalg.norm(scaled - kmeans.cluster_centers_[windows["cluster"]], axis=1)

    cluster_summary = (
        windows.groupby("cluster", as_index=False)
        .agg(
            windows=("cluster", "size"),
            anomaly_windows=("is_reconstruction_anomaly", "sum"),
            anomaly_rate=("is_reconstruction_anomaly", "mean"),
            supply_median=("supply_median", "median"),
            return_median=("return_median", "median"),
            flow_median=("flow_median", "median"),
            delta_t_median=("delta_t_median", "median"),
            delta_t_p05=("delta_t_p05", "median"),
            active_fraction_mean=("active_fraction_mean", "median"),
        )
        .sort_values("cluster")
    )

    per_sheet = (
        windows.groupby(["sheet", "cluster"], as_index=False)
        .agg(
            windows=("cluster", "size"),
            anomaly_windows=("is_reconstruction_anomaly", "sum"),
            anomaly_rate=("is_reconstruction_anomaly", "mean"),
        )
        .sort_values(["sheet", "cluster"])
    )

    pca = PCA(n_components=2, random_state=42)
    projected = pca.fit_transform(scaled)
    windows["pca_1"] = projected[:, 0]
    windows["pca_2"] = projected[:, 1]

    suffix = "" if args.flow_feature_mode == "raw" else f"_{args.flow_feature_mode}"
    windows_path = args.tables_dir / f"clustered_windows{suffix}.csv"
    cluster_path = args.tables_dir / f"cluster_summary{suffix}.csv"
    per_sheet_path = args.tables_dir / f"cluster_sheet_summary{suffix}.csv"
    fig_path = args.figures_dir / f"cluster_pca_scatter{suffix}.png"
    windows.to_csv(windows_path, index=False)
    cluster_summary.to_csv(cluster_path, index=False)
    per_sheet.to_csv(per_sheet_path, index=False)

    fig, axis = plt.subplots(figsize=(10, 7))
    scatter = axis.scatter(windows["pca_1"], windows["pca_2"], c=windows["cluster"], cmap="tab10", s=14, alpha=0.7)
    anomalous = windows[windows["is_reconstruction_anomaly"]]
    axis.scatter(anomalous["pca_1"], anomalous["pca_2"], s=28, facecolors="none", edgecolors="black", linewidths=0.8)
    axis.set_title(f"Window clusters ({args.flow_feature_mode})")
    axis.set_xlabel("PCA 1")
    axis.set_ylabel("PCA 2")
    fig.colorbar(scatter, ax=axis, label="Cluster")
    fig.tight_layout()
    fig.savefig(fig_path, dpi=160)
    plt.close(fig)

    print(cluster_summary.to_string(index=False))
    print(f"\nWrote windows: {windows_path}")
    print(f"Wrote cluster summary: {cluster_path}")
    print(f"Wrote sheet summary: {per_sheet_path}")
    print(f"Wrote figure: {fig_path}")


if __name__ == "__main__":
    main()
