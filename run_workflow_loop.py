"""Run the collect → render → [upload] loop locally.

Mimics the generate-dashboard.yml workflow on a local machine. Runs
``src.pipeline.run_pipeline`` on a configurable interval: collect unified data,
write ``dashboard-v2.json``, render the static Liquid ``preview.html``, and
optionally upload the JSON to Cloudflare R2. Loops until Ctrl+C or SIGTERM;
use ``--once`` for a single run.

Usage:
    python run_workflow_loop.py                         # loop every 60 s, both devices
    python run_workflow_loop.py --once                  # single run and exit
    python run_workflow_loop.py --interval 300          # loop every 5 minutes
    python run_workflow_loop.py --device og             # OG only
    python run_workflow_loop.py                         # upload auto-enabled when R2 creds present
    python run_workflow_loop.py --no-upload             # disable upload even if R2 creds present
    python run_workflow_loop.py --output /tmp/dash      # custom output directory
    python run_workflow_loop.py --env /path/to/.env     # load a custom env file
"""

from __future__ import annotations

import argparse
import sys
import time
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
        description="Collect data, render preview.html, and optionally upload to Cloudflare R2."
    )
    parser.add_argument("--env", type=Path, default=None, help="Optional .env file to load.")
    parser.add_argument(
        "--interval",
        type=int,
        default=None,
        help="Seconds between refresh cycles (default: REFRESH_INTERVAL_SECONDS or 600).",
    )
    parser.add_argument(
        "--device",
        choices=["og", "x", "both"],
        default="both",
        help="Which device dashboard to generate (default: both).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output"),
        help="Directory to write dashboard-v2.json and preview.html (default: output).",
    )
    parser.add_argument(
        "--upload",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Upload dashboard-v2.json to Cloudflare R2 after each render. "
             "Defaults to on when R2 credentials are present.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single iteration and exit (useful for external schedulers).",
    )
    return parser.parse_args()


def _run_once(output_dir: Path, devices: list[str], upload: bool) -> None:
    from src.pipeline import run_pipeline

    started = datetime.now(timezone.utc)
    data = run_pipeline(output_dir, devices, upload=upload)
    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    ts = started.strftime("%H:%M:%S")
    print(
        f"[{ts}] Refreshed in {elapsed:.1f}s"
        f" — {data.weather.temperature}°C {data.weather.description}"
    )


def main() -> None:
    args = _parse_args()
    _load_env_file(args.env)

    from src.config import REFRESH_INTERVAL_SECONDS
    from src.config import r2_configured

    interval = args.interval if args.interval is not None else REFRESH_INTERVAL_SECONDS
    devices: list[str] = ["og", "x"] if args.device == "both" else [args.device]
    upload = args.upload if args.upload is not None else r2_configured()

    if args.once:
        _run_once(args.output, devices, upload)
        return

    print(
        f"Starting loop: interval={interval}s  devices={devices}  upload={upload}"
        "  (Ctrl+C to stop)"
    )
    while True:
        try:
            _run_once(args.output, devices, upload)
        except Exception as exc:
            print(f"Error in refresh cycle: {exc}", file=sys.stderr)
        time.sleep(interval)


if __name__ == "__main__":
    main()
