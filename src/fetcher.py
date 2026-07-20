"""Aggregate real or dummy data for the dashboard."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from src.calendar import fetch_birthdays_or_dummy, fetch_calendar_events_or_dummy
from src.data import Birthday, CalendarEvent, Task, Weather
from src.ticktick import fetch_tasks_or_dummy
from src.weather import fetch_weather_or_dummy


def fetch_all() -> tuple[Weather, list[CalendarEvent], list[Task], list[Birthday]]:
    """Fetch weather, events, tasks, and birthdays in parallel.

    The four data sources are independent and I/O-bound, so they are fetched
    concurrently. Real data sources are used when credentials are configured;
    otherwise dummy data is returned.
    """
    with ThreadPoolExecutor(max_workers=4) as executor:
        weather_future = executor.submit(fetch_weather_or_dummy)
        events_future = executor.submit(fetch_calendar_events_or_dummy)
        tasks_future = executor.submit(fetch_tasks_or_dummy)
        birthdays_future = executor.submit(fetch_birthdays_or_dummy)

        weather = weather_future.result()
        events = events_future.result()
        tasks = tasks_future.result()
        birthdays = birthdays_future.result()

    return weather, events, tasks, birthdays
