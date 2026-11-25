# Interview Preparation

### 1. Explain your project. ⭐
"I built a Weather Forecast & Alert Application in Python. The user chooses a city, and the app gets the forecast either from a live API (Open-Meteo or OpenWeatherMap) or from a built-in simulation mode that works offline. I convert both providers into one normalised format, analyse the next 24 hours and 7 days with pandas, and run a rule engine that raises rain, heat, wind/storm, humidity and UV alerts with critical, warning or info severity. It prints current weather, forecast summary and alerts, saves CSV data, a text report and charts, and has an optional Streamlit dashboard. API keys stay in a `.env` file that is never uploaded, and I wrote 12 unit tests, including tests that check the API parsers using sample responses without needing internet."

### 2. What problem does it solve?
It turns raw forecast numbers into clear, prioritised warnings so users (travelers, farmers, logistics, event planners) don't miss important conditions.

### 3. How do you fetch the data?
`requests.get()` with the location in the parameters, a timeout, and status-code handling. The API returns JSON, which I parse into a common structure. Open-Meteo needs no key; OpenWeatherMap needs a key stored in an environment variable.

### 4. What is JSON and why is it used?
JavaScript Object Notation, a lightweight text format of key-value pairs and lists. APIs use it because it is readable, language-independent and maps directly to Python dicts and lists.

### 5. Why normalise data from different providers?
Each provider has different field names, units and time steps (OpenWeatherMap is 3-hourly, Open-Meteo hourly). Converting once into a standard format means analysis, alerts and the dashboard don't care which provider is used, and I can add a new provider by writing only one parser.

### 6. How does your alert system work?
Analysis produces a summary (max temperature, average humidity, max gust, rain chance in 12h, and so on). Each rule compares one summary value with a configurable threshold and returns an alert with a severity. Alerts are sorted so critical ones show first. Thresholds are a dataclass, so users can override them from the command line or dashboard.

### 7. How did you handle errors?
A custom `WeatherError` with friendly messages for no internet, timeouts, 401 (bad key), 404 (city not found) and 429 (rate limit). One failing city doesn't stop the others. Missing fields become `None` and rules skip them instead of crashing.

### 8. How did you test it without internet or an API?
Simulation mode with five scenario cities, plus unit tests that feed canned API responses into the parsers and check the resulting alerts. That's why 12 tests run in milliseconds with no network.

### 9. How would you improve it?
Store history in SQLite, schedule refreshes with APScheduler, add alert de-duplication (don't resend the same alert within 12 hours), AQI alerts, Telegram/SMS notifications, a map layer, a FastAPI service and Docker deployment.

### 10. How would you explain it to a non-technical person?
"It checks the weather for a city and automatically warns you if there's heavy rain, extreme heat or strong wind, so you can plan ahead."

---
**HR-friendly summary:** Self-driven project that shows problem-solving, careful handling of secrets and errors, testing discipline and clear documentation on GitHub.
**Technical summary:** Provider-agnostic ingestion (`requests`) → normalised schema → pandas window analysis → configurable threshold rule engine → CSV/text/chart reporting, optional Streamlit UI and email notifier, with unit tests.

## Honest tips
- Live API mode was not exercised against the real servers when this was built (no network in the build environment), so run `--mode api` yourself once and mention it. The parsers are tested with sample responses, and any mismatch will show as a friendly error.
- Be ready to explain that simulated data is fictional and thresholds are examples, not official warning criteria.
- Know `analyzer.py` and `alerts.py` line by line.
