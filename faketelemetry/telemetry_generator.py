import math
import time
import random
from datetime import datetime
from typing import Iterator, Tuple, Optional, Callable, List
from .enums import WaveformType
from .noise_injector import NoiseInjector


class TelemetryGenerator:
    """
    Generates real-time telemetry data based on mathematical waveforms.

    Supports various waveform types including sine, cosine, square, sawtooth,
    triangle, pulse, exponential decay, random noise, and custom waveforms.
    """

    def __init__(
        self,
        waveform: WaveformType,
        frequency: float = 1.0,
        amplitude: float = 1.0,
        offset: float = 0.0,
        phase: float = 0.0,
        noise_injector: Optional[NoiseInjector] = None,
        custom_func: Optional[Callable[[float], float]] = None,
    ):
        """
        Initialize the telemetry generator.

        :param waveform: Type of signal to generate (WaveformType enum)
        :param frequency: Frequency in Hz (must be >= 0)
        :param amplitude: Peak amplitude (must be >= 0)
        :param offset: Base offset (vertical shift)
        :param phase: Phase shift in radians (default 0.0)
        :param noise_injector: Optional NoiseInjector for adding noise
        :param custom_func: Optional function for custom waveform,
                           signature: (t: float) -> float
        """
        if frequency < 0:
            raise ValueError("Frequency must be non-negative.")
        if amplitude < 0:
            raise ValueError("Amplitude must be non-negative.")
        if waveform == WaveformType.CUSTOM and not callable(custom_func):
            raise ValueError(
                "A callable custom_func must be provided for CUSTOM waveform."
            )
        self.waveform = waveform
        self.frequency = frequency
        self.amplitude = amplitude
        self.offset = offset
        self.phase = phase
        self.noise_injector = noise_injector
        self.custom_func = custom_func

    def generate_point(self, t: float) -> float:
        """
        Generate a signal value at time t (seconds).

        :param t: Time in seconds (must be >= 0)
        :return: The computed signal value at time t
        :raises ValueError: If t is negative
        """
        if t < 0:
            raise ValueError("Time t must be non-negative.")

        # Apply phase shift to the angular frequency calculation
        phase_adjusted = 2 * math.pi * self.frequency * t + self.phase

        if self.waveform == WaveformType.SINE:
            value = self.amplitude * math.sin(phase_adjusted) + self.offset
        elif self.waveform == WaveformType.COSINE:
            value = self.amplitude * math.cos(phase_adjusted) + self.offset
        elif self.waveform == WaveformType.SQUARE:
            value = (
                self.amplitude * (1 if math.sin(phase_adjusted) >= 0 else -1)
                + self.offset
            )
        elif self.waveform == WaveformType.SAWTOOTH:
            # Sawtooth with phase: adjust the time reference
            t_adjusted = (
                t + self.phase / (2 * math.pi * self.frequency)
                if self.frequency > 0
                else t
            )
            value = (
                self.amplitude
                * (
                    2
                    * (
                        t_adjusted * self.frequency
                        - math.floor(0.5 + t_adjusted * self.frequency)
                    )
                )
                + self.offset
            )
        elif self.waveform == WaveformType.TRIANGLE:
            # Triangle with phase: adjust the time reference
            t_adjusted = (
                t + self.phase / (2 * math.pi * self.frequency)
                if self.frequency > 0
                else t
            )
            value = (
                self.amplitude
                * (
                    2
                    * abs(
                        2
                        * (
                            t_adjusted * self.frequency
                            - math.floor(t_adjusted * self.frequency + 0.5)
                        )
                    )
                    - 1
                )
                + self.offset
            )
        elif self.waveform == WaveformType.PULSE:
            # Pulse with phase: adjust the time reference
            t_adjusted = (
                t + self.phase / (2 * math.pi * self.frequency)
                if self.frequency > 0
                else t
            )
            value = (
                self.amplitude * (1 if (t_adjusted * self.frequency) % 1 < 0.1 else 0)
                + self.offset
            )
        elif self.waveform == WaveformType.EXPONENTIAL_DECAY:
            # Exponential decay: frequency acts as decay rate
            value = self.amplitude * math.exp(-self.frequency * t) + self.offset
        elif self.waveform == WaveformType.RANDOM_NOISE:
            value = self.amplitude * random.gauss(0, 1) + self.offset
        elif self.waveform == WaveformType.CUSTOM:
            if self.custom_func is None:
                raise ValueError("Custom waveform requires a custom_func argument.")
            value = self.custom_func(t)
        else:
            raise ValueError(f"Unsupported waveform: {self.waveform}")

        if self.noise_injector:
            value = self.noise_injector.add_noise(value)
        return value

    def stream(
        self, sampling_rate: float, duration: Optional[float] = None
    ) -> Iterator[Tuple[datetime, float]]:
        """
        Stream (datetime, value) tuples in real-time at the given sampling rate.

        This method generates values with actual time delays, suitable for
        simulating real-time telemetry streams.

        :param sampling_rate: Samples per second (Hz)
        :param duration: Optional duration in seconds. If None, streams forever.
        :yields: Tuple of (datetime, float) representing timestamp and value
        """
        interval = 1.0 / sampling_rate
        start_time = time.time()
        elapsed = 0.0
        while duration is None or elapsed < duration:
            now = time.time() - start_time
            value = self.generate_point(now)
            yield (datetime.now(), value)
            time.sleep(interval)
            elapsed = time.time() - start_time

    def generate_batch(
        self,
        sampling_rate: float,
        duration: float,
        start_time: Optional[datetime] = None,
    ) -> List[Tuple[datetime, float]]:
        """
        Generate a batch of telemetry data without real-time delays.

        This method is useful for generating test data, historical data,
        or when you need all samples at once without waiting.

        :param sampling_rate: Samples per second (Hz)
        :param duration: Duration in seconds to generate data for
        :param start_time: Optional start datetime. If None, uses current time.
        :return: List of (datetime, value) tuples
        """
        if sampling_rate <= 0:
            raise ValueError("Sampling rate must be positive.")
        if duration <= 0:
            raise ValueError("Duration must be positive.")

        interval = 1.0 / sampling_rate
        num_samples = int(duration * sampling_rate)
        base_time = start_time or datetime.now()

        result = []
        for i in range(num_samples):
            t = i * interval
            value = self.generate_point(t)
            # Calculate timestamp offset from base_time
            from datetime import timedelta

            timestamp = base_time + timedelta(seconds=t)
            result.append((timestamp, value))
        return result
