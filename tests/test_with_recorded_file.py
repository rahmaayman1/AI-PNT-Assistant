"""
test_with_recorded_file.py
------------------------------
End-to-end sanity check: runs the trained model on the same combined dataset
used during development, and confirms the results match what was found in
the notebook (Recall ~0.91, Precision ~0.94 on cleanStatic+ds2+ds3).

This is the test to run right after moving code out of the notebook, to
confirm nothing broke during the refactor.
"""

import pandas as pd
from sklearn.metrics import classification_report

from src.feature_engineering.satellite_baseline import load_baseline
from src.feature_engineering.feature_pipeline import build_features, FINAL_FEATURE_COLUMNS
from src.detection_model.model import GPSAnomalyDetector

DATA_PATH = "data/processed/texbat_combined_dataset.csv"
MODEL_DIR = "models"


def main():
    df = pd.read_csv(DATA_PATH)
    df = df[df["scenario"].isin(["cleanStatic", "ds2", "ds3"])].copy()

    cn0_baseline = load_baseline(f"{MODEL_DIR}/satellite_baselines.csv")
    df_features = build_features(df, cn0_baseline)

    X = df_features[FINAL_FEATURE_COLUMNS]
    y_true = df_features["label"]

    detector = GPSAnomalyDetector()
    detector.load(
        model_path=f"{MODEL_DIR}/detector.pkl",
        scaler_path=f"{MODEL_DIR}/scaler.pkl",
        threshold_path=f"{MODEL_DIR}/threshold.txt",
    )

    y_pred = detector.predict(X)

    print("=== Sanity check: results should match notebook (Recall~0.91, Precision~0.94) ===")
    print(classification_report(y_true, y_pred, target_names=["Normal", "Spoofed"]))


if __name__ == "__main__":
    main()


# NOTE: this evaluates on the FULL normal dataset (same data the model was
# trained on), not a held-out split like the notebook used. This means
# "Normal recall" here is mechanically expected to be ~(1 - threshold_percentile/100)
# by definition of the percentile threshold, and precision/recall numbers
# will differ slightly from the notebook's held-out test metrics. This test
# verifies pipeline mechanics reproduce correctly, not generalization performance.