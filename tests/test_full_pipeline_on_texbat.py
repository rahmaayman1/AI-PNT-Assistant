"""
test_full_pipeline_on_texbat.py
-----------------------------------
End-to-end check on a real labeled TEXBAT scenario (not just the combined
dataset): loads ds2 specifically, runs it through the exact same feature
pipeline and trained model used in main.py, and confirms detection
performance matches the notebook's per-scenario result (ds2 recall = 1.00).

Differs from test_with_recorded_file.py, which checks aggregate performance
across the full combined dataset (ds2+ds3+cleanStatic together).
"""

import pandas as pd
from sklearn.metrics import classification_report

from src.feature_engineering.satellite_baseline import load_baseline
from src.feature_engineering.feature_pipeline import build_features, FINAL_FEATURE_COLUMNS
from src.detection_model.model import GPSAnomalyDetector


def main():
    df = pd.read_csv("data/output/texbat_ds2_channel_labeled.csv")
    df["scenario"] = "ds2"

    cn0_baseline = load_baseline("models/satellite_baselines.csv")
    features_df = build_features(df, cn0_baseline)

    detector = GPSAnomalyDetector()
    detector.load("models/detector.pkl", "models/scaler.pkl", "models/threshold.txt")

    X = features_df[FINAL_FEATURE_COLUMNS]
    features_df["prediction"] = detector.predict(X)

    print("=== ds2-specific check (should match notebook: recall = 1.00) ===")
    print(classification_report(features_df["label"], features_df["prediction"],
                                 target_names=["Normal", "Spoofed"]))


if __name__ == "__main__":
    main()