---
id: TASK-6
title: Investigate partly cloudy weather state vs Google Weather
status: Done
assignee:
  - '@kimi'
created_date: '2026-07-23 12:18'
updated_date: '2026-07-23 12:33'
labels:
  - weather
  - open-meteo
  - research
  - icons
dependencies: []
references:
  - doc-2
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The dashboard currently shows mostly sunny/cloudy/rain icons. Google Weather reports partly cloudy states that the dashboard does not seem to surface. Investigate whether Open-Meteo provides partly-cloudy data (WMO codes 1/2, cloud cover fractions, or other fields), why it might be missing from the rendered dashboard, and whether the device templates or icon mapping need changes. Capture a side-by-side comparison for the configured location and document a recommendation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Open-Meteo fields that represent partly cloudy conditions are identified and documented
- [x] #2 Current src/weather.py icon mapping and templates/devices icon usage are reviewed for partly-cloudy support
- [x] #3 A side-by-side comparison with Google Weather for the configured location shows where the dashboard diverges
- [x] #4 A recommendation is recorded: add/mapping/icon change, model change, or no action needed
- [x] #5 If a code/config change is recommended, a follow-up implementation task is created or referenced
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Read src/weather.py and templates/devices/*.liquid to understand current WMO code mapping and partly-cloudy icon support.\n2. Fetch live Open-Meteo data for the configured location, including cloud_cover and cloud_cover_mean fields.\n3. Compare Open-Meteo daily codes + cloud cover against Google/AccuWeather-style descriptions to identify where partly-cloudy states are lost.\n4. Document findings and a recommendation in the task and/or backlog/docs.\n5. If a code/config change is recommended, create a follow-up implementation task.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Investigation complete. Open-Meteo provides partly-cloudy data via WMO codes 1/2 and cloud_cover / cloud_cover_mean fields. src/weather.py already maps 1/2 to partly-cloudy and both device templates already include a partly-cloudy SVG. The divergence comes from Open-Meteo's daily weather_code being the most-severe hour: days with mean cloud cover in the partly-cloudy range (e.g., 58%, 76%) are reported as code 3 (Overcast), so the dashboard renders a cloud icon. Side-by-side for Amsterdam (2026-07-23 to 2026-07-27) shows two days where AccuWeather reports partly-cloudy/mostly-sunny but the dashboard shows cloud. Recommendation: fetch daily.cloud_cover_mean and refine code 3 daily icons: <65% -> partly-cloudy, >=65% -> cloud. Full write-up in doc-2.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Investigated why partly-cloudy states do not appear on the dashboard. Open-Meteo provides partly-cloudy data via WMO codes 1/2 and cloud_cover/cloud_cover_mean; src/weather.py and both device templates already support the partly-cloudy icon. The real cause is that Open-Meteo's daily weather_code reports the most-severe hour, so days with partly-cloudy mean cloud cover (e.g., 58%, 76%) are reported as code 3 (Overcast) and rendered as cloud. A side-by-side comparison for Amsterdam (2026-07-23 to 2026-07-27) against AccuWeather shows two days where the dashboard shows cloud but the consumer forecast reports partly-cloudy/mostly-sunny. Documented in backlog/docs/doc-2. Recommendation: fetch daily.cloud_cover_mean and refine code-3 daily icons (<65% -> partly-cloudy, >=65% -> cloud). Follow-up implementation task TASK-8 created.
<!-- SECTION:FINAL_SUMMARY:END -->
