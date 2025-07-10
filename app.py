# app.py
from flask import Flask, jsonify, send_file, Response
import sqlite3
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo  
import threading
import scheduler  # we will call scheduler.start()
from collector_utils import collect_weather_data  # Import the function
import os

app = Flask(__name__)

# ========== ROUTES ==========

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/data')
def get_data():
    conn = sqlite3.connect('weather_data.db')
    df = pd.read_sql_query("SELECT * FROM weather_data", conn)
    conn.close()
    return df.to_json(orient="records")

@app.route('/mse-endpoint')
def compute_mse():
    conn = sqlite3.connect('weather_data.db')
    df = pd.read_sql_query("SELECT * FROM weather_data", conn)
    conn.close()
    mse_temp = ((df['forecast_temp'] - df['actual_temp']) ** 2).mean()
    mse_wind = ((df['forecast_wind'] - df['actual_wind']) ** 2).mean()
    return jsonify({"mse_temperature": mse_temp, "mse_wind": mse_wind})

@app.route('/about')
def about_us():
    return send_file('about_us.html')

@app.route('/download')
def download_csv():
    conn = sqlite3.connect('weather_data.db')
    df = pd.read_sql_query("SELECT * FROM weather_data", conn)
    conn.close()

    # ✅ Malaysia timezone-aware timestamp
    malaysia_time = datetime.now(ZoneInfo("Asia/Kuala_Lumpur"))
    timestamp = malaysia_time.strftime('%Y%m%d_%H%M')
    filename = f"WDash_{timestamp}.csv"
    csv = df.to_csv(index=False)

    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.route('/database')
def database_page():
    return send_file('database.html')

@app.route('/mse')
def mse_page():
    return send_file('mse.html')

@app.route('/analysis')
def analysis_page():
    return send_file('analysis.html')

@app.route('/run-collector')
def run_collector():
    import subprocess
    try:
        subprocess.run(['python', 'weather_collector.py'], check=True)
        return jsonify({"status": "success", "message": "Collector ran successfully."})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/daily_mse')
def daily_mse():
    conn = sqlite3.connect('weather_data.db')
    df = pd.read_sql_query("SELECT * FROM weather_data", conn)
    conn.close()

    # Convert timestamp to date (in Malaysia time)
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize('UTC').dt.tz_convert('Asia/Kuala_Lumpur')
    df['date'] = df['timestamp'].dt.date

    df['temp_sq_error'] = (df['forecast_temp'] - df['actual_temp']) ** 2
    df['wind_sq_error'] = (df['forecast_wind'] - df['actual_wind']) ** 2

    # Group by date and compute MSE
    result = df.groupby('date').agg(
        temp_mse=('temp_sq_error', 'mean'),
        wind_mse=('wind_sq_error', 'mean')
    ).reset_index()

    # Convert date to string for frontend
    result['date'] = result['date'].astype(str)
    return result.to_json(orient='records')

# ========== START SCHEDULER ==========

def start_background_tasks():
    thread = threading.Thread(target=scheduler.start, daemon=True)
    thread.start()

# ========== RUN APP ==========

if __name__ == '__main__':
    collect_weather_data()  # Initial data collection
    start_background_tasks()  # Start scheduler in background
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
