---
id: TASK-24
title: 'View: Android home-screen widget — Proposal'
status: To Do
assignee: []
created_date: '2026-07-31 20:41'
labels:
  - view
dependencies: []
ordinal: 23000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Proposal + decision ticket (pipeline Stages 1-2, plan/VIEW_PIPELINE.md) for an Android home-screen widget of the family dashboard (doc-4 option 1, Android path): a KWGT preset that fetches the published dashboard-v2.json directly — personal use, no native Kotlin app (deferred per doc-4). Android counterpart of TASK-23 (iOS Scriptable widget). The Stage-1 proposal with lofi design is in the notes. Awaiting owner decision: on 'to implement', create the Requirements / Design / Implementation tickets linked with --depends-on; on 'skip', close with the reason.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Stage 1 — Proposal (per plan/VIEW_PIPELINE.md)

**Pitch.** An Android home-screen widget showing the family essence at a
glance — the Android counterpart of the iOS Scriptable widget (TASK-23):
weather, next event, due-task count, next anniversary. Doc-4 rated a native
Android App Widget high effort (new Kotlin codebase, build/distribution
chain) and pointed at scriptable widget apps as the low-effort path: a KWGT
(Kustom Widget) preset can fetch JSON directly (its `wg()` web-get function
parses JSON), so no app development is needed for personal use.

**Lofi design (Android 4x2 home-screen widget).**

```
┌───────────────────────────────────┐
│ ☁ 23° · Amsterdam          ↻ 18:40│  weather icon+temp, city, refreshed
│───────────────────────────────────│
│  14:00   Dentist                  │  next timed event (time + title)
│  Sat     Swimming lesson          │  second upcoming event
│───────────────────────────────────│
│  □ 3 tasks due (1 overdue)        │  tasks: due / overdue counts
│  💍 Wedding · in 16 days          │  next anniversary (name + days)
└───────────────────────────────────┘
Error state: "(!) not loaded" row when the fetch fails or errors.* is set;
stale data stays visible with its timestamp.
```

**Data source.** Published `dashboard-v2.json` on R2 (HTTPS GET by the
widget; KWGT update interval configurable, typical floor ~5–30 min):
`meta.city`, `meta.generated_at`, `weather` (icon, temperature), `events[]`
(title, start, all_day), `tasks[]` (due_date, done), `birthdays[]` (name,
date, kind), `errors`.

**Effort guess: low (KWGT preset) / high (native app, deferred)** — a KWGT
preset is layout + JSON parsing formulas, distributed by exporting the
preset file to the household phones. Native App Widget stays deferred per
doc-4 unless the KWGT route proves limiting. Visual style should echo
`design/tokens.json` where KWGT's styling allows.
<!-- SECTION:NOTES:END -->
