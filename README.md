[![PyPI version](https://img.shields.io/pypi/v/faketelemetry.svg)](https://pypi.org/project/faketelemetry/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/adkvi/faketelemetry/actions/workflows/python-package.yml/badge.svg)](https://github.com/adkvi/faketelemetry/actions)

# FakeTelemetry

**A minimal Python package to generate real-time, timestamped fake telemetry streams for testing, simulation, and development.**

## Links
- 📦 [PyPI Project](https://pypi.org/project/faketelemetry/)
- 🗂️ [GitHub Repository](https://github.com/adkvi/faketelemetry)

## Features
- Sine, cosine, square, sawtooth, triangle, pulse, and random noise waveforms
- Custom user-defined waveform support
- Adjustable amplitude, frequency, offset, and sample rate
- Optional Gaussian noise injection
- Real-time streaming of (datetime, value) tuples
- Multi-channel (parallel) telemetry generation
- Well-tested and extensible

## Example Usage

```python
from faketelemetry import TelemetryGenerator, WaveformType, NoiseInjector, MultiChannelTelemetryGenerator

# Single channel with noise (sine wave)
noise = NoiseInjector(noise_level=0.2)
gen = TelemetryGenerator(
    waveform=WaveformType.SINE,
    frequency=1.0,
    amplitude=1.0,
    offset=0.0,
    noise_injector=noise
)
for timestamp, value in gen.stream(sampling_rate=2.0, duration=3):
    print(timestamp, value)

# Multi-channel example (sine and cosine)
ch1 = TelemetryGenerator(WaveformType.SINE, frequency=1.0)
ch2 = TelemetryGenerator(WaveformType.COSINE, frequency=0.5)
multi = MultiChannelTelemetryGenerator([ch1, ch2])
for sample in multi.stream(sampling_rate=2.0, duration=3):
    print({k: (v[0], v[1]) for k, v in sample.items()})

# Triangle and pulse waveforms
tri = TelemetryGenerator(WaveformType.TRIANGLE, frequency=1.0)
pulse = TelemetryGenerator(WaveformType.PULSE, frequency=1.0)
print('Triangle:', next(tri.stream(1)))
print('Pulse:', next(pulse.stream(1)))

# Custom waveform (e.g., constant 42)
def custom_func(t):
    return 42.0
gen_custom = TelemetryGenerator(WaveformType.CUSTOM, custom_func=custom_func)
print('Custom:', next(gen_custom.stream(1)))
```

## Installation

Install from PyPI:

```sh
pip install faketelemetry
```

Or clone this repo and install locally:

```sh
pip install .
```

Or install in editable/development mode:

```sh
pip install -e .
```

## Testing

Run all tests:

```sh
python -m unittest discover -s tests
```

## License
MIT
