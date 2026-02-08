import unittest
import json
from datetime import datetime

from faketelemetry import TelemetryGenerator, WaveformType, MultiChannelTelemetryGenerator
from faketelemetry.formatters import (
    to_influxdb,
    to_influxdb_multi,
    to_mqtt_json,
    to_mqtt_json_multi,
    to_prometheus,
)


class TestInfluxDB(unittest.TestCase):
    def setUp(self):
        gen = TelemetryGenerator(WaveformType.SINE, seed=1)
        self.data = gen.batch(5, sampling_rate=1)

    def test_basic(self):
        lines = to_influxdb(self.data)
        self.assertEqual(len(lines), 5)
        for line in lines:
            self.assertTrue(line.startswith("telemetry "))
            self.assertIn("value=", line)

    def test_custom_measurement_and_tags(self):
        lines = to_influxdb(
            self.data,
            measurement="sensors",
            tags={"room": "lab", "floor": "2"},
        )
        for line in lines:
            self.assertTrue(line.startswith("sensors,"))
            self.assertIn("floor=2", line)
            self.assertIn("room=lab", line)

    def test_precision(self):
        lines_s = to_influxdb(self.data, precision="s")
        lines_ms = to_influxdb(self.data, precision="ms")
        # ms timestamps should be larger numbers
        ts_s = int(lines_s[0].split()[-1])
        ts_ms = int(lines_ms[0].split()[-1])
        self.assertTrue(ts_ms > ts_s)

    def test_invalid_precision(self):
        with self.assertRaises(ValueError):
            to_influxdb(self.data, precision="invalid")

    def test_multi(self):
        multi = MultiChannelTelemetryGenerator(
            {
                "a": TelemetryGenerator(WaveformType.SINE),
                "b": TelemetryGenerator(WaveformType.COSINE),
            }
        )
        rows = multi.batch(3, sampling_rate=1)
        lines = to_influxdb_multi(rows, measurement="multi_test")
        self.assertEqual(len(lines), 3)
        for line in lines:
            self.assertIn("a=", line)
            self.assertIn("b=", line)


class TestMQTT(unittest.TestCase):
    def setUp(self):
        gen = TelemetryGenerator(WaveformType.SINE, seed=1)
        self.data = gen.batch(3, sampling_rate=1)

    def test_basic(self):
        payloads = to_mqtt_json(self.data)
        self.assertEqual(len(payloads), 3)
        for p in payloads:
            obj = json.loads(p)
            self.assertIn("timestamp", obj)
            self.assertIn("value", obj)

    def test_sensor_id(self):
        payloads = to_mqtt_json(self.data, sensor_id="temp-01")
        obj = json.loads(payloads[0])
        self.assertEqual(obj["sensor_id"], "temp-01")

    def test_extra_fields(self):
        payloads = to_mqtt_json(self.data, extra_fields={"unit": "C"})
        obj = json.loads(payloads[0])
        self.assertEqual(obj["unit"], "C")

    def test_multi(self):
        multi = MultiChannelTelemetryGenerator(
            {
                "x": TelemetryGenerator(WaveformType.SINE),
            }
        )
        rows = multi.batch(2, sampling_rate=1)
        payloads = to_mqtt_json_multi(rows, device_id="dev-01")
        self.assertEqual(len(payloads), 2)
        obj = json.loads(payloads[0])
        self.assertEqual(obj["device_id"], "dev-01")


class TestPrometheus(unittest.TestCase):
    def setUp(self):
        gen = TelemetryGenerator(WaveformType.SINE, seed=1)
        self.data = gen.batch(3, sampling_rate=1)

    def test_basic(self):
        text = to_prometheus(self.data)
        lines = text.strip().split("\n")
        self.assertTrue(lines[0].startswith("# TYPE"))
        self.assertTrue(any("telemetry_value" in l for l in lines))

    def test_with_labels_and_help(self):
        text = to_prometheus(
            self.data,
            metric_name="sensor_temp",
            labels={"room": "lab"},
            help_text="Temperature reading",
        )
        self.assertIn("# HELP sensor_temp Temperature reading", text)
        self.assertIn('room="lab"', text)

    def test_type_annotation(self):
        text = to_prometheus(self.data, type_text="counter")
        self.assertIn("# TYPE telemetry_value counter", text)


if __name__ == "__main__":
    unittest.main()
