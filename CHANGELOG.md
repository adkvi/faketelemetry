# Changelog

All notable changes to this project will be documented in this file.

## [0.4.0] - 2026-02-08
### Added
- **Command-line interface**: full CLI via `faketelemetry` command or `python -m faketelemetry`
  - `generate` -- generate data from any waveform with full parameter control
  - `preset` -- generate from any of the 19 sensor presets
  - `multi` -- multi-channel generation from comma-separated presets
  - `stream` -- real-time streaming to stdout (Ctrl+C to stop)
  - `from-config` -- generate from a saved JSON config file
  - `list` -- enumerate available presets, waveforms, noise types, anomaly types
  - `describe` -- generate data and print summary statistics
- Output formats: `table` (human-readable), `csv`, `json`, `ndjson`, `influxdb`
- File output via `-o` flag, reproducibility via `--seed`, noise via `--noise-level`
- Console entry point registered in `pyproject.toml` (`[project.scripts]`)

## [0.3.0] - 2026-02-08
### Added
- **Signal composition**: `CompositeGenerator` with `+`, `-`, `*` operator overloading on `TelemetryGenerator` -- build complex signals from simple parts (harmonics, AM, offsets)
- **`compose()` helper**: combine an arbitrary number of generators in one call
- **Async streaming**: `astream()` method on `TelemetryGenerator` and `MultiChannelTelemetryGenerator` for `async for` loops
- **Protocol formatters**: `to_influxdb()`, `to_influxdb_multi()`, `to_mqtt_json()`, `to_mqtt_json_multi()`, `to_prometheus()` for direct telemetry pipeline integration
- **Statistics**: `describe()`, `describe_values()`, `describe_multi()` -- min, max, mean, std, percentiles with zero dependencies
- **Config serialization**: `to_config()` / `from_config()` on `TelemetryGenerator` -- save and reload generator setups as JSON
- **9 new sensor presets**: light (lux), CO2 (ppm), wind speed, memory usage, disk I/O, flow rate, vibration, pH, and signal strength (RSSI) -- total now 19
- Test suite expanded: 100+ tests across all features

### Changed
- Migrated all packaging to `pyproject.toml` (removed `setup.py` and `requirements-dev.txt`)
- CI workflow: split into test + publish jobs, Python version matrix (3.9, 3.11, 3.13), uses pytest
- Added `tests/__init__.py` and `faketelemetry/py.typed` (PEP 561)
- Improved `.gitignore` and `CONTRIBUTING.md`

## [0.2.0] - 2026-02-08
### Added
- **New waveforms**: `RANDOM_WALK`, `STEP`, `EXPONENTIAL_DECAY`, `CHIRP`
- **NoiseInjector**: 6 noise types -- Gaussian, uniform, pink (1/f), Brownian, impulse, and quantization noise; seed support for reproducibility
- **AnomalyInjector** & **AnomalyConfig**: probabilistic fault injection with spike, dropout, drift, flatline, stuck-at, and jitter anomalies
- **SensorPreset**: one-liner factory for realistic sensors -- temperature, pressure, humidity, battery voltage, RPM, CPU usage, network latency, heart rate, accelerometer, GPS coordinate
- **Batch generation**: `batch()`, `batch_values()`, and `to_dict()` methods for instant (non-real-time) data generation
- **Signal control**: phase offset, duty cycle (square/pulse), exponential damping, and value clamping (`clamp_min` / `clamp_max`)
- **Named channels**: `MultiChannelTelemetryGenerator` accepts dict input for named channels with `channel_names` property and `[]` access
- **Multi-channel batch**: `batch()` returns pandas-ready row dicts; `batch_arrays()` returns raw value arrays
- **Data export**: `to_csv()`, `to_json()`, `to_ndjson()`, `to_multichannel_csv()` -- write to file or return as string
- **Seed support**: deterministic output via `seed` parameter on generators, noise, and anomalies
- **`reset()` method**: reset internal state (random walk, noise, anomalies) on all classes
- **`__repr__`** for `TelemetryGenerator` and `MultiChannelTelemetryGenerator`
- Comprehensive test suite: 60+ tests across generators, noise, anomalies, presets, and exporters

### Changed
- `NoiseInjector` now accepts `noise_type` enum parameter (default `GAUSSIAN` -- fully backward compatible)
- `MultiChannelTelemetryGenerator` now accepts both list and dict of generators
- `TelemetryGenerator` constructor has new optional parameters (all backward compatible)
- Updated examples to demonstrate new features

## [0.1.2] - 2025-05-12
### Changed
- Enhanced README: added Quickstart, Requirements, Table of Contents, Contributing, and Support sections for improved user experience.
- Updated author email to real address in setup.py.

## [0.1.1] - 2025-05-12
### Changed
- Updated README with direct PyPI and GitHub links, clarified installation instructions, and improved documentation badges.

## [0.1.0] - 2025-05-12
### Added
- Initial release: sine, cosine, square, sawtooth, triangle, pulse, random noise, and custom waveforms
- Multi-channel telemetry support
- Noise injection
- Input validation and error handling
- Full test suite
- PyPI-ready packaging and documentation
