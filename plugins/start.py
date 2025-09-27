import random
import humanize
import asyncio
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery, WebAppInfo
from info import URL, LOG_CHANNEL, SHORTLINK, BOT_TOKEN
from urllib.parse import quote_plus
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
from TechVJ.util.human_readable import humanbytes
from database.users_chats_db import db
from utils import temp, get_shortlink
import requests


@Client.on_message(filters.command("start") & filters.incoming)
async def start_command(client, message):
    # Your start command handler here
    await message.reply_text("Welcome to Goflix Bot!")


@Client.on_message(filters.private & (filters.document | filters.video))
async def stream_start(client, message):
    # Get the file info
    file = getattr(message, message.media.value)
    filename = file.file_name
    filesize = humanize.naturalsize(file.file_size)
    fileid = file.file_id
    user_id = message.from_user.id
    username = message.from_user.mention

    # Forward file to LOG_CHANNEL
    try:
        log_msg = await client.send_cached_media(
            chat_id=LOG_CHANNEL,
            file_id=fileid,
        )
    except Exception as e:
        await message.reply_text("❌ Error forwarding file to log channel")
        return

    fileName = get_name(log_msg)

    # -----------------------------
    # Generate stream & download links using your Flask app
    # -----------------------------
    try:
        # Use your Flask app endpoints instead of Telegram CDN
        stream_url = f"{URL}/player_html?message_id={log_msg.id}&title={quote_plus(filename)}"
        download_url = f"{URL}/download/{str(log_msg.id)}/{quote_plus(fileName)}?hash={get_hash(log_msg)}"
        
        # Generate shortlinks if enabled
        if SHORTLINK:
            try:
                stream_url = await get_shortlink(stream_url)
                download_url = await get_shortlink(download_url)
            except Exception as e:
                print(f"Shortlink error: {e}")
                # Continue with normal URLs if shortlink fails

    except Exception as e:
        await message.reply_text("❌ Error generating links")
        return

    # Log message
    try:
        await log_msg.reply_text(
            text=f"•• ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ꜰᴏʀ ɪᴅ #{user_id} \n•• ᴜꜱᴇʀɴᴀᴍᴇ : {username} \n\n•• ᖴᎥᒪᗴ Nᗰᴇ : {fileName}",
            quote=True,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton("🚀 Fast Download 🚀", url=download_url),
                    InlineKeyboardButton("🖥 Watch online 🖥", url=stream_url)
                ]]
            )
        )
    except Exception as e:
        print(f"Error sending log message: {e}")

    # Buttons for user
    rm = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("sᴛʀᴇᴀᴍ 🖥", url=stream_url),
                InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ 📥", url=download_url)
            ],
            [
                InlineKeyboardButton("• ᴡᴀᴛᴄʜ ɪɴ ᴡᴇʙ ᴀᴘᴘ •", web_app=WebAppInfo(url=stream_url))
            ]
        ]
    )

    # Message text
    msg_text = """<i><u>𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 !</u></i>\n\n
<b>📂 Fɪʟᴇ ɴᴀᴍᴇ :</b> <i>{}</i>\n\n
<b>📦 Fɪʟᴇ ꜱɪᴢᴇ :</b> <i>{}</i>\n\n
<b>⏰ Nᴏᴛᴇ : Tʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇᴅ ɪɴ 5 ᴍɪɴᴜᴛᴇs</b>\n
<b>🚸 Lɪɴᴋ ᴡɪʟʟ ᴇxᴘɪʀᴇ ɪɴ 24 ʜᴏᴜʀs</b>"""

    # Send message and store the message object
    try:
        main_msg = await message.reply_text(
            text=msg_text.format(
                filename,
                filesize,
            ),
            quote=True,
            disable_web_page_preview=True,
            reply_markup=rm
        )
    except Exception as e:
        await message.reply_text("❌ Error sending message")
        return

    # Auto-delete function
    async def auto_delete():
        try:
            await asyncio.sleep(300)  # 5 minutes
            await main_msg.delete()
            print(f"✅ Auto-deleted message for user {user_id}")
        except Exception as e:
            print(f"❌ Error deleting message for user {user_id}: {e}")

    # Run the auto-delete in background
    asyncio.create_task(auto_delete())


# Add help command
@Client.on_message(filters.command("help") & filters.incoming)
async def help_command(client, message):
    help_text = """
🤖 **Goflix Bot Help**

📤 **How to use:**
1. Send me any video or document file
2. I'll generate streaming and download links
3. Use the web app for best viewing experience

🔗 **Available commands:**
/start - Start the bot
/help - Show this help message

⚡ **Features:**
- Instant streaming links
- Fast download options
- Web app player
- Auto-delete for privacy
"""
    await message.reply_text(help_text)


# Add stats command for admin
@Client.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats_command(client, message):
    total_users = await db.total_users_count()
    total_chats = await db.total_chat_count()
    
    stats_text = f"""
📊 **Bot Statistics**

👥 **Total Users:** {total_users}
💬 **Total Chats:** {total_chats}
⚡ **Bot Status:** Running
"""
    await message.reply_text(stats_text)
