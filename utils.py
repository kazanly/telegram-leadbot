# utils.py
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from aiogram import Bot

BOT_TOKEN = #your bot token
bot = Bot(token=BOT_TOKEN)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_url("your table").sheet1

async def save_to_google_sheets(data: dict):
    sheet.append_row([
        data.get("name", ""),
        data.get("phone", ""),
        data.get("country", ""),
        ", ".join(data.get("services", [])),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])

async def notify_admin(data: dict):
    text = (
        f"📥 Новая заявка:\n\n"
        f"👤 Имя: {data.get('name', '')}\n"
        f"📞 Телефон: {data.get('phone', '')}\n"
        f"🌍 Страна: {data.get('country', '')}\n"
        f"🛠 Запрос: {', '.join(data.get('services', []))}"
    )
    await bot.send_message(#your id telegram, text)
