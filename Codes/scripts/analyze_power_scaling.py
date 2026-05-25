"""Explore how different power scaling assumptions affect derived-flow magnitudes."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Codes.src.features import WATER_CP_J_PER_KG_C, add_delta_t


DEFAULT_WORKBOOK = ROOT / "Data" / "DHC network" / "data" / "District Heating_updated_16_07_2025_2.xlsx"
DEFAULT_SHEETS = (
    "cons_abat_oliba",
    "cons_hostatgeria_DHW_radiators",
    "cons_hostatgeria_underfloor_hea",
    "cons_nostra_senyora",
)
TIMESTAMP_COL = "Time stamp"
POWER_COL = "Power Interval Trend Log"
RETURN_COL = "Return Temperature Interval Trend Log"
SUPPLY_COL = "Supply Temperature Interval Trend Log"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, default=DEFAULT_WORKBOOK)
    parser.add_argument("--sheets", nargs="+", default=list(DEFAULT_SHEETS))
    parser.add_argument("--target-flow", type=float, default=1.5)
    parser.add_argument("--tables-dir", type=Path, default=ROOT / "Results" / "tables")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows: list[dict[str, object]] = []
    scales = {
        "W": 1.0,
        "10W": 10.0,
        "100W": 100.0,
        "kW": 1000.0,
        "10kW": 10000.0,
    }

    for sheet in args.sheets:
        frame = pd.read_excel(args.workbook, sheet_name=sheet).dropna(how="all")
        frame[TIMESTAMP_COL] = pd.to_datetime(frame[TIMESTAMP_COL], errors="coerce", dayfirst=True)
        frame = frame.dropna(subset=[TIMESTAMP_COL]).sort_values(TIMESTAMP_COL)
        frame = add_delta_t(frame, supply_col=SUPPLY_COL, return_col=RETURN_COL)
        power = pd.to_numeric(frame[POWER_COL], errors="coerce")
        delta_t = pd.to_numeric(frame["delta_t_c"], errors="coerce")
        active = (power > 0) & (delta_t > 0)
        positive_power = power.where(active)
        positive_delta = delta_t.where(active)
        base_denominator = WATER_CP_J_PER_KG_C * positive_delta

        row: dict[str, object] = {
            "sheet": sheet,
            "active_rows": int(active.sum()),
            "median_power_raw": positive_power.median(),
            "median_delta_t_c": positive_delta.median(),
        }
        target_scale = float(args.target_flow * WATER_CP_J_PER_KG_C * positive_delta.median() / positive_power.median())
        row["implied_scale_to_target_flow"] = target_scale

        for label, multiplier in scales.items():
            flow = (positive_power * multiplier) / base_denominator
            row[f"median_flow_if_{label}"] = flow.median()
        rows.append(row)

    summary = pd.DataFrame(rows)
    args.tables_dir.mkdir(parents=True, exist_ok=True)
    output = args.tables_dir / "power_scaling_sanity_check.csv"
    summary.to_csv(output, index=False)
    print(summary.to_string(index=False))
    print(f"\nWrote summary: {output}")


if __name__ == "__main__":
    main()
