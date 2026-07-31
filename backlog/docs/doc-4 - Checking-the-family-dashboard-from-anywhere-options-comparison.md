---
id: doc-4
title: 'Checking the family dashboard from anywhere: options comparison'
type: guide
created_date: '2026-07-31 16:56'
updated_date: '2026-07-31 16:57'
---
# Checking the family dashboard from anywhere: options comparison

Exploration for TASK-12. The TRMNL device covers the at-home glance; this document compares ways to check the same family dashboard state (calendar, tasks, weather, anniversaries) from anywhere else. Outcome: a recommendation of which options to pursue. Implementations are intentionally out of scope here — they go through the view pipeline designed in TASK-13.

## Shared data source

Every option below reads the same artifact this repo already publishes:

- **`dashboard-v2.json` on Cloudflare R2** — a single JSON object, overwritten each pipeline run, served over plain HTTPS with no auth from `CLOUDFLARE_R2_PUBLIC_URL`. Built by `src/serialization.build_dashboard_payload()`, it is the single source of truth for both the Liquid templates and the terminal dashboard, and includes explicit per-source `errors` entries when a source fails.
- Local alternatives for development: `output/dashboard-v2.json`, or the `server.py` HTTP endpoint on the LAN.

Because the payload is plain JSON over HTTPS, every option is a read-only HTTP consumer — no new backend work is required for any of them. Any non-TRMNL visual surface should also apply the design system in `design/` (tokens + style guide, per AGENTS.md).

## Option 1: Mobile home-screen widgets (Android, iOS)

- **Data source:** `dashboard-v2.json` from the R2 URL, polled by the widget.
- **How it would work:**
  - *Android:* a native App Widget (Glance/RemoteViews) requires an Android app shell in Kotlin — a new codebase, a new build/distribution chain. Low-friction alternative: an existing scriptable widget app (e.g. KWGT or similar) that fetches JSON and renders it.
  - *iOS:* WidgetKit requires a Swift app distributed via the App Store (or ad-hoc for personal devices). Low-friction alternative: a Scriptable widget — a small JavaScript file that fetches the JSON and renders a widget, personal-use only.
- **Effort:** native = high (new platform codebases); Scriptable/KWGT = low.
- **Instantness:** very high — glanceable on the home screen, no app to open. Caveat: the OS controls widget refresh cadence (typically 15–30 min minimum), so "instant" refers to visibility, not freshness. The JSON updates roughly every minute, but the widget won't.
- **Platform coverage:** one option per platform; no shared code between Android and iOS.
- **Fit:** native apps belong in separate repos; a Scriptable script or KWGT preset is a small artifact that could live here (e.g. `widgets/`).

## Option 2: Desktop widgets / menu-bar / tray apps (macOS, Windows, Linux)

- **Data source:** `dashboard-v2.json` from the R2 URL (or the LAN `server.py` endpoint at home).
- **How it would work:**
  - *macOS:* a SwiftBar/xbar plugin — a single script (Python or shell) that fetches the JSON and prints menu-bar text + a dropdown with events/tasks. Very small. Übersicht desktop widgets are another option.
  - *Windows:* a Rainmeter skin, or a small tray app (e.g. Python + pystray). Medium effort.
  - *Linux:* a GNOME Shell / KDE applet, or a polybar/waybar module that runs the same fetch-and-print script. Low-medium effort.
- **Effort:** low for xbar/SwiftBar and bar modules (a script); medium for Windows tray/Rainmeter.
- **Instantness:** high — always visible in the menu bar / panel; poll interval is fully under our control.
- **Platform coverage:** one small integration per desktop platform, but the fetch/parse logic is shared and trivial.
- **Fit:** an xbar/SwiftBar plugin is a single script and fits this repo fine (e.g. `plugins/xbar/`). Windows/Linux variants can follow the same pattern.

## Option 3: Terminal / CLI check

- **Data source:** `dashboard-v2.json` from the R2 URL, a local path, or the `server.py` endpoint — `src/json_loader.resolve_input_path()` already implements exactly this fallback chain.
- **How it would work:** the interactive terminal dashboard (`terminal_dashboard.py`, Rich UI with tab switching) already exists. What's missing for a quick "check from anywhere" is a one-shot, non-interactive mode that prints the current state and exits — usable over SSH, in a tmux pane, or piped into other tools.
- **Effort:** very low — the data loading and rendering exist; add a one-shot flag/output path.
- **Instantness:** medium — you must open a terminal and run it, but output is immediate and as fresh as the JSON.
- **Platform coverage:** anywhere Python runs; ideal for SSH into home from elsewhere.
- **Fit:** squarely in this repo — it extends an existing consumer.

## Option 4: AI skill / MCP server

- **Data source:** `dashboard-v2.json` from the R2 URL.
- **How it would work:**
  - *MCP server:* a small read-only server (e.g. Python + FastMCP) exposing tools like `get_dashboard` / `get_next_events` that fetch and summarize the JSON. Any MCP-capable assistant can then answer "what's next for the family?".
  - *Agent skill:* even lighter — a skill document telling the assistant to fetch the JSON URL and interpret it. Near-zero code.
- **Effort:** low for both; the skill variant is the cheapest option in this whole comparison.
- **Instantness:** medium — requires asking the assistant, but the answer is conversational and can combine/summarize freely ("anything this weekend?").
- **Platform coverage:** any device where you already talk to an assistant — effectively the widest coverage of all options with no per-platform code.
- **Fit:** a small MCP server or skill fits this repo (it consumes the same JSON contract); could also live in the user's `~/ai-agents` setup as a skill.

## Option 5: Smart-speaker integration (voice routine)

- **Data source:** `dashboard-v2.json` from the R2 URL, likely fronted by a tiny voice-friendly endpoint (e.g. a Cloudflare Worker in front of R2 that returns a short spoken-summary text).
- **How it would work:** an Alexa Skill or Google Action that, on a routine phrase ("what's happening today"), calls the endpoint and reads the summary aloud.
- **Effort:** medium-high — a published/registered skill, an HTTPS endpoint, account linking or at least a private skill setup, plus a summary endpoint tuned for speech.
- **Instantness:** high in the kitchen/living room context — hands-free, zero screen.
- **Platform coverage:** whichever speaker ecosystem(s) the household owns; each needs its own skill/action.
- **Fit:** the skill/action itself belongs outside this repo; the spoken-summary endpoint could be a small addition here or a standalone Cloudflare Worker.

## Comparison summary

| Option | Effort | Instantness | Platform coverage | Fits this repo |
|---|---|---|---|---|
| Mobile widget — native | High | Very high (glanceable; OS-limited refresh) | Android or iOS, separate codebases | No — separate repo |
| Mobile widget — Scriptable/KWGT | Low | Very high (same caveat) | One platform per artifact | Yes, as small artifacts |
| Desktop — xbar/SwiftBar (macOS) | Low | High (always visible, own poll interval) | macOS | Yes |
| Desktop — Rainmeter / tray (Win), applet (Linux) | Medium | High | Windows / Linux | Yes, same pattern |
| Terminal one-shot CLI | Very low | Medium (must run it) | Anywhere Python/SSH runs | Yes — extends existing code |
| AI skill / MCP server | Very low – low | Medium (must ask) | Any assistant-capable device | Yes |
| Smart speaker | Medium-high | High (hands-free) | One skill per speaker ecosystem | Partly (endpoint here, skill elsewhere) |

## Recommendation

Pursue, in this order:

1. **Terminal one-shot mode** — cheapest option (the loader and renderer exist), immediately useful over SSH.
2. **AI skill / MCP server** — near-zero to low effort, widest effective coverage (any device with an assistant), conversational answers.
3. **macOS menu-bar plugin (xbar/SwiftBar)** — low effort, always-visible desktop glance.
4. **Scriptable (iOS) widget** — low-effort mobile presence without an App Store project.

Defer:

- **Native mobile widgets/apps** — high cost (new platform codebases, distribution) for a personal dashboard; revisit only if the Scriptable/KWGT route proves limiting.
- **Smart-speaker skill** — real setup and maintenance overhead (registered skill, endpoint, per-ecosystem work); revisit once one of the cheap options is in daily use and the spoken-summary use case is still wanted.

Windows/Linux desktop variants were not recommended only because the primary household desktop is macOS; the xbar pattern transfers directly if that changes.
