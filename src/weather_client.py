"""Real API mode: Open-Meteo (no key) and OpenWeatherMap (free key).

Both providers are converted into the same normalised dict:
 {city, lat, lon, source, current{}, hourly[], daily[]}
Units: Celsius, mm, m/s, % .
"""
import csv
from collections import defaultdict
import requests
from .config import CITIES_CSV, OPENWEATHER_API_KEY


class WeatherError(Exception):
    """Friendly, user-readable API problem."""


WMO = {0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast", 45: "Fog", 48: "Fog",
       51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle", 61: "Light rain", 63: "Rain", 65: "Heavy rain",
       71: "Light snow", 73: "Snow", 75: "Heavy snow", 80: "Rain showers", 81: "Rain showers",
       82: "Violent rain showers", 95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with hail"}


def _get(url: str, params: dict) -> dict:
    try:
        r = requests.get(url, params=params, timeout=15)
    except requests.exceptions.ConnectionError:
        raise WeatherError("No internet connection (or server unreachable). Try  --mode simulate")
    except requests.exceptions.Timeout:
        raise WeatherError("The weather API timed out. Try again.")
    if r.status_code == 401:
        raise WeatherError("Invalid API key (401). Check OPENWEATHER_API_KEY in your .env file.")
    if r.status_code == 404:
        raise WeatherError("City not found (404). Check the spelling.")
    if r.status_code == 429:
        raise WeatherError("API rate limit reached (429). Wait a bit and retry.")
    try:
        r.raise_for_status()
        return r.json()
    except (requests.exceptions.HTTPError, ValueError) as e:
        raise WeatherError(f"Unexpected API response: {e}")


def _item(block: dict, key: str, i: int):
    values = block.get(key)
    return values[i] if values and i < len(values) else None


# ---------------- location lookup ----------------
def geocode(city: str):
    """Return (lat, lon, tz). Checks data/cities.csv first, then Open-Meteo geocoding."""
    if CITIES_CSV.exists():
        with open(CITIES_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["city"].lower() == city.strip().lower():
                    return float(row["lat"]), float(row["lon"]), row["tz"]
    data = _get("https://geocoding-api.open-meteo.com/v1/search", {"name": city, "count": 1})
    results = data.get("results")
    if not results:
        raise WeatherError(f'City "{city}" not found. Check the spelling.')
    r = results[0]
    return r["latitude"], r["longitude"], r.get("timezone", "auto")


# ---------------- Open-Meteo ----------------
def parse_open_meteo(raw: dict, city: str, lat: float, lon: float) -> dict:
    cur, h, d = raw.get("current", {}), raw["hourly"], raw["daily"]
    hourly = []
    for i, t in enumerate(h["time"]):
        hourly.append(dict(
            time=t, temp_c=_item(h, "temperature_2m", i), humidity=_item(h, "relative_humidity_2m", i),
            wind_ms=_item(h, "wind_speed_10m", i), gust_ms=_item(h, "wind_gusts_10m", i),
            precip_mm=_item(h, "precipitation", i), precip_prob=_item(h, "precipitation_probability", i)))
    if cur.get("time"):  # hourly data starts at midnight; keep only from the current hour
        start = cur["time"][:13] + ":00"
        hourly = [r for r in hourly if r["time"] >= start]
    hourly = hourly[:48]
    daily = [dict(date=t, tmax_c=_item(d, "temperature_2m_max", i), tmin_c=_item(d, "temperature_2m_min", i),
                  rain_mm=_item(d, "precipitation_sum", i), rain_prob=_item(d, "precipitation_probability_max", i),
                  wind_max_ms=_item(d, "wind_speed_10m_max", i), uv_max=_item(d, "uv_index_max", i))
             for i, t in enumerate(d["time"])][:7]
    current = dict(temp_c=cur.get("temperature_2m"), humidity=cur.get("relative_humidity_2m"),
                   wind_ms=cur.get("wind_speed_10m"), precip_mm=cur.get("precipitation", 0),
                   description=WMO.get(cur.get("weather_code"), "Unknown"))
    return dict(city=city, lat=lat, lon=lon, source="open-meteo", current=current, hourly=hourly, daily=daily)


def fetch_open_meteo(city: str) -> dict:
    lat, lon, tz = geocode(city)
    raw = _get("https://api.open-meteo.com/v1/forecast", {
        "latitude": lat, "longitude": lon, "timezone": "auto", "forecast_days": 7, "wind_speed_unit": "ms",
        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
        "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,precipitation,wind_speed_10m,wind_gusts_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max,uv_index_max"})
    return parse_open_meteo(raw, city.title(), lat, lon)


# ---------------- OpenWeatherMap ----------------
def parse_openweathermap(cur_raw: dict, fc_raw: dict, city: str) -> dict:
    current = dict(temp_c=cur_raw["main"]["temp"], humidity=cur_raw["main"]["humidity"],
                   wind_ms=cur_raw.get("wind", {}).get("speed", 0),
                   precip_mm=(cur_raw.get("rain") or {}).get("1h", 0),
                   description=cur_raw["weather"][0]["description"].title())
    items = fc_raw["list"]  # 3-hourly steps in UTC
    hourly = [dict(time=it["dt_txt"].replace(" ", "T")[:16], temp_c=it["main"]["temp"],
                   humidity=it["main"]["humidity"], wind_ms=it["wind"].get("speed"), gust_ms=it["wind"].get("gust"),
                   precip_mm=(it.get("rain") or {}).get("3h", 0), precip_prob=round(it.get("pop", 0) * 100))
              for it in items[:16]]
    days = defaultdict(list)
    for it in items:
        days[it["dt_txt"][:10]].append(it)
    daily = [dict(date=day, tmax_c=max(i["main"]["temp"] for i in its), tmin_c=min(i["main"]["temp"] for i in its),
                  rain_mm=round(sum((i.get("rain") or {}).get("3h", 0) for i in its), 1),
                  rain_prob=round(max(i.get("pop", 0) for i in its) * 100),
                  wind_max_ms=max(i["wind"].get("speed", 0) for i in its), uv_max=None)
             for day, its in sorted(days.items())]
    coord = cur_raw.get("coord", {})
    return dict(city=city, lat=coord.get("lat"), lon=coord.get("lon"), source="openweathermap",
                current=current, hourly=hourly, daily=daily)


def fetch_openweathermap(city: str) -> dict:
    if not OPENWEATHER_API_KEY:
        raise WeatherError("OPENWEATHER_API_KEY is not set. Copy .env.example to .env and add your key.")
    p = {"q": city, "appid": OPENWEATHER_API_KEY, "units": "metric"}
    cur = _get("https://api.openweathermap.org/data/2.5/weather", p)
    fc = _get("https://api.openweathermap.org/data/2.5/forecast", p)
    return parse_openweathermap(cur, fc, city.title())


def fetch(city: str, provider: str = "open-meteo") -> dict:
    return fetch_openweathermap(city) if provider == "openweathermap" else fetch_open_meteo(city)
