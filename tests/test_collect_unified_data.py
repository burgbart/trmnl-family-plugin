"""Tests for the unified data collector (collect_unified_data.py)."""

from __future__ import annotations

from datetime import date, datetime

from src.data import Birthday, CalendarEvent, Task, Weather
from src.serialization import build_dashboard_payload
from src.terminal_fetcher import CalendarSource, TaskListSource


def _make_payload() -> dict:
    """Build a dashboard payload with representative data."""
    weather = Weather(description="Sunny", temperature=22, feels_like=20, icon="sun")
    events = [
        CalendarEvent(
            title="Dentist",
            start=datetime(2026, 7, 16, 9, 0),
            end=datetime(2026, 7, 16, 10, 0),
        )
    ]
    tasks = [Task(title="Buy milk", done=False)]
    birthdays = [Birthday(name="Emma", date=date(2026, 7, 20))]
    calendars = [CalendarSource("cal-1", "Family", events)]
    task_lists = [TaskListSource("list-1", "Shared", tasks)]

    return build_dashboard_payload(
        weather=weather,
        events=events,
        tasks=tasks,
        birthdays=birthdays,
        calendars=calendars,
        task_lists=task_lists,
        city="Amsterdam",
        reference_date=date(2026, 7, 16),
    )


def test_unified_output_structure():
    output = _make_payload()

    for key in ("meta", "errors", "weather", "events", "tasks", "birthdays", "calendars", "task_lists"):
        assert key in output, f"Missing key: {key}"

    assert output["errors"] == {"events": None, "tasks": None, "birthdays": None}

    assert output["meta"]["city"] == "Amsterdam"
    assert output["meta"]["reference_date"] == "2026-07-16"
    assert output["weather"]["temperature"] == 22

    assert len(output["calendars"]) == 1
    assert output["calendars"][0]["calendar_id"] == "cal-1"
    assert len(output["calendars"][0]["events"]) == 1
    assert output["calendars"][0]["events"][0]["title"] == "Dentist"

    assert len(output["task_lists"]) == 1
    assert output["task_lists"][0]["list_id"] == "list-1"
    assert len(output["task_lists"][0]["tasks"]) == 1
    assert output["task_lists"][0]["tasks"][0]["title"] == "Buy milk"

    assert len(output["birthdays"]) == 1
    assert output["birthdays"][0]["name"] == "Emma"


def test_unified_output_serialises_datetimes():
    output = _make_payload()

    # Aggregated events list (for the PNG renderer).
    event = output["events"][0]
    assert event["start"] == "2026-07-16T09:00:00"
    assert event["end"] == "2026-07-16T10:00:00"

    # Per-calendar events (for the terminal dashboard).
    cal_event = output["calendars"][0]["events"][0]
    assert cal_event["start"] == "2026-07-16T09:00:00"


def test_unified_output_birthdays_have_kind_field():
    output = _make_payload()

    bday = output["birthdays"][0]
    assert bday["kind"] == "birthday"
    assert bday["date"] == "2026-07-20"


def test_unified_output_includes_source_errors():
    """Errors for individual sources are serialised into the payload."""
    weather = Weather(description="Sunny", temperature=22, feels_like=20, icon="sun")
    output = build_dashboard_payload(
        weather=weather,
        events=[],
        tasks=[],
        birthdays=[],
        calendars=[],
        task_lists=[],
        city="Amsterdam",
        reference_date=date(2026, 7, 16),
        errors={"events": "Calendar not configured", "tasks": None, "birthdays": "Calendar not configured"},
    )

    assert output["errors"]["events"] == "Calendar not configured"
    assert output["errors"]["tasks"] is None
    assert output["errors"]["birthdays"] == "Calendar not configured"
