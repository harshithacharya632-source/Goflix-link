import re
import os
from os import environ

id_pattern = re.compile(r'^.\d+$')

# Bot information
SESSION = environ.get('SESSION', 'TechVJBot')
API_ID = int(environ.get('API_ID', '0'))
API_HASH = environ.get('API_HASH', '')
BOT_TOKEN = environ.get('BOT_TOKEN', "")

# Debug info
print("=== Goflix Bot Starting ===")
print(f"API_ID: {API_ID}")

# CRITICAL FIX: Handle LOG_CHANNEL properly
log_channel_str = environ.get('LOG_CHANNEL', '').strip()
if not log_channel_str:
    print("❌ FATAL ERROR: LOG_CHANNEL environment variable is empty!")
    print("Please set LOG_CHANNEL in Render environment variables")
    # Use a dummy value to prevent immediate crash
    LOG_CHANNEL = -1003059886878
else:
    try:
        LOG_CHANNEL = int(log_channel_str)
        print(f"LOG_CHANNEL: {LOG_CHANNEL}")
    except ValueError:
        print(f"❌ ERROR: Invalid LOG_CHANNEL format: {log_channel_str}")
        LOG_CHANNEL = -1003059886878

# Bot settings
PORT = environ.get("PORT", "8080")

# Online Stream and Download
MULTI_CLIENT = False
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))
ON_HEROKU = 'DYNO' in environ
URL = environ.get("URL", "https://goflix-link-bot01.onrender.com")

# Admins, Channels & Users
ADMINS = []
admins_str = environ.get('ADMINS', '')
if admins_str:
    ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in admins_str.split()]
else:
    ADMINS = [762638982]  # Your Telegram ID
    print("⚠️ ADMINS not set, using default")

print(f"ADMINS: {ADMINS}")

# MongoDB information
DATABASE_URI = environ.get('DATABASE_URI', "mongodb+srv://harshithacharya632:j2UBud9b3XUpk4Pn@goflix.iff0agy.mongodb.net/goflix?retryWrites=true&w=majority&appName=Goflix")
DATABASE_NAME = environ.get('DATABASE_NAME', "Goflix")

# Shortlink Info
SHORTLINK = environ.get('SHORTLINK', 'False').lower() == 'true'
SHORTLINK_URL = environ.get('SHORTLINK_URL', 'api.shareus.io')
SHORTLINK_API = environ.get('SHORTLINK_API', 'hRPS5vvZc0OGOEUQJMJzPiojoVK2')

print("=== Configuration Loaded ===")
