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
    [InlineKeyboardButton("⚔️ CDS Journey", callback_data="cds_j"),
     InlineKeyboardButton("🎓 Vinayak Coaching", callback_data="vinayak")],
    [InlineKeyboardButton("⬅️ Back Main", callback_data="back_to_main"),
     InlineKeyboardButton("➡️ Next Page", callback_data="page_2")]
])

PAGE_2 = InlineKeyboardMarkup([
    [InlineKeyboardButton("🧮 Verbal Maths", callback_data="v_maths"),
     InlineKeyboardButton("🏗️ Civil Guruji", callback_data="civil_g")],
    [InlineKeyboardButton("🪨 Geo. Concept", callback_data="geo_c"),
     InlineKeyboardButton("🧭 Path Finder", callback_data="path_f")],
    [InlineKeyboardButton("🏆 Rank Plus", callback_data="rank_p"),
     InlineKeyboardButton("🎯 Selection Way", callback_data="selection_w")],
    [InlineKeyboardButton("📘 Prep-Online", callback_data="prep_o"),
     InlineKeyboardButton("⌨️ Taiyari Karlo", callback_data="taiyari")],
    [InlineKeyboardButton("🔬 Repro Neet", callback_data="repro"),
     InlineKeyboardButton("⚡ Sambhavam IAS", callback_data="sambhavam")],
    [InlineKeyboardButton("🧬 IFAS Edutech", callback_data="ifas"),
     InlineKeyboardButton("🩺 AyurGuide v2", callback_data="ayur")],
    [InlineKeyboardButton("🏫 G.S. Vision", callback_data="gs_v"),
     InlineKeyboardButton("✨ Future Kul", callback_data="future")],
    [InlineKeyboardButton("✨ Sarvam Online", callback_data="sarvam"),
     InlineKeyboardButton("🔥 N Prep", callback_data="n_prep")],
    [InlineKeyboardButton("🔐 TNC Nursing", callback_data="tnc")],
    [InlineKeyboardButton("⬅️ Back Page", callback_data="page_1"),
     InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
])

# -------------------------- SUDO COMMANDS -------------------------- #

@app.on_message(filters.command("sudo") & filters.user(OWNER_ID))
async def add_sudo(_, message):
    if len(message.command) != 2:
        return await message.reply_text("Usage: `/sudo [USER_ID]`")
    user_id = int(message.text.split(None, 1)[1])
    if user_id not in SUDO_USERS:
        SUDO_USERS.append(user_id)
        await message.reply_text(f"✅ User `{user_id}` added to Sudo List.")
    else:
        await message.reply_text("❌ User is already in Sudo List.")

@app.on_message(filters.command("rmsudo") & filters.user(OWNER_ID))
async def remove_sudo(_, message):
    if len(message.command) != 2:
        return await message.reply_text("Usage: `/rmsudo [USER_ID]`")
    user_id = int(message.text.split(None, 1)[1])
    if user_id in SUDO_USERS:
        SUDO_USERS.remove(user_id)
        await message.reply_text(f"✅ User `{user_id}` removed from Sudo List.")
    else:
        await message.reply_text("❌ User not found in Sudo List.")

# -------------------------- HANDLERS -------------------------- #

@app.on_message(filters.command(["start", "apps"]))
async def start_cmd(_, message):
    try:
        join = await subscribe(_, message)
        if join == 1: return
    except Exception: pass
    
    u_name, u_id = message.from_user.first_name, message.from_user.id
    if u_id not in USER_STATS: USER_STATS[u_id] = 0
    
    caption = get_main_caption(u_name, u_id)
    await message.reply_photo(photo=IMG_MAIN, caption=caption, reply_markup=MAIN_BUTTONS)

@app.on_callback_query()
async def handle_callback(_, query):
    data = query.data
    u_name, u_id = query.from_user.first_name, query.from_user.id

    if data == "back_to_main":
        await safe_edit(query, get_main_caption(u_name, u_id), MAIN_BUTTONS)
    elif data == "page_1":
        await safe_edit(query, "📂 **Without Login Menu - Page 1**", PAGE_1)
    elif data == "page_2":
        await safe_edit(query, "📂 **Without Login Menu - Page 2**", PAGE_2)
    elif data == "selection_w":
        if u_id not in SUDO_USERS and u_id != OWNER_ID:
            return await query.answer("❌ Premium Feature!", show_alert=True)
        await query.answer("🔎 Fetching batches...", show_alert=False)
        try:
            batches = sw1.fetch_active_batches()
            list_text = "📚 **Available Batches:**\n\n"
            for i, b in enumerate(batches, 1):
                list_text += f"{i}. {b.get('title')} - ₹{b.get('price', 'None')}\n"
            list_text += "\n📝 **Send batch number to extract**"
            nav_buttons = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back Page", callback_data="page_2"), 
                                              InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]])
            await safe_edit(query, list_text, nav_buttons)
        except Exception as e:
            await safe_edit(query, f"⚠️ Error: {str(e)}", PAGE_2)
    elif data == "home_":
        await query.message.delete()

# --- EXTRACTION HANDLER WITH BLOCKQUOTES ---
@app.on_message(filters.text & filters.incoming & filters.private)
async def batch_number_handler(client, message):
    u_id = message.from_user.id
    text = message.text.strip()
    if text.isdigit():
        if u_id not in SUDO_USERS and u_id != OWNER_ID:
            return await message.reply("❌ Access Denied!")
        try:
            batches = sw1.fetch_active_batches()
            index = int(text) - 1
            if 0 <= index < len(batches):
                selected_batch = batches[index]
                course_id = selected_batch.get('id')
                status = await message.reply("⚡ **Please wait, your file will be sent soon...** ⚡")
                start_time = time.time()
                res = sw1.get_final_data(course_id, mode="1")
                if res["text"]:
                    file = io.BytesIO(res["text"].encode())
                    c_name = res["title"]
                    file.name = f"{c_name.replace(' ', '_')}_enc.txt"
                    time_taken = f"{int(time.time() - start_time)}s"
                    current_dt = datetime.now().strftime('%d-%m-%Y  %H:%M:%S')
                    
                    report = f"""
✨ **𝖲𝖤𝖫𝖤𝖢𝖳𝖨𝖮𝖭 𝖶𝖠𝖸 𝖤𝖷𝖳𝖱𝖠𝖢𝖳𝖨𝖮𝖭** ✨
━━━━━━━━━━━━━━━━━━━━━━━━━━
> 📚 **𝖡𝖺𝗍𝖼𝗁:** `{c_name}`
> 🆔 **𝖨𝖣:** `{course_id}`
━━━━━━━━━━━━━━━━━━━━━━━━━━
> ◈ 📱 **𝖠𝗉𝗉:** Selection Way
> ◈ 📂 **𝖢𝗈𝗇𝗍𝖾𝗇𝗍:** {res.get('total', 0)} Items
> ◈ 📹 **𝖵𝗂𝖽𝖾𝗈𝗌:** {res.get('videos', 0)}  |  📄 **𝖯𝖣𝖥𝗌:** {res.get('pdfs', 0)}
━━━━━━━━━━━━━━━━━━━━━━━━━━
> ⏱️ **𝖳𝗂𝗆𝖾:** {time_taken}
> 📅 **𝖣𝖺𝗍𝖾:** {current_dt}
━━━━━━━━━━━━━━━━━━━━━━━━━━
◈ 🖼️ **𝖳𝗁𝗎𝗆𝖻:** [𝖢𝗅𝗂𝖼𝗄 𝖧𝖾𝗋𝖾 𝖳𝗈 𝖵𝗂𝖾𝗐](https://telegra.ph/file/default_image.jpg)
◈ 👤 **𝖴𝗌𝖾𝗋:** `{u_id}`
◈ 🔗 **𝖡𝗒:** 𓆩 𝓞𝓝𝓮𝓧 𓆪 🐺
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
