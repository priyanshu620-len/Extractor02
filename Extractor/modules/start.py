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

# -------------------------- HANDLERS -------------------------- #

@app.on_message(filters.command(["start", "apps"]))
async def start_cmd(_, message):
    join = await subscribe(_, message)
    if join == 1: return
    
    u_name, u_id = message.from_user.first_name, message.from_user.id
    if u_id not in USER_STATS: USER_STATS[u_id] = 0
    
    caption = get_main_caption(u_name, u_id)
    await message.reply_photo(photo=IMG_MAIN, caption=caption, reply_markup=MAIN_BUTTONS)

@app.on_callback_query()
async def handle_callback(_, query):
    data = query.data
    u_name, u_id = query.from_user.first_name, query.from_user.id

    if data == "back_to_main":
        await query.message.edit_caption(caption=get_main_caption(u_name, u_id), reply_markup=MAIN_BUTTONS)
    
    elif data == "page_1":
        await query.message.edit_caption(caption="📂 **Without Login Menu - Page 1**", reply_markup=PAGE_1)

    elif data == "page_2":
        await query.message.edit_caption(caption="📂 **Without Login Menu - Page 2**", reply_markup=PAGE_2)

    # --- NOVA STYLE TRIGGER ---
    elif data == "selection_w":
        if u_id not in SUDO_USERS and u_id != OWNER_ID:
            return await query.answer("❌ This is a Premium Feature! Contact @ONeX_sell to upgrade.", show_alert=True)

        await query.answer("🔎 Fetching batches...", show_alert=False)
        try:
            batches = sw1.fetch_active_batches()
            if not batches:
                await query.message.edit_caption(caption="❌ No active batches found.", reply_markup=PAGE_2)
                return

            buttons = []
            for b in batches:
                b_id = b.get('id')
                b_name = b.get('title')[:25]
                # 64-byte limit ke liye callback chhota rakha hai
                buttons.append([InlineKeyboardButton(f"📁 {b_name}", callback_data=f"sw_{b_id}_{b_name[:15]}")])
            
            buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="page_2")])
            
            try:
                await query.message.edit_caption(
                    caption="📚 **Available Batches:**\n\nJis batch ka TXT chahiye use select karein:",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
            except Exception: pass

        except Exception as e:
            await query.message.edit_caption(caption=f"⚠️ Error: {str(e)}", reply_markup=PAGE_2)

    elif data.startswith("sw_"):
        if u_id not in SUDO_USERS and u_id != OWNER_ID:
            return await query.answer("❌ Access Denied!", show_alert=True)

        parts = data.split("_")
        course_id = parts[1]
        c_name = parts[2] if len(parts) > 2 else "Batch"
        
        start_time = time.time()
        await query.answer("⏳ Extraction Shuru...", show_alert=False)
        await query.message.edit_caption(caption=f"⚡ Please wait, your file will be sent soon... ⚡")
        
        try:
            # sw1.py se dictionary format wala data lena
            res = sw1.get_final_data(course_id, mode="1") 
            links = res["text"]
            
            if links:
                file = io.BytesIO(links.encode())
                file.name = f"{c_name}_enc.txt"
                
                time_taken = f"{int(time.time() - start_time)}s"
                current_dt = datetime.now().strftime('%d-%m-%Y  %H:%M:%S')
                
                # Professional Report Caption (As per screenshots)
                report_caption = f"""
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
• 💬 **Username:** @{query.from_user.username if query.from_user.username else "None"}
━━━━━━━━━━━━━━━━━━━━━━━━
• 👤 **Extracted by:** 𝓞𝓝𝓮𝓧 🐺
━━━━━━━━━━━━━━━━━━━━━━━━
"""
                await query.message.reply_document(document=file, caption=report_caption)
                USER_STATS[u_id] = USER_STATS.get(u_id, 0) + 1
                await query.message.delete()
            else:
                await query.answer("❌ No links found!", show_alert=True)
        except Exception as e:
            await query.message.edit_caption(caption=f"⚠️ Error: {str(e)}", reply_markup=PAGE_2)

    elif data == "home_":
        await query.message.delete()
