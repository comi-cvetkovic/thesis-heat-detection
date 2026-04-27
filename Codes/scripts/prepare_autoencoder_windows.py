"""Prepare three-channel DHC windows for autoencoder reconstruction."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Codes.src.features import add_flow_from_power


DEFAULT_WORKBOOK = ROOT / "Data" / "DHC network" / "data" / "District Heating_updated_16_07_2025_2.xlsx"
TIMESTAMP_COL = "Time stamp"
POWER_COL = "Power Interval Trend Log"
RETURN_COL = "Return Temperature Interval Trend Log"
SUPPLY_COL = "Supply Temperature Interval Trend Log"
FEATURES = ("supply_temp_c", "return_temp_c", "derived_flow_kg_s")


def clean_name(value: str) -> str:
    return value.lower().replace(" ", "_").replace("/", "_").replace("\\", "_")


def load_feature_frame(workbook: Path, sheet: str, resample_interval: str) -> pd.DataFrame:
    frame = pd.read_excel(workbook, sheet_name=sheet).dropna(how="all")
    frame[TIMESTAMP_COL] = pd.to_datetime(frame[TIMESTAMP_COL], errors="coerce", dayfirst=True)
    frame = frame.dropna(subset=[TIMESTAMP_COL]).sort_values(TIMESTAMP_COL)
    frame = add_flow_from_power(
        frame,
        power_col=POWER_COL,
        supply_col=SUPPLY_COL,
        return_col=RETURN_COL,
        output_col="derived_flow_kg_s",
        power_unit="kW",
    )
    frame["supply_temp_c"] = pd.to_numeric(frame[SUPPLY_COL], errors="coerce")
    frame["return_temp_c"] = pd.to_numeric(frame[RETURN_COL], errors="coerce")
    frame["power_kw"] = pd.to_numeric(frame[POWER_COL], errors="coerce")
    frame = frame.set_index(TIMESTAMP_COL)

    valid = (
        (frame["power_kw"] > 0)
        & (frame["delta_t_c"] > 0)
        & np.isfinite(frame["derived_flow_kg_s"])
        & (frame["derived_flow_kg_s"] > 0)
    )
    frame = frame.loc[valid, list(FEATURES)]
    frame = frame.resample(resample_interval).median()
    frame = frame.interpolate(method="time", limit=4).dropna()
    return frame


def make_windows(
    values: np.ndarray,
    timestamps: pd.DatetimeIndex,
    window_steps: int,
    stride_steps: int,
) -> tuple[np.ndarray, np.ndarray]:
    windows: list[np.ndarray] = []
    starts: list[np.datetime64] = []

    for start in range(0, len(values) - window_steps + 1, stride_steps):
        stop = start + window_steps
        window = values[start:stop]
        if np.isfinite(window).all():
            windows.append(window.T)
            starts.append(timestamps[start].to_datetime64())

    if not windows:
        raise ValueError("No complete windows were produced. Try a shorter window or larger interpolation limit.")

    return np.stack(windows).astype(np.float32), np.array(starts)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, default=DEFAULT_WORKBOOK)
    parser.add_argument("--sheet", default="cons_hostatgeria_underfloor_hea")
    parser.add_argument("--resample-interval", default="15min")
    parser.add_argument("--window-hours", type=int, default=24)
    parser.add_argument("--stride-hours", type=int, default=12)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "Results" / "processed_data")
    parser.add_argument("--summary-dir", type=Path, default=ROOT / "Results" / "tables")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frame = load_feature_frame(args.workbook, args.sheet, args.resample_interval)
    steps_per_hour = pd.Timedelta(hours=1) / pd.Timedelta(args.resample_interval)
    window_steps = int(args.window_hours * steps_per_hour)
    stride_steps = int(args.stride_hours * steps_per_hour)

    raw_values = frame.loc[:, FEATURES].to_numpy(dtype=np.float32)
    means = raw_values.mean(axis=0)
    stds = raw_values.std(axis=0)
    stds[stds == 0] = 1.0
    scaled_values = (raw_values - means) / stds
    windows, starts = make_windows(scaled_values, frame.index, window_steps, stride_steps)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.summary_dir.mkdir(parents=True, exist_ok=True)
    slug = clean_name(args.sheet)
    output_path = args.output_dir / f"autoencoder_windows_{slug}.npz"
    np.savez_compressed(
        output_path,
        windows=windows,
        window_start=starts,
        feature_names=np.array(FEATURES),
        means=means,
        stds=stds,
        sheet=args.sheet,
        resample_interval=args.resample_interval,
        window_hours=args.window_hours,
        stride_hours=args.stride_hours,
    )

    summary = pd.DataFrame(
        [
            {
                "sheet": args.sheet,
                "resample_interval": args.resample_interval,
                "window_hours": args.window_hours,
                "stride_hours": args.stride_hours,
                "resampled_rows": len(frame),
                "windows": len(windows),
                "features": ", ".join(FEATURES),
                "start": frame.index.min(),
                "end": frame.index.max(),
                "output": output_path,
            }
        ]
    )
    summary_path = args.summary_dir / f"autoencoder_windows_{slug}_summary.csv"
    summary.to_csv(summary_path, index=False)
    print(summary.to_string(index=False))
    print(f"\nWrote windows: {output_path}")
    print(f"Wrote summary: {summary_path}")


if __name__ == "__main__":
    main()
