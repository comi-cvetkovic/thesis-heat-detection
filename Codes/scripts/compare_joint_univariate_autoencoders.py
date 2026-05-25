"""Compare joint and per-feature autoencoder results for one prepared windows dataset."""

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
    parser.add_argument(
        "--windows",
        type=Path,
        default=ROOT
        / "Results"
        / "processed_data"
        / "autoencoder_windows_cons_hostatgeria_underfloor_hea_stabilized_log.npz",
    )
    parser.add_argument("--tables-dir", type=Path, default=ROOT / "Results" / "tables")
    parser.add_argument("--figures-dir", type=Path, default=ROOT / "Results" / "figures")
    return parser.parse_args()


def slugify_feature(name: str) -> str:
    return name.replace(" ", "_").replace("/", "_")


def load_summary_and_scores(tables_dir: Path, stem: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary_path = tables_dir / f"autoencoder_summary_{stem}.csv"
    scores_path = tables_dir / f"autoencoder_scores_{stem}.csv"
    summary = pd.read_csv(summary_path)
    scores = pd.read_csv(scores_path, parse_dates=["window_start"])
    return summary, scores


def summarize_model(
    stem: str,
    label: str,
    summary: pd.DataFrame,
    scores: pd.DataFrame,
    joint_flagged_windows: set[pd.Timestamp] | None = None,
) -> dict[str, object]:
    row = summary.iloc[0]
    flagged = scores[scores["is_reconstruction_anomaly"]]
    train_flagged = flagged[flagged["split"] == "train"]
    test_flagged = flagged[flagged["split"] == "test"]
    top_window = flagged.sort_values("reconstruction_mse", ascending=False).head(1)
    flagged_windows_set = set(pd.to_datetime(flagged["window_start"]))
    overlap_with_joint = (
        len(flagged_windows_set & joint_flagged_windows) if joint_flagged_windows is not None else len(flagged_windows_set)
    )
    return {
        "model_label": label,
        "stem": stem,
        "model_scope": row.get("model_scope", "joint"),
        "features": row["features"],
        "windows": int(row["windows"]),
        "train_windows": int(row["train_windows"]),
        "test_windows": int(row["test_windows"]),
        "threshold_train_p99": float(row["threshold_train_p99"]),
        "flagged_windows": int(row["flagged_windows"]),
        "flagged_train_windows": int(len(train_flagged)),
        "flagged_test_windows": int(len(test_flagged)),
        "flagged_window_rate": float(row["flagged_windows"]) / float(row["windows"]),
        "overlap_with_joint_flagged_windows": overlap_with_joint,
        "overlap_with_joint_rate": (
            overlap_with_joint / len(flagged_windows_set) if flagged_windows_set else np.nan
        ),
        "median_reconstruction_mse": float(scores["reconstruction_mse"].median()),
        "p99_reconstruction_mse": float(scores["reconstruction_mse"].quantile(0.99)),
        "top_flagged_window_start": top_window["window_start"].iloc[0] if not top_window.empty else pd.NaT,
        "top_flagged_window_mse": float(top_window["reconstruction_mse"].iloc[0]) if not top_window.empty else np.nan,
    }


def main() -> None:
    args = parse_args()
    args.tables_dir.mkdir(parents=True, exist_ok=True)
    args.figures_dir.mkdir(parents=True, exist_ok=True)

    data = np.load(args.windows, allow_pickle=True)
    feature_names = [str(value) for value in data["feature_names"]]
    base_stem = args.windows.stem.replace("autoencoder_windows_", "")

    rows: list[dict[str, object]] = []
    joint_summary, joint_scores = load_summary_and_scores(args.tables_dir, base_stem)
    joint_flagged_windows = set(pd.to_datetime(joint_scores.loc[joint_scores["is_reconstruction_anomaly"], "window_start"]))
    rows.append(summarize_model(base_stem, "joint", joint_summary, joint_scores, joint_flagged_windows))

    for feature_name in feature_names:
        feature_stem = f"{base_stem}__{slugify_feature(feature_name)}"
        summary, scores = load_summary_and_scores(args.tables_dir, feature_stem)
        rows.append(summarize_model(feature_stem, feature_name, summary, scores, joint_flagged_windows))

    comparison = pd.DataFrame(rows)
    output_path = args.tables_dir / f"autoencoder_joint_vs_univariate_{base_stem}.csv"
    comparison.to_csv(output_path, index=False)

    plot_data = comparison.copy()
    plot_data["label"] = plot_data["model_label"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    axes[0].bar(plot_data["label"], plot_data["flagged_window_rate"], color="tab:blue")
    axes[0].set_title("Flagged window rate")
    axes[0].set_ylabel("Flagged / total windows")
    axes[0].tick_params(axis="x", rotation=20)

    axes[1].bar(plot_data["label"], plot_data["median_reconstruction_mse"], color="tab:orange")
    axes[1].set_title("Median reconstruction MSE")
    axes[1].set_ylabel("MSE")
    axes[1].tick_params(axis="x", rotation=20)

    fig.tight_layout()
    figure_path = args.figures_dir / f"autoencoder_joint_vs_univariate_{base_stem}.png"
    fig.savefig(figure_path, dpi=160)
    plt.close(fig)

    print(comparison.to_string(index=False))
    print(f"\nWrote comparison: {output_path}")
    print(f"Wrote figure: {figure_path}")


if __name__ == "__main__":
    main()
