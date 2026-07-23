# AGENTS.md — trmnl-home

This file documents the project for AI coding agents. It reflects the actual state of the codebase; do not assume anything not written here.

## Project overview

`trmnl-home` collects household data (weather, calendar, tasks, birthdays) and publishes it as a single JSON file (`dashboard-v2.json`). Rendering into an actual device image is **not** done by this repo — a [TRMNL private plugin](https://usetrmnl.com) polls the published JSON and renders it using Liquid templates (the same templating language Shopify/TRMNL use) that live in `templates/`. This repo also ships a local static-HTML preview (`export_preview.py` → `preview.html`) that renders the same Liquid templates via `python-liquid` so you can see the result without a physical device or a TRMNL account, plus a terminal dashboard that reads the same JSON.

The dashboard displays:

- Current date and weather (temperature, feels-like temperature, description, icon)
- Upcoming calendar events from Google Calendar
- Tasks from a shared TickTick list
- Upcoming anniversaries (birthdays and anniversary events) detected from Google Calendar events

When API credentials are missing or a data source fails, the dashboard renders an explicit **error state** (`(!) Not loaded`) for that section instead of silently showing fake data. The bundled dummy fixture (`templates/dummy_dashboard.json`) is still available for layout previews without credentials — pass it explicitly to `export_preview.py --input templates/dummy_dashboard.json`.

This is the result of a rewrite (see `plan/PLAN.md`) away from an earlier Pillow/PNG-rendering architecture (`src/dashboard.py`, `run_local.py` — both deleted) toward the JSON+Liquid model described above. `plan/PLAN.md` and `plan/TASKS.md` are the authoritative record of what changed and why; consult them before assuming a PNG-era pattern still applies.

The project supports three operational modes, all built on the same collect → JSON → [upload] flow:

1. **GitHub Actions** — `.github/workflows/generate-dashboard.yml`, manually triggered (`workflow_dispatch`) for now — no schedule; collects data and publishes `dashboard-v2.json` (+ `preview.html` as a workflow artifact) to Cloudflare R2.
2. **Local workflow loop** (`run_workflow_loop.py`) — runs the same collect → JSON → [upload] cycle on your own machine on a configurable interval.
3. **Long-running server** (`server.py`) — always-on process with an HTTP endpoint serving `dashboard-v2.json` and `preview.html` so a TRMNL device (or you, locally) can poll them.

## Technology stack

- **Language:** Python 3.11+
- **Templating:** [`python-liquid`](https://jg-rp.github.io/liquid/) — renders `templates/` for local preview; TRMNL renders the same markup independently
- **HTTP requests:** `requests`
- **Environment variables:** `python-dotenv`
- **Google Calendar:** `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`
- **Testing:** `pytest`
- **CI/CD:** GitHub Actions

## Project structure

```
.
├── .github/workflows/generate-dashboard.yml   # Scheduled CI workflow — collects data, publishes JSON
├── .venv/                                     # Python virtual environment
├── assets/*.ttf                               # TRMNL bitmap fonts, used by templates' @font-face rules
├── output/dashboard-v2.json                      # Latest collected data (local runs)
├── plan/
│   ├── PLAN.md                                # Current architecture plan (JSON + TRMNL Liquid plugin)
│   ├── TASKS.md                                # Phase/task checklist
│   ├── TRMNL_SETUP.md                          # Stranger-friendly TRMNL account/plugin setup guide
│   └── DESIGN_REFERENCE.md                    # Visual design notes carried over from the PNG era
├── templates/
│   ├── devices/og.liquid                      # TRMNL OG (800×480) full template
│   ├── devices/x.liquid                       # TRMNL X (1872×1404) full template
│   ├── build_dummy_fixture.py                 # Generates templates/dummy_dashboard.json for local testing
│   └── dummy_dashboard.json                   # Generated dummy fixture (committed for convenience)
├── src/
│   ├── config.py                              # Environment-based configuration, DeviceProfile registry
│   ├── data.py                                # Data classes + dummy data providers
│   ├── fetcher.py                             # Simple aggregator (used by tests/older code)
│   ├── json_loader.py                         # Loads and parses dashboard-v2.json (URL or local)
│   ├── liquid_render.py                       # render(device_profile, data) -> HTML, via python-liquid
│   ├── pipeline.py                            # Shared collect → JSON → [upload] cycle
│   ├── serialization.py                       # JSON serialisation helpers
│   ├── terminal_fetcher.py                    # Multi-source fetcher (used by unified_fetcher)
│   ├── terminal_dashboard.py                  # Terminal rendering + tab state
│   ├── unified_fetcher.py                     # Fetches all sources once, returns UnifiedData
│   ├── upload.py                              # Cloudflare R2 upload helper (JSON only)
│   ├── weather.py                             # Open-Meteo weather fetcher
│   ├── calendar.py                            # Google Calendar + birthday fetcher
│   └── ticktick.py                            # TickTick task fetcher
├── tests/
│   ├── conftest.py                            # Shared pytest fixtures / CLI options
│   ├── test_calendar.py                       # Calendar filtering tests
│   ├── test_collect_unified_data.py           # Serialisation payload structure tests
│   ├── test_fetcher.py                        # fetch_all return-type tests
│   ├── test_json_loader.py                    # JSON parse/load tests
│   ├── test_pipeline.py                       # src/pipeline.py tests
│   ├── test_reference_date.py                 # Reference date override tests
│   ├── test_run_workflow_loop.py              # run_workflow_loop.py arg / run tests
│   ├── test_server.py                         # server.py HTTP handler + refresh tests
│   ├── test_terminal_dashboard.py             # Terminal rendering + tab state tests
│   └── test_upload.py                         # R2 upload helper tests
├── collect_unified_data.py                    # CLI: collect unified data → dashboard-v2.json
├── export_preview.py                          # CLI: render all device templates → preview.html
├── run_workflow_loop.py                       # CLI: collect → JSON → [upload] loop
├── server.py                                  # CLI: long-running server (headless or terminal)
├── terminal_dashboard.py                      # CLI: interactive terminal dashboard
├── .env.example                               # Template for environment variables
├── pyproject.toml                             # pytest / project configuration
├── requirements.txt                           # Python dependencies
└── README.md                                  # Project overview and quick start
```

### Module responsibilities

- `src/config.py` — Loads settings from environment variables (via `.env` if present). Defines `DeviceProfile`s for each supported device (dimensions, grayscale level count, Liquid template filename), a stub third-device profile proving the registry scales without code changes, location, API credentials, and dashboard limits.
- `src/data.py` — Defines the core dataclasses (`Weather`, `CalendarEvent`, `Task`, `Birthday`) and provides dummy data generators used for the explicit dummy fixture and low-level `fetch_*_or_dummy()` fallbacks. `Birthday` includes a `kind` field (`birthday` or `anniversary`).
- `src/liquid_render.py` — `render(device_profile, data)` renders a device's Liquid template (from `templates/devices/`) against a parsed `dashboard-v2.json` dict using `python-liquid`.
- `src/unified_fetcher.py` — `fetch_unified_data()` fetches the union of dashboard + terminal sources once, deduplicates, and returns a `UnifiedData` object containing both aggregated and per-source (terminal) views. All callers that need to collect data use this instead of calling individual fetchers directly.
- `src/pipeline.py` — `run_pipeline(output_dir, devices, upload=False)` runs one full collect → JSON → [upload] cycle: calls `fetch_unified_data()`, writes `dashboard-v2.json`, renders `preview.html` via `export_preview.build_preview_html()`, and optionally uploads the JSON to R2. Used by `run_workflow_loop.py` and `server.py`.
- `src/json_loader.py` — `load_json(path_or_url)` fetches `dashboard-v2.json` from a URL or local path and deserialises it into dataclasses. `resolve_input_path()` determines the source (CLI arg → `DASHBOARD_JSON_URL` env var → Cloudflare public URL → `output/dashboard-v2.json`).
- `src/serialization.py` — `serialise()` recursively converts dataclasses/dates to JSON-safe types; `build_dashboard_payload()` builds the full JSON payload — the single source of truth for both the Liquid templates and the terminal dashboard.
- `src/fetcher.py` — Legacy `fetch_all()` aggregator, still used by older tests. New code should use `src/unified_fetcher.py`.
- `src/terminal_fetcher.py` — Defines `CalendarSource`, `TaskListSource`, and `TerminalData`; used by `unified_fetcher`. `fetch_terminal_data()` fetches directly from APIs (legacy path).
- `src/terminal_dashboard.py` — Renders the terminal UI with `rich` and tracks the currently selected calendar / task-list indices. `render()` accepts a `last_refreshed` datetime that is shown in the header. Pressing Tab advances both indices independently.
- `src/weather.py` — Fetches current weather from Open-Meteo and maps WMO weather codes to short descriptions/icons.
- `src/calendar.py` — Fetches upcoming events from Google Calendar using a service account. All datetimes are normalized to timezone-aware UTC to avoid naive/aware comparison errors. All-day events whose title contains a birthday keyword (`birthday`, `verjaardag`) or anniversary keyword (`anniversary`, `trouwdag`, `jubileum`) are treated as anniversaries: they are excluded from the main event list and shown only in the Anniversaries section. Timed events with one of these keywords in the title are treated as celebration parties and remain in the main event list. Celebrations are fetched with a wider 90-day lookahead and larger page size so they are not dropped behind busy calendars. The main event list can be filtered by attendee email (`CALENDAR_ATTENDEE_EMAILS`) and/or main calendar (`CALENDAR_MAIN_CALENDAR_ID`); when no filter is configured, all non-celebration events are shown. Anniversaries themselves are scoped by which calendar IDs are passed in (`GOOGLE_CALENDAR_IDS`/`TERMINAL_CALENDAR_IDS`), not by event creator/organizer — this lets shared calendars (e.g. a family calendar) hold events created by either household member.
- `src/ticktick.py` — Fetches tasks from a TickTick shared list using the TickTick Developer API. Due tasks are moved to the top while preserving the user's custom sort order within each group.
- `src/upload.py` — Cloudflare R2 upload helper for `dashboard-v2.json` (`upload_json` / `upload_to_r2`).
- `export_preview.py` — `build_preview_html(payload, device_names)` renders every configured device profile that has a template via `src/liquid_render.py`, then wraps each in an `<iframe srcdoc="...">` inside one static `preview.html` with a JS tab toggle and a CSS `filter` approximation of each device's grayscale level count.

## Configuration

Create a `.env` file in the project root (see `.env.example`). Key variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| `WEATHER_LATITUDE` | Weather location latitude | `52.3676` |
| `WEATHER_LONGITUDE` | Weather location longitude | `4.9041` |
| `CITY` | City label on dashboard | `Amsterdam` |
| `TIMEZONE` | Local timezone for displaying calendar event times (e.g. `Europe/Amsterdam`, `America/New_York`) | `Europe/Amsterdam` |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Path to JSON key file or raw JSON for Google service account | — |
| `GOOGLE_CALENDAR_IDS` | Comma-separated Google Calendar IDs | — |
| `CALENDAR_ATTENDEE_EMAILS` | Comma-separated attendee emails; events with at least one matching attendee are shown | — |
| `CALENDAR_MAIN_CALENDAR_ID` | Google Calendar ID treated as the main calendar; all events from this calendar are shown | — |
| `TICKTICK_ACCESS_TOKEN` | TickTick Developer API access token | — |
| `TICKTICK_LIST_ID` | TickTick project/list ID | — |
| `OG_GRAYSCALE_LEVELS` | OG device's grayscale level count, drives `export_preview.py`'s CSS contrast approximation (`2` = hard 1-bit threshold, `4` = softer, matching the original PNG-era design) | `4` |
| `REFERENCE_DATE` | Render/dashboard/test as if today were this date (DD-MM-YYYY) | today |
| `TERMINAL_CALENDAR_IDS` | Comma-separated calendar IDs for the terminal dashboard; falls back to `GOOGLE_CALENDAR_IDS` | — |
| `TERMINAL_TICKTICK_LIST_IDS` | Comma-separated TickTick list IDs for the terminal dashboard; falls back to `TICKTICK_LIST_ID` | — |
| `REFRESH_INTERVAL_SECONDS` | Seconds between automatic data/JSON refreshes in server mode | `60` |
| `SERVER_PORT` | HTTP port for serving `dashboard-v2.json`/`preview.html` in server mode | `8080` |
| `SERVER_DEVICE` | Device(s) included in the rendered `preview.html` in server mode: `og`, `x`, or `both` | `both` |
| `CLOUDFLARE_R2_ENDPOINT` | Cloudflare R2 S3 endpoint URL | — |
| `CLOUDFLARE_R2_ACCESS_KEY_ID` | R2 API token access key ID | — |
| `CLOUDFLARE_R2_SECRET_ACCESS_KEY` | R2 API token secret access key | — |
| `CLOUDFLARE_R2_BUCKET_NAME` | R2 bucket that stores `dashboard-v2.json` | — |
| `CLOUDFLARE_R2_PUBLIC_URL` | Public base URL for the bucket (custom domain or r2.dev) | — |

## Build and run commands

Use the existing virtual environment in `.venv/`:

```bash
# Activate the virtual environment (Git Bash / POSIX style)
source .venv/Scripts/activate

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# --- Data collection (writes output/dashboard-v2.json) ---
python collect_unified_data.py --output output/dashboard-v2.json

# --- Local static preview (renders Liquid templates -> preview.html) ---
python export_preview.py                                   # dummy fixture -> preview.html
python export_preview.py --input output/dashboard-v2.json     # real collected data

# --- Local loop (collect + preview + optional upload on an interval) ---
python run_workflow_loop.py                     # both devices, every 60 s
python run_workflow_loop.py --once              # single run and exit
python run_workflow_loop.py --device og --interval 300
python run_workflow_loop.py --upload            # also upload JSON to R2

# --- Long-running server ---
python server.py                        # headless + HTTP on port 8080; press 't' for terminal UI
python server.py --no-http              # headless without HTTP
python server.py --port 9000 --interval 60

# --- Interactive terminal dashboard (reads from Cloudflare or local JSON) ---
python terminal_dashboard.py
python terminal_dashboard.py --input output/dashboard-v2.json
python terminal_dashboard.py --env /path/to/.env.terminal

# --- Tests ---
pytest
pytest --date 23-12-2026

# --- Upload dashboard-v2.json to R2 (requires R2 credentials in env) ---
python -m src.upload output/dashboard-v2.json
```

## Testing instructions

Run the test suite with pytest:

```bash
pytest
```

Current test modules:

- `tests/test_reference_date.py` — Reference date override (`--date` / `REFERENCE_DATE`).
- `tests/test_calendar.py` — Calendar event filtering and anniversary extraction.
- `tests/test_terminal_dashboard.py` — Terminal tab-state logic and rendering helpers.
- `tests/test_json_loader.py` — JSON parse/load helpers and `resolve_input_path`.
- `tests/test_collect_unified_data.py` — `build_dashboard_payload` structure and serialisation.
- `tests/test_pipeline.py` — `src/pipeline.run_pipeline` (JSON written, `preview.html` rendered, upload called).
- `tests/test_run_workflow_loop.py` — Argument parsing and single-run behavior of `run_workflow_loop.py`.
- `tests/test_server.py` — HTTP handler (serve/404 for `preview.html`/`dashboard-v2.json`), arg parsing, and background refresh loop.
- `tests/test_upload.py` — R2 upload helpers (JSON only).
- `tests/test_fetcher.py` — `fetch_all` return types.

The project does not have integration tests for live Google Calendar or TickTick fetching because those require credentials. There's also no automated test that verifies TRMNL's actual rendering of the Liquid templates — that's a manual step (see `plan/TRMNL_SETUP.md`, `plan/TASKS.md` task 4.3).

## Code style guidelines

- Use `from __future__ import annotations` at the top of every Python file.
- Prefer type hints; the codebase uses both `typing.Optional`/`List` and newer `X | Y` union syntax.
- Data fetchers follow a consistent pattern: a real `fetch_*()` function plus a `fetch_*_or_dummy()` wrapper that catches exceptions and returns dummy data. The production pipeline (`src/unified_fetcher.fetch_unified_data()`) surfaces missing credentials and API failures as `errors` entries in the JSON payload rather than falling back to dummy data.
- Use dataclasses in `src/data.py` as the common data model across modules.
- Avoid adding new required environment variables; provide sensible defaults in `src/config.py`.

## Runtime architecture

The project supports three usage models, all built on the same collect → JSON → [upload] flow:

**Data collection:** `collect_unified_data.py` (and `src/pipeline.run_pipeline()`) call `src/unified_fetcher.fetch_unified_data()`, which fetches all configured sources once (weather from Open-Meteo, events from Google Calendar, tasks from TickTick) in parallel and returns a `UnifiedData` object. The result is serialised via `src/serialization.build_dashboard_payload()` to `dashboard-v2.json` and optionally uploaded to Cloudflare R2.

**Rendering:** rendering the actual device image happens **outside this repo**, inside a TRMNL private plugin configured with the Polling strategy against the published `dashboard-v2.json` URL, using the Liquid markup in `templates/devices/`. Locally, `export_preview.py` renders the same templates via `src/liquid_render.render()` (python-liquid) into a static `preview.html` for visual iteration without a TRMNL account. The terminal dashboard is a separate, simpler consumer that reads the same JSON directly (no Liquid involved).

### Usage model 1: GitHub Actions (stateless, manual)

`.github/workflows/generate-dashboard.yml` currently runs only on manual dispatch (no `schedule:` trigger — see the workflow file for how to re-add one):

1. Calls `collect_unified_data.py --output output/dashboard-v2.json` to write the JSON.
2. Calls `export_preview.py` to render `preview.html` (uploaded as a workflow artifact for visual regression checking, not published to R2).
3. Uploads `dashboard-v2.json` to Cloudflare R2 via `python -m src.upload`.

### Usage model 2: Local workflow loop

`run_workflow_loop.py` runs the same collect → JSON → [upload] cycle on a local machine:

- `python run_workflow_loop.py` loops every `REFRESH_INTERVAL_SECONDS` (default 60 s).
- `python run_workflow_loop.py --once` runs a single iteration (useful for cron/Task Scheduler).
- Each iteration: calls `src/pipeline.run_pipeline()`, which wraps collection, `preview.html` rendering, and optional upload.
- Errors in one iteration are logged to stderr; the loop continues on the next tick.

### Usage model 3: Long-running server

`server.py` is the always-on variant for self-hosted setups (Raspberry Pi, home server):

- Starts headless: first refresh runs synchronously, then a background thread runs `src/pipeline.run_pipeline()` every `REFRESH_INTERVAL_SECONDS`, logging each cycle to stderr. The HTTP server (`http.server`, port `SERVER_PORT`) runs in its own daemon thread and serves `preview.html`/`dashboard-v2.json` from the output directory.
- When stdin is an interactive terminal, a key-listener thread watches for `t`/`q`: pressing `t` opens the Rich terminal UI (same view as `terminal_dashboard.py`) in the main console via `rich.live.Live`; the background refresh thread keeps updating it via `live.update()`. Pressing `q` inside the terminal view closes it and returns to headless logging; `q` from headless quits the server. On non-interactive stdin (e.g. a daemon/service with no tty) the key listener is skipped and the server stays purely headless.
- `--no-http` disables the HTTP server.
- The HTTP server only serves `preview.html` and `dashboard-v2.json`. All other requests return 404.
- A real TRMNL device does **not** poll this server directly — it polls the published R2 URL via a TRMNL private plugin (see `plan/TRMNL_SETUP.md`). This server's HTTP endpoint exists for local/self-hosted preview and debugging.

### Interactive terminal dashboard

`terminal_dashboard.py` is a lightweight consumer — it reads `dashboard-v2.json` from a URL or local file (defaulting to `DASHBOARD_JSON_URL` → Cloudflare → `output/dashboard-v2.json`). A background thread reloads the JSON every `TERMINAL_REFRESH_INTERVAL_SECONDS` (default 60 s) without blocking key handling or resetting the tab selection. The "last refreshed" timestamp is shown in the header.

## Deployment / automation

### GitHub Actions variant

The file `.github/workflows/generate-dashboard.yml` defines a workflow that:

- Runs only on manual dispatch (`workflow_dispatch`) — no `schedule:` trigger is configured
- Sets up Python and installs `requirements.txt`
- Runs `collect_unified_data.py`, then `export_preview.py`
- Uploads `output/dashboard-v2.json` to Cloudflare R2, and `output/preview.html` as a workflow artifact

The R2 bucket contains exactly one object: `dashboard-v2.json`. Each run overwrites it so the TRMNL plugin's poll URL stays stable.

### Local / server variant

For self-hosted setups:

```bash
# One-shot (cron / Task Scheduler):
python run_workflow_loop.py --once --upload

# Continuous loop (uploads each cycle):
python run_workflow_loop.py --upload

# Server with HTTP endpoint on port 8080 (press 't' for the terminal UI):
python server.py --upload
```

### TRMNL private plugin setup

See `plan/TRMNL_SETUP.md` for the full stranger-friendly walkthrough: creating a TRMNL account, creating a private plugin with the Polling strategy pointed at your published `dashboard-v2.json` URL, and pasting in `templates/devices/og.liquid` / `x.liquid`. This step has not yet been verified end-to-end against a real TRMNL account (`plan/TASKS.md` task 4.3) — treat the guide as the expected flow, not a confirmed one, until that's done.

## Cloudflare R2 upload

The GitHub Actions variant uploads `dashboard-v2.json` to Cloudflare R2. Required repository secrets:

- `CLOUDFLARE_R2_ENDPOINT` — `https://<account_id>.r2.cloudflarestorage.com`
- `CLOUDFLARE_R2_ACCESS_KEY_ID` — R2 API token access key ID
- `CLOUDFLARE_R2_SECRET_ACCESS_KEY` — R2 API token secret access key
- `CLOUDFLARE_R2_BUCKET_NAME` — bucket that stores `dashboard-v2.json`
- `CLOUDFLARE_R2_PUBLIC_URL` — public base URL (custom domain or r2.dev) used to build the poll URL TRMNL is configured against

Upload logic lives in `src/upload.py`. The module can also be run locally for testing:

```bash
python -m src.upload output/dashboard-v2.json
```

## Security considerations

- **Never commit `.env`** — it is listed in `.gitignore`. Keep API keys and service account JSON in repository secrets for CI.
- The `GOOGLE_SERVICE_ACCOUNT_JSON` variable can contain either a file path or the raw JSON. In CI, it is passed as a repository secret.
- `TICKTICK_ACCESS_TOKEN` is sent as a Bearer token in the `Authorization` header.
- Weather data is fetched from the public Open-Meteo API and requires no API key.

## Notes for agents

- `README.md` now contains the human-facing project documentation. For agent-focused details, build steps, and conventions, use this file and the files in `plan/`.
- `plan/PLAN.md` is the authoritative architecture record; `plan/TASKS.md` tracks phase-by-phase progress and notes any deviations from the original plan (e.g. tasks completed earlier/later than originally scheduled, or skipped with a reason). Check both before assuming an "Open item" listed there has been resolved.
- The codebase intentionally supports running without credentials by rendering explicit error states for unconfigured sources. If you add a new data source, follow the `fetch_*_or_dummy` fallback pattern for low-level fetchers, but surface missing credentials / failures through the `errors` object in `src/unified_fetcher.py`.
- Rendering (device-specific layout, grayscale dithering) happens in `templates/*.liquid`, not in Python. If you add a new device profile in `src/config.py`, it needs a corresponding `templates/devices/<name>.liquid` template before `src/liquid_render.py`/`export_preview.py` can render it — profiles without a template (`template_filename=None`, see `STUB_PROFILE`) are valid and are skipped by both.
- This project uses Backlog.md for task management. At the start of each task-focused session, run `backlog instructions overview`. Prefer `backlog task create`, `backlog task edit`, and `backlog board` over hand-editing files in `backlog/`.

<!-- BACKLOG.MD GUIDELINES START -->
<!-- backlog.md-instructions-version: 1.48.0 -->
<CRITICAL_INSTRUCTION>

## Backlog.md Workflow

This project uses Backlog.md for task and project management.

**For every user request in this project, run `backlog instructions overview` before answering or taking action.**

Use the overview to decide whether to search, read, create, or update Backlog tasks.

Before task lifecycle actions, read the matching detailed guide:
- `backlog instructions task-creation` before creating or splitting tasks
- `backlog instructions task-execution` before planning, changing status or assignee, adding a plan or implementation notes, or implementing task work
- `backlog instructions task-finalization` before checking acceptance criteria, writing final summaries, or moving tasks to terminal statuses

Use `backlog <command> --help` before running unfamiliar commands. Help shows options, fields, and examples.

Do not edit Backlog task, draft, document, decision, or milestone markdown files directly. Use the `backlog` CLI so metadata, relationships, and history stay consistent.

</CRITICAL_INSTRUCTION>
<!-- BACKLOG.MD GUIDELINES END -->
