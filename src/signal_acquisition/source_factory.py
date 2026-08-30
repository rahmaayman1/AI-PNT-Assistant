"""
source_factory.py
--------------------
Chooses between FileSource (development/testing, using recorded data like
TEXBAT) and USRPSource (real hardware), based on config. This is the ONLY
place that needs to change when moving from development to real hardware -
the rest of the pipeline (feature engineering, model, switching logic)
remains identical either way.
"""

from .file_source import FileSource
from .usrp_source import USRPSource


def get_source(config: dict):
    source_type = config["signal_source"]["type"]  # "file" or "usrp"

    if source_type == "file":
        return FileSource(config["signal_source"]["file_path"])
    elif source_type == "usrp":
        return USRPSource(config["signal_source"]["usrp_args"])
    else:
        raise ValueError(f"Unknown signal source type: {source_type}")