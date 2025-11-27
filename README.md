[![PyPI version](https://img.shields.io/pypi/v/faketelemetry.svg)](https://pypi.org/project/faketelemetry/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/adkvi/faketelemetry/actions/workflows/python-package.yml/badge.svg)](https://github.com/adkvi/faketelemetry/actions)

# FakeTelemetry

**A Python package to generate real-time and batch fake telemetry streams for testing, simulation, and development.**

## Links
- 📦 [PyPI Project](https://pypi.org/project/faketelemetry/)
- 🗂️ [GitHub Repository](https://github.com/adkvi/faketelemetry)

## Features
- **Multiple waveforms**: sine, cosine, square, sawtooth, triangle, pulse, exponential decay, and random noise
- **Custom waveforms**: Define your own signal functions
- **Phase shift support**: Control phase offset for waveforms
- **Adjustable parameters**: amplitude, frequency, offset, and sample rate
- **Multiple noise types**: Gaussian, uniform, and impulse noise injection
- **Real-time streaming**: Generate (datetime, value) tuples with actual timing delays
- **Batch generation**: Generate all samples at once without delays
- **Multi-channel support**: Parallel telemetry generation across multiple channels
- **Data export**: Export to JSON, CSV formats with import support
- **Well-tested**: Comprehensive test suite with 35+ tests
- **Pure Python**: No external dependencies required

## Quickstart

Generate a sine wave stream in seconds:

```python
from faketelemetry import TelemetryGenerator, WaveformType

gen = TelemetryGenerator(WaveformType.SINE)
for ts, val in gen.stream(sampling_rate=1.0, duration=2):
    print(ts, val)
```

## Requirements
- Python 3.7 or newer
- No external dependencies (pure Python)

## Example Usage

### Basic Waveform Generation

```python
from faketelemetry import TelemetryGenerator, WaveformType, NoiseInjector

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
```

### Phase Shift

```python
import math
from faketelemetry import TelemetryGenerator, WaveformType

# Sine wave with 90 degree phase shift (equivalent to cosine)
gen = TelemetryGenerator(
    WaveformType.SINE, 
    frequency=1.0, 
    phase=math.pi/2
)
```

### Batch Generation (No Delays)

```python
from faketelemetry import TelemetryGenerator, WaveformType

gen = TelemetryGenerator(WaveformType.SINE, frequency=1.0)

# Generate 100 samples at 10 Hz over 10 seconds - returns immediately
data = gen.generate_batch(sampling_rate=10.0, duration=10.0)
for timestamp, value in data:
    print(timestamp, value)
```

### Multi-Channel Telemetry

```python
from faketelemetry import TelemetryGenerator, WaveformType, MultiChannelTelemetryGenerator

ch1 = TelemetryGenerator(WaveformType.SINE, frequency=1.0)
ch2 = TelemetryGenerator(WaveformType.COSINE, frequency=0.5)
multi = MultiChannelTelemetryGenerator([ch1, ch2])

# Real-time streaming
for sample in multi.stream(sampling_rate=2.0, duration=3):
    print({k: (v[0], v[1]) for k, v in sample.items()})

# Or batch generation
batch_data = multi.generate_batch(sampling_rate=10.0, duration=5.0)
```

### Different Noise Types

```python
from faketelemetry import NoiseInjector, NoiseType, TelemetryGenerator, WaveformType

# Gaussian noise (default)
gaussian_noise = NoiseInjector(noise_level=0.1, noise_type=NoiseType.GAUSSIAN)

# Uniform noise
uniform_noise = NoiseInjector(noise_level=0.2, noise_type=NoiseType.UNIFORM)

# Impulse noise (random spikes)
impulse_noise = NoiseInjector(
    noise_level=1.0, 
    noise_type=NoiseType.IMPULSE, 
    impulse_probability=0.05
)

gen = TelemetryGenerator(WaveformType.SINE, noise_injector=impulse_noise)
```

### Exponential Decay

```python
from faketelemetry import TelemetryGenerator, WaveformType

# Exponential decay - frequency parameter controls decay rate
gen = TelemetryGenerator(
    WaveformType.EXPONENTIAL_DECAY, 
    frequency=0.5,  # decay rate
    amplitude=10.0,  # starting value
    offset=1.0  # asymptotic value
)
```

### Data Export

```python
from faketelemetry import TelemetryGenerator, WaveformType, to_json, to_csv, from_json

gen = TelemetryGenerator(WaveformType.SINE)
data = gen.generate_batch(sampling_rate=10.0, duration=5.0)

# Export to JSON
json_str = to_json(data)
to_json(data, "telemetry.json")  # Save to file

# Export to CSV
csv_str = to_csv(data)
to_csv(data, "telemetry.csv")  # Save to file

# Import back
restored_data = from_json("telemetry.json")
```

### Custom Waveform

```python
from faketelemetry import TelemetryGenerator, WaveformType

def custom_func(t):
    return 42.0  # Constant value

gen_custom = TelemetryGenerator(WaveformType.CUSTOM, custom_func=custom_func)
print('Custom:', next(gen_custom.stream(1)))
```

## Available Waveforms

| Waveform | Description |
|----------|-------------|
| `SINE` | Sinusoidal wave |
| `COSINE` | Cosine wave |
| `SQUARE` | Square wave (+1/-1) |
| `SAWTOOTH` | Linear rise, instant drop |
| `TRIANGLE` | Linear rise and fall |
| `PULSE` | Brief high, then low |
| `EXPONENTIAL_DECAY` | Exponential decay curve |
| `RANDOM_NOISE` | Gaussian random values |
| `CUSTOM` | User-defined function |

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

Or with pytest:

```sh
pytest tests/
```

## Support

For questions or issues, please open a [GitHub Issue](https://github.com/adkvi/faketelemetry/issues).

## License
MIT
