from aiogram import types, Dispatcher, F
from utils.keyboards import agent_main_kb, lang_selection_kb
from utils.firebase_service import USERS_REF


# ✅ Register handlers in aiogram 3.x format
async def register_handlers(dp: Dispatcher):
    dp.message.register(cmd_start, F.text == "/start")
    dp.callback_query.register(lang_callback, F.data.startswith("lang_"))


# 🚀 /start command
async def cmd_start(message: types.Message):
    uid = str(message.from_user.id)
    user = USERS_REF.child(uid).get()

    if not user:
        USERS_REF.child(uid).set({
            "name": message.from_user.full_name,
            "role": "agent",   # Default role until admin upgrades
            "team": ""
        })

    await message.reply(
        "👋 Welcome to *CRM Bot!* Please choose your language:",
        reply_markup=lang_selection_kb(),
        parse_mode="Markdown"
    )


# 🌐 Language selection handler
async def lang_callback(callback: types.CallbackQuery):
    lang = callback.data.split("_", 1)[1]
    uid = str(callback.from_user.id)

    user = USERS_REF.child(uid).get()
    if user:
        USERS_REF.child(uid).update({"language": lang})

    await callback.answer("✅ Language updated.")
    await callback.message.edit_text(
        "🌍 Language set successfully.\nNow you can use /addlead to add a lead.",
        reply_markup=agent_main_kb()
    )
