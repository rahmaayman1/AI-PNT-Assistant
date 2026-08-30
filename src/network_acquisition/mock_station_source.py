"""
mock_station_source.py
-------------------------
Placeholder network station source for development/testing, replacing the
hardcoded MOCK_STATION_COORDS previously inline in main.py.
"""

class MockStationSource:
    def __init__(self, station_coords: list):
        self.station_coords = station_coords

    def get_measurements(self):
        """Returns (station_coords, time_diffs) - dummy values for now."""
        time_diffs = [0.0002, 0.00035]  # placeholder
        return self.station_coords, time_diffs