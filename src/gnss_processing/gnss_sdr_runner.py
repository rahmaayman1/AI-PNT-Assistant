"""
gnss_sdr_runner.py
---------------------
Placeholder for running GNSS-SDR as a subprocess to convert raw IQ samples
(from USRP or a recorded .bin file) into channel/navsol observables.

Not needed for the current TEXBAT .mat-based workflow, since those files are
already pre-processed. This becomes relevant once working with raw IQ data
directly (e.g. TEXBAT's original .bin files, or real USRP captures).

Expected usage once implemented:
    runner = GnssSdrRunner(config_path="src/gnss_processing/gnss_sdr_config/default.conf")
    runner.run(input_file="capture.bin", output_dir="data/processed/")
"""

import subprocess


class GnssSdrRunner:
    def __init__(self, config_path: str):
        self.config_path = config_path

    def run(self, input_file: str, output_dir: str):
        raise NotImplementedError(
            "GNSS-SDR integration not yet implemented. Requires GNSS-SDR "
            "installed separately (not a Python package) - see gnss-sdr.org"
        )