"""Fetch data for the terminal dashboard.

Unlike the PNG pipeline, this aggregates events/tasks per source so the user
can switch between calendars and TickTick lists at runtime.
"""

from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import List

from src.calendar import (
    _is_anniversary_event,
    fetch_birthdays_for_calendar_ids,
    get_calendar_service,
)
from src.config import (
    GOOGLE_SERVICE_ACCOUNT_JSON,
    TERMINAL_CALENDAR_IDS,
    TERMINAL_MAX_BIRTHDAYS,
    TERMINAL_MAX_EVENTS,
    TERMINAL_MAX_TASKS,
    TERMINAL_TICKTICK_LIST_IDS,
    TICKTICK_ACCESS_TOKEN,
)
from src.data import Birthday, CalendarEvent, Task, Weather, fetch_birthdays, fetch_calendar_events, fetch_tasks
from src.ticktick import fetch_project_name, fetch_tasks_for_list_or_dummy
from src.weather import fetch_weather_or_dummy


@dataclass
class CalendarSource:
    """A single Google Calendar and its upcoming events."""

    calendar_id: str
    name: str
    events: List[CalendarEvent]


@dataclass
class TaskListSource:
    """A single TickTick list and its tasks."""

    list_id: str
    name: str
    tasks: List[Task]


@dataclass
class TerminalData:
    """All data needed by the terminal dashboard."""

    weather: Weather
    calendars: List[CalendarSource]
    task_lists: List[TaskListSource]
    birthdays: List[Birthday]
    # Aggregated dashboard view (matches the top-level events/tasks arrays in
    # dashboard-v2.json). These are shown alongside the per-source breakdowns.
    events: List[CalendarEvent] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    generated_at: "datetime | None" = None
    errors: dict[str, str | None] | None = None


def _fetch_calendar_name(service, calendar_id: str) -> str:
    """Return the display name for a calendar ID, falling back to the ID."""
    try:
        info = service.calendars().get(calendarId=calendar_id).execute()
        return info.get("summary", calendar_id)
    except Exception:
        return calendar_id


def _fetch_events_for_calendar(
    service, calendar_id: str, days: int = 14, max_results: int = 250
) -> List[CalendarEvent]:
    """Fetch upcoming non-celebration events for a single calendar."""
    from src.calendar import _fetch_raw_events_for_ids

    events = _fetch_raw_events_for_ids(
        [calendar_id], days=days, max_results=max_results
    )
    return [e for e in events if not _is_anniversary_event(e)]


def _fetch_single_terminal_calendar(calendar_id: str) -> CalendarSource:
    """Fetch the name and events for a single calendar.

    A fresh service client is created per call because the Google API client
    service object is not thread-safe.
    """
    service = get_calendar_service()
    name = _fetch_calendar_name(service, calendar_id)
    events = _fetch_events_for_calendar(
        service, calendar_id, max_results=TERMINAL_MAX_EVENTS * 2
    )
    return CalendarSource(calendar_id, name, events)


def _fetch_terminal_calendars() -> List[CalendarSource]:
    """Fetch events for every configured terminal calendar in parallel."""
    calendar_ids = TERMINAL_CALENDAR_IDS
    if not calendar_ids or not GOOGLE_SERVICE_ACCOUNT_JSON:
        # Fall back to a single dummy calendar.
        return [CalendarSource("dummy", "Dummy calendar", fetch_calendar_events())]

    try:
        # Validate credentials once before spawning workers.
        get_calendar_service()
    except Exception as exc:
        print(f"Calendar service failed: {exc}; using dummy data", file=sys.stderr)
        return [CalendarSource("dummy", "Dummy calendar", fetch_calendar_events())]

    sources: List[CalendarSource] = []
    with ThreadPoolExecutor(max_workers=min(len(calendar_ids), 4)) as executor:
        future_to_id = {
            executor.submit(_fetch_single_terminal_calendar, calendar_id): calendar_id
            for calendar_id in calendar_ids
        }
        for future in as_completed(future_to_id):
            calendar_id = future_to_id[future]
            try:
                sources.append(future.result())
            except Exception as exc:
                print(
                    f"Calendar fetch failed for {calendar_id}: {exc}; using empty list",
                    file=sys.stderr,
                )
                sources.append(CalendarSource(calendar_id, calendar_id, []))

    return sources


def _fetch_single_terminal_task_list(list_id: str) -> TaskListSource:
    """Fetch the name and tasks for a single TickTick list."""
    name = fetch_project_name(list_id) or list_id
    tasks = fetch_tasks_for_list_or_dummy(list_id)
    return TaskListSource(list_id, name, tasks)


def _fetch_terminal_task_lists() -> List[TaskListSource]:
    """Fetch tasks for every configured terminal TickTick list in parallel."""
    list_ids = TERMINAL_TICKTICK_LIST_IDS
    if not list_ids or not TICKTICK_ACCESS_TOKEN:
        # Fall back to a single dummy task list.
        return [TaskListSource("dummy", "Dummy tasks", fetch_tasks())]

    sources: List[TaskListSource] = []
    with ThreadPoolExecutor(max_workers=min(len(list_ids), 4)) as executor:
        future_to_id = {
            executor.submit(_fetch_single_terminal_task_list, list_id): list_id
            for list_id in list_ids
        }
        for future in as_completed(future_to_id):
            list_id = future_to_id[future]
            try:
                sources.append(future.result())
            except Exception as exc:
                print(
                    f"Task list fetch failed for {list_id}: {exc}; using empty list",
                    file=sys.stderr,
                )
                sources.append(TaskListSource(list_id, list_id, []))

    return sources


def _fetch_terminal_birthdays(calendar_ids: List[str]) -> List[Birthday]:
    """Fetch anniversaries across all terminal calendars."""
    if not calendar_ids or not GOOGLE_SERVICE_ACCOUNT_JSON:
        return fetch_birthdays()

    try:
        return fetch_birthdays_for_calendar_ids(calendar_ids)
    except Exception as exc:
        print(f"Birthday fetch failed: {exc}; using dummy data", file=sys.stderr)
        return fetch_birthdays()


def fetch_terminal_data() -> TerminalData:
    """Fetch weather, calendar sources, task lists, and anniversaries.

    Deprecated: terminal_dashboard.py and server.py now read from dashboard-v2.json
    via src.json_loader rather than calling this function. Kept because the
    CalendarSource / TaskListSource / TerminalData dataclasses defined in this
    module are still used throughout the codebase.
    """
    # The first three sources are independent and I/O-bound.
    with ThreadPoolExecutor(max_workers=3) as executor:
        weather_future = executor.submit(fetch_weather_or_dummy)
        calendars_future = executor.submit(_fetch_terminal_calendars)
        task_lists_future = executor.submit(_fetch_terminal_task_lists)

        weather = weather_future.result()
        calendars = calendars_future.result()
        task_lists = task_lists_future.result()

    # Anniversaries need the resolved calendar IDs.
    birthdays = _fetch_terminal_birthdays(
        [source.calendar_id for source in calendars if source.calendar_id != "dummy"]
    )

    # Apply terminal limits.
    for source in calendars:
        source.events = source.events[:TERMINAL_MAX_EVENTS]
    for source in task_lists:
        source.tasks = source.tasks[:TERMINAL_MAX_TASKS]
    birthdays = birthdays[:TERMINAL_MAX_BIRTHDAYS]

    # Derive the aggregated dashboard view from the per-source data so the
    # deprecated direct-fetch path still populates every TerminalData field.
    aggregated_events = sorted(
        (event for source in calendars for event in source.events),
        key=lambda e: e.start,
    )[:TERMINAL_MAX_EVENTS]
    aggregated_tasks = [
        task for source in task_lists for task in source.tasks
    ][:TERMINAL_MAX_TASKS]

    return TerminalData(
        weather=weather,
        calendars=calendars,
        task_lists=task_lists,
        birthdays=birthdays,
        events=aggregated_events,
        tasks=aggregated_tasks,
    )
