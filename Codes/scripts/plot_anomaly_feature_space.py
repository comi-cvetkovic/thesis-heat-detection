from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "Results" / "tables"
FIGURES = ROOT / "Results" / "figures"

INPUT = TABLES / "supervisor_anomaly_review_2026-06-07.csv"
OUTPUT = FIGURES / "anomaly_feature_space_stabilized_log.png"

COLOR_MAP = {
    "supply_temp_c": "tab:blue",
    "return_temp_c": "tab:green",
    "stabilized_flow_log_feature": "tab:purple",
}

LABEL_MAP = {
    "supply_temp_c": "Supply-dominant",
    "return_temp_c": "Return-dominant",
    "stabilized_flow_log_feature": "Flow-dominant",
}


def main() -> None:
    frame = pd.read_csv(INPUT, parse_dates=["window_start", "window_end"])
    if frame.empty:
        raise ValueError(f"No anomaly rows found in {INPUT}")

    pairs = [
        ("supply_temp_c_reconstruction_mse", "return_temp_c_reconstruction_mse", "Supply error [MSE]", "Return error [MSE]"),
        (
            "supply_temp_c_reconstruction_mse",
            "stabilized_flow_log_feature_reconstruction_mse",
            "Supply error [MSE]",
            "Stabilized flow error [MSE]",
        ),
        (
            "return_temp_c_reconstruction_mse",
            "stabilized_flow_log_feature_reconstruction_mse",
            "Return error [MSE]",
            "Stabilized flow error [MSE]",
        ),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(17, 5.5), constrained_layout=True)

    legend_handles = {}
    for ax, (x_col, y_col, x_label, y_label) in zip(axes, pairs, strict=True):
        for feature_key, color in COLOR_MAP.items():
            subset = frame[frame["dominant_anomalous_feature"] == feature_key]
            if subset.empty:
                continue
            scatter = ax.scatter(
                subset[x_col],
                subset[y_col],
                s=42,
                alpha=0.75,
                c=color,
                edgecolors="black",
                linewidths=0.4,
                label=LABEL_MAP[feature_key],
            )
            legend_handles[feature_key] = scatter
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.grid(alpha=0.25)

    overlap = frame[frame["has_low_delta_t_overlap"].fillna(False).astype(bool)]
    if not overlap.empty:
        axes[0].scatter(
            overlap["supply_temp_c_reconstruction_mse"],
            overlap["return_temp_c_reconstruction_mse"],
            s=110,
            facecolors="none",
            edgecolors="tab:red",
            linewidths=1.2,
            label="Low delta-T overlap",
        )

    handles = [legend_handles[key] for key in COLOR_MAP if key in legend_handles]
    labels = [LABEL_MAP[key] for key in COLOR_MAP if key in legend_handles]
    if not overlap.empty:
        handles.append(axes[0].collections[-1])
        labels.append("Low delta-T overlap")
    fig.legend(handles, labels, loc="upper center", ncol=len(labels), frameon=False, bbox_to_anchor=(0.5, 1.03))
    fig.suptitle("Anomaly feature space using actual per-feature reconstruction errors", fontsize=15)
    fig.savefig(OUTPUT, dpi=160, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
