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

# Main Menu (Image 2 style)
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
        InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/ONeX_sell")
    ],
    [InlineKeyboardButton("📄 Get OMR", callback_data="get_omr")],
    [InlineKeyboardButton("❌ Close Menu", callback_data="home_")]
])

# Page 1 - Without Login (Image 1 style)
PAGE_1 = InlineKeyboardMarkup([
    [InlineKeyboardButton("👑 Premium++", callback_data="prem_plus")],
    [InlineKeyboardButton("🔐 VideoCrypt", callback_data="videocrypt")],
    [InlineKeyboardButton("🎓 Teach Zone", callback_data="teach_zone_menu")],
    [
        InlineKeyboardButton("🪄 AppX Test", callback_data="appx"),
        InlineKeyboardButton("📚 Study IQ", callback_data="studyiq")
    ],
    [
        InlineKeyboardButton("🏛️ DAMS Delhi", callback_data="dams"),
        InlineKeyboardButton("⭐ Pinnacle", callback_data="pinnacle")
    ],
    [
        InlineKeyboardButton("🎭 Pappu", callback_data="pappu"),
        InlineKeyboardButton("📝 Test Paper", callback_data="testpaper")
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

# Page 2 - Without Login (Image 3 style)
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
        InlineKeyboardButton("⌨️ Taiyari Karlo", callback_data="taiyari")
    ],
    [
        InlineKeyboardButton("🔬 Repro Neet", callback_data="repro"),
        InlineKeyboardButton("⚡ Sambhavam IAS", callback_data="sambhavam")
    ],
    [
        InlineKeyboardButton("🧬 IFAS Edutech", callback_data="ifas"),
        InlineKeyboardButton("🩺 AyurGuide v2", callback_data="ayur")
    ],
    [
        InlineKeyboardButton("🏫 G.S. Vision", callback_data="gs_v"),
        InlineKeyboardButton("✨ Future Kul", callback_data="future")
    ],
    [
        InlineKeyboardButton("✨ Sarvam Online", callback_data="sarvam"),
        InlineKeyboardButton("🔥 N Prep", callback_data="n_prep")
    ],
    [InlineKeyboardButton("🔐 TNC Nursing", callback_data="tnc")],
    [
        InlineKeyboardButton("⬅️ Back Page", callback_data="page_1"),
        InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")
    ]
])

# Teach Zone Platforms Menu (New Screenshot style)
TEACH_ZONE_MENU = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("📚 Study Azadi", callback_data="s_azadi"),
        InlineKeyboardButton("🏫 Bishewari Study", callback_data="bishewari")
    ],
    [
        InlineKeyboardButton("📘 Aarohi Online", callback_data="aarohi"),
        InlineKeyboardButton("🎓 Alisira Academy", callback_data="alisira")
    ],
    [
        InlineKeyboardButton("🧑‍🏫 Bhanu Sir Acad.", callback_data="bhanu_sir"),
        InlineKeyboardButton("🪜 Bridge To Success", callback_data="bridge")
    ],
    [
        InlineKeyboardButton("🌎 Divya Straglobal", callback_data="divya"),
        InlineKeyboardButton("💡 Econominds", callback_data="econominds")
    ],
    [
        InlineKeyboardButton("🛡️ Exam Kavach", callback_data="exam_k"),
        InlineKeyboardButton("🏛️ Ganga Var Inst.", callback_data="ganga_var")
    ],
    [
        InlineKeyboardButton("🎯 Janata Career", callback_data="janata"),
        InlineKeyboardButton("📖 Jiya Jiyan Shin.", callback_data="jiya_j")
    ],
    [
        InlineKeyboardButton("🏫 National Acad.", callback_data="national"),
        InlineKeyboardButton("📈 Study Trend", callback_data="s_trend")
    ],
    [
        InlineKeyboardButton("⚡ Study Mafia", callback_data="s_mafia"),
        InlineKeyboardButton("🧠 Teaching Job Man.", callback_data="t_job")
    ],
    [
        InlineKeyboardButton("🚀 The Fastest Acad.", callback_data="fastest"),
        InlineKeyboardButton("📐 Vishal Sir Maths", callback_data="vishal_sir")
    ],
    [InlineKeyboardButton("🧩 Saurav Tutorial", callback_data="saurav")],
    [InlineKeyboardButton("⬅️ Back to W/O", callback_data="page_1")]
])

# -------------------------- LOGGING & HANDLERS -------------------------- #

async def log_user_activity(user):
    log_msg = f"#NewUser #Activity\n👤 **Name:** {user.first_name}\n🆔 **ID:** `{user.id}`\n🔗 **User:** @{user.username if user.username else 'None'}\n━━━━━━━━━━━━━━━━━━━━"
    try: 
        await app.send_message(CHANNEL_ID, log_msg)
    except: pass

@app.on_message(filters.command(["start", "apps"]))
async def start_cmd(_, message):
    join = await subscribe(_, message)
    if join == 1: return
    
    await log_user_activity(message.from_user)
    caption = get_main_caption(message.from_user.first_name, message.from_user.id)
    
    await message.reply_photo(
        photo=random.choice(script.IMG), 
        caption=caption,
        reply_markup=MAIN_BUTTONS
    )

@app.on_callback_query()
async def handle_callback(_, query):
    data = query.data
    u_name = query.from_user.first_name
    u_id = query.from_user.id

    if data == "back_to_main":
        await query.message.edit_caption(caption=get_main_caption(u_name, u_id), reply_markup=MAIN_BUTTONS)
    
    elif data == "page_1":
        await query.message.edit_caption(caption="📂 **Without Login Menu - Page 1**", reply_markup=PAGE_1)

    elif data == "page_2":
        await query.message.edit_caption(caption="📂 **Without Login Menu - Page 2**", reply_markup=PAGE_2)

    elif data == "teach_zone_menu":
        await query.message.edit_caption(caption="🎓 **Teach Zone Platforms Menu Opened**", reply_markup=TEACH_ZONE_MENU)

    elif data == "home_":
        await query.message.delete()

    # --- Extraction logic (Example Callbacks) ---
    elif data == "rg_vikramjeet":     
        await appex_v3_txt(app, query.message, "rgvikramjeetapi.akamai.net.in/", "RG Vikramjeet")
    
    elif data == "rwa_":   
        await appex_v3_txt(app, query.message, "rozgarapinew.teachx.in", "Rojgar with Ankit")

    elif data == "close_data":
        await query.message.delete()
