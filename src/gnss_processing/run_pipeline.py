"""
run_pipeline.py

Glue script connecting observable_parser.py (real GNSS-SDR tracking data)
to feature_pipeline.py (the trained model's exact preprocessing).

This does NOT call model.predict() yet - that requires confirming
model.py's predict() interface first, so this step stops right before
that and prints the final feature matrix for inspection.
"""

import pandas as pd
from src.gnss_processing.observable_parser import parse_all_tracking_files
from src.feature_engineering.feature_pipeline import build_features, get_feature_matrix

# Fixed label for data coming from this live GNSS-SDR run, so grouping
# (group_cols=["scenario", "txid"]) does not mix it with TEXBAT scenarios.
LIVE_SCENARIO_LABEL = "gnss_sdr_live"

BASELINE_PATH = "models/satellite_baselines.csv"


def main():
    # Step 1: parse real GNSS-SDR tracking output into the target schema
    live_df = parse_all_tracking_files(output_dir="data/output")
    live_df["scenario"] = LIVE_SCENARIO_LABEL

    print(f"Parsed {len(live_df)} rows from GNSS-SDR tracking output.")
    print(f"Satellites present: {sorted(live_df['txid'].unique())}")

    # Step 2: load the per-satellite CN0 baseline computed during training
    cn0_baseline = pd.read_csv(BASELINE_PATH)

    # Step 3: build the exact same features used at training time
    featured_df = build_features(live_df, cn0_baseline)

    dropped_count = len(live_df) - len(featured_df)
    if dropped_count > 0:
        print(f"WARNING: {dropped_count} rows dropped "
              f"(no satellite baseline and/or insufficient rolling window history).")

    print(f"\nRows remaining after feature building: {len(featured_df)}")
    print(f"Satellites remaining: {sorted(featured_df['txid'].unique()) if len(featured_df) else 'NONE'}")

    # --- DIAGNOSTIC: compare live CN0 means against training baseline ---
    # This checks whether the mismatch we saw in z-scores is a systematic
    # calibration offset (affects all satellites similarly) or something
    # specific to individual satellites.
    live_means = featured_df.groupby("txid")["cn0"].mean()
    baseline_indexed = cn0_baseline.set_index("txid")

    comparison = pd.DataFrame({
        "live_cn0_mean": live_means,
        "baseline_mean": baseline_indexed["cn0_baseline_mean"],
        "baseline_std": baseline_indexed["cn0_baseline_std"],
    })
    comparison["offset"] = comparison["live_cn0_mean"] - comparison["baseline_mean"]
    comparison["typical_zscore"] = comparison["offset"] / comparison["baseline_std"]

    print("\nLive vs baseline CN0 comparison (diagnostic):")
    print(comparison)
    # --- END DIAGNOSTIC ---

    # Step 4: extract the final feature matrix, ready for model.predict()
    feature_matrix = get_feature_matrix(featured_df)
    print("\nFeature matrix preview:")
    print(feature_matrix.head(20))
    output_path = "data/output/feature_matrix.csv"
    feature_matrix_with_id = feature_matrix.copy()
    feature_matrix_with_id["txid"] = featured_df["txid"].values

    feature_matrix_with_id.to_csv(output_path, index=False)
    print(f"\nFeature matrix saved to: {output_path}")


    return featured_df, feature_matrix


if __name__ == "__main__":
    main()