import io
import time
import json
import os
import random
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from Extractor import app
from config import OWNER_ID
from Extractor.core import script

# --- MODULE IMPORTS ---
from Extractor.modules import sw1 # 'sway1' ko 'sw1' ki tarah use karenge

try:
    from Extractor.modules.future_kul import FutureKulExtractor
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from future_kul import FutureKulExtractor

# Initializing
fx = FutureKulExtractor()
user_cache = {} # Structure: {u_id: {"list": [], "msg_id": 0, "menu_id": 0, "app": "sw/fk"}}

# -------------------------- DATABASE & PREMIUM -------------------------- #
SUDO_DATA_FILE = "sudo_users.json"
USER_STATS = {} 
IMG_MAIN = random.choice(script.IMG) if script.IMG else "https://telegra.ph/file/default_image.jpg"

def load_sudo_users():
    if os.path.exists(SUDO_DATA_FILE):
        try:
            with open(SUDO_DATA_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_sudo_users(data):
    with open(SUDO_DATA_FILE, "w") as f: json.dump(data, f)

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

# -------------------------- KEYBOARDS -------------------------- #

MAIN_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("👑 FutureKul", callback_data="fk_choice"),
     InlineKeyboardButton("🎯 Selection Way", callback_data="selection_w")],
    [InlineKeyboardButton("📊 My Stats", callback_data="view_stats"),
     InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/ONeX_sell")],
    [InlineKeyboardButton("❌ Close Menu", callback_data="home_")]
])

FK_TYPE_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔴 Live Batches", callback_data="futurekul_live"),
     InlineKeyboardButton("📀 Recorded Batches", callback_data="futurekul_rec")],
    [InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")]
])

# -------------------------- COMMANDS -------------------------- #

@app.on_message(filters.command(["start", "apps"]))
async def start_cmd(client, message):
    u_id = message.from_user.id
    u_name = message.from_user.first_name

    # --- ANTI-SPAM: Delete Old Menu ---
    if u_id in user_cache and "menu_id" in user_cache[u_id]:
        try: await client.delete_messages(message.chat.id, user_cache[u_id]["menu_id"])
        except: pass

    stats = USER_STATS.get(u_id, 0)
    caption = (f"💎 **Premium Extractor Bot** 💎\n━━━━━━━━━━━━━━━━━━━━\n"
               f"👤 **User:** {u_name}\n🆔 **ID:** `{u_id}`\n📊 **Extractions:** `{stats}`\n"
               f"━━━━━━━━━━━━━━━━━━━━\n🚀 **Choose an app below:**")

    sent = await message.reply_photo(photo=IMG_MAIN, caption=caption, reply_markup=MAIN_BUTTONS)
    
    if u_id not in user_cache: user_cache[u_id] = {}
    user_cache[u_id]["menu_id"] = sent.id

@app.on_message(filters.command("sudo") & filters.user(OWNER_ID))
async def add_sudo(_, message):
    try:
        args = message.command
        user_id, days = str(args[1]), int(args[2])
        expiry = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        SUDO_DATA[user_id] = expiry
        save_sudo_users(SUDO_DATA)
        await message.reply_text(f"✅ **Premium Added!**\n🆔 `{user_id}`\n⏳ `{days} Days`")
    except: await message.reply_text("❌ `/sudo [ID] [DAYS]`")

@app.on_message(filters.command("users") & filters.user(OWNER_ID))
async def list_users(_, message):
    msg = f"👥 **Premium Users:** {len(SUDO_DATA)}\n" + "\n".join([f"`{k}`" for k in SUDO_DATA.keys()])
    await message.reply_text(msg)

# -------------------------- CALLBACK HANDLER -------------------------- #

@app.on_callback_query()
async def handle_callback(client, query):
    data, u_id = query.data, query.from_user.id
    u_name = query.from_user.first_name

    if data == "back_to_main":
        stats = USER_STATS.get(u_id, 0)
        await query.message.edit_caption(
            caption=f"💎 **Premium Extractor**\n━━━━━━━━━━━━━━━━━━━━\n👤 {u_name}\n📊 Stats: `{stats}`",
            reply_markup=MAIN_BUTTONS
        )

    elif data == "fk_choice":
        if not is_premium(u_id): return await query.answer("❌ Premium Required!", show_alert=True)
        await query.message.reply_text("✨ **FutureKul Selection**\nChoose batch type:", reply_markup=FK_TYPE_BUTTONS)
        await query.answer()

    elif data.startswith("futurekul_"):
        is_live = "live" in data
        status = await query.message.reply_text("🔎 Fetching FutureKul Batches...")
        try:
            batches = await fx.get_batches(is_live=is_live)
            user_cache[u_id].update({"list": batches, "type": "Live" if is_live else "Recorded", "msg_id": status.id, "app": "fk"})
            list_txt = f"✨ **FUTUREKUL {'LIVE' if is_live else 'REC'}**\n━━━━━━━━━━━━━━━━━━━━\n"
            list_txt += "\n".join([f"**{i+1}.** `{b['title']}`" for i, b in enumerate(batches)])
            await status.edit_text(list_txt + "\n\n> 📝 **Send Number to Extract**")
        except Exception as e: await status.edit_text(f"⚠️ Error: {e}")

    elif data == "selection_w":
        if not is_premium(u_id): return await query.answer("❌ Premium Required!", show_alert=True)
        status = await query.message.reply_text("🔎 Fetching Selection Way Batches...")
        try:
            batches = sw1.fetch_active_batches()
            user_cache[u_id].update({"list": batches, "msg_id": status.id, "app": "sw"})
            list_txt = "📚 **Selection Way Batches**\n━━━━━━━━━━━━━━━━━━━━\n"
            list_txt += "\n".join([f"**{i+1}.** {b['title']}" for i, b in enumerate(batches)])
            await status.edit_text(list_txt + "\n\n> 📝 **Send Number to Extract**")
        except Exception as e: await status.edit_text(f"⚠️ Error: {e}")

    elif data == "view_stats":
        await query.answer(f"📊 Total Extractions: {USER_STATS.get(u_id, 0)}", show_alert=True)
    elif data == "home_": await query.message.delete()

# -------------------------- EXTRACTION HANDLER -------------------------- #

@app.on_message(filters.text & filters.incoming & filters.private)
async def batch_number_handler(client, message):
    u_id = message.from_user.id
    if not message.text.isdigit() or u_id not in user_cache: return
    if not is_premium(u_id): return await message.reply("❌ Premium Expired!")

    index = int(message.text) - 1
    cache = user_cache[u_id]
    if index < 0 or index >= len(cache.get("list", [])): return await message.reply("❌ Invalid Number!")

    selected = cache["list"][index]
    status = await message.reply("⚡ **Extracting... Please Wait**")

    try:
        # Selection Way Logic
        if cache["app"] == "sw":
            res = sw1.get_final_data(selected['id'], u_id, message.from_user.username or "N/A", message.from_user.first_name)
            if res.get("text"):
                file = io.BytesIO(res["text"].encode())
                file.name = f"{res['title'].replace(' ', '_')}.txt"
                await message.reply_document(document=file, caption=res["report"])
                USER_STATS[u_id] = USER_STATS.get(u_id, 0) + 1
                await client.delete_messages(message.chat.id, [cache["msg_id"], status.id, message.id])
                del user_cache[u_id]["list"] # Clear list only

        # FutureKul Logic
        elif cache["app"] == "fk":
            u_info = {"id": u_id, "username": message.from_user.username or "N/A", "mention": message.from_user.first_name}
            file_io, report = await fx.extract_links(selected['id'], selected['title'], u_info, time.time(), cache["type"])
            if file_io:
                await message.reply_document(document=file_io, caption=report)
                USER_STATS[u_id] = USER_STATS.get(u_id, 0) + 1
                await client.delete_messages(message.chat.id, [cache["msg_id"], status.id, message.id])
                del user_cache[u_id]["list"]

    except Exception as e: await status.edit_text(f"⚠️ Error: {e}")
