"""Interactive terminal dashboard.

Loads the unified dashboard JSON from a URL or local file and renders it as an
interactive terminal UI. The data refreshes automatically every
TERMINAL_REFRESH_INTERVAL_SECONDS (default 60 seconds) without interrupting
key handling or resetting the selected tab.

Usage:
    python terminal_dashboard.py
    python terminal_dashboard.py --input https://example.com/dashboard-v2.json
    python terminal_dashboard.py --input output/dashboard-v2.json
    python terminal_dashboard.py --env /path/to/.env.terminal
    python terminal_dashboard.py --date 23-12-2026

Controls:
    q    quit
"""

from __future__ import annotations

import argparse
import threading
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv


def _load_env_file(path: Path | None) -> None:
    if path is None:
        return
    if not path.exists():
        raise FileNotFoundError(f"Env file not found: {path}")
    load_dotenv(dotenv_path=path, override=True)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Interactive terminal dashboard for weather, calendar, and tasks. "
            "Reads a unified JSON file and auto-refreshes on a configurable interval."
        )
    )
    parser.add_argument(
        "--input",
        default=None,
        help="URL or path to the unified dashboard JSON. Defaults to DASHBOARD_JSON_URL or Cloudflare.",
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
        help="Render as if this date (DD-MM-YYYY). Defaults to today.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    _load_env_file(args.env)

    # Import project modules only after env is configured.
    from readchar import readkey
    from rich.console import Console
    from rich.live import Live

    from src.config import TERMINAL_REFRESH_INTERVAL_SECONDS, set_reference_date
    from src.json_loader import load_json, parse_terminal_data, resolve_input_path
    from src.terminal_dashboard import render

    if args.date:
        set_reference_date(args.date)

    input_path = resolve_input_path(args.input)
    data = parse_terminal_data(load_json(input_path))
    last_refreshed = datetime.now(timezone.utc)
    console = Console()
    stop_event = threading.Event()

    def _refresh_loop(live: Live) -> None:
        nonlocal data, last_refreshed
        # wait() returns True when the event is set (stop requested).
        while not stop_event.wait(TERMINAL_REFRESH_INTERVAL_SECONDS):
            try:
                data = parse_terminal_data(load_json(input_path))
                last_refreshed = datetime.now(timezone.utc)
            except Exception:
                pass
            live.update(render(data, console, last_refreshed=last_refreshed))

    try:
        with Live(
            render(data, console, last_refreshed=last_refreshed),
            console=console,
            screen=True,
            refresh_per_second=4,
        ) as live:
            refresh_thread = threading.Thread(
                target=_refresh_loop, args=(live,), daemon=True
            )
            refresh_thread.start()

            while True:
                key = readkey()
                if key.lower() == "q":
                    break
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()


if __name__ == "__main__":
    main()
