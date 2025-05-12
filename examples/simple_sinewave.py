from faketelemetry import TelemetryGenerator, WaveformType, NoiseInjector, MultiChannelTelemetryGenerator

if __name__ == "__main__":
    import time
    # Single channel with noise
    gen = TelemetryGenerator(
        waveform=WaveformType.SINE,
        frequency=1.0,
        amplitude=1.0,
        offset=0.0,
        noise_injector=NoiseInjector(noise_level=0.2)
    )
    print("Single channel with noise:")
    for timestamp, value in gen.stream(sampling_rate=2.0, duration=3):
        print(f"{timestamp}: {value:.3f}")
        time.sleep(0.1)

    # Multi-channel example
    print("\nMulti-channel example:")
    gen1 = TelemetryGenerator(WaveformType.SINE, frequency=1.0)
    gen2 = TelemetryGenerator(WaveformType.COSINE, frequency=0.5)
    multi = MultiChannelTelemetryGenerator([gen1, gen2])
    for sample in multi.stream(sampling_rate=2.0, duration=3):
        print({k: f"{v[0]}: {v[1]:.3f}" for k, v in sample.items()})
        time.sleep(0.1)
