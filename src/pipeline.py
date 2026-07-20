"""Shared collect → render → [upload] pipeline.

Both run_workflow_loop.py and server.py use this to run one full refresh cycle:
fetch unified data, write dashboard.json, render the static Liquid preview.html,
and optionally upload the JSON to Cloudflare R2.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def run_pipeline(
    output_dir: Path,
    devices: list[str],
    *,
    upload: bool = False,
) -> "UnifiedData":
    """Collect data, render the Liquid preview, and optionally upload to R2.

    Args:
        output_dir: Directory to write ``dashboard.json`` and ``preview.html``.
        devices:    Slugs of devices to include in the preview, e.g. ["og", "x"].
        upload:     When True, upload dashboard.json to Cloudflare R2.

    Returns:
        The :class:`~src.unified_fetcher.UnifiedData` from this run so callers
        can display or inspect it without re-parsing the written JSON.
    """
    from export_preview import build_preview_html
    from src.config import CITY, get_reference_date
    from src.serialization import build_dashboard_payload
    from src.unified_fetcher import fetch_unified_data

    data = fetch_unified_data()
    generated_at = datetime.now(timezone.utc)
    payload = build_dashboard_payload(
        weather=data.weather,
        events=data.events,
        tasks=data.tasks,
        birthdays=data.birthdays,
        calendars=data.calendars,
        task_lists=data.task_lists,
        city=CITY,
        reference_date=get_reference_date(),
        generated_at=generated_at,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "dashboard.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    preview_html = build_preview_html(payload, device_names=devices)
    (output_dir / "preview.html").write_text(preview_html, encoding="utf-8")

    if upload:
        from src.upload import upload_json

        upload_json(json_path)

    return data
