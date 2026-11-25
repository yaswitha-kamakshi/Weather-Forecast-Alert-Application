import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.alerts import Thresholds, evaluate
from src.analyzer import analyze
from src.simulator import available_cities, load_city
from src.weather_client import parse_open_meteo, parse_openweathermap

OPEN_METEO_SAMPLE = {
    "current": {"time": "2026-11-24T10:15", "temperature_2m": 31.2, "relative_humidity_2m": 55,
                "precipitation": 0.0, "wind_speed_10m": 3.1, "weather_code": 2},
    "hourly": {"time": ["2026-11-24T08:00", "2026-11-24T10:00", "2026-11-24T11:00"],
               "temperature_2m": [29, 31, 32], "relative_humidity_2m": [60, 55, 52],
               "precipitation_probability": [10, 20, 70], "precipitation": [0, 0, 1.5],
               "wind_speed_10m": [2, 3, 3], "wind_gusts_10m": [4, 6, 9]},
    "daily": {"time": ["2026-11-24", "2026-11-25"], "temperature_2m_max": [34, 36], "temperature_2m_min": [22, 23],
              "precipitation_sum": [1.5, 0], "precipitation_probability_max": [70, 10],
              "wind_speed_10m_max": [9, 5], "uv_index_max": [8.5, 7]},
}

OWM_CURRENT = {"coord": {"lat": 28.6, "lon": 77.2}, "main": {"temp": 30.5, "humidity": 40},
               "wind": {"speed": 2.5}, "weather": [{"description": "haze"}]}
OWM_FORECAST = {"list": [
    {"dt_txt": "2026-11-24 12:00:00", "main": {"temp": 31, "humidity": 40}, "wind": {"speed": 3, "gust": 5}, "pop": 0.1},
    {"dt_txt": "2026-11-24 15:00:00", "main": {"temp": 33, "humidity": 35}, "wind": {"speed": 4}, "pop": 0.8, "rain": {"3h": 2.0}},
    {"dt_txt": "2026-11-25 12:00:00", "main": {"temp": 28, "humidity": 50}, "wind": {"speed": 2}, "pop": 0.0}]}


class AlertTests(unittest.TestCase):
    def codes(self, city):
        return {a["code"] for a in evaluate(city, analyze(load_city(city)))}

    def test_delhi_heat_wave(self):
        self.assertIn("HEAT_EXTREME", self.codes("Delhi"))

    def test_mumbai_storm_and_heavy_rain(self):
        c = self.codes("Mumbai")
        self.assertTrue({"STORM_WIND", "RAIN_HEAVY"} <= c)

    def test_visakhapatnam_rain_and_humidity(self):
        c = self.codes("Visakhapatnam")
        self.assertTrue({"RAIN_LIKELY", "HUMIDITY_HIGH"} <= c)

    def test_bengaluru_has_no_alerts(self):
        self.assertEqual(self.codes("Bengaluru"), set())

    def test_custom_threshold_changes_result(self):
        s = analyze(load_city("Bengaluru"))
        alerts = evaluate("Bengaluru", s, Thresholds(heat_warn_c=20, heat_critical_c=50))
        self.assertIn("HEAT_HIGH", {a["code"] for a in alerts})

    def test_critical_sorted_first(self):
        sev = [a["severity"] for a in evaluate("Mumbai", analyze(load_city("Mumbai")))]
        self.assertEqual(sev[0], "critical")

    def test_missing_values_do_not_crash(self):
        self.assertEqual(evaluate("X", {}), [])


class SimulatorTests(unittest.TestCase):
    def test_all_cities_have_48_hours_and_7_days(self):
        for c in available_cities():
            d = load_city(c)
            self.assertEqual(len(d["hourly"]), 48)
            self.assertEqual(len(d["daily"]), 7)

    def test_case_insensitive_and_unknown_city(self):
        self.assertEqual(load_city("delhi")["city"], "Delhi")
        with self.assertRaises(KeyError):
            load_city("Atlantis")


class ParserTests(unittest.TestCase):
    def test_open_meteo_parser_filters_past_hours(self):
        d = parse_open_meteo(OPEN_METEO_SAMPLE, "Delhi", 28.6, 77.2)
        self.assertEqual(len(d["hourly"]), 2)  # 08:00 is before current hour 10:00
        self.assertEqual(d["current"]["description"], "Partly cloudy")
        self.assertEqual(d["daily"][0]["uv_max"], 8.5)

    def test_open_meteo_end_to_end_alerts(self):
        d = parse_open_meteo(OPEN_METEO_SAMPLE, "Delhi", 28.6, 77.2)
        codes = {a["code"] for a in evaluate("Delhi", analyze(d))}
        self.assertIn("RAIN_LIKELY", codes)
        self.assertIn("UV_HIGH", codes)

    def test_openweathermap_parser(self):
        d = parse_openweathermap(OWM_CURRENT, OWM_FORECAST, "Delhi")
        self.assertEqual(d["current"]["description"], "Haze")
        self.assertEqual(d["hourly"][1]["precip_prob"], 80)
        self.assertEqual(len(d["daily"]), 2)
        self.assertEqual(d["daily"][0]["rain_mm"], 2.0)
        self.assertIsNone(d["daily"][0]["uv_max"])
        analyze(d)  # must not crash when gust/uv are missing


if __name__ == "__main__":
    unittest.main()
