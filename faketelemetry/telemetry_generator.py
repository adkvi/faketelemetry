from __future__ import annotations

import asyncio
import math
import time
import random
from datetime import datetime, timedelta
from typing import (
    AsyncIterator,
    Iterator,
    Tuple,
    Optional,
    Callable,
    List,
    Dict,
    Any,
    TYPE_CHECKING,
)

from .enums import WaveformType, NoiseType
from .noise_injector import NoiseInjector
from .anomaly_injector import AnomalyInjector

if TYPE_CHECKING:
    from .compose import CompositeGenerator


class TelemetryGenerator:
    """
    Generates telemetry data based on mathematical waveforms with optional
    noise injection, anomaly injection, phase control, duty-cycle control,
    damping, and value clamping.

    Supports both **real-time streaming** and **batch generation** (no sleep).

    Example::

        gen = TelemetryGenerator(
            waveform=WaveformType.SINE,
            frequency=1.0,
            amplitude=5.0,
            offset=20.0,
            phase=0.0,
            noise_injector=NoiseInjector(noise_level=0.2),
        )

        # Real-time stream
        for ts, val in gen.stream(sampling_rate=10, duration=5):
            print(ts, val)

        # Batch (instant, no sleep)
        points = gen.batch(num_samples=500, sampling_rate=100)
    """

    def __init__(
        self,
        waveform: WaveformType,
        frequency: float = 1.0,
        amplitude: float = 1.0,
        offset: float = 0.0,
        phase: float = 0.0,
        noise_injector: Optional[NoiseInjector] = None,
        anomaly_injector: Optional[AnomalyInjector] = None,
        custom_func: Optional[Callable[[float], float]] = None,
        duty_cycle: float = 0.5,
        damping: float = 0.0,
        clamp_min: Optional[float] = None,
        clamp_max: Optional[float] = None,
        seed: Optional[int] = None,
        name: Optional[str] = None,
    ):
        """
        :param waveform: Type of signal to generate.
        :param frequency: Frequency in Hz (>= 0).
        :param amplitude: Peak amplitude (>= 0).
        :param offset: Vertical shift.
        :param phase: Phase offset in **radians** (default 0).
        :param noise_injector: Optional :class:`NoiseInjector`.
        :param anomaly_injector: Optional :class:`AnomalyInjector`.
        :param custom_func: Required when *waveform* is ``CUSTOM``.
        :param duty_cycle: Fraction of the period that SQUARE / PULSE is high (0-1).
        :param damping: Exponential decay coefficient (0 = no damping).
        :param clamp_min: If set, output is clamped to this minimum.
        :param clamp_max: If set, output is clamped to this maximum.
        :param seed: Random seed for the internal RNG (RANDOM_NOISE, RANDOM_WALK).
        :param name: Optional human-readable label for this channel.
        """
        if frequency < 0:
            raise ValueError("Frequency must be non-negative.")
        if amplitude < 0:
            raise ValueError("Amplitude must be non-negative.")
        if not 0 < duty_cycle <= 1:
            raise ValueError("duty_cycle must be in (0, 1].")
        if damping < 0:
            raise ValueError("damping must be non-negative.")
        if waveform == WaveformType.CUSTOM and not callable(custom_func):
            raise ValueError("A callable custom_func must be provided for CUSTOM waveform.")
        if clamp_min is not None and clamp_max is not None and clamp_min > clamp_max:
            raise ValueError("clamp_min must be <= clamp_max.")

        self.waveform = waveform
        self.frequency = frequency
        self.amplitude = amplitude
        self.offset = offset
        self.phase = phase
        self.noise_injector = noise_injector
        self.anomaly_injector = anomaly_injector
        self.custom_func = custom_func
        self.duty_cycle = duty_cycle
        self.damping = damping
        self.clamp_min = clamp_min
        self.clamp_max = clamp_max
        self.name = name

        self._rng = random.Random(seed)
        self._walk_state = 0.0  # for RANDOM_WALK

    # ------------------------------------------------------------------
    # Core signal generation
    # ------------------------------------------------------------------

    def generate_point(self, t: float) -> float:
        """
        Generate a signal value at time *t* (seconds).
        """
        if t < 0:
            raise ValueError("Time t must be non-negative.")

        omega = 2 * math.pi * self.frequency * t + self.phase

        wf = self.waveform
        if wf == WaveformType.SINE:
            raw = math.sin(omega)
        elif wf == WaveformType.COSINE:
            raw = math.cos(omega)
        elif wf == WaveformType.SQUARE:
            cycle_pos = (t * self.frequency + self.phase / (2 * math.pi)) % 1
            raw = 1.0 if cycle_pos < self.duty_cycle else -1.0
        elif wf == WaveformType.SAWTOOTH:
            raw = 2 * (t * self.frequency - math.floor(0.5 + t * self.frequency))
        elif wf == WaveformType.TRIANGLE:
            raw = 2 * abs(2 * (t * self.frequency - math.floor(t * self.frequency + 0.5))) - 1
        elif wf == WaveformType.PULSE:
            cycle_pos = (t * self.frequency) % 1
            raw = 1.0 if cycle_pos < self.duty_cycle else 0.0
        elif wf == WaveformType.RANDOM_NOISE:
            raw = self._rng.gauss(0, 1)
        elif wf == WaveformType.RANDOM_WALK:
            step = self._rng.gauss(0, 1)
            self._walk_state += step
            raw = self._walk_state
        elif wf == WaveformType.STEP:
            raw = 0.0 if t < (1.0 / max(self.frequency, 1e-12)) else 1.0
        elif wf == WaveformType.EXPONENTIAL_DECAY:
            raw = math.exp(-self.frequency * t)
        elif wf == WaveformType.CHIRP:
            # Linear chirp: frequency sweeps from frequency to 2*frequency
            instantaneous = self.frequency + self.frequency * t
            raw = math.sin(2 * math.pi * instantaneous * t + self.phase)
        elif wf == WaveformType.CUSTOM:
            if self.custom_func is None:
                raise ValueError("Custom waveform requires a custom_func argument.")
            raw = self.custom_func(t)
            # Skip standard amplitude/offset for custom (user controls everything)
            value = raw
            return self._postprocess(value, t)
        else:
            raise ValueError(f"Unsupported waveform: {wf}")

        value = self.amplitude * raw + self.offset
        return self._postprocess(value, t)

    # ------------------------------------------------------------------
    # Post-processing pipeline: damping -> noise -> anomaly -> clamp
    # ------------------------------------------------------------------

    def _postprocess(self, value: float, t: float) -> float:
        # Exponential damping envelope
        if self.damping > 0:
            value *= math.exp(-self.damping * t)

        # Noise
        if self.noise_injector:
            value = self.noise_injector.add_noise(value)

        # Anomalies
        if self.anomaly_injector:
            value = self.anomaly_injector.apply(value)

        # Clamp
        if self.clamp_min is not None:
            value = max(value, self.clamp_min)
        if self.clamp_max is not None:
            value = min(value, self.clamp_max)

        return value

    # ------------------------------------------------------------------
    # Real-time streaming
    # ------------------------------------------------------------------

    def stream(
        self, sampling_rate: float, duration: Optional[float] = None
    ) -> Iterator[Tuple[datetime, float]]:
        """
        Yield ``(datetime, value)`` tuples in **real-time** at the given
        sampling rate.

        :param sampling_rate: Samples per second.
        :param duration: Stop after this many seconds (``None`` = infinite).
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

    # ------------------------------------------------------------------
    # Batch (non-real-time) generation
    # ------------------------------------------------------------------

    def batch(
        self,
        num_samples: int,
        sampling_rate: float,
        start_time: Optional[datetime] = None,
    ) -> List[Tuple[datetime, float]]:
        """
        Generate *num_samples* points instantly (no sleeping).

        :param num_samples: Number of data points.
        :param sampling_rate: Determines time spacing between points.
        :param start_time: Anchor timestamp for the first point (default: now).
        :returns: List of ``(datetime, value)`` tuples.
        """
        if num_samples < 0:
            raise ValueError("num_samples must be non-negative.")
        if sampling_rate <= 0:
            raise ValueError("sampling_rate must be positive.")

        interval = 1.0 / sampling_rate
        base = start_time or datetime.now()
        points: List[Tuple[datetime, float]] = []
        for i in range(num_samples):
            t = i * interval
            ts = base + timedelta(seconds=t)
            val = self.generate_point(t)
            points.append((ts, val))
        return points

    def batch_values(
        self,
        num_samples: int,
        sampling_rate: float,
    ) -> List[float]:
        """
        Generate *num_samples* raw values instantly (no timestamps, no sleep).
        """
        if num_samples < 0:
            raise ValueError("num_samples must be non-negative.")
        if sampling_rate <= 0:
            raise ValueError("sampling_rate must be positive.")

        interval = 1.0 / sampling_rate
        return [self.generate_point(i * interval) for i in range(num_samples)]

    def to_dict(
        self,
        num_samples: int,
        sampling_rate: float,
        start_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Return batch data as a list of dicts, convenient for DataFrames::

            import pandas as pd
            df = pd.DataFrame(gen.to_dict(1000, 100))
        """
        points = self.batch(num_samples, sampling_rate, start_time)
        return [
            {"timestamp": ts.isoformat(), "value": val, "channel": self.name} for ts, val in points
        ]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Reset internal state (random-walk position, noise, anomalies)."""
        self._walk_state = 0.0
        if self.noise_injector:
            self.noise_injector.reset()
        if self.anomaly_injector:
            self.anomaly_injector.reset()

    # ------------------------------------------------------------------
    # Async streaming
    # ------------------------------------------------------------------

    async def astream(
        self, sampling_rate: float, duration: Optional[float] = None
    ) -> AsyncIterator[Tuple[datetime, float]]:
        """
        Async version of :meth:`stream`.  Use with ``async for``::

            async for ts, val in gen.astream(sampling_rate=10, duration=5):
                print(ts, val)
        """
        interval = 1.0 / sampling_rate
        start_time = time.time()
        elapsed = 0.0
        while duration is None or elapsed < duration:
            now = time.time() - start_time
            value = self.generate_point(now)
            yield (datetime.now(), value)
            await asyncio.sleep(interval)
            elapsed = time.time() - start_time

    # ------------------------------------------------------------------
    # Config serialization
    # ------------------------------------------------------------------

    def to_config(self) -> Dict[str, Any]:
        """
        Serialize generator parameters to a plain dict (JSON-safe).

        Useful for saving / reproducing experiments::

            import json
            config = gen.to_config()
            json.dump(config, open("config.json", "w"))
        """
        cfg: Dict[str, Any] = {
            "waveform": self.waveform.value,
            "frequency": self.frequency,
            "amplitude": self.amplitude,
            "offset": self.offset,
            "phase": self.phase,
            "duty_cycle": self.duty_cycle,
            "damping": self.damping,
        }
        if self.clamp_min is not None:
            cfg["clamp_min"] = self.clamp_min
        if self.clamp_max is not None:
            cfg["clamp_max"] = self.clamp_max
        if self.name is not None:
            cfg["name"] = self.name
        if self.noise_injector is not None:
            cfg["noise"] = {
                "noise_level": self.noise_injector.noise_level,
                "noise_type": self.noise_injector.noise_type.value,
                "impulse_probability": self.noise_injector.impulse_probability,
                "quantization_step": self.noise_injector.quantization_step,
            }
        return cfg

    @classmethod
    def from_config(cls, cfg: Dict[str, Any]) -> "TelemetryGenerator":
        """
        Reconstruct a generator from a config dict (output of :meth:`to_config`).

        Example::

            gen = TelemetryGenerator.from_config(json.load(open("config.json")))
        """
        noise_injector = None
        noise_cfg = cfg.get("noise")
        if noise_cfg:
            noise_injector = NoiseInjector(
                noise_level=noise_cfg.get("noise_level", 0.0),
                noise_type=NoiseType(noise_cfg.get("noise_type", "gaussian")),
                impulse_probability=noise_cfg.get("impulse_probability", 0.01),
                quantization_step=noise_cfg.get("quantization_step", 0.1),
            )

        return cls(
            waveform=WaveformType(cfg["waveform"]),
            frequency=cfg.get("frequency", 1.0),
            amplitude=cfg.get("amplitude", 1.0),
            offset=cfg.get("offset", 0.0),
            phase=cfg.get("phase", 0.0),
            duty_cycle=cfg.get("duty_cycle", 0.5),
            damping=cfg.get("damping", 0.0),
            clamp_min=cfg.get("clamp_min"),
            clamp_max=cfg.get("clamp_max"),
            noise_injector=noise_injector,
            name=cfg.get("name"),
        )

    # ------------------------------------------------------------------
    # Operator overloading (signal composition)
    # ------------------------------------------------------------------

    def __add__(self, other: Any) -> "CompositeGenerator":
        from .compose import CompositeGenerator

        return CompositeGenerator(self, other, "add")

    def __radd__(self, other: Any) -> "CompositeGenerator":
        from .compose import CompositeGenerator

        return CompositeGenerator(other, self, "add")

    def __sub__(self, other: Any) -> "CompositeGenerator":
        from .compose import CompositeGenerator

        return CompositeGenerator(self, other, "sub")

    def __rsub__(self, other: Any) -> "CompositeGenerator":
        from .compose import CompositeGenerator

        return CompositeGenerator(other, self, "sub")

    def __mul__(self, other: Any) -> "CompositeGenerator":
        from .compose import CompositeGenerator

        return CompositeGenerator(self, other, "mul")

    def __rmul__(self, other: Any) -> "CompositeGenerator":
        from .compose import CompositeGenerator

        return CompositeGenerator(other, self, "mul")

    def __neg__(self) -> "CompositeGenerator":
        from .compose import CompositeGenerator

        return CompositeGenerator(-1, self, "mul")

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        label = f"'{self.name}'" if self.name else "unnamed"
        return (
            f"TelemetryGenerator({label}, waveform={self.waveform.value}, "
            f"freq={self.frequency}, amp={self.amplitude}, offset={self.offset})"
        )
