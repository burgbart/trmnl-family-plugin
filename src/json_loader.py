"""Load dashboard JSON from a URL or local file and parse it into dataclasses.

The dashboard PNG renderer and terminal dashboard both consume the same unified
JSON file. This module handles fetching (HTTP/HTTPS) or reading (local path) and
deserialising the JSON into the project's dataclasses.
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

from src.config import DASHBOARD_JSON_URL
from src.data import Birthday, CalendarEvent, Task, Weather
from src.terminal_fetcher import CalendarSource, TaskListSource, TerminalData


def _parse_datetime(value: str | None) -> datetime | None:
    """Parse an ISO datetime string, defaulting missing tzinfo to UTC."""
    if value is None:
        return None
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _parse_date(value: str | None) -> date | None:
    """Parse an ISO date string."""
    if value is None:
        return None
    return date.fromisoformat(value)


def load_json(path_or_url: str | None = None) -> dict:
    """Load dashboard JSON from a URL or local file path.

    Args:
        path_or_url: URL or local path. If omitted, resolves via
            ``resolve_input_path``.

    Returns:
        The parsed JSON object.
    """
    path_or_url = path_or_url or resolve_input_path()
    parsed = urlparse(path_or_url)

    if parsed.scheme in ("http", "https"):
        response = requests.get(path_or_url, timeout=30)
        response.raise_for_status()
        return response.json()

    return json.loads(Path(path_or_url).read_text(encoding="utf-8"))


def resolve_input_path(cli_input: str | None = None) -> str:
    """Resolve the dashboard JSON location.

    Resolution order:
    1. Explicit ``cli_input`` argument.
    2. ``DASHBOARD_JSON_URL`` environment variable.
    3. ``CLOUDFLARE_R2_PUBLIC_URL`` + ``/dashboard.json``.
    4. Local ``output/dashboard.json`` fallback for local development.
    """
    if cli_input:
        return cli_input
    if DASHBOARD_JSON_URL:
        return DASHBOARD_JSON_URL
    public_url_base = os.getenv("CLOUDFLARE_R2_PUBLIC_URL", "").rstrip("/")
    if public_url_base:
        return f"{public_url_base}/dashboard.json"
    return "output/dashboard.json"


def parse_weather(data: dict) -> Weather:
    """Parse a weather dictionary into a ``Weather`` dataclass."""
    return Weather(
        description=data["description"],
        temperature=int(data["temperature"]),
        feels_like=int(data["feels_like"]),
        icon=data["icon"],
    )


def parse_event(data: dict) -> CalendarEvent:
    """Parse an event dictionary into a ``CalendarEvent`` dataclass."""
    return CalendarEvent(
        title=data["title"],
        start=_parse_datetime(data["start"]),
        end=_parse_datetime(data.get("end")),
        all_day=data.get("all_day", False),
        attendees=tuple(data.get("attendees", [])),
        calendar_id=data.get("calendar_id"),
    )


def parse_task(data: dict) -> Task:
    """Parse a task dictionary into a ``Task`` dataclass."""
    return Task(
        title=data["title"],
        done=data.get("done", False),
        priority=data.get("priority", 0),
        due_date=_parse_date(data.get("due_date")),
        sort_order=data.get("sort_order", 0),
    )


def parse_birthday(data: dict) -> Birthday:
    """Parse a birthday/anniversary dictionary into a ``Birthday`` dataclass."""
    return Birthday(
        name=data["name"],
        date=_parse_date(data["date"]),
        kind=data.get("kind", "birthday"),
    )


def parse_dashboard_data(data: dict) -> tuple[Weather, list[CalendarEvent], list[Task], list[Birthday]]:
    """Parse the aggregated data needed by the PNG renderer."""
    weather = parse_weather(data["weather"])
    events = [parse_event(event) for event in data.get("events", [])]
    tasks = [parse_task(task) for task in data.get("tasks", [])]
    birthdays = [parse_birthday(bday) for bday in data.get("birthdays", [])]
    return weather, events, tasks, birthdays


def parse_generated_at(data: dict) -> datetime | None:
    """Parse the collection timestamp from the JSON payload's meta block."""
    return _parse_datetime(data.get("meta", {}).get("generated_at"))


def parse_calendar_source(data: dict) -> CalendarSource:
    """Parse a calendar source dictionary for the terminal dashboard."""
    return CalendarSource(
        calendar_id=data["calendar_id"],
        name=data["name"],
        events=[parse_event(event) for event in data.get("events", [])],
    )


def parse_task_list_source(data: dict) -> TaskListSource:
    """Parse a task-list source dictionary for the terminal dashboard."""
    return TaskListSource(
        list_id=data["list_id"],
        name=data["name"],
        tasks=[parse_task(task) for task in data.get("tasks", [])],
    )


def parse_terminal_data(data: dict) -> TerminalData:
    """Parse the full data needed by the terminal dashboard."""
    weather = parse_weather(data["weather"])
    calendars = [parse_calendar_source(source) for source in data.get("calendars", [])]
    task_lists = [parse_task_list_source(source) for source in data.get("task_lists", [])]
    birthdays = [parse_birthday(bday) for bday in data.get("birthdays", [])]
    generated_at = _parse_datetime(data.get("meta", {}).get("generated_at"))
    return TerminalData(
        weather=weather,
        calendars=calendars,
        task_lists=task_lists,
        birthdays=birthdays,
        generated_at=generated_at,
    )
