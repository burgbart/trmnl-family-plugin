---
id: TASK-10
title: >-
  In Upcoming events and Anniversaries show when an event is Tomorrow instead of
  date
status: Done
assignee:
  - '@agent'
created_date: '2026-07-24 09:15'
updated_date: '2026-07-24 09:41'
labels: []
dependencies: []
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
In Upcoming events show when an event is Tomorrow instead of date. Also make Today and Tomorrow events clearer by showing the text bold, example:

*Tomorrow* 18:00   Photoshoot Belly   

Do the same with anniversaries. 

Also switch anniversary date with name so that it aligns event. Don't make the name of an anniversary bold by default like it is now.

Generate previews for validation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Upcoming events display 'Tomorrow' instead of the date when the event is the day after reference_date.
- [x] #2 The 'Today'/'Tomorrow' part of event times is bold; the time remains normal weight.
- [x] #3 Upcoming events never use an exclamation mark.
- [x] #4 Anniversaries display 'Tomorrow' / 'Today' when appropriate.
- [x] #5 Anniversary names are always bold.
- [x] #6 Anniversary dates (including Today/Tomorrow words) are non-bold.
- [x] #7 Anniversaries append the bold text ' (!)' only for Today/Tomorrow.
- [x] #8 Previews are regenerated and validated.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Compute tomorrow from meta.reference_date inside both device templates using Liquid date math (reference_date to seconds, add one day in seconds, format back to YYYY-MM-DD).\n2. In Upcoming events: bold the event-time text and render Today/Tomorrow labels when event_date matches reference_date or tomorrow; otherwise keep existing date formatting.\n3. In Anniversaries: swap name and date order so date appears first (aligning with events); bold the date only for Today/Tomorrow; remove default bold from anniversary names.\n4. Regenerate output/preview.html from templates/dummy_dashboard.json for visual validation.\n5. Run pytest to ensure no regressions.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Verified by rendering og and x templates against templates/dummy_dashboard.json: Tomorrow event shows 'Tomorrow 10:00' bold, Today events show 'Today HH:MM' bold, anniversaries show date-first layout with 'Tomorrow!' bold and non-bold names. pytest: 130 passed.

User feedback: revert anniversary name/date swap to original order, keep Today/Tomorrow text, and make only the Today!/Tomorrow! word bold with trailing (!).

Second iteration verified: reverted anniversary name/date swap to original order. Events show 'Today! 09:00' / 'Tomorrow! 10:00' with only Today!/Tomorrow! bold. Anniversaries show name-first with Today!/Tomorrow! bold. pytest: 130 passed.

User clarification: events keep Today/Tomorrow bold but NO exclamation mark. Anniversaries keep original order, name always bold, date non-bold, and append bold ' (!)' only for Today/Tomorrow.

Final iteration verified: events show 'Today 09:00' / 'Tomorrow 10:00' (no !, only Today/Tomorrow bold). Anniversaries show name bold, date non-bold, with bold ' (!)' appended for Today/Tomorrow (e.g. 'Mum Tomorrow (!)'). pytest: 130 passed.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Final implementation: events render 'Today'/'Tomorrow' bold with no exclamation mark; anniversaries keep original name-first layout with names always bold, dates non-bold, and a bold ' (!)' appended only for Today/Tomorrow. Updated og.liquid and x.liquid, regenerated previews, and verified with pytest (130 passed).
<!-- SECTION:FINAL_SUMMARY:END -->
