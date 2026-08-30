"""
observable_parser.py

Converts GNSS-SDR tracking dump (.mat, MATLAB v7.3 / HDF5 format) into the
target schema used across this project:
    [txid, cn0, doppler_hz, ort_whole_sec, ort_frac_sec]

Data source: reads directly from tracking_ch_N.mat files (NOT observables.mat),
since CN0 is only available in the tracking dumps. PRN and carrier_doppler_hz
are read from the same file, so no cross-file join is needed.

Confirmed from real data inspection:
1. CN0_SNV_dB_Hz has a fixed warm-up period of exactly 20 zero-valued samples
   at the start of every channel, before the estimator converges to realistic
   values (~28-55 dB-Hz). These leading samples are dropped.
2. GNSS-SDR tracking loop outputs one sample per ~1 ms (1000 Hz), while the
   TEXBAT training data (channel.mat / texbat_*_channel_clean.csv) is at
   0.2 s intervals (5 Hz) per satellite. This is a ~200x mismatch in temporal
   density. To preserve the meaning of rolling-window features that were
   tuned against 5 Hz data, GNSS-SDR output is downsampled to 5 Hz by
   averaging cn0 and doppler_hz within each 200 ms bin, per satellite.
"""

import glob
import os
import h5py
import numpy as np
import pandas as pd

# Must match SignalSource.sampling_frequency in the GNSS-SDR .conf file
SAMPLING_FREQUENCY_HZ = 25_000_000

# Confirmed via real data inspection: CN0_SNV_dB_Hz estimator warm-up period
# is exactly 20 samples (zero-valued) at the start of every channel.
WARMUP_SKIP_SAMPLES = 20

# Confirmed from TEXBAT training data: consecutive readings per satellite are
# spaced exactly 0.2 s apart (5 Hz). GNSS-SDR raw tracking output is
# downsampled to match this rate.
DOWNSAMPLE_INTERVAL_SEC = 0.2


def parse_tracking_file(filepath: str) -> pd.DataFrame:
    """
    Reads a single tracking_ch_N.mat file and returns a raw (not yet
    downsampled) DataFrame with columns:
    [txid, cn0, doppler_hz, ort_whole_sec, ort_frac_sec]
    at the native ~1 kHz tracking loop rate.
    """
    with h5py.File(filepath, "r") as f:
        prn = np.array(f["PRN"]).flatten()
        cn0 = np.array(f["CN0_SNV_dB_Hz"]).flatten()
        doppler_hz = np.array(f["carrier_doppler_hz"]).flatten()
        sample_count = np.array(f["PRN_start_sample_count"]).flatten()

    # Convert sample count to absolute receiver time in seconds
    time_sec = sample_count.astype(np.float64) / SAMPLING_FREQUENCY_HZ

    df = pd.DataFrame({
        "txid": prn.astype(np.int64),
        "cn0": cn0.astype(np.float64),
        "doppler_hz": doppler_hz.astype(np.float64),
        "time_sec": time_sec,
    })

    # Drop the fixed warm-up period where CN0 estimator has not converged yet
    if WARMUP_SKIP_SAMPLES > 0:
        df = df.iloc[WARMUP_SKIP_SAMPLES:].reset_index(drop=True)

    return df


def downsample_to_target_rate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Downsamples a single-satellite DataFrame (native ~1 kHz) to
    DOWNSAMPLE_INTERVAL_SEC (0.2 s / 5 Hz) by averaging cn0 and doppler_hz
    within each time bin. This matches the temporal density of the TEXBAT
    training data so rolling-window features stay meaningful.
    """
    df = df.copy()
    df["bin_index"] = (df["time_sec"] // DOWNSAMPLE_INTERVAL_SEC).astype(np.int64)

    grouped = df.groupby("bin_index").agg(
        txid=("txid", "first"),
        cn0=("cn0", "mean"),
        doppler_hz=("doppler_hz", "mean"),
        time_sec=("time_sec", "mean"),
        sample_count=("cn0", "size"),  # useful for QA, not part of target schema
    ).reset_index(drop=True)

    ort_whole_sec = np.floor(grouped["time_sec"]).astype(np.int64)
    ort_frac_sec = grouped["time_sec"] - ort_whole_sec

    result = pd.DataFrame({
        "txid": grouped["txid"],
        "cn0": grouped["cn0"],
        "doppler_hz": grouped["doppler_hz"],
        "ort_whole_sec": ort_whole_sec,
        "ort_frac_sec": ort_frac_sec,
    })

    return result


def parse_all_tracking_files(output_dir: str = "data/output") -> pd.DataFrame:
    """
    Parses every tracking_ch_*.mat file in output_dir, downsamples each
    satellite's stream to 5 Hz independently, then concatenates and sorts
    the result by time. Output matches the structure expected by
    feature_pipeline.py.
    """
    filepaths = sorted(glob.glob(os.path.join(output_dir, "tracking_ch_*.mat")))
    if not filepaths:
        raise FileNotFoundError(f"No tracking_ch_*.mat files found in {output_dir}")

    downsampled_frames = []
    for fp in filepaths:
        raw_df = parse_tracking_file(fp)
        downsampled_frames.append(downsample_to_target_rate(raw_df))

    combined = pd.concat(downsampled_frames, ignore_index=True)
    combined = combined.sort_values(
        by=["ort_whole_sec", "ort_frac_sec"]
    ).reset_index(drop=True)

    return combined


if __name__ == "__main__":
    result = parse_all_tracking_files()
    print(result.head(20))
    print(f"\nTotal rows: {len(result)}")
    print(f"Unique satellites (txid): {sorted(result['txid'].unique())}")
    print(f"CN0 stats -> min: {result['cn0'].min():.2f}, "
          f"max: {result['cn0'].max():.2f}, "
          f"mean: {result['cn0'].mean():.2f}")
    print(f"Rows per satellite:")
    print(result['txid'].value_counts().sort_index())