"""Tests for src/weather.py icon selection and Open-Meteo fetching."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from src import weather
from src.weather import (
    BORDERLINE_RAIN_FALLBACK_ICON,
    BORDERLINE_RAIN_MAX_PRECIPITATION,
    BORDERLINE_RAIN_MAX_PROBABILITY,
    fetch_weather,
    select_weather_icon,
)


class TestSelectWeatherIcon:
    """Tests for select_weather_icon threshold logic."""

    @pytest.mark.parametrize("code", [51, 53, 80])
    def test_borderline_rain_downgraded_when_low_probability_and_amount(
        self, code: int
    ) -> None:
        """Drizzle/slight-shower codes become cloud when both thresholds are low."""
        icon = select_weather_icon(
            code,
            BORDERLINE_RAIN_MAX_PRECIPITATION - 0.1,
            is_daily=True,
            precipitation_probability=BORDERLINE_RAIN_MAX_PROBABILITY - 1,
        )
        assert icon == BORDERLINE_RAIN_FALLBACK_ICON

    @pytest.mark.parametrize("code", [51, 53, 80])
    def test_borderline_rain_kept_when_probability_high(
        self, code: int
    ) -> None:
        """A high enough probability keeps the rain icon for borderline codes."""
        icon = select_weather_icon(
            code,
            BORDERLINE_RAIN_MAX_PRECIPITATION - 0.1,
            is_daily=True,
            precipitation_probability=BORDERLINE_RAIN_MAX_PROBABILITY + 1,
        )
        assert icon == "rain-light"

    @pytest.mark.parametrize("code", [51, 53, 80])
    def test_borderline_rain_kept_when_precipitation_high(
        self, code: int
    ) -> None:
        """A high enough precipitation amount keeps the rain icon for borderline codes."""
        icon = select_weather_icon(
            code,
            BORDERLINE_RAIN_MAX_PRECIPITATION + 0.1,
            is_daily=True,
            precipitation_probability=BORDERLINE_RAIN_MAX_PROBABILITY - 1,
        )
        assert icon == "rain-light"

    @pytest.mark.parametrize("code", [51, 53, 80])
    def test_borderline_rain_kept_when_probability_unknown(
        self, code: int
    ) -> None:
        """Without a probability we cannot threshold, so keep the rain icon."""
        icon = select_weather_icon(
            code,
            BORDERLINE_RAIN_MAX_PRECIPITATION - 0.1,
            is_daily=True,
            precipitation_probability=None,
        )
        assert icon == "rain-light"

    def test_non_borderline_rain_ignores_thresholds(self) -> None:
        """Real rain codes show rain even with tiny probability/amount."""
        icon = select_weather_icon(
            61,
            BORDERLINE_RAIN_MAX_PRECIPITATION - 0.1,
            is_daily=True,
            precipitation_probability=BORDERLINE_RAIN_MAX_PROBABILITY - 1,
        )
        assert icon == "rain-light"

    def test_borderline_rain_not_downgraded_for_current_hourly(self) -> None:
        """The threshold only applies to daily icons, not current/hourly."""
        icon = select_weather_icon(
            51,
            0.1,
            is_daily=False,
            precipitation_probability=BORDERLINE_RAIN_MAX_PROBABILITY - 1,
        )
        assert icon == "rain-light"

    @pytest.mark.parametrize(
        "code,expected",
        [
            (0, "sun"),
            (1, "partly-cloudy"),
            (2, "partly-cloudy"),
            (3, "cloud"),
            (95, "thunder"),
            (71, "snow"),
        ],
    )
    def test_non_rain_codes_unchanged(self, code: int, expected: str) -> None:
        """Sun, cloud, thunder, and snow codes keep their regular icons."""
        assert select_weather_icon(code, 0.0, is_daily=True, default=expected) == expected


class TestFetchWeather:
    """Tests for fetch_weather Open-Meteo integration."""

    @staticmethod
    def _forecast_response() -> dict:
        return {
            "latitude": 52.366,
            "longitude": 4.901,
            "current": {
                "time": "2026-07-23T13:30",
                "interval": 900,
                "temperature_2m": 18.8,
                "apparent_temperature": 16.6,
                "weather_code": 3,
                "precipitation": 0.0,
            },
            "daily": {
                "time": ["2026-07-23", "2026-07-24"],
                "weather_code": [51, 80],
                "temperature_2m_max": [19.1, 22.8],
                "temperature_2m_min": [16.8, 16.7],
                "precipitation_sum": [0.2, 0.1],
                "precipitation_probability_max": [4, 10],
            },
        }

    @patch("src.weather.requests.get")
    def test_fetch_weather_applies_daily_threshold(self, mock_get: MagicMock) -> None:
        """Borderline daily codes with low probability/amount are downgraded."""
        mock_response = MagicMock()
        mock_response.json.return_value = self._forecast_response()
        mock_get.return_value = mock_response

        result = fetch_weather()

        assert len(result.forecast) == 2
        assert result.forecast[0].icon == BORDERLINE_RAIN_FALLBACK_ICON
        assert result.forecast[1].icon == BORDERLINE_RAIN_FALLBACK_ICON
        assert result.forecast[0].precipitation_probability == 4
        assert result.forecast[0].precipitation_amount == 0.2

    @patch("src.weather.requests.get")
    def test_fetch_weather_passes_model_when_configured(
        self, mock_get: MagicMock
    ) -> None:
        """WEATHER_MODEL is forwarded as the Open-Meteo models parameter."""
        mock_response = MagicMock()
        mock_response.json.return_value = self._forecast_response()
        mock_get.return_value = mock_response

        with patch("src.weather.WEATHER_MODEL", "icon_seamless"):
            fetch_weather()

        mock_get.assert_called_once()
        call_params = mock_get.call_args.kwargs.get("params") or mock_get.call_args[1].get("params")
        assert call_params is not None
        assert call_params["models"] == "icon_seamless"

    @patch("src.weather.requests.get")
    def test_fetch_weather_omits_model_when_unconfigured(
        self, mock_get: MagicMock
    ) -> None:
        """No models parameter is sent when WEATHER_MODEL is empty."""
        mock_response = MagicMock()
        mock_response.json.return_value = self._forecast_response()
        mock_get.return_value = mock_response

        with patch("src.weather.WEATHER_MODEL", ""):
            fetch_weather()

        call_params = mock_get.call_args.kwargs.get("params") or mock_get.call_args[1].get("params")
        assert "models" not in call_params
