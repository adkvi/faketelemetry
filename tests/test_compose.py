import unittest
from datetime import datetime

from faketelemetry import TelemetryGenerator, WaveformType, CompositeGenerator, compose


class TestCompositeGenerator(unittest.TestCase):
    def test_add_two_generators(self):
        g1 = TelemetryGenerator(WaveformType.SINE, frequency=1.0, amplitude=1.0)
        g2 = TelemetryGenerator(WaveformType.COSINE, frequency=1.0, amplitude=1.0)
        combined = g1 + g2
        self.assertIsInstance(combined, CompositeGenerator)
        # sin(0) + cos(0) = 0 + 1 = 1
        self.assertAlmostEqual(combined.generate_point(0), 1.0, places=5)

    def test_add_generator_and_scalar(self):
        g = TelemetryGenerator(WaveformType.SINE, frequency=1.0, amplitude=1.0)
        biased = g + 10.0
        # sin(0) + 10 = 10
        self.assertAlmostEqual(biased.generate_point(0), 10.0, places=5)

    def test_radd_scalar_and_generator(self):
        g = TelemetryGenerator(WaveformType.SINE, frequency=1.0, amplitude=1.0)
        biased = 5.0 + g
        self.assertAlmostEqual(biased.generate_point(0), 5.0, places=5)

    def test_subtract(self):
        g1 = TelemetryGenerator(WaveformType.SINE, amplitude=3.0)
        g2 = TelemetryGenerator(WaveformType.SINE, amplitude=1.0)
        diff = g1 - g2
        # Both are sin(0) = 0, so diff = 0
        self.assertAlmostEqual(diff.generate_point(0), 0.0, places=5)

    def test_rsub(self):
        g = TelemetryGenerator(WaveformType.COSINE, amplitude=1.0)
        result = 10.0 - g
        # 10 - cos(0) = 10 - 1 = 9
        self.assertAlmostEqual(result.generate_point(0), 9.0, places=5)

    def test_multiply(self):
        g1 = TelemetryGenerator(WaveformType.COSINE, amplitude=2.0)
        g2 = TelemetryGenerator(WaveformType.COSINE, amplitude=3.0)
        product = g1 * g2
        # cos(0)*2 * cos(0)*3 = 2*3 = 6
        self.assertAlmostEqual(product.generate_point(0), 6.0, places=5)

    def test_multiply_by_scalar(self):
        g = TelemetryGenerator(WaveformType.COSINE, amplitude=1.0)
        scaled = g * 0.5
        # cos(0) * 0.5 = 0.5
        self.assertAlmostEqual(scaled.generate_point(0), 0.5, places=5)

    def test_rmul_scalar(self):
        g = TelemetryGenerator(WaveformType.COSINE, amplitude=1.0)
        scaled = 3.0 * g
        self.assertAlmostEqual(scaled.generate_point(0), 3.0, places=5)

    def test_negate(self):
        g = TelemetryGenerator(WaveformType.COSINE, amplitude=1.0)
        neg = -g
        # -cos(0) = -1
        self.assertAlmostEqual(neg.generate_point(0), -1.0, places=5)

    def test_chain_three(self):
        g1 = TelemetryGenerator(WaveformType.SINE, amplitude=1.0)
        g2 = TelemetryGenerator(WaveformType.SINE, amplitude=0.5)
        g3 = TelemetryGenerator(WaveformType.SINE, amplitude=0.25)
        chained = g1 + g2 + g3
        # All sin(0)=0, so sum = 0
        self.assertAlmostEqual(chained.generate_point(0), 0.0, places=5)

    def test_compose_function(self):
        g1 = TelemetryGenerator(WaveformType.COSINE, amplitude=1.0)
        g2 = TelemetryGenerator(WaveformType.COSINE, amplitude=2.0)
        g3 = TelemetryGenerator(WaveformType.COSINE, amplitude=3.0)
        combined = compose(g1, g2, g3)
        # cos(0)=1, so 1+2+3=6
        self.assertAlmostEqual(combined.generate_point(0), 6.0, places=5)

    def test_compose_mul(self):
        g1 = TelemetryGenerator(WaveformType.COSINE, amplitude=2.0)
        g2 = TelemetryGenerator(WaveformType.COSINE, amplitude=3.0)
        product = compose(g1, g2, operation="mul")
        self.assertAlmostEqual(product.generate_point(0), 6.0, places=5)

    def test_compose_too_few(self):
        g = TelemetryGenerator(WaveformType.SINE)
        with self.assertRaises(ValueError):
            compose(g)

    def test_batch(self):
        g1 = TelemetryGenerator(WaveformType.SINE, amplitude=1.0)
        combined = g1 + 5.0
        points = combined.batch(10, sampling_rate=10)
        self.assertEqual(len(points), 10)
        for ts, val in points:
            self.assertIsInstance(ts, datetime)

    def test_batch_values(self):
        combined = TelemetryGenerator(WaveformType.COSINE, amplitude=1.0) + 1.0
        vals = combined.batch_values(5, sampling_rate=10)
        self.assertEqual(len(vals), 5)
        # cos(0)+1 = 2
        self.assertAlmostEqual(vals[0], 2.0, places=5)

    def test_to_dict(self):
        combined = TelemetryGenerator(WaveformType.SINE) + 0.0
        combined.name = "test"
        rows = combined.to_dict(3, sampling_rate=10)
        self.assertEqual(len(rows), 3)
        self.assertIn("timestamp", rows[0])
        self.assertIn("value", rows[0])

    def test_reset(self):
        g1 = TelemetryGenerator(WaveformType.RANDOM_WALK, seed=1)
        combined = g1 + 0.0
        combined.generate_point(0)
        combined.generate_point(0.1)
        combined.reset()
        self.assertEqual(g1._walk_state, 0.0)

    def test_repr(self):
        g1 = TelemetryGenerator(WaveformType.SINE)
        g2 = TelemetryGenerator(WaveformType.COSINE)
        combined = g1 + g2
        r = repr(combined)
        self.assertIn("+", r)


if __name__ == "__main__":
    unittest.main()
