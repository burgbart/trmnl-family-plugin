# TASKS.md — Liquid/TRMNL rewrite task breakdown

> Supersedes all prior task lists. See `PLAN.md` for the architecture and
> decisions behind this breakdown.
>
> Legend: **[∥ with X]** marks tasks that can run in parallel with task/group
> X because they don't share files or depend on each other's output. Tasks
> without a parallel marker are assumed sequential within their phase.
> Phases themselves are mostly sequential (each depends on the previous
> phase's output), except where noted.

## Phase 0 — Groundwork

- [x] 0.1 Add `python-liquid` to `requirements.txt`, verify it installs and
      renders a trivial template in the venv.
- [x] 0.2 **[∥ with 0.1]** Inventory the current `output/dashboard.png` /
      `dashboard_x.png` design: sections, spacing, grayscale levels, font
      choices. Write a short design-reference note (can live at the top of
      `templates/partials/` as a comment, or inline in this file) so Liquid
      templates can match the existing look. No code dependency on 0.1.

## Phase 1 — Liquid templates (dummy data)

Depends on Phase 0. Internally parallelizable once the partial contracts
(what variables each partial expects) are agreed in 1.1.

- [x] 1.1 Define the JSON→Liquid variable contract: decide what shape
      `dashboard-v2.json` data is exposed as inside templates (reuse the
      existing `dashboard-v2.json` schema from `src/serialization.py` — don't
      invent a new one). Write shared Liquid partials for each section:
      `templates/partials/weather.liquid`, `calendar.liquid`, `tasks.liquid`,
      `birthdays.liquid`. Contract documented in `templates/CONTRACT.md`.
- [x] 1.2 **[∥ with 1.3]** Build `templates/devices/og.liquid` (800×480,
      1-bit look) composing the Phase 1.1 partials.
- [x] 1.3 **[∥ with 1.2]** Build `templates/devices/x.liquid` (1872×1404,
      16-level grayscale look) composing the same partials.
- [x] 1.4 Prepare a dummy `dashboard-v2.json` fixture (reuse
      `src/data.py` dummy generators via `src/serialization.py`, don't
      hand-write a second fixture) for local template testing.
      (`templates/build_dummy_fixture.py` → `templates/dummy_dashboard.json`)

## Phase 2 — Local rendering pipeline

Scaffolding (2.1, 2.3) can start as soon as Phase 0 is done, using a
placeholder template — it does not need to wait for Phase 1 to finish, since
it only needs the `python-liquid` API surface, not final template content.
2.2 depends on 2.1 producing real output.

- [x] 2.1 **[∥ with 2.3]** `src/liquid_render.py`: `render(device_profile,
      data) -> str` using `python-liquid`, loading templates from
      `templates/devices/`.
- [x] 2.2 `export_preview.py` CLI: renders every configured device profile
      via 2.1 and writes one static `preview.html` containing all device
      frames (correct pixel dimensions, CSS filter to approximate grayscale
      levels) with a JS tab/toggle to switch between them. Depends on 2.1.
- [x] 2.3 **[∥ with 2.1]** Extend the device profile registry in
      `src/config.py` with whatever fields the Liquid/CSS frames need
      (resolution, grayscale level count, template filename) plus a stub
      entry to prove a third/future device can be added without code changes
      elsewhere.
- [x] 2.4 Run `export_preview.py` against the Phase 1 dummy fixture, open
      `preview.html` in a browser, and visually compare against the existing
      `output/dashboard.png` / `dashboard_x.png` — iterate on Phase 1
      templates until it's close enough. (Checkpoint before continuing —
      report back to the user for review, per the original request.)

- [x] 2.5 Make the OG device's grayscale level configurable instead of
      hardcoded to 2. `plan/DESIGN_REFERENCE.md` documents the original
      Pillow-rendered `output/dashboard.png` as **4-level** grayscale, but
      `OG_PROFILE.grayscale_levels` in `src/config.py` is currently `2`
      (which drives `export_preview.py`'s `contrast(4.5)` hard-threshold CSS
      approximation — a harsher look than the original PNG). Add an env var
      (e.g. `OG_GRAYSCALE_LEVELS`, default `2` to keep current behavior
      unchanged) read in `src/config.py` and applied to `OG_PROFILE`; when set
      to `4`, `export_preview.py`'s `_grayscale_filter_css` should pick the
      softer `contrast(2.2)` approximation already defined for the 4-level
      bucket, matching the original dashboard image. No change needed to the
      Liquid templates themselves — this is CSS-filter/config only, not a
      layout change. Requested 2026-07-20, after Phase 3 landed; do this
      before or alongside Phase 6 cleanup, whichever session picks it up
      next.
      (Update, later same day: default flipped from `2` to `4` per explicit
      user request, so OG now matches the original PNG's 4-level look
      out of the box; set `OG_GRAYSCALE_LEVELS=2` to get the harsher
      1-bit approximation instead.)

## Phase 3 — Server & CLI wiring

Depends on Phase 2 being verified. 3.1/3.2 touch different files from 3.3 and
can run in parallel with it.

- [x] 3.1 **[∥ with 3.2, 3.3]** Update `server.py`: background refresh loop
      calls `fetch_unified_data()` → write `dashboard-v2.json` → run
      `export_preview.py` logic → upload JSON (no PNG step). HTTP handler
      serves `/`, `/preview.html`, `/dashboard-v2.json` only.
- [x] 3.2 **[∥ with 3.1, 3.3]** Update `run_workflow_loop.py` the same way
      for the one-shot/cron use case.
- [x] 3.3 **[∥ with 3.1, 3.2]** Verify `terminal_dashboard.py` still works
      unchanged against the (unchanged) `dashboard-v2.json` schema — it doesn't
      touch templates at all, this is a regression check, not new code.
      (Confirmed via `pytest tests/test_terminal_dashboard.py` — unchanged,
      all passing.)

> Note: `src/pipeline.py` (which both 3.1 and 3.2 call into) dropped its PNG
> rendering step here, ahead of the original Phase 5.2 schedule, to avoid
> leaving `tests/test_pipeline.py` / `tests/test_server.py` red across two
> phases. Both were updated in this phase instead of Phase 5; Phase 5.2 now
> only needs `tests/test_run_workflow_loop.py` (checked — unaffected, no
> changes needed) plus whatever the `.github/workflows/generate-dashboard.yml`
> edit in 5.1 touches.

## Phase 4 — TRMNL integration

4.1 (code) and 4.2 (docs) touch different files and can run in parallel.
4.3 depends on both.

- [x] 4.1 **[∥ with 4.2]** Simplify `src/upload.py` to JSON-only (drop PNG
      upload functions and their call sites in `src/pipeline.py`).
- [x] 4.2 **[∥ with 4.1]** Write a public-repo-friendly setup guide (README
      section or `plan/TRMNL_SETUP.md`) covering, from scratch: creating a
      TRMNL account, creating a private plugin, choosing the **Polling**
      strategy, pointing it at your own published `dashboard-v2.json` URL, and
      pasting in `templates/devices/og.liquid` / `x.liquid`. Written for a
      stranger cloning the repo, not just future-us.
      (`plan/TRMNL_SETUP.md` — flagged as unverified pending 4.3.)
- [ ] 4.3 Manual verification: follow the guide against a real TRMNL account,
      paste the templates in, confirm the private plugin renders correctly
      against real (or dummy) published JSON. Fix template issues found here
      (e.g. how TRMNL actually exposes polled JSON fields — see "Open items"
      in `PLAN.md`).

## Phase 5 — GitHub Actions simplification

Independent of Phase 3; can start as soon as Phase 4.1 lands (needs the
JSON-only upload path). 5.1/5.2 touch different files.

- [x] 5.1 **[∥ with 5.2]** Update `.github/workflows/generate-dashboard.yml`:
      drop PNG render steps, keep `collect_unified_data.py` + JSON upload.
      Optionally add `export_preview.py` + upload `preview.html` as a
      workflow artifact for visual regression checking without a local run.
      (File didn't exist in the repo yet — created fresh, JSON-only, with
      `export_preview.py` + artifact upload included.)
- [x] 5.2 **[∥ with 5.1]** Update/remove tests that assumed PNG steps in the
      workflow path (`tests/test_run_workflow_loop.py`, `tests/test_pipeline.py`).
      (Already clean — no PNG references in either file, confirmed via grep;
      12/12 passing.)

## Phase 6 — Cleanup pass

Only start once Phases 1–5 are verified working end-to-end. These tasks
touch overlapping files (deletions), so treat as sequential to avoid
conflicting edits, though 6.1/6.2/6.4 could be split across two sessions if
careful about ordering.

- [x] 6.1 Delete `src/dashboard.py`, the Pillow dependency, PNG-specific
      tests (`tests/test_render.py` PNG assertions), and
      `output/dashboard.png` / `dashboard_x.png`. (Also deleted
      `run_local.py`, which was 100%-PNG and imported `src.dashboard`
      directly — `export_preview.py` is its replacement for local
      preview; trimmed the two `src.dashboard`-only tests out of
      `tests/test_reference_date.py` rather than the whole file, since
      most of that file is generic reference-date coverage.)
- [x] 6.2 Delete `assets/*.ttf` fonts *unless* Phase 4.3 showed TRMNL markup
      needs custom web fonts (check before deleting — see `PLAN.md` open
      items). (Skipped deletion: `templates/devices/og.liquid` and
      `x.liquid` both declare `@font-face` rules pointing at
      `../../assets/TRMNL{16,21}-{Bold,Regular}.ttf` for local preview
      rendering, so the fonts are actively used, not PNG-only leftovers.
      Whether TRMNL's own plugin editor also needs/supports them is still
      unverified — see task 4.3.)
- [x] 6.3 Trim any PNG-only fields left in `src/data.py` / `src/serialization.py`.
      (Checked both files — no PNG-only fields present, no change needed.)
- [x] 6.4 Rewrite `AGENTS.md` and `README.md` to describe the new
      architecture (data collection → JSON → TRMNL Liquid plugin, plus local
      preview and terminal dashboard) and remove references to PNG
      rendering.
- [x] 6.5 Remove Pillow from `requirements.txt` / `pyproject.toml`.
      (`pyproject.toml` had no dependency list to begin with — nothing to
      change there.)
