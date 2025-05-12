from enum import Enum

class WaveformType(Enum):
    """
    Enumeration of supported waveform types for telemetry generation.
    """
    SINE = 'sine'
    COSINE = 'cosine'
    SQUARE = 'square'
    SAWTOOTH = 'sawtooth'
    TRIANGLE = 'triangle'
    PULSE = 'pulse'
    RANDOM_NOISE = 'random_noise'
    CUSTOM = 'custom'
