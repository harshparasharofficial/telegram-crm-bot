from aiogram import types, Dispatcher, F
from utils.firebase_service import ATTENDANCE_REF, ACTIVITY_LOG_REF
import time
from datetime import datetime
import pytz


# ✅ Register handlers properly for aiogram v3.x
async def register_handlers(dp: Dispatcher):
    dp.message.register(cmd_attendance_in, F.text == "/attendance_in")
    dp.message.register(cmd_attendance_out, F.text == "/attendance_out")
    dp.message.register(location_handler, F.location)


# 🕘 Check-IN command
async def cmd_attendance_in(message: types.Message):
    await message.reply(
        "📍 Please share your *current location* now.\n"
        "Use: 📎 → Location → Send My Current Location",
        parse_mode="Markdown"
    )


# 🕔 Check-OUT command
async def cmd_attendance_out(message: types.Message):
    await message.reply(
        "📍 Please share your *current location* to mark checkout.",
        parse_mode="Markdown"
    )


# 📍 Handle location messages
async def location_handler(message: types.Message):
    user_id = str(message.from_user.id)
    loc = message.location
    lat, lon = loc.latitude, loc.longitude
    today = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d")
    user_ref = ATTENDANCE_REF.child(user_id).child(today)

    existing = user_ref.get()
    now_ms = int(time.time() * 1000)

    # If no record or no check_in — mark IN
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

        local_time = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%I:%M %p")
        await message.reply(f"✅ *Checked IN* at {local_time}\n📍 Location: {lat}, {lon}", parse_mode="Markdown")

    # Else mark OUT
    else:
        user_ref.child("check_out").set({
            "time": now_ms,
            "lat": lat,
            "lon": lon
        })

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

        local_time = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%I:%M %p")
        await message.reply(
            f"✅ *Checked OUT* at {local_time}\n⏱ Worked *{duration_minutes} minutes* today.",
            parse_mode="Markdown"
        )
