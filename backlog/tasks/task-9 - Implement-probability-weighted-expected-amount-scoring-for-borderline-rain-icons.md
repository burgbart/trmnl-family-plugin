---
id: TASK-9
title: >-
  Implement probability-weighted expected-amount scoring for borderline rain
  icons
status: Done
assignee:
  - '@agent'
created_date: '2026-07-23 13:04'
updated_date: '2026-07-24 09:55'
labels:
  - weather
  - enhancement
  - forecast
dependencies:
  - TASK-7
documentation:
  - backlog/docs/weather/doc-3 - Precipitation-weighted-rain-icon-selection.md
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update src/weather.py to use the probability-weighted expected-amount scoring proposed in doc-3 for borderline drizzle/shower codes (51/53/80). Replace the current binary downgrade (cloud when both prob < 30% and amount < 1.0 mm) with a smooth threshold based on precipitation_sum * precipitation_probability_max / 100. Keep non-borderline rain codes on the existing amount-based intensity thresholds.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 src/weather.py computes expected_amount = precipitation_sum * (precipitation_probability_max / 100) for borderline codes
- [x] #2 Borderline code with expected_amount < 0.2 mm renders cloud icon
- [x] #3 Borderline code with 0.2 <= expected_amount < 1.5 mm renders rain-light icon
- [x] #4 Borderline code with expected_amount >= 1.5 mm falls through to existing amount-based thresholds
- [x] #5 Non-borderline rain codes (61/63/65/66/67/81/82) keep their current amount-based behavior
- [x] #6 Tests cover the new expected-amount thresholds and unchanged non-borderline behavior
- [x] #7 Existing tests in tests/test_weather.py continue to pass
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented in worktree task/TASK-9 and merged into main. pytest: 138 passed after merge.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Replaced binary borderline downgrade in src/weather.py with probability-weighted expected_amount scoring for codes 51/53/80. Added tests for cloud/rain-light/fall-through thresholds and non-borderline behavior. Merged via worktree task/TASK-9; all tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
