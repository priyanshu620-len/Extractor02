import re
import io
import time
import json
import os
import random
import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from Extractor import app
from config import OWNER_ID, SUDO_USERS, CHANNEL_ID 
from Extractor.core import script
from Extractor.core.func import subscribe, chk_user

# --- MODULE IMPORTS ---
from Extractor.modules import sw1 

# --- FUTUREKUL MODULE IMPORT ---
try:
    from Extractor.modules.future_kul import FutureKulExtractor
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from future_kul import FutureKulExtractor

# Initializing
fx = FutureKulExtractor()
user_cache = {} # Structure: {user_id: {"list": [], "msg_id": 0, "app": "fk/sw", "type": "Live/Rec"}}

# -------------------------- DATABASE SETUP -------------------------- #
SUDO_DATA_FILE = "sudo_users.json"
USER_STATS = {} 
IMG_MAIN = random.choice(script.IMG) if script.IMG else "https://telegra.ph/file/default_image.jpg"

def load_sudo_users():
    if os.path.exists(SUDO_DATA_FILE):
        try:
            with open(SUDO_DATA_FILE, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def save_sudo_users(data):
    with open(SUDO_DATA_FILE, "w") as f:
        json.dump(data, f)

SUDO_DATA = load_sudo_users()

def is_premium(user_id):
    u_id_str = str(user_id)
    if int(user_id) == OWNER_ID: return True
    if u_id_str in SUDO_DATA:
        expiry = datetime.strptime(SUDO_DATA[u_id_str], '%Y-%m-%d %H:%M:%S')
        if datetime.now() < expiry: return True
    return False

# -------------------------- UI TEXTS -------------------------- #

def get_main_caption(name, user_id):
    stats = USER_STATS.get(user_id, 0)
    return f"""💎 **Premium Extractor Bot** 💎
━━━━━━━━━━━━━━━━━━━━━━━━
👤 **User:** {name}
🆔 **ID:** `{user_id}`
📊 **Extractions:** `{stats}`
━━━━━━━━━━━━━━━━━━━━━━━━
🚀 **Select App for Extraction:**"""

# -------------------------- KEYBOARDS -------------------------- #

MAIN_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("👑 FutureKul", callback_data="fk_choice"),
     InlineKeyboardButton("🎯 Selection Way", callback_data="selection_w")],
    [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/ONeX_sell"),
     InlineKeyboardButton("📊 Stats", callback_data="view_stats")],
    [InlineKeyboardButton("❌ Close Menu", callback_data="home_")]
])

FK_TYPE_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔴 Live Batches", callback_data="futurekul_live"),
     InlineKeyboardButton("📀 Recorded Batches", callback_data="futurekul_rec")],
    [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
])

# -------------------------- COMMANDS -------------------------- #

@app.on_message(filters.command(["start", "apps"]))
async def start_cmd(_, message):
    u_name, u_id = message.from_user.first_name, message.from_user.id
    if u_id not in USER_STATS: USER_STATS[u_id] = 0
    await message.reply_photo(photo=IMG_MAIN, caption=get_main_caption(u_name, u_id), reply_markup=MAIN_BUTTONS)

# -------------------------- CALLBACK HANDLER -------------------------- #

@app.on_callback_query()
async def handle_callback(client, query):
    data = query.data
    u_id = query.from_user.id
    u_name = query.from_user.first_name

    if data == "back_to_main":
        await query.message.edit_caption(caption=get_main_caption(u_name, u_id), reply_markup=MAIN_BUTTONS)

    elif data == "fk_choice":
        if not is_premium(u_id): return await query.answer("❌ Premium Required!", show_alert=True)
        await query.message.reply_text("✨ **FutureKul Selection**\nKaunse batches dekhna chahte hain?", reply_markup=FK_TYPE_BUTTONS)
        await query.answer()

    elif data.startswith("futurekul_"):
        is_live = "live" in data
        status = await query.message.reply_text(f"🔎 Fetching {'Live' if is_live else 'Recorded'} Batches...")
        try:
            batches = await fx.get_batches(is_live=is_live)
            user_cache[u_id] = {"list": batches, "type": "Live" if is_live else "Recorded", "msg_id": status.id, "app": "fk"}
            list_text = f"✨ **FUTUREKUL {'LIVE' if is_live else 'REC'} BATCHES** ✨\n━━━━━━━━━━━━━━━━━━━━\n"
            for i, b in enumerate(batches, 1):
                list_text += f"**{i}.** `{b.get('title')}`\n"
            list_text += "\n> 📝 **Send batch number to extract.**"
            await status.edit_text(list_text)
        except Exception as e: await status.edit_text(f"⚠️ Error: {e}")

    elif data == "selection_w":
        if not is_premium(u_id): return await query.answer("❌ Premium Required!", show_alert=True)
        status = await query.message.reply_text("🔎 Fetching Selection Way batches...")
        try:
            batches = sw1.fetch_active_batches()
            user_cache[u_id] = {"list": batches, "msg_id": status.id, "app": "sw"}
            list_text = "📚 **Selection Way Batches:**\n━━━━━━━━━━━━━━━━━━━━\n"
            for i, b in enumerate(batches, 1):
                list_text += f"**{i}.** {b.get('title')}\n"
            list_text += "\n> 📝 **Send batch number to extract.**"
            await status.edit_text(list_text)
        except Exception as e: await status.edit_text(f"⚠️ Error: {e}")
            
    elif data == "view_stats":
        await query.answer(f"📊 Total Extractions: {USER_STATS.get(u_id, 0)}", show_alert=True)
    elif data == "home_": await query.message.delete()

# -------------------------- EXTRACTION HANDLER -------------------------- #

@app.on_message(filters.text & filters.incoming & filters.private)
async def batch_number_handler(client, message):
    u_id = message.from_user.id
    text = message.text.strip()
    
    if not text.isdigit() or u_id not in user_cache: return
    if not is_premium(u_id): return await message.reply("❌ Premium Expired!")

    index = int(text) - 1
    cache = user_cache[u_id]
    
    if index < 0 or index >= len(cache["list"]):
        return await message.reply("❌ Invalid number!")

    selected = cache["list"][index]
    status = await message.reply("⚡ **Extracting Data... Please Wait**")

    try:
        # --- SELECTION WAY ---
        if cache["app"] == "sw":
            res = sw1.get_final_data(selected.get('id'), u_id, message.from_user.username or "N/A", message.from_user.first_name)
            if res.get("text"):
                file = io.BytesIO(res["text"].encode())
                file.name = f"{res.get('title', 'Batch').replace(' ', '_')}.txt"
                await message.reply_document(document=file, caption=res["report"])
                USER_STATS[u_id] = USER_STATS.get(u_id, 0) + 1
                # Auto-Delete List Message
                await client.delete_messages(message.chat.id, [cache["msg_id"], status.id])
                del user_cache[u_id]

        # --- FUTUREKUL ---
        elif cache["app"] == "fk":
            user_info = {"id": u_id, "username": message.from_user.username or "N/A", "mention": message.from_user.first_name}
            file_io, report = await fx.extract_links(selected['id'], selected['title'], user_info, time.time(), cache["type"])
            if file_io:
                await message.reply_document(document=file_io, caption=report)
                USER_STATS[u_id] = USER_STATS.get(u_id, 0) + 1
                await client.delete_messages(message.chat.id, [cache["msg_id"], status.id])
                del user_cache[u_id]

    except Exception as e:
        await status.edit_text(f"⚠️ Extraction Error: {e}")
