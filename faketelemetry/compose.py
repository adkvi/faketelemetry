"""
Signal composition: combine multiple generators using arithmetic operators.

Supports ``+``, ``-``, ``*``, and nesting to build complex signals from
simple building blocks.

Example::

    from faketelemetry import TelemetryGenerator, WaveformType

    # Sum of harmonics (approximates a square wave)
    fundamental = TelemetryGenerator(WaveformType.SINE, frequency=1.0, amplitude=1.0)
    harmonic3   = TelemetryGenerator(WaveformType.SINE, frequency=3.0, amplitude=1/3)
    harmonic5   = TelemetryGenerator(WaveformType.SINE, frequency=5.0, amplitude=1/5)
    approx_square = fundamental + harmonic3 + harmonic5

    # Amplitude modulation
    carrier = TelemetryGenerator(WaveformType.SINE, frequency=100.0)
    envelope = TelemetryGenerator(WaveformType.SINE, frequency=1.0, amplitude=0.5, offset=0.5)
    am_signal = carrier * envelope

    # Offset a signal by a constant
    biased = TelemetryGenerator(WaveformType.SINE) + 10.0

    # All composite generators support batch/stream/generate_point
    values = approx_square.batch_values(500, sampling_rate=200)
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import Dict, Iterator, List, Optional, Tuple, Any, Union

# Anything that has a ``generate_point(t) -> float`` method.
_Generatable = Any  # TelemetryGenerator | CompositeGenerator | float | int


class CompositeGenerator:
    """
    A generator formed by combining two operands with an arithmetic
    operation.  Operands can be :class:`TelemetryGenerator`,
    other :class:`CompositeGenerator` instances, or plain numbers.

    You rarely need to construct this directly -- use the ``+``, ``-``,
    ``*`` operators on any generator instead.
    """

    def __init__(
        self,
        left: _Generatable,
        right: _Generatable,
        operation: str,
        name: Optional[str] = None,
    ):
        if operation not in ("add", "sub", "mul"):
            raise ValueError(f"Unsupported operation: {operation!r}")
        self.left = left
        self.right = right
        self.operation = operation
        self.name = name

    # ------------------------------------------------------------------
    # Core
    # ------------------------------------------------------------------

    @staticmethod
    def _eval(operand: _Generatable, t: float) -> float:
        """Evaluate an operand at time *t*."""
        if isinstance(operand, (int, float)):
            return float(operand)
        return operand.generate_point(t)

    def generate_point(self, t: float) -> float:
        """Generate the composite signal value at time *t*."""
        l = self._eval(self.left, t)
        r = self._eval(self.right, t)
        if self.operation == "add":
            return l + r
        elif self.operation == "sub":
            return l - r
        elif self.operation == "mul":
            return l * r
        raise ValueError(f"Unsupported operation: {self.operation!r}")

    # ------------------------------------------------------------------
    # Batch & streaming (mirror TelemetryGenerator API)
    # ------------------------------------------------------------------

    def batch(
        self,
        num_samples: int,
        sampling_rate: float,
        start_time: Optional[datetime] = None,
    ) -> List[Tuple[datetime, float]]:
        """Generate *num_samples* points instantly."""
        if num_samples < 0:
            raise ValueError("num_samples must be non-negative.")
        if sampling_rate <= 0:
            raise ValueError("sampling_rate must be positive.")
        interval = 1.0 / sampling_rate
        base = start_time or datetime.now()
        return [
            (base + timedelta(seconds=i * interval), self.generate_point(i * interval))
            for i in range(num_samples)
        ]

    def batch_values(self, num_samples: int, sampling_rate: float) -> List[float]:
        """Generate raw values (no timestamps)."""
        if num_samples < 0:
            raise ValueError("num_samples must be non-negative.")
        if sampling_rate <= 0:
            raise ValueError("sampling_rate must be positive.")
        interval = 1.0 / sampling_rate
        return [self.generate_point(i * interval) for i in range(num_samples)]

    def stream(
        self, sampling_rate: float, duration: Optional[float] = None
    ) -> Iterator[Tuple[datetime, float]]:
        """Real-time streaming."""
        interval = 1.0 / sampling_rate
        start = time.time()
        elapsed = 0.0
        while duration is None or elapsed < duration:
            now = time.time() - start
            yield (datetime.now(), self.generate_point(now))
            time.sleep(interval)
            elapsed = time.time() - start

    def to_dict(
        self,
        num_samples: int,
        sampling_rate: float,
        start_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Return batch as list of dicts (DataFrame-ready)."""
        points = self.batch(num_samples, sampling_rate, start_time)
        return [
            {"timestamp": ts.isoformat(), "value": val, "channel": self.name} for ts, val in points
        ]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Reset state on both operands (if they support it)."""
        for operand in (self.left, self.right):
            if hasattr(operand, "reset"):
                operand.reset()

    # ------------------------------------------------------------------
    # Operators (allow further composition)
    # ------------------------------------------------------------------

    def __add__(self, other: _Generatable) -> "CompositeGenerator":
        return CompositeGenerator(self, other, "add")

    def __radd__(self, other: _Generatable) -> "CompositeGenerator":
        return CompositeGenerator(other, self, "add")

    def __sub__(self, other: _Generatable) -> "CompositeGenerator":
        return CompositeGenerator(self, other, "sub")

    def __rsub__(self, other: _Generatable) -> "CompositeGenerator":
        return CompositeGenerator(other, self, "sub")

    def __mul__(self, other: _Generatable) -> "CompositeGenerator":
        return CompositeGenerator(self, other, "mul")

    def __rmul__(self, other: _Generatable) -> "CompositeGenerator":
        return CompositeGenerator(other, self, "mul")

    def __neg__(self) -> "CompositeGenerator":
        return CompositeGenerator(-1, self, "mul")

    def __repr__(self) -> str:
        op_map = {"add": "+", "sub": "-", "mul": "*"}
        return f"({self.left!r} {op_map[self.operation]} {self.right!r})"


# ------------------------------------------------------------------
# Convenience function
# ------------------------------------------------------------------


def compose(*generators: _Generatable, operation: str = "add") -> CompositeGenerator:
    """
    Combine an arbitrary number of generators with the given operation.

    Example::

        from faketelemetry.compose import compose

        signal = compose(gen1, gen2, gen3)           # gen1 + gen2 + gen3
        signal = compose(gen1, gen2, operation="mul") # gen1 * gen2
    """
    if len(generators) < 2:
        raise ValueError("compose() requires at least two generators.")
    result = CompositeGenerator(generators[0], generators[1], operation)
    for g in generators[2:]:
        result = CompositeGenerator(result, g, operation)
    return result
