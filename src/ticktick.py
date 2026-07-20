"""Fetch tasks from a shared TickTick list."""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

import requests

from src.config import TICKTICK_ACCESS_TOKEN, TICKTICK_LIST_ID, get_reference_date
from src.data import Task

BASE_URL = "https://api.ticktick.com/open/v1"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {TICKTICK_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }


def _parse_due(date_str: str | None) -> Optional[date]:
    if not date_str:
        return None
    try:
        # TickTick due dates look like '2025-09-12T22:00:00.000+0000'
        if "T" in date_str:
            return datetime.strptime(date_str[:10], "%Y-%m-%d").date()
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def _fetch_task_items(data: dict) -> List[Task]:
    """Parse TickTick project data into Task objects."""
    tasks: List[Task] = []
    for item in data.get("tasks", []):
        status = item.get("status", 0)
        tasks.append(
            Task(
                title=item.get("title", "(Untitled)"),
                done=status == 2,
                priority=item.get("priority", 0),
                due_date=_parse_due(item.get("dueDate")),
                sort_order=item.get("sortOrder", 0),
            )
        )

    # Due tasks first, then preserve TickTick's custom sort order.
    tasks.sort(key=lambda t: (0 if _is_due(t) else 1, t.sort_order))
    return tasks


def fetch_tasks_for_list(list_id: str) -> List[Task]:
    """Fetch tasks from a specific TickTick list.

    Tasks are returned in the custom order defined in TickTick (sortOrder).
    """
    if not TICKTICK_ACCESS_TOKEN:
        raise RuntimeError("TICKTICK_ACCESS_TOKEN must be set")

    url = f"{BASE_URL}/project/{list_id}/data"
    response = requests.get(url, headers=_headers(), timeout=20)
    response.raise_for_status()
    data = response.json()
    return _fetch_task_items(data)


def fetch_project_name(list_id: str) -> str | None:
    """Fetch the display name for a TickTick project/list ID."""
    if not TICKTICK_ACCESS_TOKEN:
        return None
    try:
        response = requests.get(
            f"{BASE_URL}/project/{list_id}", headers=_headers(), timeout=20
        )
        response.raise_for_status()
        return response.json().get("name")
    except Exception:
        return None


def fetch_tasks() -> List[Task]:
    """Fetch tasks from the configured TickTick list.

    Tasks are returned in the custom order defined in TickTick (sortOrder).
    """
    if not TICKTICK_ACCESS_TOKEN or not TICKTICK_LIST_ID:
        raise RuntimeError("TICKTICK_ACCESS_TOKEN and TICKTICK_LIST_ID must be set")
    return fetch_tasks_for_list(TICKTICK_LIST_ID)


def _is_due(task: Task) -> bool:
    if task.done or task.due_date is None:
        return False
    return task.due_date <= get_reference_date()


def fetch_tasks_or_dummy() -> List[Task]:
    """Fetch real TickTick tasks, falling back to dummy data on error."""
    try:
        return fetch_tasks()
    except Exception as exc:  # pragma: no cover
        print(f"TickTick fetch failed: {exc}; using dummy data")
        from src.data import fetch_tasks as _dummy_tasks

        return _dummy_tasks()


def fetch_tasks_for_list_or_dummy(list_id: str) -> List[Task]:
    """Fetch tasks for a specific list, falling back to dummy data on error."""
    try:
        return fetch_tasks_for_list(list_id)
    except Exception as exc:  # pragma: no cover
        print(f"TickTick fetch failed for {list_id}: {exc}; using dummy data")
        from src.data import fetch_tasks as _dummy_tasks

        return _dummy_tasks()
