"""
Protocol formatters for common telemetry ingestion systems.

Convert generated data into wire formats used by InfluxDB, MQTT brokers,
and Prometheus scrapers.

Example::

    from faketelemetry import TelemetryGenerator, WaveformType
    from faketelemetry.formatters import to_influxdb, to_mqtt_json

    gen = TelemetryGenerator(WaveformType.SINE, name="temperature")
    data = gen.batch(10, sampling_rate=1)

    for line in to_influxdb(data, measurement="sensors", tags={"room": "lab"}):
        print(line)

    for payload in to_mqtt_json(data, sensor_id="temp-01"):
        print(payload)
"""

import json
from datetime import datetime
from typing import Dict, Iterator, List, Optional, Tuple


# ------------------------------------------------------------------
# InfluxDB line protocol
# ------------------------------------------------------------------

def to_influxdb(
    data: List[Tuple[datetime, float]],
    measurement: str = "telemetry",
    field_name: str = "value",
    tags: Optional[Dict[str, str]] = None,
    precision: str = "ns",
) -> List[str]:
    """
    Format batch data as InfluxDB line protocol strings.

    Format: ``measurement,tag=val field=val timestamp``

    :param data: Output from :meth:`TelemetryGenerator.batch`.
    :param measurement: InfluxDB measurement name.
    :param field_name: Field key for the value.
    :param tags: Optional dict of tag key-value pairs.
    :param precision: Timestamp precision (``"ns"``, ``"us"``, ``"ms"``, ``"s"``).
    :returns: List of line-protocol strings.
    """
    multipliers = {"s": 1, "ms": 1_000, "us": 1_000_000, "ns": 1_000_000_000}
    if precision not in multipliers:
        raise ValueError(f"precision must be one of {list(multipliers)}")
    mult = multipliers[precision]

    tag_str = ""
    if tags:
        tag_str = "," + ",".join(f"{k}={v}" for k, v in sorted(tags.items()))

    lines: List[str] = []
    for ts, val in data:
        epoch = int(ts.timestamp() * mult)
        lines.append(f"{measurement}{tag_str} {field_name}={val} {epoch}")
    return lines


def to_influxdb_multi(
    rows: List[Dict],
    measurement: str = "telemetry",
    tags: Optional[Dict[str, str]] = None,
    precision: str = "ns",
) -> List[str]:
    """
    Format multi-channel batch rows as InfluxDB line protocol.

    Each row dict should have a ``"timestamp"`` key plus one key per channel.
    All channel values become fields on a single line.
    """
    multipliers = {"s": 1, "ms": 1_000, "us": 1_000_000, "ns": 1_000_000_000}
    if precision not in multipliers:
        raise ValueError(f"precision must be one of {list(multipliers)}")
    mult = multipliers[precision]

    tag_str = ""
    if tags:
        tag_str = "," + ",".join(f"{k}={v}" for k, v in sorted(tags.items()))

    lines: List[str] = []
    for row in rows:
        ts_raw = row.get("timestamp")
        if ts_raw is None:
            continue
        if isinstance(ts_raw, str):
            ts = datetime.fromisoformat(ts_raw)
        else:
            ts = ts_raw
        epoch = int(ts.timestamp() * mult)
        fields = ",".join(
            f"{k}={v}" for k, v in row.items()
            if k != "timestamp" and isinstance(v, (int, float))
        )
        if fields:
            lines.append(f"{measurement}{tag_str} {fields} {epoch}")
    return lines


# ------------------------------------------------------------------
# MQTT JSON payloads
# ------------------------------------------------------------------

def to_mqtt_json(
    data: List[Tuple[datetime, float]],
    sensor_id: Optional[str] = None,
    extra_fields: Optional[Dict] = None,
) -> List[str]:
    """
    Format batch data as MQTT-style JSON payloads (one JSON string per sample).

    :param data: Output from :meth:`TelemetryGenerator.batch`.
    :param sensor_id: Optional sensor identifier to include.
    :param extra_fields: Optional extra key-value pairs to include in each payload.
    :returns: List of JSON strings.
    """
    payloads: List[str] = []
    for ts, val in data:
        obj: Dict = {"timestamp": ts.isoformat(), "value": val}
        if sensor_id is not None:
            obj["sensor_id"] = sensor_id
        if extra_fields:
            obj.update(extra_fields)
        payloads.append(json.dumps(obj))
    return payloads


def to_mqtt_json_multi(
    rows: List[Dict],
    device_id: Optional[str] = None,
) -> List[str]:
    """
    Format multi-channel batch rows as MQTT JSON payloads.
    """
    payloads: List[str] = []
    for row in rows:
        obj = dict(row)
        if device_id is not None:
            obj["device_id"] = device_id
        payloads.append(json.dumps(obj))
    return payloads


# ------------------------------------------------------------------
# Prometheus exposition format
# ------------------------------------------------------------------

def to_prometheus(
    data: List[Tuple[datetime, float]],
    metric_name: str = "telemetry_value",
    labels: Optional[Dict[str, str]] = None,
    help_text: Optional[str] = None,
    type_text: str = "gauge",
) -> str:
    """
    Format batch data as Prometheus exposition format text.

    :param data: Output from :meth:`TelemetryGenerator.batch`.
    :param metric_name: Prometheus metric name.
    :param labels: Optional label key-value pairs.
    :param help_text: HELP line text.
    :param type_text: TYPE annotation (``"gauge"``, ``"counter"``, etc.).
    :returns: Multi-line string in Prometheus exposition format.
    """
    lines: List[str] = []

    if help_text:
        lines.append(f"# HELP {metric_name} {help_text}")
    lines.append(f"# TYPE {metric_name} {type_text}")

    label_str = ""
    if labels:
        inner = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        label_str = "{" + inner + "}"

    for ts, val in data:
        epoch_ms = int(ts.timestamp() * 1000)
        lines.append(f"{metric_name}{label_str} {val} {epoch_ms}")

    return "\n".join(lines) + "\n"
