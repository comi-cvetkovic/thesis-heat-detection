"""Create an inventory of the Excel data files used in the thesis project.

The script scans workbook sheets, records column-level metadata, and writes CSV
summaries that help decide which dataset should be used first for HEAT
replication and baseline anomaly detection.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


DEFAULT_INPUTS = [
    Path("Data/Abat Oliba Building/Abat_Oliba/Abat_Oliba_Data.xlsx"),
    Path("Data/DHC network/data/District Heating_updated_16_07_2025_1.xlsx"),
    Path("Data/DHC network/data/District Heating_updated_16_07_2025_2.xlsx"),
    Path("Data/DHC network/data/District Cooling_updated_16_07_2025.xlsx"),
    Path("Data/20250915_Modbus.xlsx"),
    Path("Data/old/20240606_Data_Montserrat.xlsx"),
    Path("Data/old/20231025_Data_Montserrat v2.xlsx"),
]

TIME_KEYWORDS = ("time", "date", "timestamp", "fecha", "hora")
SUPPLY_TEMP_KEYWORDS = ("supply", "sup", "ts", "impulsion", "impulsio", "ida")
RETURN_TEMP_KEYWORDS = ("return", "ret", "tr", "retorn", "retorno", "vuelta")
FLOW_KEYWORDS = ("flow", "mass", "m3", "kg/s", "kg_s", "caudal", "debit")
POWER_KEYWORDS = ("power", "kw", "watt", "energia", "energy", "potencia")


@dataclass(frozen=True)
class KeywordHit:
    category: str
    keyword: str


def normalize_name(value: object) -> str:
    return str(value).strip().lower()


def find_keyword_hits(column_name: object) -> list[KeywordHit]:
    normalized = normalize_name(column_name)
    keyword_groups = {
        "timestamp_candidate": TIME_KEYWORDS,
        "supply_temperature_candidate": SUPPLY_TEMP_KEYWORDS,
        "return_temperature_candidate": RETURN_TEMP_KEYWORDS,
        "flow_candidate": FLOW_KEYWORDS,
        "power_or_energy_candidate": POWER_KEYWORDS,
    }

    hits: list[KeywordHit] = []
    for category, keywords in keyword_groups.items():
        for keyword in keywords:
            if keyword in normalized:
                hits.append(KeywordHit(category, keyword))
    return hits


def safe_datetime_summary(series: pd.Series) -> tuple[str, str, str]:
    """Return date range and inferred sampling for plausible datetime columns."""
    converted = pd.to_datetime(series, errors="coerce", dayfirst=True)
    valid = converted.dropna()
    if valid.empty:
        return "", "", ""

    min_time = valid.min().isoformat()
    max_time = valid.max().isoformat()

    diffs = valid.sort_values().drop_duplicates().diff().dropna()
    if diffs.empty:
        return min_time, max_time, ""

    mode_delta = diffs.mode()
    inferred_step = str(mode_delta.iloc[0]) if not mode_delta.empty else ""
    return min_time, max_time, inferred_step


def inspect_workbook(
    path: Path,
    max_rows_per_sheet: int | None,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    workbook_rows: list[dict[str, object]] = []
    column_rows: list[dict[str, object]] = []

    excel = pd.ExcelFile(path)
    for sheet_name in excel.sheet_names:
        df = pd.read_excel(excel, sheet_name=sheet_name, nrows=max_rows_per_sheet)
        rows, cols = df.shape
        total_cells = rows * cols
        missing_cells = int(df.isna().sum().sum())
        missing_pct = (missing_cells / total_cells) if total_cells else 0.0

        sheet_keyword_categories: set[str] = set()
        datetime_ranges: list[str] = []
        numeric_columns = 0

        for column in df.columns:
            series = df[column]
            non_null = int(series.notna().sum())
            missing = int(series.isna().sum())
            missing_column_pct = (missing / rows) if rows else 0.0
            dtype = str(series.dtype)
            is_numeric = pd.api.types.is_numeric_dtype(series)
            if is_numeric:
                numeric_columns += 1

            hits = find_keyword_hits(column)
            hit_categories = sorted({hit.category for hit in hits})
            sheet_keyword_categories.update(hit_categories)

            min_time = ""
            max_time = ""
            inferred_step = ""
            if "timestamp_candidate" in hit_categories or pd.api.types.is_datetime64_any_dtype(series):
                min_time, max_time, inferred_step = safe_datetime_summary(series)
                if min_time and max_time:
                    datetime_ranges.append(f"{column}: {min_time} to {max_time}")

            column_rows.append(
                {
                    "file": str(path),
                    "sheet": sheet_name,
                    "column": str(column),
                    "dtype": dtype,
                    "non_null_rows": non_null,
                    "missing_rows": missing,
                    "missing_pct": round(missing_column_pct, 4),
                    "is_numeric": is_numeric,
                    "candidate_categories": ";".join(hit_categories),
                    "matched_keywords": ";".join(sorted({hit.keyword for hit in hits})),
                    "datetime_min": min_time,
                    "datetime_max": max_time,
                    "inferred_time_step": inferred_step,
                    "sample_values": " | ".join(map(str, series.dropna().head(5).tolist())),
                }
            )

        workbook_rows.append(
            {
                "file": str(path),
                "sheet": sheet_name,
                "rows": rows,
                "columns": cols,
                "sampled": max_rows_per_sheet is not None,
                "max_rows_per_sheet": max_rows_per_sheet or "",
                "numeric_columns": numeric_columns,
                "missing_cells": missing_cells,
                "missing_pct": round(missing_pct, 4),
                "candidate_categories": ";".join(sorted(sheet_keyword_categories)),
                "datetime_ranges": " || ".join(datetime_ranges[:5]),
                "column_preview": " | ".join(map(str, df.columns[:20])),
            }
        )

    return workbook_rows, column_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("Results/tables"),
        help="Directory where CSV summaries are written.",
    )
    parser.add_argument(
        "--inputs",
        nargs="*",
        type=Path,
        default=DEFAULT_INPUTS,
        help="Excel files to inspect, relative to --root unless absolute.",
    )
    parser.add_argument(
        "--max-rows-per-sheet",
        type=int,
        default=5000,
        help="Maximum rows to read per sheet for fast schema discovery. Use 0 to read all rows.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = root / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    input_paths = []
    for input_path in args.inputs:
        path = input_path if input_path.is_absolute() else root / input_path
        if path.exists():
            input_paths.append(path)

    if not input_paths:
        raise FileNotFoundError("No input Excel files were found.")

    sheet_rows: list[dict[str, object]] = []
    column_rows: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    max_rows_per_sheet = args.max_rows_per_sheet if args.max_rows_per_sheet > 0 else None

    for path in input_paths:
        try:
            workbook_sheet_rows, workbook_column_rows = inspect_workbook(
                path,
                max_rows_per_sheet=max_rows_per_sheet,
            )
            sheet_rows.extend(workbook_sheet_rows)
            column_rows.extend(workbook_column_rows)
        except Exception as exc:  # noqa: BLE001 - inventory should continue across files.
            errors.append({"file": str(path), "error": repr(exc)})

    pd.DataFrame(sheet_rows).to_csv(output_dir / "data_inventory_sheets.csv", index=False)
    pd.DataFrame(column_rows).to_csv(output_dir / "data_inventory_columns.csv", index=False)
    pd.DataFrame(errors).to_csv(output_dir / "data_inventory_errors.csv", index=False)

    print(f"Inspected {len(input_paths)} workbook(s).")
    print(f"Wrote {output_dir / 'data_inventory_sheets.csv'}")
    print(f"Wrote {output_dir / 'data_inventory_columns.csv'}")
    if errors:
        print(f"Some files had errors. See {output_dir / 'data_inventory_errors.csv'}")


if __name__ == "__main__":
    main()
