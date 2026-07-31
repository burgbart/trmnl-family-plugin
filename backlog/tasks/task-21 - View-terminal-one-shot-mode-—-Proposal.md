---
id: TASK-21
title: 'View: terminal one-shot mode — Proposal'
status: To Do
assignee: []
created_date: '2026-07-31 20:40'
labels:
  - view
dependencies: []
ordinal: 20000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Proposal + decision ticket (pipeline Stages 1-2, plan/VIEW_PIPELINE.md) for a one-shot, non-interactive terminal view of the family dashboard (doc-4 recommendation #1): run one command, print the current state, exit — usable over SSH or piped into other tools. Extends terminal_dashboard.py. The Stage-1 proposal with lofi design is in the notes. Awaiting owner decision: on 'to implement', create the Requirements / Design / Implementation tickets linked with --depends-on; on 'skip', close with the reason.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Stage 1 — Proposal (per plan/VIEW_PIPELINE.md)

**Pitch.** A one-shot terminal view: run one command, get the whole family
state printed, done — no interactive UI. Ideal over SSH from anywhere, in a
tmux pane, a cron mail, or piped into other tools. It extends the existing
`terminal_dashboard.py`, which already loads the JSON and renders the same
data interactively; this adds a non-interactive print-and-exit mode.

**Lofi design.**

```
$ python terminal_dashboard.py --once

 Fri 31 Jul · Amsterdam      ☁ Overcast 23° (fl 21°) · No rain expected
────────────────────────────────────────────────────────────────────────
 EVENTS                      TASKS DUE (3)             ANNIVERSARIES
 Today 14:00  Dentist       □ Send packages back (!)   16 Aug Wedding 💍
 all day      Hamide visits □ Water the plants         2 Sep Emma 🎂
 Sat 09:30    Swimming      □ Buy birthday gift
────────────────────────────────────────────────────────────────────────
 (!) Tasks not loaded   <- line shown only when errors.tasks is set
 refreshed 18:40 · source: pub-<hash>.r2.dev/dashboard-v2.json
```

Sections side by side where the terminal is wide, stacked when narrow;
Rich markup, colors from `src/terminal_theme.py` (THEME), no interaction,
exit code 0 (or 1 when any `errors.*` is set, for scripting).

**Data source.** `dashboard-v2.json` via the existing
`src/json_loader.resolve_input_path()` chain (CLI arg → `DASHBOARD_JSON_URL`
→ R2 public URL → local `output/dashboard-v2.json`): `meta`, `weather`,
`events[]`, `tasks[]`, `birthdays[]`, `errors` — exactly what the
interactive view already consumes.

**Effort guess: low** — loading and rendering helpers exist; add a `--once`
flag and a plain print path to `terminal_dashboard.py`. Doc-4 rated this the
cheapest option overall.
<!-- SECTION:NOTES:END -->
