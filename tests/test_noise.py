import unittest
from faketelemetry import NoiseInjector, NoiseType


class TestNoiseInjector(unittest.TestCase):
    def test_no_noise(self):
        ni = NoiseInjector(noise_level=0.0)
        self.assertEqual(ni.add_noise(5.0), 5.0)

    def test_gaussian_noise(self):
        ni = NoiseInjector(noise_level=1.0, noise_type=NoiseType.GAUSSIAN, seed=42)
        values = [ni.add_noise(5.0) for _ in range(100)]
        self.assertTrue(any(abs(v - 5.0) > 0.1 for v in values))

    def test_uniform_noise(self):
        ni = NoiseInjector(noise_level=2.0, noise_type=NoiseType.UNIFORM, seed=7)
        values = [ni.add_noise(0.0) for _ in range(200)]
        # All values should be in [-2, 2]
        self.assertTrue(all(-2.0 <= v <= 2.0 for v in values))
        # But not all zero
        self.assertTrue(any(abs(v) > 0.1 for v in values))

    def test_brownian_noise_drifts(self):
        ni = NoiseInjector(noise_level=0.5, noise_type=NoiseType.BROWNIAN, seed=1)
        values = [ni.add_noise(0.0) for _ in range(500)]
        # Brownian should drift away from 0 over time
        self.assertTrue(abs(values[-1]) > 0.5)

    def test_pink_noise(self):
        ni = NoiseInjector(noise_level=1.0, noise_type=NoiseType.PINK, seed=3)
        values = [ni.add_noise(0.0) for _ in range(200)]
        self.assertTrue(any(abs(v) > 0.01 for v in values))

    def test_impulse_noise(self):
        ni = NoiseInjector(
            noise_level=100.0,
            noise_type=NoiseType.IMPULSE,
            impulse_probability=0.5,
            seed=42,
        )
        values = [ni.add_noise(0.0) for _ in range(200)]
        # Some should be spiked, some not
        spiked = [v for v in values if abs(v) > 50]
        clean = [v for v in values if abs(v) < 1]
        self.assertTrue(len(spiked) > 10)
        self.assertTrue(len(clean) > 10)

    def test_quantization_noise(self):
        ni = NoiseInjector(
            noise_level=0.0,
            noise_type=NoiseType.QUANTIZATION,
            quantization_step=0.5,
        )
        self.assertAlmostEqual(ni.add_noise(0.3), 0.5)
        self.assertAlmostEqual(ni.add_noise(0.7), 0.5)
        self.assertAlmostEqual(ni.add_noise(1.1), 1.0)

    def test_seed_reproducibility(self):
        ni1 = NoiseInjector(noise_level=1.0, seed=99)
        ni2 = NoiseInjector(noise_level=1.0, seed=99)
        vals1 = [ni1.add_noise(0.0) for _ in range(50)]
        vals2 = [ni2.add_noise(0.0) for _ in range(50)]
        self.assertEqual(vals1, vals2)

    def test_reset(self):
        ni = NoiseInjector(noise_level=0.5, noise_type=NoiseType.BROWNIAN, seed=1)
        for _ in range(100):
            ni.add_noise(0.0)
        ni.reset()
        self.assertEqual(ni._brownian_state, 0.0)

    def test_invalid_noise_level(self):
        with self.assertRaises(ValueError):
            NoiseInjector(noise_level=-1.0)

    def test_invalid_noise_type(self):
        with self.assertRaises(TypeError):
            NoiseInjector(noise_type="not_an_enum")  # type: ignore

    def test_invalid_impulse_probability(self):
        with self.assertRaises(ValueError):
            NoiseInjector(noise_type=NoiseType.IMPULSE, impulse_probability=2.0)


if __name__ == "__main__":
    unittest.main()
