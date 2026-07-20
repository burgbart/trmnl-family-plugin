# Liquid template variable contract

This document defines the exact variable names the shared partials in
`templates/partials/` expect, and how a parent device template (`og.liquid` /
`x.liquid`, built in tasks 1.2/1.3 — not part of this doc) is expected to
supply them. It reuses the `dashboard.json` schema verbatim (see
`src/serialization.py::build_dashboard_payload()` / `src/data.py`) — no field
was renamed or restructured.

## Top-level render context

For local rendering, the parsed `dashboard.json` dict is passed as the
top-level Liquid render context, so a device template can reference:

```
meta.generated_at        ISO datetime string
meta.reference_date      ISO date string "YYYY-MM-DD"
meta.city                str
weather.description      str
weather.temperature      int
weather.feels_like       int
weather.icon             "sun" | "cloud" | "rain" | "partly-cloudy"
events[n].title           str
events[n].start           ISO datetime string
events[n].end             ISO datetime string | null
events[n].all_day         bool
events[n].attendees       array of str
events[n].calendar_id     str | null
tasks[n].title            str
tasks[n].done             bool
tasks[n].priority         int
tasks[n].due_date         ISO date string "YYYY-MM-DD" | null
tasks[n].sort_order       int
birthdays[n].name         str
birthdays[n].date         ISO date string "YYYY-MM-DD"
birthdays[n].kind         "birthday" | "anniversary"
calendars, task_lists      (not consumed by any partial)
```

All dates/datetimes arrive as **ISO strings**, not Liquid `date` objects —
that's what `json.loads()` produces, and it's also what python-liquid's
`date` filter accepts directly (it parses common string formats, including
ISO 8601, before formatting). No template-side parsing step is needed.

## Partial responsibilities vs. parent responsibilities

Each partial renders **only its inner content** (section title + rows) with
inline CSS for typography/spacing. It does **not** render the outer
DARK_GRAY-bordered/WHITE-background section box, absolute positioning, or
overall page width/height — those differ enough between OG (800×480,
absolute pixel layout) and X (1872×1404) that they belong in the device
template, which wraps each partial's `{% render %}` call in its own
positioned/bordered container div. This keeps the partials device-agnostic:
a device template supplies sizing/position via its own wrapper markup, and
font/spacing *values* (not layout) via explicit parameters.

## Partial parameters

python-liquid's `{% render %}` tag runs in an **isolated scope** — the parent
template's variables are not automatically visible to the partial (unlike
`{% include %}`, which shares scope but is deprecated in favor of `render`
in modern Liquid). Every variable each partial touches must be passed
explicitly as a `render` parameter. Syntax:

```liquid
{% render 'partials/weather', weather: weather, font_size_large: 34,
   font_size_tiny: 13, icon_size: 40, padding: 10 %}
```

(Filenames passed to `render`/`include` need the `.liquid` extension unless
the `Environment`'s `FileSystemLoader` is constructed with `ext=".liquid"`,
in which case the bare name — `partials/weather` — resolves correctly. Use
whichever convention `src/liquid_render.py` (task 2.1) adopts; document it
there.)

### `partials/weather.liquid`

| Variable | Source | Notes |
|---|---|---|
| `weather` | `weather` (whole object) | icon/description/temp/feels-like |
| `font_size_large` | `DeviceProfile.font_size_large` | temperature figure |
| `font_size_tiny` | `DeviceProfile.font_size_tiny` | feels-like + description |
| `icon_size` | device template's choice (not a `DeviceProfile` field) | icon square px |
| `padding` | `DeviceProfile.padding` | gap between icon and text, block padding |

### `partials/calendar.liquid`

| Variable | Source | Notes |
|---|---|---|
| `events` | `events` (array) | pre-sorted/pre-filtered by the caller |
| `today` | `meta.reference_date` | ISO date string, used to detect "Today" |
| `max_events` | `DeviceProfile.max_events` | row cutoff (`limit:` in the `for` loop) |
| `font_size_medium` | `DeviceProfile.font_size_medium` | section title |
| `font_size_small` | `DeviceProfile.font_size_small` | row text |
| `line_height` | `DeviceProfile.line_height` | row height |
| `padding` | `DeviceProfile.padding` | internal padding |
| `title` | optional, default `"Upcoming"` | override if ever needed |

### `partials/tasks.liquid`

| Variable | Source | Notes |
|---|---|---|
| `tasks` | `tasks` (array) | pre-sorted by the caller |
| `today` | `meta.reference_date` | ISO date string; `due_date <= today` (plain string compare, since ISO dates sort lexically) mirrors `src/dashboard.py::_is_due` |
| `max_tasks` | `DeviceProfile.max_tasks` | row cutoff |
| `checkbox_size` | `DeviceProfile.checkbox_size` | checkbox square px |
| `font_size_medium` | `DeviceProfile.font_size_medium` | section title |
| `font_size_small` | `DeviceProfile.font_size_small` | row text |
| `line_height` | `DeviceProfile.line_height` | row height |
| `padding` | `DeviceProfile.padding` | internal padding |
| `title` | optional, default `"Tasks"` | override if ever needed |

The partial computes its own due-count for the `"Tasks - N due (!)"` title
suffix and its own per-row `(!)` marker — the caller doesn't need to
precompute either.

### `partials/birthdays.liquid`

| Variable | Source | Notes |
|---|---|---|
| `birthdays` | `birthdays` (array) | pre-sorted by the caller |
| `today` | `meta.reference_date` | ISO date string; shows "Today!" on match |
| `max_birthdays` | `DeviceProfile.max_birthdays` | row cutoff |
| `font_size_medium` | `DeviceProfile.font_size_medium` | section title |
| `font_size_small` | `DeviceProfile.font_size_small` | row text |
| `line_height` | `DeviceProfile.line_height` | row height |
| `padding` | `DeviceProfile.padding` | internal padding |
| `title` | optional, default `"Anniversaries"` | override if ever needed |

**Known gap vs. the PNG renderer**: `src/dashboard.py` shows a `(in Nd)`
countdown next to each birthday date (e.g. "Mon 20 Jul (in 5d)"). Stock
Liquid/python-liquid ships no day-count-between-two-dates filter, so this
partial renders the formatted date (`date: "%a %d %b"`) plus a `"Today!"`
special case instead of a countdown. If the countdown turns out to matter
visually, options for a later task: (a) precompute a `days_until` field
server-side in `build_dashboard_payload()` (schema change, out of scope
here), or (b) register a custom Liquid filter in `src/liquid_render.py`
(task 2.1) — python-liquid supports `Environment.add_filter()` for exactly
this.

## python-liquid quirks discovered while building this

- **`render` vs `include`**: use `{% render %}` for partials. It has
  isolated scope (must pass every variable explicitly, as shown above) and
  is the modern/recommended tag; `{% include %}` shares the caller's full
  scope implicitly, which would make partials silently depend on whatever
  variable names the parent happens to use — worth avoiding for a
  multi-device template set.
- **`FileSystemLoader(ext=".liquid")`**: without an explicit `ext=`, `render`
  requires the full filename with extension (`'partials/weather.liquid'`).
  With `ext=".liquid"` set on the loader, the bare name works
  (`'partials/weather'`). Pick one convention for task 2.1's
  `src/liquid_render.py` and keep partial-to-partial references consistent
  with it.
- **`date` filter accepts ISO strings directly** — `"2026-07-20" | date:
  "%a %d %b"` and `"2026-07-20T09:30:00+00:00" | date: "%H:%M"` both work
  with no separate parsing step, confirmed against python-liquid 2.3.0.
- **`for ... limit: N`** works as the cutoff mechanism for `max_events` /
  `max_tasks` / `max_birthdays` — no need for a separate `slice` filter.
- **String comparison for ISO dates**: since `due_date`/`reference_date` are
  ISO `YYYY-MM-DD` strings, `<=`/`==` comparisons in Liquid `if` tags sort
  correctly lexically — no date parsing needed for the "is due" / "is today"
  checks.
- **`{% for %} ... {% else %} ... {% endfor %}`** renders the `else` block
  when the collection is empty — used for the "No upcoming events" / "No
  tasks" / "No upcoming dates" empty states so sections still render with
  title + empty body, per DESIGN_REFERENCE.md's "Empty Content" rule.

## Sanity check performed

All four partials were rendered via a throwaway script
(`Environment(loader=FileSystemLoader(..., ext=".liquid"))`) against a
dummy payload shaped exactly like `build_dashboard_payload()`'s output
(mirroring `src/data.py`'s dummy generators), covering: timed events, an
all-day multi-day event, a due task, a completed task, and birthdays
including a long name needing truncation. All four rendered without errors;
output HTML was visually inspected for correct tag structure. The script was
not committed.
