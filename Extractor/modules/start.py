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
        with open(SUDO_DATA_FILE, "r") as f:
            return json.load(f)
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

# ... (PAGE_1 aur PAGE_2 keyboard same rahenge)

# -------------------------- PREMIUM COMMANDS -------------------------- #

@app.on_message(filters.command("sudo") & filters.user(OWNER_ID))
async def add_sudo_with_time(_, message):
    args = message.command
    if len(args) < 3:
        return await message.reply_text("❌ **Format:** `/sudo [USER_ID] [DAYS]`\nExample: `/sudo 12345 30`")
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
    """Allows user to check their own premium status"""
    u_id = str(message.from_user.id)
    if int(u_id) == OWNER_ID:
        return await message.reply_text("👑 **Status:** `OWNER` (Lifetime Access)")
    
    if u_id in SUDO_DATA:
        expiry = SUDO_DATA[u_id]
        await message.reply_text(f"💎 **Premium Status:** `ACTIVE`\n📅 **Expiry Date:** `{expiry}`")
    else:
        await message.reply_text("❌ **Premium Status:** `INACTIVE`\nContact @ONeX_sell to buy subscription.")

# -------------------------- HANDLERS -------------------------- #

@app.on_message(filters.command(["start", "apps"]))
async def start_cmd(_, message):
    try:
        join = await subscribe(_, message)
        if join == 1: return
    except Exception: pass
    u_name, u_id = message.from_user.first_name, message.from_user.id
    if u_id not in USER_STATS: USER_STATS[u_id] = 0
    await message.reply_photo(photo=IMG_MAIN, caption=get_main_caption(u_name, u_id), reply_markup=MAIN_BUTTONS)

# --- BATCH NUMBER HANDLER ---
@app.on_message(filters.text & filters.incoming & filters.private)
async def batch_number_handler(client, message):
    u_id = message.from_user.id
    text = message.text.strip()
    if text.isdigit():
        if not is_premium(u_id):
            return await message.reply("❌ **Premium Required!**\nType /check to see status or contact @ONeX_sell.")
        try:
            batches = sw1.fetch_active_batches()
            index = int(text) - 1
            if 0 <= index < len(batches):
                selected_batch = batches[index]
                course_id = selected_batch.get('id')
                status = await message.reply("⚡ **Please wait...**")
                start_time = time.time()
                res = sw1.get_final_data(course_id, mode="1")
                if res["text"]:
                    file = io.BytesIO(res["text"].encode())
                    c_name = res["title"]
                    file.name = f"{c_name.replace(' ', '_')}_enc.txt"
                    
                    # Full Blockquote Stylish Report
                    report = f"""
✨ **𝖲𝖤𝖫𝖤𝖢𝖳𝖨𝖮𝖭 𝖶𝖠𝖸 𝖤𝖷𝖳𝖱𝖠𝖢𝖳𝖨𝖮𝖭** ✨
━━━━━━━━━━━━━━━━━━━━━━━━━━
> 📚 **𝖡𝖺𝗍𝖼𝗁:** `{c_name}`
> 🆔 **𝖨𝖣:** `{course_id}`
> ━━━━━━━━━━━━━━━━━━━━━━━━
> ◈ 📱 **𝖠𝗉𝗉:** Selection Way
> ◈ 📂 **𝖢𝗈𝗇𝗍𝖾𝗇𝗍:** {res.get('total', 0)} Items
> ◈ 📹 **𝖵𝗂𝖽𝖾𝗈𝗌:** {res.get('videos', 0)}  |  📄 **𝖯𝖣𝖥𝗌:** {res.get('pdfs', 0)}
> ━━━━━━━━━━━━━━━━━━━━━━━━
> ⏱️ **𝖳𝗂𝗆𝖾:** {int(time.time() - start_time)}s
> 📅 **𝖣𝖺𝗍𝖾:** {datetime.now().strftime('%d-%m-%Y  %H:%M:%S')}
> 🖼️ **𝖳𝗁𝗎𝗆𝖻:** [𝖢𝗅𝗂𝖼𝗄 𝖧𝖾𝗋𝖾 𝖳𝗈 𝖵𝗂𝖾𝗐](https://telegra.ph/file/default_image.jpg)
> ━━━━━━━━━━━━━━━━━━━━━━━━
> 👤 **𝖴𝗌𝖾𝗋:** `{u_id}`
> 🔗 **𝖡𝗒:** 𓆩 𝓞𝓝𝓮𝓧 𓆪 🐺
━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
                    await message.reply_document(document=file, caption=report)
                    await status.delete()
                    USER_STATS[u_id] = USER_STATS.get(u_id, 0) + 1
                else:
                    await status.edit("❌ No links found!")
            else:
                await message.reply("❌ Invalid number!")
        except Exception as e:
            await message.reply(f"⚠️ Error: {str(e)}")
