"""
decision_engine.py
--------------------
Decides whether the system should trust GPS or fall back to network-based
PNT, based on the anomaly detector's output. Uses a hysteresis window to
avoid rapidly flapping between GPS and network on borderline scores.
"""

from collections import deque


class SwitchingDecisionEngine:
    def __init__(self, hysteresis_window: int = 5):
        self.hysteresis_window = hysteresis_window
        self.recent_flags = deque(maxlen=hysteresis_window)
        self.current_source = "gps"  # "gps" or "network"

    def update(self, is_anomaly: int) -> str:
        """
        is_anomaly: 1 or 0, output of GPSAnomalyDetector.predict() for the
        latest reading.

        Returns the current source decision: "gps" or "network".
        """
        self.recent_flags.append(bool(is_anomaly))

        if len(self.recent_flags) == self.hysteresis_window:
            if sum(self.recent_flags) >= (self.hysteresis_window // 2 + 1):
                self.current_source = "network"
            else:
                self.current_source = "gps"

        return self.current_source