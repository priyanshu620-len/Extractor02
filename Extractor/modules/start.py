import re
import io
import time
import random
import asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from Extractor import app
from config import OWNER_ID, SUDO_USERS, CHANNEL_ID 
from Extractor.core import script
from Extractor.core.func import subscribe, chk_user

# --- MODULE IMPORTS ---
from Extractor.modules import sw1 

# -------------------------- DATABASE & CONFIG -------------------------- #
USER_STATS = {} 
IMG_MAIN = random.choice(script.IMG) if script.IMG else "https://telegra.ph/file/default_image.jpg"

# -------------------------- HELPERS -------------------------- #

async def safe_edit(query, caption, reply_markup):
    """Prevents bot from crashing on MESSAGE_NOT_MODIFIED error"""
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
    [InlineKeyboardButton("🎓 Teach Zone", callback_data="teach_zone_menu")],
    [InlineKeyboardButton("🪄 AppX Test", callback_data="appx_test"),
     InlineKeyboardButton("📚 Study IQ", callback_data="studyiq")],
    [InlineKeyboardButton("🏛️ DAMS Delhi", callback_data="dams"),
     InlineKeyboardButton("⭐ Pinnacle", callback_data="pinnacle")],
    [InlineKeyboardButton("🎭 Pappu", callback_data="pappu"),
     InlineKeyboardButton("📝 Test Paper", callback_data="test_paper")],
    [InlineKeyboardButton("🏫 ClassPlus", callback_data="classplus_"),
     InlineKeyboardButton("🔥 ClassPlus Inside", callback_data="cp_inside")],
    [InlineKeyboardButton("🎯 JRF ADDA", callback_data="jrf_adda"),
     InlineKeyboardButton("🧪 J Chemistry", callback_data="j_chem")],
    [InlineKeyboardButton("⚔️ CDS
