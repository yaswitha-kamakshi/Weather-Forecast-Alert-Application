# 1. Project Guide

## What is a Weather Forecast & Alert Application?
**Simple:** a program that looks up the weather for a city and warns you when something important is coming: heavy rain, extreme heat, strong wind.
**Technical:** a pipeline that ingests forecast data from a weather API (JSON over HTTP), normalises it into one internal format, analyses time windows with pandas, evaluates threshold-based rules, and outputs alerts, reports and charts. Providers are swappable because everything downstream uses the same normalised structure.

## Problem it solves
Raw forecasts are long tables of numbers. People miss the one hour of heavy rain or the heat spike. Alerts turn data into decisions.

## Who benefits
| Group | Use |
|---|---|
| Everyday users / travelers | Umbrella, packing, flight and road-trip decisions |
| Farmers | Irrigation and spraying windows, heat/frost risk |
| Logistics | Reroute or delay deliveries for storms and floods |
| Event planners | Go/no-go and backup plans for outdoor events |
| Businesses | Protect staff and assets, avoid downtime |

## How weather apps get live data
The app sends an HTTP GET request to a weather API with a location (lat/lon or city). The API replies with JSON. The app parses it, converts units, and stores or displays it. Free APIs: Open-Meteo (no key), OpenWeatherMap (free key). Keys are secrets and belong in `.env`.

## How alerts are generated
A rule compares a summary value with a threshold: `max temperature >= 40°C → CRITICAL heat`, `rain chance in next 12h >= 60% → WARN rain`, `gust >= 20 m/s → CRITICAL storm`, `average humidity >= 85% → INFO`. Rules are ordered by severity so the most dangerous appear first.

## Workflow
```
user enters city → weather API fetches data → data processing → forecast analysis → alert condition check → display output → save report
```

# 2. Tech stack options
| | A: Easy | B: Intermediate ⭐ (implemented) | C: Advanced |
|---|---|---|---|
| Tools | requests, json, print | requests, pandas, Matplotlib, argparse, dotenv, simulation mode, Streamlit (optional), unittest | FastAPI, SQLite/Postgres, APScheduler, Docker, Next.js + Recharts/Leaflet, Telegram/Twilio |
| Difficulty | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| Output | Current weather printed | Forecast analysis, alerts, CSV/text reports, charts, dashboard | REST API, DB history, scheduled alerts, map dashboard, notifications |
| Time | 1 day | 4-6 days | 3-4 weeks |

**Best for students: Option B.** It runs offline, shows real API skills and professional habits (modular code, tests, secrets handling) and upgrades naturally to Option C.

# 3. Architecture
```
 INPUT                      PROCESSING                                        OUTPUT
┌───────────────┐   ┌─────────────────────────────────────────────┐   ┌──────────────────────┐
│ city name     │   │ weather_client / simulator → normalised dict │   │ current weather      │
│ mode + provider──▶│ analyzer (pandas)  → 24h / 7-day summary     │──▶│ forecast summary     │
│ thresholds    │   │ alerts (rule engine) → critical/warn/info    │   │ alert messages       │
│ .env API key  │   │ notifier (optional email)                    │   │ CSV + text + chart   │
└───────────────┘   └─────────────────────────────────────────────┘   └──────────────────────┘
```
**Data flow:** `main.py` picks simulation or API → client returns `{city, current, hourly[], daily[]}` → `analyze()` computes max/min temperature, average humidity, max gust, total rain, 12h rain chance → `evaluate()` compares with `Thresholds` → results are printed and saved by `reporter`.

# 4. Implementation plan (10 phases)
| # | Phase | What / why | Expected output | Beginner mistakes |
|---|---|---|---|---|
| 1 | Setup | Python, VS Code, Git, venv. Isolated environment. | `python --version` works | Not activating the venv |
| 2 | Folder creation | Separate code, data, outputs, reports. | Folder tree + `.gitignore` | One giant file |
| 3 | API key setup | Open-Meteo needs none; OpenWeatherMap key goes in `.env`. | `.env` (local only) | Pasting the key into code; committing `.env`; using a key before it activates (can take ~1h) |
| 4 | Data fetching | `requests.get(url, params, timeout)`. | Raw JSON | No timeout; no status-code checks |
| 5 | JSON parsing | Pull fields into a common format with unit conversions (m/s, °C, mm). | Normalised dict | Assuming a field always exists |
| 6 | Forecast analysis | pandas time windows (next 12h/24h). | Summary dict | Mixing units; forgetting NaN values |
| 7 | Alert logic | Threshold rules with severity. | Alert list | Hard-coding thresholds; alert spam |
| 8 | Visualisation | Matplotlib charts with threshold lines. | PNG chart | Not closing figures; unreadable axes |
| 9 | Reports | CSV + text report per run. | `outputs/`, `reports/` | Overwriting old reports (we timestamp them) |
| 10 | GitHub upload | Commit, push, README, screenshots. | Public repo | Committing `.env` |

# 5. Folder structure explained
`data/` city coordinates and simulated snapshot · `src/` one module per job · `outputs/` CSVs and charts · `reports/` human-readable text reports · `images/` README screenshots · `docs/` guides · `tests/` unit tests · `main.py` CLI · `dashboard.py` Streamlit · `.env.example` safe config template · `.gitignore` keeps secrets out of Git.

# 6. Installation
1. Install Python 3.9+ (Windows: tick **Add Python to PATH**). Check with `python --version`.
2. Create and activate a venv. Windows: `python -m venv venv` then `venv\Scripts\activate`. Mac/Linux: `python3 -m venv venv` then `source venv/bin/activate`.
3. `pip install -r requirements.txt`
4. Optional (OpenWeatherMap only): copy `.env.example` to `.env` and add your key. Open-Meteo needs nothing.
5. **Never upload your key:** `.env` is in `.gitignore`; run `git status` before every push and confirm `.env` is not listed. If a key ever leaks, delete it on the provider's website and create a new one.

# Upgrade path to Option C (from the project PDF)
Replace in-memory results with SQLite tables (`locations`, `weather_hourly`, `weather_daily`), add FastAPI endpoints (`/forecast/hourly`, `/alerts`), schedule `refresh_all()` with cron/APScheduler, add a 12-hour alert debounce log, and swap the Streamlit dashboard for Next.js + Recharts. Our `weather_client`, `analyzer` and `alerts` modules map directly onto the PDF's `ingest`, `rules` and API layers.
