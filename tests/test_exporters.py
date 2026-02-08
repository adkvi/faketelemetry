import unittest
import json
import io
from datetime import datetime

from faketelemetry import TelemetryGenerator, WaveformType, MultiChannelTelemetryGenerator
from faketelemetry.exporters import to_csv, to_json, to_ndjson, to_multichannel_csv


class TestExporters(unittest.TestCase):
    def setUp(self):
        gen = TelemetryGenerator(WaveformType.SINE, frequency=1.0, seed=42)
        self.data = gen.batch(num_samples=10, sampling_rate=10)

    # ----- CSV -----

    def test_to_csv_string(self):
        result = to_csv(self.data)
        self.assertIsNotNone(result)
        lines = result.strip().split("\n")
        self.assertEqual(len(lines), 11)  # header + 10 rows
        self.assertTrue(lines[0].startswith("timestamp"))

    def test_to_csv_file(self):
        buf = io.StringIO()
        ret = to_csv(self.data, buf)
        self.assertIsNone(ret)
        buf.seek(0)
        lines = buf.read().strip().split("\n")
        self.assertEqual(len(lines), 11)

    def test_to_csv_custom_delimiter(self):
        result = to_csv(self.data, delimiter="\t")
        self.assertIn("\t", result)

    # ----- JSON -----

    def test_to_json_string(self):
        result = to_json(self.data)
        parsed = json.loads(result)
        self.assertEqual(len(parsed), 10)
        self.assertIn("timestamp", parsed[0])
        self.assertIn("value", parsed[0])

    def test_to_json_file(self):
        buf = io.StringIO()
        to_json(self.data, buf)
        buf.seek(0)
        parsed = json.loads(buf.read())
        self.assertEqual(len(parsed), 10)

    # ----- NDJSON -----

    def test_to_ndjson_string(self):
        result = to_ndjson(self.data)
        lines = result.strip().split("\n")
        self.assertEqual(len(lines), 10)
        for line in lines:
            obj = json.loads(line)
            self.assertIn("timestamp", obj)
            self.assertIn("value", obj)

    # ----- Multi-channel CSV -----

    def test_to_multichannel_csv(self):
        multi = MultiChannelTelemetryGenerator({
            "a": TelemetryGenerator(WaveformType.SINE),
            "b": TelemetryGenerator(WaveformType.COSINE),
        })
        rows = multi.batch(num_samples=5, sampling_rate=10)
        result = to_multichannel_csv(rows)
        lines = result.strip().split("\n")
        self.assertEqual(len(lines), 6)  # header + 5 rows
        self.assertIn("timestamp", lines[0])
        self.assertIn("a", lines[0])
        self.assertIn("b", lines[0])

    def test_to_multichannel_csv_empty(self):
        result = to_multichannel_csv([])
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
