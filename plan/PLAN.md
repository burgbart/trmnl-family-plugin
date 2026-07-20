# PLAN.md — Liquid/TRMNL private-plugin rewrite

This supersedes all prior plan documents. It reflects decisions made
2026-07-20 and reframes the project around a YAGNI goal: **stop rendering
PNGs ourselves, publish JSON, and let a TRMNL private plugin render it via
Liquid** — the same templating language TRMNL uses
(https://shopify.dev/docs/api/liquid).

## Why

The current project (Pillow rendering of `dashboard.png`/`dashboard_x.png`,
per-device layout code, font asset management) duplicates work TRMNL already
does natively for private plugins. Moving rendering into a TRMNL private
plugin removes the heaviest third-party dependency (Pillow), removes all
pixel-layout code, and lets TRMNL handle device-specific rendering concerns
(dithering, refresh, etc.) that we currently hand-roll.

## End state

1. **Data collection** (mostly unchanged): weather, calendar, tasks →
   `dashboard.json`, published to Cloudflare R2. This is the only artifact
   TRMNL needs.
2. **TRMNL private plugin** (new, external to this repo's runtime): configured
   with the **Polling** strategy against the public R2 JSON URL, and Liquid
   markup pasted in from `templates/` in this repo. TRMNL renders the actual
   device image — we no longer generate PNGs.
3. **Local preview** (new): a static HTML export (`preview.html`) that renders
   the same Liquid templates against the same JSON (dummy or real) inside
   CSS-framed containers sized/colored to emulate each device profile
   (trmnl-og, trmnl-x, and future profiles), with a JS toggle to switch
   between them. No live server-side Liquid rendering per request — the
   export is a build step, the server just serves the resulting file.
4. **Server** (simplified, stdlib `http.server`, no new framework): serves
   `dashboard.json` and `preview.html`, runs the refresh loop, and can drop
   into the existing Rich terminal dashboard on demand (`t` key), same as
   today.
5. **GitHub Actions** (simplified): collects data and publishes JSON only —
   no PNG render steps. Alternative to running the server yourself.
6. **Repo is public**: README must include a full walkthrough for a stranger
   to set up their own TRMNL account, create a private plugin, point it at
   their own published JSON, and paste in the Liquid templates from this repo.

## Key decisions (from clarifying questions)

- **Delivery to TRMNL**: Polling. TRMNL pulls `dashboard.json` from our public
  R2 URL on its own interval. No webhook push code needed.
- **Liquid source of truth**: this repo (`templates/`). TRMNL's plugin editor
  is just where we paste the current version; the repo is authoritative and
  versioned.
- **Local preview mechanism**: static HTML export, not a live template server.
  A script renders Liquid → HTML once (or on each refresh cycle) and writes
  one `preview.html` containing all device frames with a JS toggle.
- **Cutover style**: build the new Liquid path alongside the existing Pillow
  path, verify it end-to-end (dummy data → local preview → real TRMNL plugin
  render), *then* do one dedicated pass to delete Pillow/PNG code.
- **Server stack**: keep stdlib `http.server` — no Flask/FastAPI. Matches the
  YAGNI goal and the current `server.py` shape.
- **Liquid engine (local)**: [`python-liquid`](https://jg-rp.github.io/liquid/)
  — closest fidelity to Shopify/TRMNL Liquid syntax among Python options.
- **TRMNL account**: not set up yet. Plan and README must include first-time
  setup steps (account, private plugin, polling URL, pasting markup) written
  for a public-repo stranger, not just future-us.

## Target architecture

```
collect_unified_data.py  → src/unified_fetcher.py → dashboard.json → R2 (unchanged)
templates/
  ├── partials/*.liquid          # shared sections: weather, calendar, tasks, birthdays
  ├── devices/og.liquid          # trmnl-og full template (includes partials)
  └── devices/x.liquid           # trmnl-x full template (includes partials)
src/liquid_render.py             # render(device_profile, data) -> HTML string, via python-liquid
export_preview.py                # CLI: renders all device profiles -> preview.html (static, JS-toggle)
server.py                        # stdlib http.server: /dashboard.json, /preview.html, refresh loop, terminal UI
terminal_dashboard.py            # unchanged (rich-based, reads dashboard.json)
.github/workflows/generate-dashboard.yml  # collect + publish JSON only
```

## What gets removed (Phase 6, after the above is verified)

- `src/dashboard.py` (Pillow rendering)
- Pillow dependency, `assets/*.ttf` fonts (unless TRMNL markup needs custom
  fonts — check before deleting)
- `output/dashboard.png`, `output/dashboard_x.png`
- PNG-specific code paths in `src/upload.py`, `src/pipeline.py`,
  `run_local.py`
- PNG-specific tests (`tests/test_render.py` PNG assertions)

## Open items to resolve during implementation (not blocking the plan)

- OG grayscale level should be configurable (requested 2026-07-20): the
  original PNG dashboard used 4-level grayscale for OG (see
  `DESIGN_REFERENCE.md`), but the current `OG_PROFILE.grayscale_levels` in
  `src/config.py` is hardcoded to 2, giving a harsher CSS contrast
  approximation in `export_preview.py` than the original render. Add a config
  knob so 4-level can be selected — see `TASKS.md` task 2.5.

- Exact mechanism TRMNL uses to expose polled JSON fields inside Liquid
  (e.g. whether the whole payload is available as one variable, or fields are
  mapped individually in the plugin config) — confirm against real TRMNL docs
  during Phase 4, adjust `templates/` accordingly.
- Whether TRMNL private plugins support custom web fonts in Liquid/CSS, or
  whether we're limited to TRMNL's built-in font set — decides whether
  `assets/*.ttf` survives the cleanup pass.

See `TASKS.md` for the phased, parallelizable task breakdown.

## Model & effort guidance (cost control)

Most of this rewrite is mechanical (file moves, boilerplate CLI wiring, YAML
edits) and doesn't need a top-tier model or high reasoning effort. Reserve
that budget for the few genuinely judgment-heavy steps: matching the existing
visual design in Liquid, and figuring out TRMNL's actual data-binding
behavior once we're working against the real product. Rule of thumb: **start
every task at the lowest tier below and only step up if the result is wrong
or the task stalls** — don't pre-select a bigger model "to be safe."

| Phase | Nature of the work | Recommended model | Effort | Why |
|---|---|---|---|---|
| 0 — Groundwork | Add a dependency, write a design-notes summary | Haiku (or Sonnet) | low | Pure lookup/summarization, no design decisions |
| 1.1 — Variable contract | Deciding the JSON→Liquid shape | Sonnet | medium | One-time architectural call; wrong choice ripples through every template |
| 1.2/1.3 — Device templates | Visual fidelity to the existing PNG design | Sonnet (Opus if results look off after 1-2 tries) | medium–high | Genuine design/layout judgment; this is where quality actually matters |
| 1.4 — Dummy fixture | Reuse existing dummy generators | Haiku | low | Mechanical, no new logic |
| 2.1/2.3 — Render pipeline, config | Standard Python plumbing | Sonnet | low–medium | Routine coding against a clear spec |
| 2.2 — Preview export + CSS toggle | Some layout/CSS judgment for device frames | Sonnet | medium | Needs to *look* right, worth a bit more care |
| 3 — Server/CLI wiring | Editing existing, working code paths | Sonnet | low | Small, well-scoped diffs against known files |
| 4.1 — Simplify upload.py | Delete PNG code paths | Haiku (or Sonnet) | low | Subtractive, mechanical |
| 4.2 — TRMNL setup guide | Public-facing docs, needs to read well for strangers | Sonnet | medium | Writing quality matters since it's public-repo-facing |
| 4.3 — Manual TRMNL verification | Debugging against real, possibly undocumented TRMNL behavior | Sonnet, step up to Opus if stuck | medium–high | Ambiguity from an external system, not from our code |
| 5 — GitHub Actions edits | YAML + small test edits | Haiku (or Sonnet) | low | Mechanical, well-understood pattern from the existing workflow |
| 6 — Cleanup/removal | Deletions + doc rewrites | Sonnet | low–medium | Low complexity, but verify nothing left references deleted code |

General principles:

- **Fan-out isn't for parallelism here** — the phases are small and mostly
  sequential-within-file, so spawning agents doesn't save wall-clock time.
  Parallelism in `TASKS.md` refers to working on independent files
  back-to-back, not concurrent agents. The reason to use a subagent per
  phase (see below) is **cost arbitrage**: if the driving session is on a
  pricier model/effort, delegate the mechanical phases to a cheaper model
  instead of burning the expensive one on boilerplate.
- **Default reasoning effort to low/medium** everywhere in this project
  unless a task explicitly says otherwise in the table above. Bump effort
  only when a first attempt is visibly wrong (template doesn't match the
  design, TRMNL doesn't render as expected) — treat that as a signal to
  step up one tier, not as a reason to start high everywhere.
- Re-check this table if TRMNL's actual Liquid data-binding turns out to be
  more complex than assumed (see "Open items" above) — Phase 4.3 might need
  more effort than estimated if TRMNL's polling/variable model is unusual.

## How to invoke phases via subagents

**For whoever's driving this (human or agent): you don't need to construct
`Agent()` calls by hand.** Just say "run phase 0" / "invoke phase 1", etc.
The agent responsible for this repo should read the relevant tasks from
`plan/TASKS.md` and the model mapping below, then build and issue the
`Agent()` call(s) itself. The table and example below exist so that mapping
survives a context reset or a different session/agent picking this up — they
are instructions *to the agent*, not a script for a human to type.

The `Agent` tool's `model` parameter (`sonnet` / `opus` / `haiku` / `fable`)
is the only real cost lever for a spawned subagent — **there is no separate
"effort" parameter for subagents**; reasoning effort is a property of how a
model reasons inline, not something passed to `Agent`. So "effort" from the
table above translates into subagent usage two ways: (1) the `model` choice
itself, and (2) explicitly telling the subagent in its prompt whether this is
mechanical ("keep it minimal, don't over-engineer") or judgment-heavy ("this
needs to visually match X, iterate until it does") — that framing is the
closest available substitute for a literal effort dial.

Run phases **one at a time, in order** (each phase's tasks depend on the
previous phase's files existing) with `run_in_background: false` so the next
phase doesn't start before the current one's files land. Map each call's
`model` from the table above:

```
Phase 0   → model: "haiku"   (0.1, 0.2 — mechanical)
Phase 1.1 → model: "sonnet"  (variable contract — one architectural call)
Phase 1.2/1.3 → model: "sonnet", escalate to "opus" only if a rendered
                preview doesn't match output/dashboard.png after 1-2 iterations
Phase 1.4 → model: "haiku"   (reuse existing dummy generators)
Phase 2.1/2.3 → model: "sonnet" (routine plumbing)
Phase 2.2 → model: "sonnet"  (CSS/layout judgment for device frames)
Phase 3   → model: "sonnet"  (editing existing working code)
Phase 4.1 → model: "haiku"   (subtractive, mechanical)
Phase 4.2 → model: "sonnet"  (public-facing docs, quality matters)
Phase 4.3 → model: "sonnet", escalate to "opus" only if stuck against
            undocumented TRMNL behavior
Phase 5   → model: "haiku"   (YAML + test edits, well-understood pattern)
Phase 6   → model: "sonnet"  (deletions + doc rewrites, verify no dangling refs)
```

Each call needs a **self-contained prompt** — the subagent has no memory of
this conversation — including: the exact task IDs from `plan/TASKS.md` being
done, the relevant file paths, what "done" looks like, and (per the point
above) whether to treat the work as mechanical or judgment-heavy. Example for
Phase 0:

```
Agent({
  description: "Phase 0 — groundwork",
  subagent_type: "claude",
  model: "haiku",
  run_in_background: false,
  prompt: "Repo: C:\\Users\\BartB\\Projects\\trmnl-family-plugin. Do tasks
    0.1 and 0.2 from plan/TASKS.md: (1) add python-liquid to
    requirements.txt and verify it installs + renders a trivial template
    in the venv; (2) inventory output/dashboard.png and dashboard_x.png
    (sections, spacing, grayscale levels, fonts used per src/dashboard.py)
    and write a short design-reference note for later Liquid template work.
    This is mechanical — keep changes minimal, don't add abstractions.
    Report back what you changed and the design-reference note content."
})
```

After each phase's agent finishes, skim its diff before starting the next
phase's call — a cheap model on a mechanical task can still misread a file
path or skip a step, and Phase N+1 will inherit that mistake silently.
