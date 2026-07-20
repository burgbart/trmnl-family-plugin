"""Fetch current weather from Open-Meteo."""

from __future__ import annotations

from typing import Optional

import requests

from src.config import LATITUDE, LONGITUDE
from src.data import Weather

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
    """Fetch current weather from Open-Meteo."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": "temperature_2m,apparent_temperature,weather_code",
        "timezone": "auto",
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()

    current = data.get("current", {})
    temperature = int(round(current.get("temperature_2m", 0)))
    feels_like = int(round(current.get("apparent_temperature", 0)))
    code = current.get("weather_code", 0)

    description, icon = WEATHER_CODES.get(code, ("Unknown", "cloud"))

    return Weather(
        description=description,
        temperature=temperature,
        feels_like=feels_like,
        icon=icon,
    )


def fetch_weather_or_dummy() -> Weather:
    """Fetch real weather, falling back to dummy data on error."""
    try:
        return fetch_weather()
    except Exception as exc:  # pragma: no cover
        print(f"Weather fetch failed: {exc}; using dummy data")
        return Weather(
            description="Partly cloudy",
            temperature=21,
            feels_like=19,
            icon="partly-cloudy",
        )
