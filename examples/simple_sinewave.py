"""
Simple examples demonstrating the core faketelemetry API.
"""
from faketelemetry import (
    TelemetryGenerator,
    WaveformType,
    NoiseInjector,
    NoiseType,
    AnomalyInjector,
    AnomalyConfig,
    AnomalyType,
)

if __name__ == "__main__":
    # ---------------------------------------------------------------
    # 1) Basic sine wave (real-time stream)
    # ---------------------------------------------------------------
    print("=== Basic sine wave (3 seconds) ===")
    gen = TelemetryGenerator(
        waveform=WaveformType.SINE,
        frequency=1.0,
        amplitude=1.0,
        offset=0.0,
        noise_injector=NoiseInjector(noise_level=0.2),
    )
    for timestamp, value in gen.stream(sampling_rate=2.0, duration=3):
        print(f"  {timestamp}: {value:.3f}")

    # ---------------------------------------------------------------
    # 2) Batch generation (instant, no sleep)
    # ---------------------------------------------------------------
    print("\n=== Batch generation (10 points) ===")
    gen = TelemetryGenerator(WaveformType.COSINE, frequency=2.0, amplitude=5.0)
    for ts, val in gen.batch(num_samples=10, sampling_rate=10):
        print(f"  {ts} -> {val:.3f}")

    # ---------------------------------------------------------------
    # 3) Noise types
    # ---------------------------------------------------------------
    print("\n=== Brownian noise on a flat signal ===")
    gen = TelemetryGenerator(
        WaveformType.SINE,
        frequency=0.0,
        amplitude=0.0,
        offset=50.0,
        noise_injector=NoiseInjector(0.5, NoiseType.BROWNIAN, seed=42),
    )
    vals = gen.batch_values(20, sampling_rate=10)
    print("  Values:", [f"{v:.2f}" for v in vals])

    # ---------------------------------------------------------------
    # 4) Anomaly injection (spike + drift)
    # ---------------------------------------------------------------
    print("\n=== Sine wave with spike + drift anomalies ===")
    gen = TelemetryGenerator(
        WaveformType.SINE,
        frequency=1.0,
        amplitude=5.0,
        anomaly_injector=AnomalyInjector(
            configs=[
                AnomalyConfig(AnomalyType.SPIKE, probability=0.1, magnitude=20.0),
                AnomalyConfig(AnomalyType.DRIFT, probability=1.0, drift_rate=0.1),
            ],
            seed=7,
        ),
    )
    vals = gen.batch_values(30, sampling_rate=10)
    print("  Values:", [f"{v:.2f}" for v in vals])

    # ---------------------------------------------------------------
    # 5) Phase offset + damping + clamping
    # ---------------------------------------------------------------
    import math

    print("\n=== Damped sine with clamping ===")
    gen = TelemetryGenerator(
        WaveformType.SINE,
        frequency=2.0,
        amplitude=10.0,
        phase=math.pi / 4,
        damping=0.5,
        clamp_min=-5.0,
        clamp_max=5.0,
    )
    vals = gen.batch_values(20, sampling_rate=10)
    print("  Values:", [f"{v:.2f}" for v in vals])
