---
id: TASK-8
title: Use cloud_cover_mean to surface partly-cloudy daily forecast icons
status: Done
assignee:
  - '@kimi'
created_date: '2026-07-23 12:32'
updated_date: '2026-07-23 12:42'
labels:
  - weather
  - enhancement
dependencies:
  - TASK-6
references:
  - doc-2
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The dashboard currently renders a plain cloud icon on days where Open-Meteo reports WMO code 3 (Overcast) even when the daily mean cloud cover is in the partly-cloudy range. Update src/weather.py to fetch daily.cloud_cover_mean and refine code 3 daily icons: <65% cloud cover -> partly-cloudy, >=65% -> cloud. Keep existing rain/snow/thunder and precipitation-intensity logic unchanged. Add tests for the new behavior.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 src/weather.py fetches daily cloud_cover_mean from Open-Meteo
- [x] #2 Daily WMO code 3 with cloud_cover_mean < 65% renders partly-cloudy icon
- [x] #3 Daily WMO code 3 with cloud_cover_mean >= 65% renders cloud icon
- [x] #4 Codes 0/1/2 and all rain/snow/thunder codes keep their current icon behavior
- [x] #5 Tests cover the new cloud-cover threshold logic
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add daily.cloud_cover_mean to Open-Meteo request in src/weather.py. 2. Pass cloud_cover_mean into select_weather_icon for daily code 3, mapping <65% to partly-cloudy and >=65% to cloud. 3. Keep all rain/snow/thunder and precipitation-intensity logic unchanged. 4. Add tests covering the threshold and unchanged behaviors. 5. Run pytest tests/test_weather.py and full suite.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Verification passed: pytest tests/test_weather.py (31 passed) and full pytest suite (130 passed). cloud_cover_mean added to Open-Meteo daily request; code 3 daily icons refined at 65% threshold.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added daily.cloud_cover_mean to the Open-Meteo request in src/weather.py and refined daily WMO code 3 icon selection: <65% cloud cover renders partly-cloudy, >=65% renders cloud. Rain/snow/thunder and precipitation-intensity logic remain unchanged. Added tests for the threshold and the unchanged code paths; all 130 tests pass.
<!-- SECTION:FINAL_SUMMARY:END -->
