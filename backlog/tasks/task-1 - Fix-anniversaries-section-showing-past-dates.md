---
id: TASK-1
title: Fix anniversaries section showing past dates
status: Done
assignee:
  - '@kimi'
created_date: '2026-07-23 09:44'
updated_date: '2026-07-23 09:50'
labels: []
dependencies: []
references:
  - src/calendar.py
  - src/serialization.py
  - tests/test_calendar.py
modified_files:
  - src/calendar.py
  - tests/test_calendar.py
type: bug
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The anniversaries section is currently displaying an anniversary from yesterday. This suggests the collection or filtering logic may not be respecting the current date, or there may be a timezone normalization issue causing stale/offset dates to be included.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Anniversaries from dates before today are not displayed
- [x] #2 All-day anniversary events are compared against the current local date using the configured TIMEZONE
- [x] #3 Timed celebration events remain visible in the main event list as intended
- [x] #4 Tests cover anniversary filtering across reference dates and timezones
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add client-side date filtering in src/calendar.py _extract_birthdays: skip all-day celebration events whose normalized start date is before the configured reference date (compared in the configured TIMEZONE).\n2. Ensure timed celebration events are untouched: they are already excluded from _extract_birthdays by _is_anniversary_event and remain eligible for the main event list.\n3. Add tests covering: yesterday's anniversary excluded; today's/tomorrow's included; reference-date override honored; timezone normalization honored; timed party stays in main events.\n4. Run pytest and fix any regressions.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented client-side date filtering in _extract_birthdays using _normalize_dt to compare the event's local date against get_reference_date(). Added tests for yesterday exclusion, today/future inclusion, reference date override, and timezone normalization. Full test suite passes: 94 passed.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Fixed the anniversaries section by filtering out all-day celebration events whose normalized local start date is before the configured reference date in src/calendar.py. Timed celebration events continue to appear in the main event list because they are never routed through _extract_birthdays. Added four tests covering past-date exclusion, current/future inclusion, reference-date override, and timezone-aware date comparison. Verified with pytest (94 passed).
<!-- SECTION:FINAL_SUMMARY:END -->
