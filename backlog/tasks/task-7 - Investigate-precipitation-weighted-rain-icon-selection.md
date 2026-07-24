---
id: TASK-7
title: Investigate precipitation-weighted rain icon selection
status: Done
assignee:
  - '@kimi'
created_date: '2026-07-23 12:18'
updated_date: '2026-07-23 13:05'
labels:
  - weather
  - open-meteo
  - research
  - forecast
dependencies:
  - TASK-5
references:
  - doc-1
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A specific day (Sunday in the current forecast) is rendered as rainy while Google Weather shows it as a rainy day with only a single light-drop indicator, suggesting Google weights precipitation amount by probability of precipitation. Investigate how consumer forecasts represent low-confidence light rain and propose a scoring function for the dashboard that combines precipitation probability and amount to decide when a day deserves a full rain icon versus a lighter or non-rain icon. Compare the proposed scoring against recent Open-Meteo responses and the current threshold logic implemented in TASK-5.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The Sunday (or other representative) forecast day is captured from Open-Meteo with all available precipitation fields
- [x] #2 At least one plausible scoring formula is proposed (e.g., precipitation_sum * precipitation_probability_max or similar)
- [x] #3 The proposed scoring is applied to recent forecast data and compared with the current threshold approach
- [x] #4 A recommendation is recorded: adopt a new scoring approach, tune thresholds, or keep current logic
- [x] #5 If a code/config change is recommended, a follow-up implementation task is created or referenced
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Query Open-Meteo for Amsterdam with extended precipitation fields (daily precipitation_sum, precipitation_probability_max, precipitation_hours; hourly precipitation, precipitation_probability, weather_code) to capture a representative forecast day. 2. Propose scoring formulas that combine precipitation amount and probability (e.g., amount * probability, amount weighted by probability, expected wet-hours). 3. Apply formulas to the captured data and compare icon outcomes against the current TASK-5 borderline-rain threshold logic in src/weather.py. 4. Document findings and a recommendation in backlog/docs/doc-1 or a new doc. 5. Create a follow-up implementation task if a code/config change is recommended.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Captured Amsterdam 7-day forecast with daily precipitation_sum, precipitation_probability_max, precipitation_hours and hourly precipitation/probability/cloud cover. Saved raw data to backlog/docs/weather/open-meteo-precipitation-investigation.json and synthetic scenarios to backlog/docs/weather/synthetic-precipitation-scenarios.json. Proposed expected-amount and wet-hours scoring functions, compared against current TASK-5 thresholds in doc-3.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Investigated precipitation-weighted rain icon selection. Captured Open-Meteo forecast data with all precipitation fields, proposed expected-amount and wet-hours scoring functions, and compared them against the current TASK-5 borderline-rain thresholds. Recommended adopting probability-weighted expected-amount scoring for borderline codes (51/53/80) with smooth thresholds, keeping non-borderline rain codes on amount-based intensity. Findings recorded in doc-3; follow-up implementation task TASK-9 created.
<!-- SECTION:FINAL_SUMMARY:END -->
