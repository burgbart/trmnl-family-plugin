"""Fetch unified dashboard data in a single pass.

The unified JSON consumed by the TRMNL Liquid templates and the terminal
dashboard contains both aggregated (dashboard) and per-source (terminal)
data. This module fetches every configured data source once, then derives
both views from that single dataset so no API is called twice for the same
information.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List

from src.calendar import (
    _event_matches_filters,
    _fetch_raw_events_for_ids,
    _is_anniversary_event,
    fetch_birthdays_for_calendar_ids,
    get_calendar_service,
)
from src.config import (
    GOOGLE_CALENDAR_IDS,
    GOOGLE_SERVICE_ACCOUNT_JSON,
    TERMINAL_CALENDAR_IDS,
    TERMINAL_MAX_EVENTS,
    TERMINAL_MAX_TASKS,
    TERMINAL_TICKTICK_LIST_IDS,
    TICKTICK_ACCESS_TOKEN,
    TICKTICK_LIST_ID,
)
from src.data import Birthday, CalendarEvent, Task, Weather
from src.terminal_fetcher import CalendarSource, TaskListSource
from src.ticktick import fetch_project_name, fetch_tasks_for_list
from src.weather import fetch_weather_or_dummy


@dataclass
class UnifiedData:
    """All dashboard data, both aggregated for the Liquid templates and per-source for the terminal.

    ``errors`` maps a dashboard list key (``events``, ``tasks``, ``birthdays``) to
    an error message when that source could not be fetched. A missing key or
    ``None`` means the list loaded successfully (even if it is empty). Missing
    credentials and API failures are surfaced here instead of being hidden behind
    dummy data.
    """

    weather: Weather
    events: List[CalendarEvent]
    tasks: List[Task]
    birthdays: List[Birthday]
    calendars: List[CalendarSource]
    task_lists: List[TaskListSource]
    errors: dict[str, str | None] | None = None


def _dedupe_preserve_order(items: List[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _fetch_calendar_name(service, calendar_id: str) -> str:
    try:
        info = service.calendars().get(calendarId=calendar_id).execute()
        return info.get("summary", calendar_id)
    except Exception:
        return calendar_id


def _fetch_events_for_ids(calendar_ids: List[str]) -> List[CalendarEvent]:
    """Fetch non-celebration events for the supplied calendar IDs."""
    if not calendar_ids or not GOOGLE_SERVICE_ACCOUNT_JSON:
        return []
    try:
        # Validate credentials; _fetch_raw_events_for_ids builds its own service.
        get_calendar_service()
    except Exception:
        return []
    return _fetch_raw_events_for_ids(calendar_ids, days=14, max_results=250)


def _fetch_tasks_for_id(list_id: str) -> tuple[str, str, List[Task]]:
    name = fetch_project_name(list_id) or list_id
    tasks = fetch_tasks_for_list(list_id)
    return list_id, name, tasks


def _fetch_all_task_lists(list_ids: List[str]) -> List[tuple[str, str, List[Task]]]:
    """Fetch tasks for every list ID in parallel."""
    if not list_ids or not TICKTICK_ACCESS_TOKEN:
        return []
    results: List[tuple[str, str, List[Task]]] = []
    with ThreadPoolExecutor(max_workers=min(len(list_ids), 4)) as executor:
        future_to_id = {
            executor.submit(_fetch_tasks_for_id, list_id): list_id for list_id in list_ids
        }
        for future in as_completed(future_to_id):
            list_id = future_to_id[future]
            try:
                results.append(future.result())
            except Exception:
                results.append((list_id, list_id, []))
    return results


def _error_message(exc: Exception, default: str) -> str:
    """Return a readable error message from an exception."""
    message = str(exc).strip()
    return message if message else default


def fetch_unified_data() -> UnifiedData:
    """Fetch weather, calendars, tasks, and birthdays once.

    The function determines the union of dashboard and terminal sources, fetches
    each unique source a single time, then derives the aggregated dashboard view
    and the per-source terminal view from that dataset.

    Missing credentials and API failures are recorded in ``errors`` rather than
    being hidden behind dummy data, so the dashboard can render explicit error
    states. Weather uses a dummy fallback because it requires no credentials.
    """
    weather = fetch_weather_or_dummy()

    dashboard_calendar_ids = GOOGLE_CALENDAR_IDS
    terminal_calendar_ids = TERMINAL_CALENDAR_IDS
    all_calendar_ids = _dedupe_preserve_order(terminal_calendar_ids + dashboard_calendar_ids)

    dashboard_list_ids = [TICKTICK_LIST_ID] if TICKTICK_LIST_ID else []
    terminal_list_ids = TERMINAL_TICKTICK_LIST_IDS
    all_list_ids = _dedupe_preserve_order(terminal_list_ids + dashboard_list_ids)

    errors: dict[str, str | None] = {"events": None, "tasks": None, "birthdays": None}

    # -----------------------------------------------------------------------
    # Calendar data
    # -----------------------------------------------------------------------
    events: List[CalendarEvent] = []
    birthdays: List[Birthday] = []
    calendars: List[CalendarSource] = []

    if not all_calendar_ids or not GOOGLE_SERVICE_ACCOUNT_JSON:
        message = "Calendar not configured: set GOOGLE_SERVICE_ACCOUNT_JSON and GOOGLE_CALENDAR_IDS"
        errors["events"] = message
        errors["birthdays"] = message
    else:
        try:
            all_events = _fetch_events_for_ids(all_calendar_ids)
            service = get_calendar_service()

            calendars = []
            for calendar_id in terminal_calendar_ids:
                cal_events = [
                    e
                    for e in all_events
                    if e.calendar_id == calendar_id and not _is_anniversary_event(e)
                ]
                cal_events = cal_events[:TERMINAL_MAX_EVENTS]
                name = _fetch_calendar_name(service, calendar_id)
                calendars.append(CalendarSource(calendar_id, name, cal_events))

            events = [
                e
                for e in all_events
                if e.calendar_id in dashboard_calendar_ids
                and not _is_anniversary_event(e)
                and _event_matches_filters(e)
            ]
            events.sort(key=lambda e: e.start)

            birthdays = fetch_birthdays_for_calendar_ids(all_calendar_ids)
        except Exception as exc:
            message = _error_message(exc, "Calendar not available")
            errors["events"] = message
            errors["birthdays"] = message

    # -----------------------------------------------------------------------
    # Task data
    # -----------------------------------------------------------------------
    tasks: List[Task] = []
    task_lists: List[TaskListSource] = []

    if not all_list_ids or not TICKTICK_ACCESS_TOKEN:
        errors["tasks"] = (
            "Tasks not configured: set TICKTICK_ACCESS_TOKEN and TICKTICK_LIST_ID"
        )
    else:
        try:
            all_task_results = _fetch_all_task_lists(all_list_ids)

            for list_id, name, list_tasks in all_task_results:
                if list_id in terminal_list_ids:
                    task_lists.append(
                        TaskListSource(list_id, name, list_tasks[:TERMINAL_MAX_TASKS])
                    )
                if list_id == TICKTICK_LIST_ID:
                    tasks = list_tasks

            # When no terminal lists are configured, expose the main dashboard list
            # in the terminal UI as well so there is still something to switch to.
            if not terminal_list_ids and TICKTICK_LIST_ID:
                for list_id, name, list_tasks in all_task_results:
                    if list_id == TICKTICK_LIST_ID:
                        task_lists.append(
                            TaskListSource(list_id, name, list_tasks[:TERMINAL_MAX_TASKS])
                        )
                        break
        except Exception as exc:
            errors["tasks"] = _error_message(exc, "Tasks not available")

    return UnifiedData(
        weather=weather,
        events=events,
        tasks=tasks,
        birthdays=birthdays,
        calendars=calendars,
        task_lists=task_lists,
        errors=errors,
    )
