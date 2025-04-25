import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Customizable cleanup time
REMOVE_HOUR = int(os.getenv("REMOVE_HOUR", 0))
REMOVE_MINUTE = int(os.getenv("REMOVE_MINUTE", 0))

bot = Client("mass_kicker_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
scheduler = AsyncIOScheduler(timezone=timezone("Asia/Kolkata"))

removal_stats = {}

@bot.on_message(filters.new_chat_members | filters.left_chat_member)
async def delete_system_messages(client: Client, message: Message):
    try:
        await message.delete()
    except Exception as e:
        print(f"Couldn't delete system message: {e}")

@bot.on_message(filters.command("start"))
async def start_handler(client: Client, message: Message):
    await message.reply_text("I'm active! I’ll auto-remove non-admin users from groups daily at your set time.")

@bot.on_message(filters.command("stats") & filters.group)
async def stats_handler(client: Client, message: Message):
    group_id = message.chat.id
    removed = removal_stats.get(group_id, 0)
    await message.reply_text(f"Removed users today: {removed}")

async def remove_users_from_group(group_id):
    removal_stats[group_id] = 0
    async for member in bot.get_chat_members(group_id):
        try:
            if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                await bot.kick_chat_member(group_id, member.user.id)
                await bot.unban_chat_member(group_id, member.user.id)
                removal_stats[group_id] += 1
        except Exception as e:
            print(f"Error removing user in group {group_id}: {e}")

async def clean_all_groups():
    async for dialog in bot.get_dialogs():
        if dialog.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP]:
            await remove_users_from_group(dialog.chat.id)

@scheduler.scheduled_job("cron", hour=REMOVE_HOUR, minute=REMOVE_MINUTE)
async def scheduled_cleanup():
    print("Running scheduled cleanup...")
    await clean_all_groups()

async def main():
    await bot.start()
    scheduler.start()
    print(f"Bot started. Scheduled daily cleanup at {REMOVE_HOUR:02}:{REMOVE_MINUTE:02} IST.")
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        print("Shutting down...")
        await bot.stop()

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            print(f"Bot crashed, restarting... Error: {e}")
