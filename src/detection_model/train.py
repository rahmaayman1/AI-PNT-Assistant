"""
train.py
---------
Trains the final (v4) GPS anomaly detector on cleanStatic + ds2 + ds3
(ds7 intentionally excluded - evaluated separately as a documented limitation).

Usage:
    python -m src.detection_model.train --data data/processed/combined_labeled.csv
"""

import argparse
import pandas as pd

from src.feature_engineering.satellite_baseline import compute_satellite_baseline, save_baseline
from src.feature_engineering.feature_pipeline import build_features, FINAL_FEATURE_COLUMNS
from src.detection_model.model import GPSAnomalyDetector

TRAINING_SCENARIOS = ["cleanStatic", "ds2", "ds3"]


def main(data_path: str, model_dir: str = "models"):
    df = pd.read_csv(data_path)
    df = df[df["scenario"].isin(TRAINING_SCENARIOS)].copy()

    normal_df = df[df["label"] == 0]

    # Baseline must be computed from normal data only, to avoid leakage
    cn0_baseline = compute_satellite_baseline(normal_df, txid_col="txid", value_col="cn0")
    save_baseline(cn0_baseline, f"{model_dir}/satellite_baselines.csv")

    df_features = build_features(df, cn0_baseline)

    # Train only on normal readings
    train_df = df_features[df_features["label"] == 0]
    X_train = train_df[FINAL_FEATURE_COLUMNS]

    detector = GPSAnomalyDetector()
    detector.fit(X_train, threshold_percentile=20)

    detector.save(
        model_path=f"{model_dir}/detector.pkl",
        scaler_path=f"{model_dir}/scaler.pkl",
        threshold_path=f"{model_dir}/threshold.txt",
    )

    print(f"Model trained and saved to {model_dir}/")
    print(f"Threshold (percentile 20): {detector.threshold}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train the GPS spoofing anomaly detector")
    parser.add_argument("--data", required=True, help="Path to combined labeled dataset (CSV)")
    parser.add_argument("--model_dir", default="models", help="Directory to save model artifacts")
    args = parser.parse_args()

    main(args.data, args.model_dir)