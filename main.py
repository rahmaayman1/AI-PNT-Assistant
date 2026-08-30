"""
main.py
--------
Entry point that wires together: signal source -> feature engineering ->
detection model -> switching logic -> PNT engine.
"""

import yaml

from src.signal_acquisition.source_factory import get_source
from src.feature_engineering.satellite_baseline import load_baseline
from src.feature_engineering.feature_pipeline import build_features, FINAL_FEATURE_COLUMNS
from src.detection_model.model import GPSAnomalyDetector
from src.switching_logic.decision_engine import SwitchingDecisionEngine
from src.network_acquisition.station_source_factory import get_station_source
from src.pnt_engine.tdoa import estimate_position_tdoa


def load_config(path: str = "configs/config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def main():
    config = load_config()

    source = get_source(config)
    cn0_baseline = load_baseline(f"{config['detection_model']['model_dir']}/satellite_baselines.csv")
    station_source = get_station_source(config)

    detector = GPSAnomalyDetector()
    detector.load(
        model_path=f"{config['detection_model']['model_dir']}/detector.pkl",
        scaler_path=f"{config['detection_model']['model_dir']}/scaler.pkl",
        threshold_path=f"{config['detection_model']['model_dir']}/threshold.txt",
    )

    switch = SwitchingDecisionEngine(
        hysteresis_window=config["switching_logic"]["hysteresis_window"]
    )

    for chunk in source.stream():
        if "scenario" not in chunk.columns:
         chunk["scenario"] = "ds2"
        features_df = build_features(chunk, cn0_baseline)
        if features_df.empty:
            continue

        X = features_df[FINAL_FEATURE_COLUMNS]
        predictions = detector.predict(X)

        for pred in predictions:
            source_decision = switch.update(pred)

            if source_decision == "gps":
                print("Prediction: normal -> Using GPS position")
            else:
                # Fallback: compute position from network stations instead of GPS
                station_coords, time_diffs = station_source.get_measurements()
                position = estimate_position_tdoa(station_coords, time_diffs)
                print(f"Prediction: SPOOFED -> Switched to network. Estimated position: {position}")


if __name__ == "__main__":
    main()