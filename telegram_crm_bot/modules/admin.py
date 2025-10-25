from aiogram import types, Dispatcher, F
from utils.firebase_service import USERS_REF, ATTENDANCE_REF
from utils.keyboards import admin_main_kb
from datetime import datetime
import pytz


# ✅ Register handlers properly for aiogram 3.x
async def register_handlers(dp: Dispatcher):
    dp.message.register(cmd_admin_start, F.text == "/admin")
    dp.message.register(cmd_add_user, F.text.startswith("/adduser"))
    dp.message.register(cmd_attendance_summary, F.text == "/attendance_summary")


# 🧭 Admin Panel
async def cmd_admin_start(message: types.Message):
    user_id = str(message.from_user.id)
    user = USERS_REF.child(user_id).get()

    if not user or user.get("role") != "admin":
        await message.reply("🚫 Unauthorized. Admins only.")
        return

    await message.reply("🛠 *Admin Panel:*", parse_mode="Markdown", reply_markup=admin_main_kb())


# ➕ Add User Command
async def cmd_add_user(message: types.Message):
    user_id = str(message.from_user.id)
    user = USERS_REF.child(user_id).get()

    if not user or user.get("role") != "admin":
        await message.reply("🚫 Unauthorized. Admins only.")
        return

    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        await message.reply("🧾 Usage:\n`/adduser telegram_id,Name,role(team_leader/agent/admin),team(optional)`", parse_mode="Markdown")
        return

    try:
        data = parts[1]
        tid, name, role, *rest = [p.strip() for p in data.split(",")]
        team = rest[0] if rest else ""
    except Exception:
        await message.reply("⚠️ Invalid format. Example:\n`/adduser 9876543210,Ravi,agent,Sales Team`", parse_mode="Markdown")
        return

    USERS_REF.child(tid).set({
        "name": name,
        "role": role,
        "team": team
    })

    await message.reply(f"✅ User *{name}* added as `{role}`.", parse_mode="Markdown")


# 📋 Attendance Summary
async def cmd_attendance_summary(message: types.Message):
    user_id = str(message.from_user.id)
    user = USERS_REF.child(user_id).get()

    if not user or user.get("role") not in ["admin", "team_leader"]:
        await message.reply("🚫 Unauthorized access.")
        return

    today = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d")
    att = ATTENDANCE_REF.get()
    present = 0
    total = 0

    if att:
        total = len(att)
        for uid, data in att.items():
            if today in data:
                present += 1

    absent = max(total - present, 0)

    await message.reply(
        f"📅 *Attendance Summary for {today}*\n\n"
        f"✅ Present: {present}\n"
        f"❌ Absent: {absent}\n"
        f"👥 Total Employees: {total}",
        parse_mode="Markdown"
    )
