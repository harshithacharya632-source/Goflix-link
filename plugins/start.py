import random
import humanize
import asyncio
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery, WebAppInfo
from info import URL, LOG_CHANNEL, SHORTLINK, BOT_TOKEN, ADMINS
from urllib.parse import quote_plus
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
from TechVJ.util.human_readable import humanbytes
from database.users_chats_db import db
from utils import temp, get_shortlink
import requests


@Client.on_message(filters.command("start") & filters.incoming)
async def start_command(client, message):
    if len(message.command) > 1:
        # Handle deep linking
        if message.command[1].startswith('file_'):
            file_id = message.command[1].split('_')[1]
            await message.reply_text(
                f"**Welcome to FileToLink Bot!**\n\n"
                f"File ID: `{file_id}`\n\n"
                "To convert files, simply send me any file (video, document, audio, image)."
            )
        return
    
    # Regular start command
    await message.reply_text(
        script.START_TXT.format(message.from_user.mention),
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📚 Help", callback_data="help"),
                InlineKeyboardButton("📊 About", callback_data="about")
            ],
            [
                InlineKeyboardButton("🔐 Close", callback_data="close")
            ]
        ])
    )


@Client.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def file_to_link_handler(client, message):
    """Handle all file types for conversion"""
    # Get the file info based on media type
    if message.video:
        file = message.video
        media_type = "video"
    elif message.document:
        file = message.document
        media_type = "document"
    elif message.audio:
        file = message.audio
        media_type = "audio"
    elif message.photo:
        # For photos, use the largest size
        file = message.photo
        media_type = "photo"
        file_id = file.file_id
        file_name = "photo.jpg"
        file_size = file.file_size if hasattr(file, 'file_size') else 0
    else:
        await message.reply_text("❌ Unsupported file type")
        return

    if media_type != "photo":
        file_name = getattr(file, 'file_name', 'Unknown File')
        file_size = getattr(file, 'file_size', 0)
        file_id = getattr(file, 'file_id', None)

    if not file_id:
        await message.reply_text("❌ Could not get file information")
        return

    user_id = message.from_user.id
    username = message.from_user.mention

    # Forward file to LOG_CHANNEL
    try:
        if media_type == "photo":
            log_msg = await client.send_photo(
                chat_id=LOG_CHANNEL,
                photo=file_id,
                caption=f"**📁 File Converted**\n\n**User:** {username}\n**User ID:** `{user_id}`\n**File:** {file_name}\n**Type:** {media_type}"
            )
        else:
            log_msg = await client.send_cached_media(
                chat_id=LOG_CHANNEL,
                file_id=file_id,
                caption=f"**📁 File Converted**\n\n**User:** {username}\n**User ID:** `{user_id}`\n**File:** {file_name}\n**Type:** {media_type}"
            )
    except Exception as e:
        await message.reply_text("❌ Error processing file. Please try again.")
        return

    # Generate links
    try:
        if media_type == "photo":
            # For photos, use direct download
            stream_url = f"{URL}/download_photo/{log_msg.id}"
            download_url = stream_url
            fileName = file_name
        else:
            fileName = get_name(log_msg)
            fileHash = get_hash(log_msg)
            
            # Generate appropriate URLs
            if media_type == "video":
                stream_url = f"{URL}/player_html?message_id={log_msg.id}&title={quote_plus(fileName)}"
                download_url = f"{URL}/download/{log_msg.id}/{quote_plus(fileName)}?hash={fileHash}"
            else:
                stream_url = f"{URL}/download/{log_msg.id}/{quote_plus(fileName)}?hash={fileHash}"
                download_url = stream_url

        # Generate shortlinks if enabled
        if SHORTLINK:
            try:
                stream_url = await get_shortlink(stream_url)
                download_url = await get_shortlink(download_url)
            except Exception as e:
                print(f"Shortlink error: {e}")
                # Continue with normal URLs

    except Exception as e:
        await message.reply_text("❌ Error generating links")
        return

    # Create buttons based on file type
    if media_type == "video":
        buttons = [
            [
                InlineKeyboardButton("🎥 Stream Online", url=stream_url),
                InlineKeyboardButton("📥 Download", url=download_url)
            ],
            [
                InlineKeyboardButton("📱 Web Player", web_app=WebAppInfo(url=stream_url))
            ]
        ]
    elif media_type == "audio":
        buttons = [
            [
                InlineKeyboardButton("🎵 Listen Online", url=stream_url),
                InlineKeyboardButton("📥 Download", url=download_url)
            ]
        ]
    elif media_type == "photo":
        buttons = [
            [
                InlineKeyboardButton("🖼️ View Image", url=stream_url),
                InlineKeyboardButton("📥 Download", url=download_url)
            ]
        ]
    else:  # documents
        buttons = [
            [
                InlineKeyboardButton("📄 View Online", url=stream_url),
                InlineKeyboardButton("📥 Download", url=download_url)
            ]
        ]

    buttons.append([InlineKeyboardButton("🔄 Convert Another", switch_inline_query_current_chat="")])

    # Prepare message text
    file_size_str = humanbytes(file_size) if file_size > 0 else "Unknown size"
    
    msg_text = f"""**✅ File Converted Successfully!**

📂 **File Name:** `{file_name}`
📦 **File Size:** `{file_size_str}`
📄 **File Type:** `{media_type.title()}`

⚡ **Your links are ready!**
• {'Stream online' if media_type == 'video' else 'View online'}
• Download directly to your device
{'• Watch in web app for best experience' if media_type == 'video' else ''}

⏰ **Note:** Links will expire in 24 hours
🔒 **Privacy:** This message will auto-delete in 5 minutes"""

    # Send the result
    try:
        main_msg = await message.reply_text(
            text=msg_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
    except Exception as e:
        await message.reply_text("❌ Error sending result message")
        return

    # Auto-delete function
    async def auto_delete():
        try:
            await asyncio.sleep(300)  # 5 minutes
            await main_msg.delete()
            print(f"✅ Auto-deleted message for user {user_id}")
        except Exception as e:
            print(f"❌ Error deleting message for user {user_id}: {e}")

    # Run auto-delete in background
    asyncio.create_task(auto_delete())


@Client.on_callback_query(filters.regex("help"))
async def help_callback(client, callback_query):
    await callback_query.message.edit_text(
        script.HELP_TXT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Home", callback_data="home"),
             InlineKeyboardButton("📊 About", callback_data="about")],
            [InlineKeyboardButton("🔐 Close", callback_data="close")]
        ])
    )


@Client.on_callback_query(filters.regex("about"))
async def about_callback(client, callback_query):
    await callback_query.message.edit_text(
        script.ABOUT_TXT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Home", callback_data="home"),
             InlineKeyboardButton("📚 Help", callback_data="help")],
            [InlineKeyboardButton("🔐 Close", callback_data="close")]
        ])
    )


@Client.on_callback_query(filters.regex("home"))
async def home_callback(client, callback_query):
    await callback_query.message.edit_text(
        script.START_TXT.format(callback_query.from_user.mention),
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📚 Help", callback_data="help"),
                InlineKeyboardButton("📊 About", callback_data="about")
            ],
            [
                InlineKeyboardButton("🔐 Close", callback_data="close")
            ]
        ])
    )


@Client.on_callback_query(filters.regex("close"))
async def close_callback(client, callback_query):
    await callback_query.message.delete()


@Client.on_message(filters.command("help") & filters.incoming)
async def help_command(client, message):
    await message.reply_text(
        script.HELP_TXT,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔐 Close", callback_data="close")]
        ])
    )


@Client.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats_command(client, message):
    try:
        total_users = await db.total_users_count()
        total_chats = await db.total_chat_count()
        
        stats_text = f"""📊 **Bot Statistics**

👥 **Total Users:** `{total_users}`
💬 **Total Chats:** `{total_chats}`
⚡ **Bot Status:** Running

**Admin Commands:**
• /broadcast - Broadcast message
• /stats - Show statistics
• /users - List all users"""
        
        await message.reply_text(stats_text)
        
    except Exception as e:
        await message.reply_text(f"❌ Error fetching statistics: {str(e)}")


@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def broadcast_command(client, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /broadcast <message>")
        return
    
    broadcast_msg = message.text.split(" ", 1)[1]
    users = await db.get_all_users()
    
    success = 0
    failed = 0
    
    await message.reply_text("🔄 Starting broadcast...")
    
    for user in users:
        try:
            await client.send_message(
                chat_id=int(user['id']),
                text=broadcast_msg
            )
            success += 1
            await asyncio.sleep(0.1)  # Prevent flooding
        except Exception:
            failed += 1
    
    await message.reply_text(
        f"📢 **Broadcast Completed**\n\n"
        f"✅ Success: `{success}`\n"
        f"❌ Failed: `{failed}`\n"
        f"📊 Total: `{success + failed}`"
    )


print("✅ Start plugin loaded successfully!")
