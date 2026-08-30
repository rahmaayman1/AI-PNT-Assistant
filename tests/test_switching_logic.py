"""
test_switching_logic.py
--------------------------
Tests the SwitchingDecisionEngine in isolation, using mock predictions
(no need for real data or a trained model).
"""

from src.switching_logic.decision_engine import SwitchingDecisionEngine


def test_stays_on_gps_when_all_normal():
    engine = SwitchingDecisionEngine(hysteresis_window=5)
    decisions = [engine.update(0) for _ in range(10)]
    assert all(d == "gps" for d in decisions)


def test_switches_to_network_when_majority_anomalous():
    engine = SwitchingDecisionEngine(hysteresis_window=5)
    # Feed 3 anomalies + 2 normals within the hysteresis window -> majority anomalous
    predictions = [1, 1, 1, 0, 0]
    decisions = [engine.update(p) for p in predictions]
    assert decisions[-1] == "network"


def test_does_not_flap_on_single_anomaly():
    engine = SwitchingDecisionEngine(hysteresis_window=5)
    # Only 1 anomaly out of 5 - should NOT switch (majority still normal)
    predictions = [0, 0, 1, 0, 0]
    decisions = [engine.update(p) for p in predictions]
    assert decisions[-1] == "gps"


if __name__ == "__main__":
    test_stays_on_gps_when_all_normal()
    test_switches_to_network_when_majority_anomalous()
    test_does_not_flap_on_single_anomaly()
    print("All switching_logic tests passed")