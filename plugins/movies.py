import os
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from TechVJ.bot import TechVJBot

CHANNELS = os.environ.get("CHANNELS", "-1001234567890,-1009876543210")
channel_list = [ch.strip() for ch in CHANNELS.split(",")]

# Command to list movies from private channels
@TechVJBot.on_message(filters.command("movies"))
async def list_movies(client, message):
    for channel in channel_list:
        try:
            messages = await client.get_chat_history(channel, limit=10)  # list 10 per channel
        except Exception as e:
            await message.reply_text(f"❌ Could not read from {channel}\nError: {e}")
            continue

        if not messages:
            await message.reply_text(f"No movies found in {channel}.")
            continue

        await message.reply_text(f"🎬 Movies from {channel}:")
        for msg in messages:
            if msg.video or msg.document:
                caption = msg.video.file_name if msg.video else msg.document.file_name
                # Save reference (channel + message_id)
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("▶️ Play Online", callback_data=f"play_{channel}_{msg.id}")]]
                )
                await message.reply_text(f"🎞️ {caption}", reply_markup=keyboard)

# Callback handler to stream movie
@TechVJBot.on_callback_query(filters.regex(r"play_(.+)"))
async def play_movie(client, callback_query):
    data = callback_query.data.split("_", 2)
    channel = data[1]
    msg_id = int(data[2])

    try:
        # Forward or copy the original movie message
        await client.copy_message(
            chat_id=callback_query.message.chat.id,
            from_chat_id=channel,
            message_id=msg_id,
        )
        await callback_query.answer("🎥 Streaming...")
    except Exception as e:
        await callback_query.answer("❌ Error streaming file", show_alert=True)
