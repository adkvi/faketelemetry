# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2025-01-27
### Added
- **Phase shift parameter**: New `phase` parameter for waveform generators to control signal phase offset
- **Batch generation**: New `generate_batch()` method for generating data without real-time delays
- **Exponential decay waveform**: New `WaveformType.EXPONENTIAL_DECAY` for decay curves
- **Multiple noise types**: New `NoiseType` enum with Gaussian, uniform, and impulse noise support
- **Data export utilities**: New `to_json()`, `to_csv()`, `from_json()`, `from_csv()` functions
- **Improved type hints**: Enhanced type annotations throughout the codebase
- **Comprehensive docstrings**: Added detailed documentation to all classes and methods
- **Modern pyproject.toml**: Migrated to modern Python packaging with full metadata

### Changed
- Bumped version to 0.2.0
- Enhanced README with extensive documentation and examples
- Added 21 new tests (total: 35 tests)
- `NoiseInjector` now validates `noise_level` parameter

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
