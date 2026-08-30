"""
trilateration.py
-------------------
Computes position using trilateration, when direct distances (not time
differences) from at least 3 known reference stations are available.
"""

import numpy as np
from scipy.optimize import least_squares


def trilateration_residuals(position, station_coords, distances):
    residuals = []
    for coord, d in zip(station_coords, distances):
        estimated_distance = np.linalg.norm(position - coord)
        residuals.append(estimated_distance - d)
    return residuals


def estimate_position_trilateration(station_coords: list, distances: list, initial_guess=(0, 0)):
    """
    station_coords: [(x1, y1), (x2, y2), (x3, y3), ...]
    distances: [d1, d2, d3, ...] measured distance from each station to the target point
    """
    if len(station_coords) < 3:
        raise ValueError("At least 3 stations are required for reliable trilateration")

    station_coords = np.array(station_coords)
    result = least_squares(
        trilateration_residuals,
        x0=np.array(initial_guess, dtype=float),
        args=(station_coords, distances),
    )
    return result.x