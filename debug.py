# debug.py
import os
from pyrogram import Client

print("=== DEBUG: Checking Environment Variables ===")

# Check if variables exist
api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')
log_channel = os.environ.get('LOG_CHANNEL')

print(f"API_ID: {api_id}")
print(f"API_HASH: {'***' if api_hash else 'MISSING'}")
print(f"BOT_TOKEN: {'***' if bot_token else 'MISSING'}")
print(f"LOG_CHANNEL: {log_channel}")

if not all([api_id, api_hash, bot_token, log_channel]):
    print("❌ ERROR: One or more environment variables are missing!")
    print("Please check your Render environment variables")
else:
    print("✅ All environment variables are present")

# Test channel access
if log_channel:
    try:
        app = Client("debug_bot", api_id=int(api_id), api_hash=api_hash, bot_token=bot_token)
        
        async def test_channel():
            await app.start()
            try:
                # Test if we can access the channel
                chat = await app.get_chat(int(log_channel))
                print(f"✅ Channel access successful!")
                print(f"Channel Title: {chat.title}")
                print(f"Channel ID: {chat.id}")
                return True
            except Exception as e:
                print(f"❌ Channel access failed: {e}")
                return False
            finally:
                await app.stop()
        
        import asyncio
        asyncio.run(test_channel())
    except Exception as e:
        print(f"❌ Bot startup failed: {e}")

print("=== DEBUG END ===")
