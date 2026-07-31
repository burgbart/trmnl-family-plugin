# trmnl-home Design System

**Version 1.3.0** — updated 2026-07-31

Design language for every **non-TRMNL** view of the family dashboard — web pages, mobile/desktop widgets, menu-bar apps, AI surfaces. The TRMNL device itself keeps its own 1-bit Liquid templates (`templates/devices/`) and is out of scope here.

The style is based on [heimdalsecurity.com](https://heimdalsecurity.com/): a friendly, modern SaaS look — deep navy, vivid pink CTAs, blue gradients, rounded shapes, soft blue-tinted shadows.

## Files

| File | Audience | Purpose |
|------|----------|---------|
| `tokens.json` | AI + machines | Single source of truth. W3C Design Tokens (DTCG draft) format — the standard used by Style Dictionary, Figma Tokens, Tokens Studio. |
| `index.html` | Humans | Static style guide webpage rendering the tokens: colors, accessibility, typography, shape, motion, gradients, components, and a sample dashboard view. Open it in a browser, no build step. |
| `README.md` | Both | This document. |
| `../tests/test_design_tokens.py` | CI | The guard. Fails the build on dangling references, mirror drift, or a contrast regression. |

`index.html` re-declares the palette as CSS custom properties so it needs no build step. **That mirror is enforced, not trusted:** `tests/test_design_tokens.py` maps every `--color-*` / `--gradient-*` variable to a token path and fails when the two disagree, when a variable has no token behind it, or when a prescribed color pair drops below its WCAG threshold. Change `tokens.json` and `index.html` in the same commit, and run `pytest tests/test_design_tokens.py`.

## Principles

- **Navy leads, pink acts, blue informs.** Navy (`#0A1A65`) for headings and dark sections; pink (`#FF2F70`, gradient to `#FF2626`) is reserved for primary actions; blue (`#0065FE`) for links, times, and interactive elements.
- **Rounded and friendly.** Pill buttons (30px), 18px cards, 28px hero panels, circular icon chips.
- **Soft, tinted depth.** Three elevations only. Shadows are navy/blue-tinted on light surfaces (`rgba(0,56,255,.15)`), neutral black on dark, where a blue tint reads as haze.
- **Two typefaces.** Nunito Sans (extrabold) for display/headings/numbers; Inter for body and UI text. Display sizes are fluid (`clamp()`); 14px is the type floor; numbers use `tabular-nums` so times and temperatures do not jitter between refreshes.
- **Lavender bands.** Alternate white and pale lavender (`#E8EAFD`) sections; navy bands for heroes and footers.
- **Dark mode built in.** `tokens.json` carries a `theme.dark` override group. New views ship both themes from day one, defaulting to the OS `prefers-color-scheme`.
- **Accessible by construction.** See below — this is a rule, not an aspiration, and it is tested.
- **Mobile down to 375px.** Two breakpoints (`tablet` 900px, `mobile` 600px); no view may scroll horizontally at 375px.
- **Motion is subtle and functional.** Three durations (150/250/400ms), three easings, one default entrance (`fade-up`). Nothing loops, nothing bounces, and `prefers-reduced-motion` disables all animation *and* smooth scrolling.
- **Gradients have strict jobs.** `gradient.cta` (pink) is reserved for the one primary action per view; `gradient.blue` fills icon chips and decorative art. Never behind body copy, never competing gradient panels.

## Accessibility rules

Everything the system prescribes meets **WCAG 2.1 AA**: 4.5:1 for text, 3:1 for text ≥24px (or ≥18.66px bold) and for non-text UI boundaries. The style guide's Accessibility section measures every pair live from the CSS variables; the test suite measures them from the tokens.

- **Muted text is theme-specific.** `text.muted` (`#4B5791`) on light surfaces — 6.84:1 on white, 5.74:1 on lavender. `text.secondary` (`#ACB3D3`) on dark surfaces only — 7.52:1 on navy, but **2.07:1 on white**. They are not interchangeable. This was the v1.0 bug: `text.secondary` was used for every muted paragraph, caption and placeholder on light surfaces.
- **State colors never carry white text.** Each state is a trio — `<state>` (the indicator/fill), `<state>-surface` (a tinted background), `<state>-text` (a foreground accessible on both that surface and `surface.base`). Solid fills under white text fail AA at badge size: success is 1.99:1, warning 3.05:1, error 3.78:1. Badges and alerts use the pair; the solid value is for dots, bars and icon fills.
- **Color is never the only signal.** Every state also carries a word — "Overdue", "Due soon", "Done".
- **Borders that carry meaning use `border.strong`** (`#7B85B2`, 3.60:1 on white). `border.subtle` is decorative and does not reach 3:1 — it must not be the only thing marking an input.
- **Focus is always visible.** A 3px `color.focus.ring` outline at 2px offset on `:focus-visible`, switching to `focus.ring-dark` in the dark theme. Never `outline: none` without a replacement.
- **Every view starts with a skip link** to its `<main>` landmark, and controls are properly labelled (`<label>`, `aria-pressed`, `aria-current`, `aria-selected`).
- **Hit targets are ≥44px** in any view that ships to a phone.

The terminal dashboard is the one surface exempt from the surface tokens — the terminal owns its background — and `src/terminal_theme.py` deliberately uses `text.secondary` and `theme.dark.interactive`, which is exactly right against a dark terminal.

## Component inventory

The style guide's Components section is the canonical markup for each of these — copy it instead of inventing new markup:

- **Buttons** — primary (pink gradient pill), secondary (outline), ghost; lift on hover, shared focus ring
- **Badges** — tinted semantic pills (success, warning, error, info, accent, purple, neutral)
- **Cards** — 18px radius, `border.strong` outline, blue-tinted shadow
- **Form elements** — text input, select, gradient toggle switch (8px radius, 2px `border.strong`, blue focus ring)
- **Navigation** — nav bar in a raised card, segmented pill tabs driven by `aria-selected`
- **Lists** — event/task rows: source dot, title + metadata, right-aligned time or badge
- **Alerts & toasts** — 6px semantic left-border alerts with a matching semantic title color, navy pill toasts for transient confirmations
- **Modal** — 28px radius on a 45% navy backdrop, one primary action
- **Empty state** — dashed `border.strong`, dimmed icon chip, one friendly sentence

Each component renders in both themes on the style guide page.

## Iconography

A small set of hand-drawn line icons on a 24x24 grid, defined once as an SVG sprite (`<symbol>` + `<use>`) at the top of `index.html` — no external icon library is loaded.

- **No icon has its own color.** Every icon inherits `currentColor`; recolor one by setting `color` on it or an ancestor, exactly like text. The style guide's Color row shows the same bell icon in `text.primary`, `text.muted`, the interactive color, and on a fixed navy chip.
- **Stroke width is fixed, not scaled.** `icon.strokeWidth` (1.75) stays constant across every size in `icon.size` (`sm` 16px, `md` 20px, `lg` 24px, `xl` 32px) — icons get bigger, never heavier.
- **Meaningful icons still need 3:1 contrast.** A status glyph or alert icon shown with no adjacent label is a non-text UI element under WCAG 1.4.11, same as a border or focus ring.
- **Card boundaries need to be visible on their own.** Every card-style component (`.card`, `.swatch`, `.nav`, `.list`, `.modal`, motion demo cards, the dashboard sample card) borders on `border.strong`, not `border.subtle` — a card's own edge must read regardless of whether it happens to sit on a plain or tinted section, since `--color-card` and `--color-surface` are the same white in the light theme.
- **The weather set has one icon per state, not one generic glyph.** `icon.weather` documents the 8 states `src/weather.py` can produce (`sun`, `partly-cloudy`, `cloud`, `rain-light`, `rain`, `rain-heavy`, `thunder`, `snow`); each has a matching sprite symbol at `icon-weather-<state>`, so a view maps `weather.icon` straight to a glyph with `"#icon-weather-" + weather.icon` — no lookup table needed. These are the colorable, non-TRMNL equivalent of the 1-bit glyphs already baked into `templates/devices/og.liquid` and `x.liquid`.

## Consuming the tokens

- **Web / HTML views:** copy the `:root` custom-property block from `index.html` (or generate it from `tokens.json`), plus the `[data-theme="dark"]` override block; toggle by setting `data-theme="dark"` on `<html>`.
- **Python views:** load `tokens.json` with `json.load()`; references like `{color.brand.navy}` resolve to other token paths. `src/terminal_theme.py` is the working example.
- **AI agents:** read `tokens.json` first when creating or styling any non-TRMNL view; every token carries a `$description` stating its intended use and, for color, its measured contrast.

## Applying it to new views

New views follow the prompt pipeline (see TASK-13). At the Design stage, use this design system for both the UX design and the technical design's visual layer; the sample dashboard card at the bottom of `index.html` is the reference lofi for the dashboard data model.

## Changelog

- **1.3.0** — Added `icon.weather`: the full 8-state weather icon set (`sun`, `partly-cloudy`, `cloud`, `rain-light`, `rain`, `rain-heavy`, `thunder`, `snow`) matching `src/weather.py`, each drawn as a colorable SVG sprite symbol at `icon-weather-<state>` and shown in a dedicated Weather states grid in the Iconography section.
- **1.2.0** — Fixed cards rendering with no visible boundary on plain sections: `.card`, `.swatch`, `.nav`, `.list`, `.modal`, motion demo cards and the sample dashboard card now border on `border.strong` instead of `border.subtle`, which no longer depends on whether the surrounding section happens to be tinted. Fixed missing spacing between the gradient do/dont cards' paragraph and the element beneath it. Added an `icon` token group (stroke width, a 4-step size scale) and an Iconography section to the style guide, with a small hand-drawn set (weather, calendar, tasks, birthday, alert) shown at every size and in default/muted/interactive/dark colors.
- **1.1.0** — Accessibility pass. Added `text.muted` for light surfaces and re-scoped `text.secondary` to dark surfaces only; added per-state semantic `-surface` / `-text` pairs in both themes; added `border.subtle` / `border.strong` and `focus.ring` / `focus.ring-dark`; added `breakpoint` tokens and fluid display type. Style guide gained a sticky section nav, an Accessibility section with live contrast measurement, copy-to-clipboard swatches, a skip link, visible focus states, and responsive layout down to 375px. Added `tests/test_design_tokens.py` as the enforcement guard.
- **1.0.0** — Initial palette, typography, shape, motion and gradient tokens extracted from heimdalsecurity.com's production CSS, plus the style guide and dark theme.
