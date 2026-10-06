import numpy as np
import pandas as pd

from src.feature_engineering.zscore_features import (
    FEATURE_COLUMNS_V2, StreamingZScoreFeatures, add_zscore_features, compute_baseline,
)


def _make_df():
    rng = np.random.default_rng(0)
    rows = []
    for txid in (3, 6, 11, 99):            # 99 is NOT in the baseline on purpose
        for i in range(400):
            t = 1000 + i * 0.2
            rows.append({"scenario": "s1", "txid": txid, "ort_whole_sec": int(t),
                         "ort_frac_sec": t - int(t),
                         "cn0": 45 + txid * 0.1 + rng.normal(0, 0.4) + (3 if i > 250 else 0),
                         "label": int(i > 250)})
    return pd.DataFrame(rows)


def test_batch_and_streaming_give_same_features():
    df = _make_df()
    base = compute_baseline(df[(df.label == 0) & (df.txid != 99)])
    batch = add_zscore_features(df, base)

    ordered = df.sort_values(["ort_whole_sec", "ort_frac_sec", "txid"]).reset_index(drop=True)
    stream = StreamingZScoreFeatures(base)
    parts = [stream.update_frame(ordered.iloc[i:i + 50]) for i in range(0, len(ordered), 50)]
    streamed = pd.concat(parts)

    key = ["txid", "ort_whole_sec", "ort_frac_sec"]
    b = batch.sort_values(key).reset_index(drop=True)
    s = streamed.sort_values(key).reset_index(drop=True)

    assert len(b) == len(s)
    assert stream.unknown_rows == 400            # all rows of satellite 99
    for c in FEATURE_COLUMNS_V2:
        assert np.allclose(b[c], s[c], atol=1e-9)