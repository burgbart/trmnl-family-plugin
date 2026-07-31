# trmnl-home Design System

Design language for every **non-TRMNL** view of the family dashboard — web pages, mobile/desktop widgets, menu-bar apps, AI surfaces. The TRMNL device itself keeps its own 1-bit Liquid templates (`templates/devices/`) and is out of scope here.

The style is based on [heimdalsecurity.com](https://heimdalsecurity.com/): a friendly, modern SaaS look — deep navy, vivid pink CTAs, blue gradients, rounded shapes, soft blue-tinted shadows.

## Files

| File | Audience | Purpose |
|------|----------|---------|
| `tokens.json` | AI + machines | Single source of truth. W3C Design Tokens (DTCG draft) format — the popular standard used by Style Dictionary, Figma Tokens, Tokens Studio. |
| `index.html` | Humans | Static style guide webpage rendering the tokens: colors, typography, shape, components, and a sample dashboard view. Open it in a browser, no build step. |
| `README.md` | Both | This document. |

When a token changes, update **both** `tokens.json` and the CSS custom properties block at the top of `index.html` (marked `mirror of design/tokens.json`).

## Principles

- **Navy leads, pink acts, blue informs.** Navy (`#0A1A65`) for headings and dark sections; pink (`#FF2F70`, gradient to `#FF2626`) is reserved for primary actions; blue (`#0065FE`) for links, times, and interactive elements.
- **Rounded and friendly.** Pill buttons (30px), 18px cards, 28px hero panels, circular icon chips.
- **Soft, tinted depth.** Shadows are navy/blue-tinted (`rgba(0,56,255,.15)`, `rgba(1,22,55,.25)`), never plain gray.
- **Two typefaces.** Nunito Sans (extrabold) for display/headings/numbers; Inter for body and UI text.
- **Lavender bands.** Alternate white and pale lavender (`#E8EAFD`) sections; navy bands for heroes and footers.
- **Dark mode built in.** `tokens.json` carries a `theme.dark` override group (deeper-than-navy backgrounds, raised cards, blue-light interactive text). The style guide has a dark-mode toggle (top right) that persists via `localStorage` and defaults to the OS `prefers-color-scheme`. New views should ship both themes from day one.
- **Motion is subtle and functional.** Three durations (150/250/400ms), three easings (standard, entrance, exit), one default entrance (`fade-up`). Micro-interactions are fast, state changes normal, entrances slow. Nothing loops, nothing bounces, and `prefers-reduced-motion` disables all animation. Tokens live in the `motion` group.
- **Gradients have strict jobs.** `gradient.cta` (pink) is reserved for the one primary action per view; `gradient.blue` fills icon chips and decorative art. Never behind body copy, never multiple competing gradient panels in one region.

## Component inventory

The style guide's Components section is the canonical markup for each of these — copy it instead of inventing new markup:

- **Buttons** — primary (pink gradient pill), secondary (outline), ghost; lift on hover
- **Badges** — semantic pills (success, warning, error, info, neutral)
- **Cards** — white/raised, 18px radius, blue-tinted shadow
- **Form elements** — text input, select, gradient toggle switch (8px radius, 2px border, blue focus ring)
- **Navigation** — nav bar in a raised card, segmented pill tabs
- **Lists** — event/task rows: source dot, title + metadata, right-aligned time or badge
- **Alerts & toasts** — 6px semantic left-border alerts for error states (e.g. `(!) Not loaded`), navy pill toasts for transient confirmations
- **Modal** — 28px radius on a 45% navy backdrop, one primary action
- **Empty state** — dashed border, dimmed icon chip, one friendly sentence

Each component renders in both themes on the style guide page.

## Consuming the tokens

- **Web / HTML views:** copy the `:root` custom-property block from `index.html` (or generate it from `tokens.json`), plus the `[data-theme="dark"]` override block for dark mode; toggle by setting `data-theme="dark"` on `<html>`.
- **Python views:** load `tokens.json` with `json.load()`; references like `{color.brand.navy}` resolve to other token paths.
- **AI agents:** read `tokens.json` first when creating or styling any non-TRMNL view; every token carries a `$description` stating its intended use.

## Applying it to new views

New views follow the prompt pipeline (see TASK-13). At the Design stage, use this design system for both the UX design and the technical design's visual layer; the sample dashboard card at the bottom of `index.html` is the reference lofi for the dashboard data model.
