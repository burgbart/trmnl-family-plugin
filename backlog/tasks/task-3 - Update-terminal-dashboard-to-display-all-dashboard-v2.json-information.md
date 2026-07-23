---
id: TASK-3
title: Update terminal dashboard to display all dashboard-v2.json information
status: Done
assignee:
  - '@kimi'
created_date: '2026-07-23 11:12'
updated_date: '2026-07-23 12:11'
labels: []
dependencies: []
references:
  - src/terminal_dashboard.py
  - src/terminal_fetcher.py
  - src/serialization.py
  - CHANGELOG.md
type: enhancement
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The terminal dashboard currently only shows a subset of the data published in dashboard-v2.json. It should be updated so the terminal view contains all the new information that the device templates display: current weather details (including feels-like, alert, and forecast), aggregated upcoming events and tasks, per-source calendar and task-list breakdowns, anniversary kinds, and the generated/synced timestamp. This ensures parity between the TRMNL device preview and the local terminal dashboard.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Terminal dashboard renders the current weather section including temperature, feels-like, description, alert, and a multi-day forecast
- [x] #2 Terminal dashboard renders the aggregated upcoming events list from the top-level events array
- [x] #3 Terminal dashboard renders the aggregated tasks list from the top-level tasks array, including due-date indicators
- [x] #4 Terminal dashboard continues to show per-source calendar and task-list breakdowns, or provides a clear way to access them
- [x] #5 Terminal dashboard distinguishes birthday and anniversary kinds in the anniversaries section
- [x] #6 Terminal dashboard displays the generated/synced timestamp and data age
- [x] #7 CHANGELOG.md is updated under [Unreleased] describing the terminal dashboard changes
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Extend TerminalData with top-level events/tasks fields and update json_loader parsing for weather forecast/alert/precip and aggregated events/tasks. 2. Update src/terminal_dashboard.py render layout to include weather forecast, aggregated events/tasks, per-source breakdowns, anniversary kinds, and data age. 3. Update server.py to pass events/tasks into TerminalData. 4. Update tests/test_terminal_dashboard.py to cover new render output. 5. Update CHANGELOG.md. 6. Run pytest and finalize.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation complete. Extended TerminalData with events/tasks fields and updated json_loader to parse weather forecast/alert/precipitation plus top-level events/tasks. Restructured terminal_dashboard.py render layout: header shows weather alert and data age, a compact horizontal forecast panel sits above the events/tasks lists, each list column shows the aggregated dashboard view followed by per-source breakdowns, and the footer distinguishes birthday/anniversary kinds. Updated server.py to pass events/tasks into TerminalData. Updated tests/test_terminal_dashboard.py with new coverage and adjusted footer assertions for the new kind label. Updated CHANGELOG.md under [Unreleased]. Full test suite passed: 122/122.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented TASK-3: terminal dashboard now displays all dashboard-v2.json information — current weather with alert/forecast, aggregated events/tasks, per-source calendar/task-list breakdowns, anniversary kinds, and generated/synced timestamp with data age. Updated src/terminal_fetcher.py, src/json_loader.py, src/terminal_dashboard.py, server.py, tests/test_terminal_dashboard.py, and CHANGELOG.md. Verified with full pytest run: 122 passed.
<!-- SECTION:FINAL_SUMMARY:END -->
