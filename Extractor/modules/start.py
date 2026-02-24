import re
import random
from pyrogram import filters
from Extractor import app
from config import OWNER_ID, SUDO_USERS, CHANNEL_ID
from Extractor.core import script
from Extractor.core.func import subscribe, chk_user
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
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

# -------------------------- UI TEXTS -------------------------- #

MAIN_CAPTION = """💎 **Welcome to Premium Extractor Bot** 💎
━━━━━━━━━━━━━━━━━━━━━━━━
⚙️ **Choose your mode below:**

🔐 **Login Required:** For apps that need ID & Password.
🚀 **Without Login:** Extract freely from supported apps.
━━━━━━━━━━━━━━━━━━━━━━━━
🧠 **Tip:** Use correct input format for smooth extraction.
💬 **Need Help?** Tap 'Developer' below for direct support.
━━━━━━━━━━━━━━━━━━━━━━━━"""

# -------------------------- KEYBOARDS -------------------------- #

# Main Menu Keyboard
MAIN_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🔑 Login Required", callback_data="login_section"),
        InlineKeyboardButton("🟢 Without Login", callback_data="page_1")
    ],
    [
        InlineKeyboardButton("📄 Compare Files", callback_data="compare"),
        InlineKeyboardButton("📽️ YT Extractor", callback_data="yt_ext")
    ],
    [
        InlineKeyboardButton("📋 TXT → HTML", callback_data="txt_html"),
        InlineKeyboardButton("👨‍💻 Developer", url=f"tg://user?id={8301160173}")
    ],
    [InlineKeyboardButton("📄 Get OMR", callback_data="get_omr")],
    [InlineKeyboardButton("❌ Close Menu", callback_data="home_")]
])

# Login Section Keyboard
LOGIN_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("📚 Physics Wallah", callback_data="pw_")],
    [InlineKeyboardButton("🎓 Khan GS App", callback_data="khan_")],
    [InlineKeyboardButton("🏫 Career Will", callback_data="careerwill_")],
    [InlineKeyboardButton("🏛️ KD Live", callback_data="kdlive_")],
    [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
])

# Page 1 - Without Login
PAGE_1 = InlineKeyboardMarkup([
    [InlineKeyboardButton("👑 Premium++", callback_data="prem_plus")],
    [InlineKeyboardButton("🔐 VideoCrypt", callback_data="videocrypt")],
    [InlineKeyboardButton("🎓 Teach Zone", callback_data="teachzone")],
    [
        InlineKeyboardButton("🪄 AppX Test", callback_data="appx"),
        InlineKeyboardButton("📚 Study IQ", callback_data="studyiq")
    ],
    [
        InlineKeyboardButton("🏛️ DAMS Delhi", callback_data="dams"),
        InlineKeyboardButton("⭐ Pinnacle", callback_data="pinnacle")
    ],
    [
        InlineKeyboardButton("⬅️ Back Main", callback_data="back_to_main"),
        InlineKeyboardButton("➡️ Next Page", callback_data="page_2")
    ]
])

# Page 2 - Academy List (From your original list)
PAGE_2 = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🚀 Aman Sir", callback_data="aman_sir"),
        InlineKeyboardButton("🚀 Exampur", callback_data="exampur_")
    ],
    [
        InlineKeyboardButton("🚀 Army Study", callback_data="army_study"),
        InlineKeyboardButton("🚀 Ashish Lec", callback_data="Ashish_lec")
    ],
    [
        InlineKeyboardButton("🚀 RG Vikramjeet", callback_data="rg_vikramjeet"),
        InlineKeyboardButton("🚀 RWA", callback_data="rwa_")
    ],
    [
        InlineKeyboardButton("⬅️ Back Page", callback_data="page_1"),
        InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")
    ]
])

# -------------------------- HANDLERS -------------------------- #

@app.on_message(filters.command(["start", "apps"]))
async def start_cmd(_, message):
    join = await subscribe(_, message)
    if join == 1:
        return
    await message.reply_photo(
        photo=random.choice(script.IMG), 
        caption=MAIN_CAPTION,
        reply_markup=MAIN_BUTTONS
    )

@app.on_callback_query()
async def handle_callback(_, query):
    data = query.data

    # --- Navigation Logic ---
    if data == "back_to_main":
        await query.message.edit_caption(caption=MAIN_CAPTION, reply_markup=MAIN_BUTTONS)
    
    elif data == "login_section":
        await query.message.edit_caption(caption="🔐 **Login Required Section**", reply_markup=LOGIN_BUTTONS)

    elif data == "page_1":
        await query.message.edit_caption(caption="📂 **Without Login Menu - Page 1**", reply_markup=PAGE_1)

    elif data == "page_2":
        await query.message.edit_caption(caption="📂 **Without Login Menu - Page 2**", reply_markup=PAGE_2)

    elif data == "home_":
        await query.message.delete()

    # --- Extraction Logic ---
    elif data == "pw_":
        await pw_login(app, query.message)
    
    elif data == "khan_":
        await khan_login(app, query.message)

    elif data == "rg_vikramjeet":     
        api = "rgvikramjeetapi.akamai.net.in/"
        name = "RG Vikramjeet"
        await appex_v3_txt(app, query.message, api, name)
    
    elif data == "rwa_":   
        api = "rozgarapinew.teachx.in"
        name = "Rojgar with Ankit"
        await appex_v3_txt(app, query.message, api, name)

    elif data == "aman_sir":     
        api = "amansirenglishapi.classx.co.in"
        name = "Aman Sir English"
        await appex_v3_txt(app, query.message, api, name)

    elif data == "exampur_":
        await appex_v3_txt(app, query.message)

    # ... Your other specific platform callbacks go here ...

    elif data == "close_data":
        await query.message.delete()
        if query.message.reply_to_message:
            await query.message.reply_to_message.delete()
