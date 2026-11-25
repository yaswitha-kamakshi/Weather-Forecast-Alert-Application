# 🌦️ Weather Forecast & Alert Application

A beginner-friendly **Python project** that fetches (or simulates) weather for Indian cities, analyses the next 24 hours and 7 days with pandas, applies a **rule engine** to raise rain, heat, wind/storm, humidity and UV alerts, and saves CSV data, text reports and charts. It has an optional **Streamlit dashboard**.

It works **offline in simulation mode** (no API key needed) and with **real data** from Open-Meteo (free, no key) or OpenWeatherMap (free key).

## Problem Statement
Checking forecasts by hand is slow, and the important details (a heavy-rain hour, a heat spike, storm gusts) are easy to miss. This project turns raw forecast numbers into clear, prioritised alerts and saved reports.

## Industry Relevance
Logistics (route planning), agriculture (irrigation windows), events (go/no-go), energy and construction (safety), travel and public safety. The same pipeline (ingest → normalise → analyse → rules → notify) is used in real monitoring products.

## Features
- Two modes: **simulation** (offline, 5 cities with different scenarios) and **api** (live data)
- Two providers behind one normalised format: Open-Meteo and OpenWeatherMap
- pandas analysis of the next 24h and a 7-day outlook
- Alert rules: extreme/high heat, likely/heavy rain, strong wind/storm, high humidity, high UV, with `critical / warn / info` severity
- Adjustable thresholds from the command line or dashboard sliders
- Friendly handling of bad city names, invalid API keys, rate limits and no internet
- Outputs: forecast CSV, alerts CSV, text report, 3-panel Matplotlib chart
- Optional email notification (dry-run preview if SMTP isn't configured)
- Streamlit dashboard, 12 unit tests (including provider-parser tests with canned API data)

## Tech Stack
Python 3.9+, requests, JSON, pandas, Matplotlib, datetime, argparse, python-dotenv, Streamlit, unittest

## Folder Structure
```
Weather-Forecast-Alert-Application/
├── data/        cities.csv (city → lat/lon), sample_weather.json (simulated snapshot)
├── src/         config, simulator, weather_client, analyzer, alerts, notifier, reporter
├── outputs/     forecast CSVs, alerts CSV, chart PNGs
├── reports/     text reports
├── images/      screenshots for this README
├── docs/        guides and interview prep
├── tests/       unit tests
├── main.py      command-line entry point
├── dashboard.py Streamlit dashboard
├── requirements.txt
├── .env.example
└── .gitignore
```

## Setup
```bash
git clone https://github.com/<your-username>/Weather-Forecast-Alert-Application.git
cd Weather-Forecast-Alert-Application

# Windows
python -m venv venv
venv\Scripts\activate
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

## API Setup
- **Open-Meteo (default):** no key needed. Just run `--mode api`.
- **OpenWeatherMap (optional):** create a free key at openweathermap.org, then `cp .env.example .env` (Windows: `copy .env.example .env`) and paste the key into `OPENWEATHER_API_KEY`. Never commit `.env`.

## How to Run
```bash
python main.py                                  # simulation, all 5 cities
python main.py --city Mumbai                    # one city
python main.py --mode api --city Delhi          # live data (Open-Meteo)
python main.py --mode api --provider openweathermap --city Delhi
python main.py --heat-warn 30 --rain-prob 40    # custom thresholds
python main.py --notify                         # email alerts (dry-run preview without SMTP)
streamlit run dashboard.py                      # dashboard
python -m unittest discover -s tests            # tests
```

## Sample Output
```
==============================================================
 MUMBAI   [simulation]
==============================================================
 CURRENT   28.4°C | Thunderstorm | humidity 84% | wind 9.0 m/s
 NEXT 24H  temp 24°C to 28°C | avg humidity 93%
           max gust 23.0 m/s | total rain 144.0 mm | rain chance (12h) 92%
 ALERTS
   🔴 CRITICAL Heavy rain: up to 12 mm/hour. Flooding possible.
   🔴 CRITICAL Storm-force gusts of 23 m/s (83 km/h). Secure loose objects.
   🔵 INFO     High humidity: averaging 93% over the next 24h.

 SUMMARY: 5 city(ies) | 9 alert(s): 3 critical, 4 warning, 2 info
```

## Screenshots
![Terminal output](images/terminal_output.png)
![Chart](images/chart.png)
![Dashboard](images/dashboard.png)

## Learning Outcomes
REST API integration with `requests` · JSON parsing and normalising two different provider formats · pandas time-window analysis · rule-based alert design · error handling · data visualisation · secret management · writing testable code (parsers tested without network) · Git/GitHub workflow

## Future Improvements
AQI alerts, SQLite history + caching, scheduled refresh (cron/APScheduler), Telegram/SMS alerts, map layer, FastAPI service, Docker

> ⚠️ Educational project. Simulated data is fictional; do not use it for real safety decisions. Always follow official weather warnings.

## 👩‍💻 Author

**Yaswitha Kamakshi V.**

B.Tech – Computer Science and Engineering

GitHub: https://github.com/yaswitha-kamakshi

LinkedIn: https://www.linkedin.com/in/yaswitha-kamakshi-292b5242b/

---
