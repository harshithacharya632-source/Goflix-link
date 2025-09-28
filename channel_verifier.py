# channel_verifier.py
from pyrogram import Client
from info import API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL
import asyncio

async def verify_channel_access():
    """Verify if bot can access the log channel"""
    app = Client("verify_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
    
    await app.start()
    try:
        # Test channel access
        chat = await app.get_chat(LOG_CHANNEL)
        print("✅ CHANNEL ACCESS VERIFIED!")
        print(f"Channel Title: {chat.title}")
        print(f"Channel ID: {chat.id}")
        print(f"Channel Username: @{chat.username}" if chat.username else "Private Channel")
        return True
    except Exception as e:
        print(f"❌ CHANNEL ACCESS FAILED: {e}")
        print("\n🔧 SOLUTIONS:")
        print("1. Make sure the bot is added to the channel as ADMIN")
        print("2. Check if LOG_CHANNEL ID is correct")
        print("3. Ensure the channel exists and bot has permissions")
        return False
    finally:
        await app.stop()

# Run verification
if __name__ == "__main__":
    asyncio.run(verify_channel_access())
