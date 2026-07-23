"""Fetch Google Calendar events and birthdays."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import List

from google.oauth2 import service_account
from googleapiclient.discovery import build

from src.config import (
    CALENDAR_ATTENDEE_EMAILS,
    CALENDAR_MAIN_CALENDAR_ID,
    GOOGLE_CALENDAR_IDS,
    GOOGLE_SERVICE_ACCOUNT_JSON,
    TIMEZONE,
    get_reference_date,
    get_reference_datetime,
)
from src.data import Birthday, CalendarEvent

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def _get_credentials():
    if not GOOGLE_SERVICE_ACCOUNT_JSON:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON is not set")

    if os.path.exists(GOOGLE_SERVICE_ACCOUNT_JSON):
        return service_account.Credentials.from_service_account_file(
            GOOGLE_SERVICE_ACCOUNT_JSON, scopes=SCOPES
        )

    info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
    return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)


def get_calendar_service():
    """Return an authorised Google Calendar API service client."""
    creds = _get_credentials()
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def _normalize_dt(dt: datetime) -> datetime:
    """Convert a datetime to a timezone-aware datetime in the configured timezone."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=ZoneInfo(TIMEZONE))
    return dt.astimezone(ZoneInfo(TIMEZONE))


def _parse_event(item: dict, calendar_id: str) -> CalendarEvent:
    summary = item.get("summary", "(No title)")
    start = item.get("start", {})
    end = item.get("end", {})

    if "dateTime" in start:
        start_dt = _normalize_dt(datetime.fromisoformat(start["dateTime"]))
        end_dt = (
            _normalize_dt(datetime.fromisoformat(end["dateTime"]))
            if "dateTime" in end
            else None
        )
        all_day = False
    else:
        # All-day event — treat as midnight in the configured timezone so sorting
        # never mixes naive/aware and the calendar date is preserved.
        start_dt = _normalize_dt(datetime.strptime(start["date"], "%Y-%m-%d"))
        # For all-day events Google returns an exclusive end date. Store it so
        # multi-day events can be rendered with their real span.
        end_dt = (
            _normalize_dt(datetime.strptime(end["date"], "%Y-%m-%d"))
            if "date" in end
            else None
        )
        all_day = True

    attendees = tuple(
        attendee.get("email", "").strip().lower()
        for attendee in item.get("attendees", [])
        if attendee.get("email", "").strip()
    )

    return CalendarEvent(
        title=summary,
        start=start_dt,
        end=end_dt,
        all_day=all_day,
        attendees=attendees,
        calendar_id=calendar_id,
    )


BIRTHDAY_KEYWORDS = ("birthday", "verjaardag")
ANNIVERSARY_KEYWORDS = ("anniversary", "trouwdag", "jubileum")


def _is_celebration(title: str) -> bool:
    """Return True if the event title marks a birthday or anniversary."""
    title_lower = title.lower()
    return any(k in title_lower for k in BIRTHDAY_KEYWORDS) or any(
        k in title_lower for k in ANNIVERSARY_KEYWORDS
    )


def _is_anniversary_event(event: CalendarEvent) -> bool:
    """Return True for all-day events that represent a birthday/anniversary.

    Non-all-day events with "birthday" or "anniversary" in the title are
    treated as celebration *parties* and should appear in the main event list
    instead of the anniversaries list.
    """
    return event.all_day and _is_celebration(event.title)


def _fetch_raw_events_for_ids(
    calendar_ids: List[str], *, days: int = 14, max_results: int = 20
) -> List[CalendarEvent]:
    """Fetch upcoming events from the supplied Google Calendar IDs."""
    if not calendar_ids:
        raise RuntimeError("No calendar IDs provided")

    service = get_calendar_service()
    now = get_reference_datetime().isoformat()
    max_dt = (get_reference_datetime() + timedelta(days=days)).isoformat()

    events: List[CalendarEvent] = []
    for calendar_id in calendar_ids:
        result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=now,
                timeMax=max_dt,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        for item in result.get("items", []):
            events.append(_parse_event(item, calendar_id))

    events.sort(key=lambda e: e.start)
    return events


def _fetch_raw_events(
    *, days: int = 14, max_results: int = 20
) -> List[CalendarEvent]:
    """Fetch upcoming events from configured Google Calendars (unfiltered)."""
    if not GOOGLE_CALENDAR_IDS:
        raise RuntimeError("GOOGLE_CALENDAR_IDS is not set")
    return _fetch_raw_events_for_ids(
        GOOGLE_CALENDAR_IDS, days=days, max_results=max_results
    )


def _fetch_celebration_events_for_ids(
    calendar_ids: List[str],
) -> List[CalendarEvent]:
    """Fetch all-day celebration events from the supplied calendar IDs."""
    events = _fetch_raw_events_for_ids(calendar_ids, days=90, max_results=250)
    return [e for e in events if _is_anniversary_event(e)]


def _fetch_celebration_events() -> List[CalendarEvent]:
    """Fetch events specifically for birthday/anniversary detection.

    Uses a wider lookahead and larger result page than the main event list so
    sporadic all-day celebrations are not dropped behind busy calendars.
    """
    if not GOOGLE_CALENDAR_IDS:
        raise RuntimeError("GOOGLE_CALENDAR_IDS is not set")
    return _fetch_celebration_events_for_ids(GOOGLE_CALENDAR_IDS)


def _event_matches_filters(event: CalendarEvent) -> bool:
    """Return True when an event should be shown in the calendar section.

    Events pass when at least one filter is configured and they match it:
    either an attendee email is listed in CALENDAR_ATTENDEE_EMAILS, or the
    event lives on CALENDAR_MAIN_CALENDAR_ID. When no filters are configured,
    every event passes so existing behaviour is preserved.
    """
    filters_active = bool(CALENDAR_ATTENDEE_EMAILS or CALENDAR_MAIN_CALENDAR_ID)
    if not filters_active:
        return True

    if CALENDAR_MAIN_CALENDAR_ID and event.calendar_id == CALENDAR_MAIN_CALENDAR_ID:
        return True

    if CALENDAR_ATTENDEE_EMAILS:
        event_attendees = {email.lower() for email in event.attendees}
        if event_attendees.intersection(CALENDAR_ATTENDEE_EMAILS):
            return True

    return False


def fetch_calendar_events() -> List[CalendarEvent]:
    """Fetch upcoming events from configured Google Calendars.

    Birthday and anniversary events are excluded because they are shown in the
    Anniversaries section instead. Remaining events are filtered by attendee
    email and/or main calendar when those environment variables are set.
    """
    return [
        e
        for e in _fetch_raw_events()
        if not _is_anniversary_event(e) and _event_matches_filters(e)
    ]


def _extract_birthdays(events: List[CalendarEvent]) -> List[Birthday]:
    """Convert celebration events into Birthday dataclasses.

    Celebrations are compared against the current local date in the configured
    timezone; all-day events from before the reference date are skipped so the
    anniversaries section never shows stale entries.
    """
    celebrations: List[Birthday] = []
    seen = set()
    today = get_reference_date()

    for event in events:
        local_start_date = _normalize_dt(event.start).date()
        if local_start_date < today:
            continue

        title_lower = event.title.lower()
        matched_keyword = next(
            (k for k in BIRTHDAY_KEYWORDS if k in title_lower), None
        )
        if matched_keyword:
            kind = "birthday"
            name = title_lower.replace(matched_keyword, "").replace("🎂", "").strip(" -:\t")
        else:
            matched_keyword = next(
                (k for k in ANNIVERSARY_KEYWORDS if k in title_lower), None
            )
            if matched_keyword:
                kind = "anniversary"
                name = (
                    title_lower.replace(matched_keyword, "")
                    .replace("💍", "")
                    .strip(" -:\t")
                )
            else:
                continue

        if not name:
            name = event.title.strip()

        if not name:
            continue

        key = (name, local_start_date, kind)
        if key in seen:
            continue
        seen.add(key)

        celebrations.append(
            Birthday(name=name.title(), date=local_start_date, kind=kind)
        )

    return celebrations


def fetch_birthdays_for_calendar_ids(calendar_ids: List[str]) -> List[Birthday]:
    """Fetch upcoming birthdays and anniversaries from the given calendar IDs."""
    events = _fetch_celebration_events_for_ids(calendar_ids)
    return _extract_birthdays(events)


def fetch_birthdays() -> List[Birthday]:
    """Fetch upcoming birthdays and anniversaries from Google Calendar events.

    Looks for events whose title contains 'birthday' or 'anniversary'
    (case-insensitive).
    """
    events = _fetch_celebration_events()
    return _extract_birthdays(events)


def fetch_calendar_events_or_dummy() -> List[CalendarEvent]:
    """Fetch real events, falling back to dummy data on error."""
    try:
        return fetch_calendar_events()
    except Exception as exc:  # pragma: no cover
        print(f"Calendar fetch failed: {exc}; using dummy data")
        from src.data import fetch_calendar_events as _dummy_events

        return _dummy_events()


def fetch_birthdays_or_dummy() -> List[Birthday]:
    """Fetch real birthdays, falling back to dummy data on error."""
    try:
        return fetch_birthdays()
    except Exception as exc:  # pragma: no cover
        print(f"Birthday fetch failed: {exc}; using dummy data")
        from src.data import fetch_birthdays as _dummy_birthdays

        return _dummy_birthdays()
