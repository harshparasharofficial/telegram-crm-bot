from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InputFile
from utils.firebase_service import LEADS_REF, ACTIVITY_LOG_REF, USERS_REF
from utils.keyboards import agent_main_kb
import time
import uuid

class LeadStates(StatesGroup):
    waiting_for_details = State()

async def register_handlers(dp: Dispatcher):
    dp.message.register(cmd_add_lead, commands=["addlead"])
    dp.message.register(process_lead_details, LeadStates.waiting_for_details)
    dp.message.register(cmd_my_leads, commands=["myleads"])
    dp.message.register(cmd_all_leads, commands=["allleads"])  # admin use

async def cmd_add_lead(message: types.Message, state: FSMContext):
    await message.reply("Send lead details in one line: Name, Phone, Budget, Source (comma separated)\nExample:\nRavi Kumar,9876543210,60L,Meta Ads")
    await state.set_state(LeadStates.waiting_for_details)

async def process_lead_details(message: types.Message, state: FSMContext):
    txt = message.text.strip()
    parts = [p.strip() for p in txt.split(",")]
    if len(parts) < 4:
        await message.reply("Invalid format. Please send: Name, Phone, Budget, Source")
        return
    name, phone, budget, source = parts[:4]
    lead_id = str(uuid.uuid4())[:8]
    payload = {
        "name": name,
        "phone": phone,
        "budget": budget,
        "source": source,
        "status": "New",
        "created_by": str(message.from_user.id),
        "assigned_to": str(message.from_user.id),
        "created_at": int(time.time() * 1000)
    }
    LEADS_REF.child(lead_id).set(payload)
    ACTIVITY_LOG_REF.push({
        "time": int(time.time() * 1000),
        "actor": str(message.from_user.id),
        "action": f"added_lead:{lead_id}"
    })
    await message.reply(f"Lead saved with id `{lead_id}`", parse_mode="Markdown")
    await state.clear()

async def cmd_my_leads(message: types.Message):
    user_id = str(message.from_user.id)
    leads = LEADS_REF.order_by_child("assigned_to").equal_to(user_id).get()
    if not leads:
        await message.reply("You have no leads.")
        return
    text = "Your Leads:\n"
    for lid, data in leads.items():
        text += f"\nID: {lid}\nName: {data.get('name')}\nPhone: {data.get('phone')}\nStatus: {data.get('status')}\n---\n"
    await message.reply(text)

async def cmd_all_leads(message: types.Message):
    # Admin use only -- simple check
    user_id = str(message.from_user.id)
    user = USERS_REF.child(user_id).get()
    if not user or user.get("role") != "admin":
        await message.reply("Unauthorized.")
        return
    leads = LEADS_REF.get()
    if not leads:
        await message.reply("No leads in DB.")
        return
    text = "All Leads:\n"
    for lid, data in leads.items():
        text += f"\nID: {lid} | {data.get('name')} | {data.get('phone')} | {data.get('status')}\n"
    await message.reply(text)

