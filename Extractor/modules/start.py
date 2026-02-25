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

# -------------------------- HANDLERS -------------------------- #

@app.on_message(filters.command(["start", "apps"]))
async def start_cmd(_, message):
    try:
        join = await subscribe(_, message)
        if join == 1: return
    except Exception: pass # Skip subscribe errors
    
    u_name, u_id = message.from_user.first_name, message.from_user.id
    if u_id not in USER_STATS: USER_STATS[u_id] = 0
    
    caption = get_main_caption(u_name, u_id)
    await message.reply_photo(photo=IMG_MAIN, caption=caption, reply_markup=MAIN_BUTTONS)

@app.on_callback_query()
async def handle_callback(_, query):
    data = query.data
    u_name, u_id = query.from_user.first_name, query.from_user.id

    # --- Navigation with Safe Edit ---
    if data == "back_to_main":
        await safe_edit(query, get_main_caption(u_name, u_id), MAIN_BUTTONS)
    
    elif data == "page_1":
        await safe_edit(query, "📂 **Without Login Menu - Page 1**", PAGE_1)

    elif data == "page_2":
        await safe_edit(query, "📂 **Without Login Menu - Page 2**", PAGE_2)

    # --- NOVA STYLE TRIGGER ---
    elif data == "selection_w":
        if u_id not in SUDO_USERS and u_id != OWNER_ID:
            return await query.answer("❌ Premium Feature! Contact @ONeX_sell", show_alert=True)

        await query.answer("🔎 Fetching batches...", show_alert=False)
        try:
            batches = sw1.fetch_active_batches()
            if not batches:
                await safe_edit(query, "❌ No active batches found.", PAGE_2)
                return

            buttons = []
            for b in batches:
                b_id = b.get('id')
                b_name = b.get('title')[:25]
                buttons.append([InlineKeyboardButton(f"📁 {b_name}", callback_data=f"sw_{b_id}_{b_name[:15]}")])
            
            buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="page_2")])
            await safe_edit(query, "📚 **Available Batches:**\nSelect a batch to extract:", InlineKeyboardMarkup(buttons))

        except Exception as e:
            await safe_edit(query, f"⚠️ Error: {str(e)}", PAGE_2)

    elif data.startswith("sw_"):
        if u_id not in SUDO_USERS and u_id != OWNER_ID:
            return await query.answer("❌ Access Denied!", show_alert=True)

        parts = data.split("_")
        course_id, c_name = parts[1], parts[2] if len(parts) > 2 else "Batch"
        
        start_time = time.time()
        await query.answer("⏳ Extraction Shuru...", show_alert=False)
        await safe_edit(query, "⚡ Please wait, your file will be sent soon... ⚡", None)
        
        try:
            res = sw1.get_final_data(course_id, mode="1")
            if res["text"]:
                file = io.BytesIO(res["text"].encode())
                file.name = f"{c_name}_enc.txt"
                
                time_taken = f"{int(time.time() - start_time)}s"
                current_dt = datetime.now().strftime('%d-%m-%Y  %H:%M:%S')
                
                report = f"""
⚡ **Selection Way Extraction Report** ⚡

📚 **Batch Name:** `{c_name}`
━━━━━━━━━━━━━━━━━━━━━━━━
• 📱 **App:** Selection Way
• 🆔 **Batch ID:** `{course_id}`
• 🔗 **Total Content:** {res['total']}
• 📹 **Videos:** {res['videos']} | 📄 **PDFs:** {res['pdfs']}
• 🖼️ **Thumbnail:** [Click Here To View](https://telegra.ph/file/default_image.jpg)
• ⏱️ **Total Time Taken:** {time_taken}
• 📅 **Date-Time:** {current_dt}
• 📄 **User ID:** `{u_id}`
• 💬 **Username:** @{query.from_user.username or "None"}
━━━━━━━━━━━━━━━━━━━━━━━━
• 👤 **Extracted by:** 𝓞𝓝𝓮𝓧 🐺
━━━━━━━━━━━━━━━━━━━━━━━━
"""
                await query.message.reply_document(document=file, caption=report)
                USER_STATS[u_id] = USER_STATS.get(u_id, 0) + 1
                await query.message.delete()
            else:
                await query.answer("❌ No links found!", show_alert=True)
        except Exception as e:
            await safe_edit(query, f"⚠️ Error: {str(e)}", PAGE_2)

    elif data == "home_":
        await query.message.delete()
