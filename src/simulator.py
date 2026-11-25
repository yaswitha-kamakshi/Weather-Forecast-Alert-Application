"""Simulation mode: realistic fake weather for 5 cities (no internet or API key needed).

Data uses the SAME normalised structure as the API clients, so everything
downstream (analysis, alerts, reports) works identically in both modes.
"""
import json
import math
from datetime import datetime, timedelta
from .config import SAMPLE_JSON, DATA_DIR

# rain = (start_hour, end_hour, probability %, mm per hour) counted from "now"
SCENARIOS = {
    "Visakhapatnam": dict(lat=17.69, lon=83.22, desc="Monsoon showers", tmean=28, tamp=2.5, hmean=88, wind=5, gust=13,
                          rain=(5, 20, 75, 3.0), tmax=[30, 29, 29, 30, 31, 31, 30], rain_daily=[22, 18, 6, 2, 0, 1, 4], uv=6),
    "Delhi": dict(lat=28.61, lon=77.21, desc="Heat wave, clear sky", tmean=38, tamp=5, hmean=28, wind=4, gust=8,
                  rain=(0, 0, 5, 0.0), tmax=[43, 44, 42, 41, 40, 39, 38], rain_daily=[0, 0, 0, 0, 0, 2, 5], uv=10),
    "Mumbai": dict(lat=19.08, lon=72.88, desc="Thunderstorm", tmean=27, tamp=1.5, hmean=90, wind=9, gust=23,
                   rain=(2, 14, 92, 12.0), tmax=[29, 28, 28, 29, 30, 30, 31], rain_daily=[85, 60, 25, 8, 3, 0, 1], uv=4),
    "Bengaluru": dict(lat=12.97, lon=77.59, desc="Pleasant, partly cloudy", tmean=25, tamp=3, hmean=60, wind=3, gust=6,
                      rain=(0, 0, 15, 0.0), tmax=[28, 28, 27, 28, 29, 28, 27], rain_daily=[0, 1, 0, 3, 2, 0, 0], uv=7),
    "Chennai": dict(lat=13.08, lon=80.27, desc="Hot and humid", tmean=33, tamp=4, hmean=82, wind=6, gust=11,
                    rain=(0, 0, 20, 0.0), tmax=[37, 38, 36, 36, 35, 35, 34], rain_daily=[0, 0, 4, 6, 0, 0, 2], uv=9),
}


def build_city(name: str, now: datetime = None) -> dict:
    s = SCENARIOS[name]
    now = (now or datetime.now()).replace(minute=0, second=0, microsecond=0)
    start, end, prob, mm = s["rain"]
    hourly = []
    for i in range(48):
        t = now + timedelta(hours=i)
        raining = start <= (i % 24) < end and end > 0
        temp = s["tmean"] + s["tamp"] * math.sin((t.hour - 9) / 24 * 2 * math.pi)
        if raining:
            temp -= 2
        humidity = min(98, s["hmean"] + (8 if raining else 0) - 6 * math.sin((t.hour - 9) / 24 * 2 * math.pi))
        gust = s["gust"] if raining else s["wind"] + (s["gust"] - s["wind"]) * 0.3
        hourly.append(dict(
            time=t.strftime("%Y-%m-%dT%H:%M"), temp_c=round(temp, 1), humidity=round(humidity),
            wind_ms=round(s["wind"] * (1.4 if raining else 1.0), 1), gust_ms=round(gust, 1),
            precip_mm=mm if raining else 0.0, precip_prob=prob if raining else 10))
    daily = []
    for d in range(7):
        day = (now + timedelta(days=d)).strftime("%Y-%m-%d")
        daily.append(dict(date=day, tmax_c=s["tmax"][d], tmin_c=round(s["tmean"] - s["tamp"] - 1, 1),
                          rain_mm=s["rain_daily"][d], rain_prob=min(95, s["rain_daily"][d] * 4 + 10),
                          wind_max_ms=s["gust"], uv_max=s["uv"]))
    first = hourly[0]
    return dict(city=name, lat=s["lat"], lon=s["lon"], source="simulation",
                current=dict(temp_c=first["temp_c"], humidity=first["humidity"], wind_ms=first["wind_ms"],
                             precip_mm=first["precip_mm"], description=s["desc"]),
                hourly=hourly, daily=daily)


def available_cities() -> list:
    return list(SCENARIOS)


def generate_sample_file() -> None:
    """Write data/sample_weather.json (a snapshot you can inspect or commit)."""
    DATA_DIR.mkdir(exist_ok=True)
    data = {c: build_city(c) for c in SCENARIOS}
    SAMPLE_JSON.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote {SAMPLE_JSON} with {len(data)} cities")


def load_city(name: str) -> dict:
    """Case-insensitive lookup. Always rebuilt relative to NOW so the demo never goes stale."""
    for key in SCENARIOS:
        if key.lower() == name.strip().lower():
            return build_city(key)
    raise KeyError(f'"{name}" is not in simulation data. Available: {", ".join(SCENARIOS)}')
