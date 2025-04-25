import os
import time
import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.daily import Daily
from pyrogram import Client
from pyrogram.errors import BadMsgNotification
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Define the bot client
bot = Client("telegram_cleanup_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Sync time with NTP server
def sync_time():
    import ntplib
    client = ntplib.NTPClient()
    response = client.request('pool.ntp.org')
    return response.tx_time

# Retry logic for bot start
async def start_bot():
    try:
        await bot.start()
        logger.info("Bot started successfully.")
    except BadMsgNotification as e:
        logger.error(f"Error starting bot: {e}")
        time.sleep(5)  # Retry after 5 seconds
        await start_bot()

# Define a simple cleanup task
async def cleanup_task():
    logger.info("Running cleanup task.")
    # Add your cleanup logic here

# Define the job scheduler
def setup_scheduler():
    scheduler = AsyncIOScheduler()
    # Schedule cleanup task every day at 12:00 AM IST
    scheduler.add_job(cleanup_task, Daily(hour=0, minute=0, timezone="Asia/Kolkata"))
    scheduler.start()

# Main function to run the bot
async def main():
    try:
        # Sync time before starting bot
        sync_time()
        await start_bot()

        # Setup scheduler for daily tasks
        setup_scheduler()

        # Run the bot until it's stopped
        await bot.idle()

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        time.sleep(5)  # Retry after 5 seconds
        await main()  # Retry the connection

if __name__ == "__main__":
    asyncio.run(main())
