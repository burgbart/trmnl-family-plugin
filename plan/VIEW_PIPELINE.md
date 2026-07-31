# VIEW_PIPELINE.md — the view pipeline

Every new **view** of the dashboard data — a widget, desktop app,
terminal variant, AI surface, smart-speaker summary, or any other rendering —
goes through the same six stages:

1. **Propose view** — proposal includes a lofi design (rough layout/structure sketch).
2. **Approve/reject view** — explicit per-view decision: `to implement` or `skip`.
3. **Refine view requirements** — what the view must show, for whom, and its limits.
4. **Design** — UX design + concise high-level technical design.
5. **Implementation** — build it.
6. **Improve** — iterate based on real usage.

The pipeline exists so every view is judged on a visible proposal before any
effort is spent, so rejected views are visibly excluded, and so an agent told
"propose a new view" or "implement approved view X" can run the right stage
without rediscovering the process.

## Ticket structure (how stages map to Backlog tasks)

Stages are tracked as **separate Backlog tickets** (label `view`), linked by
dependencies — so the board shows where every view stands and each stage's
artifact lives on its own ticket:

- **One ticket is created when a view is proposed**, covering Stages 1–2:
  `View: <name> — Proposal`. It holds the proposal (with lofi sketch) and the
  owner's implement/skip decision.
- **On `to implement`**, the remaining stage tickets are created, each
  depending on the previous one:
  - `View: <name> — Requirements` (Stage 3, depends on the Proposal ticket)
  - `View: <name> — Design` (Stage 4, depends on Requirements)
  - `View: <name> — Implementation` (Stage 5, depends on Design; carries the
    acceptance criteria)
- **Stage 6 (Improve) has no standing ticket** — it is continuous. Small
  improvements become ordinary tasks; big ones re-enter the pipeline as a new
  Proposal ticket.

Create tickets with `backlog task create "View: <name> — <stage>" -l view
--depends-on <previous ticket id>`. Create them **one at a time**: confirm
each new ticket's ID from the CLI output before creating the next ticket in
the chain — do not batch the creations or scrape IDs blindly. (Ticket IDs
are sequential in creation order; if creation does go wrong, the
`--depends-on` chain is the source of truth for stage order and `--ordinal`
can realign board ordering.) A `skip` decision closes the Proposal
ticket as Done with the reason in its final summary — skipped views stay
visibly decided, and no downstream tickets are created.

## How the pipeline is applied (entry point)

- **Entry points:** a new view candidate arrives from (a) an exploration/comparison
  doc such as `doc-4` (TASK-12's "Checking the family dashboard from anywhere"),
  which recommends views and explicitly defers their implementation to this
  pipeline; (b) the owner's idea directly ("I want a glanceable kitchen iPad
  view"); or (c) an Improve-stage finding on an existing view that is large
  enough to be a new view.
- **Running a stage:** the agent reads this document, runs the stage prompt
  below with the listed inputs, produces the artifact on that stage's ticket
  (`backlog task edit <id> --append-notes ...`), verifies the gate, and moves
  the ticket to Done. A stage ticket is only started when its dependency is
  Done.
- **Shared ground rules for every view:** all views are read-only consumers of
  `dashboard-v2.json` (the single source of truth, published to Cloudflare R2;
  local fallbacks via `src/json_loader.resolve_input_path()`). Any non-TRMNL
  visual surface must apply the design system in `design/`
  (`design/tokens.json`, `design/index.html`, rules in `design/README.md`).

## Stages 1–2 — Proposal & decision (the first ticket)

Ticket: `View: <name> — Proposal` (label `view`), created as soon as a view
candidate arrives.

- **Inputs:** the trigger (comparison-doc recommendation, owner idea, or Improve
  finding); this document's ground rules; `README.md`/`AGENTS.md` only if the
  proposer is unfamiliar with the project.
- **Prompt (proposal):**
  > Propose view "<name>". In ≤60 lines: (1) one-paragraph pitch — who uses it,
  > where, and why it's worth having; (2) lofi design — an ASCII/text sketch of
  > the layout and structure (sections, what data each shows, rough sizing);
  > (3) data source: which fields of `dashboard-v2.json` it reads;
  > (4) effort guess: low / medium / high, one line why. No code, no detailed
  > visuals.
- **Artifact:** the proposal in the ticket's notes. **Must include the lofi
  sketch** — a proposal without one is incomplete.
- **Prompt (decision):**
  > Show the proposal for view "<name>" to the owner and ask: implement or skip?
  > Record the verdict and a one-line reason on the ticket.
- **Gate:** the **owner decides**, recorded on the ticket as
  `Decision: to implement — <reason>` or `Decision: skip — <reason>`.
  `to implement` → create the Requirements/Design/Implementation tickets
  (dependency chain), then close this ticket Done. `skip` → close this ticket
  Done with the skip decision; the view exits the pipeline.

## Stage 3 — Refine requirements (ticket)

Ticket: `View: <name> — Requirements`, depends on the Proposal ticket.

- **Inputs:** the approved proposal; relevant existing docs/code only as needed
  (e.g. `src/serialization.py` for the exact JSON fields).
- **Prompt:**
  > Refine requirements for approved view "<name>". In ≤40 lines: (1) audience
  > and context of use; (2) must-show data (exact `dashboard-v2.json` fields);
  > (3) must-not / out of scope; (4) freshness needs (poll interval acceptable?);
  > (5) platform constraints; (6) 3–6 testable acceptance criteria. Flag any
  > open question for the owner.
- **Artifact:** the refined requirements in the ticket's notes; the acceptance
  criteria are set on the **Implementation ticket** (`backlog task edit <impl
  id> --ac ...`) so its finalization can verify them.
- **Gate:** requirements contain no unresolved blockers; open questions either
  answered by the owner or explicitly deferred. Agent checks completeness; owner
  resolves flagged questions. Close Done when met.

## Stage 4 — Design (ticket)

Ticket: `View: <name> — Design`, depends on the Requirements ticket.

- **Inputs:** refined requirements; the design system in `design/` (for any
  non-TRMNL visual surface — read `design/README.md` rules and the relevant
  tokens, not the whole style guide); existing similar code if the view extends
  a current consumer (e.g. `terminal_dashboard.py`, `src/json_loader.py`).
- **Prompt:**
  > Design view "<name>" against its requirements. Two parts, ≤80 lines total:
  > (1) UX design — layout/states (loading, error, empty), interaction if any,
  > which `design/` tokens or terminal theme apply; (2) technical design, kept
  > high-level — technology/runtime, where the artifact lives (this repo or
  > elsewhere), and the data flow (which JSON URL/path is read, poll interval,
  > error handling per the payload's `errors` entries). No implementation code;
  > pseudocode only where a flow is non-obvious.
- **Artifact:** the design note on the ticket (or a short `backlog doc` linked
  from it). UX part references `design/` token names, not ad-hoc colors.
- **Gate:** **owner approves the design** (quick review — this is the last cheap
  moment to change direction). Both parts must be present; the technical part
  must name the data source and how it's read. Close Done when approved.

## Stage 5 — Implementation (ticket)

Ticket: `View: <name> — Implementation`, depends on the Design ticket, carries
the acceptance criteria from Stage 3.

- **Inputs:** the approved design; the acceptance criteria; the repo conventions
  in `AGENTS.md` (code style, tests with pytest, design-system rules enforced by
  `tests/test_design_tokens.py` where applicable).
- **Prompt:**
  > Implement view "<name>" per its approved design and acceptance criteria.
  > Follow AGENTS.md conventions; add/extend tests like neighboring code does;
  > run `pytest -q`. Record progress in task notes. If the design proves wrong
  > on a material point, stop and go back to Stage 4 instead of improvising.
- **Artifact:** working code/artifact in the repo (or the external location
  named in the design), tests passing, notes on the ticket.
- **Gate:** every acceptance criterion verified with objective evidence (tests,
  commands run, rendered output inspected), per `backlog instructions
  task-finalization`; the ticket moves to Done.

## Stage 6 — Improve (continuous, no standing ticket)

- **Inputs:** real usage of the shipped view; owner feedback; observed
  annoyances or misses.
- **Prompt:**
  > Review view "<name>" after real use. In ≤20 lines: what works, what's
  > missing or annoying, and a short list of concrete improvements — each
  > marked *small* (a new ordinary task, or a direct fix) or *big* (treat as a
  > new view proposal → new `View: … — Proposal` ticket).
- **Artifact:** the improvement list (e.g. on a `backlog doc` or the review
  conversation); small items become task(s), big items re-enter the pipeline.
- **Gate:** none — this stage is continuous and re-entered any time after
  shipping. An improvement only leaves this stage as a tracked fix or a new
  Proposal ticket.

## Current pipeline state

See `backlog task list --labels view --plain` for all views and their stage
tickets. The TASK-12 follow-ups recommended in `doc-4` (terminal one-shot mode,
AI skill/MCP, desktop app, Scriptable iOS widget) enter at Stage 1 when the
owner asks for them.

Note: doc-4 recommended the desktop option as a macOS xbar/SwiftBar menu-bar
plugin; the owner redirected it (31 Jul 2026) and then split it into two
views: a full-screen desktop app using the proven `dashboard-md-launcher`
technique (Python server + HTML + pywebview + PyInstaller .app) — approved,
Proposal ticket TASK-20, stage chain TASK-25 (Requirements) → TASK-27
(Design) → TASK-26 (Implementation) — and a macOS menu-bar quick view
(native SwiftUI MenuBarExtra direction per architecture advisory), Proposal
ticket TASK-28.
