---
id: TASK-13
title: Design a prompt pipeline for creating each new view
status: Done
assignee:
  - '@kimi'
created_date: '2026-07-31 10:19'
updated_date: '2026-07-31 18:20'
labels:
  - enhancement
dependencies: []
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Every new "view" we create (e.g. a new dashboard surface like the widget/desktop/terminal/AI options being explored in TASK-12, or any new rendering of the dashboard data) should go through the same pipeline. Design that pipeline as a documented list of prompts that can be followed per view. The stages, in order: (1) Propose view — the proposal must already include a lofi design (rough layout/structure sketch) so the value of the view is visible before any decision is made; (2) Approve/reject view — explicitly mark the view as "to implement" or "skip"; (3) Refine view requirements — nail down what the view must show and for whom; (4) Design — covers both UX design (detailed interaction and visual design) and a concise, mostly high-level technical design (what technology is used, how communication happens, e.g. which data source is read and how); (5) Implementation — build it; (6) Improve — iterate based on real usage. For each stage, define the prompt to run, its inputs, its expected output/artifact, and the gate to move to the next stage (who/what approves). The pipeline document should live in the repo (e.g. plan/ or backlog/docs/) so it can be reused for every future view.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Pipeline document exists in the repo listing the six stages: Propose view (with lofi design), Approve/reject view, Refine view requirements, Design (UX + technical), Implementation, Improve
- [x] #2 Each stage has a concrete prompt, its required inputs, and its expected output/artifact. Prompts must be concise and designed with token economy in mind.
- [x] #3 The Approve/reject stage records an explicit decision per view: "to implement" or "skip" (or an equivalent marking with the same outcome), so skipped views are visibly excluded and approved views flow into the next stages
- [x] #4 The Propose stage requires a lofi design (rough layout/structure sketch) as part of the proposal artifact, so the value of every view can be judged before approval
- [x] #5 The Design stage covers both UX design and a concise technical design (high-level: what technology, how communication/data flow happens)
- [x] #6 Each stage defines a gate: what must be true (and who decides) before moving to the next stage
- [x] #7 The document explains how the pipeline is applied when a new view is proposed (entry point, e.g. from TASK-12 follow-ups)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Decide document home: plan/VIEW_PIPELINE.md (repo-process doc alongside PLAN.md), referenced from AGENTS.md project-structure tree.
2. Write the pipeline document: purpose/scope, entry point (how a new view enters, incl. TASK-12 follow-ups), six stages (Propose w/ lofi design, Approve/reject, Refine requirements, Design UX+technical, Implementation, Improve) — each with a concise token-economical prompt, inputs, output/artifact, and an explicit gate (who/what approves). Design stage references design/ token system for non-TRMNL views. Include a per-view state record convention (tracked via Backlog tasks with stage labels/decision notes).
3. Update AGENTS.md project-structure tree to list plan/VIEW_PIPELINE.md.
4. Verify: read the doc back, check all 7 ACs against actual content; run pytest -q as a sanity check.
5. Finalize per backlog instructions task-finalization: evidence per AC, check ACs, notes, final summary, status Done.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Wrote plan/VIEW_PIPELINE.md: six stages (Propose w/ lofi design, Approve/reject, Refine requirements, Design UX+technical, Implementation, Improve), each with a concise prompt (line-budgeted for token economy), inputs, output/artifact, and an explicit gate. Per-view tracking = Backlog task with label 'view'; owner decides Approve/reject and Design gates. Entry-point section covers TASK-12/doc-4 follow-ups. Updated AGENTS.md project-structure tree and Notes-for-agents to reference the pipeline.

Verification: re-read plan/VIEW_PIPELINE.md in full. AC1: file exists, six stages listed at lines 5-12. AC2: every stage section has Inputs/Prompt/Output-Gate bullets; prompts carry line budgets (<=60/<=40/<=80/<=20) for token economy. AC3: Stage 2 records 'Decision: to implement/skip' per view on its Backlog task; skip -> Done so skipped views are visibly excluded. AC4: Stage 1 prompt requires a lofi ASCII sketch and states a proposal without one is incomplete. AC5: Stage 4 prompt has two parts: UX design (design/ tokens) + high-level technical design (technology, data flow). AC6: every stage has a Gate bullet naming who decides (owner at Approve/reject and Design). AC7: 'How the pipeline is applied (entry point)' section names doc-4/TASK-12 follow-ups as entry points. Sanity check: pytest -q -> 259 passed, 4 warnings (no code touched).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Created plan/VIEW_PIPELINE.md: a reusable six-stage prompt pipeline for every new dashboard view (Propose w/ mandatory lofi design -> Approve/reject with explicit per-view 'to implement'/'skip' decision -> Refine requirements -> Design covering UX via design/ tokens plus concise technical design -> Implementation -> Improve). Each stage defines a concise line-budgeted prompt, its inputs, its output artifact, and its gate (owner decides Approve/reject and Design). Entry-point section explains how views enter the pipeline, incl. the TASK-12/doc-4 recommendations, and per-view tracking is a Backlog task labeled 'view'. AGENTS.md updated (project-structure tree + Notes for agents). Verified by re-reading the document against all 7 acceptance criteria (details in implementation notes) and by pytest -q: 259 passed.
<!-- SECTION:FINAL_SUMMARY:END -->
