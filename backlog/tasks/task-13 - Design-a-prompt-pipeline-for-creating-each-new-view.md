---
id: TASK-13
title: Design a prompt pipeline for creating each new view
status: To Do
assignee: []
created_date: '2026-07-31 10:19'
updated_date: '2026-07-31 10:38'
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
- [ ] #1 Pipeline document exists in the repo listing the six stages: Propose view (with lofi design), Approve/reject view, Refine view requirements, Design (UX + technical), Implementation, Improve
- [ ] #2 Each stage has a concrete prompt, its required inputs, and its expected output/artifact. Prompts must be concise and designed with token economy in mind.
- [ ] #3 The Approve/reject stage records an explicit decision per view: "to implement" or "skip" (or an equivalent marking with the same outcome), so skipped views are visibly excluded and approved views flow into the next stages
- [ ] #4 The Propose stage requires a lofi design (rough layout/structure sketch) as part of the proposal artifact, so the value of every view can be judged before approval
- [ ] #5 The Design stage covers both UX design and a concise technical design (high-level: what technology, how communication/data flow happens)
- [ ] #6 Each stage defines a gate: what must be true (and who decides) before moving to the next stage
- [ ] #7 The document explains how the pipeline is applied when a new view is proposed (entry point, e.g. from TASK-12 follow-ups)
<!-- AC:END -->
