<p align="center">
  <img src="assets/logo.png" alt="FakeTelemetry" width="600">
</p>

<p align="center">
  <strong>Realistic fake telemetry streams for testing, simulation & IoT development.</strong><br>
  Zero dependencies. Pure Python 3.7+.
</p>

<p align="center">
  <a href="https://pypi.org/project/faketelemetry/"><img src="https://img.shields.io/pypi/v/faketelemetry.svg?style=flat-square&color=blue" alt="PyPI"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/license-MIT-green.svg?style=flat-square" alt="License"></a>
  <a href="https://github.com/adkvi/faketelemetry/actions"><img src="https://img.shields.io/github/actions/workflow/status/adkvi/faketelemetry/python-package.yml?style=flat-square&label=CI" alt="CI"></a>
  <a href="https://pypi.org/project/faketelemetry/"><img src="https://img.shields.io/pypi/pyversions/faketelemetry.svg?style=flat-square" alt="Python"></a>
</p>

<p align="center">
  <a href="https://pypi.org/project/faketelemetry/">PyPI</a> &bull;
  <a href="https://github.com/adkvi/faketelemetry">GitHub</a> &bull;
  <a href="#quickstart">Quickstart</a> &bull;
  <a href="#cli">CLI</a> &bull;
  <a href="#features">Features</a> &bull;
  <a href="#api-reference">API Reference</a>
</p>

---

## Quickstart

```sh
pip install faketelemetry
```

```python
from faketelemetry import TelemetryGenerator, WaveformType

gen = TelemetryGenerator(WaveformType.SINE, frequency=1.0, amplitude=5.0)

# Real-time stream (blocking, with sleep)
for ts, val in gen.stream(sampling_rate=10, duration=2):
    print(ts, round(val, 2))

# Instant batch (no sleeping -- great for tests & pipelines)
points = gen.batch(num_samples=100, sampling_rate=50)
```

---

## Features

<table>
<tr><td width="200"><b>12 Waveforms</b></td>
<td>Sine, cosine, square, sawtooth, triangle, pulse, random noise, random walk, step, exponential decay, chirp, and custom user-defined functions</td></tr>
<tr><td><b>6 Noise Types</b></td>
<td>Gaussian, uniform, pink (1/f), Brownian, impulse spikes, and quantization noise</td></tr>
<tr><td><b>6 Anomaly Types</b></td>
<td>Spikes, dropouts, drift, flatline, stuck-at, and jitter -- all probabilistic with configurable duration</td></tr>
<tr><td><b>19 Sensor Presets</b></td>
<td>One-liner generators for temperature, pressure, humidity, battery voltage, RPM, CPU, latency, heart rate, accelerometer, GPS, light, CO2, wind, memory, disk I/O, flow rate, vibration, pH, and RSSI</td></tr>
<tr><td><b>Signal Composition</b></td>
<td>Combine generators with <code>+</code> <code>-</code> <code>*</code> operators -- build harmonics, AM signals, or complex waveforms from simple parts</td></tr>
<tr><td><b>Signal Control</b></td>
<td>Amplitude, frequency, offset, phase, duty cycle, exponential damping, and value clamping</td></tr>
<tr><td><b>Batch & Stream</b></td>
<td>Real-time <code>stream()</code>, instant <code>batch()</code>, and <code>async</code>-native <code>astream()</code></td></tr>
<tr><td><b>Multi-Channel</b></td>
<td>Synchronised named channels with dict or list input</td></tr>
<tr><td><b>Export</b></td>
<td>CSV, JSON, NDJSON -- plus InfluxDB line protocol, MQTT JSON, and Prometheus exposition format</td></tr>
<tr><td><b>Statistics</b></td>
<td>Built-in <code>describe()</code> for min, max, mean, std, percentiles on generated data</td></tr>
<tr><td><b>Reproducible</b></td>
<td>Seed support across generators, noise, and anomalies; <code>to_config()</code> / <code>from_config()</code> for saving and replaying setups</td></tr>
<tr><td><b>CLI</b></td>
<td>Full command-line interface -- generate data, stream, export, and inspect without writing Python</td></tr>
<tr><td><b>DataFrame-Ready</b></td>
<td><code>to_dict()</code> and <code>batch()</code> plug directly into <code>pandas.DataFrame()</code></td></tr>
</table>

---

## Installation

```sh
pip install faketelemetry
```

Or from source:

```sh
git clone https://github.com/adkvi/faketelemetry.git
cd faketelemetry
pip install -e .
```

> **Requirements:** Python 3.7+ &mdash; no external dependencies.

---

## CLI

After installing, the `faketelemetry` command is available in your terminal (or use `python -m faketelemetry`).

### Generate from a sensor preset

```sh
faketelemetry preset temperature -n 10 --rate 1
faketelemetry preset cpu_usage -n 100 --rate 10 -f csv -o cpu.csv
```

### Generate from a waveform

```sh
faketelemetry generate -w sine --freq 2 --amp 5 --offset 10 -n 50 --rate 10
faketelemetry generate -w square --duty-cycle 0.3 -n 20 -f json
```

### Multi-channel output

```sh
faketelemetry multi temperature,pressure,cpu_usage -n 100 --rate 10 -f csv
```

### Real-time streaming to stdout

```sh
faketelemetry stream --preset heart_rate --rate 2 --duration 30
faketelemetry stream -w sine --rate 10       # Ctrl+C to stop
```

### Generate from a saved config

```sh
faketelemetry from-config config.json -n 500 -f ndjson -o data.ndjson
```

### List available presets, waveforms, noise types

```sh
faketelemetry list presets
faketelemetry list waveforms
faketelemetry list noise
faketelemetry list anomalies
```

### Summary statistics

```sh
faketelemetry describe --preset temperature -n 1000 --rate 10
faketelemetry describe -w sine -n 5000 --rate 100
```

### Output formats

All batch commands support `--format` / `-f` with: `table` (default), `csv`, `json`, `ndjson`, `influxdb`.

### Other flags

| Flag | Description |
|---|---|
| `-n` / `--samples` | Number of data points |
| `--rate` | Sampling rate in Hz |
| `-f` / `--format` | Output format |
| `-o` / `--output` | Write to file instead of stdout |
| `--seed` | Random seed for reproducibility |
| `--noise-level` | Add Gaussian noise |
| `--no-header` | Omit header row in table/csv |
| `--version` | Print version and exit |

---

## Python API Examples

### Noise Injection

Six noise distributions, all with optional seed for reproducibility.

```python
from faketelemetry import TelemetryGenerator, WaveformType, NoiseInjector, NoiseType

# Gaussian noise
gen = TelemetryGenerator(
    WaveformType.SINE,
    noise_injector=NoiseInjector(noise_level=0.5, noise_type=NoiseType.GAUSSIAN, seed=42),
)

# Brownian (random-walk) noise
gen = TelemetryGenerator(
    WaveformType.SINE,
    noise_injector=NoiseInjector(noise_level=0.1, noise_type=NoiseType.BROWNIAN),
)

# Quantization noise (simulates low-resolution ADC)
gen = TelemetryGenerator(
    WaveformType.SINE,
    amplitude=5.0,
    noise_injector=NoiseInjector(noise_type=NoiseType.QUANTIZATION, quantization_step=0.25),
)
```

### Anomaly / Fault Injection

Stack multiple anomaly behaviours -- each fires independently per sample.

```python
from faketelemetry import (
    TelemetryGenerator, WaveformType,
    AnomalyInjector, AnomalyConfig, AnomalyType,
)

gen = TelemetryGenerator(
    WaveformType.SINE,
    frequency=1.0,
    amplitude=5.0,
    anomaly_injector=AnomalyInjector(
        configs=[
            AnomalyConfig(AnomalyType.SPIKE, probability=0.05, magnitude=20.0),
            AnomalyConfig(AnomalyType.DRIFT, probability=1.0, drift_rate=0.01),
            AnomalyConfig(AnomalyType.DROPOUT, probability=0.02, duration_samples=5),
        ],
        seed=42,
    ),
)

values = gen.batch_values(num_samples=500, sampling_rate=100)
```

### Sensor Presets

19 realistic sensor simulators, each returns a ready-to-use `TelemetryGenerator`.

```python
from faketelemetry.presets import SensorPreset

temp    = SensorPreset.temperature(seed=1)        # ~22 C +/- 3 C
press   = SensorPreset.pressure(seed=1)            # ~1013 hPa
humid   = SensorPreset.humidity(seed=1)            # 0-100 %
battery = SensorPreset.battery_voltage(seed=1)     # 4.2 V decaying
rpm     = SensorPreset.rpm(seed=1)                 # ~800 RPM idle
cpu     = SensorPreset.cpu_usage(seed=1)           # 0-100 %
latency = SensorPreset.network_latency(seed=1)     # ~25 ms
hr      = SensorPreset.heart_rate(seed=1)          # ~72 BPM
accel   = SensorPreset.accelerometer(seed=1)       # +/- 1 g
gps     = SensorPreset.gps_coordinate(seed=1)      # wandering lat/lon
light   = SensorPreset.light_lux(seed=1)           # ~400 lux
co2     = SensorPreset.co2_ppm(seed=1)             # ~420 ppm
wind    = SensorPreset.wind_speed(seed=1)           # ~12 m/s
mem     = SensorPreset.memory_usage(seed=1)         # 0-100 %
disk    = SensorPreset.disk_io(seed=1)              # MB/s bursts
flow    = SensorPreset.flow_rate(seed=1)            # ~50 l/min
vib     = SensorPreset.vibration(seed=1)            # mm/s
ph      = SensorPreset.ph_level(seed=1)             # 0-14
rssi    = SensorPreset.signal_strength(seed=1)      # -120..0 dBm

data = temp.batch(num_samples=1000, sampling_rate=10)
```

### Phase, Duty Cycle, Damping & Clamping

Fine-tune signal shape and bounds.

```python
import math
from faketelemetry import TelemetryGenerator, WaveformType

gen = TelemetryGenerator(
    WaveformType.SINE,
    frequency=2.0,
    amplitude=10.0,
    phase=math.pi / 4,   # 45-degree phase shift
    damping=0.3,          # exponential decay envelope
    clamp_min=-5.0,       # hard floor
    clamp_max=5.0,        # hard ceiling
)

values = gen.batch_values(200, sampling_rate=100)
```

### Multi-Channel with Named Channels

Synchronise multiple signals on the same time base.

```python
from faketelemetry import TelemetryGenerator, WaveformType, MultiChannelTelemetryGenerator

multi = MultiChannelTelemetryGenerator({
    "temperature": TelemetryGenerator(WaveformType.SINE, frequency=0.1, offset=22.0, name="temp"),
    "pressure":    TelemetryGenerator(WaveformType.COSINE, frequency=0.05, offset=1013.0, name="press"),
})

# Batch -> list of dicts (pandas-ready)
import pandas as pd
df = pd.DataFrame(multi.batch(num_samples=1000, sampling_rate=10))
print(df.head())

# Or raw arrays for plotting
arrays = multi.batch_arrays(num_samples=500, sampling_rate=50)
```

### Data Export

Write to file or get back a string -- CSV, JSON, or NDJSON.

```python
from faketelemetry import TelemetryGenerator, WaveformType, to_csv, to_json, to_ndjson

gen = TelemetryGenerator(WaveformType.SINE, name="sensor_a")
data = gen.batch(num_samples=500, sampling_rate=100)

# To file
to_csv(data, "output.csv")
to_json(data, "output.json")
to_ndjson(data, "output.ndjson")

# To string
csv_string  = to_csv(data)
json_string = to_json(data)
```

### Signal Composition

Combine generators with `+`, `-`, `*` to build complex signals.

```python
from faketelemetry import TelemetryGenerator, WaveformType, compose

# Sum of harmonics (approximate square wave via Fourier series)
fundamental = TelemetryGenerator(WaveformType.SINE, frequency=1.0, amplitude=1.0)
harmonic3   = TelemetryGenerator(WaveformType.SINE, frequency=3.0, amplitude=1/3)
harmonic5   = TelemetryGenerator(WaveformType.SINE, frequency=5.0, amplitude=1/5)
approx_square = fundamental + harmonic3 + harmonic5

# Amplitude modulation
carrier  = TelemetryGenerator(WaveformType.SINE, frequency=100.0)
envelope = TelemetryGenerator(WaveformType.SINE, frequency=1.0, amplitude=0.5, offset=0.5)
am_signal = carrier * envelope

# Scalar offset
biased = TelemetryGenerator(WaveformType.SINE) + 10.0

# compose() for many generators
signal = compose(fundamental, harmonic3, harmonic5)  # same as +
values = signal.batch_values(500, sampling_rate=200)
```

### Async Streaming

Native `async for` support for asyncio applications.

```python
import asyncio
from faketelemetry import TelemetryGenerator, WaveformType

async def main():
    gen = TelemetryGenerator(WaveformType.SINE, frequency=1.0, amplitude=5.0)
    async for ts, val in gen.astream(sampling_rate=10, duration=3):
        print(f"{ts}: {val:.2f}")

asyncio.run(main())
```

### Protocol Formatters

Output data in InfluxDB, MQTT, or Prometheus format -- ready for ingestion.

```python
from faketelemetry import TelemetryGenerator, WaveformType
from faketelemetry.formatters import to_influxdb, to_mqtt_json, to_prometheus

gen = TelemetryGenerator(WaveformType.SINE, name="temp")
data = gen.batch(10, sampling_rate=1)

# InfluxDB line protocol
for line in to_influxdb(data, measurement="sensors", tags={"room": "lab"}):
    print(line)
# sensors,room=lab value=0.123 1706745600000000000

# MQTT JSON payloads
for payload in to_mqtt_json(data, sensor_id="temp-01"):
    print(payload)
# {"timestamp": "...", "value": 0.123, "sensor_id": "temp-01"}

# Prometheus exposition format
print(to_prometheus(data, metric_name="room_temp", labels={"room": "lab"}))
```

### Statistics

Built-in summary stats -- no pandas required.

```python
from faketelemetry import TelemetryGenerator, WaveformType, describe, describe_values

gen = TelemetryGenerator(WaveformType.SINE, amplitude=5.0)
data = gen.batch(1000, sampling_rate=100)

stats = describe(data)
print(stats)
# {'count': 1000, 'mean': 0.01, 'std': 3.54, 'min': -5.0, 'max': 5.0,
#  'range': 10.0, 'p25': ..., 'p50': ..., 'p75': ..., ...}

# Or from raw values
stats = describe_values(gen.batch_values(1000, sampling_rate=100))
```

### Config Serialization

Save and replay generator setups as JSON.

```python
import json
from faketelemetry import TelemetryGenerator, WaveformType, NoiseInjector

gen = TelemetryGenerator(
    WaveformType.SINE, frequency=2.0, amplitude=5.0,
    noise_injector=NoiseInjector(noise_level=0.3), name="sensor_x",
)

# Save config
config = gen.to_config()
json.dump(config, open("config.json", "w"))

# Reload later
gen2 = TelemetryGenerator.from_config(json.load(open("config.json")))
```

### Reproducible Output

Same seed = identical data every run.

```python
from faketelemetry import TelemetryGenerator, WaveformType, NoiseInjector

gen = TelemetryGenerator(
    WaveformType.SINE,
    noise_injector=NoiseInjector(noise_level=0.5, seed=42),
    seed=42,
)

run1 = gen.batch_values(100, sampling_rate=50)
gen.reset()
run2 = gen.batch_values(100, sampling_rate=50)
# run1 == run2
```

### DataFrame Integration

```python
import pandas as pd
from faketelemetry import TelemetryGenerator, WaveformType

gen = TelemetryGenerator(WaveformType.SINE, frequency=1.0, name="vibration")

df = pd.DataFrame(gen.to_dict(num_samples=1000, sampling_rate=100))
print(df.describe())
```

---

## API Reference

### Core Classes

| Class | Description |
|---|---|
| `TelemetryGenerator` | Single-channel generator with `stream()`, `astream()`, `batch()`, `to_config()`, and `+` `-` `*` operators |
| `CompositeGenerator` | Compound signal from combining generators with arithmetic operators |
| `MultiChannelTelemetryGenerator` | Synchronised multi-channel generator with `stream()`, `astream()`, and `batch()` |
| `NoiseInjector` | 6 noise types: Gaussian, uniform, pink, Brownian, impulse, quantization |
| `AnomalyInjector` | Fault injection engine processing one or more `AnomalyConfig` rules |
| `AnomalyConfig` | Configuration for a single anomaly behaviour |
| `SensorPreset` | Factory with 19 ready-made realistic sensor generators |

### Enums

| Enum | Values |
|---|---|
| `WaveformType` | `SINE` `COSINE` `SQUARE` `SAWTOOTH` `TRIANGLE` `PULSE` `RANDOM_NOISE` `RANDOM_WALK` `STEP` `EXPONENTIAL_DECAY` `CHIRP` `CUSTOM` |
| `NoiseType` | `GAUSSIAN` `UNIFORM` `PINK` `BROWNIAN` `IMPULSE` `QUANTIZATION` |
| `AnomalyType` | `SPIKE` `DROPOUT` `DRIFT` `FLATLINE` `JITTER` `STUCK_AT` |

### Export & Formatting

| Function | Description |
|---|---|
| `to_csv(data, path)` | Single-channel to CSV (file or string) |
| `to_json(data, path)` | Single-channel to JSON array (file or string) |
| `to_ndjson(data, path)` | Single-channel to newline-delimited JSON |
| `to_multichannel_csv(rows, path)` | Multi-channel batch output to CSV |
| `to_influxdb(data, ...)` | InfluxDB line protocol |
| `to_influxdb_multi(rows, ...)` | Multi-channel InfluxDB line protocol |
| `to_mqtt_json(data, ...)` | MQTT JSON payloads |
| `to_prometheus(data, ...)` | Prometheus exposition format |

### Statistics

| Function | Description |
|---|---|
| `describe(data)` | Summary stats (count, mean, std, min, max, percentiles) for single-channel batch |
| `describe_values(values)` | Same, from a raw list of floats |
| `describe_multi(rows)` | Per-channel stats for multi-channel batch |

---

## Testing

```sh
python -m pytest tests/ -v
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support

For questions or issues, please open a [GitHub Issue](https://github.com/adkvi/faketelemetry/issues).

## License

MIT -- see [LICENSE](LICENSE) for details.
