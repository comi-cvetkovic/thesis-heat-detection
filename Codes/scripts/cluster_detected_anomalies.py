"""Cluster only autoencoder-flagged anomaly windows into anomaly types."""

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
    parser.add_argument("--clusters", type=int, default=3)
    parser.add_argument("--tables-dir", type=Path, default=ROOT / "Results" / "tables")
    parser.add_argument("--figures-dir", type=Path, default=ROOT / "Results" / "figures")
    return parser.parse_args()


def build_anomaly_rows(args: argparse.Namespace) -> pd.DataFrame:
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
        if not scores_path.exists():
            continue

        scores = pd.read_csv(scores_path, parse_dates=["window_start"])
        scores = scores[scores["is_reconstruction_anomaly"]].copy()
        if scores.empty:
            continue

        score_map = {pd.Timestamp(row.window_start): row for row in scores.itertuples(index=False)}

        for window, start in zip(windows, starts, strict=True):
            start_ts = pd.Timestamp(start)
            if start_ts not in score_map:
                continue

            row = score_map[start_ts]
            supply = window[0]
            return_ = window[1]
            flow = window[2]
            delta_t = supply - return_
            active_slice = feature_frame.loc[
                (feature_frame.index >= start_ts) & (feature_frame.index < start_ts + pd.Timedelta(hours=args.window_hours)),
                "active_fraction",
            ]
            rows.append(
                {
                    "sheet": sheet,
                    "window_start": start_ts,
                    "split": row.split,
                    "flow_feature_mode": args.flow_feature_mode,
                    "reconstruction_mse": float(row.reconstruction_mse),
                    "dominant_anomalous_feature": str(row.dominant_anomalous_feature),
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
                    "supply_temp_c_reconstruction_mse": float(getattr(row, "supply_temp_c_reconstruction_mse")),
                    "return_temp_c_reconstruction_mse": float(getattr(row, "return_temp_c_reconstruction_mse")),
                    f"{flow_feature_name}_reconstruction_mse": float(
                        getattr(row, f"{flow_feature_name}_reconstruction_mse")
                    ),
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    args = parse_args()
    args.tables_dir.mkdir(parents=True, exist_ok=True)
    args.figures_dir.mkdir(parents=True, exist_ok=True)

    anomalies = build_anomaly_rows(args)
    if anomalies.empty:
        raise ValueError("No anomaly windows found for the requested sheets and flow mode.")

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
        "reconstruction_mse",
        "supply_temp_c_reconstruction_mse",
        "return_temp_c_reconstruction_mse",
        [col for col in anomalies.columns if col.endswith("_reconstruction_mse") and col not in ("supply_temp_c_reconstruction_mse", "return_temp_c_reconstruction_mse", "reconstruction_mse")][0],
    ]

    scaler = StandardScaler()
    scaled = scaler.fit_transform(anomalies[feature_cols])
    n_clusters = min(args.clusters, len(anomalies))
    if n_clusters < 2:
        raise ValueError("Need at least two anomaly windows to form clusters.")
    kmeans = KMeans(n_clusters=n_clusters, n_init=20, random_state=42)
    anomalies["anomaly_cluster"] = kmeans.fit_predict(scaled)
    anomalies["distance_to_center"] = np.linalg.norm(scaled - kmeans.cluster_centers_[anomalies["anomaly_cluster"]], axis=1)

    cluster_summary = (
        anomalies.groupby("anomaly_cluster", as_index=False)
        .agg(
            windows=("anomaly_cluster", "size"),
            sheets=("sheet", lambda values: ", ".join(sorted(pd.unique(values)))),
            dominant_feature_mode=("dominant_anomalous_feature", lambda values: pd.Series(values).mode().iloc[0]),
            reconstruction_mse_median=("reconstruction_mse", "median"),
            supply_median=("supply_median", "median"),
            return_median=("return_median", "median"),
            flow_median=("flow_median", "median"),
            delta_t_median=("delta_t_median", "median"),
            delta_t_min=("delta_t_min", "median"),
        )
        .sort_values("anomaly_cluster")
    )

    per_sheet = (
        anomalies.groupby(["sheet", "anomaly_cluster"], as_index=False)
        .agg(
            windows=("anomaly_cluster", "size"),
            dominant_feature_mode=("dominant_anomalous_feature", lambda values: pd.Series(values).mode().iloc[0]),
            reconstruction_mse_median=("reconstruction_mse", "median"),
        )
        .sort_values(["sheet", "anomaly_cluster"])
    )

    dominant_feature_counts = (
        anomalies.groupby(["anomaly_cluster", "dominant_anomalous_feature"], as_index=False)
        .size()
        .rename(columns={"size": "windows"})
        .sort_values(["anomaly_cluster", "windows"], ascending=[True, False])
    )

    pca = PCA(n_components=2, random_state=42)
    projected = pca.fit_transform(scaled)
    anomalies["pca_1"] = projected[:, 0]
    anomalies["pca_2"] = projected[:, 1]

    suffix = "" if args.flow_feature_mode == "raw" else f"_{args.flow_feature_mode}"
    windows_path = args.tables_dir / f"clustered_anomaly_windows{suffix}.csv"
    cluster_path = args.tables_dir / f"anomaly_cluster_summary{suffix}.csv"
    per_sheet_path = args.tables_dir / f"anomaly_cluster_sheet_summary{suffix}.csv"
    dominant_path = args.tables_dir / f"anomaly_cluster_dominant_feature_summary{suffix}.csv"
    fig_path = args.figures_dir / f"anomaly_cluster_pca_scatter{suffix}.png"

    anomalies.to_csv(windows_path, index=False)
    cluster_summary.to_csv(cluster_path, index=False)
    per_sheet.to_csv(per_sheet_path, index=False)
    dominant_feature_counts.to_csv(dominant_path, index=False)

    fig, axis = plt.subplots(figsize=(10, 7))
    scatter = axis.scatter(
        anomalies["pca_1"],
        anomalies["pca_2"],
        c=anomalies["anomaly_cluster"],
        cmap="tab10",
        s=45,
        alpha=0.85,
    )
    for row in anomalies.itertuples(index=False):
        axis.annotate(row.sheet.replace("cons_", ""), (row.pca_1, row.pca_2), fontsize=7, alpha=0.8)
    axis.set_title(f"Detected anomaly clusters ({args.flow_feature_mode})")
    axis.set_xlabel("PCA 1")
    axis.set_ylabel("PCA 2")
    fig.colorbar(scatter, ax=axis, label="Anomaly cluster")
    fig.tight_layout()
    fig.savefig(fig_path, dpi=160)
    plt.close(fig)

    print(cluster_summary.to_string(index=False))
    print(f"\nWrote anomaly windows: {windows_path}")
    print(f"Wrote cluster summary: {cluster_path}")
    print(f"Wrote sheet summary: {per_sheet_path}")
    print(f"Wrote dominant-feature summary: {dominant_path}")
    print(f"Wrote figure: {fig_path}")


if __name__ == "__main__":
    main()
