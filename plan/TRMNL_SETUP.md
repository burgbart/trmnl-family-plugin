# TRMNL setup guide

This guide walks you through pointing a real TRMNL device at your own copy of
this dashboard, from zero. It assumes you've already run
`collect_unified_data.py` locally (or via GitHub Actions) and have a
`dashboard.json` published somewhere with a stable public URL — for example
`https://<CLOUDFLARE_R2_PUBLIC_URL>/dashboard.json`. See the main
[README](../README.md) for how to get that URL.

## 1. Create a TRMNL account

1. Go to [usetrmnl.com](https://usetrmnl.com) and sign up (or log in if you
   already have an account tied to your physical device).
2. Pair your device if you haven't already — follow TRMNL's own onboarding
   flow for that; it's unrelated to this repo.

## 2. Create a private plugin

TRMNL's "Playlist" is the list of plugins your device cycles through.
A **private plugin** is a plugin only you can see/edit, backed by your own
data source and your own Liquid markup — exactly what this repo provides.

1. In the TRMNL dashboard, go to **Plugins → Private Plugin → Add New**.
2. Give it a name (e.g. "Family Dashboard").
3. For **Strategy**, choose **Polling**. This tells TRMNL to fetch your
   `dashboard.json` on its own schedule rather than you pushing data to it.
4. Set the **Polling URL** to your published JSON URL, e.g.:
   ```
   https://<CLOUDFLARE_R2_PUBLIC_URL>/dashboard.json
   ```
5. Set the **Polling Verb** to `GET` and leave headers/body empty unless your
   hosting requires auth headers.
6. Set a **Refresh Rate** — how often TRMNL re-fetches the JSON. This is
   independent of how often *you* regenerate `dashboard.json` (see
   `REFRESH_INTERVAL_SECONDS` / the GitHub Actions cron); pick something
   equal to or slightly longer than your generation interval so TRMNL isn't
   polling faster than the data actually changes.

## 3. Paste in the Liquid markup

TRMNL's plugin editor has a markup tab per device layout (it may show
separate tabs for different device resolutions, or one shared tab depending
on your TRMNL plan/UI version — check what's presented for your plugin).

1. Open `templates/devices/og.liquid` in this repo and copy its full
   contents into the markup editor for the **TRMNL OG** layout.
2. Open `templates/devices/x.liquid` and copy its full contents into the
   markup editor for the **TRMNL X** layout, if your plugin editor exposes a
   separate slot for it. If TRMNL only accepts one shared markup slot at your
   plan tier, use `og.liquid` (800×480) as the baseline and adjust — file a
   note back in `plan/PLAN.md`'s "Open items" section if this turns out to
   be the common case.
3. Save.

Note that `templates/partials/*.liquid` (weather, calendar, tasks, birthdays)
are `{% render %}`-ed *by* `og.liquid`/`x.liquid` in this repo's local
preview pipeline (`export_preview.py`). TRMNL's plugin editor may not support
multi-file Liquid includes for private plugins — if it doesn't, you'll need
to inline the partials' contents into the device template before pasting.
Confirm this against the real editor UI; update this section once verified
(see `plan/TASKS.md` task 4.3).

## 4. Verify the field names TRMNL exposes

TRMNL polling plugins typically expose the fetched JSON directly as Liquid
variables matching the JSON's top-level keys — so `dashboard.json`'s
`weather`, `events`, `tasks`, `birthdays`, `meta` keys should be usable the
same way they are in `templates/CONTRACT.md` (e.g. `weather.temperature`,
`events[0].title`). Some TRMNL plugin configurations instead require you to
explicitly map each field name in the plugin's settings UI rather than
exposing the whole payload — check what your plugin editor shows after your
first successful poll (TRMNL usually previews the fetched JSON structure
once it's polled successfully). Adjust `templates/` if the actual variable
names differ from the contract.

## 5. Add the plugin to your playlist

1. Go to **Playlist** and add your new private plugin.
2. Set how long it stays on-screen relative to any other plugins you run.
3. Force a refresh from the device (or wait for its normal refresh cycle) to
   see the rendered dashboard.

## Troubleshooting

- **Blank or error screen**: check the plugin's poll history/logs in the
  TRMNL dashboard — it usually shows the last fetched payload and any Liquid
  render errors.
- **Data looks stale**: confirm your `dashboard.json` is actually being
  regenerated (check `meta.generated_at`) and that TRMNL's refresh rate
  isn't longer than you expect.
- **Layout looks wrong for your device**: double check you pasted the OG
  markup into the OG slot and the X markup into the X slot — the two
  templates assume different canvas sizes (800×480 vs 1872×1404) and are not
  interchangeable.

## Status

This guide describes the expected flow based on TRMNL's documented Polling
strategy. It has **not yet been verified end-to-end against a real TRMNL
account** (see `plan/TASKS.md` task 4.3, `plan/PLAN.md` "Open items"). If you
follow this guide and hit a discrepancy — especially around partial
includes or field exposure — please update this file and
`templates/CONTRACT.md` to match reality.
