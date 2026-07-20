"""Build a dummy dashboard.json fixture for local Liquid template testing."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add parent directory to path so src can be imported
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import fetchers and serialization after dotenv is loaded
from src.config import CITY, get_reference_date
from src.data import fetch_weather, fetch_calendar_events, fetch_tasks, fetch_birthdays
from src.serialization import build_dashboard_payload


def main() -> None:
    """Fetch dummy data and write to templates/dummy_dashboard.json."""
    weather = fetch_weather()
    events = fetch_calendar_events()
    tasks = fetch_tasks()
    birthdays = fetch_birthdays()

    output = build_dashboard_payload(
        weather=weather,
        events=events,
        tasks=tasks,
        birthdays=birthdays,
        calendars=[],
        task_lists=[],
        city=CITY,
        reference_date=get_reference_date(),
    )

    output_path = Path(__file__).parent / "dummy_dashboard.json"
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote dummy fixture to {output_path}")


if __name__ == "__main__":
    main()
