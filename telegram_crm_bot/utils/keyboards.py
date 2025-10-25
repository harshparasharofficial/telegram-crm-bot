from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def lang_selection_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="English", callback_data="lang_en"),
         InlineKeyboardButton(text="हिंदी", callback_data="lang_hi")],
        [InlineKeyboardButton(text="Mix", callback_data="lang_mix")]
    ])
    return kb

def admin_main_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("📋 All Leads", callback_data="admin_leads")],
        [InlineKeyboardButton("🕒 Attendance", callback_data="admin_attendance"),
         InlineKeyboardButton("👥 Users", callback_data="admin_users")],
        [InlineKeyboardButton("📈 Reports", callback_data="admin_reports")]
    ])
    return kb

def agent_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("➕ Add Lead", callback_data="agent_add_lead")],
        [InlineKeyboardButton("📂 My Leads", callback_data="agent_my_leads")],
        [InlineKeyboardButton("🕒 Attendance", callback_data="agent_attendance")]
    ])
