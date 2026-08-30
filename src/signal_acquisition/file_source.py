"""
file_source.py
----------------
Reads channel/navsol observable data from pre-recorded files (e.g. TEXBAT
.mat exports converted to CSV). Acts as a stand-in for real USRP hardware
during development and testing, so the rest of the pipeline can be built and
validated before hardware is available.
"""

import pandas as pd


class FileSource:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def read_all(self) -> pd.DataFrame:
        """Reads the entire file at once (offline analysis mode)."""
        return pd.read_csv(self.file_path)

    def stream(self, chunk_size: int = 50):
        """
        Generator that yields data in small chunks, to simulate a live stream
        even though the data is coming from a static file.
        """
        for chunk in pd.read_csv(self.file_path, chunksize=chunk_size):
            yield chunk