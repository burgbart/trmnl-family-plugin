"""Tests for server.py."""

from __future__ import annotations

import http.server
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import patch

import pytest

import server


# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------


def _start_test_server(output_dir: Path) -> tuple[http.server.HTTPServer, int]:
    """Start a test HTTP server on a random port. Caller must shut it down."""
    handler = server._make_handler_class(output_dir)
    httpd = http.server.HTTPServer(("127.0.0.1", 0), handler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd, port


class TestHttpHandler:
    def test_serves_preview_html_with_correct_headers(self, tmp_path: Path) -> None:
        (tmp_path / "preview.html").write_bytes(b"<html>preview</html>")
        httpd, port = _start_test_server(tmp_path)
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/preview.html"
            ) as resp:
                assert resp.read() == b"<html>preview</html>"
                assert resp.headers["Cache-Control"] == "max-age=0, must-revalidate"
                assert "html" in resp.headers["Content-Type"]
        finally:
            httpd.shutdown()

    def test_serves_json_with_json_content_type(self, tmp_path: Path) -> None:
        (tmp_path / "dashboard.json").write_bytes(b'{"meta":{}}')
        httpd, port = _start_test_server(tmp_path)
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/dashboard.json"
            ) as resp:
                body = resp.read()
                assert b"meta" in body
                assert "json" in resp.headers["Content-Type"]
        finally:
            httpd.shutdown()

    def test_root_path_serves_preview_html(self, tmp_path: Path) -> None:
        (tmp_path / "preview.html").write_bytes(b"<html>root</html>")
        httpd, port = _start_test_server(tmp_path)
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/") as resp:
                assert resp.read() == b"<html>root</html>"
        finally:
            httpd.shutdown()

    def test_404_for_unknown_path(self, tmp_path: Path) -> None:
        httpd, port = _start_test_server(tmp_path)
        try:
            with pytest.raises(urllib.error.HTTPError) as exc_info:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/etc/passwd")
            assert exc_info.value.code == 404
        finally:
            httpd.shutdown()

    def test_404_when_file_not_yet_generated(self, tmp_path: Path) -> None:
        # output_dir exists but preview.html has not been rendered yet.
        httpd, port = _start_test_server(tmp_path)
        try:
            with pytest.raises(urllib.error.HTTPError) as exc_info:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/preview.html")
            assert exc_info.value.code == 404
        finally:
            httpd.shutdown()


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------


class TestParseArgs:
    def test_defaults(self, monkeypatch) -> None:
        monkeypatch.setattr(sys, "argv", ["server.py"])
        args = server._parse_args()
        assert args.no_http is False
        assert args.port is None
        assert args.interval is None
        assert args.device is None
        assert args.upload is None  # auto-detect via r2_configured() in main()
        assert args.output == Path("output")

    def test_no_http_flag(self, monkeypatch) -> None:
        monkeypatch.setattr(sys, "argv", ["server.py", "--no-http"])
        args = server._parse_args()
        assert args.no_http is True

    def test_port(self, monkeypatch) -> None:
        monkeypatch.setattr(sys, "argv", ["server.py", "--port", "9000"])
        args = server._parse_args()
        assert args.port == 9000

    def test_interval(self, monkeypatch) -> None:
        monkeypatch.setattr(sys, "argv", ["server.py", "--interval", "300"])
        args = server._parse_args()
        assert args.interval == 300


# ---------------------------------------------------------------------------
# Background refresh thread
# ---------------------------------------------------------------------------


def test_background_refresh_calls_pipeline_and_stops(tmp_path: Path) -> None:
    """The background thread runs the pipeline and stops when the event is set."""
    from src.data import Weather
    from src.terminal_fetcher import CalendarSource, TaskListSource
    from src.unified_fetcher import UnifiedData

    dummy = UnifiedData(
        weather=Weather(description="Clear", temperature=20, feels_like=18, icon="sun"),
        events=[],
        tasks=[],
        birthdays=[],
        calendars=[CalendarSource("c1", "Cal", [])],
        task_lists=[TaskListSource("t1", "Tasks", [])],
    )

    refresh_calls: list = []
    stop_event = threading.Event()

    def _on_refresh(data, ts):
        refresh_calls.append(ts)
        stop_event.set()  # Stop after the first successful refresh.

    with patch("src.pipeline.run_pipeline", return_value=dummy):
        thread = server._start_background_refresh(
            stop_event=stop_event,
            output_dir=tmp_path,
            devices=["og"],
            upload=False,
            interval=1,  # 1-second interval; the thread waits before its first run.
            on_refresh=_on_refresh,
        )
        thread.join(timeout=3.0)

    assert len(refresh_calls) == 1
    assert not thread.is_alive()
