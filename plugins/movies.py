import os
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from TechVJ.bot import TechVJBot  # use your main bot client

# Read channels from environment variable
CHANNELS = os.environ.get("CHANNELS", "-1001234567890,-1009876543210")  
channel_list = [ch.strip() for ch in CHANNELS.split(",")]

# Command to list movies from private channels
@TechVJBot.on_message(filters.command("movies"))
async def list_movies(client, message):
    for channel in channel_list:
        try:
            messages = await client.get_chat_history(channel, limit=50)
        except Exception as e:
            await message.reply_text(f"❌ Could not read from {channel}\nError: {e}")
            continue

        if not messages:
            await message.reply_text(f"No movies found in {channel}.")
            continue

        await message.reply_text(f"🎬 Movies from {channel}:")
        for msg in messages:
            if msg.video or msg.document:
                file_id = msg.video.file_id if msg.video else msg.document.file_id
                caption = msg.video.file_name if msg.video else msg.document.file_name

                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("▶️ Play Online", callback_data=f"play_{file_id}")]]
                )
                await message.reply_text(f"🎞️ {caption}", reply_markup=keyboard)

# Callback handler to stream movie
@TechVJBot.on_callback_query(filters.regex(r"play_(.+)"))
async def play_movie(client, callback_query):
    file_id = callback_query.data.split("_", 1)[1]
    await callback_query.message.reply_video(file_id, caption="Enjoy your movie! 🎥")
    await callback_query.answer()
