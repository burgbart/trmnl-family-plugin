---
id: TASK-17
title: 'Design system v1.1 — accessibility, responsive style guide, token-sync guard'
status: Done
assignee:
  - '@claude'
created_date: '2026-07-31 13:30'
updated_date: '2026-07-31 13:54'
labels: []
dependencies: []
references:
  - design/tokens.json
  - design/index.html
  - tests/test_design_tokens.py
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow-up to TASK-15. The design system is complete in coverage but not yet professional in two respects.

DESIGN SUBSTANCE — the light theme fails WCAG AA in its most-used places. Measured contrast ratios: text.secondary #ACB3D3 on white = 2.07:1 and on lavender #E8EAFD = 1.74:1, and it is used for every muted paragraph, caption, list metadata, placeholder and empty-state sentence on light surfaces (on dark it is fine at 7.5:1). Solid badges are also below AA: white on success = 1.99:1, on warning = 3.05:1, on error = 3.78:1, on brand pink = 3.56:1. There is no focus-visible ring on buttons, tabs, links or the theme toggle, no skip link, and no light-surface border token (only theme.dark.border exists).

PRESENTATION — the style guide is a single unbroken scroll of nine sections with no navigation, no section anchors, no responsive rules at all (the 4rem hero and fixed-width demo rows overflow on a phone), swatches you cannot copy a value from, and no stated version.

RIGOR — tokens.json and the :root block in index.html are kept in sync by hand with only a README sentence enforcing it, and nothing tests that the palette is accessible.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Every text/background pair the design system prescribes for light and dark surfaces meets WCAG AA (4.5:1 body, 3:1 large/UI), verified by computed ratios, with the accessible replacements added as tokens rather than one-off hex values in the style guide
- [x] #2 tokens.json documents a semantic color group where each state carries base + accessible surface + accessible on-surface text for both themes, and text.secondary is re-scoped to dark surfaces only so src/terminal_theme.py keeps working unchanged
- [x] #3 Keyboard users get a visible focus indicator on every interactive element in the style guide and a skip-to-content link; focus styles are token-driven and documented as a rule for new views
- [x] #4 The style guide is navigable and responsive: persistent section navigation with anchors, fluid type, and no horizontal overflow at 375px width
- [x] #5 Swatches show their token path, hex, and measured contrast, and clicking one copies the value
- [x] #6 The style guide has an Accessibility section stating the contrast rules and showing the measured pairs
- [x] #7 A pytest test fails when index.html CSS custom properties drift from tokens.json, when a token reference is dangling, or when a prescribed color pair drops below its AA threshold
- [x] #8 design/README.md documents the new tokens, the accessibility rules, and the design-system version; pytest passes
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. tokens.json v1.1: add version metadata under $extensions; add color.text.muted for light surfaces and re-scope color.text.secondary to dark surfaces; add color.border.subtle/strong and color.focus.ring/ring-dark; add per-state semantic -surface and -text tokens in both themes; add breakpoint tokens. Keep every token path src/terminal_theme.py reads intact.
2. index.html: mirror the new tokens in the :root and dark-theme blocks; add skip link, sticky section nav with scroll-spy, anchored headings, hero eyebrow and version chip; fluid clamp() display type; breakpoints at 900px and 600px; global :focus-visible ring.
3. Components: badges become tinted (-surface + -text); alerts get semantic titles; all muted copy, captions, placeholders and empty states move to text.muted; input and dashed borders use border.strong.
4. New Accessibility section: contrast rules plus a table of prescribed pairs measured live from the CSS variables, re-measured on theme toggle.
5. Swatches: token path, hex, measured contrast chip, click-to-copy with a toast.
6. tests/test_design_tokens.py: parse, dangling/circular references, CSS-variable mirror for both themes, unmapped colour variables, and a WCAG threshold per prescribed pair.
7. README.md and AGENTS.md: version, new tokens, accessibility rules, the enforced sync guard. Run pytest and render both themes at desktop and at a true 375px viewport in headless Chrome.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Design system v1.1.0.

TOKENS. Kept every path src/terminal_theme.py reads, so the terminal view is untouched: each color.semantic.<state> stayed a leaf token and the accessible values were added as sibling -surface / -text tokens rather than restructuring the state into a group. color.text.secondary keeps its value (#ACB3D3) and gains a description scoping it to dark surfaces; the accessible light-surface value is the new color.text.muted (#4B5791, 6.84:1 on white and 5.74:1 on lavender). Semantic pairs were derived by mixing each state into white (14%) for the surface, then darkening the state until it cleared 4.5:1 on both that surface and surface.base; dark-theme pairs mix into surface.base (18%) and lighten until they clear 4.5:1 on the surface, on base and on raised. border.strong was first set to #C9CFF0 and rejected at 1.54:1 — an input border must clear the WCAG 1.4.11 3:1 floor — and is now #7B85B2 (3.60:1 / 3.02:1); theme.dark.border-strong went from 0.45 to 0.55 alpha for the same reason (2.71:1 to 3.50:1). Version metadata lives under $extensions because DTCG reserves top-level $-keys.

GUARD. tests/test_design_tokens.py (118 tests) holds an explicit CSS-variable to token-path map for both themes and fails on drift, on a colour variable with no token behind it, on dangling or circular references, and on any prescribed pair below its threshold (49 pairs: 26 light, 23 dark). The only unmapped dark variables are --shadow-card and --shadow-raised, allowlisted as DERIVED_DARK_VARS because blue-tinted shadows read as haze on dark. It also asserts that the hero token-count stat matches the real leaf count, that every nav link resolves to a real section id, and that the skip link, focus-visible, reduced-motion and breakpoint rules are present.

STYLE GUIDE. Swatch contrast chips are theme-scoped via a data-contrast attribute (light, dark or both) so brand.navy is not reported as a 1.22:1 failure in dark mode, where the system never asks anyone to use it as text; the off-theme case renders a neutral surfaces-only chip instead. Added a theme query parameter so screenshots and shared links are reproducible.

VERIFICATION. pytest 259 passed (118 new). The guard was proven by injection rather than inspection: changing text.muted to #8A93C0 produced 3 failures (mirror drift plus both muted-text contrast pairs), and renaming a reference to a non-existent token produced 4 (dangling reference, dark mirror, both dark focus-ring pairs). Both were reverted and re-verified green. Rendered in headless Chrome: light and dark full pages at 1280px, and the page inside a 375px iframe. Windows will not open a browser window narrower than about 500px, so a 375px window-size clips rather than reflows and is not a valid mobile check; the iframe gives a true 375px layout viewport. At that width there is no horizontal overflow: hero and body copy reflow, the swatch grid drops to two columns, the section nav becomes a horizontal scroller. The live contrast table renders all 13 rows as AA or AAA in light. Click-to-copy was exercised with a scripted click: the toast fires with the token value and the swatch aria-label reads Copy color.brand.pink, #FF2F70.

FOUND DURING REVIEW. The section nav lacked min-width:0, which would have let the flex item refuse to shrink; type-specimen labels were given a fixed 260px width so the samples align; and the clipboard fallback now names itself instead of showing a bare hex.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Design system v1.1.0: the v1.0 system was complete in coverage but shipped an inaccessible light theme, an unnavigable style guide, and a hand-maintained mirror nothing enforced.

Accessibility. Added color.text.muted (#4B5791) for light surfaces and re-scoped color.text.secondary (#ACB3D3, 2.07:1 on white) to dark surfaces only, which is where it was always correct — src/terminal_theme.py is unchanged and still reads it. Each semantic state gained an accessible -surface / -text pair in both themes, so badges and alerts no longer put white text on a solid fill (success was 1.99:1). Added border.subtle / border.strong (the latter clearing the 3:1 non-text floor for input outlines) and focus.ring / focus.ring-dark. All 49 prescribed pairs now meet AA.

Presentation. The style guide gained a sticky section nav with scroll-spy and anchored headings, a numbered section rhythm with eyebrows, an Accessibility section whose contrast table is measured live from the CSS variables and re-measured on theme toggle, swatches showing token path, hex and measured contrast with click-to-copy, a skip link, a visible focus-visible ring on every control, aria state on tabs and navigation, fluid clamp() display type, and breakpoints that hold down to 375px.

Rigor. tests/test_design_tokens.py (118 tests) is now the guard: it maps every colour custom property to a token path in both themes and fails on drift, on an unbacked variable, on dangling or circular references, and on any prescribed pair below its WCAG threshold.

Verified: pytest 259 passed. The guard was proven by injecting a drifted hex (3 failures) and a dangling reference (4 failures), then reverting to green. Both themes rendered in headless Chrome at 1280px and at a true 375px viewport (via an iframe, since Windows clamps window width at about 500px) with no horizontal overflow; click-to-copy exercised by scripted click. README.md documents the rules and the changelog, AGENTS.md points agents at them, and CHANGELOG.md records the release.
<!-- SECTION:FINAL_SUMMARY:END -->
