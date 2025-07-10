# scheduler.py
import schedule
import time
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo 

def job():
    try:
        current_time = datetime.now(ZoneInfo("Asia/Kuala_Lumpur"))
        print(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] [Scheduler] Running weather_collector.py...")
        subprocess.run(["python", "weather_collector.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[Scheduler] Failed: {e}")

def start():
    print("[Scheduler] Collector is now running every 20 minutes...")

    # Schedule the job every 20 minutes
    schedule.every(20).minutes.do(job)

    # Keep running loop
    while True:
        schedule.run_pending()
        # Print alive message every 2 minutes
        current_time = datetime.now(ZoneInfo("Asia/Kuala_Lumpur"))
        print(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] [Scheduler] App is running...")
        time.sleep(1)  
