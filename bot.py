import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook

# Legge il token dalle variabili di ambiente
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN non trovato nelle variabili d'ambiente")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Config Webhook
WEBHOOK_HOST = "https://b-st-bot.onrender.com"  # URL di Render
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Handlers
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.reply("Ciao 👋, il bot è attivo su Render con Webhook!")

# Funzioni startup/shutdown
async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dp):
    await bot.delete_webhook()

if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000))  # Render fornisce PORT automaticamente
    )
