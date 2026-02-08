import unittest
import math
from datetime import datetime

from faketelemetry import (
    TelemetryGenerator,
    WaveformType,
    MultiChannelTelemetryGenerator,
    NoiseInjector,
    NoiseType,
)


class TestTelemetryGenerator(unittest.TestCase):
    # ----- basic waveforms -----

    def test_sine_wave(self):
        gen = TelemetryGenerator(WaveformType.SINE, frequency=1.0, amplitude=2.0, offset=1.0)
        self.assertAlmostEqual(gen.generate_point(0), 1.0)
        self.assertAlmostEqual(gen.generate_point(0.25), 3.0, places=1)

    def test_cosine_wave(self):
        gen = TelemetryGenerator(WaveformType.COSINE, frequency=1.0, amplitude=1.0, offset=0.0)
        self.assertAlmostEqual(gen.generate_point(0), 1.0)

    def test_square_wave(self):
        gen = TelemetryGenerator(WaveformType.SQUARE, frequency=1.0, amplitude=1.0, offset=0.0)
        self.assertIn(gen.generate_point(0.1), [1.0, -1.0])

    def test_sawtooth_wave(self):
        gen = TelemetryGenerator(WaveformType.SAWTOOTH, frequency=1.0, amplitude=1.0, offset=0.0)
        self.assertAlmostEqual(gen.generate_point(0), 0.0)

    def test_triangle_wave(self):
        gen = TelemetryGenerator(WaveformType.TRIANGLE, frequency=1.0, amplitude=1.0, offset=0.0)
        self.assertAlmostEqual(gen.generate_point(0), -1.0, places=1)
        self.assertAlmostEqual(gen.generate_point(0.25), 0.0, places=1)
        self.assertAlmostEqual(gen.generate_point(0.5), 1.0, places=1)
        self.assertAlmostEqual(gen.generate_point(0.75), 0.0, places=1)

    def test_pulse_wave(self):
        gen = TelemetryGenerator(WaveformType.PULSE, frequency=1.0, amplitude=1.0, offset=0.0)
        self.assertEqual(gen.generate_point(0), 1.0)
        self.assertEqual(gen.generate_point(0.6), 0.0)
        self.assertEqual(gen.generate_point(1.0), 1.0)

    def test_custom_wave(self):
        gen = TelemetryGenerator(WaveformType.CUSTOM, custom_func=lambda t: 42.0)
        self.assertEqual(gen.generate_point(0), 42.0)
        self.assertEqual(gen.generate_point(1), 42.0)

    # ----- new waveforms -----

    def test_random_walk(self):
        gen = TelemetryGenerator(WaveformType.RANDOM_WALK, amplitude=1.0, seed=42)
        v1 = gen.generate_point(0)
        v2 = gen.generate_point(0.1)
        # Walk should accumulate steps so values differ
        self.assertNotAlmostEqual(v1, v2)

    def test_step(self):
        gen = TelemetryGenerator(WaveformType.STEP, frequency=1.0, amplitude=5.0, offset=0.0)
        self.assertAlmostEqual(gen.generate_point(0.5), 0.0)
        self.assertAlmostEqual(gen.generate_point(1.5), 5.0)

    def test_exponential_decay(self):
        gen = TelemetryGenerator(WaveformType.EXPONENTIAL_DECAY, frequency=1.0, amplitude=10.0)
        v0 = gen.generate_point(0)
        v5 = gen.generate_point(5)
        self.assertAlmostEqual(v0, 10.0, places=1)
        self.assertTrue(v5 < v0)

    def test_chirp(self):
        gen = TelemetryGenerator(WaveformType.CHIRP, frequency=1.0, amplitude=1.0)
        vals = [gen.generate_point(t * 0.01) for t in range(100)]
        self.assertTrue(any(v > 0 for v in vals))
        self.assertTrue(any(v < 0 for v in vals))

    # ----- phase -----

    def test_phase_offset(self):
        gen0 = TelemetryGenerator(WaveformType.SINE, phase=0.0)
        gen90 = TelemetryGenerator(WaveformType.SINE, phase=math.pi / 2)
        # sin(0) = 0, sin(pi/2) = 1
        self.assertAlmostEqual(gen0.generate_point(0), 0.0, places=5)
        self.assertAlmostEqual(gen90.generate_point(0), 1.0, places=5)

    # ----- duty cycle -----

    def test_duty_cycle_square(self):
        gen = TelemetryGenerator(WaveformType.SQUARE, frequency=1.0, amplitude=1.0, duty_cycle=0.25)
        # First 25% of cycle should be high
        self.assertEqual(gen.generate_point(0.1), 1.0)
        # Last 75% should be low
        self.assertEqual(gen.generate_point(0.5), -1.0)

    def test_duty_cycle_pulse(self):
        gen = TelemetryGenerator(WaveformType.PULSE, frequency=1.0, amplitude=1.0, duty_cycle=0.8)
        self.assertEqual(gen.generate_point(0.5), 1.0)  # within 80%
        self.assertEqual(gen.generate_point(0.9), 0.0)  # outside 80%

    # ----- damping -----

    def test_damping(self):
        gen = TelemetryGenerator(WaveformType.SINE, amplitude=1.0, damping=1.0)
        v0 = gen.generate_point(0.25)
        v5 = gen.generate_point(5.0)
        self.assertTrue(abs(v5) < abs(v0))

    # ----- clamp -----

    def test_clamp(self):
        gen = TelemetryGenerator(WaveformType.SINE, amplitude=10.0, clamp_min=-2.0, clamp_max=2.0)
        for t in [0.0, 0.1, 0.25, 0.5, 0.75]:
            v = gen.generate_point(t)
            self.assertGreaterEqual(v, -2.0)
            self.assertLessEqual(v, 2.0)

    # ----- batch -----

    def test_batch(self):
        gen = TelemetryGenerator(WaveformType.SINE, frequency=1.0)
        points = gen.batch(num_samples=50, sampling_rate=10)
        self.assertEqual(len(points), 50)
        for ts, val in points:
            self.assertIsInstance(ts, datetime)
            self.assertIsInstance(val, float)

    def test_batch_values(self):
        gen = TelemetryGenerator(WaveformType.SINE, frequency=1.0, seed=42)
        vals = gen.batch_values(num_samples=20, sampling_rate=10)
        self.assertEqual(len(vals), 20)
        self.assertTrue(all(isinstance(v, float) for v in vals))

    def test_to_dict(self):
        gen = TelemetryGenerator(WaveformType.SINE, name="test_ch")
        rows = gen.to_dict(num_samples=5, sampling_rate=10)
        self.assertEqual(len(rows), 5)
        self.assertIn("timestamp", rows[0])
        self.assertIn("value", rows[0])
        self.assertEqual(rows[0]["channel"], "test_ch")

    # ----- validation -----

    def test_invalid_frequency(self):
        with self.assertRaises(ValueError):
            TelemetryGenerator(WaveformType.SINE, frequency=-1)

    def test_invalid_amplitude(self):
        with self.assertRaises(ValueError):
            TelemetryGenerator(WaveformType.SINE, amplitude=-1)

    def test_invalid_custom_func(self):
        with self.assertRaises(ValueError):
            TelemetryGenerator(WaveformType.CUSTOM, custom_func=None)

    def test_negative_time(self):
        gen = TelemetryGenerator(WaveformType.SINE)
        with self.assertRaises(ValueError):
            gen.generate_point(-1)

    def test_invalid_duty_cycle(self):
        with self.assertRaises(ValueError):
            TelemetryGenerator(WaveformType.PULSE, duty_cycle=0.0)

    def test_invalid_clamp(self):
        with self.assertRaises(ValueError):
            TelemetryGenerator(WaveformType.SINE, clamp_min=5, clamp_max=2)

    # ----- repr / reset -----

    def test_repr(self):
        gen = TelemetryGenerator(WaveformType.SINE, name="my_sensor")
        self.assertIn("my_sensor", repr(gen))

    def test_reset(self):
        gen = TelemetryGenerator(WaveformType.RANDOM_WALK, seed=1)
        gen.generate_point(0)
        gen.generate_point(0.1)
        gen.reset()
        # After reset the walk state should be back at 0
        self.assertEqual(gen._walk_state, 0.0)


# ==================================================================
# Multi-channel tests
# ==================================================================


class TestMultiChannelTelemetryGenerator(unittest.TestCase):
    def test_list_input(self):
        g1 = TelemetryGenerator(WaveformType.SINE, name="a")
        g2 = TelemetryGenerator(WaveformType.COSINE, name="b")
        multi = MultiChannelTelemetryGenerator([g1, g2])
        self.assertEqual(len(multi), 2)
        self.assertIn("a", multi.channel_names)
        self.assertIn("b", multi.channel_names)

    def test_dict_input(self):
        gens = {
            "temp": TelemetryGenerator(WaveformType.SINE),
            "press": TelemetryGenerator(WaveformType.COSINE),
        }
        multi = MultiChannelTelemetryGenerator(gens)
        self.assertEqual(multi.channel_names, ["temp", "press"])

    def test_stream(self):
        g1 = TelemetryGenerator(WaveformType.SINE, frequency=1.0, name="ch0")
        g2 = TelemetryGenerator(WaveformType.COSINE, frequency=2.0, name="ch1")
        multi = MultiChannelTelemetryGenerator([g1, g2])
        results = list(multi.stream(sampling_rate=2.0, duration=1))
        self.assertTrue(len(results) > 0)
        for sample in results:
            self.assertEqual(len(sample), 2)
            for v in sample.values():
                self.assertIsInstance(v[0], datetime)
                self.assertIsInstance(v[1], float)

    def test_batch(self):
        multi = MultiChannelTelemetryGenerator(
            {
                "a": TelemetryGenerator(WaveformType.SINE),
                "b": TelemetryGenerator(WaveformType.COSINE),
            }
        )
        rows = multi.batch(num_samples=10, sampling_rate=10)
        self.assertEqual(len(rows), 10)
        self.assertIn("timestamp", rows[0])
        self.assertIn("a", rows[0])
        self.assertIn("b", rows[0])

    def test_batch_arrays(self):
        multi = MultiChannelTelemetryGenerator(
            {
                "x": TelemetryGenerator(WaveformType.SINE),
                "y": TelemetryGenerator(WaveformType.COSINE),
            }
        )
        arrays = multi.batch_arrays(num_samples=20, sampling_rate=10)
        self.assertEqual(len(arrays["x"]), 20)
        self.assertEqual(len(arrays["y"]), 20)

    def test_getitem(self):
        gen = TelemetryGenerator(WaveformType.SINE)
        multi = MultiChannelTelemetryGenerator({"s": gen})
        self.assertIs(multi["s"], gen)

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            MultiChannelTelemetryGenerator([])


if __name__ == "__main__":
    unittest.main()
