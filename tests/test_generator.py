import unittest
from datetime import datetime
from faketelemetry import TelemetryGenerator, WaveformType, MultiChannelTelemetryGenerator

class TestTelemetryGenerator(unittest.TestCase):
    def test_sine_wave(self):
        gen = TelemetryGenerator(WaveformType.SINE, frequency=1.0, amplitude=2.0, offset=1.0)
        value = gen.generate_point(0)
        self.assertAlmostEqual(value, 1.0)
        value = gen.generate_point(0.25)
        self.assertAlmostEqual(value, 3.0, places=1)

    def test_cosine_wave(self):
        gen = TelemetryGenerator(WaveformType.COSINE, frequency=1.0, amplitude=1.0, offset=0.0)
        value = gen.generate_point(0)
        self.assertAlmostEqual(value, 1.0)

    def test_square_wave(self):
        gen = TelemetryGenerator(WaveformType.SQUARE, frequency=1.0, amplitude=1.0, offset=0.0)
        self.assertIn(gen.generate_point(0), [1.0, -1.0])

    def test_sawtooth_wave(self):
        gen = TelemetryGenerator(WaveformType.SAWTOOTH, frequency=1.0, amplitude=1.0, offset=0.0)
        value = gen.generate_point(0)
        self.assertAlmostEqual(value, 0.0)
        
    def test_multichannel_stream(self):
        gen1 = TelemetryGenerator(WaveformType.SINE, frequency=1.0)
        gen2 = TelemetryGenerator(WaveformType.COSINE, frequency=2.0)
        multi = MultiChannelTelemetryGenerator([gen1, gen2])
        stream = multi.stream(sampling_rate=2.0, duration=1)
        results = list(stream)
        # There should be at least one sample
        self.assertTrue(len(results) > 0)
        for sample in results:
            # Should have two channels
            self.assertEqual(len(sample), 2)
            # Each value should be a (datetime, float) tuple
            for v in sample.values():
                self.assertIsInstance(v[0], datetime)
                self.assertIsInstance(v[1], float)

    def test_triangle_wave(self):
        gen = TelemetryGenerator(WaveformType.TRIANGLE, frequency=1.0, amplitude=1.0, offset=0.0)
        self.assertAlmostEqual(gen.generate_point(0), -1.0, places=1)
        self.assertAlmostEqual(gen.generate_point(0.25), 0.0, places=1)
        self.assertAlmostEqual(gen.generate_point(0.5), 1.0, places=1)
        self.assertAlmostEqual(gen.generate_point(0.75), 0.0, places=1)

    def test_pulse_wave(self):
        gen = TelemetryGenerator(WaveformType.PULSE, frequency=1.0, amplitude=1.0, offset=0.0)
        self.assertEqual(gen.generate_point(0), 1.0)
        self.assertEqual(gen.generate_point(0.11), 0.0)
        self.assertEqual(gen.generate_point(1.0), 1.0)

    def test_custom_wave(self):
        def custom_func(t):
            return 42.0
        gen = TelemetryGenerator(WaveformType.CUSTOM, custom_func=custom_func)
        self.assertEqual(gen.generate_point(0), 42.0)
        self.assertEqual(gen.generate_point(1), 42.0)

    def test_invalid_frequency(self):
        with self.assertRaises(ValueError) as cm:
            TelemetryGenerator(WaveformType.SINE, frequency=-1)
        self.assertIn("Frequency must be non-negative", str(cm.exception))

    def test_invalid_amplitude(self):
        with self.assertRaises(ValueError) as cm:
            TelemetryGenerator(WaveformType.SINE, amplitude=-1)
        self.assertIn("Amplitude must be non-negative", str(cm.exception))

    def test_invalid_custom_func(self):
        with self.assertRaises(ValueError) as cm:
            TelemetryGenerator(WaveformType.CUSTOM, custom_func=None)
        self.assertIn("callable custom_func", str(cm.exception))

    def test_negative_time(self):
        gen = TelemetryGenerator(WaveformType.SINE)
        with self.assertRaises(ValueError) as cm:
            gen.generate_point(-1)
        self.assertIn("Time t must be non-negative", str(cm.exception))

if __name__ == "__main__":
    unittest.main()
