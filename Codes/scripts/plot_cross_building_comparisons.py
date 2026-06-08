from __future__ import annotations

from math import ceil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "Results" / "tables"
FIGURES = ROOT / "Results" / "figures"

SHEETS = [
    ("cons_abat_cisneros", "cons_abat_cisneros", "Abat Cisneros"),
    ("cons_abat_garriga", "cons_abat_garriga", "Abat Garriga"),
    ("cons_abat_marcet", "cons_abat_marcet", "Abat Marcet"),
    ("cons_abat_oliba", "cons_abat_oliba", "Abat Oliba"),
    ("cons_hostatgeria_DHW_radiators", "cons_hostatgeria_dhw_radiators", "Hostatgeria DHW Radiators"),
    ("cons_hostatgeria_underfloor_hea", "cons_hostatgeria_underfloor_hea", "Hostatgeria Underfloor"),
    ("cons_nostra_senyora", "cons_nostra_senyora", "Nostra Senyora"),
]

FLOW_MODE = "stabilized_log"
FLOW_SUFFIX = f"_{FLOW_MODE}"


def load_summary() -> pd.DataFrame:
    baseline = pd.read_csv(TABLES / "dhc_delta_t_baseline_summary.csv")[
        ["sheet", "median_active_delta_t_c", "anomalies"]
    ].rename(
        columns={
            "median_active_delta_t_c": "baseline_median_active_delta_t_c",
            "anomalies": "baseline_anomalies",
        }
    )
    rows: list[dict[str, object]] = []
    for sheet, stem, label in SHEETS:
        summary = pd.read_csv(TABLES / f"autoencoder_summary_{stem}{FLOW_SUFFIX}.csv").iloc[0]
        inspect = pd.read_csv(TABLES / f"inspect_autoencoder_{stem}{FLOW_SUFFIX}_summary.csv")
        top = inspect.iloc[0]
        rows.append(
            {
                "sheet": sheet,
                "stem": stem,
                "display_label": label,
                "windows": int(summary["windows"]),
                "train_windows": int(summary["train_windows"]),
                "test_windows": int(summary["test_windows"]),
                "threshold_method": str(summary["threshold_method"]) if "threshold_method" in summary.index else "train_p99",
                "threshold_value": float(summary["threshold_value"]) if "threshold_value" in summary.index else float(summary["threshold_train_p99"]),
                "flagged_windows": int(summary["flagged_windows"]),
                "top_window_start": top["window_start"],
                "top_window_end": top["window_end"],
                "top_reconstruction_mse_from_inspect": float(top["reconstruction_mse"]),
                "top_has_low_delta_t_overlap": bool(top.get("has_low_delta_t_overlap", False)),
                "top_dominant_feature": str(top.get("dominant_anomalous_feature", "")),
            }
        )
    merged = pd.DataFrame(rows).merge(baseline, on="sheet", how="left")
    merged["flagged_rate"] = merged["flagged_windows"] / merged["windows"]
    return merged


def make_axes_grid(n_items: int, cols: int = 3, base_height: float = 4.0):
    rows = ceil(n_items / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5.5, rows * base_height), constrained_layout=True)
    if rows == 1:
        axes = [axes] if cols == 1 else axes.ravel()
    else:
        axes = axes.ravel()
    return fig, axes


def hide_unused_axes(axes, used: int) -> None:
    for ax in axes[used:]:
        ax.axis("off")


def plot_reconstruction_grid(summary: pd.DataFrame) -> None:
    fig, axes = make_axes_grid(len(SHEETS), cols=3, base_height=3.8)
    for ax, (sheet, stem, label) in zip(axes, SHEETS, strict=False):
        scores = pd.read_csv(TABLES / f"autoencoder_scores_{stem}{FLOW_SUFFIX}.csv")
        scores["window_start"] = pd.to_datetime(scores["window_start"])
        sheet_summary = summary.loc[summary["sheet"] == sheet].iloc[0]
        flagged = scores[scores["is_reconstruction_anomaly"]]
        threshold_label = "Train mean + 3 sigma" if sheet_summary["threshold_method"] == "train_3sigma" else "Train p99 threshold"

        ax.plot(scores["window_start"], scores["reconstruction_mse"], linewidth=0.9, color="tab:blue")
        if not flagged.empty:
            ax.scatter(flagged["window_start"], flagged["reconstruction_mse"], color="tab:red", s=18, zorder=3)
        ax.axhline(sheet_summary["threshold_value"], color="tab:orange", linestyle="--", linewidth=1.0)
        ax.set_title(
            f"{label}\n{int(sheet_summary['flagged_windows'])} flagged / {int(sheet_summary['windows'])} windows",
            fontsize=10,
        )
        ax.set_ylabel("Reconstruction MSE")
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=3, maxticks=5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        ax.tick_params(axis="x", rotation=30, labelsize=8)
        ax.grid(alpha=0.2)
    hide_unused_axes(axes, len(SHEETS))
    fig.suptitle("Autoencoder reconstruction error across all heating-consumer sheets (stabilized flow)", fontsize=16)
    fig.savefig(FIGURES / "all_buildings_reconstruction_error_grid.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def plot_top_anomaly_grid() -> None:
    fig, axes = make_axes_grid(len(SHEETS), cols=3, base_height=3.8)
    summary = load_summary().set_index("sheet")
    for ax, (sheet, stem, label) in zip(axes, SHEETS, strict=False):
        image = mpimg.imread(FIGURES / f"inspect_autoencoder_{stem}{FLOW_SUFFIX}_01.png")
        dominant = str(summary.loc[sheet, "top_dominant_feature"])
        ax.imshow(image)
        ax.set_title(f"{label}\nTop feature: {dominant}", fontsize=10)
        ax.axis("off")
    hide_unused_axes(axes, len(SHEETS))
    fig.suptitle("Top inspected stabilized-flow anomaly window for each heating-consumer sheet", fontsize=16)
    fig.savefig(FIGURES / "all_buildings_top_anomaly_grid.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def plot_anomaly_summary(summary: pd.DataFrame) -> None:
    ordered = summary.sort_values("display_label").reset_index(drop=True)
    labels = ordered["display_label"]
    x = range(len(ordered))

    fig, axes = plt.subplots(1, 2, figsize=(16, 5), constrained_layout=True)
    axes[0].bar(x, ordered["windows"], color="lightsteelblue", label="Retained windows")
    axes[0].bar(x, ordered["flagged_windows"], color="indianred", label="Flagged windows")
    axes[0].set_xticks(list(x), labels, rotation=30, ha="right")
    axes[0].set_ylabel("Count")
    axes[0].set_title("Retained windows vs flagged windows")
    axes[0].legend()

    axes[1].bar(x, ordered["flagged_rate"] * 100.0, color="slateblue")
    axes[1].set_xticks(list(x), labels, rotation=30, ha="right")
    axes[1].set_ylabel("Flagged windows (%)")
    axes[1].set_title("Autoencoder flagged-window rate by sheet")

    fig.suptitle("Seven-sheet anomaly detection summary (stabilized flow)", fontsize=16)
    fig.savefig(FIGURES / "all_buildings_anomaly_summary.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def plot_baseline_vs_autoencoder(summary: pd.DataFrame) -> None:
    ordered = summary.sort_values("display_label").reset_index(drop=True)
    labels = ordered["display_label"]
    x = range(len(ordered))
    width = 0.38
    fig, ax = plt.subplots(figsize=(14, 5), constrained_layout=True)
    ax.bar([i - width / 2 for i in x], ordered["flagged_windows"], width=width, color="tab:red", label="Autoencoder flagged windows")
    ax.bar([i + width / 2 for i in x], ordered["baseline_anomalies"], width=width, color="tab:green", label="Low delta-T baseline anomalies")
    ax.set_xticks(list(x), labels, rotation=30, ha="right")
    ax.set_ylabel("Count")
    ax.set_title("Autoencoder vs low delta-T baseline by sheet")
    ax.legend()
    fig.savefig(FIGURES / "all_buildings_baseline_vs_autoencoder.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def plot_cluster_distribution() -> None:
    cluster_sheet = pd.read_csv(TABLES / "cluster_sheet_summary_stabilized_log.csv")
    cluster_pivot = cluster_sheet.pivot(index="sheet", columns="cluster", values="windows").fillna(0)
    order = [sheet for sheet, _, _ in SHEETS]
    labels = {sheet: label for sheet, _, label in SHEETS}
    cluster_pivot = cluster_pivot.reindex(order)
    cluster_pivot.index = [labels[idx] for idx in cluster_pivot.index]

    fig, ax = plt.subplots(figsize=(14, 5), constrained_layout=True)
    bottom = None
    for cluster in cluster_pivot.columns:
        values = cluster_pivot[cluster]
        ax.bar(cluster_pivot.index, values, bottom=bottom, label=f"Cluster {cluster}")
        bottom = values if bottom is None else bottom + values
    ax.set_ylabel("Window count")
    ax.set_title("All-window operating-regime cluster distribution by sheet (stabilized flow)")
    ax.legend(ncol=4, fontsize=9)
    ax.tick_params(axis="x", rotation=30)
    fig.savefig(FIGURES / "all_buildings_window_cluster_distribution.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def plot_anomaly_cluster_distribution() -> None:
    cluster_sheet = pd.read_csv(TABLES / "anomaly_cluster_sheet_summary_stabilized_log.csv")
    cluster_pivot = cluster_sheet.pivot(index="sheet", columns="anomaly_cluster", values="windows").fillna(0)
    order = [sheet for sheet, _, _ in SHEETS]
    labels = {sheet: label for sheet, _, label in SHEETS}
    cluster_pivot = cluster_pivot.reindex(order).fillna(0)
    cluster_pivot.index = [labels[idx] for idx in cluster_pivot.index]

    fig, ax = plt.subplots(figsize=(14, 5), constrained_layout=True)
    bottom = None
    for cluster in cluster_pivot.columns:
        values = cluster_pivot[cluster]
        ax.bar(cluster_pivot.index, values, bottom=bottom, label=f"Anomaly cluster {cluster}")
        bottom = values if bottom is None else bottom + values
    ax.set_ylabel("Anomalous window count")
    ax.set_title("Anomaly-only cluster distribution by sheet (stabilized flow)")
    ax.legend(ncol=3, fontsize=9)
    ax.tick_params(axis="x", rotation=30)
    fig.savefig(FIGURES / "all_buildings_anomaly_cluster_distribution.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    summary = load_summary()
    summary.to_csv(TABLES / "all_buildings_result_summary.csv", index=False)
    plot_reconstruction_grid(summary)
    plot_top_anomaly_grid()
    plot_anomaly_summary(summary)
    plot_baseline_vs_autoencoder(summary)
    plot_cluster_distribution()
    plot_anomaly_cluster_distribution()


if __name__ == "__main__":
    main()
