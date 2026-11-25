# Simulation & How to Run

## How the simulation works
`src/simulator.py` builds 48 hourly rows and a 7-day outlook for five cities, each with a different scenario, relative to the current time:

| City | Scenario | Expected alerts |
|---|---|---|
| Visakhapatnam | Monsoon showers, very humid | Rain likely, high humidity |
| Delhi | Heat wave, clear sky | Extreme heat, high UV |
| Mumbai | Thunderstorm | Heavy rain, storm-force wind, high humidity |
| Bengaluru | Pleasant weather | None (shows the "all clear" case) |
| Chennai | Hot and humid | High temperature, high UV |

The data has exactly the same structure as the API clients produce, so analysis, alerts, reports and charts run identically in both modes.

**City-wise representation:** a dict with `city, lat, lon, source, current{}, hourly[], daily[]`. Hourly rows hold `time, temp_c, humidity, wind_ms, gust_ms, precip_mm, precip_prob`. Daily rows hold `date, tmax_c, tmin_c, rain_mm, rain_prob, wind_max_ms, uv_max`.

**Threshold checks (defaults):** heat warn 35°C, critical 40°C · rain chance ≥ 60% in 12h · heavy rain ≥ 10 mm/hour · humidity ≥ 85% (24h average) · gust warn 15 m/s, storm 20 m/s · UV ≥ 8. Change them with flags such as `--heat-warn 30`.

**In real life:** a scheduler (cron/APScheduler) would fetch every 1-3 hours, store results in a database, run the same rules, send alerts by SMS/email/Telegram with de-duplication, and feed a dashboard.

## Commands
```bash
python main.py                                   # simulation, all cities
python main.py --city Mumbai,Delhi               # chosen cities
python main.py --generate-sample-data            # write data/sample_weather.json
python main.py --mode api --city Delhi           # live Open-Meteo (no key)
python main.py --mode api --provider openweathermap --city Delhi   # needs key in .env
python main.py --heat-warn 30 --rain-prob 40     # custom thresholds
python main.py --notify                          # email (dry-run preview unless SMTP is set)
streamlit run dashboard.py
python -m unittest discover -s tests             # 12 tests
```
Expected terminal output: one block per city (CURRENT, NEXT 24H, 7-DAY, ALERTS) then a SUMMARY box (see README).

## Generated files
- `outputs/forecast_<City>_<time>.csv` hourly forecast
- `outputs/alerts_<time>.csv` all alerts of the run
- `outputs/chart_<City>_<time>.png` temperature, humidity and rain chart
- `reports/weather_report_<time>.txt` readable summary

## API mode troubleshooting
| Message | Meaning / fix |
|---|---|
| No internet connection | Check Wi-Fi/firewall, or use `--mode simulate` |
| City not found (404) | Check the spelling |
| Invalid API key (401) | Fix `OPENWEATHER_API_KEY`; new keys can take up to an hour to activate |
| Rate limit (429) | Wait and retry |

## Screenshots to capture (save in `images/`)
1. `project_structure.png`: Explorer with folders expanded
2. `terminal_output.png`: `python main.py` output (current weather, forecast summary, alerts)
3. `alert_output.png`: a city with CRITICAL alerts (e.g. `--city Mumbai`)
4. `report_txt.png`: a file from `reports/`
5. `alerts_csv.png`: the alerts CSV
6. `chart.png`: a chart from `outputs/`
7. `dashboard.png`: Streamlit dashboard
8. `github_repo.png`: repo page after pushing

## Upload to GitHub ✅ / never upload ❌
✅ code, simulated data, sample outputs/reports, screenshots, `.env.example`
❌ `.env`, real API keys, SMTP/App passwords, screenshots that show a key or inbox
