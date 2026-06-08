"""Create clearer diagnostic plots for autoencoder reconstruction error."""

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
    parser.add_argument("--sheet", default="cons_hostatgeria_underfloor_hea")
    parser.add_argument("--flow-feature-mode", choices=["raw", "stabilized_log"], default="stabilized_log")
    parser.add_argument("--gap-hours", type=float, default=72.0)
    parser.add_argument("--tables-dir", type=Path, default=ROOT / "Results" / "tables")
    parser.add_argument("--figures-dir", type=Path, default=ROOT / "Results" / "figures")
    return parser.parse_args()


def clean_name(value: str) -> str:
    return value.lower().replace(" ", "_").replace("/", "_").replace("\\", "_")


def main() -> None:
    args = parse_args()
    args.figures_dir.mkdir(parents=True, exist_ok=True)
    suffix = "" if args.flow_feature_mode == "raw" else f"_{args.flow_feature_mode}"
    slug = clean_name(args.sheet)
    scores_path = args.tables_dir / f"autoencoder_scores_{slug}{suffix}.csv"
    summary_path = args.tables_dir / f"autoencoder_summary_{slug}{suffix}.csv"

    scores = pd.read_csv(scores_path, parse_dates=["window_start"]).sort_values("window_start").reset_index(drop=True)
    summary = pd.read_csv(summary_path).iloc[0]
    threshold = float(summary["threshold_value"]) if "threshold_value" in summary.index else float(summary["threshold_train_p99"])
    threshold_method = str(summary["threshold_method"]) if "threshold_method" in summary.index else "train_p99"
    threshold_label = "Train mean + 3 sigma" if threshold_method == "train_3sigma" else "Train p99 threshold"

    # Gap-aware time series: break line where windows are not contiguous enough.
    gap = pd.Timedelta(hours=args.gap_hours)
    plot_df = scores[["window_start", "reconstruction_mse"]].copy()
    diffs = plot_df["window_start"].diff()
    insert_rows: list[dict[str, object]] = []
    for idx, value in enumerate(diffs):
        if idx == 0 or pd.isna(value) or value <= gap:
            continue
        insert_rows.append({"position": idx, "window_start": pd.NaT, "reconstruction_mse": np.nan})

    if insert_rows:
        pieces = []
        last = 0
        for row in insert_rows:
            pieces.append(plot_df.iloc[last : row["position"]])
            pieces.append(pd.DataFrame([{"window_start": pd.NaT, "reconstruction_mse": np.nan}]))
            last = row["position"]
        pieces.append(plot_df.iloc[last:])
        gap_plot_df = pd.concat(pieces, ignore_index=True)
    else:
        gap_plot_df = plot_df

    fig, axis = plt.subplots(figsize=(12, 5))
    axis.plot(gap_plot_df["window_start"], gap_plot_df["reconstruction_mse"], linewidth=1.0, label="Reconstruction MSE")
    flagged = scores[scores["is_reconstruction_anomaly"]]
    axis.scatter(flagged["window_start"], flagged["reconstruction_mse"], s=24, color="tab:red", label="Flagged window")
    axis.axhline(threshold, color="tab:orange", linestyle="--", linewidth=1.1, label=threshold_label)
    axis.set_title(f"Gap-aware reconstruction error: {slug}{suffix}")
    axis.set_xlabel("Window start")
    axis.set_ylabel("MSE")
    axis.legend(loc="best")
    fig.autofmt_xdate()
    fig.tight_layout()
    gap_path = args.figures_dir / f"autoencoder_reconstruction_error_gapaware_{slug}{suffix}.png"
    fig.savefig(gap_path, dpi=160)
    plt.close(fig)

    # Train vs test distributions.
    fig, axis = plt.subplots(figsize=(8, 5))
    train = scores.loc[scores["split"] == "train", "reconstruction_mse"].to_numpy()
    test = scores.loc[scores["split"] == "test", "reconstruction_mse"].to_numpy()
    bins = np.histogram_bin_edges(scores["reconstruction_mse"], bins="auto")
    axis.hist(train, bins=bins, alpha=0.65, label="Train", color="tab:blue")
    axis.hist(test, bins=bins, alpha=0.55, label="Test", color="tab:green")
    axis.axvline(threshold, color="tab:orange", linestyle="--", linewidth=1.1, label=threshold_label)
    axis.set_title(f"Reconstruction error distribution: {slug}{suffix}")
    axis.set_xlabel("Reconstruction MSE")
    axis.set_ylabel("Windows")
    axis.legend(loc="best")
    fig.tight_layout()
    dist_path = args.figures_dir / f"autoencoder_reconstruction_error_distribution_{slug}{suffix}.png"
    fig.savefig(dist_path, dpi=160)
    plt.close(fig)

    print(f"Wrote figures: {gap_path}, {dist_path}")


if __name__ == "__main__":
    main()
