# collector_utils.py
import requests
import sqlite3
from datetime import datetime

def collect_weather_data():
    try:
        forecast_url = "https://api.open-meteo.com/v1/forecast?latitude=3.139&longitude=101.6869&hourly=temperature_2m,precipitation_probability,wind_speed_10m&timezone=Asia%2FKuala_Lumpur"
        current_url = "https://api.open-meteo.com/v1/forecast?latitude=3.139&longitude=101.6869&current=temperature_2m,wind_speed_10m,weathercode&timezone=Asia%2FKuala_Lumpur"

        # Connect and ensure table exists
        conn = sqlite3.connect('weather_data.db')
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            forecast_temp REAL,
            actual_temp REAL,
            forecast_wind REAL,
            actual_wind REAL
        )
        ''')
        conn.commit()

        now = datetime.now().strftime("%Y-%m-%dT%H:00")

        forecast = requests.get(forecast_url).json()
        current = requests.get(current_url).json()

        if now in forecast['hourly']['time']:
            i = forecast['hourly']['time'].index(now)
            forecast_temp = forecast['hourly']['temperature_2m'][i]
            forecast_wind = forecast['hourly']['wind_speed_10m'][i]
        else:
            print(f"[Collector] No forecast data available for {now}")
            return

        actual_temp = current['current']['temperature_2m']
        actual_wind = current['current']['wind_speed_10m']

        # Prevent duplicate
        cursor.execute("SELECT COUNT(*) FROM weather_data WHERE timestamp = ?", (now,))
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO weather_data (timestamp, forecast_temp, actual_temp, forecast_wind, actual_wind)
                VALUES (?, ?, ?, ?, ?)
            ''', (now, forecast_temp, actual_temp, forecast_wind, actual_wind))
            conn.commit()
            print(f"[Collector] Inserted data for {now}")
        else:
            print(f"[Collector] Skipped duplicate for {now}")

        conn.close()

    except Exception as e:
        print(f"[Collector] Error: {e}")
