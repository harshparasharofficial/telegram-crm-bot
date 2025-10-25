import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, ADMIN_IDS
from utils.firebase_service import ROOT_DB, USERS_REF
from utils.scheduler import start_scheduler
from modules import leads, attendance, admin, agent

import logging
logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Register module handlers
    await leads.register_handlers(dp)
    attendance.register_handlers(dp)
    admin.register_handlers(dp)
    agent.register_handlers(dp)

    # Make sure admin users are present in DB
    if ADMIN_IDS:
        for aid in ADMIN_IDS:
            USERS_REF.child(str(aid)).update({"role": "admin", "name": "Admin"})

    # Start scheduler
    start_scheduler(bot)

    # Start polling
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
