"""Feature engineering helpers for district heating/cooling time series."""

from __future__ import annotations

import numpy as np
import pandas as pd


WATER_CP_J_PER_KG_C = 4180.0


def add_delta_t(
    frame: pd.DataFrame,
    supply_col: str,
    return_col: str,
    output_col: str = "delta_t_c",
) -> pd.DataFrame:
    """Add temperature difference, `Ts - Tr`, to a copy of `frame`."""
    result = frame.copy()
    result[output_col] = pd.to_numeric(result[supply_col], errors="coerce") - pd.to_numeric(
        result[return_col],
        errors="coerce",
    )
    return result


def add_flow_from_power(
    frame: pd.DataFrame,
    power_col: str,
    supply_col: str,
    return_col: str,
    output_col: str = "flow_kg_s",
    cp_j_per_kg_c: float = WATER_CP_J_PER_KG_C,
    power_unit: str = "W",
) -> pd.DataFrame:
    """Add mass flow rate using `m = Power / (Cp * (Ts - Tr))`.

    Set `power_unit="kW"` when the source power column is stored in kilowatts.
    Invalid or zero temperature differences are returned as NaN.
    """
    result = add_delta_t(frame, supply_col=supply_col, return_col=return_col)
    power = pd.to_numeric(result[power_col], errors="coerce")
    if power_unit.lower() == "kw":
        power = power * 1000.0
    elif power_unit.lower() != "w":
        raise ValueError("power_unit must be either 'W' or 'kW'.")

    delta_t = result["delta_t_c"].replace(0, np.nan)
    result[output_col] = power / (cp_j_per_kg_c * delta_t)
    return result


def add_stabilized_flow_from_power(
    frame: pd.DataFrame,
    power_col: str,
    supply_col: str,
    return_col: str,
    output_col: str = "stabilized_flow_feature",
    cp_j_per_kg_c: float = WATER_CP_J_PER_KG_C,
    power_unit: str = "W",
    min_delta_t_c: float = 2.0,
    clip_quantile: float = 0.995,
    log_transform: bool = True,
) -> pd.DataFrame:
    """Add a flow-derived feature that is less sensitive to near-zero delta-T.

    The denominator is floored at `min_delta_t_c`, the resulting positive flow values
    are winsorized at `clip_quantile`, and the feature can optionally be log-scaled.
    """
    if min_delta_t_c <= 0:
        raise ValueError("min_delta_t_c must be positive.")
    if not 0 < clip_quantile <= 1:
        raise ValueError("clip_quantile must be in the interval (0, 1].")

    result = add_delta_t(frame, supply_col=supply_col, return_col=return_col)
    power = pd.to_numeric(result[power_col], errors="coerce")
    if power_unit.lower() == "kw":
        power = power * 1000.0
    elif power_unit.lower() != "w":
        raise ValueError("power_unit must be either 'W' or 'kW'.")

    delta_t = pd.to_numeric(result["delta_t_c"], errors="coerce")
    stabilized_delta = delta_t.clip(lower=min_delta_t_c)
    flow = power / (cp_j_per_kg_c * stabilized_delta)
    positive_flow = flow.where(flow > 0)
    clip_value = positive_flow.quantile(clip_quantile)
    clipped_flow = positive_flow.clip(upper=clip_value)
    result[output_col] = np.log1p(clipped_flow) if log_transform else clipped_flow
    return result


def add_power_from_flow(
    frame: pd.DataFrame,
    flow_col: str,
    supply_col: str,
    return_col: str,
    output_col: str = "power_w",
    cp_j_per_kg_c: float = WATER_CP_J_PER_KG_C,
) -> pd.DataFrame:
    """Add thermal power using `Power = m * Cp * (Ts - Tr)`."""
    result = add_delta_t(frame, supply_col=supply_col, return_col=return_col)
    flow = pd.to_numeric(result[flow_col], errors="coerce")
    result[output_col] = flow * cp_j_per_kg_c * result["delta_t_c"]
    return result
