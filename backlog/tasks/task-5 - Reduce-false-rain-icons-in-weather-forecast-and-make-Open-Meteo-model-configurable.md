---
id: TASK-5
title: >-
  Reduce false rain icons in weather forecast and make Open-Meteo model
  configurable
status: Done
assignee:
  - '@kimi'
created_date: '2026-07-23 11:40'
updated_date: '2026-07-23 11:54'
labels:
  - weather
  - open-meteo
  - config
  - forecast
dependencies:
  - TASK-4
priority: medium
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Open-Meteo daily weather_code reports the most severe condition of the day, and the current src/weather.py maps any drizzle/rain code directly to a rain icon. This makes the dashboard look gloomier than consumer forecasts like Google Weather. Investigation in TASK-4 and doc-1 identified that brief 0.1 mm drizzle events are causing full-day rain icons, and that the default Open-Meteo best_match model over-predicts drizzle for Amsterdam compared to the DWD icon_seamless model. Implement the recommended fix: (1) threshold daily icon selection on precipitation_probability_max and precipitation_sum before showing a rain icon for borderline codes, and (2) add an optional WEATHER_MODEL config variable to select a specific Open-Meteo model.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 src/weather.py thresholds rain icons for drizzle/shower codes based on precipitation probability and/or amount
- [x] #2 src/config.py exposes WEATHER_MODEL (default unset / best_match) and src/weather.py passes it to the Open-Meteo API
- [x] #3 .env.example documents WEATHER_MODEL with a sensible example for Europe
- [x] #4 Tests cover the new threshold logic and model parameter passthrough
- [x] #5 The decision doc doc-1 is referenced from the task notes
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Read .env.example and existing weather tests. 2. Add WEATHER_MODEL to src/config.py (default unset/best_match) and wire it into src/weather.py Open-Meteo request params. 3. Refactor select_weather_icon to accept precipitation_probability and threshold borderline drizzle/shower codes (51/53/80) to cloud/partly-cloudy icons when probability and/or amount are low. 4. Update .env.example with WEATHER_MODEL example (icon_seamless for Europe). 5. Add/update tests for threshold logic and model passthrough. 6. Run pytest and verify. 7. Record doc-1 reference in task notes and finalize.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation complete. Added BORDERLINE_RAIN_CODES threshold logic in src/weather.py for daily drizzle/shower codes (51/53/80): downgraded to cloud icon when precipitation_probability_max < 30% AND precipitation_sum < 1.0 mm. Added WEATHER_MODEL config in src/config.py and wired it into the Open-Meteo request params as 'models'. Updated .env.example with icon_seamless example for Europe. Added tests/test_weather.py with 23 tests covering threshold logic (low prob+amount, high prob, high amount, unknown prob, non-borderline codes, hourly exclusion) and model parameter passthrough (set/unset). Full test suite passed: 117/117. Decision doc reference: backlog/docs/weather/doc-1.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented TASK-5: thresholded daily drizzle/shower weather icons on precipitation probability and amount in src/weather.py, added optional WEATHER_MODEL config in src/config.py passed to Open-Meteo, documented it in .env.example, and added tests/test_weather.py. Verified with full pytest run: 117 passed.
<!-- SECTION:FINAL_SUMMARY:END -->
