"""Save results: forecast CSV, alerts CSV, text report and a chart image."""
from datetime import datetime
import matplotlib
matplotlib.use("Agg")  # draw to files, no window needed
import matplotlib.pyplot as plt
import pandas as pd
from .analyzer import to_frames
from .config import OUTPUTS_DIR, REPORTS_DIR


def _stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_forecast_csv(data: dict, stamp: str):
    OUTPUTS_DIR.mkdir(exist_ok=True)
    hourly, _ = to_frames(data)
    path = OUTPUTS_DIR / f"forecast_{data['city'].replace(' ', '_')}_{stamp}.csv"
    hourly.to_csv(path, index=False)
    return path


def save_alerts_csv(alerts: list, stamp: str):
    OUTPUTS_DIR.mkdir(exist_ok=True)
    cols = ["city", "code", "severity", "message"]
    path = OUTPUTS_DIR / f"alerts_{stamp}.csv"
    pd.DataFrame(alerts, columns=cols).to_csv(path, index=False)
    return path


def save_chart(data: dict, th, stamp: str):
    OUTPUTS_DIR.mkdir(exist_ok=True)
    hourly, _ = to_frames(data)
    fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
    axes[0].plot(hourly["time"], hourly["temp_c"], color="tab:red", linewidth=2)
    axes[0].axhline(th.heat_warn_c, color="orange", linestyle="--", label=f"Heat warn {th.heat_warn_c:.0f}°C")
    axes[0].axhline(th.heat_critical_c, color="red", linestyle="--", label=f"Heat critical {th.heat_critical_c:.0f}°C")
    axes[0].set_ylabel("Temperature (°C)")
    axes[0].legend(loc="upper right", fontsize=8)
    axes[1].plot(hourly["time"], hourly["humidity"], color="tab:blue", linewidth=2)
    axes[1].axhline(th.humidity_pct, color="navy", linestyle="--", label=f"Humidity alert {th.humidity_pct:.0f}%")
    axes[1].set_ylabel("Humidity (%)")
    axes[1].legend(loc="upper right", fontsize=8)
    axes[2].bar(hourly["time"], hourly["precip_mm"].fillna(0), width=0.03, color="tab:cyan", label="Rain (mm)")
    axes[2].set_ylabel("Rain (mm)")
    twin = axes[2].twinx()
    twin.plot(hourly["time"], hourly["precip_prob"], color="gray", linestyle=":", label="Chance (%)")
    twin.set_ylabel("Rain chance (%)")
    axes[2].set_xlabel("Time")
    fig.suptitle(f"{data['city']}: next 48 hours ({data['source']})", fontsize=13)
    fig.autofmt_xdate()
    fig.tight_layout()
    path = OUTPUTS_DIR / f"chart_{data['city'].replace(' ', '_')}_{stamp}.png"
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return path


def fmt(v, unit="", digits=0):
    return "n/a" if v is None else f"{v:.{digits}f}{unit}"


def build_text_report(results: list, th) -> str:
    lines = ["WEATHER FORECAST & ALERT REPORT", f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}", "=" * 60]
    for r in results:
        d, s, c = r["data"], r["summary"], r["data"]["current"]
        lines += [f"\n{d['city'].upper()}  (source: {d['source']})", "-" * 60,
                  f"Now: {fmt(c['temp_c'], '°C', 1)}, {c['description']}, humidity {fmt(c['humidity'], '%')}, wind {fmt(c['wind_ms'], ' m/s', 1)}",
                  f"Next 24h: temp {fmt(s['temp_min'], '°C')} to {fmt(s['temp_max'], '°C')}, avg humidity {fmt(s['humidity_avg'], '%')}, "
                  f"max gust {fmt(s['gust_max'], ' m/s', 1)}, rain {fmt(s['rain_total_mm'], ' mm', 1)}",
                  "Alerts:"]
        lines += [f"  [{a['severity'].upper()}] {a['message']}" for a in r["alerts"]] or ["  None. Conditions are normal."]
    lines += ["\n" + "=" * 60, "Thresholds used: " + ", ".join(f"{k}={v}" for k, v in th.as_dict().items())]
    return "\n".join(lines)


def save_text_report(results: list, th, stamp: str):
    REPORTS_DIR.mkdir(exist_ok=True)
    path = REPORTS_DIR / f"weather_report_{stamp}.txt"
    path.write_text(build_text_report(results, th), encoding="utf-8")
    return path


def new_stamp():
    return _stamp()
