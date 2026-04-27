"""Summarize district-heating workbook sheets for dataset selection."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Codes.src.features import WATER_CP_J_PER_KG_C, add_delta_t, add_flow_from_power


DEFAULT_WORKBOOKS = (
    ROOT / "Data" / "DHC network" / "data" / "District Heating_updated_16_07_2025_1.xlsx",
    ROOT / "Data" / "DHC network" / "data" / "District Heating_updated_16_07_2025_2.xlsx",
)
DEFAULT_SHEETS = (
    "cons_abat_oliba",
    "cons_hostatgeria_DHW_radiators",
    "cons_hostatgeria_underfloor_hea",
    "cons_nostra_senyora",
    "cons_abat_cisneros",
    "cons_abat_garriga",
    "cons_abat_marcet",
)

TIMESTAMP_COL = "Time stamp"
POWER_COL = "Power Interval Trend Log"
RETURN_COL = "Return Temperature Interval Trend Log"
SUPPLY_COL = "Supply Temperature Interval Trend Log"
FLOW_COL = "flow (kg/s)"


def summarize_sheet(workbook_path: Path, sheet_name: str) -> dict[str, object]:
    frame = pd.read_excel(workbook_path, sheet_name=sheet_name)
    frame = frame.dropna(how="all")
    frame[TIMESTAMP_COL] = pd.to_datetime(frame[TIMESTAMP_COL], errors="coerce", dayfirst=True)
    frame = frame.dropna(subset=[TIMESTAMP_COL]).sort_values(TIMESTAMP_COL).reset_index(drop=True)

    required = {POWER_COL, RETURN_COL, SUPPLY_COL}
    missing = required.difference(frame.columns)
    if missing:
        return {
            "workbook": workbook_path.name,
            "sheet": sheet_name,
            "rows": len(frame),
            "usable": False,
            "notes": f"missing columns: {', '.join(sorted(missing))}",
        }

    frame = add_delta_t(frame, supply_col=SUPPLY_COL, return_col=RETURN_COL)
    power = pd.to_numeric(frame[POWER_COL], errors="coerce")
    delta_t = pd.to_numeric(frame["delta_t_c"], errors="coerce")

    positive_delta = delta_t > 0
    positive_power = power > 0
    active = positive_power & positive_delta

    summary: dict[str, object] = {
        "workbook": workbook_path.name,
        "sheet": sheet_name,
        "rows": len(frame),
        "usable": True,
        "start": frame[TIMESTAMP_COL].min(),
        "end": frame[TIMESTAMP_COL].max(),
        "median_power": power.median(),
        "max_power": power.max(),
        "median_delta_t_c": delta_t.median(),
        "min_delta_t_c": delta_t.min(),
        "max_delta_t_c": delta_t.max(),
        "pct_positive_delta_t": positive_delta.mean(),
        "pct_positive_power": positive_power.mean(),
        "pct_active_heating": active.mean(),
        "notes": "",
    }

    flow_estimate = (power * 1000.0) / (WATER_CP_J_PER_KG_C * delta_t.replace(0, pd.NA))
    summary["median_estimated_flow_kg_s_from_kw"] = flow_estimate.where(active).median()

    if FLOW_COL in frame.columns:
        measured_flow = pd.to_numeric(frame[FLOW_COL], errors="coerce")
        summary["median_reported_flow"] = measured_flow.median()
        summary["median_reported_to_estimated_flow_ratio"] = (
            measured_flow.where(active) / flow_estimate.where(active)
        ).replace([float("inf"), float("-inf")], pd.NA).median()

    if summary["pct_positive_delta_t"] < 0.5:
        summary["notes"] = "supply-return sign looks inverted or non-heating-dominant"
    elif summary["pct_active_heating"] < 0.25:
        summary["notes"] = "low active-heating fraction"

    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbooks", nargs="+", type=Path, default=list(DEFAULT_WORKBOOKS))
    parser.add_argument("--sheets", nargs="+", default=list(DEFAULT_SHEETS))
    parser.add_argument("--output", type=Path, default=ROOT / "Results" / "tables" / "dhc_heating_sheet_summary.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summaries: list[dict[str, object]] = []

    for workbook_path in args.workbooks:
        xlsx = pd.ExcelFile(workbook_path)
        for sheet_name in xlsx.sheet_names:
            if args.sheets and sheet_name not in args.sheets:
                continue
            summaries.append(summarize_sheet(workbook_path, sheet_name))

    output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    summary_frame = pd.DataFrame(summaries)
    summary_frame.to_csv(output, index=False)

    columns = [
        "workbook",
        "sheet",
        "rows",
        "start",
        "end",
        "median_power",
        "median_delta_t_c",
        "pct_positive_delta_t",
        "pct_active_heating",
        "notes",
    ]
    print(summary_frame[[column for column in columns if column in summary_frame.columns]].to_string(index=False))
    print(f"\nWrote summary: {output}")
    print(f"Assumed power unit for estimated flow: kW; Cp={WATER_CP_J_PER_KG_C:g} J/(kg C)")


if __name__ == "__main__":
    main()
