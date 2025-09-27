# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio
from flask import Flask, request, render_template_string, abort, Response
from TechVJ.bot import TechVJBot
from TechVJ.util.custom_dl import ByteStreamer

app = Flask(__name__)
PRIVATE_CHANNEL_ID = int(os.getenv("PRIVATE_CHANNEL_ID", "-1001234567890"))

# Simple in-memory cache for ByteStreamer objects
stream_cache = {}

# Async helper to run Pyrogram inside Flask
def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)

@app.route("/player")
def player():
    """
    Streams a video from a private channel using message_id.
    Usage: /player?message_id=123&title=MyVideo
    """
    message_id = request.args.get("message_id", type=int)
    title = request.args.get("title", "Player")

    if not message_id:
        return "❌ Missing message_id", 400

    try:
        # Get message from private channel
        msg = run_async(TechVJBot.get_messages(PRIVATE_CHANNEL_ID, message_id))
        if not msg or not (msg.video or msg.document):
            return "❌ File not found", 404

        media = msg.video or msg.document

        # Use ByteStreamer to generate a streamable generator
        if TechVJBot not in stream_cache:
            stream_cache[TechVJBot] = ByteStreamer(TechVJBot)
        streamer = stream_cache[TechVJBot]

        def generate():
            # Streaming generator
            for chunk in streamer.yield_file(
                media=media,
                index=0,          # single client
                offset=0,
                first_cut=0,
                last_cut=media.file_size,
                part_count=1,
                chunk_size=1024*1024
            ):
                yield chunk

        # Serve video as a Flask Response
        return Response(
            generate(),
            mimetype=media.mime_type or "application/octet-stream",
            headers={
                "Content-Disposition": f'inline; filename="{media.file_name}"',
                "Accept-Ranges": "bytes"
            }
        )

    except Exception as e:
        return f"❌ Error streaming file: {e}", 500

@app.route("/player_html")
def player_html():
    """
    HTML player for embedding in browser.
    Usage: /player_html?message_id=123&title=MyVideo
    """
    message_id = request.args.get("message_id", type=int)
    title = request.args.get("title", "Player")
    if not message_id:
        return "❌ Missing message_id", 400

    # The source points to /player which streams the actual media
    source_url = f"/player?message_id={message_id}"
    html_template = f"""
    <html>
        <head><title>{title}</title></head>
        <body style="margin:0;display:flex;justify-content:center;align-items:center;height:100vh;background:#000;">
            <video controls autoplay width="80%" height="80%" style="background:#000;">
                <source src="{source_url}" type="video/mp4">
                Your browser does not support HTML video.
            </video>
        </body>
    </html>
    """
    return render_template_string(html_template)
