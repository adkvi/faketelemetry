import math
import random
from typing import Optional

from .enums import NoiseType


class NoiseInjector:
    """
    Injects configurable noise into a signal value.

    Supports Gaussian, uniform, pink (1/f), Brownian (random-walk),
    impulse (occasional spikes), and quantization noise.

    Example::

        noise = NoiseInjector(noise_level=0.1, noise_type=NoiseType.GAUSSIAN, seed=42)
        noisy_value = noise.add_noise(3.14)
    """

    def __init__(
        self,
        noise_level: float = 0.0,
        noise_type: NoiseType = NoiseType.GAUSSIAN,
        seed: Optional[int] = None,
        impulse_probability: float = 0.01,
        quantization_step: float = 0.1,
    ):
        """
        :param noise_level: Controls noise magnitude (meaning varies by type).
            - GAUSSIAN: standard deviation
            - UNIFORM: half-width of the uniform range [-noise_level, +noise_level]
            - PINK: amplitude scaling factor
            - BROWNIAN: step standard deviation
            - IMPULSE: spike magnitude
            - QUANTIZATION: (ignored, use quantization_step instead)
        :param noise_type: Distribution / character of the noise.
        :param seed: Optional random seed for reproducibility.
        :param impulse_probability: Probability of a spike per sample (IMPULSE only).
        :param quantization_step: Step size for QUANTIZATION noise.
        """
        if noise_level < 0:
            raise ValueError("noise_level must be non-negative.")
        if not isinstance(noise_type, NoiseType):
            raise TypeError(f"noise_type must be a NoiseType enum, got {type(noise_type)}")
        if impulse_probability < 0 or impulse_probability > 1:
            raise ValueError("impulse_probability must be between 0 and 1.")
        if quantization_step <= 0:
            raise ValueError("quantization_step must be positive.")

        self.noise_level = noise_level
        self.noise_type = noise_type
        self.impulse_probability = impulse_probability
        self.quantization_step = quantization_step

        self._rng = random.Random(seed)

        # Internal state for pink and brownian noise
        self._brownian_state = 0.0
        self._pink_octaves = 8
        self._pink_values = [0.0] * self._pink_octaves
        self._pink_counter = 0

    def reset(self) -> None:
        """Reset internal noise state (useful for brownian / pink)."""
        self._brownian_state = 0.0
        self._pink_values = [0.0] * self._pink_octaves
        self._pink_counter = 0

    def add_noise(self, value: float) -> float:
        """
        Add noise to the input value and return the noisy result.
        """
        if self.noise_level == 0 and self.noise_type != NoiseType.QUANTIZATION:
            return value

        if self.noise_type == NoiseType.GAUSSIAN:
            return value + self._rng.gauss(0, self.noise_level)

        elif self.noise_type == NoiseType.UNIFORM:
            return value + self._rng.uniform(-self.noise_level, self.noise_level)

        elif self.noise_type == NoiseType.PINK:
            return value + self._pink_sample() * self.noise_level

        elif self.noise_type == NoiseType.BROWNIAN:
            step = self._rng.gauss(0, self.noise_level)
            self._brownian_state += step
            return value + self._brownian_state

        elif self.noise_type == NoiseType.IMPULSE:
            if self._rng.random() < self.impulse_probability:
                sign = self._rng.choice([-1, 1])
                return value + sign * self.noise_level
            return value

        elif self.noise_type == NoiseType.QUANTIZATION:
            step = self.quantization_step
            return round(value / step) * step

        else:
            raise ValueError(f"Unsupported noise type: {self.noise_type}")

    # ------------------------------------------------------------------
    # Pink noise via Voss-McCartney algorithm
    # ------------------------------------------------------------------
    def _pink_sample(self) -> float:
        """Generate one sample of pink (1/f) noise."""
        last = self._pink_counter
        self._pink_counter += 1

        # Update octaves whose bit changed
        diff = last ^ self._pink_counter
        for i in range(self._pink_octaves):
            if diff & (1 << i):
                self._pink_values[i] = self._rng.uniform(-1, 1)

        return sum(self._pink_values) / self._pink_octaves
