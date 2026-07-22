# trmnl-home

Custom family dashboard for **TRMNL OG** and **TRMNL X** e-ink devices, rendered by a TRMNL private plugin.

Fetches weather, Google Calendar events, TickTick tasks, and upcoming anniversaries into a single JSON file (`dashboard-v2.json`). A [TRMNL](https://usetrmnl.com) private plugin polls that JSON on its own schedule and renders it into the actual device image using the Liquid templates in this repo — this project never renders a PNG itself. Three operational modes are supported for producing and publishing the JSON:

1. **GitHub Actions** — manually triggered workflow (no schedule); collects data and publishes `dashboard-v2.json` to Cloudflare R2.
2. **Local workflow loop** — runs the same collect → publish cycle on your own machine on a configurable interval.
3. **Long-running server** — always-on service with an HTTP endpoint for local preview/debugging (not what the TRMNL device polls — see [TRMNL setup](plan/TRMNL_SETUP.md)).

A separate **terminal dashboard** reads the same JSON data and renders a live text UI that auto-refreshes.

## What it shows

- Current date, city, and weather (temperature, feels-like, description, icon)
- Upcoming calendar events from Google Calendar
- Tasks from a shared TickTick list
- Upcoming birthdays and anniversaries detected from Google Calendar events

## Supported devices

| Device | Resolution | Liquid template |
|--------|------------|------------------|
| TRMNL OG | 800 × 480 px | `templates/devices/og.liquid` |
| TRMNL X | 1872 × 1404 px | `templates/devices/x.liquid` |

Both templates render in grayscale to match their e-ink panels — see `plan/DESIGN_REFERENCE.md` for the original visual design this was matched against, and `templates/CONTRACT.md` for the JSON→Liquid variable contract shared partials expect.

## Quick start

```bash
# Activate the virtual environment
source .venv/Scripts/activate   # Windows (Git Bash)
source .venv/bin/activate        # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Copy the template and fill in your credentials
cp .env.example .env

# Step 1: collect data → output/dashboard-v2.json
python collect_unified_data.py --output output/dashboard-v2.json

# Step 2: render a local static preview (no TRMNL account needed)
python export_preview.py --input output/dashboard-v2.json
```

Open the generated `preview.html` in a browser to see both device layouts side by side. When API credentials are missing or a fetch fails, the dashboard renders an explicit error state (`(!) Not loaded`) in the affected section rather than silently showing fake data. To preview the layout without any credentials, use the bundled dummy fixture:

```bash
python export_preview.py --input templates/dummy_dashboard.json
```

To see it rendered on a real device, follow **[plan/TRMNL_SETUP.md](plan/TRMNL_SETUP.md)** — a from-scratch guide to creating a TRMNL account, a private plugin, and pointing it at your own published `dashboard-v2.json`.

## Configuration

Create a `.env` file in the project root (see `.env.example` for all options).

| Variable | Purpose | Default |
|----------|---------|---------|
| `WEATHER_LATITUDE`, `WEATHER_LONGITUDE` | Weather location | Amsterdam |
| `CITY` | City label on the dashboard | Amsterdam |
| `TIMEZONE` | Local timezone for event times (e.g. `Europe/Amsterdam`) | `Europe/Amsterdam` |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Path to JSON key file or raw JSON for service account | — |
| `GOOGLE_CALENDAR_IDS` | Comma-separated Google Calendar IDs | — |
| `CALENDAR_ATTENDEE_EMAILS` | Only show events with these attendees (comma-separated) | — |
| `CALENDAR_MAIN_CALENDAR_ID` | Always show events from this calendar ID | — |
| `TICKTICK_ACCESS_TOKEN`, `TICKTICK_LIST_ID` | TickTick Developer API credentials | — |
| `TERMINAL_CALENDAR_IDS` | Calendar IDs for the terminal dashboard (falls back to `GOOGLE_CALENDAR_IDS`) | — |
| `TERMINAL_TICKTICK_LIST_IDS` | TickTick list IDs for the terminal dashboard | — |
| `OG_GRAYSCALE_LEVELS` | OG device grayscale level count for the local preview's CSS approximation (`2` = hard 1-bit, `4` = softer) | `4` |
| `DASHBOARD_JSON_URL` | URL or path to the unified JSON (used by `terminal_dashboard.py`) | auto |
| `CLOUDFLARE_R2_PUBLIC_URL` | Public base URL for the R2 bucket | — |
| `REFRESH_INTERVAL_SECONDS` | Seconds between refreshes in server/loop mode | `60` |
| `SERVER_PORT` | HTTP port in server mode | `8080` |
| `REFERENCE_DATE` | Treat this date as today (`DD-MM-YYYY`), useful for testing | today |

## Usage

### Collect data

`collect_unified_data.py` fetches all sources once and writes a single JSON file. All other scripts read from this file rather than calling APIs directly.

```bash
# Write to output/dashboard-v2.json (default)
python collect_unified_data.py --output output/dashboard-v2.json

# Pretend today is a different date
python collect_unified_data.py --date 23-12-2026 --output output/dashboard-v2.json
```

### Local preview

`export_preview.py` renders every configured device's Liquid template (`templates/devices/`) against a JSON file into one static `preview.html`, with a JS tab toggle to switch between devices and a CSS filter approximating each device's grayscale level count.

```bash
python export_preview.py                                   # dummy fixture -> preview.html
python export_preview.py --input output/dashboard-v2.json  # real collected data
python export_preview.py --output /tmp/preview.html        # custom output path
```

### Terminal dashboard

`terminal_dashboard.py` renders an interactive terminal UI that auto-refreshes every `TERMINAL_REFRESH_INTERVAL_SECONDS` (default 60 s). It reads from `DASHBOARD_JSON_URL` (the Cloudflare URL) or a local file.

```bash
python terminal_dashboard.py
python terminal_dashboard.py --input output/dashboard-v2.json  # local file
python terminal_dashboard.py --env /path/to/.env.other
```

Controls: `Tab` — switch calendar/task-list pair · `q` — quit

### Local workflow loop

`run_workflow_loop.py` runs the full collect → preview → [upload] cycle on your machine, sleeping between iterations. Useful for a home server or developer machine where you want fresh JSON without GitHub Actions.

```bash
python run_workflow_loop.py                     # both devices, every 60 s; uploads if R2 creds present
python run_workflow_loop.py --once              # single run and exit
python run_workflow_loop.py --device og         # OG only
python run_workflow_loop.py --interval 300      # every 5 minutes
python run_workflow_loop.py --no-upload         # disable R2 upload even when creds are present
python run_workflow_loop.py --env /path/.env    # custom env file
```

Errors in one iteration are logged to stderr and the loop continues on the next tick.

### Long-running server

`server.py` is the always-on variant. It runs the same collect → preview → [upload] loop in a background thread and serves `dashboard-v2.json`/`preview.html` over HTTP on port `SERVER_PORT` (default 8080) for local preview/debugging. **This is not what a real TRMNL device polls** — TRMNL polls your published Cloudflare R2 URL directly via its own private plugin (see [plan/TRMNL_SETUP.md](plan/TRMNL_SETUP.md)).

```bash
# Headless: HTTP on port 8080, refresh every 10 min; uploads to R2 if creds present
python server.py

# Custom port and interval
python server.py --port 9000 --interval 300

# Without HTTP (refresh loop only)
python server.py --no-http

# Disable R2 upload even when creds are present
python server.py --no-upload
```

Runs headless by default, logging each refresh to stderr. If stdin is an interactive
terminal, press `t` at any time to open the Rich terminal UI, and `q` inside it to
return to headless logging (`q` from headless quits the server; `Ctrl+C` always quits).

The HTTP server serves only two paths:

| Path | Content |
|------|---------|
| `/preview.html` | Static Liquid-rendered preview of both devices |
| `/dashboard-v2.json` | Latest unified data |

## Setting up the TRMNL private plugin

See **[plan/TRMNL_SETUP.md](plan/TRMNL_SETUP.md)** for the full walkthrough, written for a stranger cloning this repo: creating a TRMNL account, creating a private plugin, choosing the **Polling** strategy against your published `dashboard-v2.json` URL, and pasting in `templates/devices/og.liquid` / `x.liquid`.

## Running as a service

### Linux (systemd)

Create `/etc/systemd/system/trmnl-home.service`:

```ini
[Unit]
Description=TRMNL Home Dashboard Server
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=<your-user>
WorkingDirectory=/path/to/trmnl-home
ExecStart=/path/to/trmnl-home/.venv/bin/python server.py --upload
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now trmnl-home
sudo journalctl -u trmnl-home -f   # follow logs
```

### macOS (launchd)

Create `~/Library/LaunchAgents/com.trmnl-home.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>             <string>com.trmnl-home</string>
  <key>ProgramArguments</key>
  <array>
    <string>/path/to/trmnl-home/.venv/bin/python</string>
    <string>/path/to/trmnl-home/server.py</string>
    <string>--upload</string>
  </array>
  <key>WorkingDirectory</key>  <string>/path/to/trmnl-home</string>
  <key>RunAtLoad</key>         <true/>
  <key>KeepAlive</key>         <true/>
  <key>StandardErrorPath</key> <string>/tmp/trmnl-home.log</string>
</dict>
</plist>
```

```bash
launchctl load ~/Library/LaunchAgents/com.trmnl-home.plist
```

### Windows (Task Scheduler)

For a one-shot approach (no persistent process), schedule `run_workflow_loop.py --once` via Task Scheduler every minute:

1. Open Task Scheduler → Create Basic Task.
2. Trigger: **Daily**, repeat every **1 minute** indefinitely.
3. Action: `C:\path\to\.venv\Scripts\python.exe`  
   Arguments: `C:\path\to\trmnl-home\run_workflow_loop.py --once --upload`  
   Start in: `C:\path\to\trmnl-home`

Or run `server.py` directly (it loops in-process):

```powershell
# Run at startup via a scheduled task
Start-Process python -ArgumentList "server.py","--upload" `
  -WorkingDirectory "C:\path\to\trmnl-home" -WindowStyle Hidden
```

## Automation via GitHub Actions

`.github/workflows/generate-dashboard.yml` runs on manual dispatch only (no schedule is configured), collects data, renders `preview.html`, uploads `dashboard-v2.json` to Cloudflare R2, and stores `preview.html` as a workflow artifact. Trigger it from the repo's **Actions** tab ("Run workflow"), or re-add a `schedule:` block to the workflow file if you want it running automatically again.

Required GitHub repository secrets:

| Secret | Description |
|--------|-------------|
| `CLOUDFLARE_R2_ENDPOINT` | `https://<account_id>.r2.cloudflarestorage.com` |
| `CLOUDFLARE_R2_ACCESS_KEY_ID` | R2 API token access key ID |
| `CLOUDFLARE_R2_SECRET_ACCESS_KEY` | R2 API token secret access key |
| `CLOUDFLARE_R2_BUCKET_NAME` | Bucket name |
| `CLOUDFLARE_R2_PUBLIC_URL` | Public base URL (custom domain or r2.dev) |

TRMNL's private plugin polls the stable public URL:

```
<CLOUDFLARE_R2_PUBLIC_URL>/dashboard-v2.json
```

## Testing

```bash
pytest
pytest --date 23-12-2026   # run as if today were a different date
```

## Project structure

| Path | Role |
|------|------|
| `collect_unified_data.py` | CLI: collect all data → `dashboard-v2.json` |
| `export_preview.py` | CLI: render all device Liquid templates → `preview.html` |
| `run_workflow_loop.py` | CLI: collect → preview → [upload] loop |
| `server.py` | CLI: long-running server (headless or terminal UI) |
| `terminal_dashboard.py` | CLI: interactive terminal dashboard |
| `src/pipeline.py` | Shared collect → preview → [upload] cycle |
| `src/unified_fetcher.py` | Fetches all sources once, returns `UnifiedData` |
| `src/json_loader.py` | Loads and parses `dashboard-v2.json` |
| `src/liquid_render.py` | Renders a device's Liquid template against `dashboard-v2.json` data |
| `src/config.py` | All environment-based configuration |
| `src/data.py` | Core dataclasses and dummy data |
| `templates/` | Liquid partials and device templates rendered locally and by TRMNL |
| `.github/workflows/generate-dashboard.yml` | Scheduled GitHub Actions workflow |
| `plan/TRMNL_SETUP.md` | TRMNL account/private-plugin setup guide |

## License

MIT
