import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook

# ====== CONFIG ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN non trovato nelle variabili d'ambiente")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Carica whitelist da file JSON
if os.path.exists("whitelist.json"):
    with open("whitelist.json", "r") as f:
        WHITELIST = json.load(f)
else:
    WHITELIST = {}

# ====== WEBHOOK CONFIG ======
WEBHOOK_HOST = "https://b-st-bot.onrender.com"   # dominio del tuo bot su Render
WEBHOOK_PATH = f"/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 10000))  # Render assegna la porta tramite variabile

# ====== HANDLERS ======
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer("👋 Ciao! Sono attivo con webhook su Render.")

@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def check_whitelist(message: types.Message):
    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)

    if chat_id in WHITELIST:
        allowed_users = WHITELIST[chat_id]
        if user_id not in allowed_users:
            await message.delete()
            return

    # se permesso, lascia passare
    await message.answer(f"✅ {message.from_user.first_name} ha scritto: {message.text}")

# ====== AVVIO/STOP WEBHOOK ======
async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    print("🚀 Webhook impostato correttamente:", WEBHOOK_URL)

async def on_shutdown(dp):
    await bot.delete_webhook()
    print("🛑 Webhook rimosso")

if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
