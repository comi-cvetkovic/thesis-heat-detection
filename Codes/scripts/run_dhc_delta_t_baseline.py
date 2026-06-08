"""Run a low delta-T baseline on selected DHC heating sheets."""

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

from Codes.src.anomaly_detection import modified_z_score
from Codes.src.features import add_delta_t


DEFAULT_TARGETS = {
    "cons_abat_cisneros": ROOT / "Data" / "DHC network" / "data" / "District Heating_updated_16_07_2025_1.xlsx",
    "cons_abat_garriga": ROOT / "Data" / "DHC network" / "data" / "District Heating_updated_16_07_2025_1.xlsx",
    "cons_abat_marcet": ROOT / "Data" / "DHC network" / "data" / "District Heating_updated_16_07_2025_1.xlsx",
    "cons_abat_oliba": ROOT / "Data" / "DHC network" / "data" / "District Heating_updated_16_07_2025_2.xlsx",
    "cons_hostatgeria_DHW_radiators": ROOT
    / "Data"
    / "DHC network"
    / "data"
    / "District Heating_updated_16_07_2025_2.xlsx",
    "cons_hostatgeria_underfloor_hea": ROOT
    / "Data"
    / "DHC network"
    / "data"
    / "District Heating_updated_16_07_2025_2.xlsx",
    "cons_nostra_senyora": ROOT / "Data" / "DHC network" / "data" / "District Heating_updated_16_07_2025_2.xlsx",
}

TIMESTAMP_COL = "Time stamp"
POWER_COL = "Power Interval Trend Log"
RETURN_COL = "Return Temperature Interval Trend Log"
SUPPLY_COL = "Supply Temperature Interval Trend Log"


def clean_name(value: str) -> str:
    return value.lower().replace(" ", "_").replace("/", "_").replace("\\", "_")


def run_sheet(
    workbook_path: Path,
    sheet_name: str,
    output_records: Path,
    output_figures: Path,
    z_threshold: float,
) -> dict[str, object]:
    frame = pd.read_excel(workbook_path, sheet_name=sheet_name)
    frame = frame.dropna(how="all")
    frame[TIMESTAMP_COL] = pd.to_datetime(frame[TIMESTAMP_COL], errors="coerce", dayfirst=True)
    frame = frame.dropna(subset=[TIMESTAMP_COL]).sort_values(TIMESTAMP_COL).reset_index(drop=True)
    frame = add_delta_t(frame, supply_col=SUPPLY_COL, return_col=RETURN_COL)

    frame["power"] = pd.to_numeric(frame[POWER_COL], errors="coerce")
    frame["is_active_heating"] = (frame["power"] > 0) & (frame["delta_t_c"] > 0)
    frame["active_delta_t_modified_z"] = pd.NA
    active_index = frame["is_active_heating"]
    frame.loc[active_index, "active_delta_t_modified_z"] = modified_z_score(frame.loc[active_index, "delta_t_c"])
    frame["is_low_delta_t_anomaly"] = frame["active_delta_t_modified_z"] <= z_threshold

    output_records.mkdir(parents=True, exist_ok=True)
    output_figures.mkdir(parents=True, exist_ok=True)
    slug = clean_name(sheet_name)
    output_csv = output_records / f"dhc_delta_t_baseline_{slug}.csv"
    output_plot = output_figures / f"dhc_delta_t_baseline_{slug}.png"

    columns = [
        TIMESTAMP_COL,
        POWER_COL,
        SUPPLY_COL,
        RETURN_COL,
        "delta_t_c",
        "is_active_heating",
        "active_delta_t_modified_z",
        "is_low_delta_t_anomaly",
    ]
    frame[columns].to_csv(output_csv, index=False)

    active = frame[frame["is_active_heating"]]
    anomalies = frame[frame["is_low_delta_t_anomaly"]]

    fig, axis = plt.subplots(figsize=(12, 5))
    axis.plot(active[TIMESTAMP_COL], active["delta_t_c"], linewidth=0.7, label="Active heating delta-T")
    if not anomalies.empty:
        axis.scatter(
            anomalies[TIMESTAMP_COL],
            anomalies["delta_t_c"],
            s=12,
            color="tab:red",
            label="Low delta-T anomaly",
        )
    axis.set_title(f"{sheet_name}: active-heating low delta-T baseline")
    axis.set_xlabel("Timestamp")
    axis.set_ylabel("Supply - return [C]")
    axis.legend(loc="best")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(output_plot, dpi=160)
    plt.close(fig)

    return {
        "sheet": sheet_name,
        "workbook": workbook_path.name,
        "rows": len(frame),
        "active_rows": int(frame["is_active_heating"].sum()),
        "start": frame[TIMESTAMP_COL].min(),
        "end": frame[TIMESTAMP_COL].max(),
        "median_active_delta_t_c": active["delta_t_c"].median(),
        "p05_active_delta_t_c": active["delta_t_c"].quantile(0.05),
        "anomalies": int(frame["is_low_delta_t_anomaly"].sum()),
        "table": output_csv,
        "figure": output_plot,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sheets", nargs="+", default=list(DEFAULT_TARGETS))
    parser.add_argument("--z-threshold", type=float, default=-3.5)
    parser.add_argument("--output-tables", type=Path, default=ROOT / "Results" / "tables")
    parser.add_argument("--output-records", type=Path, default=ROOT / "Results" / "processed_data")
    parser.add_argument("--output-figures", type=Path, default=ROOT / "Results" / "figures")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summaries = [
        run_sheet(
            workbook_path=DEFAULT_TARGETS[sheet],
            sheet_name=sheet,
            output_records=args.output_records,
            output_figures=args.output_figures,
            z_threshold=args.z_threshold,
        )
        for sheet in args.sheets
    ]

    args.output_tables.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_tables / "dhc_delta_t_baseline_summary.csv"
    summary_frame = pd.DataFrame(summaries)
    summary_frame.to_csv(summary_path, index=False)
    print(summary_frame.to_string(index=False))
    print(f"\nWrote summary: {summary_path}")


if __name__ == "__main__":
    main()
