# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added `design/` — a design system for all non-TRMNL views, based on heimdalsecurity.com (TASK-15): `tokens.json` (W3C DTCG design tokens with a `theme.dark` override group and `motion` group), `index.html` (static style guide with dark-mode toggle, component inventory, motion and gradient-usage guidance, and a sample dashboard view), and `README.md` (principles and consumption rules).
- Added `tests/test_design_tokens.py` (TASK-17): the design system's guard. Fails on dangling token references, drift between `design/tokens.json` and the CSS custom properties in `design/index.html`, a colour variable with no token behind it, or any prescribed text/background pair falling below its WCAG AA threshold.
- Added accessibility tokens to `design/tokens.json` (TASK-17, design system v1.1.0): `color.text.muted` for light surfaces, `color.border.subtle` / `color.border.strong`, `color.focus.ring` / `color.focus.ring-dark`, per-state semantic `-surface` / `-text` pairs in both themes, and `breakpoint` tokens.
- Added an `icon` token group to `design/tokens.json` (TASK-18, design system v1.2.0): a fixed stroke width and a 4-step size scale (`sm`/`md`/`lg`/`xl`), plus a new Iconography section in `design/index.html` — an SVG sprite of five hand-drawn icons (weather, calendar, tasks, birthday, alert) shown at every size and recolored via `currentColor` (default, muted, interactive, on a dark chip).
- Added the full 8-state weather icon set to the design system (TASK-19, design system v1.3.0): `icon.weather` in `design/tokens.json` documents `sun`, `partly-cloudy`, `cloud`, `rain-light`, `rain`, `rain-heavy`, `thunder`, and `snow` — the exact identifiers `src/weather.py` produces — and `design/index.html` gained a matching sprite symbol per state (`icon-weather-<state>`) plus a Weather states grid in the Iconography section, so a non-TRMNL view can map `weather.icon` straight to a colorable glyph.
- Added an Accessibility section, a sticky section navigation with scroll-spy, copy-to-clipboard swatches showing measured contrast, a skip link, and a shareable `?theme=light|dark` parameter to `design/index.html` (TASK-17).
- Added `src/terminal_theme.py` and `tests/test_terminal_theme.py` (TASK-16): terminal color palette loaded from `design/tokens.json` (DTCG references resolved) with a fallback mirroring the tokens.
- Added a top-level `errors` object to `dashboard-v2.json` with keys `events`, `tasks`, and `birthdays`. Missing credentials and API failures are surfaced here instead of being hidden behind dummy data.
- Added error-state rendering in the Liquid partials (`partials/calendar.liquid`, `partials/tasks.liquid`, `partials/birthdays.liquid`) and device templates (`devices/og.liquid`, `devices/x.liquid`). Affected sections now display `(!) Not loaded` plus the error message.
- Added error-state rendering in the terminal dashboard (`terminal_dashboard.py`). Failed sources render red error panels.
- Added `DASHBOARD_JSON_FILENAME` constant in `src/config.py` as the single source of truth for the output JSON filename.
- Added `tests/test_unified_fetcher.py` and `tests/test_liquid_render.py` to cover missing-credential, API-failure, and error-rendering paths.
- Added full `dashboard-v2.json` parity to the terminal dashboard: current weather details (feels-like, alert, precipitation), a multi-day forecast, aggregated upcoming events and tasks, per-source calendar and task-list breakdowns, anniversary kinds, and the generated/synced timestamp with data age.

### Changed

- Fixed card-style components (`.card`, `.swatch`, `.nav`, `.list`, `.modal`, motion demo cards, the dashboard sample card) rendering with no visible boundary on plain sections in `design/index.html` (TASK-18): `--color-card` equals `--color-surface` in the light theme, so a card bordered in `border.subtle` (~1.2:1 against white) was invisible wherever it sat on an untinted section — most visibly, every card in the Motion section. Borders now use `border.strong`, which no longer depends on the surrounding section's background. Also fixed the gradient do/dont cards' description paragraph having no space before the button/icon/color-bar beneath it, and un-jumbled the motion demo cards' multi-line captions, which were centering each `<br>`-separated line independently.
- Fixed WCAG AA failures in the design system's light theme (TASK-17). `color.text.secondary` (`#ACB3D3`) was used for every muted paragraph, caption, placeholder and empty-state sentence on light surfaces at 2.07:1; it is now documented as dark-surfaces-only and replaced by `color.text.muted` (`#4B5791`, 6.84:1). Badges and alerts moved from solid state fills under white text (success was 1.99:1) to the `-surface` / `-text` pairs. Input and empty-state borders moved to `border.strong`, which clears the 3:1 non-text floor. `src/terminal_theme.py` is unaffected — it reads `text.secondary` against a dark terminal, which is the correct use.
- Updated `design/index.html` to be responsive down to 375px (fluid `clamp()` display type, breakpoints at 900px and 600px) and keyboard-accessible (a `:focus-visible` ring on every control, `aria-pressed` / `aria-current` / `aria-selected` state, reduced-motion also disabling smooth scrolling) (TASK-17).
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
