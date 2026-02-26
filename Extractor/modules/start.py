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
user_cache = {} 

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
        else:
            del SUDO_DATA[u_id_str]
            save_sudo_users(SUDO_DATA)
    return False

# -------------------------- PREMIUM COMMANDS -------------------------- #

@app.on_message(filters.command("sudo") & filters.user(OWNER_ID))
async def add_premium(_, message):
    args = message.command
    if len(args) < 3: return await message.reply_text("❌ `/sudo [ID] [DAYS]`")
    try:
        user_id, days = str(args[1]), int(args[2])
        exp = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        SUDO_DATA[user_id] = exp
        save_sudo_users(SUDO_DATA)
        await message.reply_text(f"✅ Premium Added for `{user_id}`\n📅 Expiry: `{exp}`")
    except Exception as e: await message.reply_text(f"⚠️ Error: {e}")

@app.on_message(filters.command("users") & filters.user(OWNER_ID))
async def list_premium_users(_, message):
    if not SUDO_DATA: return await message.reply_text("❌ No premium users.")
    msg = "👥 **Premium Users:**\n" + "\n".join([f"• `{k}` ({v})" for k, v in SUDO_DATA.items()])
    await message.reply_text(msg)

@app.on_message(filters.command("check"))
async def my_status(_, message):
    u_id = str(message.from_user.id)
    status = "ACTIVE" if is_premium(u_id) else "INACTIVE"
    exp = SUDO_DATA.get(u_id, "N/A") if status == "ACTIVE" else "None"
    await message.reply_text(f"💎 Status: `{status}`\n📅 Expiry: `{exp}`")

# -------------------------- KEYBOARDS & START -------------------------- #

MAIN_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("👑 FutureKul", callback_data="fk_choice"),
     InlineKeyboardButton("🎯 Selection Way", callback_data="selection_w")],
    [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/ONeX_sell"),
     InlineKeyboardButton("📊 Stats", callback_data="view_stats")],
    [InlineKeyboardButton("❌ Close Menu", callback_data="home_")]
])

FK_TYPE_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔴 Live", callback_data="futurekul_live"),
     InlineKeyboardButton("📀 Recorded", callback_data="futurekul_rec")],
    [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
])

@app.on_message(filters.command(["start", "apps"]))
async def start_cmd(_, message):
    u_name, u_id = message.from_user.first_name, message.from_user.id
    if u_id not in USER_STATS: USER_STATS[u_id] = 0
    stats = USER_STATS.get(u_id, 0)
    caption = f"💎 **Premium Extractor**\n━━━━━━━━━━━━━━━━━━━━\n👤 User: {u_name}\n🆔 ID: `{u_id}`\n📊 Extractions: `{stats}`"
    await message.reply_photo(photo=IMG_MAIN, caption=caption, reply_markup=MAIN_BUTTONS)

# -------------------------- CALLBACKS -------------------------- #

@app.on_callback_query()
async def handle_callback(client, query):
    data, u_id = query.data, query.from_user.id
    if data == "back_to_main":
        await query.message.edit_caption(caption="💎 Back to Menu", reply_markup=MAIN_BUTTONS)
    elif data == "fk_choice":
        if not is_premium(u_id): return await query.answer("❌ Premium Required!", show_alert=True)
        await query.message.reply_text("✨ Select FutureKul Type:", reply_markup=FK_TYPE_BUTTONS)
    elif data.startswith("futurekul_"):
        is_live = "live" in data
        status = await query.message.reply_text("🔎 Fetching...")
        try:
            batches = await fx.get_batches(is_live=is_live)
            user_cache[u_id] = {"list": batches, "type": "Live" if is_live else "Recorded", "msg_id": status.id, "app": "fk"}
            await status.edit_text(f"✨ **FUTUREKUL {'LIVE' if is_live else 'REC'}**\n" + "\n".join([f"{i+1}. `{b['title']}`" for i, b in enumerate(batches)]))
        except Exception as e: await status.edit_text(f"⚠️ Error: {e}")
    elif data == "selection_w":
        if not is_premium(u_id): return await query.answer("❌ Premium Required!", show_alert=True)
        status = await query.message.reply_text("🔎 Fetching SW...")
        try:
            batches = sw1.fetch_active_batches()
            user_cache[u_id] = {"list": batches, "msg_id": status.id, "app": "sw"}
            await status.edit_text("📚 **Selection Way Batches:**\n" + "\n".join([f"{i+1}. {b['title']}" for i, b in enumerate(batches)]))
        except Exception as e: await status.edit_text(f"⚠️ Error: {e}")
    elif data == "home_": await query.message.delete()

# -------------------------- EXTRACTION HANDLER -------------------------- #

@app.on_message(filters.text & filters.incoming & filters.private)
async def batch_number_handler(client, message):
    u_id = message.from_user.id
    if not message.text.isdigit() or u_id not in user_cache: return
    if not is_premium(u_id): return await message.reply("❌ Premium Expired!")

    index = int(message.text) - 1
    cache = user_cache[u_id]
    if index < 0 or index >= len(cache["list"]): return await message.reply("❌ Invalid Index!")
    
    selected = cache["list"][index]
    status = await message.reply("⚡ **Extracting...**")

    try:
        if cache["app"] == "sw":
            res = sw1.get_final_data(selected['id'], u_id, message.from_user.username or "N/A", message.from_user.first_name)
            if res.get("text"):
                file = io.BytesIO(res["text"].encode())
                file.name = f"{res['title'].replace(' ', '_')}.txt"
                await message.reply_document(document=file, caption=res["report"])
                USER_STATS[u_id] = USER_STATS.get(u_id, 0) + 1
                await client.delete_messages(message.chat.id, [cache["msg_id"], status.id])
                del user_cache[u_id]
        elif cache["app"] == "fk":
            user_info = {"id": u_id, "username": message.from_user.username or "N/A", "mention": message.from_user.first_name}
            file_io, report = await fx.extract_links(selected['id'], selected['title'], user_info, time.time(), cache["type"])
            if file_io:
                await message.reply_document(document=file_io, caption=report)
                USER_STATS[u_id] = USER_STATS.get(u_id, 0) + 1
                await client.delete_messages(message.chat.id, [cache["msg_id"], status.id])
                del user_cache[u_id]
    except Exception as e: await status.edit_text(f"⚠️ Error: {e}")
