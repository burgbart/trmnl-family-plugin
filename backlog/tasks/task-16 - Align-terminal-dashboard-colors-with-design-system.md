---
id: TASK-16
title: Align terminal dashboard colors with design system
status: Done
assignee:
  - '@kimi'
created_date: '2026-07-31 12:16'
updated_date: '2026-07-31 12:22'
labels: []
dependencies: []
references:
  - design/tokens.json
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The terminal dashboard (src/terminal_dashboard.py) currently uses ad-hoc Rich color names (cyan, yellow, green, bright_magenta, #D97757). Align it with the design system in design/ (TASK-15): load the palette from design/tokens.json so the terminal view uses the same colors as all other non-TRMNL views — pink #FF2F70 accent, blue-light #8EBEFF for interactive/time values (readable on dark terminal backgrounds, unlike navy #0A1A65), muted #ACB3D3 secondary, semantic success/warning/error (#6DCE43/#FF5F00/#FF2626), purple #A459FF for differentiation. Scope is colors only; terminal layout and typography stay as-is (terminals control the font and background).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Terminal dashboard styles come from a palette loaded out of design/tokens.json, with a hardcoded fallback matching the tokens when the file is unavailable
- [x] #2 Event times/interactive values use blue-light #8EBEFF, due/overdue items use error #FF2626, done/success uses #6DCE43, warnings use #FF5F00, anniversaries use purple #A459FF or pink #FF2F70
- [x] #3 No Rich named colors (cyan, yellow, green, magenta, red, blue) remain as ad-hoc literals in src/terminal_dashboard.py
- [x] #4 pytest passes, including terminal dashboard tests
- [x] #5 Terminal output visually verified (rendered output checked with the new palette)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create src/terminal_theme.py: TerminalTheme dataclass + load_theme() reading design/tokens.json (resolving {reference} values), with fallback constants mirroring the tokens.
2. Replace all ad-hoc Rich color literals in src/terminal_dashboard.py with theme values (cyan->interactive, green->success, red->error, yellow->purple/warning, bright_blue/magenta borders->interactive/accent, white/bright_white->text).
3. Run pytest; render sample output with the new palette for visual verification.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented: src/terminal_theme.py (TerminalTheme dataclass + load_theme() resolving DTCG {references}, fallback mirrors tokens) and src/terminal_dashboard.py now sources every color from THEME. One test updated (test_footer_uses_red_for_days_within_7 -> test_footer_uses_error_color_for_days_within_7, asserts THEME.error hex) since the palette intentionally replaced the red literal; added tests/test_terminal_theme.py (3 tests).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Terminal dashboard now uses the design-system palette. New src/terminal_theme.py loads colors from design/tokens.json (resolving DTCG references) with a fallback mirroring the tokens; src/terminal_dashboard.py has zero ad-hoc Rich color names left (cyan/yellow/green/red/blue/magenta/#D97757 all replaced: times/interactive #8EBEFF, error #FF2626, success #6DCE43, warning #FF5F00, anniversaries #A459FF, accents #FF2F70). Navy/brand-blue deliberately not used for text — too dark on terminal backgrounds; dark-theme interactive color used instead. Verified: grep shows no remaining color literals; pytest 141 passed (incl. 3 new theme tests + updated footer-color test); rendered sample dashboard exported via Rich save_html and screenshotted in headless Chrome showing the new palette applied. AGENTS.md updated. Scope stayed colors-only; terminal font/background remain terminal-controlled.
<!-- SECTION:FINAL_SUMMARY:END -->
