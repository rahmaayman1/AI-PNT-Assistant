"""
kalman_filter.py
-------------------
Simple 2D Kalman filter for smoothly fusing position estimates from GPS and
network-based sources, instead of abruptly switching between them.

Uses a constant-velocity motion model in 2D (x, y).
"""

import numpy as np


class SimpleKalmanFilter2D:
    def __init__(self, dt: float = 1.0, process_noise: float = 0.01, measurement_noise: float = 1.0):
        # State: [x, y, vx, vy]
        self.state = np.zeros(4)
        self.P = np.eye(4) * 500  # initial uncertainty

        self.F = np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ])

        self.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
        ])

        self.Q = np.eye(4) * process_noise
        self.R = np.eye(2) * measurement_noise

    def predict(self):
        self.state = self.F @ self.state
        self.P = self.F @ self.P @ self.F.T + self.Q
        return self.state[:2]

    def update(self, measurement: np.ndarray):
        """measurement: [x, y] new reading, either from GPS or from TDOA/trilateration."""
        y = measurement - (self.H @ self.state)
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)

        self.state = self.state + K @ y
        self.P = (np.eye(4) - K @ self.H) @ self.P
        return self.state[:2]