import requests
import os
from flask import Flask, request, render_template_string

app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN")

@app.route("/player")
def player():
    file_id = request.args.get("file_id")
    title = request.args.get("title", "Player")

    if not file_id:
        return "❌ Missing file_id", 400

    resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}").json()
    if not resp.get("ok"):
        return f"❌ Error fetching file: {resp}", 400

    file_path = resp["result"]["file_path"]
    cdn_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

    # Your existing HTML player template, just replace source
    return render_template_string(
        """<video controls autoplay width="100%" src="{{ cdn_url }}"></video>""",
        cdn_url=cdn_url
    )
