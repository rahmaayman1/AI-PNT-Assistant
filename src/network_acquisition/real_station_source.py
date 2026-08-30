"""
real_station_source.py
-------------------------
Placeholder for real network station measurements (once physical stations
with synchronized timing exist). Will likely read from a message queue or
socket connection to each station, similar in spirit to USRPSource.
"""

class RealStationSource:
    def __init__(self, station_config: dict):
        self.station_config = station_config
        raise NotImplementedError(
            "Real network stations not yet available - use MockStationSource for now."
        )

    def get_measurements(self):
        raise NotImplementedError