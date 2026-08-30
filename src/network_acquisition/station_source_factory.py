"""
station_source_factory.py
----------------------------
Mirrors source_factory.py's pattern: swaps between mock and real network
station sources based on config, with no changes needed elsewhere.
"""

from .mock_station_source import MockStationSource
from .real_station_source import RealStationSource


def get_station_source(config: dict):
    source_type = config["network_source"]["type"]  # "mock" or "real"

    if source_type == "mock":
        return MockStationSource(config["network_source"]["station_coords"])
    elif source_type == "real":
        return RealStationSource(config["network_source"]["station_config"])
    else:
        raise ValueError(f"Unknown network source type: {source_type}")