"""Tests for src/weather.py icon selection and Open-Meteo fetching."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from src import weather
from src.weather import (
    BORDERLINE_RAIN_EXPECTED_AMOUNT_CLOUD_THRESHOLD,
    BORDERLINE_RAIN_EXPECTED_AMOUNT_RAIN_LIGHT_THRESHOLD,
    CLOUD_COVER_PARTLY_CLOUDY_THRESHOLD,
    fetch_weather,
    select_weather_icon,
)


class TestSelectWeatherIcon:
    """Tests for select_weather_icon threshold logic."""

    @pytest.mark.parametrize("code", [51, 53, 80])
    def test_borderline_rain_cloud_when_expected_amount_below_threshold(
        self, code: int
    ) -> None:
        """Very low expected amount downgrades borderline codes to cloud."""
        amount = BORDERLINE_RAIN_EXPECTED_AMOUNT_CLOUD_THRESHOLD / 2
        # probability 100% so amount == expected_amount
        icon = select_weather_icon(
            code,
            amount,
            is_daily=True,
            precipitation_probability=100,
        )
        assert icon == "cloud"

    @pytest.mark.parametrize("code", [51, 53, 80])
    def test_borderline_rain_light_when_expected_amount_between_thresholds(
        self, code: int
    ) -> None:
        """Moderate expected amount renders rain-light for borderline codes."""
        expected = (
            BORDERLINE_RAIN_EXPECTED_AMOUNT_CLOUD_THRESHOLD
            + BORDERLINE_RAIN_EXPECTED_AMOUNT_RAIN_LIGHT_THRESHOLD
        ) / 2
        # 50% probability -> amount = expected * 2
        amount = expected * 2
        icon = select_weather_icon(
            code,
            amount,
            is_daily=True,
            precipitation_probability=50,
        )
        assert icon == "rain-light"

    @pytest.mark.parametrize("code", [51, 53, 80])
    def test_borderline_rain_falls_through_when_expected_amount_high(
        self, code: int
    ) -> None:
        """High expected amount falls through to amount-based thresholds."""
        amount = BORDERLINE_RAIN_EXPECTED_AMOUNT_RAIN_LIGHT_THRESHOLD * 2
        icon = select_weather_icon(
            code,
            amount,
            is_daily=True,
            precipitation_probability=100,
        )
        # amount 3.0 mm is below daily light threshold 2.5? Wait 3.0 >= 2.5 so rain
        assert icon == "rain"

    @pytest.mark.parametrize("code", [51, 53, 80])
    def test_borderline_rain_falls_through_when_probability_unknown(
        self, code: int
    ) -> None:
        """Without a probability we cannot compute expected amount."""
        icon = select_weather_icon(
            code,
            BORDERLINE_RAIN_EXPECTED_AMOUNT_CLOUD_THRESHOLD / 2,
            is_daily=True,
            precipitation_probability=None,
        )
        assert icon == "rain-light"

    @pytest.mark.parametrize("code", [61, 63, 65, 66, 67, 81, 82])
    def test_non_borderline_rain_uses_amount_based_thresholds(
        self, code: int
    ) -> None:
        """Non-borderline rain codes ignore expected-amount scoring."""
        icon = select_weather_icon(
            code,
            0.1,
            is_daily=True,
            precipitation_probability=5,
        )
        assert icon == "rain-light"

    def test_borderline_rain_not_downgraded_for_current_hourly(self) -> None:
        """Expected-amount scoring only applies to daily icons."""
        icon = select_weather_icon(
            51,
            BORDERLINE_RAIN_EXPECTED_AMOUNT_CLOUD_THRESHOLD / 2,
            is_daily=False,
            precipitation_probability=100,
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

    def test_code_3_daily_partly_cloudy_when_cloud_cover_below_threshold(self) -> None:
        """Code 3 with low mean cloud cover surfaces as partly-cloudy."""
        icon = select_weather_icon(
            3,
            0.0,
            is_daily=True,
            cloud_cover_mean=CLOUD_COVER_PARTLY_CLOUDY_THRESHOLD - 1,
        )
        assert icon == "partly-cloudy"

    def test_code_3_daily_cloud_when_cloud_cover_at_threshold(self) -> None:
        """Code 3 with mean cloud cover at the threshold stays cloud."""
        icon = select_weather_icon(
            3,
            0.0,
            is_daily=True,
            cloud_cover_mean=CLOUD_COVER_PARTLY_CLOUDY_THRESHOLD,
        )
        assert icon == "cloud"

    def test_code_3_daily_cloud_when_cloud_cover_above_threshold(self) -> None:
        """Code 3 with high mean cloud cover stays cloud."""
        icon = select_weather_icon(
            3,
            0.0,
            is_daily=True,
            cloud_cover_mean=CLOUD_COVER_PARTLY_CLOUDY_THRESHOLD + 10,
        )
        assert icon == "cloud"

    def test_code_3_daily_cloud_when_cloud_cover_unknown(self) -> None:
        """Code 3 falls back to cloud when cloud_cover_mean is unavailable."""
        icon = select_weather_icon(3, 0.0, is_daily=True, cloud_cover_mean=None)
        assert icon == "cloud"

    def test_code_3_current_ignores_cloud_cover(self) -> None:
        """The cloud-cover refinement applies only to daily icons."""
        icon = select_weather_icon(
            3,
            0.0,
            is_daily=False,
            cloud_cover_mean=CLOUD_COVER_PARTLY_CLOUDY_THRESHOLD - 1,
        )
        assert icon == "cloud"

    def test_rain_codes_ignore_cloud_cover(self) -> None:
        """Precipitation codes are not affected by cloud cover refinement."""
        icon = select_weather_icon(
            61,
            5.0,
            is_daily=True,
            cloud_cover_mean=CLOUD_COVER_PARTLY_CLOUDY_THRESHOLD - 1,
        )
        assert icon == "rain"


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
                "cloud_cover_mean": [95, 58],
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
        assert result.forecast[0].icon == "cloud"
        assert result.forecast[1].icon == "cloud"
        assert result.forecast[0].precipitation_probability == 4
        assert result.forecast[0].precipitation_amount == 0.2

    @patch("src.weather.requests.get")
    def test_fetch_weather_requests_cloud_cover_mean(self, mock_get: MagicMock) -> None:
        """The Open-Meteo daily parameter list includes cloud_cover_mean."""
        mock_response = MagicMock()
        mock_response.json.return_value = self._forecast_response()
        mock_get.return_value = mock_response

        fetch_weather()

        call_params = mock_get.call_args.kwargs.get("params") or mock_get.call_args[1].get("params")
        assert "cloud_cover_mean" in call_params["daily"]

    @patch("src.weather.requests.get")
    def test_fetch_weather_code_3_cloud_cover_refines_icon(self, mock_get: MagicMock) -> None:
        """Daily code 3 with low mean cloud cover surfaces as partly-cloudy."""
        response = self._forecast_response()
        response["daily"]["weather_code"] = [3, 3]
        response["daily"]["cloud_cover_mean"] = [58, 76]
        response["daily"]["precipitation_sum"] = [0.0, 0.0]
        response["daily"]["precipitation_probability_max"] = [12, 10]
        mock_response = MagicMock()
        mock_response.json.return_value = response
        mock_get.return_value = mock_response

        result = fetch_weather()

        assert result.forecast[0].icon == "partly-cloudy"
        assert result.forecast[1].icon == "cloud"

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
