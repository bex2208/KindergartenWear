# ===== Imports =====
import requests
from datetime import datetime
from google import genai
import os
from telegram import Bot

# ===== Environment Variables =====
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")  
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
chat_id = os.environ.get("CHAT_ID")

# ===== City =====
CITY = "Ubstadt-Weiher"

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
client = genai.Client(api_key=GEMINI_API_KEY)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=(
        f"3-year-old child at kindergarten from 8–14h. Weather forecast: {summary}. "
        "In 3–4 sentences, give concise practical clothing advice for the day: "
        "Specify sleeve length, number of layers, type of jacket (winter/light/rain), "
        "warm leggings or pants, and whether a hat is needed. Advice should be easy to follow "
        "and actionable, not a long paragraph."
    )
)
advice = response.text

# advice = "Jacket and waterproof boots. Maybe a hat if it rains." <--- placeholder for testing

# ===== Telegram Bot =====
bot = Bot(token=bot_token)
bot.send_message(chat_id=chat_id, text=f"🌤 Morning Clothing Advice 🌤\n\n{advice}")

#web service

from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web).start()
