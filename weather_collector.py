# weather_collector.py
import requests
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo  # Top of the file


# API URLs
forecast_url = "https://api.open-meteo.com/v1/forecast?latitude=3.139&longitude=101.6869&hourly=temperature_2m,precipitation_probability,wind_speed_10m&timezone=Asia%2FKuala_Lumpur"
current_url = "https://api.open-meteo.com/v1/forecast?latitude=3.139&longitude=101.6869&current=temperature_2m,wind_speed_10m,weathercode&timezone=Asia%2FKuala_Lumpur"

# Create DB and table
conn = sqlite3.connect('weather_data.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS weather_data (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    forecast_temp REAL,
    actual_temp REAL,
    forecast_wind REAL,
    actual_wind REAL
)
''')
conn.commit()

# Fetch data
forecast = requests.get(forecast_url).json()
current = requests.get(current_url).json()

# Extract current hour timestamp
malaysia_time = datetime.now(ZoneInfo("Asia/Kuala_Lumpur"))
now = malaysia_time.strftime("%Y-%m-%dT%H:00")


# Extract matching forecast data
forecast_temp = forecast['hourly']['temperature_2m'][forecast['hourly']['time'].index(now)]
forecast_wind = forecast['hourly']['wind_speed_10m'][forecast['hourly']['time'].index(now)]
actual_temp = current['current']['temperature_2m']
actual_wind = current['current']['wind_speed_10m']

# ✅ Prevent duplicate entry
cursor.execute("SELECT COUNT(*) FROM weather_data WHERE timestamp = ?", (now,))
exists = cursor.fetchone()[0]

if exists == 0:
    cursor.execute('''
    INSERT INTO weather_data (timestamp, forecast_temp, actual_temp, forecast_wind, actual_wind)
    VALUES (?, ?, ?, ?, ?)
    ''', (now, forecast_temp, actual_temp, forecast_wind, actual_wind))
    conn.commit()
    print(f"Data inserted for {now}")
else:
    print(f"Skipped duplicate for {now}")

conn.close()
