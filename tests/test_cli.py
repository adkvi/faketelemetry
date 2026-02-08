import json
import os
import tempfile
import unittest
from io import StringIO
from unittest import mock

from faketelemetry.cli import build_parser, main


class _CaptureMixin:
    """Helper that calls main(argv) and captures stdout."""

    def _run(self, argv):
        buf = StringIO()
        with mock.patch("sys.stdout", buf):
            main(argv)
        return buf.getvalue()


class TestGenerate(_CaptureMixin, unittest.TestCase):
    def test_table_output(self):
        out = self._run(["generate", "-w", "sine", "-n", "5", "--rate", "10"])
        lines = out.strip().split("\n")
        # header + 5 data rows
        self.assertEqual(len(lines), 6)
        self.assertIn("timestamp", lines[0])
        self.assertIn("value", lines[0])

    def test_csv_output(self):
        out = self._run(["generate", "-w", "cosine", "-n", "3", "-f", "csv"])
        lines = out.strip().split("\n")
        self.assertEqual(len(lines), 4)  # header + 3
        self.assertIn("timestamp", lines[0])

    def test_json_output(self):
        out = self._run(["generate", "-w", "sine", "-n", "3", "-f", "json"])
        data = json.loads(out)
        self.assertEqual(len(data), 3)
        self.assertIn("timestamp", data[0])
        self.assertIn("value", data[0])

    def test_ndjson_output(self):
        out = self._run(["generate", "-w", "sine", "-n", "3", "-f", "ndjson"])
        lines = out.strip().split("\n")
        self.assertEqual(len(lines), 3)
        obj = json.loads(lines[0])
        self.assertIn("value", obj)

    def test_influxdb_output(self):
        out = self._run(["generate", "-w", "sine", "-n", "3", "-f", "influxdb"])
        lines = out.strip().split("\n")
        self.assertEqual(len(lines), 3)
        self.assertTrue(lines[0].startswith("telemetry "))

    def test_with_noise(self):
        out = self._run(["generate", "-w", "sine", "-n", "5", "--noise-level", "0.5", "--seed", "42"])
        lines = out.strip().split("\n")
        self.assertEqual(len(lines), 6)

    def test_no_header(self):
        out = self._run(["generate", "-w", "sine", "-n", "3", "--no-header"])
        lines = out.strip().split("\n")
        self.assertEqual(len(lines), 3)  # no header row
        self.assertNotIn("timestamp", lines[0])

    def test_waveform_params(self):
        out = self._run([
            "generate", "-w", "square",
            "--freq", "2.0", "--amp", "5.0", "--offset", "10.0",
            "--duty-cycle", "0.3", "-n", "3",
        ])
        lines = out.strip().split("\n")
        self.assertEqual(len(lines), 4)

    def test_output_to_file(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            self._run(["generate", "-w", "sine", "-n", "5", "-f", "csv", "-o", path])
            with open(path, "r") as f:
                content = f.read()
            lines = content.strip().split("\n")
            self.assertEqual(len(lines), 6)
        finally:
            os.unlink(path)


class TestPreset(_CaptureMixin, unittest.TestCase):
    def test_basic(self):
        out = self._run(["preset", "temperature", "-n", "5"])
        lines = out.strip().split("\n")
        self.assertEqual(len(lines), 6)

    def test_csv(self):
        out = self._run(["preset", "cpu_usage", "-n", "3", "-f", "csv"])
        lines = out.strip().split("\n")
        self.assertEqual(len(lines), 4)

    def test_with_seed(self):
        out1 = self._run(["preset", "pressure", "-n", "5", "--seed", "42", "-f", "json"])
        out2 = self._run(["preset", "pressure", "-n", "5", "--seed", "42", "-f", "json"])
        vals1 = [r["value"] for r in json.loads(out1)]
        vals2 = [r["value"] for r in json.loads(out2)]
        self.assertEqual(vals1, vals2)


class TestMulti(_CaptureMixin, unittest.TestCase):
    def test_basic_table(self):
        out = self._run(["multi", "temperature,pressure", "-n", "3"])
        lines = out.strip().split("\n")
        self.assertEqual(len(lines), 4)  # header + 3
        self.assertIn("temperature", lines[0])
        self.assertIn("pressure", lines[0])

    def test_csv(self):
        out = self._run(["multi", "cpu_usage,heart_rate", "-n", "3", "-f", "csv"])
        lines = out.strip().split("\n")
        self.assertEqual(len(lines), 4)

    def test_json(self):
        out = self._run(["multi", "temperature,humidity", "-n", "3", "-f", "json"])
        data = json.loads(out)
        self.assertEqual(len(data), 3)
        self.assertIn("temperature", data[0])

    def test_influxdb(self):
        out = self._run(["multi", "temperature,pressure", "-n", "3", "-f", "influxdb"])
        lines = out.strip().split("\n")
        self.assertEqual(len(lines), 3)

    def test_invalid_preset(self):
        with self.assertRaises(SystemExit):
            self._run(["multi", "temperature,nonexistent", "-n", "3"])


class TestFromConfig(_CaptureMixin, unittest.TestCase):
    def test_basic(self):
        cfg = {"waveform": "sine", "frequency": 2.0, "amplitude": 3.0}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump(cfg, f)
            path = f.name
        try:
            out = self._run(["from-config", path, "-n", "5", "-f", "json"])
            data = json.loads(out)
            self.assertEqual(len(data), 5)
        finally:
            os.unlink(path)

    def test_bad_file(self):
        with self.assertRaises(SystemExit):
            self._run(["from-config", "/nonexistent/path.json", "-n", "3"])


class TestList(_CaptureMixin, unittest.TestCase):
    def test_presets(self):
        out = self._run(["list", "presets"])
        self.assertIn("temperature", out)
        self.assertIn("cpu_usage", out)
        self.assertIn("signal_strength", out)

    def test_waveforms(self):
        out = self._run(["list", "waveforms"])
        self.assertIn("sine", out)
        self.assertIn("chirp", out)
        self.assertNotIn("custom", out)

    def test_noise(self):
        out = self._run(["list", "noise"])
        self.assertIn("gaussian", out)
        self.assertIn("brownian", out)

    def test_anomalies(self):
        out = self._run(["list", "anomalies"])
        self.assertIn("spike", out)
        self.assertIn("drift", out)


class TestDescribe(_CaptureMixin, unittest.TestCase):
    def test_preset(self):
        out = self._run(["describe", "--preset", "temperature", "-n", "100", "--rate", "10"])
        self.assertIn("count:", out)
        self.assertIn("mean:", out)
        self.assertIn("std:", out)
        self.assertIn("min:", out)
        self.assertIn("max:", out)
        self.assertIn("p50:", out)

    def test_waveform(self):
        out = self._run(["describe", "-w", "sine", "-n", "200", "--rate", "50"])
        self.assertIn("count:", out)
        self.assertIn("200", out)

    def test_with_seed(self):
        out1 = self._run(["describe", "--preset", "cpu_usage", "-n", "100", "--seed", "7"])
        out2 = self._run(["describe", "--preset", "cpu_usage", "-n", "100", "--seed", "7"])
        self.assertEqual(out1, out2)


class TestVersion(unittest.TestCase):
    def test_version_flag(self):
        buf = StringIO()
        with mock.patch("sys.stdout", buf), self.assertRaises(SystemExit) as cm:
            main(["--version"])
        self.assertEqual(cm.exception.code, 0)
        self.assertIn("faketelemetry", buf.getvalue())


class TestNoCommand(unittest.TestCase):
    def test_no_args(self):
        """No subcommand should print help and exit 0."""
        buf = StringIO()
        with mock.patch("sys.stdout", buf), self.assertRaises(SystemExit) as cm:
            main([])
        # exits cleanly
        self.assertEqual(cm.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
