import asyncio
import json
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

CONFIG_PATH = "config.json"

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

def get_topic_whitelist(cfg, chat_id, topic_id):
    return cfg.get("whitelist", {}).get(str(chat_id), {}).get(str(topic_id), [])

def set_topic_whitelist(cfg, chat_id, topic_id, ids):
    wl = cfg.setdefault("whitelist", {})
    chat = wl.setdefault(str(chat_id), {})
    chat[str(topic_id)] = ids
    save_config(cfg)

async def main():
    cfg = load_config()
    bot = Bot(cfg["bot_token"])
    dp = Dispatcher()

    async def is_admin(chat_id, user_id):
        try:
            member = await bot.get_chat_member(chat_id, user_id)
            return member.status in ("creator", "administrator")
        except:
            return False

    @dp.message(Command("show_ids"))
    async def show_ids(message: Message):
        await message.reply(
            f"chat_id = {message.chat.id}\n"
            f"topic_id = {message.message_thread_id}\n"
            f"user_id = {message.from_user.id}"
        )

    @dp.message(Command("topic_allow"))
    async def topic_allow(message: Message):
        if message.message_thread_id is None:
            return await message.reply("Usa questo comando dentro un topic")
        cfg = load_config()
        chat_id = message.chat.id
        topic_id = message.message_thread_id
        parts = message.text.split()
        if len(parts) < 2:
            return await message.reply("Uso: /topic_allow <user_id>")
        uid = int(parts[1])
        wl = get_topic_whitelist(cfg, chat_id, topic_id)
        if uid not in wl:
            wl.append(uid)
        set_topic_whitelist(cfg, chat_id, topic_id, wl)
        await message.reply(f"Aggiunto {uid} alla whitelist del topic")

    @dp.message(F.message_thread_id.as_("mtid"))
    async def enforce(message: Message, mtid=None):
        if mtid is None:
            return
        cfg = load_config()
        chat_id = message.chat.id
        topic_id = mtid
        user_id = message.from_user.id
        if await is_admin(chat_id, user_id) or message.from_user.is_bot:
            return
        allowed = get_topic_whitelist(cfg, chat_id, topic_id)
        if user_id not in allowed:
            try:
                await message.delete()
            except TelegramBadRequest:
                pass

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
