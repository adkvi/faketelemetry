from datetime import datetime, timedelta
import time
from typing import Optional, Dict, Tuple, List, Iterator
from .telemetry_generator import TelemetryGenerator


class MultiChannelTelemetryGenerator:
    """
    Generate multiple telemetry streams (channels) in parallel.

    This class allows you to combine multiple TelemetryGenerator instances
    and produce synchronized samples across all channels.
    """

    def __init__(self, generators: list[TelemetryGenerator]):
        """
        Initialize the multi-channel generator.

        :param generators: List of TelemetryGenerator instances (one per channel)
        """
        self.generators = generators

    def stream(
        self, sampling_rate: float, duration: Optional[float] = None
    ) -> Iterator[Dict[int, Tuple[datetime, float]]]:
        """
        Yield a dict of {channel_index: (datetime, value)} for each sample.

        This method generates values with actual time delays, suitable for
        simulating real-time multi-channel telemetry streams.

        :param sampling_rate: Samples per second (Hz)
        :param duration: Optional duration in seconds. If None, streams forever.
        :yields: Dictionary mapping channel index to (timestamp, value) tuple
        """
        interval = 1.0 / sampling_rate
        start_time = time.time()
        elapsed = 0.0
        while duration is None or elapsed < duration:
            now = time.time() - start_time
            result: Dict[int, Tuple[datetime, float]] = {}
            for idx, gen in enumerate(self.generators):
                value = gen.generate_point(now)
                result[idx] = (datetime.now(), value)
            yield result
            time.sleep(interval)
            elapsed = time.time() - start_time

    def generate_batch(
        self,
        sampling_rate: float,
        duration: float,
        start_time: Optional[datetime] = None,
    ) -> List[Dict[int, Tuple[datetime, float]]]:
        """
        Generate a batch of multi-channel telemetry data without real-time delays.

        This method is useful for generating test data, historical data,
        or when you need all samples at once without waiting.

        :param sampling_rate: Samples per second (Hz)
        :param duration: Duration in seconds to generate data for
        :param start_time: Optional start datetime. If None, uses current time.
        :return: List of dictionaries, each mapping channel index to (timestamp, value)
        """
        if sampling_rate <= 0:
            raise ValueError("Sampling rate must be positive.")
        if duration <= 0:
            raise ValueError("Duration must be positive.")

        interval = 1.0 / sampling_rate
        num_samples = int(duration * sampling_rate)
        base_time = start_time or datetime.now()

        results = []
        for i in range(num_samples):
            t = i * interval
            timestamp = base_time + timedelta(seconds=t)
            sample: Dict[int, Tuple[datetime, float]] = {}
            for idx, gen in enumerate(self.generators):
                value = gen.generate_point(t)
                sample[idx] = (timestamp, value)
            results.append(sample)
        return results
