"""
satellite_baseline.py
-----------------------
Computes and stores per-satellite baseline statistics (mean, std) for C/N0.

Why this exists: different satellites have naturally different C/N0 levels
depending on signal strength and elevation angle (e.g. a weak satellite might
average ~36 dB-Hz while a strong one averages ~53 dB-Hz). Feeding raw C/N0
into a model directly causes it to confuse "naturally weak satellite" with
"anomalous satellite". Normalizing per-satellite (z-score against its own
baseline) fixes this.

IMPORTANT: baselines must always be computed from normal (label=0) TRAINING
data only, never from test/attack data, to avoid data leakage.
"""

import pandas as pd


def compute_satellite_baseline(normal_train_df: pd.DataFrame, txid_col: str = "txid",
                                value_col: str = "cn0") -> pd.DataFrame:
    """
    Computes per-satellite mean/std for a given column, using normal training
    data only.

    Returns a DataFrame indexed by txid with columns:
        {value_col}_baseline_mean, {value_col}_baseline_std
    """
    baseline = normal_train_df.groupby(txid_col)[value_col].agg(["mean", "std"])
    baseline = baseline.rename(columns={
        "mean": f"{value_col}_baseline_mean",
        "std": f"{value_col}_baseline_std",
    })
    return baseline


def apply_satellite_zscore(df: pd.DataFrame, baseline: pd.DataFrame,
                            txid_col: str = "txid", value_col: str = "cn0") -> pd.DataFrame:
    """
    Merges the baseline into df and computes a per-satellite z-score column:
        {value_col}_zscore_per_satellite

    Rows whose txid is missing from the baseline (satellite never seen during
    training) will have NaN in the z-score column and should be dropped before
    scoring, since we have no reference to normalize them against.
    """
    # Ensure the txid column exists in df; if it's the index, reset it.
    if txid_col not in df.columns:
        if isinstance(df.index, pd.MultiIndex):
            # try to find txid in index level names
            if txid_col in df.index.names:
                df = df.reset_index()
        else:
            if df.index.name == txid_col:
                df = df.reset_index()

    if txid_col not in df.columns:
        raise KeyError(f"Expected txid column '{txid_col}' not found in dataframe. Available columns: {list(df.columns)}")

    # Ensure baseline has txid as a column (some callers save baseline with txid as index)
    if txid_col not in baseline.columns:
        baseline = baseline.reset_index()
        if txid_col not in baseline.columns:
            # fallback: rename first column to txid
            baseline = baseline.rename(columns={baseline.columns[0]: txid_col})

    # Coerce numeric types for reliable merging
    df[txid_col] = pd.to_numeric(df[txid_col], errors="coerce")
    baseline[txid_col] = pd.to_numeric(baseline[txid_col], errors="coerce")

    df = df.merge(baseline, on=txid_col, how="left")
    df[f"{value_col}_zscore_per_satellite"] = (
        (df[value_col] - df[f"{value_col}_baseline_mean"]) / df[f"{value_col}_baseline_std"]
    )
    return df


def save_baseline(baseline: pd.DataFrame, path: str):
    baseline.to_csv(path)


def load_baseline(path: str) -> pd.DataFrame:
    return pd.read_csv(path, index_col=0)