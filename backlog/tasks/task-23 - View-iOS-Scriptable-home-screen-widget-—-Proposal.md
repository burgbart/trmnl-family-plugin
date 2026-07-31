---
id: TASK-23
title: 'View: iOS Scriptable home-screen widget — Proposal'
status: To Do
assignee: []
created_date: '2026-07-31 20:40'
labels:
  - view
dependencies: []
ordinal: 22000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Proposal + decision ticket (pipeline Stages 1-2, plan/VIEW_PIPELINE.md) for an iOS home-screen widget of the family dashboard (doc-4 recommendation #4): a small Scriptable JavaScript widget that fetches the published dashboard-v2.json — personal use, no App Store or native codebase. The Stage-1 proposal with lofi design is in the notes. Awaiting owner decision: on 'to implement', create the Requirements / Design / Implementation tickets linked with --depends-on; on 'skip', close with the reason.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Stage 1 — Proposal (per plan/VIEW_PIPELINE.md)

**Pitch.** An iOS home-screen widget showing the family essence at a glance:
weather, next event, due-task count, next anniversary. Built with the
Scriptable app (small JavaScript file that fetches JSON and renders a
widget) — personal-use only, no App Store, no Swift codebase. Doc-4 picked
this as the low-effort mobile path, deferring native WidgetKit unless this
proves limiting.

**Lofi design (iOS medium widget).**

```
┌───────────────────────────────┐
│ ☁ 23° · Amsterdam             │  weather: icon, temperature, city
│ 14:00  Dentist                │  next timed event (title + time)
│ □ 3 tasks due (1 overdue)     │  tasks: count due / overdue
│ 💍 Wedding · in 16 days       │  next anniversary (name + days)
│                    ↻ 18:40    │  meta.generated_at
└───────────────────────────────┘
Small widget variant (if wanted later): temp + next event only.
Error state: "(!) not loaded" line when fetch fails or errors.* set;
widget keeps showing last good data with a stale timestamp.
```

**Data source.** Published `dashboard-v2.json` on R2 (HTTPS GET by the
widget, OS-controlled refresh ~15–30 min): `meta.city`,
`meta.generated_at`, `weather` (icon, temperature), `events[]` (title,
start, all_day), `tasks[]` (due_date, done), `birthdays[]` (name, date,
kind), `errors`.

**Effort guess: low** — one JavaScript file in Scriptable: fetch, pick next
items, draw rows. Distribution = copy the script onto the household iPhones.
Visual style should echo `design/tokens.json` where Scriptable's drawing
APIs allow.
<!-- SECTION:NOTES:END -->
