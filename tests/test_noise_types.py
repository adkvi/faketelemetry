import unittest
from faketelemetry.noise_injector import NoiseInjector, NoiseType


class TestNoiseTypes(unittest.TestCase):
    """Tests for different noise types."""

    def test_gaussian_noise(self):
        ni = NoiseInjector(noise_level=1.0, noise_type=NoiseType.GAUSSIAN)
        values = [ni.add_noise(5.0) for _ in range(100)]
        # Should have variation around the original value
        self.assertTrue(any(abs(v - 5.0) > 0.1 for v in values))

    def test_uniform_noise(self):
        ni = NoiseInjector(noise_level=1.0, noise_type=NoiseType.UNIFORM)
        values = [ni.add_noise(5.0) for _ in range(100)]
        # All values should be within [-1, 1] of original
        for v in values:
            self.assertTrue(4.0 <= v <= 6.0)

    def test_impulse_noise(self):
        ni = NoiseInjector(
            noise_level=5.0, noise_type=NoiseType.IMPULSE, impulse_probability=0.5
        )
        values = [ni.add_noise(0.0) for _ in range(100)]
        # Some values should have impulse spikes
        impulse_count = sum(1 for v in values if abs(v) > 0.1)
        # With 50% probability, expect roughly half to have impulses
        self.assertTrue(20 < impulse_count < 80)

    def test_invalid_noise_level(self):
        with self.assertRaises(ValueError):
            NoiseInjector(noise_level=-1.0)

    def test_invalid_impulse_probability(self):
        with self.assertRaises(ValueError):
            NoiseInjector(noise_level=1.0, impulse_probability=1.5)
        with self.assertRaises(ValueError):
            NoiseInjector(noise_level=1.0, impulse_probability=-0.1)


if __name__ == "__main__":
    unittest.main()
