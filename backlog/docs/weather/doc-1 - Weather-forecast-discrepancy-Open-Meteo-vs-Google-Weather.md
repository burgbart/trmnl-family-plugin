---
id: doc-1
title: 'Weather forecast discrepancy: Open-Meteo vs Google Weather'
type: guide
created_date: '2026-07-23 11:38'
updated_date: '2026-07-23 11:40'
---
# Weather forecast discrepancy: Open-Meteo vs Google Weather

## Context

The TRMNL dashboard fetches weather forecasts from the free [Open-Meteo API](https://open-meteo.com/en/docs). A user observed that the dashboard often looks gloomier than Google Weather, predicting rain on days when Google does not.

## Investigation (2026-07-23)

### Location and method

- Location: Amsterdam, Netherlands (default config: `WEATHER_LATITUDE=52.3676`, `WEATHER_LONGITUDE=4.9041`).
- Open-Meteo request: same parameters used by `src/weather.py` (`daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max`, `forecast_days=5`).
- Comparison source: [AccuWeather 10-day forecast for Amsterdam](https://www.accuweather.com/en/nl/amsterdam/249758/daily-weather-forecast/249758). AccuWeather is a reasonable proxy for the consumer-grade forecast Google Weather presents in its UI.

Raw data and scripts are stored alongside this document in `backlog/docs/weather/`.

### Side-by-side forecast

| Date | Open-Meteo daily code | Open-Meteo description | Precip sum | Max PoP | AccuWeather description | AccuWeather PoP | Match? |
|------|----------------------|------------------------|------------|---------|-------------------------|-----------------|--------|
| 2026-07-23 | 51 | Light drizzle | 0.2 mm | 4% | Rather cloudy | 7% | **No** |
| 2026-07-24 | 51 | Light drizzle | 0.1 mm | 10% | Pleasant with a sun-and-cloud mix | 25% | **No** |
| 2026-07-25 | 3 | Overcast | 0.0 mm | 12% | Mostly sunny and delightful | 4% | **No** |
| 2026-07-26 | 80 | Slight rain showers | 2.7 mm | 70% | Variable cloudiness with a brief shower or two | 62% | Yes |
| 2026-07-27 | 51 | Light drizzle | 0.3 mm | 49% | Mostly sunny and pleasant | 5% | **No** |

Only one day (2026-07-26) matched. On the other four days, Open-Meteo reported rain/drizzle/overcast while AccuWeather showed cloudy, partly sunny, or mostly sunny conditions with low precipitation chances.

### Why Open-Meteo looks gloomier

Three interacting factors cause the dashboard to show more rain icons than Google/AccuWeather:

#### 1. Open-Meteo daily `weather_code` is the most severe condition of the day

Open-Meteo documents the daily `weather_code` as **"the most severe weather condition on a given day"**. The hourly data shows that the reported drizzle usually comes from one or two brief hours with only 0.1 mm of precipitation; the rest of the day can be clear or partly cloudy. Because the daily code captures the worst hour, a short-lived drizzle turns the whole day into a "Light drizzle" icon.

#### 2. The dashboard maps any drizzle/rain code directly to a rain icon

`src/weather.py` treats every WMO code in the 51-67 (drizzle/rain) and 80-82 (showers) ranges as a rain icon. It only distinguishes `rain-light` vs `rain` vs `rain-heavy` by total daily precipitation amount. It does not consider how brief the precipitation is or how low the probability is.

#### 3. The default forecast model over-predicts light drizzle for this location

Open-Meteo's default `best_match` model produced drizzle/shower codes on four of the five days. Repeating the request with model-specific endpoints showed that the DWD `icon_seamless` model (higher-resolution for Central Europe) produced drizzle/shower codes on only one of the five days, much closer to AccuWeather. The default model selection therefore contributes to the gloomy bias for Amsterdam.

## Options considered

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| A. Do nothing and document | Keep current code; explain that Open-Meteo may differ from Google. | Zero risk; no code change. | Dashboard continues to look gloomier than expected. |
| B. Switch Open-Meteo model | Request `icon_seamless` (or another regional model) for Europe. | Better regional resolution; fewer false drizzle days. | Model suitability varies by location; adds config complexity. |
| C. Threshold daily icon selection | Only show a rain icon when `precipitation_probability_max` or `precipitation_sum` crosses a threshold; otherwise prefer cloud/sun icon. | Keeps free Open-Meteo provider; aligns better with consumer forecasts. | Requires choosing thresholds; may occasionally hide real light rain. |
| D. Derive icon from hourly data | Fetch hourly codes and pick the most frequent or weighted condition. | More representative of the whole day. | More data and more complex logic. |
| E. Switch provider | Use AccuWeather, OpenWeatherMap, or another commercial API. | Matches Google-like consumer forecasts. | Requires API key, rate limits, and possibly cost. |

## Recommendation

Adopt a **combined short-term + medium-term approach**:

1. **Short-term:** Adjust `src/weather.py` so the daily icon selection thresholds on precipitation probability and/or amount before showing a rain icon for borderline codes (drizzle and slight showers). For example, a code 51/53/80 day with `precipitation_probability_max < 30%` and `precipitation_sum < 1.0 mm` should fall back to a cloud or partly-cloudy icon instead of a rain icon.
2. **Medium-term:** Add an optional `WEATHER_MODEL` configuration variable that passes a specific Open-Meteo model (e.g., `icon_seamless` for Europe, `gfs_seamless` elsewhere) so deployments can choose a higher-resolution model for their region.
3. **Documentation:** Keep this guide so future maintainers understand why Open-Meteo and Google Weather can diverge.

This preserves the free, no-API-key Open-Meteo setup while making the dashboard visually closer to consumer forecasts.

## Follow-up work

- Implementation task: update `src/weather.py` icon selection and add `WEATHER_MODEL` config (see linked Backlog task).
- Update tests in `tests/test_fetcher.py` or add a new `tests/test_weather.py` to cover threshold logic.

## References

- [Open-Meteo forecast API docs](https://open-meteo.com/en/docs)
- [AccuWeather Amsterdam 10-day forecast](https://www.accuweather.com/en/nl/amsterdam/249758/daily-weather-forecast/249758)
- Open-Meteo daily `weather_code` is described as "the most severe weather condition on a given day" in the API documentation.
