# GitHub Upload & Proof-Building Plan

## Repository details
- **Name:** `Weather-Forecast-Alert-Application`
- **Description:** Python weather forecast and alert system: live (Open-Meteo/OpenWeatherMap) or simulated data, pandas analysis, rule-based alerts, reports, charts and Streamlit dashboard.
- **Topics:** `python` `weather` `weather-api` `open-meteo` `alert-system` `pandas` `matplotlib` `streamlit` `automation` `portfolio-project`

## Steps
1. GitHub → **New repository** → name above → Public → leave README/.gitignore/license **unchecked** → Create.
2. In the folder that contains `main.py`:
```powershell
git init
git add .
git status          # CHECK: .env and venv/ must NOT be listed
git commit -m "feat: initial project with simulation mode and alert engine"
git branch -M main
git remote add origin https://github.com/<your-username>/Weather-Forecast-Alert-Application.git
git push -u origin main
```
3. Later: `git add .` → `git commit -m "..."` → `git push`.
4. Screenshots: save with clean names (Windows can add `.png.png`; check the file names), then `git add images`, commit, push.

### Security rules
Never commit API keys. Use `.env` locally and `.env.example` in the repo. If a key leaks, revoke it on the provider's site immediately; deleting the file later does not remove it from Git history.

## Day-wise proof plan
| Day | Work | Commit message | Screenshots |
|---|---|---|---|
| 1 | Setup, folders, `.gitignore`, `.env.example`, `requirements.txt` | `chore: project scaffold` | `project_structure.png` |
| 2 | `weather_client.py` (Open-Meteo + OpenWeatherMap), geocoding, error handling | `feat: weather API clients with error handling` | API-mode output (if you have internet) |
| 3 | Parsing/normalising, `simulator.py`, `analyzer.py` | `feat: normalised data, simulation mode, pandas analysis` | `terminal_output.png` |
| 4 | `alerts.py` rules and thresholds, `notifier.py`, tests | `feat: alert rule engine and tests` | `alert_output.png` |
| 5 | `reporter.py` (CSV, text, chart), `dashboard.py` | `feat: reports, charts and Streamlit dashboard` | `chart.png`, `report_txt.png`, `dashboard.png` |
| 6 | README, docs, final push, pin repo | `docs: README, guides and screenshots` | `github_repo.png` |
