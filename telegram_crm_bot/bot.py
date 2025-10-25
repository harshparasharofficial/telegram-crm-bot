import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, ADMIN_IDS
from utils.firebase_service import ROOT_DB, USERS_REF
from utils.scheduler import start_scheduler
from modules import leads, attendance, admin, agent

# ✅ Logging setup
logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # ✅ Register module handlers (await all async ones)
    await leads.register_handlers(dp)
    await attendance.register_handlers(dp)
    await admin.register_handlers(dp)
    await agent.register_handlers(dp)

    # ✅ Ensure admin users exist in Firebase
    if ADMIN_IDS:
        for aid in ADMIN_IDS:
            USERS_REF.child(str(aid)).update({"role": "admin", "name": "Admin"})

    # ✅ Start background scheduler (attendance reminders, daily logs, etc.)
    start_scheduler(bot)

    logging.info("🚀 Bot started successfully. Listening for updates...")

    # ✅ Start polling Telegram
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Polling stopped due to: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
