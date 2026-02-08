from enum import Enum


class WaveformType(Enum):
    """
    Enumeration of supported waveform types for telemetry generation.
    """

    SINE = "sine"
    COSINE = "cosine"
    SQUARE = "square"
    SAWTOOTH = "sawtooth"
    TRIANGLE = "triangle"
    PULSE = "pulse"
    RANDOM_NOISE = "random_noise"
    RANDOM_WALK = "random_walk"
    STEP = "step"
    EXPONENTIAL_DECAY = "exponential_decay"
    CHIRP = "chirp"
    CUSTOM = "custom"


class NoiseType(Enum):
    """
    Enumeration of noise distribution types.
    """

    GAUSSIAN = "gaussian"
    UNIFORM = "uniform"
    PINK = "pink"
    BROWNIAN = "brownian"
    IMPULSE = "impulse"
    QUANTIZATION = "quantization"


class AnomalyType(Enum):
    """
    Enumeration of anomaly / fault-injection types.
    """

    SPIKE = "spike"
    DROPOUT = "dropout"
    DRIFT = "drift"
    FLATLINE = "flatline"
    JITTER = "jitter"
    STUCK_AT = "stuck_at"
