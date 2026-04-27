"""Run a simple low temperature-separation anomaly baseline."""

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

from Codes.src.anomaly_detection import flag_low_delta_t
from Codes.src.excel_timeseries import read_timeseries_sheet
from Codes.src.features import add_delta_t


DEFAULT_WORKBOOK = ROOT / "Data" / "Abat Oliba Building" / "Abat_Oliba" / "Abat_Oliba_Data.xlsx"
DEFAULT_SHEETS = ("Ground floor", "First floor")


def clean_name(value: str) -> str:
    return (
        value.lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace("[", "")
        .replace("]", "")
    )


def run_sheet(
    workbook_path: Path,
    sheet_name: str,
    output_records: Path,
    output_figures: Path,
    z_threshold: float,
) -> dict[str, object]:
    frame = read_timeseries_sheet(workbook_path, sheet_name)
    frame = add_delta_t(frame, supply_col="Supply Temperature", return_col="Return Temperature")
    frame["temperature_separation_c"] = frame["delta_t_c"].abs()
    frame = flag_low_delta_t(
        frame,
        delta_t_col="temperature_separation_c",
        z_threshold=z_threshold,
        output_col="is_low_temperature_separation_anomaly",
    )

    output_records.mkdir(parents=True, exist_ok=True)
    output_figures.mkdir(parents=True, exist_ok=True)

    slug = clean_name(sheet_name)
    output_csv = output_records / f"baseline_delta_t_{slug}.csv"
    output_plot = output_figures / f"baseline_delta_t_{slug}.png"

    columns = [
        "Time stamp",
        "Supply Temperature",
        "Return Temperature",
        "delta_t_c",
        "temperature_separation_c",
        "temperature_separation_c_modified_z",
        "is_low_temperature_separation_anomaly",
    ]
    frame[columns].to_csv(output_csv, index=False)

    anomalies = frame[frame["is_low_temperature_separation_anomaly"]]
    fig, axis = plt.subplots(figsize=(12, 5))
    axis.plot(frame["Time stamp"], frame["temperature_separation_c"], linewidth=0.8, label="Temperature separation")
    if not anomalies.empty:
        axis.scatter(
            anomalies["Time stamp"],
            anomalies["temperature_separation_c"],
            s=12,
            color="tab:red",
            label="Low-separation anomaly",
        )
    axis.set_title(f"{sheet_name}: low temperature-separation baseline")
    axis.set_xlabel("Timestamp")
    axis.set_ylabel("abs(Supply - Return) [C]")
    axis.legend(loc="best")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(output_plot, dpi=160)
    plt.close(fig)

    return {
        "sheet": sheet_name,
        "rows": len(frame),
        "start": frame["Time stamp"].min(),
        "end": frame["Time stamp"].max(),
        "median_temperature_separation_c": frame["temperature_separation_c"].median(),
        "anomalies": int(frame["is_low_temperature_separation_anomaly"].sum()),
        "table": output_csv,
        "figure": output_plot,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, default=DEFAULT_WORKBOOK)
    parser.add_argument("--sheets", nargs="+", default=list(DEFAULT_SHEETS))
    parser.add_argument("--z-threshold", type=float, default=-3.5)
    parser.add_argument("--output-tables", type=Path, default=ROOT / "Results" / "tables")
    parser.add_argument("--output-records", type=Path, default=ROOT / "Results" / "processed_data")
    parser.add_argument("--output-figures", type=Path, default=ROOT / "Results" / "figures")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summaries = [
        run_sheet(
            workbook_path=args.workbook,
            sheet_name=sheet,
            output_records=args.output_records,
            output_figures=args.output_figures,
            z_threshold=args.z_threshold,
        )
        for sheet in args.sheets
    ]

    summary_path = args.output_tables / "baseline_delta_t_summary.csv"
    pd.DataFrame(summaries).to_csv(summary_path, index=False)
    print(pd.DataFrame(summaries).to_string(index=False))
    print(f"\nWrote summary: {summary_path}")


if __name__ == "__main__":
    main()
