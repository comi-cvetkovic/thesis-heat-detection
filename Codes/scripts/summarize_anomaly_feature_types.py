from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


DISPLAY_FEATURE = {
    "supply_temp_c": "Supply",
    "return_temp_c": "Return",
    "stabilized_flow_log_feature": "Flow",
    "derived_flow_kg_s": "Flow",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--flow-feature-mode", choices=["raw", "stabilized_log"], default="stabilized_log")
    parser.add_argument("--tables-dir", type=Path, default=ROOT / "Results" / "tables")
    parser.add_argument("--figures-dir", type=Path, default=ROOT / "Results" / "figures")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    suffix = "" if args.flow_feature_mode == "raw" else f"_{args.flow_feature_mode}"
    anomalies = pd.read_csv(args.tables_dir / f"clustered_anomaly_windows{suffix}.csv")
    anomalies["feature_type"] = anomalies["dominant_anomalous_feature"].map(DISPLAY_FEATURE).fillna(
        anomalies["dominant_anomalous_feature"]
    )

    summary = (
        anomalies.groupby("feature_type", as_index=False)
        .agg(
            windows=("feature_type", "size"),
            sheets=("sheet", lambda values: ", ".join(sorted(pd.unique(values)))),
            reconstruction_mse_median=("reconstruction_mse", "median"),
            supply_mse_median=("supply_temp_c_reconstruction_mse", "median"),
            return_mse_median=("return_temp_c_reconstruction_mse", "median"),
            flow_mse_median=(
                [col for col in anomalies.columns if col.endswith("_reconstruction_mse") and "flow" in col][0],
                "median",
            ),
        )
        .sort_values("windows", ascending=False)
    )

    per_sheet = (
        anomalies.groupby(["sheet", "feature_type"], as_index=False)
        .agg(
            windows=("feature_type", "size"),
            reconstruction_mse_median=("reconstruction_mse", "median"),
        )
        .sort_values(["sheet", "feature_type"])
    )

    args.tables_dir.mkdir(parents=True, exist_ok=True)
    args.figures_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.tables_dir / f"anomaly_feature_type_summary{suffix}.csv"
    sheet_path = args.tables_dir / f"anomaly_feature_type_sheet_summary{suffix}.csv"
    summary.to_csv(summary_path, index=False)
    per_sheet.to_csv(sheet_path, index=False)

    order = ["Supply", "Return", "Flow"]
    summary_plot = summary.set_index("feature_type").reindex([ft for ft in order if ft in summary["feature_type"].values])

    fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)
    ax.bar(summary_plot.index, summary_plot["windows"], color=["tab:blue", "tab:green", "tab:purple"][: len(summary_plot)])
    ax.set_ylabel("Anomalous windows")
    ax.set_title(f"Anomaly windows by dominant feature ({args.flow_feature_mode})")
    counts_path = args.figures_dir / f"anomaly_feature_type_counts{suffix}.png"
    fig.savefig(counts_path, dpi=160, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4.8), constrained_layout=True)
    x = range(len(summary_plot))
    width = 0.22
    ax.bar([i - width for i in x], summary_plot["supply_mse_median"], width=width, label="Supply MSE", color="tab:blue")
    ax.bar(x, summary_plot["return_mse_median"], width=width, label="Return MSE", color="tab:green")
    ax.bar([i + width for i in x], summary_plot["flow_mse_median"], width=width, label="Flow MSE", color="tab:purple")
    ax.set_xticks(list(x), summary_plot.index)
    ax.set_ylabel("Median channel reconstruction MSE")
    ax.set_title(f"Median per-feature error within each feature-type group ({args.flow_feature_mode})")
    ax.legend()
    mse_path = args.figures_dir / f"anomaly_feature_type_median_mse{suffix}.png"
    fig.savefig(mse_path, dpi=160, bbox_inches="tight")
    plt.close(fig)

    pivot = per_sheet.pivot(index="sheet", columns="feature_type", values="windows").fillna(0)
    pivot = pivot.reindex(columns=[ft for ft in order if ft in pivot.columns])
    fig, ax = plt.subplots(figsize=(12, 5), constrained_layout=True)
    bottom = None
    colors = {"Supply": "tab:blue", "Return": "tab:green", "Flow": "tab:purple"}
    for feature_type in pivot.columns:
        values = pivot[feature_type]
        ax.bar(pivot.index, values, bottom=bottom, label=feature_type, color=colors[feature_type])
        bottom = values if bottom is None else bottom + values
    ax.set_ylabel("Anomalous windows")
    ax.set_title(f"Dominant anomaly feature by sheet ({args.flow_feature_mode})")
    ax.tick_params(axis="x", rotation=30)
    ax.legend()
    sheet_fig_path = args.figures_dir / f"anomaly_feature_type_by_sheet{suffix}.png"
    fig.savefig(sheet_fig_path, dpi=160, bbox_inches="tight")
    plt.close(fig)

    print(summary.to_string(index=False))
    print(f"\nWrote tables: {summary_path}, {sheet_path}")
    print(f"Wrote figures: {counts_path}, {mse_path}, {sheet_fig_path}")


if __name__ == "__main__":
    main()
