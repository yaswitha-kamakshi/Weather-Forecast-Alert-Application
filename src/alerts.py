"""Rule engine: compare the forecast summary with thresholds and create alerts."""
from dataclasses import dataclass, asdict

SEVERITY_ORDER = {"critical": 0, "warn": 1, "info": 2}
ICON = {"critical": "🔴", "warn": "🟠", "info": "🔵"}


@dataclass
class Thresholds:
    heat_warn_c: float = 35.0         # warn at/above this temperature
    heat_critical_c: float = 40.0     # critical at/above this temperature
    rain_prob_pct: float = 60.0       # "rain likely" if chance in next 12h >= this
    heavy_rain_mm_per_h: float = 10.0 # critical if any hour has this much rain
    humidity_pct: float = 85.0        # average humidity in next 24h
    wind_warn_ms: float = 15.0        # 15 m/s = 54 km/h
    storm_wind_ms: float = 20.0       # 20 m/s = 72 km/h
    uv_index: float = 8.0

    def as_dict(self):
        return asdict(self)


def _alert(city, code, severity, message):
    return {"city": city, "code": code, "severity": severity, "message": message}


def evaluate(city: str, s: dict, th: Thresholds = None) -> list:
    th = th or Thresholds()
    out = []

    temps = [v for v in (s.get("temp_max"), s.get("tmax_today"), s.get("tmax_tomorrow")) if v is not None]
    if temps:
        peak = max(temps)
        if peak >= th.heat_critical_c:
            out.append(_alert(city, "HEAT_EXTREME", "critical", f"Extreme heat: up to {peak:.0f}°C expected. Avoid outdoor work."))
        elif peak >= th.heat_warn_c:
            out.append(_alert(city, "HEAT_HIGH", "warn", f"High temperature: up to {peak:.0f}°C expected. Stay hydrated."))

    prob = s.get("rain_prob_max_12h")
    hour_mm = s.get("hourly_rain_max_mm")
    if hour_mm is not None and hour_mm >= th.heavy_rain_mm_per_h:
        out.append(_alert(city, "RAIN_HEAVY", "critical", f"Heavy rain: up to {hour_mm:.0f} mm/hour. Flooding possible."))
    elif prob is not None and prob >= th.rain_prob_pct:
        out.append(_alert(city, "RAIN_LIKELY", "warn", f"Rain likely in next 12h ({prob:.0f}% chance). Carry an umbrella."))

    gust = s.get("gust_max")
    if gust is not None:
        if gust >= th.storm_wind_ms:
            out.append(_alert(city, "STORM_WIND", "critical", f"Storm-force gusts of {gust:.0f} m/s ({gust * 3.6:.0f} km/h). Secure loose objects."))
        elif gust >= th.wind_warn_ms:
            out.append(_alert(city, "WIND_HIGH", "warn", f"Strong winds: gusts up to {gust:.0f} m/s ({gust * 3.6:.0f} km/h)."))

    hum = s.get("humidity_avg")
    if hum is not None and hum >= th.humidity_pct:
        out.append(_alert(city, "HUMIDITY_HIGH", "info", f"High humidity: averaging {hum:.0f}% over the next 24h."))

    uv = s.get("uv_today")
    if uv is not None and uv >= th.uv_index:
        out.append(_alert(city, "UV_HIGH", "warn", f"High UV index ({uv:.0f}). Use sunscreen and avoid midday sun."))

    return sorted(out, key=lambda a: SEVERITY_ORDER[a["severity"]])
