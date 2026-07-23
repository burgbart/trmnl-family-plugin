"""Tests for the terminal dashboard."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from rich.console import Console
from rich.layout import Layout

from src.config import get_reference_date
from src.data import Birthday, CalendarEvent, Task, Weather, WeatherForecast
from src.terminal_dashboard import _allocate_rows, render
from src.terminal_fetcher import CalendarSource, TaskListSource, TerminalData, fetch_terminal_data


def _make_dt(day_offset: int = 0) -> datetime:
    return datetime.combine(
        get_reference_date() + timedelta(days=day_offset),
        datetime.min.time(),
    ).replace(tzinfo=timezone.utc)


class TestAllocateRows:
    def test_splits_evenly_when_demand_matches(self):
        assert _allocate_rows([5, 5], 10) == [5, 5]

    def test_gives_surplus_to_source_with_more_demand(self):
        # Source 0 only needs 2 rows; its unused share goes to source 1.
        assert _allocate_rows([2, 20], 10) == [2, 8]

    def test_handles_zero_total(self):
        assert _allocate_rows([3, 4], 0) == [0, 0]

    def test_handles_no_sources(self):
        assert _allocate_rows([], 10) == []


def _make_terminal_data() -> TerminalData:
    today = get_reference_date()
    return TerminalData(
        weather=Weather(
            description="Partly cloudy",
            temperature=21,
            feels_like=19,
            icon="partly-cloudy",
            forecast=[
                WeatherForecast(
                    date=today,
                    description="Sunny",
                    temperature_high=22,
                    temperature_low=15,
                    icon="sun",
                )
            ],
        ),
        events=[
            CalendarEvent(title="Aggregated Event A", start=_make_dt()),
            CalendarEvent(title="Aggregated Event B", start=_make_dt(1)),
        ],
        tasks=[
            Task(title="Aggregated Task A", due_date=today),
            Task(title="Aggregated Task B"),
        ],
        calendars=[
            CalendarSource(
                "cal-1",
                "Test Calendar",
                [
                    CalendarEvent(title="Event A", start=_make_dt()),
                    CalendarEvent(title="Event B", start=_make_dt(1)),
                ],
            )
        ],
        task_lists=[
            TaskListSource(
                "list-1",
                "Test Tasks",
                [
                    Task(title="Task A", due_date=today),
                    Task(title="Task B", done=True),
                ],
            )
        ],
        birthdays=[Birthday(name="Alice", date=today)],
    )


def test_render_returns_layout():
    data = _make_terminal_data()
    layout = render(data)
    assert isinstance(layout, Layout)


def test_render_with_empty_sources():
    data = TerminalData(
        weather=Weather(description="Clear", temperature=0, feels_like=0, icon="sun"),
        calendars=[CalendarSource("none", "No calendars", [])],
        task_lists=[TaskListSource("none", "No tasks", [])],
        birthdays=[],
    )
    layout = render(data)
    assert isinstance(layout, Layout)


def test_render_merges_multiple_calendars_and_task_lists():
    today = get_reference_date()
    data = TerminalData(
        weather=Weather(description="Clear", temperature=10, feels_like=9, icon="sun"),
        calendars=[
            CalendarSource("cal-1", "Work", [CalendarEvent(title="Standup", start=_make_dt())]),
            CalendarSource("cal-2", "Home", [CalendarEvent(title="Bins", start=_make_dt(1))]),
        ],
        task_lists=[
            TaskListSource("list-1", "Work Tasks", [Task(title="Ship it", due_date=today)]),
            TaskListSource("list-2", "Home Tasks", [Task(title="Fix sink")]),
        ],
        birthdays=[],
    )
    console = Console(width=100, height=40, record=True)
    layout = render(data, console)
    with console.capture() as capture:
        console.print(layout)
    rendered = capture.get()
    assert "Work" in rendered
    assert "Home" in rendered
    assert "Work Tasks" in rendered
    assert "Home Tasks" in rendered


def test_render_shows_weather_forecast():
    today = get_reference_date()
    data = TerminalData(
        weather=Weather(
            description="Clear",
            temperature=20,
            feels_like=19,
            icon="sun",
            forecast=[
                WeatherForecast(
                    date=today,
                    description="Sunny",
                    temperature_high=22,
                    temperature_low=15,
                    icon="sun",
                )
            ],
        ),
        calendars=[CalendarSource("none", "No calendars", [])],
        task_lists=[TaskListSource("none", "No tasks", [])],
        birthdays=[],
    )
    console = Console(width=100, height=40, record=True)
    layout = render(data, console)
    with console.capture() as capture:
        console.print(layout)
    rendered = capture.get()
    assert "Forecast" in rendered
    assert "Sunny" in rendered


def test_render_shows_aggregated_events_and_tasks():
    today = get_reference_date()
    data = TerminalData(
        weather=Weather(description="Clear", temperature=20, feels_like=19, icon="sun"),
        events=[CalendarEvent(title="Top Event", start=_make_dt())],
        tasks=[Task(title="Top Task", due_date=today)],
        calendars=[CalendarSource("cal-1", "Work", [])],
        task_lists=[TaskListSource("list-1", "Work Tasks", [])],
        birthdays=[],
    )
    console = Console(width=100, height=40, record=True)
    layout = render(data, console)
    with console.capture() as capture:
        console.print(layout)
    rendered = capture.get()
    assert "Upcoming Events" in rendered
    assert "Top Event" in rendered
    assert "Tasks" in rendered
    assert "Top Task" in rendered


def test_render_shows_weather_alert_in_header():
    data = TerminalData(
        weather=Weather(
            description="Rain",
            temperature=15,
            feels_like=13,
            icon="rain",
            alert="Rain expected today",
        ),
        calendars=[CalendarSource("none", "No calendars", [])],
        task_lists=[TaskListSource("none", "No tasks", [])],
        birthdays=[],
    )
    console = Console(width=100, height=40, record=True)
    layout = render(data, console)
    with console.capture() as capture:
        console.print(layout)
    rendered = capture.get()
    assert "Rain expected today" in rendered


def test_render_shows_anniversary_kind_in_footer():
    today = get_reference_date()
    data = TerminalData(
        weather=Weather(description="Clear", temperature=20, feels_like=19, icon="sun"),
        calendars=[CalendarSource("none", "No calendars", [])],
        task_lists=[TaskListSource("none", "No tasks", [])],
        birthdays=[
            Birthday(name="Alice", date=today + timedelta(days=5), kind="birthday"),
            Birthday(name="Wedding", date=today + timedelta(days=10), kind="anniversary"),
        ],
    )
    console = Console(width=100, height=40, record=True)
    layout = render(data, console)
    with console.capture() as capture:
        console.print(layout)
    rendered = capture.get()
    assert "birthday" in rendered
    assert "anniversary" in rendered


def test_render_shows_data_age():
    from src.terminal_dashboard import _build_header

    generated_at = datetime(2026, 7, 23, 10, 0, tzinfo=timezone.utc)
    last_refreshed = datetime(2026, 7, 23, 10, 5, tzinfo=timezone.utc)
    data = TerminalData(
        weather=Weather(description="Clear", temperature=20, feels_like=19, icon="sun"),
        calendars=[CalendarSource("none", "No calendars", [])],
        task_lists=[TaskListSource("none", "No tasks", [])],
        birthdays=[],
        generated_at=generated_at,
    )
    text = _build_header(data, last_refreshed=last_refreshed)
    assert "refreshed" in text.plain
    assert "data 5 min old" in text.plain


def test_fetch_terminal_data_returns_data(monkeypatch):
    """Smoke test that the fetcher returns a populated TerminalData object.

    Credentials are monkey-patched away so the dummy fallback path is exercised.
    """
    import src.terminal_fetcher as fetcher_module

    monkeypatch.setattr(fetcher_module, "TERMINAL_CALENDAR_IDS", [])
    monkeypatch.setattr(fetcher_module, "TERMINAL_TICKTICK_LIST_IDS", [])
    monkeypatch.setattr(fetcher_module, "GOOGLE_SERVICE_ACCOUNT_JSON", None)
    monkeypatch.setattr(fetcher_module, "TICKTICK_ACCESS_TOKEN", None)

    data = fetch_terminal_data()
    assert isinstance(data, TerminalData)
    assert data.weather is not None
    assert len(data.calendars) >= 1
    assert len(data.task_lists) >= 1


def test_event_when_for_multi_day_all_day_event():
    from src.terminal_dashboard import _event_when

    start = _make_dt()
    end = start + timedelta(days=3)
    event = CalendarEvent(title="Holiday", start=start, end=end, all_day=True)
    text = _event_when(event)
    # Multi-day events show the date span only, no "All day" label.
    assert "All day" not in text.plain
    assert "–" in text.plain


def test_event_when_for_single_day_all_day_event():
    from src.terminal_dashboard import _event_when

    start = _make_dt()
    end = start + timedelta(days=1)
    event = CalendarEvent(title="Holiday", start=start, end=end, all_day=True)
    text = _event_when(event)
    assert "All day" in text.plain
    assert "–" not in text.plain


def test_event_when_for_timed_event_with_end():
    from src.terminal_dashboard import _event_when

    start = _make_dt()
    end = start + timedelta(hours=2)
    event = CalendarEvent(title="Meeting", start=start, end=end, all_day=False)
    text = _event_when(event)
    assert "All day" not in text.plain
    assert "–" in text.plain


def test_event_when_converts_timed_event_to_local_timezone(monkeypatch):
    from src.terminal_dashboard import _event_when
    import src.config as config

    monkeypatch.setattr(config, "TIMEZONE", "US/Eastern")

    # 14:00 UTC = 10:00 EDT during July DST.
    start = datetime(2026, 7, 15, 14, 0, tzinfo=timezone.utc)
    end = start + timedelta(hours=1)
    event = CalendarEvent(title="Meeting", start=start, end=end, all_day=False)
    text = _event_when(event)
    assert "10:00–11:00" in text.plain


def test_footer_uses_red_for_days_within_7():
    from src.terminal_dashboard import _build_footer

    today = get_reference_date()
    bday = Birthday(name="Soon", date=today + timedelta(days=3), kind="anniversary")
    text = _build_footer([bday])

    label = "(anniversary · in 3d)"
    start = text.plain.find(label)
    assert start != -1
    span_styles = [
        span.style
        for span in text.spans
        if span.start <= start < span.end
    ]
    assert any("red" in str(style) for style in span_styles)


def test_footer_uses_dim_for_days_beyond_7():
    from src.terminal_dashboard import _build_footer

    today = get_reference_date()
    bday = Birthday(name="Far", date=today + timedelta(days=20), kind="birthday")
    text = _build_footer([bday])

    label = "(birthday · in 20d)"
    start = text.plain.find(label)
    assert start != -1
    span_styles = [
        span.style
        for span in text.spans
        if span.start <= start < span.end
    ]
    assert any("dim" in str(style) for style in span_styles)


def test_render_shows_error_panels_when_sources_failed():
    """When errors are present, the terminal dashboard renders error panels."""
    data = TerminalData(
        weather=Weather(description="Clear", temperature=0, feels_like=0, icon="sun"),
        calendars=[],
        task_lists=[],
        birthdays=[],
        errors={
            "events": "Calendar not configured",
            "tasks": "TickTick not configured",
            "birthdays": "Calendar not configured",
        },
    )
    console = Console(width=100, height=40, record=True)
    layout = render(data, console)
    with console.capture() as capture:
        console.print(layout)
    rendered = capture.get()
    assert "(!) Not loaded" in rendered
    assert "Calendar not configured" in rendered
    assert "TickTick not configured" in rendered
