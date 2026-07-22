"""JSON serialization helpers for dashboard dataclasses."""

from __future__ import annotations

import dataclasses
from datetime import date, datetime, timezone
from typing import Any


def serialise(value: Any) -> Any:
    """Recursively convert datetimes, dates, and dataclasses to JSON-safe types."""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return serialise(dataclasses.asdict(value))
    if isinstance(value, dict):
        return {k: serialise(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serialise(v) for v in value]
    return value


def build_dashboard_payload(
    weather: Any,
    events: list[Any],
    tasks: list[Any],
    birthdays: list[Any],
    calendars: list[Any],
    task_lists: list[Any],
    city: str,
    reference_date: date,
    generated_at: datetime | None = None,
    errors: dict[str, str | None] | None = None,
) -> dict[str, Any]:
    """Build the unified dashboard JSON payload from the fetched data."""
    return {
        "meta": {
            "generated_at": (generated_at or datetime.now(timezone.utc)).isoformat(),
            "reference_date": reference_date.isoformat(),
            "city": city,
        },
        "errors": errors or {"events": None, "tasks": None, "birthdays": None},
        "weather": serialise(weather),
        "events": [serialise(event) for event in events],
        "tasks": [serialise(task) for task in tasks],
        "birthdays": [serialise(birthday) for birthday in birthdays],
        "calendars": [serialise(calendar) for calendar in calendars],
        "task_lists": [serialise(task_list) for task_list in task_lists],
    }
