"""Streamlit dashboard (optional).  Run with:  streamlit run dashboard.py
Works offline in Simulation mode; use Live mode for real Open-Meteo data."""
import pandas as pd
import streamlit as st

from src.alerts import Thresholds, evaluate
from src.analyzer import analyze, to_frames
from src.simulator import available_cities, load_city
from src.weather_client import WeatherError, fetch

st.set_page_config(page_title="Weather Forecast & Alerts", page_icon="🌦️", layout="wide")
st.title("🌦️ Weather Forecast & Alert Dashboard")

# ---------------- Sidebar ----------------
mode = st.sidebar.radio("Data source", ["Simulation (offline)", "Live (Open-Meteo)"])
if mode.startswith("Simulation"):
    city = st.sidebar.selectbox("City", available_cities())
else:
    city = st.sidebar.text_input("City", "Delhi")

st.sidebar.header("Alert thresholds")
d = Thresholds()
th = Thresholds(
    heat_warn_c=st.sidebar.slider("Heat warning (°C)", 25, 45, int(d.heat_warn_c)),
    heat_critical_c=st.sidebar.slider("Heat critical (°C)", 30, 50, int(d.heat_critical_c)),
    rain_prob_pct=st.sidebar.slider("Rain chance (%)", 10, 100, int(d.rain_prob_pct)),
    humidity_pct=st.sidebar.slider("Humidity (%)", 50, 100, int(d.humidity_pct)),
    wind_warn_ms=st.sidebar.slider("Wind gust warning (m/s)", 5, 30, int(d.wind_warn_ms)),
)


@st.cache_data(ttl=600, show_spinner="Fetching weather...")
def get_data(mode_name: str, city_name: str):
    return load_city(city_name) if mode_name.startswith("Simulation") else fetch(city_name)


try:
    data = get_data(mode, city)
except (KeyError, WeatherError) as e:
    st.error(e.args[0] if e.args else str(e))
    st.stop()

summary = analyze(data)
alerts = evaluate(data["city"], summary, th)
hourly, daily = to_frames(data)
cur = data["current"]

# ---------------- Current weather ----------------
st.subheader(f"{data['city']}: {cur['description']}  ·  source: {data['source']}")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Temperature", f"{cur['temp_c']:.1f} °C" if cur["temp_c"] is not None else "n/a")
c2.metric("Humidity", f"{cur['humidity']:.0f} %" if cur["humidity"] is not None else "n/a")
c3.metric("Wind", f"{cur['wind_ms']:.1f} m/s" if cur["wind_ms"] is not None else "n/a")
c4.metric("Rain next 24h", f"{summary['rain_total_mm']:.1f} mm" if summary["rain_total_mm"] is not None else "n/a")

# ---------------- Alerts ----------------
st.subheader("🚨 Alerts")
if not alerts:
    st.success("No alerts. Conditions are normal.")
for a in alerts:
    {"critical": st.error, "warn": st.warning, "info": st.info}[a["severity"]](f"**{a['code']}**: {a['message']}")

# ---------------- Charts ----------------
left, right = st.columns(2)
with left:
    st.markdown("**Temperature (°C), next 48h**")
    st.line_chart(hourly.set_index("time")["temp_c"])
    st.markdown("**Humidity (%)**")
    st.line_chart(hourly.set_index("time")["humidity"])
with right:
    st.markdown("**Rain (mm per step)**")
    st.bar_chart(hourly.set_index("time")["precip_mm"].fillna(0))
    st.markdown("**7-day outlook**")
    st.dataframe(daily, use_container_width=True, hide_index=True)

st.download_button("⬇ Download hourly forecast (CSV)", hourly.to_csv(index=False),
                   file_name=f"forecast_{data['city']}.csv", mime="text/csv")
