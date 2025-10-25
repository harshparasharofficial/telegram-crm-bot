import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import pytz

scheduler = AsyncIOScheduler()

async def send_reminders(bot):
    # Query Firebase for leads with followup today and ping assigned agents
    # Placeholder implementation - extend as needed
    print("Running reminders at", datetime.now())

def start_scheduler(bot):
    # example: run every day at 08:55 IST
    scheduler.add_job(lambda: asyncio.create_task(send_reminders(bot)),
                      'cron', hour=8, minute=55, timezone='Asia/Kolkata')
    scheduler.start()
