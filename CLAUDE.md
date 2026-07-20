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
python collect_unified_data.py --output output/dashboard.json
python run_local.py                    # reads dashboard.json; generates both devices
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

1. `collect_unified_data.py` → `src/unified_fetcher.py` hits external APIs once per source, writes `dashboard.json`, and uploads it to Cloudflare R2.
2. `run_local.py` and `terminal_dashboard.py` read `dashboard.json` via `src/json_loader.py` — they never call external APIs directly.

`src/config.py` is imported at module level by most files; scripts that accept `--env` must call `load_dotenv(override=True)` before importing any project module. The `--date DD-MM-YYYY` flag on any entry point calls `set_reference_date()` to override "today" throughout the codebase.

See **AGENTS.md** for full details on every module, the fetcher dummy-data pattern, multi-device rendering, and CI/deployment.
