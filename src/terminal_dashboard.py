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


def _build_merged_events_panel(calendars: List[CalendarSource], total_rows: int) -> Group:
    """Stack every calendar's events in one panel, sized to fit the terminal.

    Row budget is water-filled across calendars (see ``_allocate_rows``) so a
    calendar with few events doesn't hog space a busier one needs; whatever a
    calendar still can't fit collapses to a single "+N more" line rather than
    being silently dropped.
    """
    n = len(calendars)
    overhead = n + max(n - 1, 0)  # one title row + one blank spacer between sections
    available = max(total_rows - overhead, n)
    demands = [max(len(cal.events), 1) for cal in calendars]
    alloc = _allocate_rows(demands, available)

    renderables: List[object] = []
    for i, cal in enumerate(calendars):
        if i > 0:
            renderables.append(Text(""))
        renderables.append(_build_events_table(cal, max(alloc[i], 1)))
    return Group(*renderables)


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


def _build_merged_tasks_panel(task_lists: List[TaskListSource], total_rows: int) -> Group:
    """Stack every task list in one panel, sized to fit the terminal.

    Same water-filling strategy as ``_build_merged_events_panel``.
    """
    n = len(task_lists)
    overhead = n + max(n - 1, 0)
    available = max(total_rows - overhead, n)
    demands = [max(len(tl.tasks), 1) for tl in task_lists]
    alloc = _allocate_rows(demands, available)

    renderables: List[object] = []
    for i, tl in enumerate(task_lists):
        if i > 0:
            renderables.append(Text(""))
        renderables.append(_build_tasks_table(tl, max(alloc[i], 1)))
    return Group(*renderables)


def _build_header(
    data: TerminalData, last_refreshed: datetime | None = None
) -> Text:
    today = get_reference_date()
    weather_text = (
        f"{data.weather.temperature}°C (feels {data.weather.feels_like}°C)"
        f" · {data.weather.description}"
    )

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


def _build_footer(birthdays: List[Birthday]) -> Text:
    text = Text("Anniversaries  ", style="bold bright_white")
    if not birthdays:
        text.append("None upcoming", style="dim")
        return text

    entries = Text()
    for i, bday in enumerate(birthdays):
        if i > 0:
            entries.append(" · ", style="dim")
        days = _days_until(bday.date)
        label = "today!" if days == 0 else f"in {days}d"
        # All anniversaries use the birthday yellow; only the urgency indicator
        # turns red when the date is within a week.
        entries.append(f"{bday.name} ", style="yellow")
        entries.append(f"({label})", style="bold red" if days <= 7 else "dim")

    text.append(entries)
    return text


def render(
    data: TerminalData,
    console: Console | None = None,
    *,
    last_refreshed: datetime | None = None,
) -> Layout:
    """Render the terminal dashboard layout, merging every calendar and task
    list into a single scrollable-by-eye view instead of one-at-a-time tabs.
    """
    active_console = console or Console()
    height = active_console.height or 24
    # Reserve space for header, footer, borders and padding.
    max_rows = max(height - 12, 5)

    calendars = data.calendars or [CalendarSource("none", "No calendars", [])]
    task_lists = data.task_lists or [TaskListSource("none", "No tasks", [])]

    header = _build_header(data, last_refreshed=last_refreshed)
    events_panel = _build_merged_events_panel(calendars, max_rows)
    tasks_panel = _build_merged_tasks_panel(task_lists, max_rows)
    footer = _build_footer(data.birthdays)

    layout = Layout(name="root")
    layout.split_column(
        Layout(Panel(header, border_style="bright_blue"), size=4),
        Layout(name="main", ratio=1),
        Layout(Panel(footer, border_style="bright_magenta"), size=3),
    )
    layout["main"].split_row(
        Layout(Panel(events_panel, border_style="blue"), ratio=1),
        Layout(Panel(tasks_panel, border_style="green"), ratio=1),
    )

    return layout
