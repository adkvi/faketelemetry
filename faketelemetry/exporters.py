"""
Data export utilities for faketelemetry.

Provides functions to export telemetry data to various formats
including JSON and CSV.
"""

import json
import csv
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any, TextIO, Union
from pathlib import Path


def to_json(
    data: List[Tuple[datetime, float]],
    output: Optional[Union[str, Path, TextIO]] = None,
    indent: int = 2,
    datetime_format: str = "%Y-%m-%dT%H:%M:%S.%f",
) -> str:
    """
    Export telemetry data to JSON format.

    :param data: List of (datetime, value) tuples
    :param output: Optional file path or file-like object to write to.
                   If None, returns the JSON string.
    :param indent: JSON indentation level (default 2)
    :param datetime_format: Format string for datetime serialization
    :return: JSON string representation of the data
    """
    records = [
        {"timestamp": ts.strftime(datetime_format), "value": val} for ts, val in data
    ]

    json_str = json.dumps(records, indent=indent)

    if output is not None:
        if isinstance(output, (str, Path)):
            with open(output, "w", encoding="utf-8") as f:
                f.write(json_str)
        else:
            output.write(json_str)

    return json_str


def to_csv(
    data: List[Tuple[datetime, float]],
    output: Optional[Union[str, Path, TextIO]] = None,
    datetime_format: str = "%Y-%m-%dT%H:%M:%S.%f",
    include_header: bool = True,
) -> str:
    """
    Export telemetry data to CSV format.

    :param data: List of (datetime, value) tuples
    :param output: Optional file path or file-like object to write to.
                   If None, returns the CSV string.
    :param datetime_format: Format string for datetime serialization
    :param include_header: Whether to include a header row (default True)
    :return: CSV string representation of the data
    """
    import io

    buffer = io.StringIO()
    writer = csv.writer(buffer)

    if include_header:
        writer.writerow(["timestamp", "value"])

    for ts, val in data:
        writer.writerow([ts.strftime(datetime_format), val])

    csv_str = buffer.getvalue()

    if output is not None:
        if isinstance(output, (str, Path)):
            with open(output, "w", encoding="utf-8", newline="") as f:
                f.write(csv_str)
        else:
            output.write(csv_str)

    return csv_str


def to_dict(
    data: List[Tuple[datetime, float]],
    datetime_format: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Convert telemetry data to a list of dictionaries.

    :param data: List of (datetime, value) tuples
    :param datetime_format: Optional format string for datetime.
                           If None, datetime objects are kept as-is.
    :return: List of dictionaries with 'timestamp' and 'value' keys
    """
    if datetime_format:
        return [
            {"timestamp": ts.strftime(datetime_format), "value": val}
            for ts, val in data
        ]
    return [{"timestamp": ts, "value": val} for ts, val in data]


def from_json(
    source: Union[str, Path, TextIO],
    datetime_format: str = "%Y-%m-%dT%H:%M:%S.%f",
) -> List[Tuple[datetime, float]]:
    """
    Import telemetry data from JSON format.

    :param source: JSON string, file path, or file-like object
    :param datetime_format: Format string for datetime parsing
    :return: List of (datetime, value) tuples
    """
    if isinstance(source, (str, Path)):
        path = Path(source)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                records = json.load(f)
        else:
            # Assume it's a JSON string
            records = json.loads(str(source))
    else:
        records = json.load(source)

    return [
        (datetime.strptime(r["timestamp"], datetime_format), float(r["value"]))
        for r in records
    ]


def from_csv(
    source: Union[str, Path, TextIO],
    datetime_format: str = "%Y-%m-%dT%H:%M:%S.%f",
    has_header: bool = True,
) -> List[Tuple[datetime, float]]:
    """
    Import telemetry data from CSV format.

    :param source: CSV string, file path, or file-like object
    :param datetime_format: Format string for datetime parsing
    :param has_header: Whether the CSV has a header row (default True)
    :return: List of (datetime, value) tuples
    """
    import io

    if isinstance(source, (str, Path)):
        path = Path(source)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            # Assume it's a CSV string
            content = str(source)
        reader = csv.reader(io.StringIO(content))
    else:
        reader = csv.reader(source)

    if has_header:
        next(reader, None)  # Skip header

    return [
        (datetime.strptime(row[0], datetime_format), float(row[1]))
        for row in reader
        if row
    ]
