import asyncio
import os
from pyrogram import Client
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger  # Updated import
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Initialize bot with credentials from .env file
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Function to remove users
async def remove_users():
    async with bot:
        # Get all members of the group (except admins)
        members = await bot.get_chat_members(CHAT_ID)
        for member in members:
            if not member.status == "administrator":
                try:
                    await bot.kick_chat_member(CHAT_ID, member.user.id)
                    print(f"Removed user {member.user.id}")
                except Exception as e:
                    print(f"Failed to remove user {member.user.id}: {e}")

# Function to send the daily cleanup message
async def send_cleanup_message():
    async with bot:
        try:
            await bot.send_message(CHAT_ID, "Daily cleanup in progress. All non-admin users will be removed.")
        except Exception as e:
            print(f"Error sending cleanup message: {e}")

# Scheduler to run the removal at 12:00 AM IST daily
def start_scheduler():
    scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
    # Schedule the daily task using IntervalTrigger
    scheduler.add_job(remove_users, IntervalTrigger(hours=24, minutes=0, seconds=0, start_date=datetime.now()))  # Run every 24 hours
    scheduler.add_job(send_cleanup_message, IntervalTrigger(hours=24, minutes=0, seconds=30, start_date=datetime.now()))  # Send message 30 seconds after
    scheduler.start()

# Start the bot
async def main():
    await bot.start()
    print("Bot started. Scheduled daily cleanup at 00:00 IST.")
    start_scheduler()
    while True:
        await asyncio.sleep(3600)  # Keep the bot running

if __name__ == "__main__":
    asyncio.run(main())
