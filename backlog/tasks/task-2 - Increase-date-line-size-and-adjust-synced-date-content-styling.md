---
id: TASK-2
title: Increase date-line size and adjust synced/date-content styling
status: Done
assignee:
  - '@bart'
created_date: '2026-07-23 10:55'
updated_date: '2026-07-23 11:03'
labels: []
dependencies: []
references:
  - templates/devices/og.liquid
type: enhancement
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update the date header styling in the OG device template so the date line is larger and the synced timestamp/date-content layout matches the requested design. The synced timestamp font-size should be 13px.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 .date-line font-size is 24px in templates/devices/og.liquid
- [x] #2 .date-line no longer has a margin-top property
- [x] #3 .date-content no longer uses justify-content: center
- [x] #4 .synced uses the CSS block: position: absolute; right: 8px; bottom: 4px; font-size: 13px;
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update .date-line, .date-content, and .synced CSS in templates/devices/og.liquid per acceptance criteria. 2. Run export_preview.py against the dummy fixture to confirm the template still renders without Liquid errors. 3. Check acceptance criteria and mark task Done.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Verified by rendering preview.html with templates/dummy_dashboard.json; CSS values confirmed in rendered output.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated .date-line, .date-content, and .synced CSS in templates/devices/og.liquid per the design request; verified by running export_preview.py and inspecting the rendered preview.html.
<!-- SECTION:FINAL_SUMMARY:END -->
