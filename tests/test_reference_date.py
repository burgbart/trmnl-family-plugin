"""Tests for the reference date override."""

from __future__ import annotations

from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from src import config as config_module
from src.config import (
    get_reference_date,
    get_reference_datetime,
    set_reference_date,
)


@pytest.fixture(autouse=True)
def _reset_reference_date(monkeypatch):
    """Reset reference date override before each test."""
    monkeypatch.setattr(config_module, "_REFERENCE_DATE", None)


def test_default_reference_date_is_today():
    assert get_reference_date() == date.today()


def test_set_reference_date_from_string():
    set_reference_date("23-12-2026")
    assert get_reference_date() == date(2026, 12, 23)


def test_set_reference_date_from_iso_string():
    set_reference_date("2026-12-23")
    assert get_reference_date() == date(2026, 12, 23)


def test_set_reference_date_from_date():
    set_reference_date(date(2026, 12, 23))
    assert get_reference_date() == date(2026, 12, 23)


def test_set_reference_date_from_datetime():
    set_reference_date(datetime(2026, 12, 23, 15, 30, tzinfo=timezone.utc))
    assert get_reference_date() == date(2026, 12, 23)


def test_get_reference_datetime_is_midnight_local(monkeypatch):
    monkeypatch.setattr(config_module, "TIMEZONE", "Europe/Amsterdam")
    set_reference_date("23-12-2026")
    assert get_reference_datetime() == datetime(
        2026, 12, 23, 0, 0, 0, tzinfo=ZoneInfo("Europe/Amsterdam")
    )


def test_invalid_reference_date_raises():
    with pytest.raises(ValueError):
        set_reference_date("not-a-date")
