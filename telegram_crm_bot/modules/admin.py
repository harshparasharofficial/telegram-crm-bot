from aiogram import types, Dispatcher
from utils.firebase_service import USERS_REF, ATTENDANCE_REF, ACTIVITY_LOG_REF
from utils.keyboards import admin_main_kb
from datetime import datetime
import pytz

def register_handlers(dp: Dispatcher):
    dp.message.register(cmd_admin_start, commands=["admin"])
    dp.message.register(cmd_add_user, commands=["adduser"])
    dp.message.register(cmd_attendance_summary, commands=["attendance_summary"])

async def cmd_admin_start(message: types.Message):
    user_id = str(message.from_user.id)
    # Check role
    user = USERS_REF.child(user_id).get()
    if not user or user.get("role") != "admin":
        await message.reply("Unauthorized. Admins only.")
        return
    await message.reply("Admin panel:", reply_markup=admin_main_kb())

async def cmd_add_user(message: types.Message):
    # Usage: /adduser telegram_id,name,role,team(optional)
    user_id = str(message.from_user.id)
    user = USERS_REF.child(user_id).get()
    if not user or user.get("role") != "admin":
        await message.reply("Unauthorized.")
        return
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        await message.reply("Usage: /adduser 9876543210,Name,role(teamleader/agent/admin),team(optional)")
        return
    data = parts[1]
    try:
        tid, name, role, *rest = [p.strip() for p in data.split(",")]
    except Exception:
        await message.reply("Invalid format.")
        return
    team = rest[0] if rest else ""
    USERS_REF.child(tid).set({
        "name": name,
        "role": role,
        "team": team
    })
    await message.reply(f"User {name} added as {role}.")

async def cmd_attendance_summary(message: types.Message):
    user_id = str(message.from_user.id)
    user = USERS_REF.child(user_id).get()
    if not user or user.get("role") not in ["admin", "team_leader"]:
        await message.reply("Unauthorized.")
        return
    # For simplicity: show today's attendance counts
    today = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d")
    att = ATTENDANCE_REF.get()
    present = 0
    absent = 0
    if att:
        for uid, data in att.items():
            if today in data:
                present += 1
            else:
                absent += 1
    await message.reply(f"Attendance Summary for {today}\nPresent: {present}\nAbsent (no records): {absent}")
