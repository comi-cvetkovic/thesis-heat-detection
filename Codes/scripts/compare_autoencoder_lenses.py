"""Compare raw-flow and stabilized-flow autoencoder lenses."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


DEFAULT_SHEETS = ("cons_abat_oliba", "cons_hostatgeria_underfloor_hea")
DEFAULT_MODES = ("raw", "stabilized_log")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sheets", nargs="+", default=list(DEFAULT_SHEETS))
    parser.add_argument("--modes", nargs="+", default=list(DEFAULT_MODES))
    parser.add_argument("--tables-dir", type=Path, default=ROOT / "Results" / "tables")
    parser.add_argument("--output", type=Path, default=ROOT / "Results" / "tables" / "autoencoder_lens_comparison.csv")
    return parser.parse_args()


def suffix_for_mode(mode: str) -> str:
    return "" if mode == "raw" else f"_{mode}"


def main() -> None:
    args = parse_args()
    rows: list[dict[str, object]] = []
    for sheet in args.sheets:
        for mode in args.modes:
            suffix = suffix_for_mode(mode)
            summary = pd.read_csv(args.tables_dir / f"autoencoder_summary_{sheet}{suffix}.csv").iloc[0]
            inspected = pd.read_csv(args.tables_dir / f"inspect_autoencoder_{sheet}{suffix}_summary.csv")
            rows.append(
                {
                    "sheet": sheet,
                    "flow_lens": mode,
                    "windows": int(summary["windows"]),
                    "flagged_windows": int(summary["flagged_windows"]),
                    "threshold_train_p99": float(summary["threshold_train_p99"]),
                    "top_inspected_reconstruction_mse": float(inspected["reconstruction_mse"].max()),
                    "top_overlap_count": int(inspected["has_low_delta_t_overlap"].fillna(False).sum()),
                }
            )

    comparison = pd.DataFrame(rows)
    comparison.to_csv(args.output, index=False)
    print(comparison.to_string(index=False))
    print(f"\nWrote summary: {args.output}")


if __name__ == "__main__":
    main()
