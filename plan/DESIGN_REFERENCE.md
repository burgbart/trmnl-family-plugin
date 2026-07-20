# Dashboard Design Reference

## Purpose
This document captures the current visual design of the PNG dashboard output (`output/dashboard.png` / `output/dashboard_x.png`) as rendered by `src/dashboard.py`. It serves as a visual specification for future Liquid/CSS template implementations to maintain pixel-accurate parity with the existing Pillow-rendered output.

---

## Device Profiles

### TRMNL OG
- **Dimensions**: 800 × 480 pixels
- **Color Mode**: 8-bit Grayscale ("L")
- **Supported Grayscale Levels**: 4-level (rendered as 8-bit)

### TRMNL X
- **Dimensions**: 1872 × 1404 pixels
- **Color Mode**: 8-bit Grayscale ("L")
- **Supported Grayscale Levels**: 16-level (rendered as 8-bit)

---

## Grayscale Palette

All colors are single-channel grayscale values (0–255):

| Name | Value | Hex | Usage |
|------|-------|-----|-------|
| BLACK | 0 | #000000 | Text, borders, icons, lines |
| DARK_GRAY | 85 | #555555 | Section box outlines |
| LIGHT_GRAY | 170 | #AAAAAA | Page background |
| WHITE | 255 | #FFFFFF | Section backgrounds |

---

## Typography

### Fonts
All fonts are TRMNL typeface (official TRMNL family, free for commercial use):
- **TRMNL16-Bold.ttf** – Bold body text
- **TRMNL16-Regular.ttf** – Regular body text
- **TRMNL21-Bold.ttf** – Large headings (day name in header)

Font loading is case-sensitive and path-based; fallback to system default if font file not found.

### Font Sizes and Usage

#### TRMNL OG Profile
| Size | Name | Usage |
|------|------|-------|
| 28px | Title | Day name (e.g., "Monday") in header |
| 34px | Large | Temperature value (e.g., "22°C") |
| 18px | Medium | Section titles ("Upcoming", "Tasks", "Anniversaries") |
| 16px | Small | Event/task/birthday details |
| 13px | Tiny | "Feels like" text, descriptions, sync timestamp |

#### TRMNL X Profile
All sizes are scaled proportionally:
| Size | Name | Usage |
|------|------|-------|
| 64px | Title | Day name in header |
| 72px | Large | Temperature value |
| 36px | Medium | Section titles |
| 30px | Small | Event/task/birthday details |
| 24px | Tiny | Secondary text, timestamps |

---

## Layout Regions

### Overall Structure
- **Page Background**: LIGHT_GRAY (fills entire 800×480 or 1872×1404)
- **Sections**: WHITE rectangles with DARK_GRAY borders, arranged as follows:

#### TRMNL OG (800×480)

**1. Header**
- **Position**: (10, 10) to (790, 100)
- **Height**: 90px
- **Contents**:
  - **Left side**: Day name + date (e.g., "Monday\n20 July"), centered vertically
  - **Right side**: Weather icon + temperature + "Feels like" + description
  - Background: WHITE
  - Border: DARK_GRAY, 2px width
  - Padding: 10px

**2. Calendar/Upcoming**
- **Position**: (10, 110) to (490, 470)
- **Width**: 60% of total width (480px)
- **Height**: ~360px
- **Contents**:
  - Section title: "Upcoming" (bold, 18px)
  - Event rows (up to 6 events)
  - Each row: time/date + event title (truncated to fit)
  - Row height: ~45px (variable, ~1.6× line_height + 4px)
  - Bottom-right corner: "Synced HH:MM DD/MM" timestamp (tiny font)
  - Background: WHITE
  - Border: DARK_GRAY, 2px width
  - Padding: 10px

**3. Tasks**
- **Position**: (500, 110) to (790, 300)
- **Width**: 40% of total width (290px)
- **Height**: ~190px (62% of total height)
- **Contents**:
  - Section title: "Tasks" (bold) + optional " - X due (!)" suffix
  - Task rows (up to 6 tasks)
  - Each row: checkbox (12×12px) + task title (truncated) + optional " (!)" if due
  - Row height: 28px (line_height)
  - Background: WHITE
  - Border: DARK_GRAY, 2px width
  - Padding: 10px

**4. Anniversaries/Birthdays**
- **Position**: (500, 310) to (790, 470)
- **Width**: 40% of total width (290px)
- **Height**: ~160px (remaining space)
- **Contents**:
  - Section title: "Anniversaries" (bold, 18px)
  - Birthday rows (up to 4 birthdays)
  - Each row: name (truncated) + date (e.g., "Mon 20 Jul (in 5d)")
  - Row height: 28px (line_height)
  - Background: WHITE
  - Border: DARK_GRAY, 2px width
  - Padding: 10px

#### TRMNL X (1872×1404)

**Proportions scale approximately 2.3×:**
- **Header**: Height 180px (padding 24px)
- **Calendar**: Width 58% (~1085px)
- **Tasks**: Height 62% of viewport (from 190px to ~845px)
- **Birthdays**: Remaining space (~560px)
- **Line height**: 44px
- **Checkbox**: 26×26px

---

## Spacing & Padding

### TRMNL OG Profile
| Dimension | Value | Notes |
|-----------|-------|-------|
| Padding | 10px | Applied to sections and internal spacing |
| Line height | 28px | Space between rows (calendar, tasks, birthdays) |
| Checkbox size | 12px | Square checkbox for tasks |
| Border width | 2px | Section box outlines |
| Section margin | 10px | Gap between header and sections, sections and edges |

### TRMNL X Profile
| Dimension | Value | Notes |
|-----------|-------|-------|
| Padding | 24px | Proportionally larger internal spacing |
| Line height | 44px | Taller row spacing for readability at scale |
| Checkbox size | 26px | Larger checkbox for TRMNL X |
| Border width | 2px | Same border weight (stays readable) |

---

## Content Rendering Rules

### Text Truncation
- Event/task/birthday text that exceeds available width is truncated with "…" suffix
- Truncation respects margins and doesn't overflow box boundaries

### Weather Icons
Simple monochrome line-drawn icons (2px line width, BLACK lines):
- **Sun**: Circle with 8 radial rays
- **Cloud**: Three overlapping ellipses forming a cloud shape
- **Rain**: Cloud + 3 vertical rain drop lines below
- **Partly Cloudy**: Small sun overlapped by smaller cloud

Icon size: 40px diameter (OG), scaled proportionally on TRMNL X.

### Checkboxes (Tasks)
- **Empty**: DARK_GRAY outline rectangle, no fill
- **Checked**: DARK_GRAY outline rectangle with diagonal check mark (line-drawn, 2px width)
- **Size**: 12px × 12px (OG), 26px × 26px (TRMNL X)

### Event/Task/Birthday Formatting
- **Events**: "Time/Date EventTitle"
  - Example: "Today 14:30 Team Meeting"
  - All-day events: "Today · All day" or "Mon 20 Jul – Wed 22 Jul"
- **Tasks**: "[checkbox] Task Title [(!) if due]"
  - Example: "☑ Buy groceries (!)"
- **Birthdays**: "Name Date (countdown)"
  - Example: "Alice Mon 20 Jul (in 5d)"

---

## Color & Contrast

- **Text**: All text is BLACK (0) on WHITE backgrounds for maximum contrast
- **Borders**: DARK_GRAY (85) provides visual separation without overwhelming
- **Page background**: LIGHT_GRAY (170) creates a neutral backdrop for section containers
- **No fill colors used** inside content (only WHITE/BLACK for functional elements like sun/cloud)

---

## Section Order (Rendering Sequence)

1. **Header** (full width, top) – day, date, weather
2. **Calendar** (left, below header) – upcoming events
3. **Tasks** (top-right, aligned with calendar top) – task list with checkboxes
4. **Anniversaries** (bottom-right, below tasks) – birthday list

This stacked arrangement maximizes information density: calendar dominates left side, right side splits actionable items (tasks) above upcoming dates (birthdays).

---

## Key Implementation Notes

1. **Grayscale Rendering**: Use HTML/CSS grayscale mode or pre-convert colors to L-channel equivalent (e.g., use `filter: grayscale(100%)` or render all colors as `rgb(X, X, X)` where X is the grayscale value).

2. **Font Fallback**: If TRMNL fonts unavailable, system sans-serif fonts are acceptable but will not match the original bitmap-safe rendering.

3. **Border Styling**: All section borders are 2px DARK_GRAY, consistent across both profiles. No rounded corners.

4. **Responsive Scaling**: TRMNL X dimensions are not a simple 2× scale—proportions differ subtly (e.g., `calendar_width_ratio` is 58% vs 60% on OG, `tasks_height_ratio` is constant 62%). Template implementations must respect these ratios.

5. **Truncation Algorithm**: Text is truncated character-by-character from the right, appending "…" only when it exceeds max_width (measured with actual font metrics).

6. **Empty Content**: If no events/tasks/birthdays, sections still render with title and empty list area (no collapse).

---

## References

- **Source Code**: `src/dashboard.py` (Pillow rendering logic)
- **Configuration**: `src/config.py` (device profiles, colors, fonts)
- **Font Files**: `assets/TRMNL*.ttf`
- **Example Output**: `output/dashboard.png` (OG), `output/dashboard_x.png` (X profile)
