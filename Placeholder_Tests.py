# ===== Imports =====
import requests
from datetime import datetime
import os
from telegram import Bot
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import threading

# ===== Environment Variables =====
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")  
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
chat_id = os.environ.get("CHAT_ID")

# ===== City =====
CITY = "Ubstadt-Weiher"

# ===== Telegram Bot =====
bot = Bot(token=bot_token)

# ===== Function to fetch weather and send advice =====
def send_weather_advice():
    try:
        # Fetch hourly weather data
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

        # Summarize weather
        temps = [h["temp"] for h in hourly_data]
        rain_probs = [h["rain"] for h in hourly_data]

        summary = f"Weather summary for 8am–2pm:\n" \
                  f"- Low: {min(temps):.1f}°C\n" \
                  f"- High: {max(temps):.1f}°C\n" \
                  f"- Max rain chance: {max(rain_probs):.0f}%\n" \
                  f"- Conditions: {', '.join(h['desc'] for h in hourly_data)}"

        # Placeholder advice (replace with Gemini if needed)
        advice = "Jacket and waterproof boots. Maybe a hat if it rains."

        # Send Telegram message
        bot.send_message(chat_id=chat_id, text=f"🌤 Morning Clothing Advice 🌤\n\n{advice}")

        print("✅ Message sent successfully")
    except Exception as e:
        print(f"⚠ Error sending message: {e}")

# ===== Flask app =====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

# ===== Scheduler =====
scheduler = BackgroundScheduler()
# Highlight: change here for testing interval or 6am daily
scheduler.add_job(send_weather_advice, trigger="interval", minutes=2)  # Every 2 minutes for testing
# scheduler.add_job(send_weather_advice, trigger="cron", hour=6, minute=0)  # Use for 6am daily
scheduler.start()

# ===== Send a message immediately on startup =====
send_weather_advice()  # Highlight: immediate test message

# ===== Run Flask =====
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()
