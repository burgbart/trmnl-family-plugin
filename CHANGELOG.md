# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added `design/` — a design system for all non-TRMNL views, based on heimdalsecurity.com (TASK-15): `tokens.json` (W3C DTCG design tokens with a `theme.dark` override group and `motion` group), `index.html` (static style guide with dark-mode toggle, component inventory, motion and gradient-usage guidance, and a sample dashboard view), and `README.md` (principles and consumption rules).
- Added `src/terminal_theme.py` and `tests/test_terminal_theme.py` (TASK-16): terminal color palette loaded from `design/tokens.json` (DTCG references resolved) with a fallback mirroring the tokens.
- Added a top-level `errors` object to `dashboard-v2.json` with keys `events`, `tasks`, and `birthdays`. Missing credentials and API failures are surfaced here instead of being hidden behind dummy data.
- Added error-state rendering in the Liquid partials (`partials/calendar.liquid`, `partials/tasks.liquid`, `partials/birthdays.liquid`) and device templates (`devices/og.liquid`, `devices/x.liquid`). Affected sections now display `(!) Not loaded` plus the error message.
- Added error-state rendering in the terminal dashboard (`terminal_dashboard.py`). Failed sources render red error panels.
- Added `DASHBOARD_JSON_FILENAME` constant in `src/config.py` as the single source of truth for the output JSON filename.
- Added `tests/test_unified_fetcher.py` and `tests/test_liquid_render.py` to cover missing-credential, API-failure, and error-rendering paths.
- Added full `dashboard-v2.json` parity to the terminal dashboard: current weather details (feels-like, alert, precipitation), a multi-day forecast, aggregated upcoming events and tasks, per-source calendar and task-list breakdowns, anniversary kinds, and the generated/synced timestamp with data age.

### Changed

- Updated `src/terminal_dashboard.py` to source all colors from `src/terminal_theme.py` (`THEME`) instead of ad-hoc Rich color names, aligning the terminal view with the design system palette (TASK-16). Event times use blue-light `#8EBEFF`, errors `#FF2626`, success `#6DCE43`, warnings `#FF5F00`, anniversaries `#A459FF`.
- Updated `tests/test_terminal_dashboard.py` to assert the theme error color instead of the literal `red` style (TASK-16).
- Updated `AGENTS.md` with the `design/` folder, the terminal theme module, and the convention that non-TRMNL views consume the design system.
- Renamed the produced/uploaded/served JSON artifact from `dashboard.json` to `dashboard-v2.json`. The dummy fixture `templates/dummy_dashboard.json` keeps its name and is now explicitly opt-in via `--input templates/dummy_dashboard.json`.
- Updated `src/unified_fetcher.py` to return empty data and populate `errors` when calendar or task credentials are missing or the API call fails. Weather still falls back to dummy data because it requires no credentials.
- Updated `src/serialization.py` to always include the `errors` object in the JSON payload.
- Updated `src/pipeline.py` to pass `UnifiedData.errors` into `build_dashboard_payload()`.
- Updated `src/json_loader.py` and `src/terminal_fetcher.py` to parse and carry `errors` for the terminal dashboard.
- Updated `.github/workflows/generate-dashboard.yml`, `.env.example`, `README.md`, `AGENTS.md`, `CLAUDE.md`, and `plan/*.md` to reference `dashboard-v2.json` and describe the new error-state behavior.
- Updated `templates/CONTRACT.md` to document the `errors` object and the new optional `error` parameter on affected partials.
- Regenerated `templates/dummy_dashboard.json` to include the new `errors` object.
- Updated `src/weather.py` and `tests/test_weather.py` to use daily `cloud_cover_mean` from Open-Meteo and recover a partly-cloudy icon for otherwise overcast days with low mean cloud cover (TASK-8).
- Updated `src/weather.py` and `tests/test_weather.py` to score borderline drizzle/shower codes (51/53/80) by probability-weighted expected amount (`precipitation_sum * precipitation_probability_max / 100`), smoothing the transition from cloud to rain-light to amount-based intensity (TASK-9).
- Updated `src/weather.py` and `tests/test_weather.py` so the weather alert is always populated: it describes expected rain/snow/thunder or reports `No rain expected today` when the day is dry (TASK-11).
- Updated `templates/devices/og.liquid` and `templates/devices/x.liquid` to show `Today`/`Tomorrow` labels for events and anniversaries, bold the `Today`/`Tomorrow` text in events, and append a bold ` (!)` marker to Today/Tomorrow anniversary dates while keeping anniversary names bold (TASK-10).
- Regenerated `templates/dummy_dashboard.json`, `preview.html`, and `output/preview.html` to reflect the new event and anniversary formatting.
