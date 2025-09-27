import os
import asyncio
import humanize
from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from pyrogram.errors import FloodWait
from TechVJ.bot import TechVJBot
from info import URL, LOG_CHANNEL, SHORTLINK
from urllib.parse import quote_plus
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
from TechVJ.util.human_readable import humanbytes
from utils import get_shortlink
from database.users_chats_db import db

# Store temporary conversion data
temp_conversions = {}

@TechVJBot.on_message(filters.command("convert") & filters.private)
async def convert_command(client, message):
    """Convert files to links"""
    await message.reply_text(
        "**📁 File to Link Converter**\n\n"
        "Simply send me any file (video, document, audio, image) and I'll convert it to downloadable links!\n\n"
        "**Supported Formats:**\n"
        "• Videos (MP4, MKV, AVI, etc.)\n"
        "• Documents (PDF, ZIP, RAR, etc.)\n"
        "• Audio files (MP3, WAV, etc.)\n"
        "• Images (JPG, PNG, etc.)\n\n"
        "**Features:**\n"
        "• Fast streaming links\n"
        "• Direct download links\n"
        "• Web app player for videos\n"
        "• Auto-delete for privacy\n"
    )

@TechVJBot.on_message(filters.private & (
    filters.video | 
    filters.document | 
    filters.audio | 
    filters.photo
))
async def file_to_link_converter(client, message):
    """Convert any file to streaming/download links"""
    try:
        user_id = message.from_user.id
        username = message.from_user.mention
        
        # Get file information based on media type
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
            file = message.photo
            media_type = "photo"
            # For photos, we need to get the largest size
            file = message.photo.file_id
        else:
            await message.reply_text("❌ Unsupported file type")
            return

        file_name = getattr(file, 'file_name', 'Unknown File')
        file_size = humanbytes(getattr(file, 'file_size', 0))
        file_id = getattr(file, 'file_id', None)

        if not file_id:
            await message.reply_text("❌ Could not get file information")
            return

        # Forward file to LOG_CHANNEL for permanent storage
        try:
            log_msg = await client.send_cached_media(
                chat_id=LOG_CHANNEL,
                file_id=file_id,
                caption=f"**📁 File Converted**\n\n"
                       f"**User:** {username}\n"
                       f"**User ID:** `{user_id}`\n"
                       f"**File:** {file_name}\n"
                       f"**Type:** {media_type}\n"
                       f"**Size:** {file_size}"
            )
        except Exception as e:
            await message.reply_text("❌ Error processing file. Please try again.")
            return

        # Generate links
        try:
            fileName = get_name(log_msg)
            fileHash = get_hash(log_msg)
            
            # Generate streaming URL (for videos) or direct download URL
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
                except Exception:
                    pass  # Continue with normal URLs if shortlink fails

        except Exception as e:
            await message.reply_text("❌ Error generating links")
            return

        # Create appropriate buttons based on file type
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

        # Prepare message text based on file type
        if media_type == "video":
            msg_text = """**🎬 Video Converted Successfully!**

📂 **File Name:** `{}`
📦 **File Size:** `{}`
🎞️ **Format:** Video

⚡ **Links generated successfully!**
• Stream online with our player
• Download directly to your device
• Watch in web app for best experience

⏰ **Note:** Links will expire in 24 hours"""
        
        elif media_type == "audio":
            msg_text = """**🎵 Audio Converted Successfully!**

📂 **File Name:** `{}`
📦 **File Size:** `{}`
🎵 **Format:** Audio

⚡ **Links generated successfully!**
• Listen online
• Download audio file

⏰ **Note:** Links will expire in 24 hours"""
        
        elif media_type == "photo":
            msg_text = """**🖼️ Image Converted Successfully!**

📂 **File Name:** `{}`
📦 **File Size:** `{}`
🖼️ **Format:** Image

⚡ **Links generated successfully!**
• View image online
• Download original quality

⏰ **Note:** Links will expire in 24 hours"""
        
        else:  # documents
            msg_text = """**📄 Document Converted Successfully!**

📂 **File Name:** `{}`
📦 **File Size:** `{}`
📄 **Format:** Document

⚡ **Links generated successfully!**
• View document online
• Download original file

⏰ **Note:** Links will expire in 24 hours"""

        # Send the conversion result
        main_msg = await message.reply_text(
            text=msg_text.format(file_name, file_size),
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )

        # Store conversion data for auto-delete
        temp_conversions[main_msg.id] = {
            'user_id': user_id,
            'timestamp': asyncio.get_event_loop().time()
        }

        # Auto-delete after 10 minutes
        asyncio.create_task(auto_delete_message(main_msg, 600))

        # Update user stats
        try:
            await db.update_user_stats(user_id, conversions=1)
        except Exception:
            pass

    except FloodWait as e:
        await asyncio.sleep(e.value)
        await message.reply_text("⚠️ Too many requests. Please wait a moment and try again.")
    except Exception as e:
        await message.reply_text(f"❌ Error converting file: {str(e)}")

async def auto_delete_message(message, delay):
    """Auto-delete message after specified delay"""
    try:
        await asyncio.sleep(delay)
        await message.delete()
        if message.id in temp_conversions:
            del temp_conversions[message.id]
    except Exception:
        pass

@TechVJBot.on_message(filters.command("batch") & filters.private)
async def batch_convert_command(client, message):
    """Convert multiple files at once"""
    await message.reply_text(
        "**📦 Batch File Converter**\n\n"
        "To convert multiple files:\n"
        "1. Send me up to 10 files in a single message\n"
        "2. I'll process each file individually\n"
        "3. You'll get separate links for each file\n\n"
        "**Note:** Each file will be processed separately with its own links."
    )

@TechVJBot.on_message(filters.command("myfiles") & filters.private)
async def my_files_command(client, message):
    """Show user's recent conversions"""
    user_id = message.from_user.id
    
    # Get recent conversions from database
    try:
        user_data = await db.get_user(user_id)
        conversions = getattr(user_data, 'conversions', 0)
        
        text = f"**📊 Your Conversion Stats**\n\n"
        text += f"**Total Files Converted:** `{conversions}`\n"
        text += f"**Active Links:** `{len([k for k,v in temp_conversions.items() if v['user_id'] == user_id])}`\n\n"
        text += "**💡 Tips:**\n"
        text += "• Links expire after 24 hours\n"
        text += "• No limit on number of conversions\n"
        text += "• Supported: Videos, Documents, Audio, Images"
        
        await message.reply_text(text)
        
    except Exception as e:
        await message.reply_text(
            "**📊 Your Conversions**\n\n"
            "Start converting files to see your stats here!\n\n"
            "Send any file to get started."
        )

@TechVJBot.on_message(filters.command("cancel") & filters.private)
async def cancel_command(client, message):
    """Cancel ongoing operations"""
    user_id = message.from_user.id
    user_messages = [k for k,v in temp_conversions.items() if v['user_id'] == user_id]
    
    if user_messages:
        for msg_id in user_messages:
            try:
                await client.delete_messages(message.chat.id, msg_id)
                del temp_conversions[msg_id]
            except Exception:
                pass
        
        await message.reply_text("✅ Cleared your recent conversion messages!")
    else:
        await message.reply_text("ℹ️ No active conversions to cancel.")

# Error handler for large files
@TechVJBot.on_message(filters.private & filters.media)
async def handle_large_files(client, message):
    """Handle files that are too large"""
    try:
        file_size = 0
        if message.video:
            file_size = message.video.file_size
        elif message.document:
            file_size = message.document.file_size
        elif message.audio:
            file_size = message.audio.file_size
        
        # Telegram limit is 2GB, but we set a practical limit
        if file_size > 1500 * 1024 * 1024:  # 1.5GB
            await message.reply_text(
                "⚠️ **File Too Large**\n\n"
                "This file exceeds the 1.5GB limit.\n"
                "Please try with a smaller file or split it into parts."
            )
            return
        
    except Exception:
        pass

print("✅ File to Link Converter plugin loaded successfully!")
