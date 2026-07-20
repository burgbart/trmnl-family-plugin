"""Tests for run_workflow_loop.py."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

import run_workflow_loop


class TestParseArgs:
    def test_defaults(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["run_workflow_loop.py"])
        args = run_workflow_loop._parse_args()
        assert args.device == "both"
        assert args.once is False
        assert args.upload is None  # auto-detect via r2_configured() in main()
        assert args.interval is None
        assert args.output == Path("output")
        assert args.env is None

    def test_once_flag(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["run_workflow_loop.py", "--once"])
        args = run_workflow_loop._parse_args()
        assert args.once is True

    def test_device_og(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["run_workflow_loop.py", "--device", "og"])
        args = run_workflow_loop._parse_args()
        assert args.device == "og"

    def test_upload_flag(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["run_workflow_loop.py", "--upload"])
        args = run_workflow_loop._parse_args()
        assert args.upload is True

    def test_interval(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["run_workflow_loop.py", "--interval", "120"])
        args = run_workflow_loop._parse_args()
        assert args.interval == 120


def test_run_once_calls_pipeline_and_prints(tmp_path: Path, capsys) -> None:
    """_run_once calls run_pipeline with the right arguments and prints a status line."""
    from src.data import Weather
    from src.terminal_fetcher import CalendarSource, TaskListSource
    from src.unified_fetcher import UnifiedData

    dummy = UnifiedData(
        weather=Weather(description="Sunny", temperature=22, feels_like=20, icon="sun"),
        events=[],
        tasks=[],
        birthdays=[],
        calendars=[CalendarSource("c1", "Cal", [])],
        task_lists=[TaskListSource("t1", "Tasks", [])],
    )

    with patch("src.pipeline.run_pipeline", return_value=dummy) as mock_pipeline:
        run_workflow_loop._run_once(tmp_path, ["og", "x"], upload=False)

    mock_pipeline.assert_called_once_with(tmp_path, ["og", "x"], upload=False)

    out = capsys.readouterr().out
    assert "22°C" in out
    assert "Sunny" in out


def test_main_once_exits_after_single_run(tmp_path: Path, monkeypatch) -> None:
    """main() with --once calls _run_once exactly once and returns."""
    monkeypatch.setattr(
        sys,
        "argv",
        ["run_workflow_loop.py", "--once", f"--output={tmp_path}"],
    )

    call_count = [0]

    def _fake_run_once(output_dir, devices, upload):
        call_count[0] += 1

    monkeypatch.setattr(run_workflow_loop, "_run_once", _fake_run_once)
    run_workflow_loop.main()

    assert call_count[0] == 1
