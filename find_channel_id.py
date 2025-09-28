# find_channel_id.py
from pyrogram import Client
import os

# Use your actual credentials from Render
api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')

app = Client("my_bot", api_id=int(api_id), api_hash=api_hash, bot_token=bot_token)

@app.on_message()
async def message_handler(client, message):
    if message.chat:
        print("=== CHANNEL INFO ===")
        print(f"Chat ID: {message.chat.id}")
        print(f"Chat Title: {message.chat.title}")
        print(f"Chat Username: @{message.chat.username}" if message.chat.username else "No username")
        print(f"Chat Type: {message.chat.type}")
        print("====================")
        
        # Write to a file for easy copying
        with open("channel_info.txt", "w") as f:
            f.write(f"CHANNEL_ID={message.chat.id}")
        
        await app.stop()

app.run()
