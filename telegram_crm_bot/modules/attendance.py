from aiogram import types, Dispatcher
from utils.firebase_service import ATTENDANCE_REF, ACTIVITY_LOG_REF, USERS_REF
import time
from datetime import datetime
import pytz

def register_handlers(dp: Dispatcher):
    dp.message.register(cmd_attendance_in, commands=["attendance_in"])
    dp.message.register(cmd_attendance_out, commands=["attendance_out"])
    # For location-based attendance, user should send location with caption containing "attendance_in" or "attendance_out"
    dp.message.register(location_handler, lambda m: m.location is not None)

async def cmd_attendance_in(message: types.Message):
    user_id = str(message.from_user.id)
    await message.reply("Please share your *location* now (use Telegram's attach -> Location).", parse_mode="Markdown")

async def cmd_attendance_out(message: types.Message):
    user_id = str(message.from_user.id)
    await message.reply("Please share your *location* to mark checkout.", parse_mode="Markdown")

async def location_handler(message: types.Message):
    user_id = str(message.from_user.id)
    loc = message.location
    lat, lon = loc.latitude, loc.longitude
    text_caption = (message.caption or "").lower()
    today = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d")
    user_ref = ATTENDANCE_REF.child(user_id).child(today)

    # Decide if marking in or out: check if in exists
    existing = user_ref.get()
    now_ms = int(time.time() * 1000)
    if not existing or "check_in" not in existing:
        user_ref.child("check_in").set({
            "time": now_ms,
            "lat": lat,
            "lon": lon
        })
        ACTIVITY_LOG_REF.push({
            "time": now_ms,
            "actor": user_id,
            "action": "check_in"
        })
        await message.reply(f"✅ Checked IN at {lat},{lon}")
    else:
        # Mark check_out
        user_ref.child("check_out").set({
            "time": now_ms,
            "lat": lat,
            "lon": lon
        })
        # compute duration
        ci = existing.get("check_in", {})
        duration_ms = now_ms - ci.get("time", now_ms)
        duration_minutes = int(duration_ms / 60000)
        user_ref.child("duration_minutes").set(duration_minutes)
        ACTIVITY_LOG_REF.push({
            "time": now_ms,
            "actor": user_id,
            "action": "check_out",
            "duration_minutes": duration_minutes
        })
        await message.reply(f"✅ Checked OUT. Worked {duration_minutes} minutes today.")
