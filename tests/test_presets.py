import unittest
from faketelemetry import TelemetryGenerator
from faketelemetry.presets import SensorPreset


class TestSensorPreset(unittest.TestCase):
    """Smoke tests: each preset should return a valid generator that produces data."""

    def _check_preset(self, gen: TelemetryGenerator, expected_name: str):
        self.assertIsInstance(gen, TelemetryGenerator)
        self.assertEqual(gen.name, expected_name)
        # Should generate at least one batch without error
        points = gen.batch(num_samples=10, sampling_rate=10)
        self.assertEqual(len(points), 10)

    def test_temperature(self):
        self._check_preset(SensorPreset.temperature(seed=1), "temperature_C")

    def test_pressure(self):
        self._check_preset(SensorPreset.pressure(seed=1), "pressure_hPa")

    def test_humidity(self):
        gen = SensorPreset.humidity(seed=1)
        self._check_preset(gen, "humidity_pct")
        # Clamp check
        vals = gen.batch_values(100, 10)
        self.assertTrue(all(0 <= v <= 100 for v in vals))

    def test_battery_voltage(self):
        gen = SensorPreset.battery_voltage(seed=1)
        self._check_preset(gen, "battery_V")
        vals = gen.batch_values(50, 10)
        self.assertTrue(all(2.8 <= v <= 4.2 for v in vals))

    def test_rpm(self):
        gen = SensorPreset.rpm(seed=1)
        self._check_preset(gen, "engine_rpm")
        vals = gen.batch_values(50, 10)
        self.assertTrue(all(v >= 0 for v in vals))

    def test_cpu_usage(self):
        gen = SensorPreset.cpu_usage(seed=1)
        self._check_preset(gen, "cpu_pct")
        vals = gen.batch_values(50, 10)
        self.assertTrue(all(0 <= v <= 100 for v in vals))

    def test_network_latency(self):
        gen = SensorPreset.network_latency(seed=1)
        self._check_preset(gen, "latency_ms")
        vals = gen.batch_values(50, 10)
        self.assertTrue(all(v >= 1 for v in vals))

    def test_heart_rate(self):
        gen = SensorPreset.heart_rate(seed=1)
        self._check_preset(gen, "heart_rate_bpm")
        vals = gen.batch_values(50, 10)
        self.assertTrue(all(30 <= v <= 220 for v in vals))

    def test_accelerometer(self):
        self._check_preset(SensorPreset.accelerometer(seed=1), "accel_g")

    def test_gps_coordinate(self):
        self._check_preset(SensorPreset.gps_coordinate(seed=1), "gps_lat")

    # --- new presets ---

    def test_light_lux(self):
        gen = SensorPreset.light_lux(seed=1)
        self._check_preset(gen, "light_lux")
        vals = gen.batch_values(50, 10)
        self.assertTrue(all(v >= 0 for v in vals))

    def test_co2_ppm(self):
        gen = SensorPreset.co2_ppm(seed=1)
        self._check_preset(gen, "co2_ppm")
        vals = gen.batch_values(50, 10)
        self.assertTrue(all(v >= 200 for v in vals))

    def test_wind_speed(self):
        gen = SensorPreset.wind_speed(seed=1)
        self._check_preset(gen, "wind_m_s")
        vals = gen.batch_values(50, 10)
        self.assertTrue(all(v >= 0 for v in vals))

    def test_memory_usage(self):
        gen = SensorPreset.memory_usage(seed=1)
        self._check_preset(gen, "memory_pct")
        vals = gen.batch_values(50, 10)
        self.assertTrue(all(0 <= v <= 100 for v in vals))

    def test_disk_io(self):
        gen = SensorPreset.disk_io(seed=1)
        self._check_preset(gen, "disk_io_mbps")
        vals = gen.batch_values(50, 10)
        self.assertTrue(all(v >= 0 for v in vals))

    def test_flow_rate(self):
        gen = SensorPreset.flow_rate(seed=1)
        self._check_preset(gen, "flow_l_min")
        vals = gen.batch_values(50, 10)
        self.assertTrue(all(v >= 0 for v in vals))

    def test_vibration(self):
        self._check_preset(SensorPreset.vibration(seed=1), "vibration_mm_s")

    def test_ph_level(self):
        gen = SensorPreset.ph_level(seed=1)
        self._check_preset(gen, "ph")
        vals = gen.batch_values(50, 10)
        self.assertTrue(all(0 <= v <= 14 for v in vals))

    def test_signal_strength(self):
        gen = SensorPreset.signal_strength(seed=1)
        self._check_preset(gen, "rssi_dBm")
        vals = gen.batch_values(50, 10)
        self.assertTrue(all(-120 <= v <= 0 for v in vals))


if __name__ == "__main__":
    unittest.main()
