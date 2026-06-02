"""Create a compact review table for the strongest anomaly candidates across sheets."""

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
    parser.add_argument("--flow-feature-mode", choices=["raw", "stabilized_log"], default="stabilized_log")
    parser.add_argument("--top-k-per-sheet", type=int, default=4)
    parser.add_argument("--tables-dir", type=Path, default=ROOT / "Results" / "tables")
    return parser.parse_args()


def clean_name(value: str) -> str:
    return value.lower().replace(" ", "_").replace("/", "_").replace("\\", "_")


def main() -> None:
    args = parse_args()
    suffix = "" if args.flow_feature_mode == "raw" else f"_{args.flow_feature_mode}"
    rows: list[pd.DataFrame] = []

    for sheet in args.sheets:
        slug = clean_name(sheet)
        inspect_path = args.tables_dir / f"inspect_autoencoder_{slug}{suffix}_summary.csv"
        if not inspect_path.exists():
            continue
        inspect_df = pd.read_csv(inspect_path, parse_dates=["window_start", "window_end"])
        inspect_df = inspect_df.sort_values("reconstruction_mse", ascending=False).head(args.top_k_per_sheet).copy()
        inspect_df.insert(0, "sheet", sheet)
        rows.append(inspect_df)

    if not rows:
        raise ValueError("No inspection summaries found for the requested sheets.")

    summary = pd.concat(rows, ignore_index=True)
    summary = summary[
        [
            "sheet",
            "rank",
            "window_start",
            "window_end",
            "split",
            "reconstruction_mse",
            "dominant_anomalous_feature",
            "supply_temp_c_reconstruction_mse",
            "return_temp_c_reconstruction_mse",
            [col for col in summary.columns if col.endswith("_reconstruction_mse") and col not in ("reconstruction_mse", "supply_temp_c_reconstruction_mse", "return_temp_c_reconstruction_mse")][0],
            "median_delta_t_c",
            "min_delta_t_c",
            "low_delta_t_anomaly_points",
            "has_low_delta_t_overlap",
        ]
    ]
    output = args.tables_dir / f"anomaly_candidate_review{suffix}.csv"
    summary.to_csv(output, index=False)
    print(summary.to_string(index=False))
    print(f"\nWrote summary: {output}")


if __name__ == "__main__":
    main()
