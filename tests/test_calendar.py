"""Tests for Google Calendar filtering helpers."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest

from src import calendar as calendar_module
from src.calendar import _event_matches_filters, _is_anniversary_event, _parse_event, fetch_birthdays, fetch_calendar_events
from src.data import CalendarEvent


def _make_event(
    *,
    title: str = "Test event",
    start: datetime | None = None,
    attendees: tuple[str, ...] = (),
    calendar_id: str | None = None,
    all_day: bool = False,
) -> CalendarEvent:
    return CalendarEvent(
        title=title,
        start=start or datetime.now(timezone.utc),
        attendees=attendees,
        calendar_id=calendar_id,
        all_day=all_day,
    )


@pytest.fixture(autouse=True)
def _reset_filter_config(monkeypatch):
    """Reset calendar filter config before each test."""
    monkeypatch.setattr(calendar_module, "CALENDAR_ATTENDEE_EMAILS", [])
    monkeypatch.setattr(calendar_module, "CALENDAR_MAIN_CALENDAR_ID", None)


def test_no_filters_passes_every_event():
    event = _make_event(attendees=("someone@example.com",), calendar_id="other@example.com")
    assert _event_matches_filters(event) is True


def test_main_calendar_match():
    calendar_module.CALENDAR_MAIN_CALENDAR_ID = "main@example.com"
    event = _make_event(calendar_id="main@example.com")
    assert _event_matches_filters(event) is True


def test_main_calendar_no_match():
    calendar_module.CALENDAR_MAIN_CALENDAR_ID = "main@example.com"
    event = _make_event(calendar_id="other@example.com")
    assert _event_matches_filters(event) is False


def test_attendee_match():
    calendar_module.CALENDAR_ATTENDEE_EMAILS = ["alice@example.com", "bob@example.com"]
    event = _make_event(attendees=("bob@example.com",))
    assert _event_matches_filters(event) is True


def test_attendee_match_is_case_insensitive():
    calendar_module.CALENDAR_ATTENDEE_EMAILS = ["alice@example.com"]
    event = _make_event(attendees=("ALICE@EXAMPLE.COM",))
    assert _event_matches_filters(event) is True


def test_attendee_no_match():
    calendar_module.CALENDAR_ATTENDEE_EMAILS = ["alice@example.com"]
    event = _make_event(attendees=("bob@example.com",))
    assert _event_matches_filters(event) is False


def test_either_filter_is_enough():
    calendar_module.CALENDAR_ATTENDEE_EMAILS = ["alice@example.com"]
    calendar_module.CALENDAR_MAIN_CALENDAR_ID = "main@example.com"

    attendee_match = _make_event(attendees=("alice@example.com",), calendar_id="other@example.com")
    calendar_match = _make_event(attendees=("bob@example.com",), calendar_id="main@example.com")
    no_match = _make_event(attendees=("bob@example.com",), calendar_id="other@example.com")

    assert _event_matches_filters(attendee_match) is True
    assert _event_matches_filters(calendar_match) is True
    assert _event_matches_filters(no_match) is False


class TestFetchBirthdays:
    def test_extracts_multiple_anniversaries(self, monkeypatch):
        today = datetime.now(timezone.utc)
        events = [
            _make_event(title="Wedding anniversary", start=today, all_day=True),
            _make_event(title="First date anniversary", start=today + timedelta(days=3), all_day=True),
        ]
        monkeypatch.setattr(calendar_module, "_fetch_celebration_events", lambda: events)

        birthdays = fetch_birthdays()
        assert len(birthdays) == 2
        assert birthdays[0].name == "Wedding"
        assert birthdays[0].kind == "anniversary"
        assert birthdays[1].name == "First Date"
        assert birthdays[1].kind == "anniversary"

    def test_generic_anniversary_title_keeps_name(self, monkeypatch):
        today = datetime.now(timezone.utc)
        events = [_make_event(title="Anniversary", start=today, all_day=True)]
        monkeypatch.setattr(calendar_module, "_fetch_celebration_events", lambda: events)

        birthdays = fetch_birthdays()
        assert len(birthdays) == 1
        assert birthdays[0].name == "Anniversary"
        assert birthdays[0].kind == "anniversary"

    def test_deduplicates_same_name_date_kind(self, monkeypatch):
        today = datetime.now(timezone.utc)
        events = [
            _make_event(title="Emma birthday", start=today, all_day=True),
            _make_event(title="Emma birthday", start=today, all_day=True),
        ]
        monkeypatch.setattr(calendar_module, "_fetch_celebration_events", lambda: events)

        birthdays = fetch_birthdays()
        assert len(birthdays) == 1
        assert birthdays[0].name == "Emma"

    def test_birthday_and_anniversary_same_day_are_both_kept(self, monkeypatch):
        today = datetime.now(timezone.utc)
        events = [
            _make_event(title="John birthday", start=today, all_day=True),
            _make_event(title="John anniversary", start=today, all_day=True),
        ]
        monkeypatch.setattr(calendar_module, "_fetch_celebration_events", lambda: events)

        birthdays = fetch_birthdays()
        assert len(birthdays) == 2
        kinds = {b.kind for b in birthdays}
        assert kinds == {"birthday", "anniversary"}


class TestDutchKeywords:
    def test_verjaardag_is_birthday(self, monkeypatch):
        today = datetime.now(timezone.utc)
        events = [_make_event(title="Emma verjaardag", start=today, all_day=True)]
        monkeypatch.setattr(calendar_module, "_fetch_celebration_events", lambda: events)

        birthdays = fetch_birthdays()
        assert len(birthdays) == 1
        assert birthdays[0].name == "Emma"
        assert birthdays[0].kind == "birthday"

    def test_jubileum_is_anniversary(self, monkeypatch):
        today = datetime.now(timezone.utc)
        events = [_make_event(title="John jubileum", start=today, all_day=True)]
        monkeypatch.setattr(calendar_module, "_fetch_celebration_events", lambda: events)

        birthdays = fetch_birthdays()
        assert len(birthdays) == 1
        assert birthdays[0].name == "John"
        assert birthdays[0].kind == "anniversary"

    def test_trouwdag_is_anniversary(self, monkeypatch):
        today = datetime.now(timezone.utc)
        events = [_make_event(title="John trouwdag", start=today, all_day=True)]
        monkeypatch.setattr(calendar_module, "_fetch_celebration_events", lambda: events)

        birthdays = fetch_birthdays()
        assert len(birthdays) == 1
        assert birthdays[0].name == "John"
        assert birthdays[0].kind == "anniversary"


def test_all_day_birthday_is_anniversary_event():
    event = _make_event(title="Emma birthday", all_day=True)
    assert _is_anniversary_event(event) is True


def test_timed_birthday_party_is_not_anniversary_event():
    """A non-all-day "birthday" event is a party, not an anniversary entry."""
    event = _make_event(title="Emma birthday party", all_day=False)
    assert _is_anniversary_event(event) is False


def test_fetch_birthdays_excludes_timed_birthday_party(monkeypatch):
    """Only all-day birthday/anniversary events become anniversaries."""
    today = datetime.now(timezone.utc)
    events = [
        _make_event(title="Emma birthday party", start=today, all_day=False),
        _make_event(title="John birthday", start=today + timedelta(days=1), all_day=True),
    ]
    monkeypatch.setattr(calendar_module, "_fetch_raw_events_for_ids", lambda *a, **k: events)
    monkeypatch.setattr(calendar_module, "GOOGLE_CALENDAR_IDS", ["cal@example.com"])

    birthdays = fetch_birthdays()
    assert len(birthdays) == 1
    assert birthdays[0].name == "John"


def test_fetch_calendar_events_includes_party_excludes_all_day_birthday(monkeypatch):
    today = datetime.now(timezone.utc)
    events = [
        _make_event(title="Emma birthday party", start=today, all_day=False),
        _make_event(title="John birthday", start=today + timedelta(days=1), all_day=True),
    ]
    monkeypatch.setattr(calendar_module, "_fetch_raw_events", lambda **k: events)

    calendar_events = fetch_calendar_events()
    assert len(calendar_events) == 1
    assert calendar_events[0].title == "Emma birthday party"


def test_parse_all_day_event_parses_end_date():
    item = {
        "summary": "Holiday",
        "start": {"date": "2026-07-14"},
        "end": {"date": "2026-07-17"},
    }
    event = _parse_event(item, "cal@example.com")
    assert event.all_day is True
    assert event.start.date() == date(2026, 7, 14)
    assert event.end is not None
    assert event.end.date() == date(2026, 7, 17)


def test_parse_single_day_all_day_event_has_next_day_end():
    item = {
        "summary": "Single holiday",
        "start": {"date": "2026-07-14"},
        "end": {"date": "2026-07-15"},
    }
    event = _parse_event(item, "cal@example.com")
    assert event.all_day is True
    assert event.start.date() == date(2026, 7, 14)
    assert event.end is not None
    assert event.end.date() == date(2026, 7, 15)
