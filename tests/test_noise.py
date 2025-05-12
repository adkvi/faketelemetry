import unittest
from faketelemetry.noise_injector import NoiseInjector

class TestNoiseInjector(unittest.TestCase):
    def test_no_noise(self):
        ni = NoiseInjector(noise_level=0.0)
        self.assertEqual(ni.add_noise(5.0), 5.0)

    def test_with_noise(self):
        ni = NoiseInjector(noise_level=1.0)
        # Should not always be exactly 5.0
        values = [ni.add_noise(5.0) for _ in range(100)]
        self.assertTrue(any(abs(v - 5.0) > 0.1 for v in values))

if __name__ == "__main__":
    unittest.main()
