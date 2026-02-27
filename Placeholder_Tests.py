# ===== Imports =====
import requests
from datetime import datetime
import os
from telegram import Bot
from flask import Flask
import threading
from apscheduler.schedulers.background import BackgroundScheduler

# ===== Environment Variables =====
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")  
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
chat_id = os.environ.get("CHAT_ID")

# ===== City =====
CITY = "Ubstadt-Weiher"

# ===== Telegram / Weather function =====
def send_daily_message():
    try:
        # ===== Fetch hourly weather data =====
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={CITY}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        hourly_data = []
        for item in data["list"]:
            forecast_time = datetime.fromtimestamp(item["dt"])
            hour = forecast_time.hour
            if 8 <= hour <= 14:
                temp = item["main"]["temp"]
                rain = item.get("pop", 0) * 100
                description = item["weather"][0]["description"]
                hourly_data.append({
                    "time": forecast_time.strftime("%H:%M"),
                    "temp": temp,
                    "rain": rain,
                    "desc": description
                })

        # ===== Summarize weather =====
        temps = [h["temp"] for h in hourly_data]
        rain_probs = [h["rain"] for h in hourly_data]

        summary = f"Weather summary for 8am–2pm:\n" \
                  f"- Low: {min(temps):.1f}°C\n" \
                  f"- High: {max(temps):.1f}°C\n" \
                  f"- Max rain chance: {max(rain_probs):.0f}%\n" \
                  f"- Conditions: {', '.join(h['desc'] for h in hourly_data)}"

        # ===== Gemini placeholder =====
        advice = "Jacket and waterproof boots. Maybe a hat if it rains."

        # ===== Telegram Bot =====
        bot = Bot(token=bot_token)
        bot.send_message(chat_id=chat_id, text=f"🌤 Morning Clothing Advice 🌤\n\n{advice}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Message sent!")
    except Exception as e:
        print(f"Error sending message: {e}")

# ===== Flask web service =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Start Flask in a separate thread
threading.Thread(target=run_web).start()

# ===== Scheduler =====
scheduler = BackgroundScheduler()
scheduler.add_job(send_daily_message, "interval", minutes=2)  # <-- TEST: every 2 minutes
# For daily at 6am, use: scheduler.add_job(send_daily_message, "cron", hour=6, minute=0)
scheduler.start()

# ===== Keep script running =====
print("Scheduler started, Flask app running...")
