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

# -------------------------- DATABASE & CONFIG -------------------------- #
USER_STATS = {} # Bot restart hone par reset hoga (Real stats ke liye MongoDB use karein)

# Images (Yahan apne images ke link dalein)
IMG_MAIN = random.choice(script.IMG) if script.IMG else "https://telegra.ph/file/default.jpg"

# -------------------------- UI CAPTION -------------------------- #

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
💬 **Need Help?** Tap 'Developer' below for support.
━━━━━━━━━━━━━━━━━━━━━━━━"""

# -------------------------- KEYBOARDS -------------------------- #

MAIN_BUTTONS = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🔑 Login Required", callback_data="login_section"),
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

LOGIN_BUTTONS = InlineKeyboardMarkup([
    [InlineKeyboardButton("📚 Physics Wallah", callback_data="pw_")],
    [InlineKeyboardButton("🎓 Khan GS App", callback_data="khan_")],
    [InlineKeyboardButton("🏫 Career Will", callback_data="careerwill_")],
    [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
])

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
        InlineKeyboardButton("🏫 ClassPlus", callback_data="classplus_"),
        InlineKeyboardButton("🔥 ClassPlus Inside", callback_data="cp_inside")
    ],
    [
        InlineKeyboardButton("⬅️ Back Main", callback_data="back_to_main"),
        InlineKeyboardButton("➡️ Next Page", callback_data="page_2")
    ]
])

PAGE_2 = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🧮 Verbal Maths", callback_data="v_maths"),
        InlineKeyboardButton("🏗️ Civil Guruji", callback_data="civil_g")
    ],
    [
        InlineKeyboardButton("🏆 Rank Plus", callback_data="rank_p"),
        InlineKeyboardButton("🎯 Selection Way", callback_data="selection_w")
    ],
    [
        InlineKeyboardButton("⬅️ Back Page", callback_data="page_1"),
        InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")
    ]
])

TEACH_ZONE_MENU = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("📚 Study Azadi", callback_data="s_azadi"),
        InlineKeyboardButton("🏫 Bishewari Study", callback_data="bishewari")
    ],
    [
        InlineKeyboardButton("📘 Aarohi Online", callback_data="aarohi"),
        InlineKeyboardButton("🎓 Alisira Academy", callback_data="alisira")
    ],
    [InlineKeyboardButton("⬅️ Back to W/O", callback_data="page_1")]
])

# -------------------------- LOGGING & HANDLERS -------------------------- #

async def log_user_activity(user):
    if user.id not in USER_STATS:
        USER_STATS[user.id] = 0
    log_msg = f"#NewUser\n👤 **Name:** {user.first_name}\n🆔 **ID:** `{user.id}`\n━━━━━━━━━━━━━━━━━━━━"
    try: await app.send_message(CHANNEL_ID, log_msg)
    except: pass

@app.on_message(filters.command(["start", "apps"]))
async def start_cmd(_, message):
    join = await subscribe(_, message)
    if join == 1: return
    await log_user_activity(message.from_user)
    caption = get_main_caption(message.from_user.first_name, message.from_user.id)
    await message.reply_photo(photo=IMG_MAIN, caption=caption, reply_markup=MAIN_BUTTONS)

@app.on_callback_query()
async def handle_callback(_, query):
    data = query.data
    u_name, u_id = query.from_user.first_name, query.from_user.id

    if data == "back_to_main":
        await query.message.edit_caption(caption=get_main_caption(u_name, u_id), reply_markup=MAIN_BUTTONS)
    
    elif data == "page_1":
        await query.message.edit_caption(caption="📂 **Without Login - Page 1**", reply_markup=PAGE_1)

    elif data == "page_2":
        await query.message.edit_caption(caption="📂 **Without Login - Page 2**", reply_markup=PAGE_2)

    elif data == "login_section":
        await query.message.edit_caption(caption="🔐 **Login Required Section**", reply_markup=LOGIN_BUTTONS)

    elif data == "teach_zone_menu":
        await query.message.edit_caption(caption="🎓 **Teach Zone Platforms**", reply_markup=TEACH_ZONE_MENU)

    elif data == "view_stats":
        stats = USER_STATS.get(u_id, 0)
        await query.answer(f"📊 Stats: Aapne {stats} extractions ki hain!", show_alert=True)

    elif data == "search_api":
        search_prompt = await app.ask(query.message.chat.id, "🔍 **Enter App Name to find API:**")
        # Yahan search logic add karein jaisa humne pehle discuss kiya tha
        await query.message.reply_text(f"Searching for: {search_prompt.text}...")

    elif data == "home_":
        await query.message.delete()

# -------------------------- ADMIN BROADCAST -------------------------- #

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_handler(_, message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a message with /broadcast")
    count = 0
    for user_id in USER_STATS.keys():
        try:
            await message.reply_to_message.copy(user_id)
            count += 1
        except: pass
    await message.reply_text(f"✅ Broadcast complete to {count} users.")
