---
id: TASK-15
title: Design style definition / Design System
status: Done
assignee:
  - '@kimi'
created_date: '2026-07-31 11:31'
updated_date: '2026-07-31 12:05'
labels: []
dependencies: []
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
For each view that is not in TRML device, I would like us to define a design style. I really like Heimdalsecurity.com. Can we base it off that? 

Create a webpage where I can view the design. Is there a popular format to display such designs which is readable for AI and viewable for humans?

https://heimdalsecurity.com/?partner=reddit&rdt_cid=5768191115249645866&utm_source=reddit
<!-- SECTION:DESCRIPTION:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Research heimdalsecurity.com visual style (colors, typography, spacing, components) from its HTML/CSS.
2. Define design tokens in W3C Design Tokens / Style Dictionary JSON format (AI-readable, popular standard) at design/tokens.json.
3. Build a static style-guide webpage (design/index.html) that renders the tokens: color palette, typography scale, spacing, buttons, cards, badges — no build step, viewable by humans.
4. Write design/README.md documenting the design system and how views should consume it (AI + human readable).
5. Update AGENTS.md project structure for the new design/ folder.
6. Verify: JSON parses, HTML renders (validate structure), pytest still passes.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Extracted Heimdal's style from production CSS (common.min.css, homepage.css, common-23.css, stack-section.css): fonts Nunito Sans + Inter, core palette #FF2F70/#0A1A65/#0065FE/#8EBEFF/#E8EAFD/#ACB3D3, CTA gradient #FF2F70->#FF2626, pill radius 30px, navy/blue-tinted shadows. Chose W3C DTCG design-token JSON as the AI/machine-readable format (the popular standard: Style Dictionary, Figma Tokens, Tokens Studio) plus a static HTML style guide for humans.

Verification: tokens.json parses (152 leaf values, no dangling {references}); index.html well-formed (tag-balance check, 0 errors) and rendered via headless Chrome screenshots — hero, colors, typography, shape, components, dark band, and sample dashboard view all render as designed; pytest 138 passed.

Follow-up: added dark mode. tokens.json gained a theme.dark override group (surface base #060C30 / raised #121E5C / tinted #0D1648, interactive switches to blue-light #8EBEFF, hairline borders rgba(172,179,211,.25)). index.html gained a [data-theme="dark"] CSS override block plus a fixed dark-mode toggle button (top right) persisted via localStorage, defaulting to OS prefers-color-scheme; components now consume semantic vars (--color-card, --color-interactive, --color-border) so both themes render from one stylesheet. README documents the dark theme. Verified with headless-Chrome screenshots of both themes (light default + dark-forced copy): tokens.json 174 leaf values, no dangling refs; HTML tag-balanced.

Follow-up 2: expanded the style guide into a fuller design system. Added component inventory (form elements, nav bar + segmented tabs, event/task list rows, semantic alerts + navy toasts, modal on navy backdrop, empty state) with canonical token-driven markup in light and dark. Added a Motion & animation section (motion token group in tokens.json: durations 150/250/400ms, standard/entrance/exit easings, fade-up keyframes, prefers-reduced-motion honored page-wide) and a Gradient usage section with visual do/don't examples (pink gradient = primary action only, blue = decorative; never behind body copy, never competing gradient panels). README gained principles for motion/gradients and the component inventory. Verified: tokens.json 198 leaf values with no dangling refs (keyframes restructured to from/to leaves to avoid DTCG reference-syntax braces), HTML tag-balanced, headless-Chrome screenshots of both themes covering all new sections.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Created design/ — a Heimdal-based design system for all non-TRMNL views: (1) design/tokens.json, W3C DTCG design tokens (the popular AI/machine-readable standard) with palette, typography, radii, shadows, spacing extracted from heimdalsecurity.com's production CSS; (2) design/index.html, a static no-build style-guide webpage rendering colors, type specimens, shape/depth, buttons, badges, cards, a dark band, and a sample family-dashboard view as reference lofi; (3) design/README.md documenting principles, consumption, and the sync rule between the two files. AGENTS.md updated (structure tree + agent note). Verified: JSON parses with no dangling token references, HTML tag-balanced and visually confirmed via headless-Chrome screenshots, pytest 138 passed.
<!-- SECTION:FINAL_SUMMARY:END -->
