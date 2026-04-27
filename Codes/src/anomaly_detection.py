"""Robust anomaly detection baselines for heating time series."""

from __future__ import annotations

import numpy as np
import pandas as pd


def median_absolute_deviation(values: pd.Series) -> float:
    """Return the median absolute deviation, ignoring missing values."""
    clean = pd.to_numeric(values, errors="coerce").dropna()
    if clean.empty:
        return np.nan

    median = clean.median()
    return float((clean - median).abs().median())


def modified_z_score(values: pd.Series) -> pd.Series:
    """Compute robust modified z-scores using the MAD denominator."""
    numeric = pd.to_numeric(values, errors="coerce")
    median = numeric.median(skipna=True)
    mad = median_absolute_deviation(numeric)

    if pd.isna(mad) or mad == 0:
        return pd.Series(np.nan, index=values.index, name=f"{values.name}_modified_z")

    return 0.6745 * (numeric - median) / mad


def flag_low_delta_t(
    frame: pd.DataFrame,
    delta_t_col: str = "delta_t_c",
    z_threshold: float = -3.5,
    output_col: str = "is_low_delta_t_anomaly",
) -> pd.DataFrame:
    """Flag unusually low temperature differences using modified z-scores."""
    result = frame.copy()
    z_col = f"{delta_t_col}_modified_z"
    result[z_col] = modified_z_score(result[delta_t_col])
    result[output_col] = result[z_col] <= z_threshold
    return result


def flag_groupwise_low_delta_t(
    frame: pd.DataFrame,
    group_col: str,
    delta_t_col: str = "delta_t_c",
    z_threshold: float = -3.5,
    output_col: str = "is_cluster_low_delta_t_anomaly",
) -> pd.DataFrame:
    """Flag low delta-T anomalies within each group or cluster."""
    result = frame.copy()
    z_col = f"{delta_t_col}_group_modified_z"
    result[z_col] = result.groupby(group_col, group_keys=False)[delta_t_col].apply(modified_z_score)
    result[output_col] = result[z_col] <= z_threshold
    return result

