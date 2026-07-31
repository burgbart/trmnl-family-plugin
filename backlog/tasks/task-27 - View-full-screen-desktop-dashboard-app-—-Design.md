---
id: TASK-27
title: 'View: full-screen desktop dashboard app — Design'
status: To Do
assignee: []
created_date: '2026-07-31 20:52'
updated_date: '2026-07-31 21:04'
labels:
  - view
dependencies:
  - TASK-25
ordinal: 24500
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Stage 4 ticket (plan/VIEW_PIPELINE.md) for the full-screen desktop dashboard app (proposal TASK-20). Start only after Requirements (TASK-25) is Done. Run the Stage-4 prompt: UX design (layout/states/interaction, design/ tokens) + high-level technical design (technology, artifact location, data flow, poll interval, error handling). Owner approves the design at this gate.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Handoff — where we are (31 Jul 2026, end of session)

**Status: ready to start Stage 4.** Dependency TASK-25 (Requirements) is
Done; this ticket is unblocked but not yet started (a fresh-context subagent
briefed to run it was interrupted before making any changes).

**Inputs to read (in order):**
1. `plan/VIEW_PIPELINE.md` — Stage 4 prompt/artifact/gate are authoritative.
2. TASK-25 notes — refined requirements, incl. **update v2**: freshness
   default **10 min** (configurable); **the app runs the collection cycle
   itself** (src/unified_fetcher → src/serialization dashboard-v2.json →
   src/upload to Cloudflare R2, taking over the run_workflow_loop/server.py
   role while running) and renders from the locally collected JSON; design
   system compliance is non-negotiable.
3. TASK-20 notes — approved v2 proposal with the 3-column full-screen lofi.
4. TASK-26 — the 7 acceptance criteria the design must satisfy.
5. Codebase: `server.py` (background-refresh thread pattern to mirror),
   `src/pipeline.py`, `src/unified_fetcher.py`, `src/serialization.py`,
   `src/upload.py`, `design/README.md` + token names from design/tokens.json.
6. Reference architecture (owner wants this technique):
   ~/personal-projects/dashboard (dashboard-md-launcher) — its AGENTS.md,
   `dashboard_hub/desktop.py`, `packaging/dashboard-desktop.spec`:
   stdlib HTTP server + HTML UI in a pywebview window, PyInstaller .app.

**Design must answer:** how the pywebview window and the 10-min collection
loop coexist (mirror server.py's background thread; webview refreshes from
the newly collected JSON each cycle); failure behavior (last-good-data +
stale timestamp; missing R2 credentials = local-only mode, view must not
break; per-source errors → (!) Not loaded); module layout in this repo;
PyInstaller packaging path.

**Three deferred questions** — draft these defaults, owner may override at
the approval gate: (a) launch at login: no; (b) window: remember
size/position rather than forced full screen; (c) in-window menu-bar-style
summary line: no (stays exclusive to TASK-28's tray view).

**Gate:** owner approves the design — do NOT close this ticket without that
explicit approval. Then TASK-26 (Implementation, depends on this ticket,
carries the 7 ACs) unblocks.

**Broader context:** sibling Proposal tickets awaiting owner decisions —
TASK-21 (terminal one-shot), TASK-22 (AI skill/MCP), TASK-23 (iOS widget),
TASK-24 (Android widget), TASK-28 (menu-bar quick view, split from TASK-20).
All changes committed and pushed through d8c77b1.
<!-- SECTION:NOTES:END -->
