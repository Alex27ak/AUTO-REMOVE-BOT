import os
import threading
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
from datetime import datetime

# Set your desired cleanup time in hours and minutes (24-hour format)
REMOVE_HOUR = int(os.getenv("REMOVE_HOUR", 0))  # Default: 0 (12 AM)
REMOVE_MINUTE = int(os.getenv("REMOVE_MINUTE", 0))  # Default: 0 minutes

# Set the timezone to IST (Indian Standard Time)
IST = pytz.timezone("Asia/Kolkata")

# Basic HTTP server to pass health checks
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health_check_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    httpd.serve_forever()

# Run health check server in a separate thread
threading.Thread(target=run_health_check_server, daemon=True).start()

# Initialize the bot with your API token
bot = Client("bot", bot_token=os.getenv("BOT_TOKEN"))

# Scheduler for daily cleanup
scheduler = AsyncIOScheduler(timezone=IST)

# Get list of chat_ids from environment variable
CHAT_IDS = list(map(int, os.getenv("CHAT_IDS", "-1004660096743,-1002633080719").split(",")))

# Function to remove non-admin users
async def remove_users():
    async with bot:
        print("Starting the cleanup process...")

        # Loop through all group chat IDs
        for chat_id in CHAT_IDS:
            print(f"Cleaning group {chat_id}...")
            try:
                # Fetch all members (excluding admins)
                members = await bot.get_chat_members(chat_id)
                for member in members:
                    if not member.status == "administrator":
                        try:
                            await bot.kick_chat_member(chat_id, member.user.id)
                            print(f"Removed: {member.user.id} from {chat_id}")
                        except Exception as e:
                            print(f"Error removing {member.user.id} from {chat_id}: {e}")
                print(f"Cleanup completed for group {chat_id} at {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')}.")
            except Exception as e:
                print(f"Error processing group {chat_id}: {e}")

# Function to schedule the cleanup at a specific time
def schedule_cleanup():
    cleanup_time = datetime.combine(datetime.today(), datetime.min.time()).replace(hour=REMOVE_HOUR, minute=REMOVE_MINUTE)
    scheduler.add_job(remove_users, 'interval', days=1, start_date=cleanup_time)
    print(f"Scheduled cleanup at {REMOVE_HOUR}:{REMOVE_MINUTE} IST for all groups.")

# Start the bot and scheduler
async def main():
    await bot.start()
    print(f"Bot started at {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')}")
    
    schedule_cleanup()

    # Run the scheduler in the background
    scheduler.start()

    try:
        await asyncio.Event().wait()  # Keep the bot running
    except (KeyboardInterrupt, SystemExit):
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
