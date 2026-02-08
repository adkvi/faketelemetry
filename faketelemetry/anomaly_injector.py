import random
from typing import Optional, List

from .enums import AnomalyType


class AnomalyConfig:
    """
    Configuration for a single anomaly behaviour.

    Example::

        cfg = AnomalyConfig(
            anomaly_type=AnomalyType.SPIKE,
            probability=0.05,
            magnitude=10.0,
        )
    """

    def __init__(
        self,
        anomaly_type: AnomalyType,
        probability: float = 0.01,
        magnitude: float = 5.0,
        duration_samples: int = 1,
        drift_rate: float = 0.0,
        stuck_value: Optional[float] = None,
        jitter_range: float = 0.0,
    ):
        """
        :param anomaly_type: Which anomaly behaviour to apply.
        :param probability: Chance (0-1) per sample that the anomaly activates.
        :param magnitude: Size of the anomaly effect.
            - SPIKE: added/subtracted value.
            - DROPOUT: (ignored, value is set to 0).
            - DRIFT: (ignored, use drift_rate instead).
            - FLATLINE / STUCK_AT: (ignored, value is frozen).
            - JITTER: (ignored, use jitter_range instead).
        :param duration_samples: How many consecutive samples the anomaly
            persists once triggered (FLATLINE, STUCK_AT, DROPOUT).
        :param drift_rate: Value added per sample for DRIFT anomaly.
        :param stuck_value: Fixed output value for STUCK_AT anomaly.
        :param jitter_range: Random time-jitter range added to value for JITTER.
        """
        if not 0 <= probability <= 1:
            raise ValueError("probability must be between 0 and 1.")
        if duration_samples < 1:
            raise ValueError("duration_samples must be >= 1.")

        self.anomaly_type = anomaly_type
        self.probability = probability
        self.magnitude = magnitude
        self.duration_samples = duration_samples
        self.drift_rate = drift_rate
        self.stuck_value = stuck_value
        self.jitter_range = jitter_range


class AnomalyInjector:
    """
    Applies one or more anomaly behaviours to telemetry values.

    Anomalies are stochastic: on each call to :meth:`apply` there is a
    per-anomaly *probability* that the anomaly activates.  Some anomalies
    (FLATLINE, STUCK_AT, DROPOUT) persist for ``duration_samples`` once
    triggered.

    Example::

        injector = AnomalyInjector(
            configs=[
                AnomalyConfig(AnomalyType.SPIKE, probability=0.05, magnitude=10),
                AnomalyConfig(AnomalyType.DRIFT, probability=1.0, drift_rate=0.01),
            ],
            seed=42,
        )
        clean_value = 3.14
        possibly_anomalous = injector.apply(clean_value)
    """

    def __init__(
        self,
        configs: Optional[List[AnomalyConfig]] = None,
        seed: Optional[int] = None,
    ):
        self.configs: List[AnomalyConfig] = configs or []
        self._rng = random.Random(seed)

        # Per-config internal state
        self._remaining: dict[int, int] = {}  # config index -> remaining samples
        self._frozen_value: dict[int, float] = {}
        self._drift_accum: dict[int, float] = {}
        for i, cfg in enumerate(self.configs):
            self._remaining[i] = 0
            self._frozen_value[i] = 0.0
            self._drift_accum[i] = 0.0

    def reset(self) -> None:
        """Reset all internal anomaly state."""
        for i in range(len(self.configs)):
            self._remaining[i] = 0
            self._frozen_value[i] = 0.0
            self._drift_accum[i] = 0.0

    def apply(self, value: float) -> float:
        """
        Process *value* through all configured anomalies and return the
        (possibly modified) result.
        """
        for i, cfg in enumerate(self.configs):
            value = self._apply_one(value, i, cfg)
        return value

    # ------------------------------------------------------------------
    def _apply_one(self, value: float, idx: int, cfg: AnomalyConfig) -> float:
        at = cfg.anomaly_type

        # --- persistent anomalies (active for duration_samples) ---
        if at in (AnomalyType.FLATLINE, AnomalyType.STUCK_AT, AnomalyType.DROPOUT):
            if self._remaining[idx] > 0:
                self._remaining[idx] -= 1
                if at == AnomalyType.DROPOUT:
                    return 0.0
                return self._frozen_value[idx]
            # chance to trigger
            if self._rng.random() < cfg.probability:
                self._remaining[idx] = cfg.duration_samples - 1
                if at == AnomalyType.DROPOUT:
                    return 0.0
                elif at == AnomalyType.STUCK_AT:
                    self._frozen_value[idx] = (
                        cfg.stuck_value if cfg.stuck_value is not None else value
                    )
                else:  # FLATLINE
                    self._frozen_value[idx] = value
                return self._frozen_value[idx]
            return value

        # --- spike ---
        if at == AnomalyType.SPIKE:
            if self._rng.random() < cfg.probability:
                sign = self._rng.choice([-1, 1])
                return value + sign * cfg.magnitude
            return value

        # --- drift ---
        if at == AnomalyType.DRIFT:
            if self._rng.random() < cfg.probability:
                self._drift_accum[idx] += cfg.drift_rate
            return value + self._drift_accum[idx]

        # --- jitter ---
        if at == AnomalyType.JITTER:
            if self._rng.random() < cfg.probability:
                return value + self._rng.uniform(-cfg.jitter_range, cfg.jitter_range)
            return value

        raise ValueError(f"Unsupported anomaly type: {at}")
