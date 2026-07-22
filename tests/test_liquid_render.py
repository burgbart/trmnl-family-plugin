"""Tests for src/liquid_render.py and error-state rendering."""

from __future__ import annotations

from src.config import get_device_profile
from src.liquid_render import render


def test_partial_renders_error_state():
    """When errors.events is set, the calendar partial renders the error view."""
    data = {
        "meta": {
            "generated_at": "2026-07-16T09:00:00+00:00",
            "reference_date": "2026-07-16",
            "city": "Amsterdam",
        },
        "errors": {
            "events": "Calendar not configured",
            "tasks": None,
            "birthdays": None,
        },
        "weather": {
            "description": "Sunny",
            "temperature": 22,
            "feels_like": 20,
            "icon": "sun",
        },
        "events": [],
        "tasks": [],
        "birthdays": [],
        "calendars": [],
        "task_lists": [],
    }

    html = render(get_device_profile("og"), data)
    assert "(!) Not loaded" in html
    assert "Calendar not configured" in html
