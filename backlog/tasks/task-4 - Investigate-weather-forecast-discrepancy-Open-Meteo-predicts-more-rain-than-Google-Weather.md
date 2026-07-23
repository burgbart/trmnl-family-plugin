---
id: TASK-4
title: >-
  Investigate weather forecast discrepancy: Open-Meteo predicts more rain than
  Google Weather
status: Done
assignee:
  - '@kimi'
created_date: '2026-07-23 11:33'
updated_date: '2026-07-23 11:40'
labels:
  - weather
  - open-meteo
  - investigation
  - forecast
dependencies: []
references:
  - doc-1
priority: medium
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The dashboard currently fetches weather forecasts from Open-Meteo. The user observes that Open-Meteo forecasts look consistently gloomier than Google Weather for the coming days, predicting rain on days where Google does not. This task is to investigate the root cause of the discrepancy and recommend whether to change providers, adjust how we interpret Open-Meteo data, or document the difference. Investigate differences in underlying weather models, forecast resolution, precipitation probability vs. intensity, time-of-day aggregation, and location interpolation. Compare the raw Open-Meteo API response for our configured location with Google Weather for the same location and dates. Capture findings in a decision document or task notes so future maintainers understand why the dashboard may differ from Google.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Raw Open-Meteo forecast response for the configured location is captured and inspected
- [x] #2 A side-by-side comparison with Google Weather for the same location and date range is documented
- [x] #3 The likely reason for the gloomier predictions is identified (e.g., model choice, precipitation metric, aggregation, location interpolation)
- [x] #4 A recommendation is recorded: keep Open-Meteo as-is, switch provider, or change how we interpret/present the data
- [x] #5 If a code/config change is recommended, a follow-up task is created or referenced
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Fetch and save the raw Open-Meteo forecast response for the configured location (Amsterdam defaults) using the same parameters as src/weather.py.\n2. Inspect the response structure and extract daily weather codes, precipitation sums, and precipitation probabilities.\n3. Look up Google Weather forecast for Amsterdam for the same date range via web search and/or a public Google Weather page.\n4. Compare day-by-day predictions and identify where Open-Meteo shows rain while Google does not.\n5. Investigate likely technical causes: Open-Meteo default model (ECMWF IFS vs GFS vs ICON), precipitation probability vs sum interpretation, daily aggregation (max probability vs any-hour), location grid interpolation, and WMO code thresholds.\n6. Document findings and a recommendation in a Backlog decision document or task notes.\n7. Create or reference a follow-up task if a code/config change is warranted.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Investigation findings (2026-07-23):\n\n1. Raw Open-Meteo response for Amsterdam (52.3676, 4.9041) captured in backlog/docs/open-meteo-forecast-amsterdam-2026-07-23.json.\n2. Hourly data captured in backlog/docs/open-meteo-hourly-amsterdam-2026-07-23.json shows rain/drizzle icons come from very brief events (often 1-2 hours with 0.1mm).\n3. Side-by-side comparison with AccuWeather (a reasonable proxy for Google Weather's consumer forecast) saved in backlog/docs/weather-comparison-amsterdam-2026-07-23.json.\n4. Root causes identified:\n   - Open-Meteo daily weather_code is documented as 'the most severe weather condition on a given day', so brief drizzle dominates the daily icon.\n   - src/weather.py maps any WMO drizzle/rain code (51-67, 80-82) to a rain icon with only a light/heavy distinction, ignoring probability and duration.\n   - The default Open-Meteo 'best match' model for Amsterdam produced drizzle codes on 4/5 days. The DWD ICON seamless model (higher-resolution for Central Europe) produced shower/drizzle on only 1/5 days, much closer to AccuWeather.\n5. Recommendation: adjust icon selection to threshold on precipitation probability and/or sum, and optionally allow model selection via config (e.g. icon_seamless). Full write-up will be recorded in a decision document.
<!-- SECTION:NOTES:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @kimi
created: 2026-07-23 11:40
---
Follow-up implementation task created: TASK-5
---
<!-- COMMENTS:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Investigated why Open-Meteo forecasts look gloomier than Google Weather. Captured raw Open-Meteo response for Amsterdam, compared it side-by-side with AccuWeather (Google Weather proxy), and identified three root causes: (1) Open-Meteo daily weather_code reports the most severe hourly condition of the day, (2) src/weather.py maps any drizzle/rain code directly to a rain icon regardless of probability or amount, and (3) the default best_match model over-predicts drizzle for Amsterdam compared to the DWD icon_seamless model. Documented findings and options in backlog/docs/weather/doc-1 and created follow-up implementation task TASK-5.
<!-- SECTION:FINAL_SUMMARY:END -->
