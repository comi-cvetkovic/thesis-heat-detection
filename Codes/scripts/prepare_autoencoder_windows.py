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

from Codes.src.features import add_flow_from_power, add_stabilized_flow_from_power


DEFAULT_WORKBOOK = ROOT / "Data" / "DHC network" / "data" / "District Heating_updated_16_07_2025_2.xlsx"
TIMESTAMP_COL = "Time stamp"
POWER_COL = "Power Interval Trend Log"
RETURN_COL = "Return Temperature Interval Trend Log"
SUPPLY_COL = "Supply Temperature Interval Trend Log"
BASE_FEATURES = ("supply_temp_c", "return_temp_c")


def clean_name(value: str) -> str:
    return value.lower().replace(" ", "_").replace("/", "_").replace("\\", "_")


def resolve_flow_feature_name(flow_feature_mode: str) -> str:
    if flow_feature_mode == "raw":
        return "derived_flow_kg_s"
    if flow_feature_mode == "stabilized_log":
        return "stabilized_flow_log_feature"
    raise ValueError(f"Unsupported flow_feature_mode: {flow_feature_mode}")


def load_feature_frame(
    workbook: Path,
    sheet: str,
    resample_interval: str,
    flow_feature_mode: str,
    min_delta_t_c: float,
    flow_clip_quantile: float,
) -> tuple[pd.DataFrame, tuple[str, str, str]]:
    frame = pd.read_excel(workbook, sheet_name=sheet).dropna(how="all")
    frame[TIMESTAMP_COL] = pd.to_datetime(frame[TIMESTAMP_COL], errors="coerce", dayfirst=True)
    frame = frame.dropna(subset=[TIMESTAMP_COL]).sort_values(TIMESTAMP_COL)
    if flow_feature_mode == "raw":
        frame = add_flow_from_power(
            frame,
            power_col=POWER_COL,
            supply_col=SUPPLY_COL,
            return_col=RETURN_COL,
            output_col="derived_flow_kg_s",
            power_unit="kW",
        )
    elif flow_feature_mode == "stabilized_log":
        frame = add_flow_from_power(
            frame,
            power_col=POWER_COL,
            supply_col=SUPPLY_COL,
            return_col=RETURN_COL,
            output_col="derived_flow_kg_s",
            power_unit="kW",
        )
        frame = add_stabilized_flow_from_power(
            frame,
            power_col=POWER_COL,
            supply_col=SUPPLY_COL,
            return_col=RETURN_COL,
            output_col="stabilized_flow_log_feature",
            power_unit="kW",
            min_delta_t_c=min_delta_t_c,
            clip_quantile=flow_clip_quantile,
            log_transform=True,
        )
    else:
        raise ValueError(f"Unsupported flow_feature_mode: {flow_feature_mode}")

    frame["supply_temp_c"] = pd.to_numeric(frame[SUPPLY_COL], errors="coerce")
    frame["return_temp_c"] = pd.to_numeric(frame[RETURN_COL], errors="coerce")
    frame["power_kw"] = pd.to_numeric(frame[POWER_COL], errors="coerce")
    flow_feature_name = resolve_flow_feature_name(flow_feature_mode)
    frame["is_active_heating"] = (
        (frame["power_kw"] > 0)
        & (frame["delta_t_c"] > 0)
        & np.isfinite(frame[flow_feature_name])
        & (frame[flow_feature_name] > 0)
    )
    frame = frame.set_index(TIMESTAMP_COL)

    feature_columns = BASE_FEATURES + (flow_feature_name,)
    for feature in feature_columns:
        frame.loc[~frame["is_active_heating"], feature] = np.nan

    feature_frame = frame.loc[:, list(feature_columns)].resample(resample_interval).median()
    feature_frame["active_fraction"] = frame["is_active_heating"].astype(float).resample(resample_interval).mean()
    feature_frame.loc[:, feature_columns] = feature_frame.loc[:, feature_columns].interpolate(method="time", limit=4)
    return feature_frame, feature_columns


def make_windows(
    feature_frame: pd.DataFrame,
    feature_columns: tuple[str, ...],
    timestamps: pd.DatetimeIndex,
    window_steps: int,
    stride_steps: int,
    min_active_fraction: float,
    min_complete_fraction: float,
) -> tuple[np.ndarray, np.ndarray]:
    windows: list[np.ndarray] = []
    starts: list[np.datetime64] = []

    values = feature_frame.loc[:, feature_columns].to_numpy(dtype=np.float32)
    active_fraction = feature_frame["active_fraction"].to_numpy(dtype=np.float32)
    finite_mask = np.isfinite(values).all(axis=1)

    for start in range(0, len(feature_frame) - window_steps + 1, stride_steps):
        stop = start + window_steps
        window = values[start:stop]
        window_finite = finite_mask[start:stop]
        window_active = active_fraction[start:stop]
        complete_fraction = float(window_finite.mean())
        finite_active = window_active[np.isfinite(window_active)]
        active_share = 0.0 if len(finite_active) == 0 else float(finite_active.mean())
        if complete_fraction < min_complete_fraction:
            continue
        if active_share < min_active_fraction:
            continue

        imputed = window.copy()
        if not np.isfinite(imputed).all():
            column_means = np.nanmean(imputed, axis=0)
            missing_rows, missing_cols = np.where(~np.isfinite(imputed))
            imputed[missing_rows, missing_cols] = column_means[missing_cols]

        if np.isfinite(imputed).all():
            windows.append(imputed.T)
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
    parser.add_argument("--flow-feature-mode", choices=["raw", "stabilized_log"], default="raw")
    parser.add_argument("--min-delta-t-c", type=float, default=2.0)
    parser.add_argument("--flow-clip-quantile", type=float, default=0.995)
    parser.add_argument("--min-active-fraction", type=float, default=0.6)
    parser.add_argument("--min-complete-fraction", type=float, default=0.85)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "Results" / "processed_data")
    parser.add_argument("--summary-dir", type=Path, default=ROOT / "Results" / "tables")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frame, feature_columns = load_feature_frame(
        args.workbook,
        args.sheet,
        args.resample_interval,
        args.flow_feature_mode,
        args.min_delta_t_c,
        args.flow_clip_quantile,
    )
    steps_per_hour = pd.Timedelta(hours=1) / pd.Timedelta(args.resample_interval)
    window_steps = int(args.window_hours * steps_per_hour)
    stride_steps = int(args.stride_hours * steps_per_hour)

    valid_rows = np.isfinite(frame.loc[:, feature_columns]).all(axis=1)
    raw_values = frame.loc[valid_rows, feature_columns].to_numpy(dtype=np.float32)
    means = raw_values.mean(axis=0)
    stds = raw_values.std(axis=0)
    stds[stds == 0] = 1.0
    scaled_frame = frame.copy()
    scaled_frame.loc[:, feature_columns] = (scaled_frame.loc[:, feature_columns] - means) / stds
    windows, starts = make_windows(
        scaled_frame,
        feature_columns,
        frame.index,
        window_steps,
        stride_steps,
        min_active_fraction=args.min_active_fraction,
        min_complete_fraction=args.min_complete_fraction,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.summary_dir.mkdir(parents=True, exist_ok=True)
    slug = clean_name(args.sheet)
    output_suffix = "" if args.flow_feature_mode == "raw" else f"_{args.flow_feature_mode}"
    output_path = args.output_dir / f"autoencoder_windows_{slug}{output_suffix}.npz"
    np.savez_compressed(
        output_path,
        windows=windows,
        window_start=starts,
        feature_names=np.array(feature_columns),
        means=means,
        stds=stds,
        sheet=args.sheet,
        resample_interval=args.resample_interval,
        window_hours=args.window_hours,
        stride_hours=args.stride_hours,
        flow_feature_mode=args.flow_feature_mode,
        min_delta_t_c=args.min_delta_t_c,
        flow_clip_quantile=args.flow_clip_quantile,
        min_active_fraction=args.min_active_fraction,
        min_complete_fraction=args.min_complete_fraction,
    )

    summary = pd.DataFrame(
        [
            {
                "sheet": args.sheet,
                "resample_interval": args.resample_interval,
                "window_hours": args.window_hours,
                "stride_hours": args.stride_hours,
                "flow_feature_mode": args.flow_feature_mode,
                "min_delta_t_c": args.min_delta_t_c,
                "flow_clip_quantile": args.flow_clip_quantile,
                "resampled_rows": len(frame),
                "windows": len(windows),
                "features": ", ".join(feature_columns),
                "start": frame.index.min(),
                "end": frame.index.max(),
                "complete_rows": int(valid_rows.sum()),
                "output": output_path,
            }
        ]
    )
    summary_path = args.summary_dir / f"autoencoder_windows_{slug}{output_suffix}_summary.csv"
    summary.to_csv(summary_path, index=False)
    print(summary.to_string(index=False))
    print(f"\nWrote windows: {output_path}")
    print(f"Wrote summary: {summary_path}")


if __name__ == "__main__":
    main()
