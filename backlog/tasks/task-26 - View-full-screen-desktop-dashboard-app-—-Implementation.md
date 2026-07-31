---
id: TASK-26
title: 'View: full-screen desktop dashboard app — Implementation'
status: To Do
assignee: []
created_date: '2026-07-31 20:52'
updated_date: '2026-07-31 20:59'
labels:
  - view
dependencies:
  - TASK-27
ordinal: 25000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Stage 5 ticket (plan/VIEW_PIPELINE.md) for the full-screen desktop dashboard app (proposal TASK-20). Start only after Design is Done and owner-approved. Implement per the approved design and the acceptance criteria set on this ticket in Stage 3; follow AGENTS.md conventions, run pytest -q, verify each AC with objective evidence.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Launching the app (CLI entry point or packaged .app) opens a native pywebview window rendering the full-screen dashboard view; verified by running it and inspecting the rendered window (screenshot or stated manual check)
- [ ] #2 The app runs the data cycle itself: collect (src/unified_fetcher) -> write dashboard-v2.json (src/serialization) -> upload to Cloudflare R2 (src/upload), at the configured refresh interval (default 10 minutes), so TRMNL and other views pick up fresh data; verified by running one cycle and confirming the JSON is written and the upload is invoked (or the R2 object updates)
- [ ] #3 The view renders from the locally collected dashboard-v2.json and shows all five sections: header (date/city/weather/refreshed), weather + 5-day forecast, calendar grouped by day (incl. empty days), tasks per list with due/overdue first, anniversaries footer; verified by comparing rendered sections against the JSON the app just produced
- [ ] #4 The view refreshes each cycle without restart; on collection or upload failure it keeps showing last good data with its stale timestamp, and missing R2 credentials do not break the view (local-only mode); verified by exercising the failure path (e.g. unset R2 credentials / unreachable endpoint)
- [ ] #5 Per-source error states: with errors.events/tasks/birthdays set in the payload, those sections render explicit '(!) Not loaded' states and no fabricated data; verified with a fixture payload containing errors
- [ ] #6 Styling follows the design system (design/tokens.json + design/README.md rules, light + dark themes following the OS setting), no ad-hoc colors; verified by tests/test_design_tokens.py passing and visual inspection of both themes
- [ ] #7 Credentials and configuration come from the existing env/.env configuration like the current pipeline (calendar, TickTick, R2); no new required variables beyond sensible defaults per AGENTS.md; verified by running with the existing .env
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Note: created out of ID order (before the Design ticket TASK-27) due to a CLI chaining error during creation; dependencies express the correct stage order: TASK-20 (proposal) -> TASK-25 (requirements) -> TASK-27 (design) -> TASK-26 (implementation).

Acceptance criteria set by Stage 3 (TASK-25), derived from the refined requirements recorded there.

Acceptance criteria replaced by requirements update v2 (owner, 31 Jul 2026, see TASK-25 notes): freshness default 10 min; the app runs the collect -> JSON -> R2 upload cycle itself (takes over the run_workflow_loop/server role); design system compliance is non-negotiable.
<!-- SECTION:NOTES:END -->
