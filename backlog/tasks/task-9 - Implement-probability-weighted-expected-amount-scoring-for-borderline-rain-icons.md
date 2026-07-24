---
id: TASK-9
title: >-
  Implement probability-weighted expected-amount scoring for borderline rain
  icons
status: To Do
assignee: []
created_date: '2026-07-23 13:04'
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
- [ ] #1 src/weather.py computes expected_amount = precipitation_sum * (precipitation_probability_max / 100) for borderline codes
- [ ] #2 Borderline code with expected_amount < 0.2 mm renders cloud icon
- [ ] #3 Borderline code with 0.2 <= expected_amount < 1.5 mm renders rain-light icon
- [ ] #4 Borderline code with expected_amount >= 1.5 mm falls through to existing amount-based thresholds
- [ ] #5 Non-borderline rain codes (61/63/65/66/67/81/82) keep their current amount-based behavior
- [ ] #6 Tests cover the new expected-amount thresholds and unchanged non-borderline behavior
- [ ] #7 Existing tests in tests/test_weather.py continue to pass
<!-- AC:END -->
