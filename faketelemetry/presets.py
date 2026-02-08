"""
Ready-made sensor presets that create pre-configured :class:`TelemetryGenerator`
instances with realistic parameters.

Example::

    from faketelemetry.presets import SensorPreset

    temp_gen = SensorPreset.temperature()
    for ts, val in temp_gen.stream(sampling_rate=1, duration=10):
        print(f"{ts}: {val:.1f} C")
"""

from typing import Optional

from .enums import WaveformType, NoiseType
from .noise_injector import NoiseInjector
from .telemetry_generator import TelemetryGenerator


class SensorPreset:
    """
    Factory class providing pre-configured generators that mimic common
    real-world sensors.  Every method returns a :class:`TelemetryGenerator`.
    """

    @staticmethod
    def temperature(
        base: float = 22.0,
        variation: float = 3.0,
        frequency: float = 0.005,
        noise_level: float = 0.3,
        seed: Optional[int] = None,
        name: str = "temperature_C",
    ) -> TelemetryGenerator:
        """
        Ambient temperature sensor (Celsius).

        Slow sinusoidal cycle (day/night) + Gaussian noise.
        Default range: ~19-25 C.
        """
        return TelemetryGenerator(
            waveform=WaveformType.SINE,
            frequency=frequency,
            amplitude=variation,
            offset=base,
            noise_injector=NoiseInjector(noise_level, NoiseType.GAUSSIAN, seed=seed),
            name=name,
            seed=seed,
        )

    @staticmethod
    def pressure(
        base: float = 1013.25,
        variation: float = 5.0,
        frequency: float = 0.002,
        noise_level: float = 0.5,
        seed: Optional[int] = None,
        name: str = "pressure_hPa",
    ) -> TelemetryGenerator:
        """
        Barometric pressure sensor (hPa / mbar).

        Slow sine + Gaussian noise around standard atmospheric pressure.
        """
        return TelemetryGenerator(
            waveform=WaveformType.SINE,
            frequency=frequency,
            amplitude=variation,
            offset=base,
            noise_injector=NoiseInjector(noise_level, NoiseType.GAUSSIAN, seed=seed),
            name=name,
            seed=seed,
        )

    @staticmethod
    def humidity(
        base: float = 55.0,
        variation: float = 15.0,
        frequency: float = 0.003,
        noise_level: float = 1.0,
        seed: Optional[int] = None,
        name: str = "humidity_pct",
    ) -> TelemetryGenerator:
        """
        Relative humidity sensor (%).

        Clamped to [0, 100].
        """
        return TelemetryGenerator(
            waveform=WaveformType.SINE,
            frequency=frequency,
            amplitude=variation,
            offset=base,
            noise_injector=NoiseInjector(noise_level, NoiseType.GAUSSIAN, seed=seed),
            clamp_min=0.0,
            clamp_max=100.0,
            name=name,
            seed=seed,
        )

    @staticmethod
    def battery_voltage(
        start_voltage: float = 4.2,
        frequency: float = 0.001,
        noise_level: float = 0.02,
        seed: Optional[int] = None,
        name: str = "battery_V",
    ) -> TelemetryGenerator:
        """
        Li-ion battery voltage slowly discharging (exponential decay + noise).

        Clamped to [2.8, 4.2] V.
        """
        return TelemetryGenerator(
            waveform=WaveformType.EXPONENTIAL_DECAY,
            frequency=frequency,
            amplitude=start_voltage,
            offset=0.0,
            noise_injector=NoiseInjector(noise_level, NoiseType.GAUSSIAN, seed=seed),
            clamp_min=2.8,
            clamp_max=4.2,
            name=name,
            seed=seed,
        )

    @staticmethod
    def rpm(
        idle: float = 800.0,
        variation: float = 200.0,
        frequency: float = 0.1,
        noise_level: float = 20.0,
        seed: Optional[int] = None,
        name: str = "engine_rpm",
    ) -> TelemetryGenerator:
        """
        Engine RPM sensor.

        Triangle wave around idle + noisy jitter. Clamped >= 0.
        """
        return TelemetryGenerator(
            waveform=WaveformType.TRIANGLE,
            frequency=frequency,
            amplitude=variation,
            offset=idle,
            noise_injector=NoiseInjector(noise_level, NoiseType.GAUSSIAN, seed=seed),
            clamp_min=0.0,
            name=name,
            seed=seed,
        )

    @staticmethod
    def cpu_usage(
        base: float = 35.0,
        spike_amplitude: float = 40.0,
        frequency: float = 0.05,
        noise_level: float = 3.0,
        seed: Optional[int] = None,
        name: str = "cpu_pct",
    ) -> TelemetryGenerator:
        """
        CPU usage percentage.

        Sawtooth pattern (gradual ramp-up, quick drop) + noise. Clamped [0, 100].
        """
        return TelemetryGenerator(
            waveform=WaveformType.SAWTOOTH,
            frequency=frequency,
            amplitude=spike_amplitude,
            offset=base,
            noise_injector=NoiseInjector(noise_level, NoiseType.GAUSSIAN, seed=seed),
            clamp_min=0.0,
            clamp_max=100.0,
            name=name,
            seed=seed,
        )

    @staticmethod
    def network_latency(
        base_ms: float = 25.0,
        variation: float = 10.0,
        frequency: float = 0.02,
        noise_level: float = 3.0,
        seed: Optional[int] = None,
        name: str = "latency_ms",
    ) -> TelemetryGenerator:
        """
        Network round-trip latency (ms).

        Sine with uniform noise; clamped >= 1.
        """
        return TelemetryGenerator(
            waveform=WaveformType.SINE,
            frequency=frequency,
            amplitude=variation,
            offset=base_ms,
            noise_injector=NoiseInjector(noise_level, NoiseType.UNIFORM, seed=seed),
            clamp_min=1.0,
            name=name,
            seed=seed,
        )

    @staticmethod
    def heart_rate(
        resting: float = 72.0,
        variation: float = 8.0,
        frequency: float = 0.01,
        noise_level: float = 1.5,
        seed: Optional[int] = None,
        name: str = "heart_rate_bpm",
    ) -> TelemetryGenerator:
        """
        Heart-rate monitor (BPM).

        Sine wave around resting heart rate + noise. Clamped [30, 220].
        """
        return TelemetryGenerator(
            waveform=WaveformType.SINE,
            frequency=frequency,
            amplitude=variation,
            offset=resting,
            noise_injector=NoiseInjector(noise_level, NoiseType.GAUSSIAN, seed=seed),
            clamp_min=30.0,
            clamp_max=220.0,
            name=name,
            seed=seed,
        )

    @staticmethod
    def accelerometer(
        base_g: float = 0.0,
        amplitude: float = 1.0,
        frequency: float = 5.0,
        noise_level: float = 0.05,
        seed: Optional[int] = None,
        name: str = "accel_g",
    ) -> TelemetryGenerator:
        """
        Single-axis accelerometer (g-force).

        Higher frequency sine + small noise.
        """
        return TelemetryGenerator(
            waveform=WaveformType.SINE,
            frequency=frequency,
            amplitude=amplitude,
            offset=base_g,
            noise_injector=NoiseInjector(noise_level, NoiseType.GAUSSIAN, seed=seed),
            name=name,
            seed=seed,
        )

    @staticmethod
    def gps_coordinate(
        center: float = 59.3293,
        wander: float = 0.001,
        frequency: float = 0.01,
        noise_level: float = 0.0001,
        seed: Optional[int] = None,
        name: str = "gps_lat",
    ) -> TelemetryGenerator:
        """
        GPS latitude or longitude coordinate.

        Slow sine drift around *center* with tiny Brownian noise to
        simulate wandering position.
        """
        return TelemetryGenerator(
            waveform=WaveformType.SINE,
            frequency=frequency,
            amplitude=wander,
            offset=center,
            noise_injector=NoiseInjector(noise_level, NoiseType.BROWNIAN, seed=seed),
            name=name,
            seed=seed,
        )

    # ------------------------------------------------------------------
    # Additional presets
    # ------------------------------------------------------------------

    @staticmethod
    def light_lux(
        base: float = 400.0,
        variation: float = 300.0,
        frequency: float = 0.004,
        noise_level: float = 15.0,
        seed: Optional[int] = None,
        name: str = "light_lux",
    ) -> TelemetryGenerator:
        """
        Ambient light sensor (lux).

        Slow day/night cycle. Clamped >= 0.
        """
        return TelemetryGenerator(
            waveform=WaveformType.SINE,
            frequency=frequency,
            amplitude=variation,
            offset=base,
            noise_injector=NoiseInjector(noise_level, NoiseType.GAUSSIAN, seed=seed),
            clamp_min=0.0,
            name=name,
            seed=seed,
        )

    @staticmethod
    def co2_ppm(
        base: float = 420.0,
        variation: float = 80.0,
        frequency: float = 0.008,
        noise_level: float = 5.0,
        seed: Optional[int] = None,
        name: str = "co2_ppm",
    ) -> TelemetryGenerator:
        """
        CO2 concentration sensor (parts per million).

        Slow cycle (ventilation / occupancy patterns) + noise. Clamped >= 200.
        """
        return TelemetryGenerator(
            waveform=WaveformType.SINE,
            frequency=frequency,
            amplitude=variation,
            offset=base,
            noise_injector=NoiseInjector(noise_level, NoiseType.GAUSSIAN, seed=seed),
            clamp_min=200.0,
            name=name,
            seed=seed,
        )

    @staticmethod
    def wind_speed(
        base: float = 12.0,
        variation: float = 8.0,
        frequency: float = 0.03,
        noise_level: float = 2.0,
        seed: Optional[int] = None,
        name: str = "wind_m_s",
    ) -> TelemetryGenerator:
        """
        Wind speed sensor (m/s).

        Sine with uniform noise to simulate gusts. Clamped >= 0.
        """
        return TelemetryGenerator(
            waveform=WaveformType.SINE,
            frequency=frequency,
            amplitude=variation,
            offset=base,
            noise_injector=NoiseInjector(noise_level, NoiseType.UNIFORM, seed=seed),
            clamp_min=0.0,
            name=name,
            seed=seed,
        )

    @staticmethod
    def memory_usage(
        base: float = 55.0,
        variation: float = 20.0,
        frequency: float = 0.02,
        noise_level: float = 2.0,
        seed: Optional[int] = None,
        name: str = "memory_pct",
    ) -> TelemetryGenerator:
        """
        System memory usage (%).

        Sawtooth pattern (gradual growth, GC drop) + noise. Clamped [0, 100].
        """
        return TelemetryGenerator(
            waveform=WaveformType.SAWTOOTH,
            frequency=frequency,
            amplitude=variation,
            offset=base,
            noise_injector=NoiseInjector(noise_level, NoiseType.GAUSSIAN, seed=seed),
            clamp_min=0.0,
            clamp_max=100.0,
            name=name,
            seed=seed,
        )

    @staticmethod
    def disk_io(
        base: float = 30.0,
        spike_amplitude: float = 60.0,
        frequency: float = 0.1,
        noise_level: float = 5.0,
        seed: Optional[int] = None,
        name: str = "disk_io_mbps",
    ) -> TelemetryGenerator:
        """
        Disk I/O throughput (MB/s).

        Pulse-like bursts of activity. Clamped >= 0.
        """
        return TelemetryGenerator(
            waveform=WaveformType.PULSE,
            frequency=frequency,
            amplitude=spike_amplitude,
            offset=base,
            duty_cycle=0.3,
            noise_injector=NoiseInjector(noise_level, NoiseType.GAUSSIAN, seed=seed),
            clamp_min=0.0,
            name=name,
            seed=seed,
        )

    @staticmethod
    def flow_rate(
        base: float = 50.0,
        variation: float = 15.0,
        frequency: float = 0.015,
        noise_level: float = 1.5,
        seed: Optional[int] = None,
        name: str = "flow_l_min",
    ) -> TelemetryGenerator:
        """
        Liquid flow rate sensor (litres/min).

        Sine cycle + noise. Clamped >= 0.
        """
        return TelemetryGenerator(
            waveform=WaveformType.SINE,
            frequency=frequency,
            amplitude=variation,
            offset=base,
            noise_injector=NoiseInjector(noise_level, NoiseType.GAUSSIAN, seed=seed),
            clamp_min=0.0,
            name=name,
            seed=seed,
        )

    @staticmethod
    def vibration(
        amplitude: float = 0.5,
        frequency: float = 50.0,
        noise_level: float = 0.05,
        seed: Optional[int] = None,
        name: str = "vibration_mm_s",
    ) -> TelemetryGenerator:
        """
        Vibration sensor (mm/s RMS).

        High-frequency sine to simulate mechanical vibration.
        """
        return TelemetryGenerator(
            waveform=WaveformType.SINE,
            frequency=frequency,
            amplitude=amplitude,
            offset=0.0,
            noise_injector=NoiseInjector(noise_level, NoiseType.GAUSSIAN, seed=seed),
            name=name,
            seed=seed,
        )

    @staticmethod
    def ph_level(
        base: float = 7.0,
        variation: float = 0.5,
        frequency: float = 0.005,
        noise_level: float = 0.05,
        seed: Optional[int] = None,
        name: str = "ph",
    ) -> TelemetryGenerator:
        """
        pH sensor for water quality monitoring.

        Slow drift around neutral + small noise. Clamped [0, 14].
        """
        return TelemetryGenerator(
            waveform=WaveformType.SINE,
            frequency=frequency,
            amplitude=variation,
            offset=base,
            noise_injector=NoiseInjector(noise_level, NoiseType.GAUSSIAN, seed=seed),
            clamp_min=0.0,
            clamp_max=14.0,
            name=name,
            seed=seed,
        )

    @staticmethod
    def signal_strength(
        base: float = -60.0,
        variation: float = 15.0,
        frequency: float = 0.01,
        noise_level: float = 3.0,
        seed: Optional[int] = None,
        name: str = "rssi_dBm",
    ) -> TelemetryGenerator:
        """
        Wireless signal strength / RSSI (dBm).

        Sine drift + noise. Clamped [-120, 0].
        """
        return TelemetryGenerator(
            waveform=WaveformType.SINE,
            frequency=frequency,
            amplitude=variation,
            offset=base,
            noise_injector=NoiseInjector(noise_level, NoiseType.GAUSSIAN, seed=seed),
            clamp_min=-120.0,
            clamp_max=0.0,
            name=name,
            seed=seed,
        )
