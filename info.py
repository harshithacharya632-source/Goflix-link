import re
import os
from os import environ

id_pattern = re.compile(r'^.\d+$')

# Bot information
SESSION = environ.get('SESSION', 'TechVJBot')
API_ID = int(environ.get('API_ID', '0'))
API_HASH = environ.get('API_HASH', '')
BOT_TOKEN = environ.get('BOT_TOKEN', "")

# Debug: Check environment variables
print("=== ENVIRONMENT VARIABLES ===")
print(f"API_ID: {API_ID}")
print(f"API_HASH: {bool(API_HASH)}")
print(f"BOT_TOKEN: {bool(BOT_TOKEN)}")

# Critical: LOG_CHANNEL must be a valid channel ID
LOG_CHANNEL = environ.get('LOG_CHANNEL', '')

# Validate LOG_CHANNEL
if not LOG_CHANNEL:
    print("❌ ERROR: LOG_CHANNEL is empty!")
    # Use a temporary valid channel ID for testing
    LOG_CHANNEL = '-1003059886878'  # Replace with actual ID
else:
    print(f"LOG_CHANNEL: {LOG_CHANNEL}")

try:
    LOG_CHANNEL = int(LOG_CHANNEL)
except (ValueError, TypeError):
    print("❌ ERROR: LOG_CHANNEL must be a valid integer!")
    LOG_CHANNEL = -1001234567890  # Fallback

print(f"Final LOG_CHANNEL: {LOG_CHANNEL}")
print("=============================")

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
    print("⚠️ WARNING: ADMINS not set, using default")

# MongoDB information
DATABASE_URI = environ.get('DATABASE_URI', "mongodb+srv://harshithacharya632:j2UBud9b3XUpk4Pn@goflix.iff0agy.mongodb.net/goflix?retryWrites=true&w=majority&appName=Goflix")
DATABASE_NAME = environ.get('DATABASE_NAME', "Goflix")

# Shortlink Info
SHORTLINK = environ.get('SHORTLINK', 'False').lower() == 'true'
SHORTLINK_URL = environ.get('SHORTLINK_URL', 'api.shareus.io')
SHORTLINK_API = environ.get('SHORTLINK_API', 'hRPS5vvZc0OGOEUQJMJzPiojoVK2')
