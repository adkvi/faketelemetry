"""
Multi-channel and sensor preset examples.
"""
from faketelemetry import (
    TelemetryGenerator,
    WaveformType,
    MultiChannelTelemetryGenerator,
    NoiseInjector,
    NoiseType,
    to_csv,
    to_json,
    to_multichannel_csv,
)
from faketelemetry.presets import SensorPreset

if __name__ == "__main__":
    # ---------------------------------------------------------------
    # 1) Named multi-channel (dict-based)
    # ---------------------------------------------------------------
    print("=== Named multi-channel (batch) ===")
    multi = MultiChannelTelemetryGenerator({
        "temperature": TelemetryGenerator(
            WaveformType.SINE, frequency=0.1, amplitude=3.0, offset=22.0,
            noise_injector=NoiseInjector(0.3), name="temperature",
        ),
        "pressure": TelemetryGenerator(
            WaveformType.COSINE, frequency=0.05, amplitude=5.0, offset=1013.0,
            noise_injector=NoiseInjector(0.5), name="pressure",
        ),
    })

    rows = multi.batch(num_samples=5, sampling_rate=2)
    for row in rows:
        print(f"  {row}")

    # ---------------------------------------------------------------
    # 2) Sensor presets
    # ---------------------------------------------------------------
    print("\n=== Sensor presets (batch) ===")
    temp = SensorPreset.temperature(seed=42)
    cpu = SensorPreset.cpu_usage(seed=42)
    hr = SensorPreset.heart_rate(seed=42)

    multi_preset = MultiChannelTelemetryGenerator({
        "temperature_C": temp,
        "cpu_pct": cpu,
        "heart_bpm": hr,
    })

    rows = multi_preset.batch(num_samples=5, sampling_rate=1)
    for row in rows:
        print(f"  {row}")

    # ---------------------------------------------------------------
    # 3) Export to CSV string
    # ---------------------------------------------------------------
    print("\n=== Export single-channel CSV ===")
    gen = SensorPreset.temperature(seed=1)
    data = gen.batch(num_samples=5, sampling_rate=1)
    csv_str = to_csv(data)
    print(csv_str)

    # ---------------------------------------------------------------
    # 4) Export multi-channel CSV
    # ---------------------------------------------------------------
    print("=== Export multi-channel CSV ===")
    multi_rows = multi_preset.batch(num_samples=5, sampling_rate=1)
    csv_str = to_multichannel_csv(multi_rows)
    print(csv_str)

    # ---------------------------------------------------------------
    # 5) Export to JSON string
    # ---------------------------------------------------------------
    print("=== Export single-channel JSON ===")
    json_str = to_json(data)
    print(json_str[:300], "...")

    # ---------------------------------------------------------------
    # 6) Real-time multi-channel stream
    # ---------------------------------------------------------------
    print("\n=== Real-time multi-channel (2 sec) ===")
    for sample in multi.stream(sampling_rate=2.0, duration=2):
        parts = {k: f"{v[1]:.2f}" for k, v in sample.items()}
        print(f"  {sample['temperature'][0]} | {parts}")
