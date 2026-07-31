---
id: TASK-18
title: >-
  Design system v1.2 — fix invisible cards, gradient-card spacing, add
  iconography
status: Done
assignee:
  - '@claude'
created_date: '2026-07-31 14:09'
updated_date: '2026-07-31 14:20'
labels: []
dependencies: []
references:
  - design/tokens.json
  - design/index.html
  - design/README.md
ordinal: 17000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up to TASK-17, reported directly against the rendered style guide.

BUG: cards are invisible on plain (non-tinted) sections. The Motion section renders its three demo cards as bare floating text, no visible boundary at all. Root cause: --color-card equals --color-surface (both white) in the light theme, and card borders use --color-border, which is only about 1.2:1 against white. In v1.0 this was masked because Motion and Components happened to sit on tinted (lavender) sections, where a white card still pops against the lavender background; TASK-17 inserted a new Accessibility section between Colors and Typography, which shifted every later section alternation by one and flipped Motion and Components to plain backgrounds, exposing the latent flaw. Any future reordering would reintroduce the same failure, so the fix must not depend on section background alternation.

BUG: in the Gradient usage do/dont cards, the descriptive paragraph has no bottom margin, so the primary button, icon chip, and color bars directly beneath it touch the paragraph text with no breathing room.

GAP: the design system documents color, type, shape, motion and components but has no iconography guidance: no stroke weight, no size scale, no color-usage rule for icons, and no example set, despite icons already appearing in the component demos and in the TRMNL weather templates.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Every card-style component (cards, swatches, nav, lists, modals, motion cards, the dashboard sample card) has a boundary visible on both plain and tinted sections in both themes, verified by rendering the Motion and Components sections in isolation
- [x] #2 The fix does not depend on which sections happen to be tinted vs plain; reordering sections must not reintroduce invisible cards
- [x] #3 Gradient usage do/dont cards have visible spacing between the descriptive paragraph and the button/icon/color-bar beneath it
- [x] #4 design/tokens.json gains an icon token group (stroke width, a size scale) with descriptions on when to use each size and that icons inherit currentColor by default
- [x] #5 design/index.html gains an Iconography section: the usage rule, the size scale rendered at actual size, and a small set of example icons relevant to this dashboard shown in default, muted, interactive and dark-theme colors
- [x] #6 design/README.md documents the iconography rules and the design-system version bump; tests/test_design_tokens.py and pytest pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Card visibility (systemic, not section-dependent): change the border color on every card-style component (.card, .swatch, .nav, .list, .modal, .motion-card, .dash) from --color-border to --color-border-strong in both themes, keeping --color-border for internal hairline dividers (list-row separators, table rows, specimen underlines) that already sit inside a visible container. Re-screenshot Motion and Components in isolation on a plain background to confirm.
2. Gradient card spacing: add bottom margin to the paragraph inside .dodont .card so the button/icon/color-bar beneath it has breathing room.
3. Iconography: add an icon token group to tokens.json (strokeWidth, a size scale sm/md/lg/xl) with $description guidance; add a new Iconography section to index.html between Gradients and Components (renumbering subsequent eyebrows and nav links) with the usage rule, the size scale at actual size, and hand-drawn inline SVG icons (calendar, checklist, cake, cloud-sun, bell) using currentColor stroke, shown in default/muted/interactive colors and in the dark theme.
4. Update design/README.md (iconography rules, version bump to 1.2.0) and tokens.json meta/changelog. Update the hero token-count data-fallback to the new total.
5. Run pytest, verify the guard still passes, and re-screenshot both themes at desktop and 375px.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Root cause of the invisible-card bug: --color-card equals --color-surface (both white) in the light theme, and card borders used --color-border (~1.2:1 against white). This was masked in v1.0 because Motion and Components happened to sit on tinted sections; TASK-17 inserted a new Accessibility section right after Colors, shifting every later section alternation by one and flipping Motion/Components to plain backgrounds. Fix is systemic rather than a reordering: card-style components (.card, .swatch, .rulecard, .nav, .list, .alert, .motion-card, .dash) now border on border.strong (3.60:1), which does not depend on the section background at all, so a future reorder cannot reintroduce the failure. .modal was left alone; it sits on a navy backdrop and already has strong contrast via shadow-raised. Internal hairline dividers (list-row separators, table rows, specimen underlines) were left on border.subtle since they sit inside an already-visible container.

Also fixed while in the motion cards: the three-line captions used <br> inside a centered flex container, which visually jumbled the wrapped text (each line centered independently, phrases split mid-sentence). Changed to explicit <strong>/<span> children with flex-direction:column so each line is its own block.

Gradient do/dont cards: added margin-bottom to the paragraph inside .dodont .card so the button/icon/color-bar beneath it has breathing room; previously they touched the text directly.

Iconography: added an icon token group to tokens.json (fixed strokeWidth 1.75, size scale sm/md/lg/xl) and a new Iconography section between Gradients and Components (renumbered subsequent eyebrows 08/09/10). Five icons (weather, calendar, checklist, cake, bell) defined once as an SVG sprite (<symbol> + <use>), hand-drawn on a 24x24 grid, no fill/stroke color hardcoded so they inherit currentColor. Section shows the size scale at actual size, the five-icon set in cards, and the same bell icon recolored in default/muted/interactive/on-dark-chip to demonstrate the currentColor pattern. No new color tokens were introduced, so no new guard pairs were needed; hero token-count fallback updated 103 -> 108 for the 5 new leaf tokens (icon.strokeWidth + 4 sizes).

Verified: pytest 259 passed (118 design-token tests unchanged in count, all green). Rendered Motion and Components in isolation before and after: before, the three motion cards were bare floating text; after, all three have a visible rounded boundary. Rendered the Iconography section in both themes — icons render legibly at all four sizes and recolor correctly across the four color tiles. A scripted check confirmed every <use href> resolves to a real <symbol> id and every nav link resolves to a real section id. Re-verified the 375px iframe check from TASK-17 still holds with the new section: clientWidth equals scrollWidth (no horizontal overflow), and the icon grid/scale/color-row reflow to narrower columns without breaking.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Design system v1.2.0: fixed a real rendering bug the user hit directly (cards with no visible boundary on plain sections, most visibly in Motion), fixed missing spacing in the gradient do/dont cards, and added iconography guidance the system previously lacked entirely.

Card visibility was a systemic gap, not a one-section fix: --color-card equals --color-surface in the light theme, so a border.subtle boundary (~1.2:1) disappears on any untinted section, and TASK-17's new Accessibility section had shifted alternation enough to expose it in Motion and Components. Card-style components now border on border.strong (3.60:1), which holds regardless of section background, so reordering sections again cannot reintroduce the bug.

Added an icon token group (fixed stroke width, 4-step size scale) and an Iconography section: five hand-drawn icons as one SVG sprite, shown at every size and recolored via currentColor across default/muted/interactive/dark contexts.

Verified: pytest 259 passed. Rendered Motion and Components before and after in isolation to confirm the card fix; scripted checks confirmed every icon sprite reference and every nav anchor resolves; re-checked the 375px layout (from TASK-17) still has no horizontal overflow with the new section added. design/README.md and CHANGELOG.md document the fixes and the version bump.
<!-- SECTION:FINAL_SUMMARY:END -->
