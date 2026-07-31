---
id: TASK-25
title: 'View: full-screen desktop dashboard app — Requirements'
status: Done
assignee:
  - '@kimi'
created_date: '2026-07-31 20:52'
updated_date: '2026-07-31 21:00'
labels:
  - view
dependencies:
  - TASK-20
ordinal: 24000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Stage 3 ticket (plan/VIEW_PIPELINE.md) for the full-screen desktop dashboard app approved in TASK-20. Run the Stage-3 prompt: refine requirements from the approved v2 proposal (see TASK-20 notes) - audience/context, must-show data (exact dashboard-v2.json fields), out of scope, freshness needs, platform constraints, 3-6 testable acceptance criteria (set the ACs on the Implementation ticket). Flag open questions for the owner.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Refine requirements from TASK-20's approved v2 proposal per the Stage-3 prompt (audience, exact JSON fields, out of scope, freshness, platform constraints, 3-6 testable ACs). 2. Record requirements in this ticket's notes. 3. Set the acceptance criteria on the Implementation ticket (TASK-26). 4. Defer minor open questions to the Design stage; close ticket.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Stage 3 — Refined requirements (per plan/VIEW_PIPELINE.md)

**1. Audience & context.** Household members at a Mac; the "sit down and see
everything" full-screen view (kitchen Mac, second monitor, or a quick
full-screen check). Launched manually like any app (`.app` or CLI); no Dock
presence requirement yet.

**2. Must-show data (exact `dashboard-v2.json` fields).**
- `meta.city`, `meta.generated_at` (shown as "refreshed" time), `meta.reference_date`
- `weather`: `description`, `temperature`, `feels_like`, `icon`, `alert`,
  `forecast[]` (`date`, `description`, `temperature_high`, `temperature_low`,
  `icon`, `precipitation_probability`)
- `events[]`: `title`, `start`, `end`, `all_day` — grouped by day, empty days
  shown as "nothing"
- `task_lists[]`: `name`, `tasks[]` (`title`, `due_date`, `done`, `priority`)
  — per-list sections, due/overdue first; `tasks[]` (top-level) as fallback
- `birthdays[]`: `name`, `date`, `kind` (birthday vs anniversary icon/label)
- `errors`: `events`, `tasks`, `birthdays` — per-source `(!) Not loaded`

**3. Must-not / out of scope.** No menu-bar/tray surface (that is TASK-28);
read-only — no task completion, event editing, or any write-back; no TRMNL
Liquid template changes; no signing/notarization or distribution beyond the
owner's Mac(s); no mobile/tablet layout work.

**4. Freshness.** Poll the published `dashboard-v2.json` every 60 s
(configurable). `meta.generated_at` is always visible; on fetch failure the
last good data stays on screen with its (stale) timestamp — never fabricated
data.

**5. Platform constraints.** macOS first (owner's machine); Python 3.11+.
Technique mirrors `dashboard-md-launcher`: stdlib-local HTTP server + HTML
UI + pywebview native window; PyInstaller `.app` packaging as in that repo's
`packaging/`. Data source configurable: R2 URL default, local
`output/dashboard-v2.json` or `server.py` endpoint as override. Visual style
per `design/tokens.json` (light + dark, following OS setting);
`tests/test_design_tokens.py` rules apply. Code lives in this repo.

**6. Acceptance criteria.** Set on the Implementation ticket (TASK-26).

**Open questions (deferred to Stage 4 — Design).** (a) Launch at login?
(b) Always full screen, or remember window size/position? (c) Is the
menu-bar label text ("☁ 23° · next event") wanted inside the desktop app's
window too, or only in TASK-28's tray? None blocks requirements; all are
cheap design decisions.

## Requirements update v2 (owner, 31 Jul 2026)

Supersedes the corresponding parts of the v1 requirements above:

1. **Freshness: default 10 minutes** (configurable), not 60 s.
2. **The app IS the data collector.** The desktop app runs the collection
   pipeline itself: fetch all sources (src/unified_fetcher), build
   dashboard-v2.json (src/serialization), and upload it to Cloudflare R2
   (src/upload) so TRMNL and all other views pick up the fresh data — i.e.
   the app takes over the role of run_workflow_loop.py / server.py while it
   runs. The rendered view reads the locally collected JSON from the same
   cycle (no separate polling of R2 needed for the app's own display).
3. **Design system is non-negotiable** (reaffirmed): the view must follow
   design/ (tokens.json, style-guide rules in design/README.md), light +
   dark themes, no ad-hoc colors — enforced by tests/test_design_tokens.py.

Consequences: R2 upload credentials come from the existing .env/env
configuration like the current pipeline; a no-upload local mode remains
useful for development (missing R2 credentials must not break the view).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Stage 3 complete (incl. owner requirements update v2). Refined requirements for the full-screen desktop dashboard app recorded in notes: audience/context; exact dashboard-v2.json fields per section; out of scope (no tray surface, read-only view, no distribution signing); freshness default 10 minutes (configurable); the app runs the collection pipeline itself - fetch sources, build dashboard-v2.json, upload to Cloudflare R2 for TRMNL - and renders its view from the locally collected JSON; design system (design/) compliance is non-negotiable (light+dark, token-driven). Seven testable acceptance criteria set on the Implementation ticket TASK-26 covering: native window launch, the collect->JSON->R2 cycle, all five rendered sections, refresh/failure behavior (incl. no-upload local mode), per-source error states, design-system compliance, and env/.env configuration. Three minor open questions (launch at login, window sizing, in-window summary line) explicitly deferred to Stage 4 (TASK-27). Verified by viewing TASK-25 notes and confirming all 7 ACs present on TASK-26 (backlog task view).
<!-- SECTION:FINAL_SUMMARY:END -->
