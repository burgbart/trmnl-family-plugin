---
id: TASK-28
title: 'View: macOS menu-bar quick view — Proposal'
status: To Do
assignee: []
created_date: '2026-07-31 20:53'
labels:
  - view
dependencies: []
ordinal: 27000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Proposal + decision ticket (pipeline Stages 1-2, plan/VIEW_PIPELINE.md) for a macOS menu-bar quick view: always-visible menu-bar label (temp + next event) plus a compact popover with the full family state on click. Split out of TASK-20 (31 Jul 2026): the full-screen desktop app went ahead separately with the dashboard-md-launcher technique; this view covers the tray/popover surface. Direction per architecture advisory: native SwiftUI MenuBarExtra + WKWebView (Python tray libs only render text menus). Raycast hotkeys via a familydash:// URL scheme. The Stage-1 proposal with lofi design is in the notes. Awaiting owner decision: on 'to implement', create the Requirements / Design / Implementation tickets linked with --depends-on; on 'skip', close with the reason.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Stage 1 — Proposal (per plan/VIEW_PIPELINE.md)

**Pitch.** A macOS menu-bar companion to the desktop app (TASK-20): an icon
in the menu bar that always shows today's essence (temp + next event), and
one click opens a compact quick-view popover with the full family state —
for the glance that doesn't warrant opening the full-screen app. Split out of
TASK-20 (31 Jul 2026) so the desktop app could use the proven
dashboard-md-launcher technique; the quick view needs a native popover,
which Python tray libraries can't deliver (they render text menus only).

**Lofi design.**

```
Menu bar (always visible):
┌─────────────────────┐
│ ☁ 23° · 14:00 Dent. │   <- MenuBarExtra label: icon + temp + next event
└─────────────────────┘

Quick view popover (~360px, opens under the menu-bar icon):
┌──────────────────────────────┐
│ Amsterdam ☁ 23° (fl 21°)     │  weather + alert line
│──────────────────────────────│
│ Today 14:00  Dentist         │  next events (3-4 rows)
│ Sat 09:30    Swimming lesson │
│──────────────────────────────│
│ □ 3 tasks due (1 overdue)    │  task summary + top due tasks
│ □ Send packages back         │
│──────────────────────────────│
│ 💍 Wedding · in 16 days      │  next anniversaries
│──────────────────────────────│
│ (!) Tasks not loaded         │  only when errors.* set
│ ↻ 18:40      Open full view  │  refresh time + link to desktop app
└──────────────────────────────┘
```

Interaction: click icon = toggle popover; "Open full view" launches the
TASK-20 desktop app; Raycast hotkeys drive `familydash://quickview` (toggle)
and `familydash://fullscreen` (open desktop app) via Quicklinks — URL scheme
handled with onOpenURL. One known spike: toggling the popover
programmatically needs an NSStatusItem/NSPopover bridge (~an evening).

**Data source.** Published `dashboard-v2.json` on R2 (HTTPS GET, 60 s poll,
fetched natively and injected into a WKWebView to sidestep CORS): `meta`,
`weather`, `events[]`, `tasks[]`, `birthdays[]`, `errors`. Compact HTML
layout styled from `design/tokens.json` — same view codebase as the desktop
app, compact mode.

**Effort guess: medium** — SwiftUI MenuBarExtra (.window style) + WKWebView
shell is a few hundred lines in a new sibling repo (per the architecture
advisory: Python tray libs can't do an HTML popover; Tauri/Electron are
disproportionate). The HTML compact layout shares work with TASK-20's view.
Native Swift is the advisory's recommendation for popover fidelity.
<!-- SECTION:NOTES:END -->
