---
id: TASK-3
title: Update terminal dashboard to display all dashboard-v2.json information
status: To Do
assignee: []
created_date: '2026-07-23 11:12'
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
- [ ] #1 Terminal dashboard renders the current weather section including temperature, feels-like, description, alert, and a multi-day forecast
- [ ] #2 Terminal dashboard renders the aggregated upcoming events list from the top-level events array
- [ ] #3 Terminal dashboard renders the aggregated tasks list from the top-level tasks array, including due-date indicators
- [ ] #4 Terminal dashboard continues to show per-source calendar and task-list breakdowns, or provides a clear way to access them
- [ ] #5 Terminal dashboard distinguishes birthday and anniversary kinds in the anniversaries section
- [ ] #6 Terminal dashboard displays the generated/synced timestamp and data age
- [ ] #7 CHANGELOG.md is updated under [Unreleased] describing the terminal dashboard changes
<!-- AC:END -->
