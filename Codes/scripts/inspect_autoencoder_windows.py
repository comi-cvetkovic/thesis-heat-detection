"""Inspect flagged autoencoder windows against raw signals and delta-T anomalies."""

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

from Codes.scripts.prepare_autoencoder_windows import (
    DEFAULT_WORKBOOK,
    BASE_FEATURES,
    POWER_COL,
    RETURN_COL,
    SUPPLY_COL,
    TIMESTAMP_COL,
    clean_name,
    load_feature_frame,
    resolve_flow_feature_name,
)
from Codes.src.features import add_delta_t


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sheet", default="cons_hostatgeria_underfloor_hea")
    parser.add_argument("--workbook", type=Path, default=DEFAULT_WORKBOOK)
    parser.add_argument(
        "--scores",
        type=Path,
        default=ROOT / "Results" / "tables" / "autoencoder_scores_cons_hostatgeria_underfloor_hea.csv",
    )
    parser.add_argument("--resample-interval", default="15min")
    parser.add_argument("--window-hours", type=int, default=24)
    parser.add_argument("--flow-feature-mode", choices=["raw", "stabilized_log"], default="raw")
    parser.add_argument("--min-delta-t-c", type=float, default=2.0)
    parser.add_argument("--flow-clip-quantile", type=float, default=0.995)
    parser.add_argument("--top-k", type=int, default=6)
    parser.add_argument("--tables-dir", type=Path, default=ROOT / "Results" / "tables")
    parser.add_argument("--figures-dir", type=Path, default=ROOT / "Results" / "figures")
    return parser.parse_args()


def load_baseline_frame(workbook: Path, sheet: str) -> pd.DataFrame:
    frame = pd.read_excel(workbook, sheet_name=sheet).dropna(how="all")
    frame[TIMESTAMP_COL] = pd.to_datetime(frame[TIMESTAMP_COL], errors="coerce", dayfirst=True)
    frame = frame.dropna(subset=[TIMESTAMP_COL]).sort_values(TIMESTAMP_COL).reset_index(drop=True)
    frame = add_delta_t(frame, supply_col=SUPPLY_COL, return_col=RETURN_COL)
    frame["power_kw"] = pd.to_numeric(frame[POWER_COL], errors="coerce")
    frame["is_active_heating"] = (frame["power_kw"] > 0) & (frame["delta_t_c"] > 0)
    active_delta = frame.loc[frame["is_active_heating"], "delta_t_c"].astype(float)
    median = active_delta.median()
    mad = (active_delta - median).abs().median()
    if pd.isna(mad) or mad == 0:
        frame["active_delta_t_modified_z"] = np.nan
    else:
        frame["active_delta_t_modified_z"] = np.nan
        z = 0.6745 * (active_delta - median) / mad
        frame.loc[frame["is_active_heating"], "active_delta_t_modified_z"] = z
    frame["is_low_delta_t_anomaly"] = frame["active_delta_t_modified_z"] <= -3.5
    return frame


def main() -> None:
    args = parse_args()
    slug = clean_name(args.sheet)
    scores = pd.read_csv(args.scores, parse_dates=["window_start"])
    feature_frame, feature_columns = load_feature_frame(
        args.workbook,
        args.sheet,
        args.resample_interval,
        args.flow_feature_mode,
        args.min_delta_t_c,
        args.flow_clip_quantile,
    )
    flow_feature_name = feature_columns[-1]
    baseline_frame = load_baseline_frame(args.workbook, args.sheet)
    baseline_frame = baseline_frame.set_index(TIMESTAMP_COL)

    flagged = scores[scores["is_reconstruction_anomaly"]].sort_values("reconstruction_mse", ascending=False).head(
        args.top_k
    )
    if flagged.empty:
        raise ValueError("No flagged windows found in the supplied scores file.")

    window_delta = pd.Timedelta(hours=args.window_hours)
    inspection_rows: list[dict[str, object]] = []
    args.figures_dir.mkdir(parents=True, exist_ok=True)
    args.tables_dir.mkdir(parents=True, exist_ok=True)

    for rank, row in enumerate(flagged.itertuples(index=False), start=1):
        start = row.window_start
        end = start + window_delta
        window_features = feature_frame.loc[(feature_frame.index >= start) & (feature_frame.index < end)]
        window_baseline = baseline_frame.loc[(baseline_frame.index >= start) & (baseline_frame.index < end)]
        low_delta_count = int(window_baseline["is_low_delta_t_anomaly"].fillna(False).sum())
        inspection_rows.append(
            {
                "rank": rank,
                "window_start": start,
                "window_end": end,
                "split": row.split,
                "reconstruction_mse": row.reconstruction_mse,
                "dominant_anomalous_feature": getattr(row, "dominant_anomalous_feature", ""),
                "resampled_points": len(window_features),
                "median_supply_temp_c": window_features["supply_temp_c"].median(),
                "median_return_temp_c": window_features["return_temp_c"].median(),
                f"median_{flow_feature_name}": window_features[flow_feature_name].median(),
                "supply_temp_c_reconstruction_mse": getattr(row, "supply_temp_c_reconstruction_mse", np.nan),
                "return_temp_c_reconstruction_mse": getattr(row, "return_temp_c_reconstruction_mse", np.nan),
                f"{flow_feature_name}_reconstruction_mse": getattr(
                    row,
                    f"{flow_feature_name}_reconstruction_mse",
                    np.nan,
                ),
                "median_delta_t_c": window_baseline["delta_t_c"].median(),
                "min_delta_t_c": window_baseline["delta_t_c"].min(),
                "low_delta_t_anomaly_points": low_delta_count,
                "has_low_delta_t_overlap": low_delta_count > 0,
            }
        )

        fig, axes = plt.subplots(4, 1, figsize=(12, 9), sharex=True)
        axes[0].plot(window_features.index, window_features["supply_temp_c"], linewidth=0.8)
        axes[0].set_ylabel("Supply C")
        axes[1].plot(window_features.index, window_features["return_temp_c"], linewidth=0.8, color="tab:green")
        axes[1].set_ylabel("Return C")
        axes[2].plot(window_features.index, window_features[flow_feature_name], linewidth=0.8, color="tab:purple")
        axes[2].set_ylabel(flow_feature_name)
        axes[3].plot(window_baseline.index, window_baseline["delta_t_c"], linewidth=0.8, color="tab:orange")
        overlapping = window_baseline[window_baseline["is_low_delta_t_anomaly"].fillna(False)]
        if not overlapping.empty:
            axes[3].scatter(overlapping.index, overlapping["delta_t_c"], s=15, color="tab:red")
        axes[3].set_ylabel("Delta-T C")
        axes[3].set_xlabel("Timestamp")
        fig.suptitle(
            f"{args.sheet} window {rank}: {start:%Y-%m-%d %H:%M} mse={row.reconstruction_mse:.3f}",
            fontsize=11,
        )
        fig.autofmt_xdate()
        fig.tight_layout()
        output_suffix = "" if args.flow_feature_mode == "raw" else f"_{args.flow_feature_mode}"
        figure_path = args.figures_dir / f"inspect_autoencoder_{slug}{output_suffix}_{rank:02d}.png"
        fig.savefig(figure_path, dpi=160)
        plt.close(fig)

    inspection = pd.DataFrame(inspection_rows)
    output_suffix = "" if args.flow_feature_mode == "raw" else f"_{args.flow_feature_mode}"
    summary_path = args.tables_dir / f"inspect_autoencoder_{slug}{output_suffix}_summary.csv"
    inspection.to_csv(summary_path, index=False)
    print(inspection.to_string(index=False))
    print(f"\nWrote summary: {summary_path}")


if __name__ == "__main__":
    main()
