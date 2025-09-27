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
    log_msg = await client.send_cached_media(
        chat_id=LOG_CHANNEL,
        file_id=fileid,
    )

    fileName = get_name(log_msg)

    # -----------------------------
    # Get Telegram CDN link
    # -----------------------------
    resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={fileid}").json()
    if not resp.get("ok"):
        await message.reply_text("❌ Error fetching Telegram CDN link")
        return
    file_path = resp["result"]["file_path"]
    cdn_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

    # Generate stream & download links
    if SHORTLINK is False:
        stream = cdn_url
        download = f"{URL}/download/{str(log_msg.id)}/{quote_plus(fileName)}?hash={get_hash(log_msg)}"
    else:
        stream = await get_shortlink(cdn_url)
        download = await get_shortlink(
            f"{URL}/download/{str(log_msg.id)}/{quote_plus(fileName)}?hash={get_hash(log_msg)}"
        )

    # Log message
    await log_msg.reply_text(
        text=f"•• ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ꜰᴏʀ ɪᴅ #{user_id} \n•• ᴜꜱᴇʀɴᴀᴍᴇ : {username} \n\n•• ᖴᎥᒪᗴ Nᗩᗰᴇ : {fileName}",
        quote=True,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("🚀 Fast Download 🚀", url=download),
                InlineKeyboardButton("🖥 Watch online 🖥", url=stream)
            ]]
        )
    )

    # Buttons for user
    rm = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("sᴛʀᴇᴀᴍ 🖥", url=stream),
                InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ 📥", url=download)
            ],
            [
                InlineKeyboardButton("• ᴡᴀᴛᴄʜ ɪɴ ᴡᴇʙ ᴀᴘᴘ •", web_app=WebAppInfo(url=stream))
            ]
        ]
    )

    # Message text (no raw links)
    msg_text = """<i><u>𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 !</u></i>\n\n
<b>📂 Fɪʟᴇ ɴᴀᴍᴇ :</b> <i>{}</i>\n\n
<b>📦 Fɪʟᴇ ꜱɪᴢᴇ :</b> <i>{}</i>\n\n
<b>⏰ Nᴏᴛᴇ : Tʜɪs ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇᴅ ɪɴ 5 ᴍɪɴᴜᴛᴇs</b>\n
<b>🚸 Lɪɴᴋ ᴡɪʟʟ ᴇxᴘɪʀᴇ ɪɴ 24 ʜᴏᴜʀs</b>"""

    # Send message and store the message object
    main_msg = await message.reply_text(
        text=msg_text.format(
            fileName,
            humanbytes(get_media_file_size(message)),
        ),
        quote=True,
        disable_web_page_preview=True,
        reply_markup=rm
    )

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
