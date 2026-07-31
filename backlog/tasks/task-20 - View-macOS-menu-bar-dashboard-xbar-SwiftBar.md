---
id: TASK-20
title: 'View: full-screen desktop dashboard app — Proposal'
status: To Do
assignee: []
created_date: '2026-07-31 20:19'
updated_date: '2026-07-31 20:38'
labels:
  - view
dependencies: []
ordinal: 19000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Proposal + decision ticket (pipeline Stages 1-2, plan/VIEW_PIPELINE.md) for a desktop view of the family dashboard: a simple launchable full-screen application, modeled after ~/personal-projects/dashboard (dashboard-md-launcher: Python server + HTML UI, optional pywebview native window). Supersedes the original xbar/SwiftBar menu-bar idea from doc-4 recommendation #3 (owner redirect, 31 Jul 2026). The v2 proposal with lofi design is in the notes. Awaiting owner decision: on 'to implement', create the Requirements / Design / Implementation tickets linked with --depends-on; on 'skip', close with the reason.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Stage 1 — Proposal (per plan/VIEW_PIPELINE.md)

**Pitch.** Household members working on the Mac see family state without
opening anything: the menu bar always shows today's essence (temperature +
next event or due-task count), and one click opens a dropdown with upcoming
events, due tasks, and anniversaries. It is the always-visible desktop glance
that complements the TRMNL at home and requires zero new backend — it polls
the published dashboard-v2.json.

**Lofi design.**

```
Menu bar (always visible):
┌──────────────────────────┐
│  ☁ 23° · 14:00 Dentist   │   <- icon + temp + next timed event
└──────────────────────────┘      (or "3 tasks due" when no event today)

Dropdown (on click):
┌─────────────────────────────────────┐
│ Amsterdam — Overcast, 23° (fl 21°)  │  weather: description/temp/feels_like
│ No rain expected today              │  weather.alert
│─────────────────────────────────────│
│ NEXT EVENTS                         │
│  Today 14:00   Dentist              │  events[] (title, start, all_day)
│  Sat 09:30     Swimming lesson      │
│  29 Jul–10 Aug Hamide visits        │  all-day shown as date range
│─────────────────────────────────────│
│ TASKS DUE (3)                       │
│  □ Send packages back (overdue)     │  tasks[] (title, due_date, done)
│  □ Water the plants (today)         │
│─────────────────────────────────────│
│ ANNIVERSARIES                       │
│  16 Aug  Wedding 💍                 │  birthdays[] (name, date, kind)
│─────────────────────────────────────│
│ (!) Tasks not loaded                │  only when errors.tasks != null
│─────────────────────────────────────│
│ Refreshed 18:40 · Refresh now       │  meta.generated_at + manual refresh
└─────────────────────────────────────┘
```

**Data source.** Published `dashboard-v2.json` on R2 (HTTPS GET, poll
interval e.g. 5 min): `weather` (description, temperature, feels_like, icon,
alert), `events[]` (title, start, end, all_day), `tasks[]` (title, due_date,
done), `birthdays[]` (name, date, kind), `meta.generated_at`,
`meta.city`, and `errors` for explicit not-loaded states.

**Effort guess: low** — xbar/SwiftBar plugins are a single script that prints
menu-bar text; JSON fetch + format only, no app, no distribution.

## Direction change (owner, 31 Jul 2026)

Not a menu-bar plugin. The desktop view should be a simple application that
launches full screen — modeled after `~/personal-projects/dashboard`
(`dashboard-md-launcher`: Python server + HTML UI, optional pywebview native
window, packaged `.app`). Far more screen estate than a menu bar; the lofi
below uses it. **Stage-1 proposal v2 supersedes v1.**

## Stage 1 — Proposal v2

**Pitch.** A family dashboard app for the Mac (or any desktop): double-click
to launch, full screen, and the whole household state is visible at once —
weather + 5-day forecast, the calendar grouped by day, all task lists, and
anniversaries. Unlike the TRMNL (small, at home) and the menu-bar idea
(glance only), this is the "sit down and see everything" view, e.g. on a
kitchen iPad/Mac or a second monitor. It reuses the existing collect/JSON
pipeline; the app is a read-only renderer of `dashboard-v2.json`.

**Lofi design (full screen, 3 columns + header/footer).**

```
┌────────────────────────────────────────────────────────────────────┐
│ Friday 31 July · Amsterdam        ☁ Overcast 23° (fl 21°)   ↻ 18:40│
│────────────────────────────────────────────────────────────────────│
│ WEATHER          │ CALENDAR                  │ TASKS               │
│                  │                           │                     │
│   ☁  23°         │ Today                     │ Gözde en Bart (3 due)│
│   Overcast       │  14:00 Dentist            │  □ Send packages back│
│   feels like 21° │  all day · Hamide visits  │  □ Water the plants  │
│   No rain today  │                           │  □ ...               │
│                  │ Tomorrow                  │                     │
│  Fri 24°/19° ☁   │  09:30 Swimming lesson    │ Household (1 due)   │
│  Sat 21°/17° 🌧  │                           │  □ ...               │
│  Sun 22°/18° ⛅  │ Sat 2 Aug                 │                     │
│  Mon 25°/19° ☀   │  11:00 Brunch at Anna's   │ Upcoming (no due)   │
│  Tue 24°/18° ☁   │                           │  □ ...               │
│                  │ Sun 3 Aug — nothing       │                     │
│                  │                           │                     │
│──────────────────┴───────────────────────────┴─────────────────────│
│ ANNIVERSARIES  16 Aug · Wedding 💍    2 Sep · Emma 🎂               │
│ (!) Tasks not loaded  <- shown only when errors.* is set            │
└────────────────────────────────────────────────────────────────────┘
```

States: loading (skeleton/spinner until first fetch), per-source error
(footer `(!)` lines, section keeps last good data or shows empty), empty
("Sun 3 Aug — nothing", "No tasks due").

**Data source.** Published `dashboard-v2.json` on R2 (HTTPS GET, poll every
60 s, matching the pipeline's refresh): `meta` (city, generated_at),
`weather` (description, temperature, feels_like, icon, alert, forecast[]),
`events[]` (title, start, end, all_day), `task_lists[]`/`tasks[]` (name,
title, due_date, done, priority), `birthdays[]` (name, date, kind), and
`errors` for explicit not-loaded states. Visual style per `design/tokens.json`
(non-TRMNL view — the design system applies).

**Effort guess: medium** — data loading and JSON contract already exist, but
the full-screen HTML view is new (unlike the menu-bar script), plus a thin
launcher (local server + browser/pywebview, like dashboard-md-launcher).
No backend work; packaging to a `.app` is optional polish.

Pipeline model changed (owner, 31 Jul 2026): stages are now separate tickets linked by dependencies instead of one ticket with stages in notes. This ticket is the Stage 1-2 Proposal/decision ticket for the view; downstream tickets will be created on approval.
<!-- SECTION:NOTES:END -->
