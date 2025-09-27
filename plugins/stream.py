from pyrogram import filters
from TechVJ.bot import TechVJBot

# Replace with your private channel IDs
CHANNELS = [-1001234567890, -1009876543210]

@TechVJBot.on_message(filters.command("movie"))
async def get_movie(client, message):
    try:
        # Example: fetch latest message from first private channel
        msg = await client.get_messages(chat_id=CHANNELS[0], message_ids=1234)  
        
        # Safest way → copy the message back to user
        await msg.copy(chat_id=message.chat.id)

    except Exception as e:
        await message.reply_text(f"❌ Could not fetch movie.\n\nError: {e}")
