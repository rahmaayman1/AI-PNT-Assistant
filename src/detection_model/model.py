"""
GPSAnomalyDetector: wraps Isolation Forest + percentile-based thresholding.
"""

import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class GPSAnomalyDetector:
    def __init__(self, n_estimators: int = 200, random_state: int = 42):
        self.model = IsolationForest(
            n_estimators=n_estimators,
            random_state=random_state,
        )
        self.scaler = StandardScaler()
        self.threshold = None
        self.is_fitted = False

    def fit(self, X_train, threshold_percentile: float = 20):
        X_scaled = self.scaler.fit_transform(X_train)
        self.model.fit(X_scaled)
        train_scores = self.model.decision_function(X_scaled)
        self.threshold = np.percentile(train_scores, threshold_percentile)
        self.is_fitted = True
        return self

    def anomaly_score(self, X):
        if not self.is_fitted:
            raise RuntimeError("Model is not fitted yet - call fit() first")
        X_scaled = self.scaler.transform(X)
        return self.model.decision_function(X_scaled)

    def predict(self, X):
        """Returns 1 = anomaly (spoofed), 0 = normal, based on the calibrated threshold."""
        scores = self.anomaly_score(X)
        return (scores < self.threshold).astype(int)

    def save(self, model_path: str, scaler_path: str, threshold_path: str):
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        with open(threshold_path, "w") as f:
            f.write(str(self.threshold))

    def load(self, model_path: str, scaler_path: str, threshold_path: str):
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        with open(threshold_path, "r") as f:
            self.threshold = float(f.read())
        self.is_fitted = True
        return self