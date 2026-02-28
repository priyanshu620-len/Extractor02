import os
import time
import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode

# ========== CONFIGURATION ==========
# Aapka Brand Logo Jo Aapne Provide Kiya Hai
MY_BRAND_THUMB = "https://i.postimg.cc/Y0x5RtMH/Whats-App-Image-2026-02-28-at-6-57-52-PM.jpg"

# ========== MODULES IMPORT ==========
try:
    from Extractor.modules.sw1 import get_final_data as sw1_process
    from Extractor.modules.futurekul import get_final_data as fk_process 
except ImportError as e:
    print(f"⚠️ Critical Import Error: {e}. Check your module files.")

# ========== START COMMAND WITH THUMBNAIL & BUTTONS ==========
@Client.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    welcome_text = (
        "✨ **ONeX EXTRACTOR v3.0** ✨\n"
        "«────────────────────────────»\n"
        "👋 Hello {},\n\n"
        "Welcome to the most advanced extraction bot. Niche diye gaye buttons ka use karke platform select karein:\n\n"
        "🛡️ **System Status:** `Online` ✅\n"
        "«────────────────────────────»\n"
        "⚡ *Powered by ONeX Extractor*"
    ).format(message.from_user.mention)

    # Inline Buttons Layout
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📱 Selection Way", callback_data="sw_info"),
            InlineKeyboardButton("🎓 FutureKul", callback_data="fk_info")
        ],
        [
            InlineKeyboardButton("👤 Developer", url="https://t.me/ONeX_sell")
        ]
    ])
    
    # Photo ke saath welcome message
    await message.reply_photo(
        photo=MY_BRAND_THUMB,
        caption=welcome_text,
        reply_markup=buttons
    )

# ========== CALLBACK HANDLER (Button Click) ==========
@Client.on_callback_query()
async def callback_handler(client: Client, query: CallbackQuery):
    if query.data == "sw_info":
        await query.answer()
        await query.message.edit_caption(
            caption="🚀 **SELECTION WAY EXTRACTION**\n\n"
                    "Extract karne ke liye niche wala format use karein:\n"
                    "👉 `/sw <batch_id>`\n\n"
                    "Example: `/sw 698487d5fdd21a8a2d1a5270`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_start")]])
        )
    
    elif query.data == "fk_info":
        await query.answer()
        await query.message.edit_caption(
            caption="🎓 **FUTUREKUL EXTRACTION**\n\n"
                    "Extract karne ke liye niche wala format use karein:\n"
                    "👉 `/fk <batch_id>`\n\n"
                    "Example: `/fk 1234567890`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_start")]])
        )
    
    elif query.data == "back_start":
        welcome_text = (
            "✨ **ONeX EXTRACTOR v3.0** ✨\n"
            "«────────────────────────────»\n"
            "👋 Hello {},\n\n"
            "Platform select karein:\n\n"
            "🛡️ **System Status:** `Online` ✅\n"
            "«────────────────────────────»\n"
            "⚡ *Powered by ONeX Extractor*"
        ).format(query.from_user.mention)
        
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📱 Selection Way", callback_data="sw_info"),
                InlineKeyboardButton("🎓 FutureKul", callback_data="fk_info")
            ],
            [
                InlineKeyboardButton("👤 Developer", url="https://t.me/ONeX_sell")
            ]
        ])
        await query.message.edit_caption(caption=welcome_text, reply_markup=buttons)

# ========== EXTRACTION HANDLER (REUSABLE) ==========
async def run_extraction(message: Message, platform_name, process_func):
    if len(message.command) < 2:
        return await message.reply_text(f"❌ **Usage:** `/{message.command[0]} <batch_id>`")
    
    course_id = message.command[1]
    status_msg = await message.reply_text(f"🔎 **Extracting from {platform_name}... Please wait.**")
    
    try:
        data = process_func(
            course_id, 
            tg_user_id=message.from_user.id, 
            tg_username=message.from_user.username or "N/A",
            extractor_name="ONeX"
        )
        
        suffix = "SW" if platform_name == "Selection Way" else "FK"
        safe_title = data['title'].replace(' ', '_')
        file_name = f"{safe_title}_{suffix}.txt"
        
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(data['text'])
            
        # Sending Document with ONeX Logo as Thumbnail
        await message.reply_document(
            document=file_name,
            thumb=MY_BRAND_THUMB,
            caption=data['report'],
            parse_mode=ParseMode.MARKDOWN
        )
        
        await status_msg.delete()
        if os.path.exists(file_name):
            os.remove(file_name)
            
    except Exception as e:
        await status_msg.edit(f"❌ **{platform_name} Error:** `{str(e)}`" )

# ========== COMMAND REGISTERING ==========
@Client.on_message(filters.command("sw"))
async def sw_handler(client: Client, message: Message):
    await run_extraction(message, "Selection Way", sw1_process)

@Client.on_message(filters.command("fk"))
async def fk_handler(client: Client, message: Message):
    await run_extraction(message, "FutureKul", fk_process)
