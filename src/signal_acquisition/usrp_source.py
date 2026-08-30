"""
usrp_source.py
----------------
Placeholder for real USRP hardware acquisition, to be implemented once
hardware is available. Intended interface mirrors FileSource so that
source_factory.py can swap between them with no changes needed elsewhere
in the pipeline.

Expected implementation (once hardware arrives):
- Use UHD (USRP Hardware Driver) via GNU Radio or the uhd Python bindings
  to capture raw IQ samples.
- Feed those samples into GNSS-SDR to obtain channel/navsol observables,
  matching the same columns produced by file_source.py from TEXBAT data.
"""


class USRPSource:
    def __init__(self, usrp_args: dict):
        self.usrp_args = usrp_args
        raise NotImplementedError(
            "USRPSource is not implemented yet - requires physical hardware. "
            "Use FileSource for development and testing until hardware is available."
        )

    def stream(self, chunk_size: int = 50):
        raise NotImplementedError