---
id: TASK-19
title: Add full weather icon set to the design system
status: Done
assignee:
  - '@claude'
created_date: '2026-07-31 14:30'
updated_date: '2026-07-31 14:39'
labels: []
dependencies: []
references:
  - design/tokens.json
  - design/index.html
  - design/README.md
ordinal: 18000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up to TASK-18. The Iconography section currently shows a single generic weather glyph (a sun-and-cloud combo) as a stand-in for the whole domain. The dashboard actually has 8 distinct weather states, defined in src/weather.py and already illustrated as 1-bit TRMNL glyphs in templates/devices/og.liquid and x.liquid: sun, partly-cloudy, cloud, rain-light, rain, rain-heavy, thunder, snow. Any non-TRMNL weather view (web, widget, AI surface) needs a colorable icon for every one of these states, not just one representative icon, and the design system currently does not provide that.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 design/index.html Iconography section provides one hand-drawn icon per weather state (sun, partly-cloudy, cloud, rain-light, rain, rain-heavy, thunder, snow), each distinguishable from the others at a glance and consistent with the existing icon grid style (24x24, currentColor, 1.75 stroke)
- [x] #2 Icons are defined once as SVG sprite symbols (matching the existing pattern) and referenced by the same icon.state.<name> naming implied by src/weather.py, so an AI agent building a new view can map a weather.icon value straight to a symbol id
- [x] #3 design/tokens.json documents the weather icon set (the 8 valid state names) so it is machine-readable, matching the identifiers already used in src/weather.py
- [x] #4 design/README.md documents the weather icon set and the version bump
- [x] #5 pytest and tests/test_design_tokens.py pass; the new icons render correctly in both themes
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Design 8 hand-drawn line icons on the existing 24x24 grid, one per src/weather.py state: sun, partly-cloudy, cloud, rain-light, rain, rain-heavy, thunder, snow. Differentiate rain-light, rain and rain-heavy by droplet count and thunder by an added bolt, matching the visual logic already used in the TRMNL glyphs but redrawn as colorable outlines instead of 1-bit fills.
2. Add each as a symbol in the existing SVG sprite in design/index.html.
3. Replace the single generic Weather tile in the Iconography Set grid with all 8 weather-state tiles, each labeled with its state name.
4. Add an icon.weather group to design/tokens.json listing the 8 valid state names, matching src/weather.py, with a description noting the symbol id pattern, for AI and machine consumption.
5. Update design/README.md and CHANGELOG.md with the weather icon set and the version bump. Update the hero token-count fallback for the new tokens.
6. Run pytest, verify the guard passes, and render the new icons in both themes.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Reused the existing partly-cloudy combo icon (sun peeking from behind a cloud) as icon-weather-partly-cloudy rather than redrawing it, since it already matched the intended visual. Added 7 new symbols sharing one base cloud path (shifted from the combo icon's position so it sits centered with room below for accessories): cloud alone, rain-light/rain/rain-heavy differentiated by 1/2/3 short diagonal drop lines, thunder by a small filled bolt beneath the cloud (sized up once after the first render looked too thin next to the 1.75 stroke outline), and snow by three small filled dots. sun is a plain circle with 8 short rays, distinct from partly-cloudy at a glance.

tokens.json: added icon.weather with one string-typed leaf per state, each valued as the literal weather.icon string (e.g. rain-light -> rain-light), with a single group-level $description stating the icon-weather- + value symbol-id rule once rather than repeating it 8 times. Bumped the design system to 1.3.0 (tokens.json meta, README, and the three version strings in index.html: title, header badge, hero eyebrow) and updated the hero token-count fallback 108 -> 116 for the 8 new leaves.

Also caught and fixed 3 stale v1.1 version strings left over from TASK-18 (title, header brand badge, hero eyebrow) that should have been bumped to v1.2 then and were not.

Verified: pytest 259 passed (118 design-token tests, unchanged in count since icon.weather adds string tokens, not colors, so no new guard pairs were needed). Rendered the Weather states grid in both themes: all 8 icons are distinguishable at a glance, thunder and snow accents legible against the cloud outline. Re-checked the 375px iframe layout holds with the larger icon grid (clientWidth equals scrollWidth, no horizontal overflow).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added the complete 8-state weather icon set (sun, partly-cloudy, cloud, rain-light, rain, rain-heavy, thunder, snow) to the design system, matching the exact identifiers src/weather.py produces. Each is a hand-drawn SVG sprite symbol at icon-weather-<state>, colorable via currentColor like the rest of the icon set, giving non-TRMNL weather views a direct data-to-glyph mapping instead of one generic stand-in icon. design/tokens.json documents the 8 valid states under icon.weather; design/index.html shows them in a dedicated Weather states grid; design/README.md documents the mapping rule and the version bump to 1.3.0. Also fixed 3 stale v1.1 version strings left over from the previous task.

Verified: pytest 259 passed. Rendered the full icon grid in both themes to confirm all 8 states are visually distinct (thunder's bolt was enlarged once after the first render read too thin); re-confirmed no horizontal overflow at 375px with the larger grid added.
<!-- SECTION:FINAL_SUMMARY:END -->
