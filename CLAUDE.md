# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

The authoritative project documentation for AI coding agents lives in **[AGENTS.md](AGENTS.md)**. Read it first — it covers the full project overview, module responsibilities, configuration, commands, testing instructions, code style guidelines, and deployment details.

## Quick reference

```bash
# Activate venv (Git Bash / POSIX)
source .venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Collect unified data and generate dashboard PNGs
python collect_unified_data.py --output output/dashboard-v2.json
python run_local.py                    # reads dashboard-v2.json; generates both devices
python run_local.py --device og --date 23-12-2026

# Interactive terminal dashboard
python terminal_dashboard.py

# Tests
pytest
pytest tests/test_render.py
pytest --date 23-12-2026
```

## Architecture summary

Data flows in two stages:

1. `collect_unified_data.py` → `src/unified_fetcher.py` hits external APIs once per source, writes `dashboard-v2.json`, and uploads it to Cloudflare R2.
2. `run_local.py` and `terminal_dashboard.py` read `dashboard-v2.json` via `src/json_loader.py` — they never call external APIs directly.

`src/config.py` is imported at module level by most files; scripts that accept `--env` must call `load_dotenv(override=True)` before importing any project module. The `--date DD-MM-YYYY` flag on any entry point calls `set_reference_date()` to override "today" throughout the codebase.

See **AGENTS.md** for full details on every module, the fetcher dummy-data pattern, multi-device rendering, and CI/deployment.

<!-- BACKLOG.MD GUIDELINES START -->
<!-- backlog.md-instructions-version: 1.48.0 -->
<CRITICAL_INSTRUCTION>

## Backlog.md Workflow

This project uses Backlog.md for task and project management.

**For every user request in this project, run `backlog instructions overview` before answering or taking action.**

Use the overview to decide whether to search, read, create, or update Backlog tasks.

Before task lifecycle actions, read the matching detailed guide:
- `backlog instructions task-creation` before creating or splitting tasks
- `backlog instructions task-execution` before planning, changing status or assignee, adding a plan or implementation notes, or implementing task work
- `backlog instructions task-finalization` before checking acceptance criteria, writing final summaries, or moving tasks to terminal statuses

Use `backlog <command> --help` before running unfamiliar commands. Help shows options, fields, and examples.

Do not edit Backlog task, draft, document, decision, or milestone markdown files directly. Use the `backlog` CLI so metadata, relationships, and history stay consistent.

</CRITICAL_INSTRUCTION>
<!-- BACKLOG.MD GUIDELINES END -->
