from __future__ import annotations

import asyncio
import time
from datetime import datetime, timedelta
from typing import AsyncIterator, Optional, Dict, List, Tuple, Any, Iterator, Union

from .telemetry_generator import TelemetryGenerator


class MultiChannelTelemetryGenerator:
    """
    Generate multiple telemetry streams (channels) synchronised to the
    same time base.

    Channels can be referenced by **name** (if the generators have names)
    or by **integer index**.

    Example::

        multi = MultiChannelTelemetryGenerator({
            "temperature": TelemetryGenerator(WaveformType.SINE, name="temp"),
            "pressure":    TelemetryGenerator(WaveformType.COSINE, name="press"),
        })

        # Real-time
        for sample in multi.stream(sampling_rate=2, duration=5):
            print(sample)

        # Batch
        rows = multi.batch(num_samples=200, sampling_rate=50)
    """

    def __init__(
        self,
        generators: Union[List[TelemetryGenerator], Dict[str, TelemetryGenerator]],
    ):
        """
        :param generators: Either a list (channels keyed by integer index)
            or a dict (channels keyed by string name).
        """
        if isinstance(generators, dict):
            self._generators: Dict[str, TelemetryGenerator] = generators
        elif isinstance(generators, list):
            self._generators = {(gen.name or str(idx)): gen for idx, gen in enumerate(generators)}
        else:
            raise TypeError("generators must be a list or dict of TelemetryGenerator.")

        if not self._generators:
            raise ValueError("At least one generator is required.")

    @property
    def channel_names(self) -> List[str]:
        """Return the list of channel keys."""
        return list(self._generators.keys())

    def __len__(self) -> int:
        return len(self._generators)

    def __getitem__(self, key: str) -> TelemetryGenerator:
        return self._generators[key]

    # ------------------------------------------------------------------
    # Real-time streaming
    # ------------------------------------------------------------------

    def stream(
        self,
        sampling_rate: float,
        duration: Optional[float] = None,
    ) -> Iterator[Dict[str, Tuple[datetime, float]]]:
        """
        Yield one ``{channel_key: (datetime, value)}`` dict per sample
        in **real-time**.
        """
        interval = 1.0 / sampling_rate
        start_time = time.time()
        elapsed = 0.0
        while duration is None or elapsed < duration:
            now = time.time() - start_time
            ts = datetime.now()
            result: Dict[str, Tuple[datetime, float]] = {}
            for key, gen in self._generators.items():
                value = gen.generate_point(now)
                result[key] = (ts, value)
            yield result
            time.sleep(interval)
            elapsed = time.time() - start_time

    # ------------------------------------------------------------------
    # Async streaming
    # ------------------------------------------------------------------

    async def astream(
        self,
        sampling_rate: float,
        duration: Optional[float] = None,
    ) -> AsyncIterator[Dict[str, Tuple[datetime, float]]]:
        """
        Async version of :meth:`stream`.  Use with ``async for``::

            async for sample in multi.astream(sampling_rate=10, duration=5):
                print(sample)
        """
        interval = 1.0 / sampling_rate
        start_time = time.time()
        elapsed = 0.0
        while duration is None or elapsed < duration:
            now = time.time() - start_time
            ts = datetime.now()
            result: Dict[str, Tuple[datetime, float]] = {}
            for key, gen in self._generators.items():
                value = gen.generate_point(now)
                result[key] = (ts, value)
            yield result
            await asyncio.sleep(interval)
            elapsed = time.time() - start_time

    # ------------------------------------------------------------------
    # Batch (non-real-time)
    # ------------------------------------------------------------------

    def batch(
        self,
        num_samples: int,
        sampling_rate: float,
        start_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate *num_samples* synchronised across all channels instantly.

        Returns a list of row-dicts suitable for ``pandas.DataFrame``::

            import pandas as pd
            df = pd.DataFrame(multi.batch(1000, 100))

        Each dict has keys: ``"timestamp"`` plus one key per channel name.
        """
        if num_samples < 0:
            raise ValueError("num_samples must be non-negative.")
        if sampling_rate <= 0:
            raise ValueError("sampling_rate must be positive.")

        interval = 1.0 / sampling_rate
        base = start_time or datetime.now()
        rows: List[Dict[str, Any]] = []
        for i in range(num_samples):
            t = i * interval
            ts = base + timedelta(seconds=t)
            row: Dict[str, Any] = {"timestamp": ts.isoformat()}
            for key, gen in self._generators.items():
                row[key] = gen.generate_point(t)
            rows.append(row)
        return rows

    def batch_arrays(
        self,
        num_samples: int,
        sampling_rate: float,
    ) -> Dict[str, List[float]]:
        """
        Return ``{channel_name: [values ...]}`` without timestamps.
        Useful when you just need raw arrays (e.g., for plotting).
        """
        if num_samples < 0:
            raise ValueError("num_samples must be non-negative.")
        if sampling_rate <= 0:
            raise ValueError("sampling_rate must be positive.")

        interval = 1.0 / sampling_rate
        arrays: Dict[str, List[float]] = {k: [] for k in self._generators}
        for i in range(num_samples):
            t = i * interval
            for key, gen in self._generators.items():
                arrays[key].append(gen.generate_point(t))
        return arrays

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Reset state for all child generators."""
        for gen in self._generators.values():
            gen.reset()

    def __repr__(self) -> str:
        channels = ", ".join(self._generators.keys())
        return f"MultiChannelTelemetryGenerator([{channels}])"
