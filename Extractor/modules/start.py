import re
import random
from pyrogram import filters
from Extractor import app
from config import OWNER_ID, SUDO_USERS, CHANNEL_ID
from Extractor.core import script
from Extractor.core.func import subscribe, chk_user
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from Extractor.modules.classplus import classplus_txt
from Extractor.modules.exampur import exampur_txt
from Extractor.modules.appex_v3 import appex_v3_txt
from Extractor.modules.khan import khan_login
from Extractor.modules.kdlive import kdlive
from Extractor.modules.pw import  pw_login
from Extractor.modules.careerwill import career_will
from Extractor.modules.getappxotp import send_otp
from Extractor.modules.findapi import findapis_extract
from Extractor.modules.utk import handle_utk_logic
from Extractor.modules.iq import handle_iq_logic
from Extractor.modules.adda import adda_command_handler

# -------------------------- UI TEXTS & CONFIG -------------------------- #

def get_main_caption(name, user_id):
    return f"""💎 **Welcome to Premium Extractor Bot** 💎
━━━━━━━━━━━━━━━━━━━━━━━━
👤 **User:** {name}
🆔 **ID:** `{user_id}`
━━━━━━━━━━━━━━━━━━━━━━━━
⚙️ **Choose your mode below:**

🔐 **Login Required:** For apps that need ID & Password.
🚀 **Without Login:** Extract freely from supported apps.
━━━━━━━━━━━━━━━━━━━━━━━━
🧠 **Tip:** Use correct input format for smooth extraction.
💬 **Need Help?** Tap 'Developer' below for direct support.
━━━━━━━━━━━━━━━━━━━━━━━━"""

# -------------------------- KEYBOARDS -------------------------- #

# Main Menu
MAIN_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🔐 Login Required", callback_data="login_section"),
        InlineKeyboardButton("🟢 Without Login", callback_data="page_1")
    ],
    [
        InlineKeyboardButton("🔍 Search AppX API", callback_data="search_api"),
        InlineKeyboardButton("📽️ YT Extractor", callback_data="yt_ext")
    ],
    [
        InlineKeyboardButton("📋 TXT → HTML", callback_data="txt_html"),
        InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/ONeX_sell")
    ],
    [
        InlineKeyboardButton("📊 My Stats", callback_data="view_stats"),
        InlineKeyboardButton("❌ Close Menu", callback_data="home_")
    ]
])

# Login Required Menu (Warning Removed)
LOGIN_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("📲 AppX", callback_data="appx_login"),
        InlineKeyboardButton("📱 AppX V2", callback_data="appx_v2"),
        InlineKeyboardButton("📲 AppX V3", callback_data="appx_v3")
    ],
    [
        InlineKeyboardButton("🌱 CP Without Test", callback_data="cp_no_test"),
        InlineKeyboardButton("🏫 CP With Test", callback_data="cp_test")
    ],
    [
        InlineKeyboardButton("💎 Will Pappu", callback_data="will_pappu"),
        InlineKeyboardButton("🧩 Gyan Academy", callback_data="gyan_acad")
    ],
    [
        InlineKeyboardButton("📚 Khan Global Studies", callback_data="khan_"),
        InlineKeyboardButton("🚧 Fliqi Tech", callback_data="fliqi")
    ],
    [
        InlineKeyboardButton("🌐 Appx API", callback_data="appx_api"),
        InlineKeyboardButton("🌐 WebSankul", callback_data="websankul")
    ],
    [InlineKeyboardButton("⬅️ Back to main menu", callback_data="back_to_main")]
])

# Without Login - Page 1
PAGE_1 = InlineKeyboardMarkup([
    [InlineKeyboardButton("👑 Premium++", callback_data="prem_plus")],
    [InlineKeyboardButton("🔐 VideoCrypt", callback_data="videocrypt")],
    [InlineKeyboardButton("🎓 Teach Zone", callback_data="teach_zone_menu")],
    [
        InlineKeyboardButton("🪄 AppX Test", callback_data="appx_test"),
        InlineKeyboardButton("📚 Study IQ", callback_data="studyiq")
    ],
    [
        InlineKeyboardButton("🏛️ DAMS Delhi", callback_data="dams"),
        InlineKeyboardButton("⭐ Pinnacle", callback_data="pinnacle")
    ],
    [
        InlineKeyboardButton("🎭 Pappu", callback_data="pappu"),
        InlineKeyboardButton("📝 Test Paper", callback_data="test_paper")
    ],
    [
        InlineKeyboardButton("🏫 ClassPlus", callback_data="classplus_"),
        InlineKeyboardButton("🔥 ClassPlus Inside", callback_data="cp_inside")
    ],
    [
        InlineKeyboardButton("🎯 JRF ADDA", callback_data="jrf_adda"),
        InlineKeyboardButton("🧪 J Chemistry", callback_data="j_chem")
    ],
    [
        InlineKeyboardButton("⚔️ CDS Journey", callback_data="cds_j"),
        InlineKeyboardButton("🎓 Vinayak Coaching", callback_data="vinayak")
    ],
    [
        InlineKeyboardButton("⬅️ Back Main", callback_data="back_to_main"),
        InlineKeyboardButton("➡️ Next Page", callback_data="page_2")
    ]
])

# Without Login - Page 2
PAGE_2 = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🧮 Verbal Maths", callback_data="v_maths"),
        InlineKeyboardButton("🏗️ Civil Guruji", callback_data="civil_g")
    ],
    [
        InlineKeyboardButton("🪨 Geo. Concept", callback_data="geo_c"),
        InlineKeyboardButton("🧭 Path Finder", callback_data="path_f")
    ],
    [
        InlineKeyboardButton("🏆 Rank Plus", callback_data="rank_p"),
        InlineKeyboardButton("🎯 Selection Way", callback_data="selection_w")
    ],
    [
        InlineKeyboardButton("📘 Prep-Online", callback_data="prep_o"),
        InlineKeyboardButton("⌨️ Taiyari Karlo", callback_data="taiy
