import math
import time
import random
from datetime import datetime
from typing import Iterator, Tuple, Optional
from .enums import WaveformType
from .noise_injector import NoiseInjector

class TelemetryGenerator:
    """
    Generates real-time telemetry data based on mathematical waveforms.
    """
    def __init__(
        self,
        waveform: WaveformType,
        frequency: float = 1.0,
        amplitude: float = 1.0,
        offset: float = 0.0,
        noise_injector: Optional[NoiseInjector] = None,
        custom_func: Optional[callable] = None,
    ):
        """
        Initialize the telemetry generator.
        :param waveform: Type of signal to generate
        :param frequency: Frequency in Hz (must be >= 0)
        :param amplitude: Peak amplitude (must be >= 0)
        :param offset: Base offset (vertical shift)
        :param noise_injector: Optional NoiseInjector
        :param custom_func: Optional function for custom waveform, signature: (t: float) -> float
        """
        if frequency < 0:
            raise ValueError("Frequency must be non-negative.")
        if amplitude < 0:
            raise ValueError("Amplitude must be non-negative.")
        if waveform == WaveformType.CUSTOM and not callable(custom_func):
            raise ValueError("A callable custom_func must be provided for CUSTOM waveform.")
        self.waveform = waveform
        self.frequency = frequency
        self.amplitude = amplitude
        self.offset = offset
        self.noise_injector = noise_injector
        self.custom_func = custom_func

    def generate_point(self, t: float) -> float:
        """
        Generate a signal value at time t (seconds).
        """
        if t < 0:
            raise ValueError("Time t must be non-negative.")
        if self.waveform == WaveformType.SINE:
            value = self.amplitude * math.sin(2 * math.pi * self.frequency * t) + self.offset
        elif self.waveform == WaveformType.COSINE:
            value = self.amplitude * math.cos(2 * math.pi * self.frequency * t) + self.offset
        elif self.waveform == WaveformType.SQUARE:
            value = self.amplitude * (1 if math.sin(2 * math.pi * self.frequency * t) >= 0 else -1) + self.offset
        elif self.waveform == WaveformType.SAWTOOTH:
            value = self.amplitude * (2 * (t * self.frequency - math.floor(0.5 + t * self.frequency))) + self.offset
        elif self.waveform == WaveformType.TRIANGLE:
            value = self.amplitude * (2 * abs(2 * (t * self.frequency - math.floor(t * self.frequency + 0.5))) - 1) + self.offset
        elif self.waveform == WaveformType.PULSE:
            value = self.amplitude * (1 if (t * self.frequency) % 1 < 0.1 else 0) + self.offset
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

    def stream(self, sampling_rate: float, duration: Optional[float] = None) -> Iterator[Tuple[datetime, float]]:
        """
        Stream (datetime, value) tuples in real-time at the given sampling rate.
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
