import unittest
import json

from faketelemetry import TelemetryGenerator, WaveformType, NoiseInjector, NoiseType


class TestConfig(unittest.TestCase):
    def test_roundtrip_basic(self):
        gen = TelemetryGenerator(
            WaveformType.SINE,
            frequency=2.0,
            amplitude=5.0,
            offset=10.0,
            phase=1.5,
            name="sensor_x",
        )
        cfg = gen.to_config()
        gen2 = TelemetryGenerator.from_config(cfg)

        self.assertEqual(gen2.waveform, WaveformType.SINE)
        self.assertEqual(gen2.frequency, 2.0)
        self.assertEqual(gen2.amplitude, 5.0)
        self.assertEqual(gen2.offset, 10.0)
        self.assertAlmostEqual(gen2.phase, 1.5)
        self.assertEqual(gen2.name, "sensor_x")

    def test_roundtrip_with_noise(self):
        gen = TelemetryGenerator(
            WaveformType.COSINE,
            noise_injector=NoiseInjector(
                noise_level=0.5,
                noise_type=NoiseType.UNIFORM,
            ),
        )
        cfg = gen.to_config()
        gen2 = TelemetryGenerator.from_config(cfg)

        self.assertIsNotNone(gen2.noise_injector)
        self.assertEqual(gen2.noise_injector.noise_level, 0.5)
        self.assertEqual(gen2.noise_injector.noise_type, NoiseType.UNIFORM)

    def test_roundtrip_with_clamp(self):
        gen = TelemetryGenerator(
            WaveformType.SINE,
            clamp_min=-2.0,
            clamp_max=2.0,
        )
        cfg = gen.to_config()
        gen2 = TelemetryGenerator.from_config(cfg)
        self.assertEqual(gen2.clamp_min, -2.0)
        self.assertEqual(gen2.clamp_max, 2.0)

    def test_json_serializable(self):
        gen = TelemetryGenerator(
            WaveformType.TRIANGLE,
            frequency=3.0,
            noise_injector=NoiseInjector(0.1, NoiseType.GAUSSIAN),
            name="tri",
        )
        cfg = gen.to_config()
        json_str = json.dumps(cfg)
        cfg2 = json.loads(json_str)
        gen2 = TelemetryGenerator.from_config(cfg2)
        self.assertEqual(gen2.waveform, WaveformType.TRIANGLE)
        self.assertEqual(gen2.name, "tri")

    def test_config_without_optional_fields(self):
        cfg = {"waveform": "sine"}
        gen = TelemetryGenerator.from_config(cfg)
        self.assertEqual(gen.waveform, WaveformType.SINE)
        self.assertEqual(gen.frequency, 1.0)
        self.assertIsNone(gen.noise_injector)
        self.assertIsNone(gen.clamp_min)

    def test_values_match(self):
        gen1 = TelemetryGenerator(
            WaveformType.SQUARE,
            frequency=2.0,
            amplitude=3.0,
            duty_cycle=0.3,
        )
        gen2 = TelemetryGenerator.from_config(gen1.to_config())
        # Same config -> same output at multiple time points
        for t in [0.0, 0.1, 0.25, 0.5, 1.0]:
            self.assertAlmostEqual(
                gen1.generate_point(t),
                gen2.generate_point(t),
                places=10,
            )


if __name__ == "__main__":
    unittest.main()
