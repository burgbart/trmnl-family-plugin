"""Terminal rendering for the dashboard data."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import List

from rich.box import SIMPLE
from rich.console import Console, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.config import CITY, get_reference_date, to_local_time
from src.data import Birthday, CalendarEvent, Task, Weather
from src.terminal_fetcher import CalendarSource, TaskListSource, TerminalData


def _allocate_rows(demands: List[int], total: int) -> List[int]:
    """Water-fill ``total`` rows across sections proportional to their demand.

    Sections whose full content fits within an equal share give their surplus
    back to the pool, so sections with more items get the extra rows instead
    of everyone being capped at a strict equal split.
    """
    n = len(demands)
    if n == 0:
        return []
    if total <= 0:
        return [0] * n

    alloc = [0] * n
    remaining = total
    active = set(range(n))
    while remaining > 0 and active:
        share = max(remaining // len(active), 1)
        progressed = False
        for i in list(active):
            if remaining <= 0:
                break
            need = demands[i] - alloc[i]
            take = min(share, need, remaining)
            if take <= 0:
                active.discard(i)
                continue
            alloc[i] += take
            remaining -= take
            progressed = True
            if alloc[i] >= demands[i]:
                active.discard(i)
        if not progressed:
            break
    return alloc


def _fmt_time(dt: datetime) -> str:
    return to_local_time(dt).strftime("%H:%M")


def _fmt_event_date(dt: datetime, all_day: bool = False) -> str:
    # All-day dates are absolute (midnight UTC represents the calendar date);
    # timed events are converted to the configured local timezone.
    event_dt = dt if all_day else to_local_time(dt)
    event_date = event_dt.date()
    today = get_reference_date()
    if event_date == today:
        return "Today"
    if event_date == today + timedelta(days=1):
        return "Tomorrow"
    return event_dt.strftime("%a %d %b")


def _days_until(target: date) -> int:
    return (target - get_reference_date()).days


def _is_due(task: Task) -> bool:
    if task.done or task.due_date is None:
        return False
    return task.due_date <= get_reference_date()


def _event_date_range(start: datetime, end: datetime | None) -> str:
    """Return a concise date range for an all-day event.

    For all-day events ``end`` is the exclusive end date from Google Calendar,
    so the last real day is one day earlier.
    """
    if end is None or end.date() <= start.date() + timedelta(days=1):
        return _fmt_event_date(start, all_day=True)

    last_day = end.date() - timedelta(days=1)
    start_text = _fmt_event_date(start, all_day=True)
    # Re-use the same formatting helper by building a datetime for the last day.
    end_text = _fmt_event_date(datetime.combine(last_day, start.timetz()), all_day=True)
    return f"{start_text} – {end_text}"


def _event_when(event: CalendarEvent) -> Text:
    if event.all_day:
        date_range = _event_date_range(event.start, event.end)
        # Multi-day events already show their span; no need for the "All day" label.
        if event.end and event.end.date() > event.start.date() + timedelta(days=1):
            return Text(date_range, style="italic #D97757")
        return Text(f"{date_range} · All day", style="cyan")
    time_range = _fmt_time(event.start)
    if event.end:
        time_range += f"–{_fmt_time(event.end)}"
    return Text(f"{_fmt_event_date(event.start)} {time_range}", style="cyan")


def _build_events_table(source: CalendarSource, max_rows: int) -> Table:
    table = Table(
        title=f"Upcoming: {source.name}",
        box=SIMPLE,
        show_header=False,
        expand=True,
        pad_edge=False,
    )
    table.add_column("When", style="cyan", ratio=2)
    table.add_column("What", style="white", ratio=5)

    events = source.events[:max_rows]
    prev_date = None
    for event in events:
        event_date = event.start.date()
        if prev_date is not None and event_date != prev_date:
            table.add_row("", Text("·" * 50, style="dim"))
        table.add_row(_event_when(event), Text(event.title))
        prev_date = event_date

    remaining = len(source.events) - len(events)
    if remaining > 0:
        table.add_row("", Text(f"+{remaining} more", style="dim"))
    elif not events:
        table.add_row("", Text("No upcoming events", style="dim"))

    return table


def _build_tasks_table(source: TaskListSource, max_rows: int) -> Table:
    table = Table(
        title=f"Tasks: {source.name}",
        box=SIMPLE,
        show_header=False,
        expand=True,
        pad_edge=False,
    )
    table.add_column("Done", style="green", ratio=1)
    table.add_column("Task", style="white", ratio=6)

    tasks = source.tasks[:max_rows]
    for task in tasks:
        check = "[x]" if task.done else "[ ]"
        title_text = Text(task.title)
        if task.done:
            title_text.stylize("dim strike")
        elif _is_due(task):
            title_text.stylize("bold red")
        elif task.due_date:
            title_text.append(f"  ({task.due_date.isoformat()})", style="dim")

        table.add_row(Text(check, style="green" if task.done else "white"), title_text)

    remaining = len(source.tasks) - len(tasks)
    if remaining > 0:
        table.add_row("", Text(f"+{remaining} more", style="dim"))
    elif not tasks:
        table.add_row("", Text("No tasks", style="dim"))

    return table


def _build_aggregated_events_table(events: List[CalendarEvent], max_rows: int) -> Table:
    """Render the top-level aggregated upcoming events list."""
    table = Table(
        title="Upcoming Events",
        box=SIMPLE,
        show_header=False,
        expand=True,
        pad_edge=False,
    )
    table.add_column("When", style="cyan", ratio=2)
    table.add_column("What", style="white", ratio=5)

    shown = events[:max_rows]
    prev_date = None
    for event in shown:
        event_date = event.start.date()
        if prev_date is not None and event_date != prev_date:
            table.add_row("", Text("·" * 50, style="dim"))
        table.add_row(_event_when(event), Text(event.title))
        prev_date = event_date

    remaining = len(events) - len(shown)
    if remaining > 0:
        table.add_row("", Text(f"+{remaining} more", style="dim"))
    elif not events:
        table.add_row("", Text("No upcoming events", style="dim"))

    return table


def _build_aggregated_tasks_table(tasks: List[Task], max_rows: int) -> Table:
    """Render the top-level aggregated tasks list with due-date indicators."""
    table = Table(
        title="Tasks",
        box=SIMPLE,
        show_header=False,
        expand=True,
        pad_edge=False,
    )
    table.add_column("Done", style="green", ratio=1)
    table.add_column("Task", style="white", ratio=6)

    shown = tasks[:max_rows]
    for task in shown:
        check = "[x]" if task.done else "[ ]"
        title_text = Text(task.title)
        if task.done:
            title_text.stylize("dim strike")
        elif _is_due(task):
            title_text.stylize("bold red")
        elif task.due_date:
            title_text.append(f"  ({task.due_date.isoformat()})", style="dim")

        table.add_row(Text(check, style="green" if task.done else "white"), title_text)

    remaining = len(tasks) - len(shown)
    if remaining > 0:
        table.add_row("", Text(f"+{remaining} more", style="dim"))
    elif not tasks:
        table.add_row("", Text("No tasks", style="dim"))

    return table


def _build_events_column(
    events: List[CalendarEvent],
    calendars: List[CalendarSource],
    total_rows: int,
) -> Group:
    """Stack aggregated events and per-source calendars in one column."""
    sections: List[tuple[str, List[CalendarEvent]]] = [("Upcoming Events", events)]
    for cal in calendars:
        sections.append((cal.name, cal.events))

    n = len(sections)
    overhead = n  # one title row per section
    available = max(total_rows - overhead, n)
    demands = [max(len(items), 1) for _, items in sections]
    alloc = _allocate_rows(demands, available)

    renderables: List[object] = []
    for i, (title, items) in enumerate(sections):
        if i > 0:
            renderables.append(Text(""))
        if i == 0:
            renderables.append(_build_aggregated_events_table(items, max(alloc[i], 1)))
        else:
            renderables.append(
                _build_events_table(
                    CalendarSource("", title, items), max(alloc[i], 1)
                )
            )

    return Group(*renderables)


def _build_tasks_column(
    tasks: List[Task],
    task_lists: List[TaskListSource],
    total_rows: int,
) -> Group:
    """Stack aggregated tasks and per-source task lists in one column."""
    sections: List[tuple[str, List[Task]]] = [("Tasks", tasks)]
    for tl in task_lists:
        sections.append((tl.name, tl.tasks))

    n = len(sections)
    overhead = n
    available = max(total_rows - overhead, n)
    demands = [max(len(items), 1) for _, items in sections]
    alloc = _allocate_rows(demands, available)

    renderables: List[object] = []
    for i, (title, items) in enumerate(sections):
        if i > 0:
            renderables.append(Text(""))
        if i == 0:
            renderables.append(_build_aggregated_tasks_table(items, max(alloc[i], 1)))
        else:
            renderables.append(
                _build_tasks_table(
                    TaskListSource("", title, items), max(alloc[i], 1)
                )
            )

    return Group(*renderables)


def _build_header(
    data: TerminalData, last_refreshed: datetime | None = None
) -> Text:
    today = get_reference_date()
    weather_text = (
        f"{data.weather.temperature}°C (feels {data.weather.feels_like}°C)"
        f" · {data.weather.description}"
    )
    if data.weather.alert:
        weather_text += f"\n⚠ {data.weather.alert}"

    calendar_count = len(data.calendars)
    task_count = len(data.task_lists)

    refresh_text = ""
    if last_refreshed is not None:
        age_text = ""
        if data.generated_at is not None:
            age = last_refreshed - data.generated_at
            mins = int(age.total_seconds() // 60)
            if mins < 1:
                age_text = " (just collected)"
            elif mins < 60:
                age_text = f" (data {mins} min old)"
            else:
                h, m = divmod(mins, 60)
                age_text = f" (data {h} h {m} min old)"
        refresh_text = f" · refreshed {_fmt_time(last_refreshed)}{age_text}"

    text = Text()
    text.append(
        f"{today.strftime('%A %d %B %Y')} · {CITY} · {weather_text}",
        style="bold bright_white",
    )
    text.append("\n")
    text.append(f"Calendars: ", style="dim")
    text.append(f"{calendar_count}", style="bold blue")
    text.append("   ")
    text.append("Task lists: ", style="dim")
    text.append(f"{task_count}", style="bold green")
    text.append("   ")
    text.append(f"q: quit{refresh_text}", style="dim")
    return text


def _build_footer(
    birthdays: List[Birthday], birthdays_error: str | None = None
) -> Text:
    text = Text("Anniversaries  ", style="bold bright_white")
    if birthdays_error:
        text.append(f"(!) Not loaded: {birthdays_error}", style="red")
        return text
    if not birthdays:
        text.append("None upcoming", style="dim")
        return text

    entries = Text()
    for i, bday in enumerate(birthdays):
        if i > 0:
            entries.append(" · ", style="dim")
        days = _days_until(bday.date)
        label = "today!" if days == 0 else f"in {days}d"
        kind_label = bday.kind if bday.kind else "birthday"
        # All anniversaries use the birthday yellow; only the urgency indicator
        # turns red when the date is within a week.
        entries.append(f"{bday.name} ", style="yellow")
        entries.append(
            f"({kind_label} · {label})",
            style="bold red" if days <= 7 else "dim",
        )

    text.append(entries)
    return text


def _build_error_panel(message: str) -> Panel:
    """Render a simple error panel for a failed data source."""
    text = Text()
    text.append("(!) Not loaded\n", style="bold red")
    text.append(message, style="red")
    return Panel(text, border_style="red")


def _build_weather_forecast_panel(weather: Weather) -> Text:
    """Render a compact horizontal multi-day forecast."""
    if not weather.forecast:
        return Text("No forecast available", style="dim")

    text = Text()
    text.append("Forecast  ", style="bold bright_white")
    for i, day in enumerate(weather.forecast[:5]):
        if i > 0:
            text.append("   ", style="dim")
        day_label = day.date.strftime("%a %d %b")
        precip = ""
        if day.precipitation_probability is not None:
            precip = f" · {day.precipitation_probability}%"
        elif day.precipitation_amount:
            precip = f" · {day.precipitation_amount}mm"
        text.append(
            f"{day_label}: {day.description} "
            f"{day.temperature_high}°/{day.temperature_low}°{precip}",
            style="white",
        )

    return text


def render(
    data: TerminalData,
    console: Console | None = None,
    *,
    last_refreshed: datetime | None = None,
) -> Layout:
    """Render the terminal dashboard layout.

    Shows current weather (with alerts), a multi-day forecast, the aggregated
    upcoming events and tasks from dashboard-v2.json, the per-source calendar
    and task-list breakdowns, and anniversaries with their kinds.
    """
    active_console = console or Console()
    height = active_console.height or 24

    errors = data.errors or {}
    header = _build_header(data, last_refreshed=last_refreshed)
    header_size = 5 if data.weather.alert else 4
    footer_size = 3
    forecast_size = 4

    # Row budget for the events/tasks lists below the forecast.
    lists_height = max(height - header_size - footer_size - forecast_size, 5)

    if errors.get("events"):
        events_column = _build_error_panel(errors["events"])
    else:
        calendars = data.calendars or [CalendarSource("none", "No calendars", [])]
        events_column = _build_events_column(data.events, calendars, lists_height)

    if errors.get("tasks"):
        tasks_column = _build_error_panel(errors["tasks"])
    else:
        task_lists = data.task_lists or [TaskListSource("none", "No tasks", [])]
        tasks_column = _build_tasks_column(data.tasks, task_lists, lists_height)

    footer = _build_footer(data.birthdays, birthdays_error=errors.get("birthdays"))

    layout = Layout(name="root")
    layout.split_column(
        Layout(Panel(header, border_style="bright_blue"), size=header_size),
        Layout(name="main", ratio=1),
        Layout(Panel(footer, border_style="bright_magenta"), size=footer_size),
    )
    layout["main"].split_column(
        Layout(
            Panel(
                _build_weather_forecast_panel(data.weather),
                border_style="yellow",
            ),
            size=forecast_size,
        ),
        Layout(name="lists", ratio=1),
    )
    layout["lists"].split_row(
        Layout(
            Panel(events_column, border_style="blue" if not errors.get("events") else "red"),
            ratio=1,
        ),
        Layout(
            Panel(tasks_column, border_style="green" if not errors.get("tasks") else "red"),
            ratio=1,
        ),
    )

    return layout
