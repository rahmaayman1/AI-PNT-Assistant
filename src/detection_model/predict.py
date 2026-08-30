"""
Loads a trained detector and runs inference on an ALREADY-PROCESSED feature
matrix (i.e. after build_features() has already been applied, typically by
run_pipeline.py). This script does NOT re-run feature engineering - it
expects the input CSV to already contain the final feature columns.

Usage:
    python -m src.detection_model.predict --data data/output/feature_matrix.csv
"""

import argparse
import pandas as pd

from src.feature_engineering.feature_pipeline import FINAL_FEATURE_COLUMNS
from src.detection_model.model import GPSAnomalyDetector


def main(data_path: str, model_dir: str = "models"):
    df = pd.read_csv(data_path)

    missing_cols = [c for c in FINAL_FEATURE_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Input file is missing required feature columns: {missing_cols}. "
            f"This script expects an already-processed feature matrix "
            f"(output of build_features()), not raw observable data."
        )

    X = df[FINAL_FEATURE_COLUMNS]

    detector = GPSAnomalyDetector()
    detector.load(
        model_path=f"{model_dir}/detector.pkl",
        scaler_path=f"{model_dir}/scaler.pkl",
        threshold_path=f"{model_dir}/threshold.txt",
    )

    df["anomaly_score"] = detector.anomaly_score(X)
    df["prediction"] = detector.predict(X)  # 1 = spoofed, 0 = normal

    output_path = data_path.replace(".csv", "_predictions.csv")
    df.to_csv(output_path, index=False)

    print(f"Predictions saved to: {output_path}")
    print(df["prediction"].value_counts())
    print()
    print("Anomaly score summary:")
    print(df["anomaly_score"].describe())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run spoofing detection on a pre-built feature matrix")
    parser.add_argument("--data", required=True, help="Path to feature matrix CSV (already processed)")
    parser.add_argument("--model_dir", default="models", help="Directory containing trained model artifacts")
    args = parser.parse_args()

    main(args.data, args.model_dir)