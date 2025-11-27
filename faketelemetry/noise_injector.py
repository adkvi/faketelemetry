import random
from enum import Enum
from typing import Optional


class NoiseType(Enum):
    """
    Enumeration of supported noise types.
    """

    GAUSSIAN = "gaussian"
    UNIFORM = "uniform"
    IMPULSE = "impulse"


class NoiseInjector:
    """
    Injects noise into signal values.

    Supports Gaussian (normal distribution), uniform, and impulse noise.
    """

    def __init__(
        self,
        noise_level: float = 0.0,
        noise_type: NoiseType = NoiseType.GAUSSIAN,
        impulse_probability: float = 0.01,
    ):
        """
        Initialize the noise injector.

        :param noise_level: For Gaussian: standard deviation.
                           For Uniform: half-width of the range [-noise_level, noise_level].
                           For Impulse: magnitude of impulse spikes.
        :param noise_type: Type of noise to inject (default: Gaussian)
        :param impulse_probability: Probability of an impulse occurring (0 to 1),
                                   only used with NoiseType.IMPULSE
        """
        if noise_level < 0:
            raise ValueError("noise_level must be non-negative.")
        if not 0 <= impulse_probability <= 1:
            raise ValueError("impulse_probability must be between 0 and 1.")

        self.noise_level = noise_level
        self.noise_type = noise_type
        self.impulse_probability = impulse_probability

    def add_noise(self, value: float) -> float:
        """
        Add noise to the input value.

        :param value: The input signal value
        :return: The value with noise added
        """
        if self.noise_level <= 0:
            return value

        if self.noise_type == NoiseType.GAUSSIAN:
            return value + random.gauss(0, self.noise_level)
        elif self.noise_type == NoiseType.UNIFORM:
            return value + random.uniform(-self.noise_level, self.noise_level)
        elif self.noise_type == NoiseType.IMPULSE:
            if random.random() < self.impulse_probability:
                # Random impulse spike (positive or negative)
                return value + random.choice([-1, 1]) * self.noise_level
            return value
        else:
            return value
