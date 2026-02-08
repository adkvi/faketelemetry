import unittest
from faketelemetry import AnomalyInjector, AnomalyConfig, AnomalyType


class TestAnomalyInjector(unittest.TestCase):
    def test_spike(self):
        cfg = AnomalyConfig(
            AnomalyType.SPIKE, probability=1.0, magnitude=100.0
        )
        inj = AnomalyInjector(configs=[cfg], seed=42)
        result = inj.apply(0.0)
        self.assertTrue(abs(result) == 100.0)

    def test_spike_probabilistic(self):
        cfg = AnomalyConfig(
            AnomalyType.SPIKE, probability=0.0, magnitude=100.0
        )
        inj = AnomalyInjector(configs=[cfg], seed=42)
        # probability 0 -> no spike ever
        result = inj.apply(5.0)
        self.assertEqual(result, 5.0)

    def test_dropout(self):
        cfg = AnomalyConfig(
            AnomalyType.DROPOUT, probability=1.0, duration_samples=3
        )
        inj = AnomalyInjector(configs=[cfg], seed=1)
        # First call triggers, next 2 are continuation
        self.assertEqual(inj.apply(10.0), 0.0)
        self.assertEqual(inj.apply(10.0), 0.0)
        self.assertEqual(inj.apply(10.0), 0.0)

    def test_drift(self):
        cfg = AnomalyConfig(
            AnomalyType.DRIFT, probability=1.0, drift_rate=0.5
        )
        inj = AnomalyInjector(configs=[cfg], seed=1)
        v1 = inj.apply(0.0)
        v2 = inj.apply(0.0)
        v3 = inj.apply(0.0)
        self.assertAlmostEqual(v1, 0.5)
        self.assertAlmostEqual(v2, 1.0)
        self.assertAlmostEqual(v3, 1.5)

    def test_flatline(self):
        cfg = AnomalyConfig(
            AnomalyType.FLATLINE, probability=1.0, duration_samples=3
        )
        inj = AnomalyInjector(configs=[cfg], seed=1)
        v1 = inj.apply(7.0)
        v2 = inj.apply(99.0)  # should still be 7.0
        v3 = inj.apply(99.0)  # should still be 7.0
        self.assertEqual(v1, 7.0)
        self.assertEqual(v2, 7.0)
        self.assertEqual(v3, 7.0)

    def test_stuck_at(self):
        cfg = AnomalyConfig(
            AnomalyType.STUCK_AT,
            probability=1.0,
            duration_samples=2,
            stuck_value=42.0,
        )
        inj = AnomalyInjector(configs=[cfg], seed=1)
        self.assertEqual(inj.apply(1.0), 42.0)
        self.assertEqual(inj.apply(2.0), 42.0)

    def test_jitter(self):
        cfg = AnomalyConfig(
            AnomalyType.JITTER, probability=1.0, jitter_range=5.0
        )
        inj = AnomalyInjector(configs=[cfg], seed=42)
        values = [inj.apply(10.0) for _ in range(100)]
        self.assertTrue(all(5.0 <= v <= 15.0 for v in values))
        self.assertTrue(any(abs(v - 10.0) > 0.5 for v in values))

    def test_multiple_anomalies(self):
        cfgs = [
            AnomalyConfig(AnomalyType.DRIFT, probability=1.0, drift_rate=1.0),
            AnomalyConfig(AnomalyType.SPIKE, probability=0.0, magnitude=100.0),
        ]
        inj = AnomalyInjector(configs=cfgs, seed=1)
        # Drift should accumulate, spike never fires
        self.assertAlmostEqual(inj.apply(0.0), 1.0)
        self.assertAlmostEqual(inj.apply(0.0), 2.0)

    def test_reset(self):
        cfg = AnomalyConfig(
            AnomalyType.DRIFT, probability=1.0, drift_rate=1.0
        )
        inj = AnomalyInjector(configs=[cfg], seed=1)
        inj.apply(0.0)
        inj.apply(0.0)
        inj.reset()
        self.assertEqual(inj._drift_accum[0], 0.0)

    def test_invalid_probability(self):
        with self.assertRaises(ValueError):
            AnomalyConfig(AnomalyType.SPIKE, probability=2.0)

    def test_invalid_duration(self):
        with self.assertRaises(ValueError):
            AnomalyConfig(AnomalyType.FLATLINE, duration_samples=0)


if __name__ == "__main__":
    unittest.main()
