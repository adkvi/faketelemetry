import unittest
import math
from datetime import datetime, timedelta

from faketelemetry import TelemetryGenerator, WaveformType, MultiChannelTelemetryGenerator
from faketelemetry.stats import describe, describe_values, describe_multi


class TestDescribe(unittest.TestCase):
    def test_basic_stats(self):
        gen = TelemetryGenerator(WaveformType.SINE, amplitude=5.0, seed=42)
        data = gen.batch(1000, sampling_rate=100)
        stats = describe(data)

        self.assertEqual(stats["count"], 1000)
        self.assertTrue(-5.0 <= stats["min"] <= 5.0)
        self.assertTrue(-5.0 <= stats["max"] <= 5.0)
        self.assertTrue(stats["max"] > stats["min"])
        self.assertIn("mean", stats)
        self.assertIn("std", stats)
        self.assertIn("range", stats)
        self.assertIn("p50", stats)
        self.assertIn("p95", stats)
        self.assertIn("start", stats)
        self.assertIn("end", stats)
        self.assertIn("duration_s", stats)

    def test_empty_data(self):
        stats = describe([])
        self.assertEqual(stats["count"], 0)

    def test_custom_percentiles(self):
        gen = TelemetryGenerator(WaveformType.SINE, amplitude=1.0)
        data = gen.batch(100, sampling_rate=10)
        stats = describe(data, percentiles=(0.10, 0.90))
        self.assertIn("p10", stats)
        self.assertIn("p90", stats)
        self.assertNotIn("p50", stats)

    def test_constant_signal(self):
        gen = TelemetryGenerator(WaveformType.SINE, amplitude=0.0, offset=42.0)
        data = gen.batch(50, sampling_rate=10)
        stats = describe(data)
        self.assertAlmostEqual(stats["mean"], 42.0)
        self.assertAlmostEqual(stats["std"], 0.0)
        self.assertAlmostEqual(stats["range"], 0.0)


class TestDescribeValues(unittest.TestCase):
    def test_basic(self):
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        stats = describe_values(values)
        self.assertEqual(stats["count"], 5)
        self.assertAlmostEqual(stats["mean"], 3.0)
        self.assertAlmostEqual(stats["min"], 1.0)
        self.assertAlmostEqual(stats["max"], 5.0)

    def test_empty(self):
        stats = describe_values([])
        self.assertEqual(stats["count"], 0)

    def test_no_timestamps(self):
        stats = describe_values([10.0, 20.0, 30.0])
        self.assertNotIn("start", stats)
        self.assertNotIn("end", stats)


class TestDescribeMulti(unittest.TestCase):
    def test_basic(self):
        multi = MultiChannelTelemetryGenerator({
            "a": TelemetryGenerator(WaveformType.SINE, amplitude=1.0),
            "b": TelemetryGenerator(WaveformType.COSINE, amplitude=2.0),
        })
        rows = multi.batch(100, sampling_rate=10)
        stats = describe_multi(rows)

        self.assertIn("a", stats)
        self.assertIn("b", stats)
        self.assertEqual(stats["a"]["count"], 100)
        self.assertEqual(stats["b"]["count"], 100)

    def test_empty(self):
        stats = describe_multi([])
        self.assertEqual(stats, {})


if __name__ == "__main__":
    unittest.main()
