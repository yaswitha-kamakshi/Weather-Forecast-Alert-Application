"""Weather Forecast & Alert Application - entry point.

Examples:
  python main.py --generate-sample-data              # snapshot of simulated data
  python main.py                                     # simulation mode, all 5 sample cities
  python main.py --city Mumbai                       # one city (simulation)
  python main.py --mode api --city Delhi             # real data from Open-Meteo (no key)
  python main.py --mode api --provider openweathermap --city Delhi   # needs OPENWEATHER_API_KEY
  python main.py --heat-warn 30 --rain-prob 40       # custom thresholds
"""
import argparse
import sys

from src.alerts import Thresholds, evaluate, ICON
from src.analyzer import analyze
from src.notifier import send_email
from src.reporter import (fmt, new_stamp, save_alerts_csv, save_chart, save_forecast_csv, save_text_report)
from src.simulator import available_cities, generate_sample_file, load_city
from src.weather_client import WeatherError, fetch


def parse_args():
    p = argparse.ArgumentParser(description="Weather Forecast & Alert Application")
    p.add_argument("--mode", choices=["simulate", "api"], default="simulate", help="simulate (default, offline) or api (live data)")
    p.add_argument("--city", default="", help='City name, comma-separated list, or "all" (default: all in simulate mode, Delhi in api mode)')
    p.add_argument("--provider", choices=["open-meteo", "openweathermap"], default="open-meteo")
    p.add_argument("--no-chart", action="store_true", help="skip PNG chart creation")
    p.add_argument("--notify", action="store_true", help="email alerts (dry-run preview if SMTP not configured)")
    p.add_argument("--generate-sample-data", action="store_true", help="write data/sample_weather.json and exit")
    d = Thresholds()
    p.add_argument("--heat-warn", type=float, default=d.heat_warn_c)
    p.add_argument("--heat-critical", type=float, default=d.heat_critical_c)
    p.add_argument("--rain-prob", type=float, default=d.rain_prob_pct)
    p.add_argument("--heavy-rain", type=float, default=d.heavy_rain_mm_per_h)
    p.add_argument("--humidity", type=float, default=d.humidity_pct)
    p.add_argument("--wind", type=float, default=d.wind_warn_ms)
    p.add_argument("--storm", type=float, default=d.storm_wind_ms)
    p.add_argument("--uv", type=float, default=d.uv_index)
    return p.parse_args()


def print_city(data, summary, alerts):
    c = data["current"]
    print("\n" + "=" * 62)
    print(f" {data['city'].upper()}   [{data['source']}]")
    print("=" * 62)
    print(f" CURRENT   {fmt(c['temp_c'], '°C', 1)} | {c['description']} | humidity {fmt(c['humidity'], '%')} | wind {fmt(c['wind_ms'], ' m/s', 1)}")
    print(f" NEXT 24H  temp {fmt(summary['temp_min'], '°C')} to {fmt(summary['temp_max'], '°C')} | avg humidity {fmt(summary['humidity_avg'], '%')}")
    print(f"           max gust {fmt(summary['gust_max'], ' m/s', 1)} | total rain {fmt(summary['rain_total_mm'], ' mm', 1)} | rain chance (12h) {fmt(summary['rain_prob_max_12h'], '%')}")
    print(" 7-DAY     " + "  ".join(f"{d['date'][5:]}:{fmt(d['tmax_c'], '°')}/{fmt(d['rain_mm'], 'mm')}" for d in data["daily"][:7]))
    print(" ALERTS")
    if alerts:
        for a in alerts:
            print(f"   {ICON[a['severity']]} {a['severity'].upper():<8} {a['message']}")
    else:
        print("   ✅ No alerts. Conditions are normal.")


def main():
    args = parse_args()
    if args.generate_sample_data:
        generate_sample_file()
        return

    th = Thresholds(args.heat_warn, args.heat_critical, args.rain_prob, args.heavy_rain,
                    args.humidity, args.wind, args.storm, args.uv)

    if args.mode == "simulate":
        raw = args.city or "all"
        cities = available_cities() if raw.lower() == "all" else [c.strip() for c in raw.split(",") if c.strip()]
    else:
        cities = [c.strip() for c in (args.city or "Delhi").split(",") if c.strip()]

    stamp = new_stamp()
    results, errors = [], []
    for city in cities:
        try:
            data = load_city(city) if args.mode == "simulate" else fetch(city, args.provider)
        except (KeyError, WeatherError) as e:
            msg = e.args[0] if e.args else str(e)
            print(f"\n[ERROR] {city}: {msg}")
            errors.append(city)
            continue
        summary = analyze(data)
        alerts = evaluate(data["city"], summary, th)
        print_city(data, summary, alerts)
        results.append(dict(data=data, summary=summary, alerts=alerts))
        save_forecast_csv(data, stamp)
        if not args.no_chart:
            save_chart(data, th, stamp)

    if not results:
        sys.exit("\nNo city could be processed.")

    all_alerts = [a for r in results for a in r["alerts"]]
    alerts_csv = save_alerts_csv(all_alerts, stamp)
    report = save_text_report(results, th, stamp)

    if args.notify:
        print("\n" + send_email(all_alerts))

    crit = sum(a["severity"] == "critical" for a in all_alerts)
    warn = sum(a["severity"] == "warn" for a in all_alerts)
    info = sum(a["severity"] == "info" for a in all_alerts)
    print("\n" + "=" * 62)
    print(f" SUMMARY: {len(results)} city(ies) | {len(all_alerts)} alert(s): {crit} critical, {warn} warning, {info} info")
    print(f" Alerts CSV : {alerts_csv}")
    print(f" Report     : {report}")
    print(" Charts/CSV : outputs/")
    print("=" * 62)


if __name__ == "__main__":
    main()
