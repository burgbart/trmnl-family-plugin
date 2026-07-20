"""Collect unified dashboard data and output it as JSON.

This script fetches weather, calendar events, tasks, and anniversaries once and
serialises everything into a single JSON file. The JSON is intended to be
uploaded to Cloudflare R2 so that the PNG renderer and terminal dashboard can
read from it instead of fetching data themselves.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.serialization import build_dashboard_payload


def _load_env_file(path: Path | None) -> None:
    """Load a .env file before importing configuration modules."""
    if path is None:
        return
    if not path.exists():
        raise FileNotFoundError(f"Env file not found: {path}")
    load_dotenv(dotenv_path=path, override=True)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect unified dashboard data and emit it as JSON."
    )
    parser.add_argument(
        "--env",
        type=Path,
        default=None,
        help="Optional .env file to load before fetching data.",
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Collect data as if today were this date (DD-MM-YYYY).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional file to write JSON to. Defaults to stdout.",
    )
    return parser.parse_args()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect unified dashboard data and emit it as JSON."
    )
    parser.add_argument(
        "--env",
        type=Path,
        default=None,
        help="Optional .env file to load before fetching data.",
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Collect data as if today were this date (DD-MM-YYYY).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional file to write JSON to. Defaults to stdout.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    # Load custom env *before* any project module reads configuration.
    _load_env_file(args.env)

    # Import project modules only after env is set up.
    from src.config import CITY, get_reference_date, set_reference_date
    from src.unified_fetcher import fetch_unified_data

    if args.date:
        set_reference_date(args.date)

    # Keep stdout clean JSON: redirect fallback messages from fetchers to stderr.
    with contextlib.redirect_stdout(sys.stderr):
        data = fetch_unified_data()

    output = build_dashboard_payload(
        weather=data.weather,
        events=data.events,
        tasks=data.tasks,
        birthdays=data.birthdays,
        calendars=data.calendars,
        task_lists=data.task_lists,
        city=CITY,
        reference_date=get_reference_date(),
    )

    json_text = json.dumps(output, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json_text, encoding="utf-8")
        print(f"Wrote unified dashboard data to {args.output}")
    else:
        print(json_text)


if __name__ == "__main__":
    main()
