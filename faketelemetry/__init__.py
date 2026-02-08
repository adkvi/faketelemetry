"""
FakeTelemetry -- realistic fake telemetry stream generation for testing,
simulation, and development.
"""

from .telemetry_generator import TelemetryGenerator
from .multi_channel import MultiChannelTelemetryGenerator
from .noise_injector import NoiseInjector
from .anomaly_injector import AnomalyInjector, AnomalyConfig
from .compose import CompositeGenerator, compose
from .enums import WaveformType, NoiseType, AnomalyType
from .presets import SensorPreset
from .exporters import to_csv, to_json, to_ndjson, to_multichannel_csv
from .formatters import (
    to_influxdb,
    to_influxdb_multi,
    to_mqtt_json,
    to_mqtt_json_multi,
    to_prometheus,
)
from .stats import describe, describe_values, describe_multi

__version__ = "0.4.1"

__all__ = [
    # Core
    "TelemetryGenerator",
    "MultiChannelTelemetryGenerator",
    # Composition
    "CompositeGenerator",
    "compose",
    # Noise & anomalies
    "NoiseInjector",
    "AnomalyInjector",
    "AnomalyConfig",
    # Enums
    "WaveformType",
    "NoiseType",
    "AnomalyType",
    # Presets
    "SensorPreset",
    # Export helpers
    "to_csv",
    "to_json",
    "to_ndjson",
    "to_multichannel_csv",
    # Protocol formatters
    "to_influxdb",
    "to_influxdb_multi",
    "to_mqtt_json",
    "to_mqtt_json_multi",
    "to_prometheus",
    # Statistics
    "describe",
    "describe_values",
    "describe_multi",
]
