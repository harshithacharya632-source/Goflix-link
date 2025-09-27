# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio
import re
import threading
from flask import Flask, request, render_template_string, Response
from TechVJ.bot import TechVJBot
from TechVJ.util.custom_dl import ByteStreamer

app = Flask(__name__)
PRIVATE_CHANNEL_ID = int(os.getenv("PRIVATE_CHANNEL_ID", "-1001234567890"))

# Improved cache with thread safety
stream_cache = {}
cache_lock = threading.Lock()

# Async helper to run Pyrogram inside Flask
def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)

def get_streamer():
    with cache_lock:
        if TechVJBot not in stream_cache:
            stream_cache[TechVJBot] = ByteStreamer(TechVJBot)
        return stream_cache[TechVJBot]

@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Goflix Streamer</title>
        <style>
            body { margin: 0; padding: 40px; background: #000; font-family: Arial; color: white; text-align: center; }
            .container { max-width: 800px; margin: 0 auto; background: #111; padding: 30px; border-radius: 10px; }
            h1 { color: #ff6b6b; margin-bottom: 20px; }
            .endpoints { text-align: left; background: #222; padding: 20px; border-radius: 5px; margin: 20px 0; }
            code { background: #333; padding: 10px; border-radius: 3px; display: block; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬 Goflix Streamer</h1>
            <p>Welcome to your video streaming service!</p>
            
            <div class="endpoints">
                <h3>📺 Available Endpoints:</h3>
                <code>/player_html?message_id=123&amp;title=My Video</code>
                <p>HTML video player with controls</p>
                
                <code>/player?message_id=123</code>
                <p>Direct video stream URL</p>
                
                <code>/health</code>
                <p>Health check endpoint</p>
            </div>
        </div>
    </html>
    """

@app.route("/health")
def health_check():
    return {"status": "healthy", "service": "Goflix Streamer"}

@app.route("/player")
def player():
    """
    Streams a video from a private channel using message_id.
    Usage: /player?message_id=123
    """
    message_id = request.args.get("message_id", type=int)
    
    if not message_id:
        return "❌ Missing message_id parameter", 400

    try:
        # Get message from private channel
        msg = run_async(TechVJBot.get_messages(PRIVATE_CHANNEL_ID, message_id))
        if not msg:
            return "❌ Message not found", 404
            
        if not (msg.video or msg.document):
            return "❌ No video or document found in this message", 404

        media = msg.video or msg.document
        file_size = media.file_size
        
        # Handle range requests for better streaming
        range_header = request.headers.get('Range', None)
        byte1, byte2 = 0, None
        
        if range_header:
            range_match = re.search(r'bytes=(\d+)-(\d*)', range_header)
            if range_match:
                byte1 = int(range_match.group(1))
                byte2 = int(range_match.group(2)) if range_match.group(2) else file_size - 1

        streamer = get_streamer()
        
        def generate():
            for chunk in streamer.yield_file(
                media=media,
                index=0,
                offset=byte1,
                first_cut=byte1,
                last_cut=byte2 or file_size - 1,
                part_count=1,
                chunk_size=1024*1024
            ):
                yield chunk

        # Handle partial content
        if range_header:
            resp = Response(
                generate(),
                206,
                mimetype=media.mime_type or "video/mp4"
            )
            resp.headers.add('Content-Range', f'bytes {byte1}-{byte2 or file_size-1}/{file_size}')
        else:
            resp = Response(
                generate(),
                200,
                mimetype=media.mime_type or "video/mp4"
            )
            
        resp.headers.add('Accept-Ranges', 'bytes')
        resp.headers.add('Content-Disposition', f'inline; filename="{media.file_name}"')
        
        return resp

    except Exception as e:
        return f"❌ Error streaming file: {str(e)}", 500

@app.route("/player_html")
def player_html():
    """
    HTML player for embedding in browser.
    Usage: /player_html?message_id=123&title=MyVideo
    """
    message_id = request.args.get("message_id", type=int)
    title = request.args.get("title", "Goflix Player")
    
    if not message_id:
        return "❌ Missing message_id parameter", 400

    source_url = f"/player?message_id={message_id}"
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ title }}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { margin: 0; padding: 20px; background: #000; display: flex; justify-content: center; align-items: center; min-height: 100vh; font-family: Arial; }
            .video-container { width: 90%; max-width: 1000px; background: #111; padding: 20px; border-radius: 10px; }
            video { width: 100%; height: auto; border-radius: 5px; background: #000; }
            .title { color: white; text-align: center; margin-bottom: 15px; font-size: 24px; }
        </style>
    </head>
    <body>
        <div class="video-container">
            <div class="title">{{ title }}</div>
            <video controls autoplay playsinline>
                <source src="{{ source_url }}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
        <script>
            const video = document.querySelector('video');
            
            video.addEventListener('error', function(e) {
                console.log('Video error:', e);
                setTimeout(function() {
                    video.load();
                    video.play().catch(console.error);
                }, 3000);
            });
            
            function toggleFullscreen() {
                if (!document.fullscreenElement) {
                    video.requestFullscreen().catch(err => console.error('Error attempting fullscreen:', err));
                } else {
                    document.exitFullscreen();
                }
            }
            
            function reloadVideo() {
                video.load();
                video.play().catch(console.error);
            }
            
            function toggleMute() {
                video.muted = !video.muted;
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template, title=title, source_url=source_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
