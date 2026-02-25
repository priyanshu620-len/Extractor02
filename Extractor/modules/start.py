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
    """Checks if user has active premium time"""
    u_id_str = str(user_id)
    if int(user_id) == OWNER_ID:
        return True
    if u_id_str in SUDO_DATA:
        expiry = datetime.strptime(SUDO_DATA[u_id_str], '%Y-%m-%d %H:%M:%S')
        if datetime.now() < expiry:
            return True
        else:
            del SUDO_DATA[u_id_str]
            save_sudo_users(SUDO_DATA)
    return False

# -------------------------- HELPERS -------------------------- #

async def safe_edit(query, caption, reply_markup):
    try:
        await query.message.edit_caption(caption=caption, reply_markup=reply_markup)
    except Exception as e:
        if "MESSAGE_NOT_MODIFIED" not in str(e):
            print(f"Edit Error: {e}")

# -------------------------- UI TEXTS -------------------------- #

def get_main_caption(name, user_id):
    stats = USER_STATS.get(user_id, 0)
    return f"""💎 **Welcome to Premium Extractor Bot** 💎
━━━━━━━━━━━━━━━━━━━━━━━━
👤 **User:** {name}
🆔 **ID:** `{user_id}`
📊 **Extractions:** `{stats}`
━━━━━━━━━━━━━━━━━━━━━━━━
⚙️ **Choose your mode below:**

🔐 **Login Required:** For apps that need ID & Password.
🚀 **Without Login:** Extract freely from supported apps.
━━━━━━━━━━━━━━━━━━━━━━━━
🧠 **Tip:** Use correct input format for smooth extraction.
💬 **Need Help?** Tap 'Developer' below for direct support.
━━━━━━━━━━━━━━━━━━━━━━━━"""

# -------------------------- KEYBOARDS -------------------------- #

MAIN_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔐 Login Required", callback_data="login_section"),
     InlineKeyboardButton("🟢 Without Login", callback_data="page_1")],
    [InlineKeyboardButton("🔍 Search AppX API", callback_data="search_api"),
     InlineKeyboardButton("📽️ YT Extractor", callback_data="yt_ext")],
    [InlineKeyboardButton("📋 TXT → HTML", callback_data="txt_html"),
     InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/ONeX_sell")],
    [InlineKeyboardButton("📊 My Stats", callback_data="view_stats"),
     InlineKeyboardButton("❌ Close Menu", callback_data="home_")]
])

PAGE_1 = InlineKeyboardMarkup([
    [InlineKeyboardButton("👑 Premium++", callback_data="prem_plus")],
    [InlineKeyboardButton("🔐 VideoCrypt", callback_data="videocrypt")],
    [InlineKeyboardButton("🪄 AppX Test", callback_data="appx_test"),
     InlineKeyboardButton("📚 Study IQ", callback_data="studyiq")],
    [InlineKeyboardButton("🏫 ClassPlus", callback_data="classplus_"),
     InlineKeyboardButton("🔥 ClassPlus Inside", callback_data="cp_inside")],
    [InlineKeyboardButton("⬅️ Back Main", callback_data="back_to_main"),
     InlineKeyboardButton("➡️ Next Page", callback_data="page_2")]
])

PAGE_2 = InlineKeyboardMarkup([
    [InlineKeyboardButton("🏆 Rank Plus", callback_data="rank_p"),
     InlineKeyboardButton("🎯 Selection Way", callback_data="selection_w")],
    [InlineKeyboardButton("📘 Prep-Online", callback_data="prep_o"),
     InlineKeyboardButton("⌨️ Taiyari Karlo", callback_data="taiyari")],
    [InlineKeyboardButton("⬅️ Back Page", callback_data="page_1"),
     InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
])

# -------------------------- COMMANDS -------------------------- #

@app.on_message(filters.command("sudo") & filters.user(OWNER_ID))
async def add_sudo_with_time(_, message):
    args = message.command
    if len(args) < 3:
        return await message.reply_text("❌ **Format:** `/sudo [USER_ID] [DAYS]`")
    try:
        user_id, days = str(args[1]), int(args[2])
        expiry_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        SUDO_DATA[user_id] = expiry_date
        save_sudo_users(SUDO_DATA)
        await message.reply_text(f"✅ **Premium Added!**\n> 👤 **User:** `{user_id}`\n> ⏳ **Expiry:** `{expiry_date}`")
    except Exception as e:
        await message.reply_text(f"⚠️ **Error:** {str(e)}")

@app.on_message(filters.command("check") & filters.private)
async def check_expiry(_, message):
    u_id = str(message.from_user.id)
    if int(u_id) == OWNER_ID:
        return await message.reply_text("👑 **Status:** `OWNER` (Lifetime)")
    if u_id in SUDO_DATA:
        expiry = SUDO_DATA[u_id]
        await message.reply_text(f"💎 **Premium Status:** `ACTIVE`\n📅 **Expiry:** `{expiry}`")
    else:
        await message.reply_text("❌ **Premium Status:** `INACTIVE`")

@app.on_message(filters.command(["start", "apps"]))
async def start_cmd(_, message):
    try:
        join = await subscribe(_, message)
        if join == 1: return
    except: pass
    u_name, u_id = message.from_user.first_name, message.from_user.id
    if u_id not in USER_STATS: USER_STATS[u_id] = 0
    await message.reply_photo(photo=IMG_MAIN, caption=get_main_caption(u_name, u_id), reply_markup=MAIN_BUTTONS)

# -------------------------- CALLBACK HANDLER (FIXED) -------------------------- #

@app.on_callback_query()
async def handle_callback(_, query):
    data = query.data
    u_id = query.from_user.id
    u_name = query.from_user.first_name

    if data == "back_to_main":
        await safe_edit(query, get_main_caption(u_name, u_id), MAIN_BUTTONS)
    elif data == "page_1":
        await safe_edit(query, "📂 **Without Login Menu - Page 1**", PAGE_1)
    elif data == "page_2":
        await safe_edit(query, "📂 **Without Login Menu - Page 2**", PAGE_2)
    elif data == "selection_w":
        if not is_premium(u_id):
            return await query.answer("❌ Premium Required!", show_alert=True)
        await query.answer("🔎 Fetching batches...", show_alert=False)
        try:
            batches = sw1.fetch_active_batches()
            list_text = "📚 **Available Batches:**\n\n"
            for i, b in enumerate(batches, 1):
                list_text += f"{i}. {b.get('title')} - ₹{b.get('price', 'None')}\n"
            list_text += "\n📝 **Send batch number to extract**"
            await safe_edit(query, list_text, PAGE_2)
        except Exception as e:
            await safe_edit(query, f"⚠️ Error:
