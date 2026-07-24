"""Fetch current weather from Open-Meteo."""

from __future__ import annotations

from datetime import date
from typing import Optional

import requests

from src.config import LATITUDE, LONGITUDE, WEATHER_MODEL
from src.data import Weather, WeatherForecast

# WMO Weather interpretation codes (simplified)
# https://open-meteo.com/en/docs
WEATHER_CODES = {
    0: ("Clear sky", "sun"),
    1: ("Mainly clear", "partly-cloudy"),
    2: ("Partly cloudy", "partly-cloudy"),
    3: ("Overcast", "cloud"),
    45: ("Fog", "cloud"),
    48: ("Depositing rime fog", "cloud"),
    51: ("Light drizzle", "rain"),
    53: ("Moderate drizzle", "rain"),
    55: ("Dense drizzle", "rain"),
    56: ("Light freezing drizzle", "rain"),
    57: ("Dense freezing drizzle", "rain"),
    61: ("Slight rain", "rain"),
    63: ("Moderate rain", "rain"),
    65: ("Heavy rain", "rain"),
    66: ("Light freezing rain", "rain"),
    67: ("Heavy freezing rain", "rain"),
    71: ("Slight snow", "snow"),
    73: ("Moderate snow", "snow"),
    75: ("Heavy snow", "snow"),
    77: ("Snow grains", "snow"),
    80: ("Slight rain showers", "rain"),
    81: ("Moderate rain showers", "rain"),
    82: ("Violent rain showers", "rain"),
    85: ("Slight snow showers", "snow"),
    86: ("Heavy snow showers", "snow"),
    95: ("Thunderstorm", "thunder"),
    96: ("Thunderstorm with hail", "thunder"),
    99: ("Thunderstorm with heavy hail", "thunder"),
}

RAIN_CODES = {
    51,
    53,
    55,
    56,
    57,
    61,
    63,
    65,
    66,
    67,
    80,
    81,
    82,
}
SNOW_CODES = {71, 73, 75, 77, 85, 86}
THUNDER_CODES = {95, 96, 99}

# Intensity thresholds. Daily values are mm/day; current values are mm/h.
PRECIPITATION_THRESHOLDS = {
    "daily": {"light": 2.5, "heavy": 10.0},
    "hourly": {"light": 0.5, "heavy": 4.0},
}

# Open-Meteo reports the most severe hourly weather_code for each day. Brief
# drizzle or slight showers (codes 51/53/80) can therefore dominate the daily
# icon even when the day is mostly dry. Threshold those borderline codes back
# to a cloud icon when both the precipitation probability and total amount are
# low. See backlog/docs/weather/doc-1 for the investigation.
BORDERLINE_RAIN_CODES = {51, 53, 80}
BORDERLINE_RAIN_MAX_PROBABILITY = 30  # percent
BORDERLINE_RAIN_MAX_PRECIPITATION = 1.0  # mm/day
BORDERLINE_RAIN_FALLBACK_ICON = "cloud"

# Open-Meteo reports the most severe hourly weather_code for each day. A single
# overcast hour can make an otherwise partly-cloudy day report code 3. Use the
# daily mean cloud cover to recover the partly-cloudy state. See backlog/docs/doc-2.
CLOUD_COVER_PARTLY_CLOUDY_THRESHOLD = 65  # percent


def select_weather_icon(
    code: int,
    precipitation: float,
    *,
    is_daily: bool = False,
    precipitation_probability: int | None = None,
    cloud_cover_mean: int | None = None,
    default: str = "cloud",
) -> str:
    """Map a WMO weather code + precipitation amount to a dashboard icon.

    The icon set is deliberately small for a low-resolution e-ink screen:
    sun, partly-cloudy, cloud, rain-light, rain, rain-heavy, thunder, snow.

    For daily icons, borderline drizzle/shower codes (51/53/80) are downgraded
    to a plain cloud icon when both the precipitation probability and the total
    precipitation amount are low. Open-Meteo reports the most severe hourly
    code for each day, so a brief 0.1 mm drizzle event would otherwise show a
    full-day rain icon.

    For daily code 3 (Overcast), the mean cloud cover fraction is used to
    distinguish partly-cloudy days (< 65% cover) from genuinely overcast days
    (>= 65% cover), because the most-severe-hour code can overstate cloudiness.
    """
    if code in THUNDER_CODES:
        return "thunder"
    if code in SNOW_CODES:
        return "snow"
    if code in RAIN_CODES:
        if is_daily and code in BORDERLINE_RAIN_CODES:
            prob_low = (
                precipitation_probability is not None
                and precipitation_probability < BORDERLINE_RAIN_MAX_PROBABILITY
            )
            amount_low = precipitation < BORDERLINE_RAIN_MAX_PRECIPITATION
            if prob_low and amount_low:
                return BORDERLINE_RAIN_FALLBACK_ICON
        thresholds = PRECIPITATION_THRESHOLDS["daily" if is_daily else "hourly"]
        if precipitation >= thresholds["heavy"]:
            return "rain-heavy"
        if precipitation < thresholds["light"]:
            return "rain-light"
        return "rain"
    if is_daily and code == 3 and cloud_cover_mean is not None:
        if cloud_cover_mean < CLOUD_COVER_PARTLY_CLOUDY_THRESHOLD:
            return "partly-cloudy"
    return default


def fetch_weather() -> Weather:
    """Fetch current weather and a 5-day forecast (today + 4 upcoming) from Open-Meteo."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": "temperature_2m,apparent_temperature,weather_code,precipitation",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,cloud_cover_mean",
        "timezone": "auto",
        "forecast_days": 5,
    }
    if WEATHER_MODEL:
        params["models"] = WEATHER_MODEL

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()

    current = data.get("current", {})
    temperature = int(round(current.get("temperature_2m", 0)))
    feels_like = int(round(current.get("apparent_temperature", 0)))
    code = current.get("weather_code", 0)
    current_precipitation = float(current.get("precipitation") or 0.0)

    description, base_icon = WEATHER_CODES.get(code, ("Unknown", "cloud"))
    icon = select_weather_icon(code, current_precipitation, is_daily=False, default=base_icon)

    forecast: list[WeatherForecast] = []
    daily = data.get("daily", {})
    dates = daily.get("time", [])
    codes = daily.get("weather_code", [])
    highs = daily.get("temperature_2m_max", [])
    lows = daily.get("temperature_2m_min", [])
    precip_sums = daily.get("precipitation_sum", [])
    precip_probs = daily.get("precipitation_probability_max", [])
    cloud_covers = daily.get("cloud_cover_mean", [])
    for i in range(0, min(5, len(dates))):
        day_code = codes[i] if i < len(codes) else 0
        day_desc, day_base_icon = WEATHER_CODES.get(day_code, ("Unknown", "cloud"))
        day_precip = float(precip_sums[i] if i < len(precip_sums) and precip_sums[i] is not None else 0.0)
        day_prob = precip_probs[i] if i < len(precip_probs) and precip_probs[i] is not None else None
        if day_prob is not None:
            day_prob = int(day_prob)
        day_cloud_cover = cloud_covers[i] if i < len(cloud_covers) and cloud_covers[i] is not None else None
        if day_cloud_cover is not None:
            day_cloud_cover = int(day_cloud_cover)
        day_icon = select_weather_icon(
            day_code,
            day_precip,
            is_daily=True,
            precipitation_probability=day_prob,
            cloud_cover_mean=day_cloud_cover,
            default=day_base_icon,
        )
        forecast.append(
            WeatherForecast(
                date=date.fromisoformat(dates[i]),
                description=day_desc,
                temperature_high=int(round(highs[i])),
                temperature_low=int(round(lows[i])),
                icon=day_icon,
                precipitation_amount=round(day_precip, 1) if day_precip else None,
                precipitation_probability=day_prob,
            )
        )

    alert: str | None = None
    if codes and codes[0] is not None:
        today_desc, _ = WEATHER_CODES.get(codes[0], ("Unknown", "cloud"))
        today_icon = forecast[0].icon if forecast else icon
        if today_icon in {"rain-light", "rain", "rain-heavy", "thunder"}:
            alert = f"{today_desc} expected today"

    return Weather(
        description=description,
        temperature=temperature,
        feels_like=feels_like,
        icon=icon,
        forecast=forecast,
        alert=alert,
        precipitation_amount=round(current_precipitation, 1) if current_precipitation else None,
        precipitation_probability=None,
    )


def fetch_weather_or_dummy() -> Weather:
    """Fetch real weather, falling back to dummy data on error."""
    from src.data import fetch_weather as dummy_weather

    try:
        return fetch_weather()
    except Exception as exc:  # pragma: no cover
        print(f"Weather fetch failed: {exc}; using dummy data")
        return dummy_weather()
