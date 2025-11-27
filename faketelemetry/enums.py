from enum import Enum


class WaveformType(Enum):
    """
    Enumeration of supported waveform types for telemetry generation.

    Available waveforms:
        - SINE: Sinusoidal wave
        - COSINE: Cosine wave
        - SQUARE: Square wave (alternates between +amplitude and -amplitude)
        - SAWTOOTH: Sawtooth wave (linear rise, instant drop)
        - TRIANGLE: Triangle wave (linear rise and fall)
        - PULSE: Pulse wave (brief high, then low)
        - EXPONENTIAL_DECAY: Exponential decay (starts at amplitude, decays to offset)
        - RANDOM_NOISE: Gaussian random noise
        - CUSTOM: User-defined waveform function
    """

    SINE = "sine"
    COSINE = "cosine"
    SQUARE = "square"
    SAWTOOTH = "sawtooth"
    TRIANGLE = "triangle"
    PULSE = "pulse"
    EXPONENTIAL_DECAY = "exponential_decay"
    RANDOM_NOISE = "random_noise"
    CUSTOM = "custom"
