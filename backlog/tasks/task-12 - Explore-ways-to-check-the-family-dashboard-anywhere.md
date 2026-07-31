---
id: TASK-12
title: Explore ways to check the family dashboard anywhere
status: Done
assignee:
  - '@kimi'
created_date: '2026-07-31 10:06'
updated_date: '2026-07-31 16:58'
labels:
  - enhancement
dependencies:
  - TASK-15
ordinal: 12000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The TRMNL device makes it easy to see what is upcoming at home, but the goal is to check the current family dashboard state (tasks, calendar items, weather, anniversaries) easily from anywhere. Explore and compare the different ways this could work, for example: home-screen widgets (Android, iOS), desktop widgets or menu-bar/tray apps (macOS, Windows, Linux), a lightweight desktop app that shows the dashboard, a terminal/CLI command that prints the current state, an AI skill or MCP server so assistants can answer "what is next for the family", and integrations callable from a smart home speaker (e.g. a voice routine that reads out the dashboard). For each option, assess: what it would read (the published dashboard-v2.json on R2 is the obvious shared source), effort to build, how "instant" the check is, platform coverage, and whether it fits this repo or belongs elsewhere. The outcome of this task is a documented comparison and a recommendation of which options to pursue, not the implementations themselves.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Document (backlog doc) lists the explored options: mobile widgets, desktop widgets/apps, terminal/CLI check, AI skill or MCP, smart-speaker integration
- [x] #2 Each option notes what data source it would consume and show (e.g. published dashboard-v2.json), platform coverage.
- [x] #3 Implementation tasks are not included, they will be picked up in task 13
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Confirm shared data source facts from the repo (published dashboard-v2.json on R2, server.py HTTP endpoint, existing terminal_dashboard.py, design/ system for non-TRMNL views). 2. Write a backlog doc comparing the five option families — mobile widgets (Android/iOS), desktop widgets/menu-bar/tray apps, terminal/CLI check, AI skill/MCP server, smart-speaker integration — each with data source, effort, instantness, platform coverage, and repo fit. 3. Close the doc with a recommendation of which options to pursue. 4. No implementations (those follow via TASK-13 pipeline).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created backlog doc-4 'Checking the family dashboard from anywhere: options comparison'. Verified via 'backlog doc view doc-4 --plain': all five option families present (mobile widgets, desktop widgets/menu-bar/tray, terminal/CLI, AI skill/MCP, smart speaker), each with data source (dashboard-v2.json on R2 / local fallbacks) and platform coverage, plus an effort/instantness/repo-fit comparison table and a prioritized recommendation (terminal one-shot -> AI skill/MCP -> xbar menu bar -> Scriptable iOS widget; native mobile apps and smart speaker deferred). No implementations included — deferred to the TASK-13 view pipeline.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Explored and documented five option families for checking the family dashboard from anywhere in backlog doc-4: mobile home-screen widgets (native vs Scriptable/KWGT), desktop widgets/menu-bar/tray apps (xbar/SwiftBar, Rainmeter, GNOME/KDE), terminal/CLI one-shot check (extends existing terminal_dashboard.py), AI skill/MCP server, and smart-speaker voice integration. Each option assesses data source (all read the published dashboard-v2.json on R2 — plain JSON over HTTPS, no new backend needed), build effort, instantness, platform coverage, and repo fit, with a comparison table and a prioritized recommendation: (1) terminal one-shot mode, (2) AI skill/MCP, (3) macOS xbar menu-bar plugin, (4) Scriptable iOS widget; native mobile apps and smart-speaker skill deferred. Verified by viewing the created doc (backlog doc view doc-4 --plain) and checking each acceptance criterion against its content. Implementations intentionally out of scope per AC #3 — they flow through the TASK-13 view pipeline.
<!-- SECTION:FINAL_SUMMARY:END -->
