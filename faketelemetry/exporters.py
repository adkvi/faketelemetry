"""
Utilities for exporting generated telemetry data to common file formats.

Example::

    from faketelemetry import TelemetryGenerator, WaveformType
    from faketelemetry.exporters import to_csv, to_json

    gen = TelemetryGenerator(WaveformType.SINE, name="sensor_a")
    data = gen.batch(1000, sampling_rate=100)

    to_csv(data, "output.csv")
    to_json(data, "output.json")
"""

import csv
import json
import io
from datetime import datetime
from typing import List, Tuple, Optional, Union, TextIO


def to_csv(
    data: List[Tuple[datetime, float]],
    path_or_file: Optional[Union[str, TextIO]] = None,
    fieldnames: Tuple[str, str] = ("timestamp", "value"),
    delimiter: str = ",",
) -> Optional[str]:
    """
    Write ``(datetime, value)`` tuples to CSV.

    :param data: Output from :meth:`TelemetryGenerator.batch`.
    :param path_or_file: File path or file-like object. If *None*, returns
        the CSV as a string.
    :param fieldnames: Column header names.
    :param delimiter: CSV delimiter character.
    :returns: CSV string when *path_or_file* is None, else None.
    """
    if path_or_file is None:
        buf = io.StringIO()
        _write_csv(buf, data, fieldnames, delimiter)
        return buf.getvalue()
    elif isinstance(path_or_file, str):
        with open(path_or_file, "w", newline="", encoding="utf-8") as f:
            _write_csv(f, data, fieldnames, delimiter)
        return None
    else:
        _write_csv(path_or_file, data, fieldnames, delimiter)
        return None


def _write_csv(
    f: TextIO,
    data: List[Tuple[datetime, float]],
    fieldnames: Tuple[str, str],
    delimiter: str,
) -> None:
    writer = csv.writer(f, delimiter=delimiter)
    writer.writerow(fieldnames)
    for ts, val in data:
        writer.writerow([ts.isoformat(), val])


def to_json(
    data: List[Tuple[datetime, float]],
    path_or_file: Optional[Union[str, TextIO]] = None,
    indent: Optional[int] = 2,
) -> Optional[str]:
    """
    Write ``(datetime, value)`` tuples to JSON (array of objects).

    :param data: Output from :meth:`TelemetryGenerator.batch`.
    :param path_or_file: File path or file-like object. If *None*, returns
        the JSON as a string.
    :param indent: JSON indentation (None for compact).
    :returns: JSON string when *path_or_file* is None, else None.
    """
    records = [{"timestamp": ts.isoformat(), "value": val} for ts, val in data]

    if path_or_file is None:
        return json.dumps(records, indent=indent)
    elif isinstance(path_or_file, str):
        with open(path_or_file, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=indent)
        return None
    else:
        json.dump(records, path_or_file, indent=indent)
        return None


def to_ndjson(
    data: List[Tuple[datetime, float]],
    path_or_file: Optional[Union[str, TextIO]] = None,
) -> Optional[str]:
    """
    Write ``(datetime, value)`` tuples to newline-delimited JSON (NDJSON).

    Each line is a self-contained JSON object -- ideal for streaming
    ingestion pipelines (e.g. Kafka, Logstash, BigQuery).

    :returns: NDJSON string when *path_or_file* is None, else None.
    """
    lines = [json.dumps({"timestamp": ts.isoformat(), "value": val}) for ts, val in data]
    text = "\n".join(lines) + "\n"

    if path_or_file is None:
        return text
    elif isinstance(path_or_file, str):
        with open(path_or_file, "w", encoding="utf-8") as f:
            f.write(text)
        return None
    else:
        path_or_file.write(text)
        return None


def to_multichannel_csv(
    rows: list,
    path_or_file: Optional[Union[str, TextIO]] = None,
    delimiter: str = ",",
) -> Optional[str]:
    """
    Write output from :meth:`MultiChannelTelemetryGenerator.batch` to CSV.

    *rows* should be a list of dicts with a ``"timestamp"`` key and one key
    per channel.

    :returns: CSV string when *path_or_file* is None, else None.
    """
    if not rows:
        return "" if path_or_file is None else None

    fieldnames = list(rows[0].keys())

    if path_or_file is None:
        buf = io.StringIO()
        _write_multi_csv(buf, rows, fieldnames, delimiter)
        return buf.getvalue()
    elif isinstance(path_or_file, str):
        with open(path_or_file, "w", newline="", encoding="utf-8") as f:
            _write_multi_csv(f, rows, fieldnames, delimiter)
        return None
    else:
        _write_multi_csv(path_or_file, rows, fieldnames, delimiter)
        return None


def _write_multi_csv(
    f: TextIO,
    rows: list,
    fieldnames: list,
    delimiter: str,
) -> None:
    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
    writer.writeheader()
    writer.writerows(rows)
