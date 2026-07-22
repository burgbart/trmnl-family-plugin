# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added a top-level `errors` object to `dashboard-v2.json` with keys `events`, `tasks`, and `birthdays`. Missing credentials and API failures are surfaced here instead of being hidden behind dummy data.
- Added error-state rendering in the Liquid partials (`partials/calendar.liquid`, `partials/tasks.liquid`, `partials/birthdays.liquid`) and device templates (`devices/og.liquid`, `devices/x.liquid`). Affected sections now display `(!) Not loaded` plus the error message.
- Added error-state rendering in the terminal dashboard (`terminal_dashboard.py`). Failed sources render red error panels.
- Added `DASHBOARD_JSON_FILENAME` constant in `src/config.py` as the single source of truth for the output JSON filename.
- Added `tests/test_unified_fetcher.py` and `tests/test_liquid_render.py` to cover missing-credential, API-failure, and error-rendering paths.

### Changed

- Renamed the produced/uploaded/served JSON artifact from `dashboard.json` to `dashboard-v2.json`. The dummy fixture `templates/dummy_dashboard.json` keeps its name and is now explicitly opt-in via `--input templates/dummy_dashboard.json`.
- Updated `src/unified_fetcher.py` to return empty data and populate `errors` when calendar or task credentials are missing or the API call fails. Weather still falls back to dummy data because it requires no credentials.
- Updated `src/serialization.py` to always include the `errors` object in the JSON payload.
- Updated `src/pipeline.py` to pass `UnifiedData.errors` into `build_dashboard_payload()`.
- Updated `src/json_loader.py` and `src/terminal_fetcher.py` to parse and carry `errors` for the terminal dashboard.
- Updated `.github/workflows/generate-dashboard.yml`, `.env.example`, `README.md`, `AGENTS.md`, `CLAUDE.md`, and `plan/*.md` to reference `dashboard-v2.json` and describe the new error-state behavior.
- Updated `templates/CONTRACT.md` to document the `errors` object and the new optional `error` parameter on affected partials.
- Regenerated `templates/dummy_dashboard.json` to include the new `errors` object.
