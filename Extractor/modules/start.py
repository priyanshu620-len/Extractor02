import os
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Modules Import (Ensure filenames match your repo)
from Extractor.modules.CP_PRO import process_classplus
# from Extractor.modules.sway1 import process_sway   <-- Inhe bhi aise hi import karein
# from Extractor.modules.future_kul import process_fk

import config

# Bot Setup
app = Client(
    "ExtractorBot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

# --- START COMMAND ---
@app.on_message(filters.command("start") & filters.private)
async def start_handler(bot: Client, m: Message):
    mention = m.from_user.mention
    start_text = (
        f"👋 **Welcome {mention}!**\n\n"
        "Main ek advanced Content Extractor Bot hoon. "
        "Niche diye gaye buttons se extraction start karein."
    )
    
    buttons = [
        [InlineKeyboardButton("📱 Classplus (PRO)", callback_data="run_cp")],
        [InlineKeyboardButton("✨ Sway Module", callback_data="run_sway")],
        [InlineKeyboardButton("🚀 Future Kul", callback_data="run_fk")]
    ]
    
    await m.reply_text(start_text, reply_markup=InlineKeyboardMarkup(buttons))

# --- COMMAND HANDLERS ---

# 1. Classplus PRO Command
@app.on_message(filters.command("cp") & filters.incoming)
async def cp_cmd_handler(bot: Client, m: Message):
    user_id = m.from_user.id
    # Premium check yahan add kar sakte hain
    try:
        await process_classplus(bot, m, user_id)
    except Exception as e:
        logging.error(f"CP Error: {e}")
        await m.reply_text("⚠️ **Error:** Module not responding.")

# 2. Sway Command
@app.on_message(filters.command("sway") & filters.incoming)
async def sway_cmd_handler(bot: Client, m: Message):
    user_id = m.from_user.id
    # await process_sway(bot, m, user_id) # Call your sway module
    await m.reply_text("Sway Module is being integrated...")

# --- CALLBACK HANDLERS (Buttons ke liye) ---
@app.on_callback_query()
async def cb_handler(bot: Client, query):
    user_id = query.from_user.id
    
    if query.data == "run_cp":
        await query.message.delete()
        await process_classplus(bot, query.message, user_id)
        
    elif query.data == "run_sway":
        await query.answer("Sway module starting...", show_alert=True)
        # await process_sway(bot, query.message, user_id)

# --- IDLE & RUN ---
if __name__ == "__main__":
    print("✅ Bot is live and anti-spam mode is ON!")
    app.run()
