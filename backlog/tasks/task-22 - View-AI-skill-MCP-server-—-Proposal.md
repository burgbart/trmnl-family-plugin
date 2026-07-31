---
id: TASK-22
title: 'View: AI skill / MCP server — Proposal'
status: To Do
assignee: []
created_date: '2026-07-31 20:40'
labels:
  - view
dependencies: []
ordinal: 21000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Proposal + decision ticket (pipeline Stages 1-2, plan/VIEW_PIPELINE.md) for an AI surface to the family dashboard (doc-4 recommendation #2): an agent skill and/or small read-only MCP server so assistants can answer 'what is next for the family' from the published dashboard-v2.json. The Stage-1 proposal with lofi design is in the notes. Awaiting owner decision: on 'to implement', create the Requirements / Design / Implementation tickets linked with --depends-on; on 'skip', close with the reason.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Stage 1 — Proposal (per plan/VIEW_PIPELINE.md)

**Pitch.** Ask any assistant "what's next for the family?" and get an answer
from live data — no app, no screen, works from any device where an assistant
runs. Two variants, same idea: (a) an agent skill — a small document that
tells the assistant to fetch and interpret the published JSON; (b) a tiny
read-only MCP server exposing tools like `get_dashboard` so MCP-capable
assistants can query it directly. Doc-4 rated this the widest coverage per
effort of all options.

**Lofi design (interaction structure).**

```
 You: "What's next for the family?"
         │
         ▼
 ┌──────────────────────────────────────┐
 │ skill or MCP tool: get_dashboard     │  HTTPS GET dashboard-v2.json (R2)
 │  → compact summary: weather, next    │  → trimmed to essentials
 │    3 events, due tasks, next         │    (token economy)
 │    anniversaries, errors.*           │
 └──────────────────────────────────────┘
         │
         ▼
 Assistant: "Dentist today at 14:00. 3 tasks due, one overdue
 (send packages back). Wedding anniversary in 16 days."
```

Possible later tools (not part of the first cut): `get_events(days=N)`,
`get_tasks(due_only=true)`. Error state: when `errors.*` is set, the
assistant must say "tasks not loaded" rather than invent data.

**Data source.** Published `dashboard-v2.json` on R2 (HTTPS GET, no auth):
`meta`, `weather`, `events[]`, `tasks[]`, `birthdays[]`, `errors`. The skill
variant needs no code at all; the MCP variant wraps the same fetch in one or
two read-only tools (e.g. Python + FastMCP).

**Effort guess: very low (skill) / low (MCP server)** — a skill is a single
document; an MCP server is a small read-only script. No backend, no UI.
<!-- SECTION:NOTES:END -->
