---
id: doc-2
title: 'Partly cloudy weather state: Open-Meteo vs Google/AccuWeather'
type: other
created_date: '2026-07-23 12:30'
updated_date: '2026-07-23 12:31'
---
# Partly cloudy weather state: Open-Meteo vs Google/AccuWeather

## Context

The TRMNL dashboard fetches weather from the free [Open-Meteo API](https://open-meteo.com/en/docs). A user observed that the dashboard shows mostly sunny, cloud, and rain icons, but rarely the **partly cloudy** state that Google Weather reports. This document investigates where the partly-cloudy state is lost between Open-Meteo and the rendered dashboard.

## Location and method

- Location: Amsterdam, Netherlands (default config: `WEATHER_LATITUDE=52.3676`, `WEATHER_LONGITUDE=4.9041`).
- Open-Meteo request: same parameters used by `src/weather.py`, plus `cloud_cover` (current) and `cloud_cover_mean` (daily) to see the underlying cloud fraction.
- Comparison source: [AccuWeather 10-day forecast for Amsterdam](https://www.accuweather.com/en/nl/amsterdam/249758/daily-weather-forecast/249758). AccuWeather is a reasonable proxy for the consumer-grade forecast Google Weather presents in its UI.

## Current dashboard behavior

Running `src.weather.fetch_weather()` for the default location produced:

| Date | Dashboard icon | Open-Meteo daily code | Open-Meteo description | cloud_cover_mean | Precip sum | Max PoP |
|------|----------------|----------------------|------------------------|------------------|------------|---------|
| 2026-07-23 | cloud | 51 | Light drizzle | 95% | 0.1 mm | 4% |
| 2026-07-24 | cloud | 3 | Overcast | 76% | 0.0 mm | 10% |
| 2026-07-25 | cloud | 3 | Overcast | 58% | 0.0 mm | 12% |
| 2026-07-26 | rain | 80 | Slight rain showers | 83% | 6.4 mm | 70% |
| 2026-07-27 | rain-light | 51 | Light drizzle | 18% | 1.7 mm | 49% |

(2026-07-23's code 51 was already downgraded from a rain icon to a cloud icon by the existing borderline-rain threshold added in TASK-5.)

## Side-by-side comparison with AccuWeather

| Date | Dashboard icon | AccuWeather description | AccuWeather PoP | Partly-cloudy divergence? |
|------|----------------|-------------------------|-----------------|---------------------------|
| 2026-07-23 | cloud | Rather cloudy | 7% | No |
| 2026-07-24 | cloud | Pleasant with a sun-and-cloud mix | 25% | **Yes** - dashboard shows cloud, consumer forecast is partly cloudy |
| 2026-07-25 | cloud | Mostly sunny and delightful | 4% | **Yes** - dashboard shows cloud, consumer forecast is mostly sunny |
| 2026-07-26 | rain | Variable cloudiness with a brief shower or two | 62% | No (rain expected) |
| 2026-07-27 | rain-light | Mostly sunny and pleasant | 5% | No (TASK-5 already covers false-rain thresholding) |

Two of the five days (2026-07-24 and 2026-07-25) should visually read as partly cloudy or mostly sunny, but the dashboard renders a plain cloud icon.

## What Open-Meteo provides

Open-Meteo exposes partly-cloudy information in at least two ways:

1. **WMO weather interpretation codes** in the `weather_code` field:
   - `0` - Clear sky
   - `1` - Mainly clear
   - `2` - Partly cloudy
   - `3` - Overcast

2. **Cloud cover fraction** fields:
   - `current.cloud_cover` - percent of sky covered by clouds right now.
   - `daily.cloud_cover_mean` - mean cloud cover percent for the day.

`src/weather.py` already maps WMO codes `1` and `2` to the `partly-cloudy` icon, and both `templates/devices/og.liquid` and `templates/devices/x.liquid` already ship a `partly-cloudy` SVG (sun behind cloud). The mapping and icon asset are therefore **not missing**.

## Why partly cloudy disappears from the dashboard

Open-Meteo documents the daily `weather_code` as **"the most severe weather condition on a given day"**. For cloud cover, this means a single overcast hour can cause the whole day to be reported as code `3` (Overcast), even when the day's mean cloud cover is in the partly-cloudy or mostly-sunny range.

Evidence from the query above:

- 2026-07-25: `weather_code = 3` (Overcast) but `cloud_cover_mean = 58%`. By most consumer-forecast definitions, 58% cloud cover is partly cloudy or mostly sunny, not overcast.
- 2026-07-24: `weather_code = 3` but `cloud_cover_mean = 76%`. Consumer forecasts describe this as "sun-and-cloud mix".

Because the dashboard uses the daily `weather_code` directly, these days get a plain `cloud` icon instead of `partly-cloudy`.

## Recommendation

Use `daily.cloud_cover_mean` to refine the daily icon when the WMO code is non-precipitation and the most-severe-hour code overstates cloudiness:

- Keep current mappings for codes `0`, `1`, and `2` (sun / partly-cloudy).
- For code `3` (Overcast):
  - `cloud_cover_mean < 65%` -> `partly-cloudy`
  - `cloud_cover_mean >= 65%` -> `cloud`
- Keep rain / snow / thunder codes and the existing precipitation-based intensity logic unchanged.

This preserves the simple WMO-based mapping while letting the dashboard surface partly-cloudy days that Open-Meteo otherwise reports as overcast.

### Threshold rationale

Common cloud-cover terminology maps roughly as:

| Cloud cover | Consumer term |
|-------------|---------------|
| 0-25% | Clear / mostly clear |
| 25-65% | Partly cloudy / partly sunny |
| 65-85% | Mostly cloudy |
| >85% | Overcast / cloudy |

A 65% threshold splits "partly cloudy" from "mostly cloudy" and matches the observed divergence on 2026-07-25 (58% -> partly-cloudy) and 2026-07-24 (76% -> cloud).

## Follow-up work

- Implementation task: update `src/weather.py` to fetch `daily.cloud_cover_mean` and apply the refinement above.
- Add tests covering the new cloud-cover-based daily icon selection.
- Update `templates/devices/*.liquid` only if a different icon is desired; the existing `partly-cloudy` SVG is already suitable.

## References

- [Open-Meteo forecast API docs](https://open-meteo.com/en/docs)
- [AccuWeather Amsterdam 10-day forecast](https://www.accuweather.com/en/nl/amsterdam/249758/daily-weather-forecast/249758)
- `src/weather.py` WMO code mapping and `select_weather_icon()` logic
- `templates/devices/og.liquid` and `templates/devices/x.liquid` partly-cloudy icon captures
- Related investigation: `backlog/docs/doc-1 - Weather-forecast-discrepancy-Open-Meteo-vs-Google-Weather.md`
