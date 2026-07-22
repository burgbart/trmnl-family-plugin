"""Tests for loading and parsing the unified dashboard JSON."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

from src.data import Birthday, CalendarEvent, Task, Weather
from src.json_loader import (
    load_json,
    parse_birthday,
    parse_calendar_source,
    parse_dashboard_data,
    parse_event,
    parse_task,
    parse_terminal_data,
    parse_weather,
    resolve_input_path,
)
from src.terminal_fetcher import CalendarSource, TaskListSource, TerminalData


def _make_sample_json() -> dict:
    today = date(2026, 7, 16)
    return {
        "meta": {
            "generated_at": "2026-07-16T09:15:00+00:00",
            "reference_date": today.isoformat(),
            "city": "Amsterdam",
        },
        "weather": {
            "description": "Partly cloudy",
            "temperature": 21,
            "feels_like": 19,
            "icon": "partly-cloudy",
        },
        "events": [
            {
                "title": "Dentist",
                "start": "2026-07-16T09:00:00+00:00",
                "end": "2026-07-16T10:00:00+00:00",
                "all_day": False,
                "attendees": ["anna@example.com"],
                "calendar_id": "cal@example.com",
            }
        ],
        "tasks": [
            {
                "title": "Buy milk",
                "done": False,
                "priority": 1,
                "due_date": today.isoformat(),
                "sort_order": 0,
            }
        ],
        "birthdays": [
            {
                "name": "Emma",
                "date": "2026-07-20",
                "kind": "birthday",
            }
        ],
        "calendars": [
            {
                "calendar_id": "cal@example.com",
                "name": "Main calendar",
                "events": [
                    {
                        "title": "Dentist",
                        "start": "2026-07-16T09:00:00+00:00",
                        "all_day": False,
                    }
                ],
            }
        ],
        "task_lists": [
            {
                "list_id": "list-1",
                "name": "Household",
                "tasks": [
                    {
                        "title": "Buy milk",
                        "done": False,
                    }
                ],
            }
        ],
    }


class TestParseWeather:
    def test_parses_weather(self):
        data = {"description": "Sunny", "temperature": 25, "feels_like": 23, "icon": "sun"}
        weather = parse_weather(data)
        assert isinstance(weather, Weather)
        assert weather.icon == "sun"
        assert weather.temperature == 25


class TestParseEvent:
    def test_parses_timed_event(self):
        data = {
            "title": "Meeting",
            "start": "2026-07-16T14:00:00+00:00",
            "end": "2026-07-16T15:00:00+00:00",
            "all_day": False,
            "attendees": ["bob@example.com"],
            "calendar_id": "cal@example.com",
        }
        event = parse_event(data)
        assert isinstance(event, CalendarEvent)
        assert event.title == "Meeting"
        assert event.start == datetime(2026, 7, 16, 14, 0, tzinfo=timezone.utc)
        assert event.end == datetime(2026, 7, 16, 15, 0, tzinfo=timezone.utc)
        assert event.attendees == ("bob@example.com",)

    def test_parses_all_day_event(self):
        data = {
            "title": "Holiday",
            "start": "2026-07-16T00:00:00+00:00",
            "end": "2026-07-17T00:00:00+00:00",
            "all_day": True,
        }
        event = parse_event(data)
        assert event.all_day is True
        assert event.end is not None

    def test_naive_datetime_defaults_to_utc(self):
        data = {"title": "Meeting", "start": "2026-07-16T14:00:00"}
        event = parse_event(data)
        assert event.start.tzinfo == timezone.utc


class TestParseTask:
    def test_parses_task(self):
        data = {"title": "Todo", "done": True, "priority": 2, "due_date": "2026-07-16", "sort_order": 5}
        task = parse_task(data)
        assert isinstance(task, Task)
        assert task.title == "Todo"
        assert task.done is True
        assert task.due_date == date(2026, 7, 16)

    def test_parses_task_with_defaults(self):
        data = {"title": "Simple"}
        task = parse_task(data)
        assert task.done is False
        assert task.priority == 0
        assert task.due_date is None


class TestParseBirthday:
    def test_parses_birthday(self):
        data = {"name": "Emma", "date": "2026-07-20", "kind": "birthday"}
        bday = parse_birthday(data)
        assert isinstance(bday, Birthday)
        assert bday.name == "Emma"
        assert bday.date == date(2026, 7, 20)
        assert bday.kind == "birthday"


class TestParseDashboardData:
    def test_parses_dashboard_data(self):
        weather, events, tasks, birthdays = parse_dashboard_data(_make_sample_json())
        assert isinstance(weather, Weather)
        assert len(events) == 1
        assert isinstance(events[0], CalendarEvent)
        assert len(tasks) == 1
        assert isinstance(tasks[0], Task)
        assert len(birthdays) == 1
        assert isinstance(birthdays[0], Birthday)


class TestParseTerminalData:
    def test_parses_terminal_data(self):
        data = parse_terminal_data(_make_sample_json())
        assert isinstance(data, TerminalData)
        assert isinstance(data.weather, Weather)
        assert len(data.calendars) == 1
        assert isinstance(data.calendars[0], CalendarSource)
        assert len(data.task_lists) == 1
        assert isinstance(data.task_lists[0], TaskListSource)
        assert len(data.birthdays) == 1


class TestLoadJson:
    def test_loads_local_json_file(self, tmp_path: Path):
        json_path = tmp_path / "dashboard-v2.json"
        sample = _make_sample_json()
        json_path.write_text(json.dumps(sample), encoding="utf-8")
        loaded = load_json(str(json_path))
        assert loaded["meta"]["city"] == "Amsterdam"


class TestResolveInputPath:
    def test_uses_cli_input(self):
        assert resolve_input_path("/tmp/data.json") == "/tmp/data.json"

    def test_defaults_to_local_file(self, monkeypatch):
        monkeypatch.delenv("DASHBOARD_JSON_URL", raising=False)
        monkeypatch.delenv("CLOUDFLARE_R2_PUBLIC_URL", raising=False)
        assert resolve_input_path() == "output/dashboard-v2.json"
