"""Tests for src/pipeline.py."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from src.data import Weather
from src.terminal_fetcher import CalendarSource, TaskListSource
from src.unified_fetcher import UnifiedData


def _dummy_unified_data() -> UnifiedData:
    return UnifiedData(
        weather=Weather(description="Clear", temperature=20, feels_like=18, icon="sun"),
        events=[],
        tasks=[],
        birthdays=[],
        calendars=[CalendarSource("c1", "Cal", [])],
        task_lists=[TaskListSource("t1", "Tasks", [])],
    )


def test_run_pipeline_writes_json(tmp_path: Path) -> None:
    """run_pipeline writes dashboard-v2.json with the expected top-level keys."""
    dummy = _dummy_unified_data()
    with (
        patch("src.unified_fetcher.fetch_unified_data", return_value=dummy),
        patch("export_preview.build_preview_html", return_value="<html></html>"),
    ):
        from src.pipeline import run_pipeline

        run_pipeline(tmp_path, ["og"], upload=False)

    json_path = tmp_path / "dashboard-v2.json"
    assert json_path.exists()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert "meta" in data
    assert "weather" in data
    assert data["weather"]["temperature"] == 20


def test_run_pipeline_writes_preview_html(tmp_path: Path) -> None:
    """run_pipeline renders preview.html via export_preview.build_preview_html."""
    dummy = _dummy_unified_data()
    with (
        patch("src.unified_fetcher.fetch_unified_data", return_value=dummy),
        patch(
            "export_preview.build_preview_html", return_value="<html>preview</html>"
        ) as mock_build,
    ):
        from src.pipeline import run_pipeline

        run_pipeline(tmp_path, ["og", "x"], upload=False)

    mock_build.assert_called_once()
    args, kwargs = mock_build.call_args
    assert kwargs.get("device_names") == ["og", "x"] or args[1] == ["og", "x"]

    preview_path = tmp_path / "preview.html"
    assert preview_path.exists()
    assert preview_path.read_text(encoding="utf-8") == "<html>preview</html>"


def test_run_pipeline_returns_unified_data(tmp_path: Path) -> None:
    """run_pipeline returns the UnifiedData object from the current run."""
    dummy = _dummy_unified_data()
    with (
        patch("src.unified_fetcher.fetch_unified_data", return_value=dummy),
        patch("export_preview.build_preview_html", return_value="<html></html>"),
    ):
        from src.pipeline import run_pipeline

        result = run_pipeline(tmp_path, ["og"], upload=False)

    assert result is dummy


def test_run_pipeline_creates_output_dir(tmp_path: Path) -> None:
    """run_pipeline creates the output directory if it does not exist."""
    dummy = _dummy_unified_data()
    nested = tmp_path / "a" / "b" / "c"
    with (
        patch("src.unified_fetcher.fetch_unified_data", return_value=dummy),
        patch("export_preview.build_preview_html", return_value="<html></html>"),
    ):
        from src.pipeline import run_pipeline

        run_pipeline(nested, ["og"], upload=False)

    assert nested.is_dir()
    assert (nested / "dashboard-v2.json").exists()
    assert (nested / "preview.html").exists()


def test_run_pipeline_calls_upload_when_requested(tmp_path: Path) -> None:
    """run_pipeline uploads dashboard-v2.json (only) when upload=True."""
    dummy = _dummy_unified_data()
    with (
        patch("src.unified_fetcher.fetch_unified_data", return_value=dummy),
        patch("export_preview.build_preview_html", return_value="<html></html>"),
        patch("src.upload.upload_json") as mock_upload_json,
    ):
        from src.pipeline import run_pipeline

        run_pipeline(tmp_path, ["og"], upload=True)

    mock_upload_json.assert_called_once()
