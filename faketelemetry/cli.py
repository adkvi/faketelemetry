"""
Command-line interface for faketelemetry.

Entry points:
    python -m faketelemetry ...
    faketelemetry ...            (after pip install)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from . import __version__
from .enums import AnomalyType, NoiseType, WaveformType
from .exporters import to_csv, to_json, to_ndjson, to_multichannel_csv
from .formatters import to_influxdb, to_influxdb_multi
from .multi_channel import MultiChannelTelemetryGenerator
from .noise_injector import NoiseInjector
from .presets import SensorPreset
from .stats import describe, describe_multi
from .telemetry_generator import TelemetryGenerator

# ------------------------------------------------------------------
# Preset registry: name -> (factory method, short description)
# ------------------------------------------------------------------

_PRESETS: Dict[str, Tuple[Any, str]] = {
    "temperature": (SensorPreset.temperature, "~22 C, slow sine + Gaussian noise"),
    "pressure": (SensorPreset.pressure, "~1013 hPa, slow sine + Gaussian noise"),
    "humidity": (SensorPreset.humidity, "0-100 %, sine + noise, clamped"),
    "battery_voltage": (
        SensorPreset.battery_voltage,
        "4.2 V exponential decay, clamped [2.8, 4.2]",
    ),
    "rpm": (SensorPreset.rpm, "~800 RPM idle, triangle + noise, clamped >= 0"),
    "cpu_usage": (SensorPreset.cpu_usage, "0-100 %, sawtooth + noise"),
    "network_latency": (SensorPreset.network_latency, "~25 ms, sine + uniform noise, clamped >= 1"),
    "heart_rate": (SensorPreset.heart_rate, "~72 BPM, sine + noise, clamped [30, 220]"),
    "accelerometer": (SensorPreset.accelerometer, "+/- 1 g, high-freq sine + noise"),
    "gps_coordinate": (SensorPreset.gps_coordinate, "wandering lat/lon, sine + Brownian noise"),
    "light_lux": (SensorPreset.light_lux, "~400 lux, slow cycle + noise, clamped >= 0"),
    "co2_ppm": (SensorPreset.co2_ppm, "~420 ppm, slow cycle + noise, clamped >= 200"),
    "wind_speed": (SensorPreset.wind_speed, "~12 m/s, sine + uniform noise, clamped >= 0"),
    "memory_usage": (SensorPreset.memory_usage, "0-100 %, sawtooth + noise"),
    "disk_io": (SensorPreset.disk_io, "MB/s pulse bursts + noise, clamped >= 0"),
    "flow_rate": (SensorPreset.flow_rate, "~50 l/min, sine + noise, clamped >= 0"),
    "vibration": (SensorPreset.vibration, "mm/s, high-freq sine + noise"),
    "ph_level": (SensorPreset.ph_level, "~7.0 pH, slow drift + noise, clamped [0, 14]"),
    "signal_strength": (SensorPreset.signal_strength, "-60 dBm, sine + noise, clamped [-120, 0]"),
}


# ------------------------------------------------------------------
# Argument parser
# ------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="faketelemetry",
        description="Generate realistic fake telemetry data from the command line.",
    )
    parser.add_argument("--version", action="version", version=f"faketelemetry {__version__}")
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # --- generate ---
    p_gen = sub.add_parser("generate", help="Generate data from a waveform")
    p_gen.add_argument(
        "--waveform",
        "-w",
        required=True,
        choices=[w.value for w in WaveformType if w != WaveformType.CUSTOM],
        help="Waveform type",
    )
    p_gen.add_argument("--freq", type=float, default=1.0, help="Frequency in Hz (default: 1.0)")
    p_gen.add_argument("--amp", type=float, default=1.0, help="Amplitude (default: 1.0)")
    p_gen.add_argument("--offset", type=float, default=0.0, help="Vertical offset (default: 0.0)")
    p_gen.add_argument(
        "--phase", type=float, default=0.0, help="Phase offset in radians (default: 0.0)"
    )
    p_gen.add_argument(
        "--duty-cycle", type=float, default=0.5, help="Duty cycle for square/pulse (default: 0.5)"
    )
    p_gen.add_argument(
        "--damping", type=float, default=0.0, help="Exponential damping coefficient (default: 0.0)"
    )
    p_gen.add_argument("--clamp-min", type=float, default=None, help="Minimum output clamp")
    p_gen.add_argument("--clamp-max", type=float, default=None, help="Maximum output clamp")
    _add_common_args(p_gen)

    # --- preset ---
    p_pre = sub.add_parser("preset", help="Generate data from a sensor preset")
    p_pre.add_argument("name", choices=list(_PRESETS.keys()), help="Preset name")
    _add_common_args(p_pre)

    # --- multi ---
    p_multi = sub.add_parser(
        "multi", help="Generate multi-channel data from comma-separated presets"
    )
    p_multi.add_argument(
        "presets", help="Comma-separated preset names (e.g. temperature,pressure,cpu_usage)"
    )
    _add_common_args(p_multi)

    # --- stream ---
    p_stream = sub.add_parser("stream", help="Stream data to stdout in real-time")
    p_stream_src = p_stream.add_mutually_exclusive_group(required=True)
    p_stream_src.add_argument("--preset", choices=list(_PRESETS.keys()), help="Preset name")
    p_stream_src.add_argument(
        "--waveform",
        "-w",
        choices=[w.value for w in WaveformType if w != WaveformType.CUSTOM],
        help="Waveform type",
    )
    p_stream.add_argument(
        "--rate", type=float, default=1.0, help="Sampling rate in Hz (default: 1.0)"
    )
    p_stream.add_argument(
        "--duration", type=float, default=None, help="Duration in seconds (default: infinite)"
    )
    p_stream.add_argument("--seed", type=int, default=None, help="Random seed")
    p_stream.add_argument(
        "--noise-level", type=float, default=0.0, help="Gaussian noise level (default: 0.0)"
    )

    # --- from-config ---
    p_cfg = sub.add_parser("from-config", help="Generate data from a saved JSON config file")
    p_cfg.add_argument("config_file", help="Path to JSON config file")
    _add_common_args(p_cfg)

    # --- list ---
    p_list = sub.add_parser(
        "list", help="List available presets, waveforms, noise types, or anomaly types"
    )
    p_list.add_argument(
        "category",
        choices=["presets", "waveforms", "noise", "anomalies"],
        help="What to list",
    )

    # --- describe ---
    p_desc = sub.add_parser("describe", help="Generate data and print summary statistics")
    p_desc_src = p_desc.add_mutually_exclusive_group(required=True)
    p_desc_src.add_argument("--preset", choices=list(_PRESETS.keys()), help="Preset name")
    p_desc_src.add_argument(
        "--waveform",
        "-w",
        choices=[w.value for w in WaveformType if w != WaveformType.CUSTOM],
        help="Waveform type",
    )
    p_desc.add_argument(
        "-n", "--samples", type=int, default=1000, help="Number of samples (default: 1000)"
    )
    p_desc.add_argument(
        "--rate", type=float, default=10.0, help="Sampling rate in Hz (default: 10.0)"
    )
    p_desc.add_argument("--seed", type=int, default=None, help="Random seed")

    return parser


def _add_common_args(p: argparse.ArgumentParser) -> None:
    """Add flags shared by generate / preset / multi / from-config."""
    p.add_argument("-n", "--samples", type=int, default=10, help="Number of samples (default: 10)")
    p.add_argument("--rate", type=float, default=1.0, help="Sampling rate in Hz (default: 1.0)")
    p.add_argument(
        "--format",
        "-f",
        choices=["table", "csv", "json", "ndjson", "influxdb"],
        default="table",
        help="Output format (default: table)",
    )
    p.add_argument("-o", "--output", default=None, help="Output file path (default: stdout)")
    p.add_argument("--seed", type=int, default=None, help="Random seed")
    p.add_argument(
        "--noise-level", type=float, default=0.0, help="Add Gaussian noise (default: 0.0)"
    )
    p.add_argument("--no-header", action="store_true", help="Omit header row in table/csv output")


# ------------------------------------------------------------------
# Subcommand handlers
# ------------------------------------------------------------------


def cmd_generate(args: argparse.Namespace) -> None:
    noise = _make_noise(args.noise_level, args.seed) if args.noise_level > 0 else None
    gen = TelemetryGenerator(
        waveform=WaveformType(args.waveform),
        frequency=args.freq,
        amplitude=args.amp,
        offset=args.offset,
        phase=args.phase,
        duty_cycle=args.duty_cycle,
        damping=args.damping,
        clamp_min=args.clamp_min,
        clamp_max=args.clamp_max,
        noise_injector=noise,
        seed=args.seed,
    )
    data = gen.batch(args.samples, args.rate)
    _output_single(data, args)


def cmd_preset(args: argparse.Namespace) -> None:
    factory, _ = _PRESETS[args.name]
    gen = factory(seed=args.seed)
    if args.noise_level > 0:
        gen.noise_injector = _make_noise(args.noise_level, args.seed)
    data = gen.batch(args.samples, args.rate)
    _output_single(data, args)


def cmd_multi(args: argparse.Namespace) -> None:
    names = [n.strip() for n in args.presets.split(",")]
    gens = {}
    for name in names:
        if name not in _PRESETS:
            _error(f"Unknown preset: {name!r}. Run 'faketelemetry list presets' to see options.")
        factory, _ = _PRESETS[name]
        gens[name] = factory(seed=args.seed)

    multi = MultiChannelTelemetryGenerator(gens)
    rows = multi.batch(args.samples, args.rate)
    _output_multi(rows, args)


def cmd_stream(args: argparse.Namespace) -> None:
    if args.preset:
        factory, _ = _PRESETS[args.preset]
        gen = factory(seed=args.seed)
    else:
        noise = _make_noise(args.noise_level, args.seed) if args.noise_level > 0 else None
        gen = TelemetryGenerator(
            waveform=WaveformType(args.waveform),
            noise_injector=noise,
            seed=args.seed,
        )

    try:
        for ts, val in gen.stream(sampling_rate=args.rate, duration=args.duration):
            print(f"{ts.isoformat()}  {val:.6f}")
            sys.stdout.flush()
    except KeyboardInterrupt:
        pass


def cmd_from_config(args: argparse.Namespace) -> None:
    try:
        with open(args.config_file, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        _error(f"Failed to load config: {exc}")

    gen = TelemetryGenerator.from_config(cfg)
    data = gen.batch(args.samples, args.rate)
    _output_single(data, args)


def cmd_list(args: argparse.Namespace) -> None:
    cat = args.category

    if cat == "presets":
        print("Available sensor presets:\n")
        for name, (_, desc) in _PRESETS.items():
            print(f"  {name:<22s} {desc}")

    elif cat == "waveforms":
        print("Available waveform types:\n")
        for w in WaveformType:
            if w == WaveformType.CUSTOM:
                continue
            print(f"  {w.value}")

    elif cat == "noise":
        print("Available noise types:\n")
        for n in NoiseType:
            print(f"  {n.value}")

    elif cat == "anomalies":
        print("Available anomaly types:\n")
        for a in AnomalyType:
            print(f"  {a.value}")


def cmd_describe(args: argparse.Namespace) -> None:
    if args.preset:
        factory, _ = _PRESETS[args.preset]
        gen = factory(seed=args.seed)
    else:
        gen = TelemetryGenerator(
            waveform=WaveformType(args.waveform),
            seed=args.seed,
        )

    data = gen.batch(args.samples, args.rate)
    stats = describe(data)

    label_width = max(len(k) for k in stats if k not in ("start", "end")) + 1
    for key, val in stats.items():
        if key in ("start", "end"):
            continue
        if isinstance(val, float):
            print(f"{key + ':':<{label_width}}  {val:>12.4f}")
        else:
            print(f"{key + ':':<{label_width}}  {val:>12}")


# ------------------------------------------------------------------
# Output helpers
# ------------------------------------------------------------------


def _output_single(data: List[Tuple[datetime, float]], args: argparse.Namespace) -> None:
    fmt = args.format
    text: Optional[str] = None

    if fmt == "table":
        text = _format_table(data, header=not args.no_header)
    elif fmt == "csv":
        text = to_csv(data)
        if args.no_header:
            text = "\n".join(text.split("\n")[1:])
    elif fmt == "json":
        text = to_json(data)
    elif fmt == "ndjson":
        text = to_ndjson(data)
    elif fmt == "influxdb":
        lines = to_influxdb(data, precision="ms")
        text = "\n".join(lines) + "\n"

    if text is None:
        return

    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)


def _output_multi(rows: List[Dict[str, Any]], args: argparse.Namespace) -> None:
    fmt = args.format
    text: Optional[str] = None

    if fmt == "table":
        text = _format_table_multi(rows, header=not args.no_header)
    elif fmt == "csv":
        text = to_multichannel_csv(rows)
        if args.no_header:
            text = "\n".join(text.split("\n")[1:])
    elif fmt == "json":
        text = json.dumps(rows, indent=2) + "\n"
    elif fmt == "ndjson":
        text = "\n".join(json.dumps(r) for r in rows) + "\n"
    elif fmt == "influxdb":
        lines = to_influxdb_multi(rows, precision="ms")
        text = "\n".join(lines) + "\n"

    if text is None:
        return

    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)


def _format_table(data: List[Tuple[datetime, float]], header: bool = True) -> str:
    lines: List[str] = []
    if header:
        lines.append(f"{'timestamp':<32s} {'value':>14s}")
    for ts, val in data:
        lines.append(f"{ts.isoformat():<32s} {val:>14.6f}")
    return "\n".join(lines) + "\n"


def _format_table_multi(rows: List[Dict[str, Any]], header: bool = True) -> str:
    if not rows:
        return ""
    keys = list(rows[0].keys())
    # Column widths: at least the key length, at least 14
    widths = {k: max(len(k), 14) for k in keys}
    widths["timestamp"] = max(widths.get("timestamp", 32), 32)

    lines: List[str] = []
    if header:
        hdr = "  ".join(f"{k:<{widths[k]}s}" for k in keys)
        lines.append(hdr)
    for row in rows:
        parts = []
        for k in keys:
            v = row[k]
            w = widths[k]
            if isinstance(v, float):
                parts.append(f"{v:>{w}.6f}")
            else:
                parts.append(f"{str(v):<{w}s}")
        lines.append("  ".join(parts))
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------
# Misc helpers
# ------------------------------------------------------------------


def _make_noise(level: float, seed: Optional[int]) -> NoiseInjector:
    return NoiseInjector(noise_level=level, seed=seed)


def _error(msg: str) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


# ------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        "generate": cmd_generate,
        "preset": cmd_preset,
        "multi": cmd_multi,
        "stream": cmd_stream,
        "from-config": cmd_from_config,
        "list": cmd_list,
        "describe": cmd_describe,
    }

    handler = dispatch.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
