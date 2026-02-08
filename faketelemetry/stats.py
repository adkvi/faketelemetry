"""
Statistical summary utilities for generated telemetry data.

Example::

    from faketelemetry import TelemetryGenerator, WaveformType
    from faketelemetry.stats import describe, describe_multi

    gen = TelemetryGenerator(WaveformType.SINE, amplitude=5.0)
    data = gen.batch(1000, sampling_rate=100)
    print(describe(data))
"""

import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


def describe(
    data: List[Tuple[datetime, float]],
    percentiles: Tuple[float, ...] = (0.25, 0.50, 0.75, 0.95, 0.99),
) -> Dict[str, Any]:
    """
    Compute summary statistics for single-channel batch data.

    :param data: Output from :meth:`TelemetryGenerator.batch`.
    :param percentiles: Fractional percentiles to compute (0-1).
    :returns: Dict with keys: ``count``, ``mean``, ``std``, ``min``, ``max``,
        ``range``, ``p25``, ``p50``, etc., ``start``, ``end``, ``duration_s``.
    """
    if not data:
        return {"count": 0}

    values = [v for _, v in data]
    return _summarise(values, data[0][0], data[-1][0], percentiles)


def describe_values(
    values: List[float],
    percentiles: Tuple[float, ...] = (0.25, 0.50, 0.75, 0.95, 0.99),
) -> Dict[str, Any]:
    """
    Compute summary statistics for a raw list of floats.

    :param values: List of signal values.
    :param percentiles: Fractional percentiles to compute (0-1).
    :returns: Dict with keys: ``count``, ``mean``, ``std``, ``min``, ``max``,
        ``range``, ``p25``, ``p50``, etc.
    """
    if not values:
        return {"count": 0}
    return _summarise(values, None, None, percentiles)


def describe_multi(
    rows: List[Dict[str, Any]],
    percentiles: Tuple[float, ...] = (0.25, 0.50, 0.75, 0.95, 0.99),
) -> Dict[str, Dict[str, Any]]:
    """
    Compute per-channel summary statistics for multi-channel batch data.

    :param rows: Output from :meth:`MultiChannelTelemetryGenerator.batch`.
    :param percentiles: Fractional percentiles to compute (0-1).
    :returns: ``{channel_name: {stats ...}}``.
    """
    if not rows:
        return {}

    # Collect values per channel (skip "timestamp")
    channels: Dict[str, List[float]] = {}
    for row in rows:
        for key, val in row.items():
            if key == "timestamp":
                continue
            if isinstance(val, (int, float)):
                channels.setdefault(key, []).append(float(val))

    result: Dict[str, Dict[str, Any]] = {}
    for ch, vals in channels.items():
        result[ch] = _summarise(vals, None, None, percentiles)
    return result


# ------------------------------------------------------------------
# Internal helpers (stdlib only -- no numpy)
# ------------------------------------------------------------------

def _summarise(
    values: List[float],
    start: Optional[datetime],
    end: Optional[datetime],
    percentiles: Tuple[float, ...],
) -> Dict[str, Any]:
    n = len(values)
    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / n
    std = math.sqrt(variance)
    sorted_vals = sorted(values)

    stats: Dict[str, Any] = {
        "count": n,
        "mean": mean,
        "std": std,
        "min": sorted_vals[0],
        "max": sorted_vals[-1],
        "range": sorted_vals[-1] - sorted_vals[0],
    }

    for p in percentiles:
        idx = max(0, min(n - 1, int(p * n)))
        key = f"p{int(p * 100)}"
        stats[key] = sorted_vals[idx]

    if start is not None and end is not None:
        stats["start"] = start.isoformat()
        stats["end"] = end.isoformat()
        stats["duration_s"] = (end - start).total_seconds()

    return stats
