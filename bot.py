import os
import asyncio
from pyrogram import Client
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))

bot = Client("cleanup_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
scheduler = AsyncIOScheduler(timezone=timezone("Asia/Kolkata"))

async def remove_non_admins():
    async with bot:
        admins = await bot.get_chat_members(GROUP_ID, filter="administrators")
        admin_ids = [admin.user.id for admin in admins]

        async for member in bot.get_chat_members(GROUP_ID):
            if member.user.id not in admin_ids:
                try:
                    await bot.kick_chat_member(GROUP_ID, member.user.id)
                    await bot.unban_chat_member(GROUP_ID, member.user.id)  # optional: allow rejoining
                except Exception as e:
                    print(f"Error removing {member.user.id}: {e}")

@scheduler.scheduled_job("cron", hour=0, minute=0)
async def scheduled_job():
    print("Running cleanup job...")
    await remove_non_admins()

async def main():
    await bot.start()
    scheduler.start()
    print("Bot started and scheduled.")
    await idle()

from pyrogram.idle import idle
asyncio.run(main())
