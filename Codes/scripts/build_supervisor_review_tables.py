from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "Results" / "tables"

SHEETS = [
    ("cons_abat_cisneros", "cons_abat_cisneros", "Abat Cisneros"),
    ("cons_abat_garriga", "cons_abat_garriga", "Abat Garriga"),
    ("cons_abat_marcet", "cons_abat_marcet", "Abat Marcet"),
    ("cons_abat_oliba", "cons_abat_oliba", "Abat Oliba"),
    ("cons_hostatgeria_DHW_radiators", "cons_hostatgeria_dhw_radiators", "Hostatgeria DHW Radiators"),
    ("cons_hostatgeria_underfloor_hea", "cons_hostatgeria_underfloor_hea", "Hostatgeria Underfloor"),
    ("cons_nostra_senyora", "cons_nostra_senyora", "Nostra Senyora"),
]

FLOW_SUFFIX = "_stabilized_log"


def main() -> None:
    baseline = pd.read_csv(TABLES / "dhc_delta_t_baseline_summary.csv")[
        ["sheet", "median_active_delta_t_c", "anomalies"]
    ].rename(columns={"anomalies": "baseline_anomalies"})
    feature_summary = pd.read_csv(TABLES / f"anomaly_feature_type_sheet_summary{FLOW_SUFFIX}.csv")

    sheet_rows: list[dict[str, object]] = []
    anomaly_rows: list[pd.DataFrame] = []

    for sheet, stem, label in SHEETS:
        summary = pd.read_csv(TABLES / f"autoencoder_summary_{stem}{FLOW_SUFFIX}.csv").iloc[0]
        inspect = pd.read_csv(TABLES / f"inspect_autoencoder_{stem}{FLOW_SUFFIX}_summary.csv")
        scores = pd.read_csv(TABLES / f"autoencoder_scores_{stem}{FLOW_SUFFIX}.csv")
        top = inspect.iloc[0]
        feature_counts = (
            scores[scores["is_reconstruction_anomaly"]]["dominant_anomalous_feature"].value_counts().to_dict()
        )
        sheet_rows.append(
            {
                "sheet": sheet,
                "display_label": label,
                "threshold_method": summary.get("threshold_method", "train_p99"),
                "threshold_value": summary.get("threshold_value", summary.get("threshold_train_p99")),
                "windows": int(summary["windows"]),
                "train_windows": int(summary["train_windows"]),
                "test_windows": int(summary["test_windows"]),
                "flagged_windows": int(summary["flagged_windows"]),
                "flagged_rate": int(summary["flagged_windows"]) / int(summary["windows"]),
                "top_window_start": top["window_start"],
                "top_window_end": top["window_end"],
                "top_reconstruction_mse": top["reconstruction_mse"],
                "top_dominant_anomalous_feature": top.get("dominant_anomalous_feature", ""),
                "top_has_low_delta_t_overlap": top.get("has_low_delta_t_overlap", False),
                "supply_dominant_count": feature_counts.get("supply_temp_c", 0),
                "return_dominant_count": feature_counts.get("return_temp_c", 0),
                "flow_dominant_count": feature_counts.get("stabilized_flow_log_feature", 0),
            }
        )

        inspect = inspect.copy()
        inspect.insert(0, "display_label", label)
        inspect.insert(1, "sheet", sheet)
        inspect["threshold_method"] = summary.get("threshold_method", "train_p99")
        inspect["threshold_value"] = summary.get("threshold_value", summary.get("threshold_train_p99"))
        anomaly_rows.append(inspect)

    sheet_df = pd.DataFrame(sheet_rows).merge(baseline, on="sheet", how="left")
    anomaly_df = pd.concat(anomaly_rows, ignore_index=True)

    sheet_path = TABLES / "supervisor_results_sheet_2026-06-07.csv"
    anomaly_path = TABLES / "supervisor_anomaly_review_2026-06-07.csv"
    sheet_df.to_csv(sheet_path, index=False)
    anomaly_df.to_csv(anomaly_path, index=False)

    print(f"Wrote sheet summary: {sheet_path}")
    print(f"Wrote anomaly review: {anomaly_path}")


if __name__ == "__main__":
    main()
