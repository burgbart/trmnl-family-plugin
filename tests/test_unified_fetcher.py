"""Tests for src/unified_fetcher.py."""

from __future__ import annotations

from unittest.mock import patch

from src.data import Weather
from src.unified_fetcher import UnifiedData, fetch_unified_data


def _dummy_weather() -> Weather:
    return Weather(description="Clear", temperature=20, feels_like=18, icon="sun")


def _make_unified_data(**overrides) -> UnifiedData:
    defaults = {
        "weather": _dummy_weather(),
        "events": [],
        "tasks": [],
        "birthdays": [],
        "calendars": [],
        "task_lists": [],
        "errors": {"events": None, "tasks": None, "birthdays": None},
    }
    defaults.update(overrides)
    return UnifiedData(**defaults)


def test_missing_calendar_credentials_records_errors_and_empty_data(monkeypatch):
    """When Google Calendar credentials are missing, events/birthdays are empty and errors are set."""
    monkeypatch.setattr("src.unified_fetcher.GOOGLE_SERVICE_ACCOUNT_JSON", "")
    monkeypatch.setattr("src.unified_fetcher.GOOGLE_CALENDAR_IDS", [])
    monkeypatch.setattr("src.unified_fetcher.TERMINAL_CALENDAR_IDS", [])
    monkeypatch.setattr("src.unified_fetcher.TICKTICK_ACCESS_TOKEN", "")
    monkeypatch.setattr("src.unified_fetcher.TICKTICK_LIST_ID", "")
    monkeypatch.setattr("src.unified_fetcher.TERMINAL_TICKTICK_LIST_IDS", [])

    with patch("src.unified_fetcher.fetch_weather_or_dummy") as mock_weather:
        mock_weather.return_value = _dummy_weather()
        data = fetch_unified_data()

    assert data.events == []
    assert data.birthdays == []
    assert data.calendars == []
    assert data.errors["events"] is not None
    assert "GOOGLE_SERVICE_ACCOUNT_JSON" in data.errors["events"]
    assert data.errors["birthdays"] == data.errors["events"]


def test_missing_task_credentials_records_error_and_empty_data(monkeypatch):
    """When TickTick credentials are missing, tasks are empty and the error is set."""
    monkeypatch.setattr("src.unified_fetcher.GOOGLE_SERVICE_ACCOUNT_JSON", "")
    monkeypatch.setattr("src.unified_fetcher.GOOGLE_CALENDAR_IDS", [])
    monkeypatch.setattr("src.unified_fetcher.TERMINAL_CALENDAR_IDS", [])
    monkeypatch.setattr("src.unified_fetcher.TICKTICK_ACCESS_TOKEN", "")
    monkeypatch.setattr("src.unified_fetcher.TICKTICK_LIST_ID", "")
    monkeypatch.setattr("src.unified_fetcher.TERMINAL_TICKTICK_LIST_IDS", [])

    with patch("src.unified_fetcher.fetch_weather_or_dummy") as mock_weather:
        mock_weather.return_value = _dummy_weather()
        data = fetch_unified_data()

    assert data.tasks == []
    assert data.task_lists == []
    assert data.errors["tasks"] is not None
    assert "TICKTICK_ACCESS_TOKEN" in data.errors["tasks"]


def test_calendar_api_failure_records_error_and_empty_data(monkeypatch):
    """When credentials are present but the calendar API fails, errors are set."""
    monkeypatch.setattr("src.unified_fetcher.GOOGLE_SERVICE_ACCOUNT_JSON", "{}")
    monkeypatch.setattr("src.unified_fetcher.GOOGLE_CALENDAR_IDS", ["cal@example.com"])
    monkeypatch.setattr("src.unified_fetcher.TERMINAL_CALENDAR_IDS", [])
    monkeypatch.setattr("src.unified_fetcher.TICKTICK_ACCESS_TOKEN", "")
    monkeypatch.setattr("src.unified_fetcher.TICKTICK_LIST_ID", "")
    monkeypatch.setattr("src.unified_fetcher.TERMINAL_TICKTICK_LIST_IDS", [])

    with (
        patch("src.unified_fetcher.fetch_weather_or_dummy") as mock_weather,
        patch("src.unified_fetcher._fetch_events_for_ids") as mock_events,
    ):
        mock_weather.return_value = _dummy_weather()
        mock_events.side_effect = RuntimeError("API unreachable")
        data = fetch_unified_data()

    assert data.events == []
    assert data.birthdays == []
    assert data.errors["events"] == "API unreachable"
    assert data.errors["birthdays"] == "API unreachable"
