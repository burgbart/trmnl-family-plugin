"""Long-running server for the TRMNL dashboard.

Runs a background refresh loop (collect → render → [upload]) on a configurable
interval, and optionally exposes the latest files over HTTP so a TRMNL device
can poll them directly.

Starts headless (logs refresh status to stderr). When stdin is an interactive
terminal, press 't' at any time to open the Rich terminal UI, and 'q' inside
it to return to headless logging (Ctrl+C always quits the server entirely).

Usage:
    python server.py                            # headless + HTTP on default port
    python server.py --port 9000                # custom HTTP port
    python server.py --no-http                  # headless without HTTP
    python server.py --interval 60              # refresh every minute
    python server.py --device og                # OG only
    python server.py                             # upload auto-enabled when R2 creds present
    python server.py --no-upload                 # disable upload even if R2 creds present
    python server.py --env /path/to/.env        # load a custom env file
"""

from __future__ import annotations

import argparse
import http.server
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from src.config import DASHBOARD_JSON_FILENAME


def _load_env_file(path: Path | None) -> None:
    if path is None:
        return
    if not path.exists():
        raise FileNotFoundError(f"Env file not found: {path}")
    load_dotenv(dotenv_path=path, override=True)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Long-running TRMNL dashboard server with background refresh."
    )
    parser.add_argument("--env", type=Path, default=None, help="Optional .env file to load.")
    parser.add_argument(
        "--no-http",
        action="store_true",
        dest="no_http",
        help="Disable the HTTP server.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="HTTP server port (default: SERVER_PORT or 8080).",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=None,
        help="Seconds between refresh cycles (default: REFRESH_INTERVAL_SECONDS or 600).",
    )
    parser.add_argument(
        "--device",
        choices=["og", "x", "both"],
        default=None,
        help="Device(s) to generate (default: SERVER_DEVICE or both).",
    )
    parser.add_argument(
        "--upload",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Upload dashboard-v2.json to Cloudflare R2 after each refresh. "
             "Defaults to on when R2 credentials are present.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output"),
        help="Directory to write dashboard-v2.json and preview.html (default: output).",
    )
    return parser.parse_args()


# Only these file names may be served over HTTP.
_ALLOWED_FILES = frozenset(["preview.html", DASHBOARD_JSON_FILENAME])


def _make_handler_class(output_dir: Path):
    """Return an HTTP handler class that serves allowed dashboard files."""

    class _Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            requested = self.path.lstrip("/") or "preview.html"
            if requested not in _ALLOWED_FILES:
                self.send_error(404, "Not found")
                return
            file_path = output_dir / requested
            if not file_path.is_file():
                self.send_error(404, "File not ready yet")
                return
            content = file_path.read_bytes()
            content_type = (
                "application/json" if requested.endswith(".json") else "text/html"
            )
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "max-age=0, must-revalidate")
            self.end_headers()
            self.wfile.write(content)

        def log_message(self, format, *args):  # noqa: A002
            pass  # suppress per-request log lines

    return _Handler


def _start_background_refresh(
    stop_event: threading.Event,
    output_dir: Path,
    devices: list[str],
    upload: bool,
    interval: int,
    on_refresh=None,
) -> threading.Thread:
    """Start a daemon thread that waits *interval* seconds, then runs the pipeline.

    *on_refresh(data, ts)* is called after each successful run. The thread
    loops until *stop_event* is set.
    """

    def _loop() -> None:
        # Wait before the first background refresh because the caller already
        # ran the initial refresh synchronously.
        while not stop_event.wait(interval):
            try:
                from src.pipeline import run_pipeline

                data = run_pipeline(output_dir, devices, upload=upload)
                ts = datetime.now(timezone.utc)
                if on_refresh is not None:
                    on_refresh(data, ts)
            except Exception as exc:
                print(f"[server] Refresh error: {exc}", file=sys.stderr)

    thread = threading.Thread(target=_loop, daemon=True)
    thread.start()
    return thread


def _run_initial_refresh(output_dir: Path, devices: list[str], upload: bool):
    """Run the first pipeline cycle synchronously and return (data, ts)."""
    from src.pipeline import run_pipeline

    print("Running initial refresh…", file=sys.stderr)
    data = run_pipeline(output_dir, devices, upload=upload)
    ts = datetime.now(timezone.utc)
    print(
        f"[{ts.strftime('%H:%M:%S')}] Ready"
        f" — {data.weather.temperature}°C {data.weather.description}",
        file=sys.stderr,
    )
    return data, ts


def _start_key_listener(
    stop_event: threading.Event,
    console,
    shared: dict,
    live_ref: list,
) -> "threading.Thread | None":
    """Watch stdin for 't' (open the terminal dashboard view) and 'q'.

    Runs only when stdin is a real interactive terminal; on a non-interactive
    stdin (e.g. a background/daemon deployment) this is a no-op and the server
    stays purely headless. Pressing 'q' while the terminal view is open
    returns to headless logging; pressing 'q' from headless quits the server.
    """
    if not sys.stdin.isatty():
        return None

    from readchar import readkey
    from rich.live import Live

    from src.terminal_dashboard import render

    def _loop() -> None:
        while not stop_event.is_set():
            try:
                key = readkey()
            except Exception:
                return
            if key.lower() == "q":
                stop_event.set()
                return
            if key.lower() == "t" and live_ref[0] is None:
                with Live(
                    render(shared["data"], console, last_refreshed=shared["ts"]),
                    console=console,
                    screen=True,
                    refresh_per_second=4,
                ) as live:
                    live_ref[0] = live
                    while not stop_event.is_set():
                        try:
                            inner_key = readkey()
                        except Exception:
                            break
                        if inner_key.lower() == "q":
                            break
                live_ref[0] = None
                print(
                    "Terminal view closed — press 't' to reopen, 'q' to quit.",
                    file=sys.stderr,
                )

    thread = threading.Thread(target=_loop, daemon=True)
    thread.start()
    return thread


def _run_server(
    output_dir: Path,
    devices: list[str],
    upload: bool,
    interval: int,
    port: int,
    no_http: bool,
) -> None:
    from rich.console import Console

    from src.terminal_dashboard import render
    from src.terminal_fetcher import TerminalData

    print(
        f"Server: interval={interval}s  devices={devices}"
        f"  upload={upload}  http={'disabled' if no_http else f':{port}'}",
        file=sys.stderr,
    )

    try:
        result, ts = _run_initial_refresh(output_dir, devices, upload)
    except Exception as exc:
        print(f"Initial refresh failed: {exc}", file=sys.stderr)
        return

    console = Console()
    stop_event = threading.Event()

    # Mutable shared state: refresh thread writes, key-listener thread reads.
    shared: dict = {
        "data": TerminalData(
            weather=result.weather,
            calendars=result.calendars,
            task_lists=result.task_lists,
            birthdays=result.birthdays,
            generated_at=ts,
        ),
        "ts": ts,
    }
    # live_ref[0] is set only while the terminal view is open.
    live_ref: list = [None]

    def _on_refresh(data, ts: datetime) -> None:
        shared["data"] = TerminalData(
            weather=data.weather,
            calendars=data.calendars,
            task_lists=data.task_lists,
            birthdays=data.birthdays,
            generated_at=ts,
        )
        shared["ts"] = ts
        if live_ref[0] is not None:
            live_ref[0].update(render(shared["data"], console, last_refreshed=ts))
        else:
            print(
                f"[{ts.strftime('%H:%M:%S')}] Refreshed"
                f" — {data.weather.temperature}°C {data.weather.description}",
                file=sys.stderr,
            )

    _start_background_refresh(stop_event, output_dir, devices, upload, interval, _on_refresh)

    httpd = None
    if not no_http:
        handler_class = _make_handler_class(output_dir)
        httpd = http.server.HTTPServer(("0.0.0.0", port), handler_class)
        http_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        http_thread.start()
        print(f"HTTP server listening on http://0.0.0.0:{port}", file=sys.stderr)

    if sys.stdin.isatty():
        print("Press 't' to open the terminal dashboard view, 'q' to quit.", file=sys.stderr)
    else:
        print("No interactive terminal detected — running headless. Ctrl+C to quit.", file=sys.stderr)

    _start_key_listener(stop_event, console, shared, live_ref)

    try:
        while not stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        if httpd is not None:
            httpd.shutdown()


def main() -> None:
    args = _parse_args()
    _load_env_file(args.env)

    from src.config import REFRESH_INTERVAL_SECONDS, SERVER_DEVICE, SERVER_PORT

    from src.config import r2_configured

    interval = args.interval if args.interval is not None else REFRESH_INTERVAL_SECONDS
    port = args.port if args.port is not None else SERVER_PORT
    device = args.device if args.device is not None else SERVER_DEVICE
    devices: list[str] = ["og", "x"] if device == "both" else [device]
    upload = args.upload if args.upload is not None else r2_configured()

    _run_server(args.output, devices, upload, interval, port, args.no_http)


if __name__ == "__main__":
    main()
