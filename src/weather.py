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
    71: ("Slight snow", "cloud"),
    73: ("Moderate snow", "cloud"),
    75: ("Heavy snow", "cloud"),
    77: ("Snow grains", "cloud"),
    80: ("Slight rain showers", "rain"),
    81: ("Moderate rain showers", "rain"),
    82: ("Violent rain showers", "rain"),
    85: ("Slight snow showers", "cloud"),
    86: ("Heavy snow showers", "cloud"),
    95: ("Thunderstorm", "rain"),
    96: ("Thunderstorm with hail", "rain"),
    99: ("Thunderstorm with heavy hail", "rain"),
}


def fetch_weather() -> Weather:
    """Fetch current weather and a 3-day forecast from Open-Meteo."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": "temperature_2m,apparent_temperature,weather_code",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": 4,
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()

    current = data.get("current", {})
    temperature = int(round(current.get("temperature_2m", 0)))
    feels_like = int(round(current.get("apparent_temperature", 0)))
    code = current.get("weather_code", 0)

    description, icon = WEATHER_CODES.get(code, ("Unknown", "cloud"))

    forecast: list[WeatherForecast] = []
    daily = data.get("daily", {})
    dates = daily.get("time", [])
    codes = daily.get("weather_code", [])
    highs = daily.get("temperature_2m_max", [])
    lows = daily.get("temperature_2m_min", [])
    for i in range(1, min(4, len(dates))):
        day_code = codes[i] if i < len(codes) else 0
        day_desc, day_icon = WEATHER_CODES.get(day_code, ("Unknown", "cloud"))
        forecast.append(
            WeatherForecast(
                date=date.fromisoformat(dates[i]),
                description=day_desc,
                temperature_high=int(round(highs[i])),
                temperature_low=int(round(lows[i])),
                icon=day_icon,
            )
        )

    alert: str | None = None
    if codes and codes[0] is not None:
        today_desc, today_icon = WEATHER_CODES.get(codes[0], ("Unknown", "cloud"))
        if today_icon == "rain":
            alert = f"{today_desc} expected today"

    return Weather(
        description=description,
        temperature=temperature,
        feels_like=feels_like,
        icon=icon,
        forecast=forecast,
        alert=alert,
    )


def fetch_weather_or_dummy() -> Weather:
    """Fetch real weather, falling back to dummy data on error."""
    from src.data import fetch_weather as dummy_weather

    try:
        return fetch_weather()
    except Exception as exc:  # pragma: no cover
        print(f"Weather fetch failed: {exc}; using dummy data")
        return dummy_weather()
