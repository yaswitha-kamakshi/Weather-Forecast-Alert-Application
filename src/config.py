"""Paths and environment settings."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"
REPORTS_DIR = BASE_DIR / "reports"
CITIES_CSV = DATA_DIR / "cities.csv"
SAMPLE_JSON = DATA_DIR / "sample_weather.json"

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")


def smtp_settings() -> dict:
    return {
        "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "port": int(os.getenv("SMTP_PORT", "465")),
        "user": os.getenv("SMTP_USER", ""),
        "password": os.getenv("SMTP_PASS", ""),
        "to": os.getenv("ALERT_TO", ""),
    }
