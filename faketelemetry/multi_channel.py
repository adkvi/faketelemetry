from datetime import datetime
import time
from typing import Optional
from .telemetry_generator import TelemetryGenerator

class MultiChannelTelemetryGenerator:
    """
    Generate multiple telemetry streams (channels) in parallel.
    """
    def __init__(self, generators: list[TelemetryGenerator]):
        """
        :param generators: List of TelemetryGenerator instances (one per channel)
        """
        self.generators = generators

    def stream(self, sampling_rate: float, duration: float = None):
        """
        Yield a dict of {channel_index: (datetime, value)} for each sample.
        """
        interval = 1.0 / sampling_rate
        start_time = time.time()
        elapsed = 0.0
        while duration is None or elapsed < duration:
            now = time.time() - start_time
            result = {}
            for idx, gen in enumerate(self.generators):
                value = gen.generate_point(now)
                result[idx] = (datetime.now(), value)
            yield result
            time.sleep(interval)
            elapsed = time.time() - start_time
