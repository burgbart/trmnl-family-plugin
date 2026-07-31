---
id: TASK-12
title: Explore ways to check the family dashboard anywhere
status: To Do
assignee: []
created_date: '2026-07-31 10:06'
updated_date: '2026-07-31 11:33'
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
- [ ] #1 Document (backlog doc) lists the explored options: mobile widgets, desktop widgets/apps, terminal/CLI check, AI skill or MCP, smart-speaker integration
- [ ] #2 Each option notes what data source it would consume and show (e.g. published dashboard-v2.json), platform coverage.
- [ ] #3 Implementation tasks are not included, they will be picked up in task 13
<!-- AC:END -->
