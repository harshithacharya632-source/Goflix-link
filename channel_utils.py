# channel_utils.py
from info import LOG_CHANNEL, ADMINS
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import time

class SafeChannel:
    def __init__(self):
        self.channel_id = LOG_CHANNEL
        self.fallback_admin = ADMINS[0] if ADMINS else None
    
    async def send_message(self, client, text, reply_markup=None, disable_web_page_preview=True):
        """
        SAFELY send message to channel or fallback to admin
        """
        targets = []
        
        # Add channel if available
        if self.channel_id:
            targets.append(self.channel_id)
        
        # Add admin as fallback
        if self.fallback_admin:
            targets.append(self.fallback_admin)
        
        # If no targets, just log to console
        if not targets:
            print(f"📢 [NO CHANNEL] {text}")
            return False
        
        success = False
        for target in targets:
            try:
                await client.send_message(
                    chat_id=target,
                    text=text,
                    reply_markup=reply_markup,
                    disable_web_page_preview=disable_web_page_preview
                )
                print(f"✅ Message sent to {target}")
                success = True
                break  # Stop after first successful send
            except Exception as e:
                print(f"❌ Failed to send to {target}: {e}")
                continue
        
        return success

# Create global instance
safe_channel = SafeChannel()

# Specific function for your file conversion logs
async def send_file_conversion_log(client, user_data, file_data, download_url=None):
    """
    Send the file conversion log in your specific format
    """
    message = f"""
📁 **File Converted Successfully!**

👤 **User:** {user_data.get('username', '♨️Goflix Bot')}
🆔 **User ID:** `{user_data.get('id', '7011228023')}`
📄 **File:** `{file_data.get('name', 'Unknown')}`
📊 **Type:** {file_data.get('type', 'document')}
📦 **Size:** {file_data.get('size', 'N/A')}

⏰ **Time:** {time.strftime('%H:%M')}

✅ **Conversion completed successfully!**
    """
    
    # Create buttons
    keyboard = None
    if download_url:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌐 View Online", url=download_url)],
            [InlineKeyboardButton("📥 Download", url=download_url)],
            [InlineKeyboardButton("🔄 Convert Another", callback_data="convert_another")]
        ])
    
    return await safe_channel.send_message(client, message, keyboard)

# Test function
async def test_channel_access(client):
    """Test if we can access the channel"""
    if LOG_CHANNEL:
        try:
            chat = await client.get_chat(LOG_CHANNEL)
            return f"✅ Channel accessible: {chat.title}"
        except Exception as e:
            return f"❌ Channel error: {e}"
    else:
        return "ℹ️ No channel set, using admin fallback"
