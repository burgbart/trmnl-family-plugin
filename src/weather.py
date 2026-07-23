"""Fetch current weather from Open-Meteo."""

from __future__ import annotations

from datetime import date
from typing import Optional

import requests

from src.config import LATITUDE, LONGITUDE
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


def select_weather_icon(
    code: int,
    precipitation: float,
    *,
    is_daily: bool = False,
    default: str = "cloud",
) -> str:
    """Map a WMO weather code + precipitation amount to a dashboard icon.

    The icon set is deliberately small for a low-resolution e-ink screen:
    sun, partly-cloudy, cloud, rain-light, rain, rain-heavy, thunder, snow.
    """
    if code in THUNDER_CODES:
        return "thunder"
    if code in SNOW_CODES:
        return "snow"
    if code in RAIN_CODES:
        thresholds = PRECIPITATION_THRESHOLDS["daily" if is_daily else "hourly"]
        if precipitation >= thresholds["heavy"]:
            return "rain-heavy"
        if precipitation < thresholds["light"]:
            return "rain-light"
        return "rain"
    return default


def fetch_weather() -> Weather:
    """Fetch current weather and a 5-day forecast (today + 4 upcoming) from Open-Meteo."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": "temperature_2m,apparent_temperature,weather_code,precipitation",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max",
        "timezone": "auto",
        "forecast_days": 5,
    }

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
    for i in range(0, min(5, len(dates))):
        day_code = codes[i] if i < len(codes) else 0
        day_desc, day_base_icon = WEATHER_CODES.get(day_code, ("Unknown", "cloud"))
        day_precip = float(precip_sums[i] if i < len(precip_sums) and precip_sums[i] is not None else 0.0)
        day_icon = select_weather_icon(day_code, day_precip, is_daily=True, default=day_base_icon)
        day_prob = precip_probs[i] if i < len(precip_probs) and precip_probs[i] is not None else None
        if day_prob is not None:
            day_prob = int(day_prob)
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
