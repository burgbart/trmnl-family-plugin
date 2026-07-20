"""Tests for the data fetcher aggregation."""

from __future__ import annotations

from src.data import Birthday, CalendarEvent, Task, Weather
from src.fetcher import fetch_all


def test_fetch_all_returns_expected_types() -> None:
    """fetch_all returns the four data structures in the correct order."""
    weather, events, tasks, birthdays = fetch_all()

    assert isinstance(weather, Weather)
    assert isinstance(events, list)
    assert isinstance(tasks, list)
    assert isinstance(birthdays, list)

    for event in events:
        assert isinstance(event, CalendarEvent)

    for task in tasks:
        assert isinstance(task, Task)

    for birthday in birthdays:
        assert isinstance(birthday, Birthday)
