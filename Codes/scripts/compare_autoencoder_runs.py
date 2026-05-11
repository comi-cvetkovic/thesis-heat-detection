"""Summarize multi-sheet autoencoder runs into one comparison table."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


DEFAULT_SHEETS = (
    "cons_abat_oliba",
    "cons_hostatgeria_underfloor_hea",
    "cons_hostatgeria_DHW_radiators",
    "cons_nostra_senyora",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sheets", nargs="+", default=list(DEFAULT_SHEETS))
    parser.add_argument("--tables-dir", type=Path, default=ROOT / "Results" / "tables")
    parser.add_argument("--output", type=Path, default=ROOT / "Results" / "tables" / "autoencoder_multi_sheet_comparison.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows: list[dict[str, object]] = []
    for sheet in args.sheets:
        summary = pd.read_csv(args.tables_dir / f"autoencoder_summary_{sheet}.csv").iloc[0]
        inspect_path = args.tables_dir / f"inspect_autoencoder_{sheet}_summary.csv"
        inspected_overlap_count = 0
        top_inspected_reconstruction_mse = float("nan")
        if inspect_path.exists():
            inspected = pd.read_csv(inspect_path)
            inspected_overlap_count = int(inspected["has_low_delta_t_overlap"].fillna(False).sum())
            top_inspected_reconstruction_mse = float(inspected["reconstruction_mse"].max())

        rows.append(
            {
                "sheet": sheet,
                "windows": int(summary["windows"]),
                "train_windows": int(summary["train_windows"]),
                "test_windows": int(summary["test_windows"]),
                "threshold_train_p99": float(summary["threshold_train_p99"]),
                "flagged_windows": int(summary["flagged_windows"]),
                "inspected_top_overlap_count": inspected_overlap_count,
                "top_inspected_reconstruction_mse": top_inspected_reconstruction_mse,
            }
        )

    comparison = pd.DataFrame(rows)
    comparison.to_csv(args.output, index=False)
    print(comparison.to_string(index=False))
    print(f"\nWrote summary: {args.output}")


if __name__ == "__main__":
    main()
