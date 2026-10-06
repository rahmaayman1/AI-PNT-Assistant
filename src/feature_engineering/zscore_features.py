"""
zscore_features.py
------------------
v2 feature builder for the GPS spoofing detector.

For every satellite, measure how far the current C/N0 is from that satellite's
normal level (z-score), then smooth it with causal rolling means over three
window sizes (5, 25, 50 samples = 1, 5, 10 seconds at 5 Hz).

Two interfaces that MUST give identical numbers (checked by the parity test):
  - add_zscore_features(): batch, for training and offline evaluation
  - StreamingZScoreFeatures: row-by-row, for main.py / live use
"""

from collections import defaultdict, deque

import numpy as np
import pandas as pd

WINDOWS = (5, 25, 50)
FEATURE_COLUMNS_V2 = [f"z_roll_mean_{w}" for w in WINDOWS]
STD_FLOOR_DB = 0.5          # minimum allowed baseline std (dB), safety net only
Z_COL = "cn0_zscore_per_satellite"


def compute_baseline(normal_df: pd.DataFrame, std_floor: float = STD_FLOOR_DB,
                     txid_col: str = "txid", value_col: str = "cn0") -> pd.DataFrame:
    """Per-satellite mean/std of C/N0 from NORMAL rows only (label == 0)."""
    base = normal_df.groupby(txid_col)[value_col].agg(["mean", "std"])
    base.columns = ["cn0_mu", "cn0_sd"]
    base["cn0_sd"] = base["cn0_sd"].clip(lower=std_floor)
    base.index = base.index.astype(float)
    base.index.name = "txid"
    return base


def save_baseline(baseline: pd.DataFrame, path: str) -> None:
    baseline.to_csv(path)


def load_baseline(path: str) -> pd.DataFrame:
    base = pd.read_csv(path, index_col=0)
    base.index = base.index.astype(float)
    base.index.name = "txid"
    return base


def add_zscore_features(df: pd.DataFrame, baseline: pd.DataFrame, windows=WINDOWS,
                        group_cols=("scenario", "txid"),
                        time_cols=("ort_whole_sec", "ort_frac_sec")) -> pd.DataFrame:
    """
    Batch version. Rows of satellites missing from the baseline are dropped
    (same behaviour as the notebook). Rolling windows are causal (past only)
    and computed per (scenario, txid) in time order.
    """
    out = df.copy()
    out["txid"] = pd.to_numeric(out["txid"]).astype(float)
    out = out.join(baseline[["cn0_mu", "cn0_sd"]], on="txid")
    out[Z_COL] = (out["cn0"] - out["cn0_mu"]) / out["cn0_sd"]
    out = out.dropna(subset=[Z_COL])

    out = out.sort_values(list(group_cols) + list(time_cols), kind="mergesort").reset_index(drop=True)
    grouped = out.groupby(list(group_cols))[Z_COL]
    for w in windows:
        out[f"z_roll_mean_{w}"] = grouped.transform(lambda s, w=w: s.rolling(w, min_periods=1).mean())
    return out


class StreamingZScoreFeatures:
    """
    Streaming version. Keeps the last max(windows) z-scores of every satellite,
    so chunking the stream never resets the rolling windows (the v1 chunking issue).
    Rows must be fed in time order.
    """

    def __init__(self, baseline: pd.DataFrame, windows=WINDOWS):
        self.windows = tuple(windows)
        self.mu = baseline["cn0_mu"].to_dict()
        self.sd = baseline["cn0_sd"].to_dict()
        self.buffers = defaultdict(lambda: deque(maxlen=max(self.windows)))
        self.unknown_rows = 0   # rows from satellites that are not in the baseline

    def update(self, txid: float, cn0: float):
        """Returns a dict of features, or None if the satellite has no baseline."""
        key = float(txid)
        if key not in self.mu or not np.isfinite(cn0):
            self.unknown_rows += 1
            return None
        z = (cn0 - self.mu[key]) / self.sd[key]
        buf = self.buffers[key]
        buf.append(z)
        arr = np.fromiter(buf, dtype=float)
        feats = {Z_COL: z}
        for w in self.windows:
            feats[f"z_roll_mean_{w}"] = arr[-w:].mean()
        return feats

    def update_frame(self, chunk: pd.DataFrame) -> pd.DataFrame:
        """Process a chunk (already time-ordered); returns rows that got features."""
        rows = []
        for idx, txid, cn0 in zip(chunk.index, chunk["txid"], chunk["cn0"]):
            feats = self.update(txid, cn0)
            if feats is not None:
                feats["_index"] = idx
                rows.append(feats)
        if not rows:
            return pd.DataFrame(columns=[Z_COL] + FEATURE_COLUMNS_V2)
        res = pd.DataFrame(rows).set_index("_index")
        return chunk.join(res, how="inner")