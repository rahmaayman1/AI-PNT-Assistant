"""
rolling_features.py
----------------------
Builds rolling-window statistics and rate-of-change (diff) features for a
single satellite's time series. Must be applied per (scenario, txid) group,
never across different satellites or scenarios mixed together, otherwise the
rolling window would blend unrelated time series.
"""

import pandas as pd


def add_rolling_features(group: pd.DataFrame, value_col: str, window: int = 10) -> pd.DataFrame:
    """
    Adds rolling mean, rolling std, and diff (rate of change) for a given
    column, computed within a single group (one satellite, one scenario).
    """
    group = group.copy()
    # Normalize base name for derived features: drop common suffixes like '_hz'
    base = value_col
    if base.endswith("_hz"):
        base = base[: -3]

    group[f"{base}_rolling_mean"] = group[value_col].rolling(window=window, min_periods=1).mean()
    group[f"{base}_rolling_std"] = group[value_col].rolling(window=window, min_periods=1).std().fillna(0)
    group[f"{base}_diff"] = group[value_col].diff().fillna(0)
    return group


def add_all_rolling_features(df: pd.DataFrame, group_cols: list, value_cols: list,
                              window: int = 10) -> pd.DataFrame:
    """
    Applies add_rolling_features for multiple value columns (e.g. cn0, doppler_hz),
    grouped by group_cols (e.g. ["scenario", "txid"]).
    """
    # Sort so rolling windows are computed in temporal order within each group
    df = df.sort_values(group_cols + ["ort_whole_sec", "ort_frac_sec"]).reset_index(drop=True)

    # Prepare an output frame that preserves all original columns and indices
    out = df.copy()

    # Initialize new columns to default values using normalized base names
    base_names = []
    for col in value_cols:
        base = col
        if base.endswith("_hz"):
            base = base[: -3]
        base_names.append(base)
        out[f"{base}_rolling_mean"] = None
        out[f"{base}_rolling_std"] = None
        out[f"{base}_diff"] = None

    # Process group-by-group and write results back into the original index positions
    for _, group_idx in df.groupby(group_cols).groups.items():
        group = df.loc[group_idx]
        processed = group.copy()
        for col in value_cols:
            processed = add_rolling_features(processed, col, window=window)
        # Assign back to out using the original indices; use base_names for column names
        out.loc[group_idx, [f"{b}_rolling_mean" for b in base_names]] = \
            processed[[f"{b}_rolling_mean" for b in base_names]]
        out.loc[group_idx, [f"{b}_rolling_std" for b in base_names]] = \
            processed[[f"{b}_rolling_std" for b in base_names]]
        out.loc[group_idx, [f"{b}_diff" for b in base_names]] = \
            processed[[f"{b}_diff" for b in base_names]]

    return out