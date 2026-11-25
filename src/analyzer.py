"""Forecast analysis with pandas: turn raw rows into a compact summary."""
import math
import pandas as pd


def clean(v):
    """NaN/None -> None, otherwise float."""
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    return float(v)


def to_frames(data: dict):
    hourly = pd.DataFrame(data["hourly"])
    hourly["time"] = pd.to_datetime(hourly["time"])
    daily = pd.DataFrame(data["daily"])
    for col in hourly.columns.drop("time"):
        hourly[col] = pd.to_numeric(hourly[col], errors="coerce")
    for col in daily.columns.drop("date"):
        daily[col] = pd.to_numeric(daily[col], errors="coerce")
    return hourly, daily


def analyze(data: dict) -> dict:
    hourly, daily = to_frames(data)
    start = hourly["time"].iloc[0]
    w24 = hourly[hourly["time"] < start + pd.Timedelta(hours=24)]
    w12 = hourly[hourly["time"] < start + pd.Timedelta(hours=12)]
    gust = clean(w24["gust_ms"].max())
    if gust is None:  # some providers give no gust value -> use sustained wind
        gust = clean(w24["wind_ms"].max())
    return {
        "temp_max": clean(w24["temp_c"].max()),
        "temp_min": clean(w24["temp_c"].min()),
        "humidity_avg": clean(w24["humidity"].mean()),
        "wind_max": clean(w24["wind_ms"].max()),
        "gust_max": gust,
        "rain_total_mm": clean(w24["precip_mm"].sum()),
        "hourly_rain_max_mm": clean(w24["precip_mm"].max()),
        "rain_prob_max_12h": clean(w12["precip_prob"].max()),
        "tmax_today": clean(daily["tmax_c"].iloc[0]) if len(daily) else None,
        "tmax_tomorrow": clean(daily["tmax_c"].iloc[1]) if len(daily) > 1 else None,
        "uv_today": clean(daily["uv_max"].iloc[0]) if len(daily) and "uv_max" in daily else None,
        "daily_rain_mm_7d": clean(daily["rain_mm"].sum()),
    }
