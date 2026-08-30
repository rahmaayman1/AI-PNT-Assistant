"""
tdoa.py
--------
Computes position using Time Difference of Arrival (TDOA), based on signal
arrival time differences from network stations with known coordinates.
"""

import numpy as np
from scipy.optimize import least_squares

SPEED_OF_LIGHT = 299_792_458  # m/s


def tdoa_residuals(position, station_coords, time_diffs):
    ref_coord = station_coords[0]
    ref_distance = np.linalg.norm(position - ref_coord)

    residuals = []
    for coord, dt in zip(station_coords[1:], time_diffs):
        distance = np.linalg.norm(position - coord)
        expected_diff = distance - ref_distance
        measured_diff = dt * SPEED_OF_LIGHT

        residuals.append(expected_diff - measured_diff)

    return residuals


def estimate_position_tdoa(station_coords: list, time_diffs: list, initial_guess=None):
    """
    station_coords: list of (x, y) coordinates for at least 3 stations
    time_diffs: arrival time differences relative to the reference station (seconds)

    Returns estimated [x, y] position.
    """
    if len(station_coords) < 3:
        raise ValueError("At least 3 stations are required for reliable TDOA")

    station_coords = np.array(station_coords)

    # Use the stations' centroid as the starting guess instead of (0, 0).
    # (0, 0) can be far from the true solution and cause the optimizer to
    # get stuck without actually finding the right answer.
    if initial_guess is None:
        initial_guess = station_coords.mean(axis=0)

    result = least_squares(
        tdoa_residuals,
        x0=np.array(initial_guess, dtype=float),
        args=(station_coords, time_diffs),
    )
    return result.x