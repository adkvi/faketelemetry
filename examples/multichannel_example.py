from faketelemetry import TelemetryGenerator, WaveformType, MultiChannelTelemetryGenerator

if __name__ == "__main__":
    import time
    # Multi-channel example: Sine and Cosine
    gen1 = TelemetryGenerator(waveform=WaveformType.SINE, frequency=1.0, amplitude=1.0, offset=0.0)
    gen2 = TelemetryGenerator(waveform=WaveformType.COSINE, frequency=0.5, amplitude=2.0, offset=1.0)
    multi = MultiChannelTelemetryGenerator([gen1, gen2])
    print("Multi-channel telemetry stream (2 channels):")
    for sample in multi.stream(sampling_rate=2.0, duration=5):
        for idx, (timestamp, value) in sample.items():
            print(f"Channel {idx}: {timestamp} -> {value:.3f}")
        print("---")
        time.sleep(0.1)
