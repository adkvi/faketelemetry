import random


class NoiseInjector:
    """
    Injects Gaussian noise into a signal value.
    """

    def __init__(self, noise_level: float = 0.0):
        """
        :param noise_level: Standard deviation of the Gaussian noise.
        """
        self.noise_level = noise_level

    def add_noise(self, value: float) -> float:
        """
        Add Gaussian noise to the input value.
        """
        if self.noise_level > 0:
            return value + random.gauss(0, self.noise_level)
        return value
