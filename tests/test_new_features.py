import unittest
from datetime import datetime
from faketelemetry import (
    TelemetryGenerator,
    WaveformType,
    MultiChannelTelemetryGenerator,
    to_json,
    to_csv,
    to_dict,
    from_json,
    from_csv,
)


class TestBatchGeneration(unittest.TestCase):
    """Tests for batch data generation without real-time delays."""

    def test_single_channel_batch(self):
        gen = TelemetryGenerator(WaveformType.SINE, frequency=1.0)
        data = gen.generate_batch(sampling_rate=10.0, duration=1.0)
        self.assertEqual(len(data), 10)
        for ts, val in data:
            self.assertIsInstance(ts, datetime)
            self.assertIsInstance(val, float)

    def test_batch_with_custom_start_time(self):
        gen = TelemetryGenerator(WaveformType.COSINE)
        start = datetime(2025, 1, 1, 12, 0, 0)
        data = gen.generate_batch(sampling_rate=2.0, duration=2.0, start_time=start)
        self.assertEqual(len(data), 4)
        self.assertEqual(data[0][0].year, 2025)
        self.assertEqual(data[0][0].month, 1)

    def test_multichannel_batch(self):
        gen1 = TelemetryGenerator(WaveformType.SINE)
        gen2 = TelemetryGenerator(WaveformType.COSINE)
        multi = MultiChannelTelemetryGenerator([gen1, gen2])
        data = multi.generate_batch(sampling_rate=5.0, duration=1.0)
        self.assertEqual(len(data), 5)
        for sample in data:
            self.assertEqual(len(sample), 2)
            self.assertIn(0, sample)
            self.assertIn(1, sample)

    def test_batch_invalid_sampling_rate(self):
        gen = TelemetryGenerator(WaveformType.SINE)
        with self.assertRaises(ValueError):
            gen.generate_batch(sampling_rate=0, duration=1.0)
        with self.assertRaises(ValueError):
            gen.generate_batch(sampling_rate=-1, duration=1.0)

    def test_batch_invalid_duration(self):
        gen = TelemetryGenerator(WaveformType.SINE)
        with self.assertRaises(ValueError):
            gen.generate_batch(sampling_rate=1.0, duration=0)
        with self.assertRaises(ValueError):
            gen.generate_batch(sampling_rate=1.0, duration=-1)


class TestPhaseShift(unittest.TestCase):
    """Tests for the phase shift parameter."""

    def test_sine_with_phase(self):
        import math

        # Sine with pi/2 phase should be equivalent to cosine at t=0
        gen = TelemetryGenerator(WaveformType.SINE, phase=math.pi / 2)
        value = gen.generate_point(0)
        self.assertAlmostEqual(value, 1.0, places=5)

    def test_cosine_with_phase(self):
        import math

        # Cosine with pi/2 phase should be equivalent to -sine at t=0
        gen = TelemetryGenerator(WaveformType.COSINE, phase=math.pi / 2)
        value = gen.generate_point(0)
        self.assertAlmostEqual(value, 0.0, places=5)

    def test_square_with_phase(self):
        import math

        gen = TelemetryGenerator(WaveformType.SQUARE, frequency=1.0, phase=math.pi)
        # With pi phase shift at t=0, sin(pi) = 0 which is on the boundary
        # Test at a point where we can be certain of the sign
        # At t=0.25 with no phase, sin(2*pi*0.25) = sin(pi/2) = 1 (positive)
        # With pi phase shift: sin(pi/2 + pi) = sin(3*pi/2) = -1 (negative)
        value = gen.generate_point(0.25)
        self.assertEqual(value, -1.0)


class TestExponentialDecay(unittest.TestCase):
    """Tests for the exponential decay waveform."""

    def test_exponential_decay_at_t0(self):
        gen = TelemetryGenerator(
            WaveformType.EXPONENTIAL_DECAY, frequency=1.0, amplitude=2.0, offset=0.5
        )
        # At t=0, exp(0) = 1, so value should be amplitude * 1 + offset = 2.5
        value = gen.generate_point(0)
        self.assertAlmostEqual(value, 2.5, places=5)

    def test_exponential_decay_at_t1(self):
        import math

        gen = TelemetryGenerator(
            WaveformType.EXPONENTIAL_DECAY, frequency=1.0, amplitude=1.0, offset=0.0
        )
        # At t=1, value should be exp(-1) ≈ 0.3679
        value = gen.generate_point(1)
        self.assertAlmostEqual(value, math.exp(-1), places=5)


class TestDataExport(unittest.TestCase):
    """Tests for data export utilities."""

    def setUp(self):
        self.sample_data = [
            (datetime(2025, 1, 1, 12, 0, 0), 1.5),
            (datetime(2025, 1, 1, 12, 0, 1), 2.5),
            (datetime(2025, 1, 1, 12, 0, 2), 3.5),
        ]

    def test_to_json(self):
        import json

        json_str = to_json(self.sample_data)
        parsed = json.loads(json_str)
        self.assertEqual(len(parsed), 3)
        self.assertEqual(parsed[0]["value"], 1.5)
        self.assertIn("timestamp", parsed[0])

    def test_to_csv(self):
        csv_str = to_csv(self.sample_data)
        lines = csv_str.strip().split("\n")
        self.assertEqual(len(lines), 4)  # Header + 3 data rows
        # Handle both Unix and Windows line endings
        self.assertTrue(lines[0].strip() == "timestamp,value")

    def test_to_dict(self):
        result = to_dict(self.sample_data)
        self.assertEqual(len(result), 3)
        self.assertIsInstance(result[0]["timestamp"], datetime)
        self.assertEqual(result[0]["value"], 1.5)

    def test_to_dict_with_format(self):
        result = to_dict(self.sample_data, datetime_format="%Y-%m-%d")
        self.assertEqual(result[0]["timestamp"], "2025-01-01")

    def test_json_roundtrip(self):
        json_str = to_json(self.sample_data)
        restored = from_json(json_str)
        self.assertEqual(len(restored), 3)
        self.assertAlmostEqual(restored[0][1], 1.5)

    def test_csv_roundtrip(self):
        csv_str = to_csv(self.sample_data)
        restored = from_csv(csv_str)
        self.assertEqual(len(restored), 3)
        self.assertAlmostEqual(restored[0][1], 1.5)


if __name__ == "__main__":
    unittest.main()
