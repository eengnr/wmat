import ujson
import time
from display import ColorStyle

# Handle JSON:
"""
{
  "unit": "C",
  "current": {
    "temp": 22,
    "condition": 0,
    "isDay": true
  },
  "forecast": {
    "temp1": 18,
    "temp2": 27,
    "condition": 0 // Not used yet
  },
}
"""


class WeatherManager:
    def __init__(self):
        self.unit = "C"
        self.current = None
        self.forecast = None
        self.last_update = None

        self.icon_map_day_white_warm = {
            0: "icons/wi_day-sunny_25_255_190_240.raw",
            1: "icons/wi_day-sunny-overcast_25_255_190_240.raw",
            2: "icons/wi_day-cloudy_25_255_190_240.raw",
            3: "icons/wi_cloudy_25_255_190_240.raw",
            45: "icons/wi_fog_25_255_190_240.raw",
            48: "icons/wi_day-fog_25_255_190_240.raw",
            51: "icons/wi_rain-mix_25_255_190_240.raw",
            53: "icons/wi_showers_25_255_190_240.raw",
            55: "icons/wi_showers_25_255_190_240.raw",
            56: "icons/wi_rain-mix_25_255_190_240.raw",
            57: "icons/wi_rain-mix_25_255_190_240.raw",
            61: "icons/wi_showers_25_255_190_240.raw",
            63: "icons/wi_rain_25_255_190_240.raw",
            65: "icons/wi_rain-wind_25_255_190_240.raw",
            66: "icons/wi_day-hail_25_255_190_240.raw",
            67: "icons/wi_hail_25_255_190_240.raw",
            71: "icons/wi_day-snow_25_255_190_240.raw",
            73: "icons/wi_day-snow-wind_25_255_190_240.raw",
            75: "icons/wi_snow_25_255_190_240.raw",
            77: "icons/wi_snow-wind_25_255_190_240.raw",
            80: "icons/wi_rain-mix_25_255_190_240.raw",
            81: "icons/wi_showers_25_255_190_240.raw",
            82: "icons/wi_rain_25_255_190_240.raw",
            85: "icons/wi_snow_25_255_190_240.raw",
            86: "icons/wi_snow-wind_25_255_190_240.raw",
            95: "icons/wi_day-thunderstorm_25_255_190_240.raw",
            96: "icons/wi_day-sleet-storm_25_255_190_240.raw",
            99: "icons/wi_thunderstorm_25_255_190_240.raw",
            "fallback": "icons/wi_day-sunny_25_255_190_240.raw",
        }

        self.icon_map_day_dark_red = {
            0: "icons/wi_day-sunny_25_100_10_10.raw",
            1: "icons/wi_day-sunny-overcast_25_100_10_10.raw",
            2: "icons/wi_day-cloudy_25_100_10_10.raw",
            3: "icons/wi_cloudy_25_100_10_10.raw",
            45: "icons/wi_fog_25_100_10_10.raw",
            48: "icons/wi_day-fog_25_100_10_10.raw",
            51: "icons/wi_rain-mix_25_100_10_10.raw",
            53: "icons/wi_showers_25_100_10_10.raw",
            55: "icons/wi_showers_25_100_10_10.raw",
            56: "icons/wi_rain-mix_25_100_10_10.raw",
            57: "icons/wi_rain-mix_25_100_10_10.raw",
            61: "icons/wi_showers_25_100_10_10.raw",
            63: "icons/wi_rain_25_100_10_10.raw",
            65: "icons/wi_rain-wind_25_100_10_10.raw",
            66: "icons/wi_day-hail_25_100_10_10.raw",
            67: "icons/wi_hail_25_100_10_10.raw",
            71: "icons/wi_day-snow_25_100_10_10.raw",
            73: "icons/wi_day-snow-wind_25_100_10_10.raw",
            75: "icons/wi_snow_25_100_10_10.raw",
            77: "icons/wi_snow-wind_25_100_10_10.raw",
            80: "icons/wi_rain-mix_25_100_10_10.raw",
            81: "icons/wi_showers_25_100_10_10.raw",
            82: "icons/wi_rain_25_100_10_10.raw",
            85: "icons/wi_snow_25_100_10_10.raw",
            86: "icons/wi_snow-wind_25_100_10_10.raw",
            95: "icons/wi_day-thunderstorm_25_100_10_10.raw",
            96: "icons/wi_day-sleet-storm_25_100_10_10.raw",
            99: "icons/wi_thunderstorm_25_100_10_10.raw",
            "fallback": "icons/wi_day-sunny_25_100_10_10.raw",
        }

        self.icon_map_night_white_warm = {
            0: "icons/wi_night-clear_25_255_190_240.raw",
            1: "icons/wi_night-alt-partly-cloudy_25_255_190_240.raw",
            2: "icons/wi_night-alt-cloudy_25_255_190_240.raw",
            3: "icons/wi_cloudy_25_255_190_240.raw",
            45: "icons/wi_fog_25_255_190_240.raw",
            48: "icons/wi_night-fog_25_255_190_240.raw",
            51: "icons/wi_rain-mix_25_255_190_240.raw",
            53: "icons/wi_showers_25_255_190_240.raw",
            55: "icons/wi_showers_25_255_190_240.raw",
            56: "icons/wi_rain-mix_25_255_190_240.raw",
            57: "icons/wi_rain-mix_25_255_190_240.raw",
            61: "icons/wi_showers_25_255_190_240.raw",
            63: "icons/wi_rain_25_255_190_240.raw",
            65: "icons/wi_rain-wind_25_255_190_240.raw",
            66: "icons/wi_night-alt-hail_25_255_190_240.raw",
            67: "icons/wi_hail_25_255_190_240.raw",
            71: "icons/wi_night-alt-snow_25_255_190_240.raw",
            73: "icons/wi_night-alt-snow-wind_25_255_190_240.raw",
            75: "icons/wi_snow_25_255_190_240.raw",
            77: "icons/wi_snow-wind_25_255_190_240.raw",
            80: "icons/wi_rain-mix_25_255_190_240.raw",
            81: "icons/wi_showers_25_255_190_240.raw",
            82: "icons/wi_rain_25_255_190_240.raw",
            85: "icons/wi_snow_25_255_190_240.raw",
            86: "icons/wi_snow-wind_25_255_190_240.raw",
            95: "icons/wi_night-alt-thunderstorm_25_255_190_240.raw",
            96: "icons/wi_night-alt-sleet-storm_25_255_190_240.raw",
            99: "icons/wi_thunderstorm_25_255_190_240.raw",
            "fallback": "icons/wi_night-clear_25_255_190_240.raw",
        }

        self.icon_map_night_dark_red = {
            0: "icons/wi_night-clear_25_100_10_10.raw",
            1: "icons/wi_night-alt-partly-cloudy_25_100_10_10.raw",
            2: "icons/wi_night-alt-cloudy_25_100_10_10.raw",
            3: "icons/wi_cloudy_25_100_10_10.raw",
            45: "icons/wi_fog_25_100_10_10.raw",
            48: "icons/wi_night-fog_25_100_10_10.raw",
            51: "icons/wi_rain-mix_25_100_10_10.raw",
            53: "icons/wi_showers_25_100_10_10.raw",
            55: "icons/wi_showers_25_100_10_10.raw",
            56: "icons/wi_rain-mix_25_100_10_10.raw",
            57: "icons/wi_rain-mix_25_100_10_10.raw",
            61: "icons/wi_showers_25_100_10_10.raw",
            63: "icons/wi_rain_25_100_10_10.raw",
            65: "icons/wi_rain-wind_25_100_10_10.raw",
            66: "icons/wi_night-alt-hail_25_100_10_10.raw",
            67: "icons/wi_hail_25_100_10_10.raw",
            71: "icons/wi_night-alt-snow_25_100_10_10.raw",
            73: "icons/wi_night-alt-snow-wind_25_100_10_10.raw",
            75: "icons/wi_snow_25_100_10_10.raw",
            77: "icons/wi_snow-wind_25_100_10_10.raw",
            80: "icons/wi_rain-mix_25_100_10_10.raw",
            81: "icons/wi_showers_25_100_10_10.raw",
            82: "icons/wi_rain_25_100_10_10.raw",
            85: "icons/wi_snow_25_100_10_10.raw",
            86: "icons/wi_snow-wind_25_100_10_10.raw",
            95: "icons/wi_night-alt-thunderstorm_25_100_10_10.raw",
            96: "icons/wi_night-alt-sleet-storm_25_100_10_10.raw",
            99: "icons/wi_thunderstorm_25_100_10_10.raw",
            "fallback": "icons/wi_night-clear_25_100_10_10.raw",
        }

    def update_from_json(self, json_text):
        try:
            data = ujson.loads(json_text)

            rawUnit = data.get("unit", "")
            unit = (
                "C"
                if "c" in rawUnit.lower()
                else "F" if "f" in rawUnit.lower() else "C"
            )
            self.unit = unit

            self.current = data.get("current")
            self.forecast = data.get("forecast")

            self.last_update = time.time()

            print("WeatherManager: Updated weather")

        except Exception as e:
            print("WeatherManager: Invalid JSON:", e)

    def get_current(self):
        return self.current

    def get_unit(self):
        return self.unit

    def get_forecast(self):
        return self.forecast

    def get_icon_path(self, condition_code, color):
        """Returns icon path or fallback icon."""
        try:
            code = int(condition_code)
        except (TypeError, ValueError):
            code = "fallback"
        if color == ColorStyle.WHITE_WARM:
            icon_map = self.icon_map_day_white_warm
        else:
            icon_map = self.icon_map_day_dark_red
        isDay = True
        if self.current is not None:
            isDay = self.current.get("isDay")
        if isDay is False:
            if color == ColorStyle.WHITE_WARM:
                icon_map = self.icon_map_night_white_warm
            else:
                icon_map = self.icon_map_night_dark_red

        return icon_map.get(code, icon_map.get("fallback"))
