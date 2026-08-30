"""
feature_pipeline.py
-------------------
Builds the features used by the anomaly detection model.
"""

if __name__ == "__main__" and __package__ is None:
    import sys
    from pathlib import Path
    project_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(project_root))
    __package__ = "src.feature_engineering"

import pandas as pd
from .satellite_baseline import apply_satellite_zscore
from .rolling_features import add_all_rolling_features

FINAL_FEATURE_COLUMNS = [
    "cn0_zscore_per_satellite",
    "cn0_rolling_std", "cn0_diff",
    "doppler_rolling_std", "doppler_diff",
]


def build_features(df: pd.DataFrame, cn0_baseline: pd.DataFrame,
                    group_cols: list = None) -> pd.DataFrame:
    """
    df: raw channel-level DataFrame with at least these columns:
        ["scenario", "txid", "ort_whole_sec", "ort_frac_sec", "cn0", "doppler_hz"]
    cn0_baseline: per-satellite baseline computed via
        satellite_baseline.compute_satellite_baseline() on normal training data.

    Returns df with all FINAL_FEATURE_COLUMNS added.
    """
    if group_cols is None:
        group_cols = ["scenario", "txid"]

    df = add_all_rolling_features(df, group_cols=group_cols,
                                   value_cols=["cn0", "doppler_hz"], window=10)
    df = apply_satellite_zscore(df, cn0_baseline, txid_col="txid", value_col="cn0")

    # Rows whose satellite wasn't seen during training have no baseline -> drop them,
    # since we can't normalize them reliably.
    df = df.dropna(subset=["cn0_zscore_per_satellite"])

    return df


def get_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Returns just the final feature columns, ready to feed into the model."""
    return df[FINAL_FEATURE_COLUMNS]


if __name__ == "__main__":
    print("feature_pipeline module imported/executed successfully")