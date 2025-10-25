from aiogram import types, Dispatcher
from utils.keyboards import agent_main_kb, lang_selection_kb
from utils.firebase_service import USERS_REF

def register_handlers(dp: Dispatcher):
    dp.message.register(cmd_start, commands=["start"])
    dp.callback_query.register(lang_callback, lambda c: c.data and c.data.startswith("lang_"))

async def cmd_start(message: types.Message):
    # welcome and language selection
    uid = str(message.from_user.id)
    user = USERS_REF.child(uid).get()
    if not user:
        # default create basic user doc (role=agent until admin upgrades)
        USERS_REF.child(uid).set({
            "name": message.from_user.full_name,
            "role": "agent",
            "team": ""
        })
    await message.reply("Welcome to CRM Bot! Choose language:", reply_markup=lang_selection_kb())

async def lang_callback(query: types.CallbackQuery):
    lang = query.data.split("_", 1)[1]
    uid = str(query.from_user.id)
    user = USERS_REF.child(uid).get()
    if user:
        USERS_REF.child(uid).update({"language": lang})
    await query.answer("Language updated.")
    await query.message.edit_text("Language set. Use /addlead to add a lead.", reply_markup=agent_main_kb())
