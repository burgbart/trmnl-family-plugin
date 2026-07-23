"""Dashboard configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

# Reference date override for testing / rendering a dashboard as if it were a
# different day. Set via set_reference_date() or the REFERENCE_DATE env var
# (format DD-MM-YYYY). Defaults to today when unset.
_REFERENCE_DATE: date | None = None


def set_reference_date(date_value: str | date | datetime | None) -> date | None:
    """Set the reference date used by the dashboard.

    Accepts a string in DD-MM-YYYY format, a date, a datetime, or None to
    clear the override. Returns the parsed date or None.
    """
    global _REFERENCE_DATE
    if date_value is None:
        _REFERENCE_DATE = None
        return None
    if isinstance(date_value, datetime):
        _REFERENCE_DATE = date_value.date()
        return _REFERENCE_DATE
    if isinstance(date_value, date):
        _REFERENCE_DATE = date_value
        return _REFERENCE_DATE
    for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
        try:
            _REFERENCE_DATE = datetime.strptime(date_value.strip(), fmt).date()
            return _REFERENCE_DATE
        except ValueError:
            continue
    raise ValueError(f"Invalid reference date '{date_value}'. Expected DD-MM-YYYY.")


def get_reference_date() -> date:
    """Return the reference date, defaulting to today."""
    if _REFERENCE_DATE is not None:
        return _REFERENCE_DATE
    env_date = os.getenv("REFERENCE_DATE")
    if env_date:
        return set_reference_date(env_date) or date.today()
    return date.today()


def get_reference_datetime() -> datetime:
    """Return midnight in the configured local timezone on the reference date."""
    return datetime.combine(get_reference_date(), datetime.min.time()).replace(
        tzinfo=ZoneInfo(TIMEZONE)
    )


@dataclass(frozen=True)
class DeviceProfile:
    """Per-device rendering configuration."""

    name: str
    width: int
    height: int
    mode: str  # "1" for 1-bit OG, "L" for grayscale TRMNL X
    padding: int
    header_height: int
    font_size_title: int
    font_size_large: int
    font_size_medium: int
    font_size_small: int
    font_size_tiny: int
    line_height: int
    checkbox_size: int
    calendar_width_ratio: float
    tasks_height_ratio: float
    max_events: int
    max_tasks: int
    max_birthdays: int
    # Number of distinct grayscale levels the physical e-ink panel supports
    # (used by export_preview.py's CSS approximation, not by the Liquid
    # templates themselves). OG supports 2-bit/4-level grayscale (post
    # firmware update — see https://help.trmnl.com/en/articles/12386214);
    # X is 16-level (4-bit).
    grayscale_levels: int = 16
    # Liquid template filename, relative to templates/devices/. None means
    # no template exists yet (e.g. a future/stub device profile) — callers
    # (src/liquid_render.py, export_preview.py) must skip such profiles.
    template_filename: str | None = None

    @property
    def template_path(self) -> str:
        """Path to this device's Liquid template, relative to templates/."""
        if self.template_filename is None:
            raise ValueError(f"Device '{self.name}' has no template configured")
        return f"devices/{self.template_filename}"


# TRMNL OG — 800 x 480 px e-ink panel rendered as 8-bit "L". The panel
# natively supports 2-bit/4-level grayscale (post firmware update), and
# OG_GRAYSCALE_LEVELS below defaults to that for the local preview's CSS
# approximation.
OG_PROFILE = DeviceProfile(
    name="og",
    width=800,
    height=480,
    mode="L",
    padding=10,
    header_height=90,
    font_size_title=28,
    font_size_large=34,
    font_size_medium=18,
    font_size_small=16,
    font_size_tiny=13,
    line_height=28,
    checkbox_size=12,
    calendar_width_ratio=0.60,
    tasks_height_ratio=0.62,
    max_events=10,
    max_tasks=6,
    max_birthdays=4,
    grayscale_levels=int(os.getenv("OG_GRAYSCALE_LEVELS", "4")),
    template_filename="og.liquid",
)

# TRMNL X — 1872 x 1404 px, 16-level grayscale rendered as 8-bit "L"
X_PROFILE = DeviceProfile(
    name="x",
    width=1872,
    height=1404,
    mode="L",
    padding=24,
    header_height=180,
    font_size_title=64,
    font_size_large=72,
    font_size_medium=36,
    font_size_small=30,
    font_size_tiny=24,
    line_height=44,
    checkbox_size=26,
    calendar_width_ratio=0.58,
    tasks_height_ratio=0.62,
    max_events=8,
    max_tasks=10,
    max_birthdays=6,
    grayscale_levels=16,
    template_filename="x.liquid",
)

# Placeholder future-device profile — proves the registry/data shape scales
# to a third device without any code changes elsewhere. It has no Liquid
# template yet (template_filename=None), so src/liquid_render.py and
# export_preview.py must skip it rather than crash.
STUB_PROFILE = DeviceProfile(
    name="stub",
    width=800,
    height=480,
    mode="L",
    padding=10,
    header_height=90,
    font_size_title=28,
    font_size_large=34,
    font_size_medium=18,
    font_size_small=16,
    font_size_tiny=13,
    line_height=28,
    checkbox_size=12,
    calendar_width_ratio=0.60,
    tasks_height_ratio=0.62,
    max_events=6,
    max_tasks=6,
    max_birthdays=4,
    grayscale_levels=4,
    template_filename=None,
)

_DEVICE_PROFILES: dict[str, DeviceProfile] = {
    OG_PROFILE.name: OG_PROFILE,
    X_PROFILE.name: X_PROFILE,
    STUB_PROFILE.name: STUB_PROFILE,
}


def get_device_profile(name: str) -> DeviceProfile:
    """Return the device profile for the given slug."""
    profile = _DEVICE_PROFILES.get(name.lower())
    if profile is None:
        raise ValueError(
            f"Unknown device '{name}'. Supported devices: {', '.join(_DEVICE_PROFILES)}"
        )
    return profile


# Weather location (Amsterdam defaults)
LATITUDE = float(os.getenv("WEATHER_LATITUDE", "52.3676"))
LONGITUDE = float(os.getenv("WEATHER_LONGITUDE", "4.9041"))
CITY = os.getenv("CITY", "Amsterdam")

# Optional Open-Meteo forecast model. When unset or empty, Open-Meteo uses its
# default best_match selection. Regional models such as icon_seamless (DWD,
# higher resolution for Central Europe) or gfs_seamless (NOAA GFS, global) can
# be selected by setting this variable to the model identifier.
WEATHER_MODEL = os.getenv("WEATHER_MODEL", "")

# Local timezone for displaying calendar event times. Defaults to Amsterdam to
# match the default weather location; override with the TIMEZONE env var
# (e.g. "Europe/London" or "America/New_York").
TIMEZONE = os.getenv("TIMEZONE", "Europe/Amsterdam")


def to_local_time(dt: datetime) -> datetime:
    """Convert a UTC datetime to the configured local timezone.

    Falls back to returning the original datetime if the configured timezone
    cannot be resolved.
    """
    try:
        return dt.astimezone(ZoneInfo(TIMEZONE))
    except Exception:
        return dt

# Google Calendar (service account)
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
GOOGLE_CALENDAR_IDS = [
    cid.strip()
    for cid in os.getenv("GOOGLE_CALENDAR_IDS", "").split(",")
    if cid.strip()
]

# Calendar event filtering.
# If either variable is set, only events that match are shown in the calendar
# section: events whose attendee list includes one of the configured emails, or
# events that live on the configured main calendar. When both are unset, no
# filtering is applied so existing deployments keep working.
CALENDAR_ATTENDEE_EMAILS = [
    email.strip().lower()
    for email in os.getenv("CALENDAR_ATTENDEE_EMAILS", "").split(",")
    if email.strip()
]
CALENDAR_MAIN_CALENDAR_ID = os.getenv("CALENDAR_MAIN_CALENDAR_ID", "").strip() or None

# TickTick
TICKTICK_ACCESS_TOKEN = os.getenv("TICKTICK_ACCESS_TOKEN")
TICKTICK_LIST_ID = os.getenv("TICKTICK_LIST_ID")

# Terminal dashboard sources.
# These are intentionally separate from the e-ink dashboard so the terminal
# tool can switch between different calendars / task lists. When unset, the
# terminal tool falls back to the dashboard sources above.
TERMINAL_CALENDAR_IDS = [
    cid.strip()
    for cid in os.getenv("TERMINAL_CALENDAR_IDS", "").split(",")
    if cid.strip()
] or GOOGLE_CALENDAR_IDS

TERMINAL_TICKTICK_LIST_IDS = [
    lid.strip()
    for lid in os.getenv("TERMINAL_TICKTICK_LIST_IDS", "").split(",")
    if lid.strip()
] or ([TICKTICK_LIST_ID] if TICKTICK_LIST_ID else [])

# Terminal dashboard limits. These are intentionally larger than the e-ink
# dashboard limits because the terminal UI is viewed on a regular screen.
TERMINAL_MAX_EVENTS = 20
TERMINAL_MAX_TASKS = 20
TERMINAL_MAX_BIRTHDAYS = 10

# Dashboard JSON source URL/path. Used by terminal_dashboard.py when no
# explicit --input is provided.
DASHBOARD_JSON_URL = os.getenv("DASHBOARD_JSON_URL")

# Output JSON filename produced by the pipeline, served by the server, and
# uploaded to Cloudflare R2. Centralised so all consumers stay in sync.
DASHBOARD_JSON_FILENAME = "dashboard-v2.json"

# Server/continuous publisher settings.
# Seconds between automatic data/PNG refreshes. Default is 600 (10 minutes).
REFRESH_INTERVAL_SECONDS = int(os.getenv("REFRESH_INTERVAL_SECONDS", "600"))
# Device to generate in server mode: og, x, or both.
SERVER_DEVICE = os.getenv("SERVER_DEVICE", "both")
# HTTP port when serving the latest PNG. Default is 8080.
SERVER_PORT = int(os.getenv("SERVER_PORT", "8080"))

# Terminal dashboard refresh interval. The terminal dashboard loads the unified
# JSON from Cloudflare and refreshes at this interval. Default is 60 (1 minute).
TERMINAL_REFRESH_INTERVAL_SECONDS = int(os.getenv("TERMINAL_REFRESH_INTERVAL_SECONDS", "60"))


def r2_configured() -> bool:
    """Return True if all required Cloudflare R2 credentials are present."""
    return bool(
        os.getenv("CLOUDFLARE_R2_ENDPOINT")
        and os.getenv("CLOUDFLARE_R2_ACCESS_KEY_ID")
        and os.getenv("CLOUDFLARE_R2_SECRET_ACCESS_KEY")
        and os.getenv("CLOUDFLARE_R2_BUCKET_NAME")
    )
