"""Data providers for the dashboard.

For Phase 2 this returns dummy data only.
Phase 3 will replace these with real API calls.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import List, Optional

from src.config import get_reference_date, get_reference_datetime


@dataclass
class WeatherForecast:
    date: date
    description: str
    temperature_high: int
    temperature_low: int
    icon: str


@dataclass
class Weather:
    description: str
    temperature: int
    feels_like: int
    icon: str
    forecast: list[WeatherForecast] = field(default_factory=list)
    alert: str | None = None


@dataclass
class CalendarEvent:
    title: str
    start: datetime
    end: datetime | None = None
    all_day: bool = False
    attendees: tuple[str, ...] = ()
    calendar_id: str | None = None


@dataclass
class Task:
    title: str
    done: bool = False
    priority: int = 0
    due_date: Optional[date] = None
    sort_order: int = 0


@dataclass
class Birthday:
    name: str
    date: date
    kind: str = "birthday"  # "birthday" or "anniversary"


def fetch_weather() -> Weather:
    """Dummy weather for Amsterdam."""
    today = get_reference_date()
    return Weather(
        description="Partly cloudy",
        temperature=21,
        feels_like=19,
        icon="partly-cloudy",
        forecast=[
            WeatherForecast(
                date=today,
                description="Rain",
                temperature_high=20,
                temperature_low=15,
                icon="rain",
            ),
            WeatherForecast(
                date=today + timedelta(days=1),
                description="Sunny",
                temperature_high=24,
                temperature_low=16,
                icon="sun",
            ),
            WeatherForecast(
                date=today + timedelta(days=2),
                description="Cloudy",
                temperature_high=22,
                temperature_low=17,
                icon="cloud",
            ),
        ],
        alert="Rain expected today",
    )


def fetch_calendar_events() -> List[CalendarEvent]:
    """Dummy household calendar events."""
    today = get_reference_datetime().replace(hour=0, minute=0, second=0, microsecond=0)
    return [
        CalendarEvent(
            title="Dentist — Anna",
            start=today + timedelta(hours=9),
            end=today + timedelta(hours=10),
        ),
        CalendarEvent(
            title="School pickup",
            start=today + timedelta(hours=15, minutes=30),
            end=today + timedelta(hours=16),
        ),
        CalendarEvent(
            title="Dinner at parents",
            start=today + timedelta(hours=18),
            end=today + timedelta(hours=21),
        ),
        CalendarEvent(
            title="Grocery run",
            start=today + timedelta(days=1, hours=10),
            end=today + timedelta(days=1, hours=11),
        ),
        CalendarEvent(
            title="Football practice",
            start=today + timedelta(days=2, hours=17),
            end=today + timedelta(days=2, hours=18, minutes=30),
        ),
        CalendarEvent(
            title="Piano lesson",
            start=today + timedelta(days=3, hours=16),
            end=today + timedelta(days=3, hours=17),
        ),
        CalendarEvent(
            title="Parent-teacher meeting",
            start=today + timedelta(days=4, hours=19),
            end=today + timedelta(days=4, hours=20),
        ),
        CalendarEvent(
            title="Swimming lessons",
            start=today + timedelta(days=5, hours=10),
            end=today + timedelta(days=5, hours=11),
        ),
        CalendarEvent(
            title="Family bike ride",
            start=today + timedelta(days=6, hours=11),
            end=today + timedelta(days=6, hours=13),
        ),
        CalendarEvent(
            title="Car maintenance",
            start=today + timedelta(days=7, hours=9),
            end=today + timedelta(days=7, hours=10),
        ),
    ]


def fetch_tasks() -> List[Task]:
    """Dummy TickTick tasks."""
    today = get_reference_date()
    return [
        Task(title="Buy milk & eggs", priority=1, due_date=today),
        Task(title="Call plumber", due_date=today),
        Task(title="Schedule car service", priority=1, due_date=today + timedelta(days=2)),
        Task(title="Water plants"),
        Task(title="Book weekend trip"),
    ]


def fetch_birthdays() -> List[Birthday]:
    """Dummy upcoming birthdays and anniversaries."""
    today = get_reference_date()
    return [
        Birthday(name="Emma", date=today + timedelta(days=3)),
        Birthday(name="Uncle Mark", date=today + timedelta(days=18)),
        Birthday(
            name="Wedding anniversary",
            date=today + timedelta(days=42),
            kind="anniversary",
        ),
        Birthday(name="Grandma Sue", date=today + timedelta(days=55)),
        Birthday(name="Dad", date=today + timedelta(days=63)),
        Birthday(
            name="First date anniversary",
            date=today + timedelta(days=76),
            kind="anniversary",
        ),
        Birthday(name="Cousin Lisa", date=today + timedelta(days=89)),
    ]
