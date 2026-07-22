"""Render a device's Liquid template against parsed dashboard-v2.json data.

Uses python-liquid with a `FileSystemLoader` pointed at the repo's
`templates/` directory. The loader is constructed with `ext=".liquid"`, so
partials can be referenced with the bare name inside `{% render %}` tags
(e.g. `{% render 'partials/weather', ... %}` resolves to
`templates/partials/weather.liquid`) — this is the convention documented in
`templates/CONTRACT.md`.
"""

from __future__ import annotations

from pathlib import Path

from liquid import Environment, FileSystemLoader

from src.config import DeviceProfile, get_device_profile

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

_env = Environment(loader=FileSystemLoader(str(_TEMPLATES_DIR), ext=".liquid"))


def render(
    device_profile: DeviceProfile | str,
    data: dict,
    template_path: str | None = None,
) -> str:
    """Render the given device's Liquid template against dashboard data.

    `device_profile` may be a `DeviceProfile` instance or a device name
    string (e.g. "og"/"x"), which is resolved via `get_device_profile()`.
    `data` is the parsed dashboard-v2.json dict (meta/weather/events/tasks/
    birthdays — see templates/CONTRACT.md) and is passed directly as the
    top-level Liquid render context; the device templates own all
    sizing/layout values themselves and don't expect them injected.

    Optional `template_path` overrides the template file defined by the
    device profile. This is useful for quickly testing a new design without
    registering a new profile. The path is resolved the same way as profile
    templates (relative to the `templates/` directory, e.g.
    "devices/my_custom_og.liquid").
    """
    if isinstance(device_profile, str):
        device_profile = get_device_profile(device_profile)

    effective_template_path = template_path or device_profile.template_path
    if effective_template_path is None:
        raise ValueError(
            f"Device '{device_profile.name}' has no template configured; "
            "cannot render."
        )

    template = _env.get_template(effective_template_path)
    return template.render(**data)
